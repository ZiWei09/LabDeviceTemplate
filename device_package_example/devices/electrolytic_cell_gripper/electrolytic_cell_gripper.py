"""
电解池夹爪工作站驱动

整合 2 台俏优灵步进电机 + 1 台大寰 PGE 平行电爪，对外提供 pick_sample / place_sample 高层动作。

三台设备共用 RS485 Modbus RTU（默认 COM29）：
  - 电机 1（从站 1）：水平滑台
  - 电机 2（从站 2）：垂直滑台
  - 夹爪（从站 5）：大寰 PGE

通信：115200，8N1
电机：功能码 03/06/10，速度/加速度为寄存器原始值（调试软件填 5000 即写 5000）
夹爪：功能码 03/06

v7：自包含驱动，支持延迟打开串口（首次动作时打开，不依赖框架是否调用 initialize）。
"""

import logging
import struct
import time as time_module
from typing import Dict, Any, Optional

try:
    from unilabos.ros.nodes.base_device_node import BaseROS2DeviceNode
except ImportError:
    BaseROS2DeviceNode = None

try:
    from unilabos.registry.decorators import device, action, topic_config, not_action
except ImportError:
    def device(**kwargs):
        def wrapper(cls):
            return cls
        return wrapper
    def action(**kwargs):
        def wrapper(func):
            return func
        return wrapper
    def topic_config(**kwargs):
        def wrapper(func):
            return func
        return wrapper
    def not_action(func):
        return func

try:
    import serial
    from serial import Serial
except ImportError:
    serial = None
    Serial = None


# ═══════════════════════════════════════════════════════════════════
# Modbus CRC16
# ═══════════════════════════════════════════════════════════════════

