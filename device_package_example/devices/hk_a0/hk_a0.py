import logging
from typing import Dict, Any, List, Optional

try:
    from unilabos.ros.nodes.base_device_node import BaseROS2DeviceNode
except ImportError:
    BaseROS2DeviceNode = None

try:
    from pymodbus.client import ModbusSerialClient  # 3.x
except Exception:
    try:
        from pymodbus.client.sync import ModbusSerialClient  # 2.5.x
    except Exception:
        ModbusSerialClient = None

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


@device(
    id="hk_a0",
    category=["io_module"],
    description="华控模拟量输出模块（RS485 Modbus RTU，FC06/03）",
    display_name="华控模拟量输出",
)
class HKA0:
    """华控电子（惠州）RS485 模拟量输出模块驱动。

    手册：《模拟量输出系列使用手册(RS485版) V2.0》
      - 保持寄存器 0x000A 起为第 1~12 路输出设定值
      - 固定 3 位小数：1.000 V → 寄存器值 1000（FC06/10 写，FC03 读）
      - 配置寄存器：0x0032 站号、0x0033 波特率、0x003D 校验
    """

    _ros_node: "BaseROS2DeviceNode"

    REG_OUTPUT_BASE = 0x000A
    REG_SLAVE_ADDRESS = 0x0032
    REG_BAUDRATE = 0x0033
    REG_PARITY = 0x003D
    SCALE = 1000  # 固定 3 位小数

    def __init__(self, device_id: str = None, config: Dict[str, Any] = None, **kwargs):
        if device_id is None and "id" in kwargs:
            device_id = kwargs.pop("id")
        if config is None and "config" in kwargs:
            config = kwargs.pop("config")

        self.device_id = device_id or "hk_a0_module_1"
        self.config = config or {}
        self.logger = logging.getLogger(f"HKA0.{self.device_id}")

        self.port = self.config.get("port", "/dev/ttyUSB0")
        self.baudrate = self.config.get("baudrate", 9600)
        self.slave_address = self.config.get("slave_address", 1)
        self.channel_count = self.config.get("channel_count", 6)
        self.output_max = float(self.config.get("output_max", 5.0))
        self.timeout = self.config.get("timeout", 1.0)

        self.client: Optional[ModbusSerialClient] = None
        self.data = {
            "status": "Idle",
            "outputs": [0.0] * self.channel_count,
            "last_error": "",
        }

    @not_action
    def post_init(self, ros_node: "BaseROS2DeviceNode"):
        self._ros_node = ros_node

    def _channel_register(self, channel: int) -> int:
        return self.REG_OUTPUT_BASE + channel - 1

    def _to_register(self, value: float) -> int:
        return int(round(value * self.SCALE))

    def _from_register(self, raw: int) -> float:
        return raw / self.SCALE

    @action(description="初始化设备")
    async def initialize(self) -> bool:
        """初始化 Modbus 连接。"""
        try:
            if ModbusSerialClient is None:
                self.logger.error("pymodbus 未安装")
                self.data["status"] = "Error"
                self.data["last_error"] = "pymodbus not installed"
                return False

            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                parity="N",
                stopbits=1,
                bytesize=8,
            )

            if not self.client.connect():
                self.logger.error(f"无法连接 {self.port}")
                self.data["status"] = "Error"
                self.data["last_error"] = "Connection failed"
                return False

            self.data["status"] = "Idle"
            self.logger.info(
                f"华控模拟量输出已连接: {self.port}, 从站 {self.slave_address}, "
                f"通道 {self.channel_count}, 量程 0~{self.output_max}"
            )
            return True

        except Exception as e:
            self.logger.error(f"初始化失败: {e}")
            self.data["status"] = "Error"
            self.data["last_error"] = str(e)
            return False

    @action(description="设置输出值")
    async def set_output(self, channel: int, value: float) -> bool:
        """设置单通道输出（FC06 写保持寄存器）。

        Args:
            channel[通道号]: 1 ~ channel_count
            value[输出值]: 物理量，电压单位 V（0~5 或 0~10，视模块量程）
        """
        if not (1 <= channel <= self.channel_count):
            self.logger.error(f"无效通道: {channel}")
            self.data["last_error"] = f"Invalid channel: {channel}"
            return False

        if not (0.0 <= value <= self.output_max):
            self.logger.error(f"输出超量程: {value}（允许 0~{self.output_max}）")
            self.data["last_error"] = f"Value out of range: {value}"
            return False

        try:
            raw_value = self._to_register(value)
            reg_addr = self._channel_register(channel)

            result = self.client.write_register(
                address=reg_addr,
                value=raw_value,
                slave=self.slave_address,
            )

            if result.isError():
                self.logger.error(f"写入通道 {channel} 失败")
                self.data["last_error"] = "Modbus write error"
                return False

            self.data["outputs"][channel - 1] = value
            self.logger.info(f"Ch{channel} = {value}（寄存器 {reg_addr:#06x} = {raw_value}）")
            return True

        except Exception as e:
            self.logger.error(f"设置输出失败: {e}")
            self.data["last_error"] = str(e)
            return False

    @action(description="停止所有输出")
    async def stop_all(self) -> bool:
        """全部通道置 0。"""
        success = True
        for i in range(1, self.channel_count + 1):
            if not await self.set_output(i, 0.0):
                success = False
        return success

    @action(description="读取所有输出值")
    async def read_outputs(self) -> List[float]:
        """读取各通道当前设定值（FC03，自 0x000A 连续读）。"""
        try:
            result = self.client.read_holding_registers(
                address=self.REG_OUTPUT_BASE,
                count=self.channel_count,
                slave=self.slave_address,
            )

            if result.isError():
                self.logger.error("读取输出寄存器失败")
                self.data["last_error"] = "Modbus read error"
                return self.data["outputs"]

            outputs = [self._from_register(reg) for reg in result.registers]
            self.data["outputs"] = outputs
            return outputs

        except Exception as e:
            self.logger.error(f"读取输出失败: {e}")
            self.data["last_error"] = str(e)
            return self.data["outputs"]

    @action(description="清理资源")
    async def cleanup(self) -> bool:
        """关闭 Modbus 连接。"""
        try:
            if self.client and self.client.is_socket_open():
                self.client.close()
            self.data["status"] = "Offline"
            self.logger.info("华控模拟量输出连接已关闭")
            return True
        except Exception as e:
            self.logger.error(f"清理失败: {e}")
            return False

    @property
    @topic_config()
    def status(self) -> str:
        return self.data.get("status", "Idle")

    @property
    @topic_config()
    def outputs(self) -> List[float]:
        return self.data.get("outputs", [0.0] * self.channel_count)