def _crc16_modbus(data: bytes) -> bytes:
    """计算 Modbus RTU CRC16，返回 2 字节（低字节在前）。"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack("<H", crc)


# ═══════════════════════════════════════════════════════════════════
# Modbus RTU 底层辅助
# ═══════════════════════════════════════════════════════════════════

class _ModbusRTU:
    """绑定串口的 Modbus RTU 底层通信辅助类。"""

    def __init__(self, ser: Serial, logger: logging.Logger):
        self._ser = ser
        self.logger = logger

    # ── 组帧 ──────────────────────────────────────────

    @staticmethod
    def _build_read_frame(slave_id: int, register: int, count: int = 1) -> bytes:
        frame = struct.pack(">B B H H", slave_id, 0x03, register, count)
        return frame + _crc16_modbus(frame)

    @staticmethod
    def _build_write_single_frame(slave_id: int, register: int, value: int) -> bytes:
        frame = struct.pack(">B B H H", slave_id, 0x06, register, value & 0xFFFF)
        return frame + _crc16_modbus(frame)

    @staticmethod
    def _build_write_multiple_frame(slave_id: int, start_register: int, values: list) -> bytes:
        count = len(values)
        byte_count = count * 2
        frame = struct.pack(">B B H H B", slave_id, 0x10, start_register, count, byte_count)
        for v in values:
            frame += struct.pack(">H", v & 0xFFFF)
        return frame + _crc16_modbus(frame)

    # ── 收发 ──────────────────────────────────────────

    def send_and_receive(self, frame: bytes, expect_len: int) -> Optional[bytes]:
        if self._ser is None or not self._ser.is_open:
            self.logger.error("Serial not open")
            return None

        self.logger.debug(f"TX: {frame.hex(' ')}")
        self._ser.reset_input_buffer()
        self._ser.write(frame)
        time_module.sleep(0.05)

        raw = self._ser.read(expect_len + 10)
        self.logger.debug(f"RX: {raw.hex(' ') if raw else '(empty)'}")

        if len(raw) < expect_len:
            self.logger.warning(f"Short response: expected >={expect_len}, got {len(raw)}")
            if len(raw) == 0:
                return None

        fc_sent = frame[1]
        slave_id = frame[0]
        for i in range(len(raw) - 1):
            if raw[i] == slave_id and raw[i + 1] == fc_sent:
                resp = raw[i:]
                if len(resp) >= expect_len:
                    payload = resp[:expect_len - 2]
                    crc_recv = resp[expect_len - 2:expect_len]
                    if _crc16_modbus(payload) == crc_recv:
                        return resp[:expect_len]
                    else:
                        self.logger.warning("CRC mismatch")
                        return resp[:expect_len]
                break
            if raw[i] == slave_id and raw[i + 1] == (fc_sent | 0x80):
                error_code = raw[i + 2] if i + 2 < len(raw) else 0xFF
                self.logger.error(f"Modbus error: FC=0x{raw[i+1]:02X}, err=0x{error_code:02X}")
                return None

        self.logger.warning("Could not locate valid response frame")
        return raw[:expect_len] if len(raw) >= expect_len else None

    # ── 寄存器读写 ──────────────────────────────────────────

    def read_registers(self, slave_id: int, start: int, count: int = 1) -> Optional[list]:
        frame = self._build_read_frame(slave_id, start, count)
        expect = 3 + count * 2 + 2
        resp = self.send_and_receive(frame, expect)
        if resp is None or len(resp) < expect:
            return None
        values = []
        for i in range(count):
            offset = 3 + i * 2
            values.append(struct.unpack(">H", resp[offset:offset + 2])[0])
        return values

    def write_single(self, slave_id: int, register: int, value: int) -> bool:
        frame = self._build_write_single_frame(slave_id, register, value)
        resp = self.send_and_receive(frame, 8)
        return resp is not None

    def write_multiple(self, slave_id: int, start: int, values: list) -> bool:
        frame = self._build_write_multiple_frame(slave_id, start, values)
        resp = self.send_and_receive(frame, 8)
        return resp is not None


# ═══════════════════════════════════════════════════════════════════
# 有符号 32 位整数转换
# ═══════════════════════════════════════════════════════════════════

def _from_signed32(val: int) -> tuple:
    if val < 0:
        val += 0x100000000
    return ((val >> 16) & 0xFFFF, val & 0xFFFF)


def _to_signed32(high: int, low: int) -> int:
    val = (high << 16) | low
    if val >= 0x80000000:
        val -= 0x100000000
    return val


# ═══════════════════════════════════════════════════════════════════
# 电机寄存器地址（俏优灵）
# ═══════════════════════════════════════════════════════════════════

_M_STATUS       = 0x0000
_M_POS_H        = 0x0001
_M_POS_L        = 0x0002
_M_SPEED        = 0x0003
_M_ESTOP        = 0x0004
_M_ENABLE       = 0x0006
_M_PP_TARGET_H  = 0x0010   # 点对点绝对定位模式
_M_PP_TARGET_L  = 0x0011
_M_PP_INIT_SPD  = 0x0012
_M_PP_RUN_SPD   = 0x0013
_M_PP_ACCEL     = 0x0014
_M_PP_TOL       = 0x0015
_M_HOME         = 0x001F
_M_FW_STEPS_H   = 0x0040   # 相对定位（正向）模式
_M_FW_STEPS_L   = 0x0041
_M_FW_INIT_SPD  = 0x0042
_M_FW_RUN_SPD   = 0x0043
_M_FW_ACCEL     = 0x0044
_M_FW_TOL       = 0x0045

# 夹爪寄存器地址（大寰 PGE）
_G_INIT         = 0x0100
_G_FORCE        = 0x0101
_G_TARGET_POS   = 0x0103
_G_SPEED        = 0x0104
_G_INIT_STATE   = 0x0200
_G_GRIP_STATE   = 0x0201
_G_ACTUAL_POS   = 0x0202

# 电机状态码映射
_MOTOR_STATUS = {0: "Idle", 1: "Busy", 2: "Stopped", 3: "LimitPos", 4: "LimitNeg"}


# ═══════════════════════════════════════════════════════════════════
# 工作站主类
# ═══════════════════════════════════════════════════════════════════

@device(
    id="electrolytic_cell_gripper",
    category=["custom", "electrolytic_cell_gripper"],
    description="电解池夹爪工作站（俏优灵电机 + 大寰 PGE 夹爪）",
    display_name="电解池夹爪",
)
class ElectrolyticCellGripper:
    """
    电解池夹爪工作站。

    组成：
      - 电机 1（从站 1）：俏优灵水平滑台
      - 电机 2（从站 2）：俏优灵垂直滑台
      - 夹爪（从站 5）：大寰 PGE 平行电爪

    对外动作分两类：
      - 工艺动作：pick_sample / place_sample（完整夹取/放置序列）
      - 手动动作：move_motor_mm / move_motor_steps 等（单轴或夹爪调试）

    pick/place 中的运动步数按现场工艺硬编码；手动动作由实验人员指定步数或 mm。
    """

    _ros_node: "BaseROS2DeviceNode"

    # 电机速度/加速度：调试软件中 5000 对应寄存器原始值 5000
    MOTOR_SPEED     = 5000   # 运行速度寄存器值
    MOTOR_ACCEL     = 5000   # 加速度寄存器值
    MOTOR_INIT_SPD  = 50     # 初始速度寄存器值
    MOTOR_TOL       = 100    # 定位容差（步）

    def __init__(self, device_id: str = None, config: Dict[str, Any] = None, **kwargs):
        if device_id is None and "id" in kwargs:
            device_id = kwargs.pop("id")
        if config is None and "config" in kwargs:
            config = kwargs.pop("config")

        self.device_id = device_id or "electrolytic_cell_gripper"
        self.config = config or {}
        self.logger = logging.getLogger(f"ECG.{self.device_id}")

        # ── 配置 ──────────────────────────────────────────────
        self._port_name: str = self.config.get("port", "COM29")
        self._baudrate: int = int(self.config.get("baudrate", 115200))
        self._timeout: float = float(self.config.get("timeout", 0.5))

        self._motor1_id: int = int(self.config.get("motor1_slave_id", 1))
        self._motor2_id: int = int(self.config.get("motor2_slave_id", 2))
        self._gripper_id: int = int(self.config.get("gripper_slave_id", 5))
        self._motor1_steps_per_mm: Optional[float] = self.config.get("motor1_steps_per_mm")
        self._motor2_steps_per_mm: Optional[float] = self.config.get("motor2_steps_per_mm")
        if self._motor1_steps_per_mm is not None:
            self._motor1_steps_per_mm = float(self._motor1_steps_per_mm)
        if self._motor2_steps_per_mm is not None:
            self._motor2_steps_per_mm = float(self._motor2_steps_per_mm)

        self._ser: Optional[Serial] = None
        self._bus: Optional[_ModbusRTU] = None

        # ── 状态数据 ──────────────────────────────────────────
        self.data: Dict[str, Any] = {
            "status": "Idle",
            "last_error": "",
        }

    # ── 框架回调 ─────────────────────────────────────────

    async def _sleep(self, seconds: float):
        if getattr(self, "_ros_node", None) is not None:
            await self._ros_node.sleep(seconds)
        else:
            time_module.sleep(seconds)

    @not_action
    def post_init(self, ros_node: "BaseROS2DeviceNode"):
        self._ros_node = ros_node

    def _ensure_serial(self) -> bool:
        """
        延迟打开串口。

        若串口已打开则直接返回 True；否则尝试立即打开，
        以便框架未调用 initialize() 时仍能执行动作。
        """
        if self._bus is not None and self._ser is not None and self._ser.is_open:
            return True

        self.logger.info(f"Opening serial port {self._port_name} @ {self._baudrate}...")
        try:
            if Serial is None:
                self.logger.error("pyserial not installed")
                return False

            self._ser = Serial(
                port=self._port_name,
                baudrate=self._baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=self._timeout,
            )

            if not self._ser.is_open:
                self.logger.error(f"Failed to open {self._port_name}")
                return False

            self._bus = _ModbusRTU(self._ser, self.logger)
            self.logger.info(f"Serial {self._port_name} opened successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to open serial: {e}")
            return False

    @action()
    async def initialize(self) -> bool:
        """打开串口并建立通信。"""
        self.logger.info("initialize() called")
        ok = self._ensure_serial()
        if ok:
            self.data["status"] = "Idle"
            self.logger.info("initialize() SUCCESS — serial is open")
        else:
            self.data["status"] = "Error"
            self.logger.error("initialize() FAILED — could not open serial")
        return ok

    @action()
    async def cleanup(self) -> bool:
        """关闭串口。"""
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None
        self._bus = None
        self.data["status"] = "Offline"
        return True

    # ── 状态属性 ──────────────────────────────────────────────

    @property
    @topic_config()
    def status(self) -> str:
        return self.data.get("status", "Idle")

    # ── 电机内部方法 ──────────────────────────────────

    def _motor_set_position_zero(self, slave_id: int) -> bool:
        """将当前实际位置寄存器写 0（把当前位置设为零点）。"""
        return self._bus.write_multiple(slave_id, _M_POS_H, [0, 0])

    def _motor_move_absolute(self, slave_id: int, position: int,
                              speed: int = None, accel: int = None) -> bool:
        """
        点对点模式绝对定位。

        Args:
            position: 目标位置（步，有符号 32 位）
            speed: 运行速度寄存器值（默认 MOTOR_SPEED=5000）
            accel: 加速度寄存器值（默认 MOTOR_ACCEL=5000）
        """
        spd = speed if speed is not None else self.MOTOR_SPEED
        acc = accel if accel is not None else self.MOTOR_ACCEL
        pos_h, pos_l = _from_signed32(int(position))
        values = [pos_h, pos_l, self.MOTOR_INIT_SPD, spd, acc, self.MOTOR_TOL]
        return self._bus.write_multiple(slave_id, _M_PP_TARGET_H, values)

    def _motor_read_status(self, slave_id: int) -> Optional[Dict]:
        """读取电机状态、位置、速度。"""
        regs = self._bus.read_registers(slave_id, _M_STATUS, 4)
        if regs is None or len(regs) < 4:
            return None
        return {
            "status_code": regs[0],
            "status": _MOTOR_STATUS.get(regs[0], f"Unknown({regs[0]})"),
            "position": _to_signed32(regs[1], regs[2]),
            "speed_reg": regs[3],
        }

    def _motor_emergency_stop(self, slave_id: int) -> bool:
        """发送电机急停。"""
        return self._bus.write_single(slave_id, _M_ESTOP, 0x0001)

    async def _motor_wait_idle(self, slave_id: int, timeout: float = 120.0,
                                poll_interval: float = 0.3) -> bool:
        """轮询直到电机退出 Busy（状态码 1）。"""
        elapsed = 0.0
        motor_name = f"Motor{slave_id}"
        while elapsed < timeout:
            info = self._motor_read_status(slave_id)
            if info is not None:
                code = info["status_code"]
                if code != 1:  # 非运行中
                    self.logger.info(f"{motor_name} idle: pos={info['position']}, status={info['status']}")
                    return True
            await self._sleep(poll_interval)
            elapsed += poll_interval
        self.logger.warning(f"{motor_name} wait_idle timed out after {timeout}s")
        return False

    # ── 夹爪内部方法 ────────────────────────────────

    def _gripper_init(self) -> bool:
        """发送夹爪回零/初始化命令（0x01）。"""
        return self._bus.write_single(self._gripper_id, _G_INIT, 0x01)

    async def _gripper_wait_init(self, timeout: float = 30.0) -> bool:
        """等待夹爪初始化完成。"""
        elapsed = 0.0
        while elapsed < timeout:
            regs = self._bus.read_registers(self._gripper_id, _G_INIT_STATE, 1)
            if regs is not None and regs[0] == 1:
                self.logger.info("Gripper init complete")
                return True
            await self._sleep(0.5)
            elapsed += 0.5
        self.logger.warning("Gripper init timed out")
        return False

    def _gripper_set_force(self, force: int) -> bool:
        force = max(20, min(100, force))
        return self._bus.write_single(self._gripper_id, _G_FORCE, force)

    def _gripper_set_speed(self, speed: int) -> bool:
        speed = max(1, min(100, speed))
        return self._bus.write_single(self._gripper_id, _G_SPEED, speed)

    def _gripper_set_position(self, position: int) -> bool:
        """设置夹爪目标位置。0=全闭，1000=全开。"""
        position = max(0, min(1000, position))
        return self._bus.write_single(self._gripper_id, _G_TARGET_POS, position)

    async def _gripper_wait_done(self, timeout: float = 15.0) -> bool:
        """等待夹爪动作完成（grip_state 为 1/2/3）。"""
        elapsed = 0.0
        while elapsed < timeout:
            regs = self._bus.read_registers(self._gripper_id, _G_GRIP_STATE, 1)
            if regs is not None and regs[0] in (1, 2, 3):
                state_names = {1: "Reached", 2: "Gripped", 3: "Dropped"}
                self.logger.info(f"Gripper done: {state_names.get(regs[0], regs[0])}")
                return True
            await self._sleep(0.2)
            elapsed += 0.2
        self.logger.warning("Gripper wait timed out")
        return False

    def _motor_slave_id(self, motor: int) -> Optional[int]:
        """motor: 1=水平, 2=垂直"""
        if motor == 1:
            return self._motor1_id
        if motor == 2:
            return self._motor2_id
        self.logger.error(f"无效电机编号: {motor}（仅支持 1=水平, 2=垂直）")
        return None

    def _steps_per_mm(self, motor: int) -> Optional[float]:
        return self._motor1_steps_per_mm if motor == 1 else self._motor2_steps_per_mm

    # ═══════════════════════════════════════════════════════════════
    #  实验人员手动动作（单轴 / 夹爪）
    # ═══════════════════════════════════════════════════════════════

    @action(description="单轴绝对定位（步）")
    async def move_motor_steps(
        self,
        motor: int,
        steps: int,
        wait: bool = True,
        speed: int = None,
        accel: int = None,
    ) -> bool:
        """移动指定电机到绝对位置（步）。

        Args:
            motor[电机]: 1=水平, 2=垂直
            steps[步数]: 目标位置（有符号整数）
            wait[等待]: 是否等待到位，默认 True
            speed[速度]: 可选，运行速度寄存器值
            accel[加速度]: 可选，加速度寄存器值
        """
        if not self._ensure_serial():
            self.data["status"] = "Error"
            return False

        slave_id = self._motor_slave_id(motor)
        if slave_id is None:
            return False

        self.data["status"] = "Busy"
        ok = self._motor_move_absolute(slave_id, int(steps), speed=speed, accel=accel)
        if ok and wait:
            ok = await self._motor_wait_idle(slave_id, timeout=120.0)
        self.data["status"] = "Idle" if ok else "Error"
        return ok

    @action(description="单轴绝对定位（mm）")
    async def move_motor_mm(
        self,
        motor: int,
        mm: float,
        wait: bool = True,
        speed: int = None,
        accel: int = None,
    ) -> bool:
        """移动指定电机到绝对位置（mm）。

        需在 config 中配置 motor1_steps_per_mm / motor2_steps_per_mm（现场标定）。
        """
        steps_per_mm = self._steps_per_mm(motor)
        if not steps_per_mm or steps_per_mm <= 0:
            self.logger.error(
                f"电机 {motor} 未配置 steps_per_mm，请在 graph config 中设置 motor{motor}_steps_per_mm"
            )
            self.data["last_error"] = f"motor{motor}_steps_per_mm not configured"
            return False

        steps = int(round(mm * steps_per_mm))
        self.logger.info(f"电机 {motor}: {mm} mm -> {steps} 步 (×{steps_per_mm}/mm)")
        return await self.move_motor_steps(motor, steps, wait=wait, speed=speed, accel=accel)

    @action(description="读取电机当前位置（步）")
    async def read_motor_position(self, motor: int) -> int:
        """读取电机当前位置（步）。失败时返回 0。"""
        if not self._ensure_serial():
            return 0

        slave_id = self._motor_slave_id(motor)
        if slave_id is None:
            return 0

        info = self._motor_read_status(slave_id)
        if info is None:
            return 0
        return int(info["position"])

    @action(description="将电机当前位置设为零点")
    async def motor_set_zero(self, motor: int) -> bool:
        """把指定电机当前位置写入为零点。"""
        if not self._ensure_serial():
            return False

        slave_id = self._motor_slave_id(motor)
        if slave_id is None:
            return False

        return self._motor_set_position_zero(slave_id)

    @action(description="夹爪张开")
    async def gripper_open(self, wait: bool = True) -> bool:
        """夹爪全开（位置 1000）。"""
        if not self._ensure_serial():
            return False
        self._gripper_set_position(1000)
        if wait:
            return await self._gripper_wait_done(timeout=15.0)
        return True

    @action(description="夹爪闭合")
    async def gripper_close(self, wait: bool = True) -> bool:
        """夹爪全闭（位置 0）。"""
        if not self._ensure_serial():
            return False
        self._gripper_set_position(0)
        if wait:
            return await self._gripper_wait_done(timeout=15.0)
        return True

    # ═══════════════════════════════════════════════════════════════
    #  动作 1：夹取样品（工艺序列）
    # ═══════════════════════════════════════════════════════════════

    @action()
    async def pick_sample(self):
        """
        夹取样品 — 完整序列：
          1. 夹爪初始化
          2. 设置夹爪力 50%
          3. 设置夹爪速度 100%
          4. 两个电机设置当前位置为零点
          5. 1号电机移动到 838000 步 (speed=5000, accel=5000)
          6. 2号电机移动到 -800000 步
          7. 夹爪闭合
          8. 2号电机移动到 0 步
          9. 1号电机移动到 0 步
         10. 2号电机移动到 -630000 步
        """
        # 延迟打开串口
        if not self._ensure_serial():
            self.logger.error("pick_sample ABORTED: cannot open serial port")
            self.data["status"] = "Error"
            return

        self.data["status"] = "Busy"
        self.logger.info("=" * 60)
        self.logger.info("pick_sample START")
        self.logger.info("=" * 60)

        try:
            # 步骤 1：夹爪回零
            self.logger.info("[1/10] Gripper init (homing)...")
            self._gripper_init()
            await self._gripper_wait_init(timeout=30.0)

            # 步骤 2：夹爪力 50%
            self.logger.info("[2/10] Set gripper force = 50%")
            self._gripper_set_force(50)
            time_module.sleep(0.05)

            # 步骤 3：夹爪速度 100%
            self.logger.info("[3/10] Set gripper speed = 100%")
            self._gripper_set_speed(100)
            time_module.sleep(0.05)

            # 步骤 4：两轴当前位置设为零点
            self.logger.info("[4/10] Motor1 + Motor2 set position zero")
            self._motor_set_position_zero(self._motor1_id)
            time_module.sleep(0.05)
            self._motor_set_position_zero(self._motor2_id)
            time_module.sleep(0.05)

            # 步骤 5：水平轴到 838000 步
            self.logger.info("[5/10] Motor1 move to 838000 steps (speed=5000, accel=5000)")
            self._motor_move_absolute(self._motor1_id, 838000, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor1_id, timeout=120.0)

            # 步骤 6：垂直轴到 -800000 步
            self.logger.info("[6/10] Motor2 move to -800000 steps")
            self._motor_move_absolute(self._motor2_id, -800000, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor2_id, timeout=120.0)

            # 步骤 7：夹爪闭合（位置 0）
            self.logger.info("[7/10] Gripper close")
            self._gripper_set_position(0)
            await self._gripper_wait_done(timeout=15.0)

            # 步骤 8：垂直轴回 0
            self.logger.info("[8/10] Motor2 move to 0 steps")
            self._motor_move_absolute(self._motor2_id, 0, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor2_id, timeout=120.0)

            # 步骤 9：水平轴回 0
            self.logger.info("[9/10] Motor1 move to 0 steps")
            self._motor_move_absolute(self._motor1_id, 0, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor1_id, timeout=120.0)

            # 步骤 10：垂直轴到待机位 -630000（旧值 -850000 已弃用）
            # self.logger.info("[10/10] Motor2 move to -850000 steps")
            # self._motor_move_absolute(self._motor2_id, -850000, speed=5000, accel=5000)
            self.logger.info("[10/10] Motor2 move to -630000 steps")
            self._motor_move_absolute(self._motor2_id, -630000, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor2_id, timeout=120.0)

            self.data["status"] = "Idle"
            self.logger.info("=" * 60)
            self.logger.info("pick_sample COMPLETE")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"pick_sample failed: {e}")
            self.data["status"] = "Error"

    # ═══════════════════════════════════════════════════════════════
    #  动作 2：放下样品（工艺序列）
    # ═══════════════════════════════════════════════════════════════

    @action()
    async def place_sample(self):
        """
        放下样品 — 完整序列：
          1. 2号电机移动到 0 步
          2. 1号电机移动到 838000 步
          3. 2号电机移动到 -790000 步
          4. 夹爪张开
          5. 2号电机移动到 0 步
          6. 1号电机移动到 0 步
        """
        # 延迟打开串口
        if not self._ensure_serial():
            self.logger.error("place_sample ABORTED: cannot open serial port")
            self.data["status"] = "Error"
            return

        self.data["status"] = "Busy"
        self.logger.info("=" * 60)
        self.logger.info("place_sample START")
        self.logger.info("=" * 60)

        try:
            # 步骤 1：垂直轴到 0
            self.logger.info("[1/6] Motor2 move to 0 steps")
            self._motor_move_absolute(self._motor2_id, 0, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor2_id, timeout=120.0)

            # 步骤 2：水平轴到 838000 步
            self.logger.info("[2/6] Motor1 move to 838000 steps")
            self._motor_move_absolute(self._motor1_id, 838000, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor1_id, timeout=120.0)

            # 步骤 3：垂直轴下探 -790000 步
            self.logger.info("[3/6] Motor2 move to -790000 steps")
            self._motor_move_absolute(self._motor2_id, -790000, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor2_id, timeout=120.0)

            # 步骤 4：夹爪张开（位置 1000）
            self.logger.info("[4/6] Gripper open")
            self._gripper_set_position(1000)
            await self._gripper_wait_done(timeout=15.0)

            # 步骤 5：垂直轴回 0
            self.logger.info("[5/6] Motor2 move to 0 steps")
            self._motor_move_absolute(self._motor2_id, 0, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor2_id, timeout=120.0)

            # 步骤 6：水平轴回 0
            self.logger.info("[6/6] Motor1 move to 0 steps")
            self._motor_move_absolute(self._motor1_id, 0, speed=5000, accel=5000)
            await self._motor_wait_idle(self._motor1_id, timeout=120.0)

            self.data["status"] = "Idle"
            self.logger.info("=" * 60)
            self.logger.info("place_sample COMPLETE")
            self.logger.info("=" * 60)

        except Exception as e:
            self.logger.error(f"place_sample failed: {e}")
            self.data["status"] = "Error"

    # ═══════════════════════════════════════════════════════════════
    #  急停
    # ═══════════════════════════════════════════════════════════════

    @action()
    async def emergency_stop(self):
        """立即停止所有电机（夹爪不动作）。"""
        self.logger.warning("EMERGENCY STOP")
        if self._bus is not None:
            self._motor_emergency_stop(self._motor1_id)
            time_module.sleep(0.02)
            self._motor_emergency_stop(self._motor2_id)
        self.data["status"] = "Stopped"


# ========== 本地硬件冒烟==========
# python electrolytic_cell_gripper.py --port COM29 [-v]


def _smoke_main():
    import argparse
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from smoke_runner import add_common_args, add_serial_args, run_smoke, setup_logging, smoke_lifecycle

    parser = argparse.ArgumentParser(description="电解池夹爪 - 本地硬件冒烟")
    add_serial_args(parser, default_port="COM29", default_baudrate=115200)
    parser.add_argument("--motor", type=int, default=1, help="读取位置的电机编号 (1 或 2)")
    add_common_args(parser)
    args = parser.parse_args()
    setup_logging(args.verbose)

    async def run():
        dev = ElectrolyticCellGripper(
            device_id="smoke_test",
            config={"port": args.port, "baudrate": args.baudrate},
        )
        motor = args.motor
        return await smoke_lifecycle(
            dev,
            read_fn=lambda d: d.read_motor_position(motor),
        )

    run_smoke(run)


if __name__ == "__main__":
    _smoke_main()