# ========== 本地硬件冒烟==========
# python hk_a0.py --port COM3 [-v] [--demo]


def _smoke_main():
    import argparse
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from smoke_runner import add_common_args, add_serial_args, run_smoke, setup_logging, smoke_lifecycle

    parser = argparse.ArgumentParser(description="华控模拟量输出 - 本地硬件冒烟")
    add_serial_args(parser, default_port="/dev/ttyUSB0", default_baudrate=9600)
    parser.add_argument("--slave-address", type=int, default=1, dest="slave_address")
    parser.add_argument("--channel-count", type=int, default=6, dest="channel_count")
    parser.add_argument("--output-max", type=float, default=5.0, dest="output_max")
    add_common_args(parser)
    args = parser.parse_args()
    setup_logging(args.verbose)

    async def run():
        dev = HKA0(
            device_id="smoke_test",
            config={
                "port": args.port,
                "baudrate": args.baudrate,
                "slave_address": args.slave_address,
                "channel_count": args.channel_count,
                "output_max": args.output_max,
            },
        )

        async def demo(dev_):
            await dev_.set_output(1, 0.1)
            await dev_.stop_all()

        return await smoke_lifecycle(
            dev,
            read_fn=lambda d: d.read_outputs(),
            demo_fn=demo,
            do_demo=args.demo,
        )

    run_smoke(run)


if __name__ == "__main__":
    _smoke_main()
