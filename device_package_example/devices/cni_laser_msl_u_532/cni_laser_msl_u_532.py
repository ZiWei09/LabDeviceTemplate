import logging
import time as time_module
from typing import Dict, Any, Optional

try:
    import serial
except ImportError:
    serial = None

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


@device(
    id="cni_laser_msl_u_532",
    category=["cni_laser_msl_u_532"],
    description="CNI MSL-U-532 532nm 激光器，Arduino + MCP4725 DAC 控制",
    display_name="CNI 532nm 激光器",
)
class CNILaserMSLU532:
    """CNI MSL-U-532-50mW laser driver via Arduino Nano + MCP4725 DAC.

    Arduino firmware accepts: SET <0-100> (percentage), returns OK:POWER=<val>
    All power control goes through DAC analog voltage on BNC port.
    """

    _ros_node: "BaseROS2DeviceNode"

    def __init__(self, device_id: str = None, config: Dict[str, Any] = None, **kwargs):
        if device_id is None and "id" in kwargs:
            device_id = kwargs.pop("id")
        if config is None and "config" in kwargs:
            config = kwargs.pop("config")

        self.device_id = device_id or "unknown_laser"
        self.config = config or {}
        self.logger = logging.getLogger(f"CNILaserMSLU532.{self.device_id}.cni_laser_msl_u_532")

        # Read parameters from config dict or kwargs (framework may expand config into kwargs)
        src = self.config if self.config else kwargs
        self._port: str = str(src.get("port", kwargs.get("port", "COM13")))
        self._baudrate: int = int(src.get("baudrate", kwargs.get("baudrate", 9600)))
        self._timeout: float = float(src.get("timeout", kwargs.get("timeout", 2.0)))
        self._max_power_mw: float = float(src.get("max_power_mw", kwargs.get("max_power_mw", 50.0)))

        self._serial: Optional[serial.Serial] = None
        # Last SET percentage value (0-100), used by turn_on() to restore power
        self._last_set_percent: int = 50  # default 50%

        # Pre-populate all property fields
        self.data = {
            "status": "Offline",
            "laser_on": "false",
            "power": 0.0,
            "power_percentage": 0.0,
            "wavelength": 532.0,
        }

    @not_action
    def post_init(self, ros_node: "BaseROS2DeviceNode"):
        """框架回调：保存 ROS 节点引用。"""
        self._ros_node = ros_node

    def _connect_serial(self) -> bool:
        if self._serial is not None and self._serial.is_open:
            return True
        if serial is None:
            self.logger.error("pyserial 未安装")
            return False
        self.logger.info(f"connecting to {self._port} @ {self._baudrate}")
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
            )
            self.logger.info("serial opened, waiting for Arduino reset...")
            time_module.sleep(2.5)

            if self._serial.in_waiting > 0:
                startup = self._serial.readline().decode("utf-8", errors="ignore").strip()
                self.logger.info(f"Arduino startup: {startup}")

            self._serial.reset_input_buffer()
            resp = self._send_command("IDN?")
            if resp and "ArduinoUno_LaserValve" in resp:
                self.logger.info(f"firmware OK: {resp}")
                self._send_command("SET 0")
                self.data["status"] = "Idle"
                self.data["laser_on"] = "false"
                self.data["power"] = 0.0
                self.data["power_percentage"] = 0.0
                return True

            self.logger.error(f"firmware check failed, got: {resp}")
            self.data["status"] = "Alarm"
            return False
        except Exception as e:
            self.logger.error(f"serial open failed: {e}")
            self._serial = None
            self.data["status"] = "Offline"
            return False

    def _send_command(self, cmd: str) -> str:
        """Send command to Arduino and read response."""
        if self._serial is None or not self._serial.is_open:
            self.logger.error("serial not connected")
            return ""
        try:
            self._serial.reset_input_buffer()
            self._serial.write((cmd + "\n").encode("utf-8"))
            self._serial.flush()
            time_module.sleep(0.05)
            resp = self._serial.readline().decode("utf-8", errors="ignore").strip()
            self.logger.debug(f"TX: {cmd} -> RX: {resp}")
            return resp
        except Exception as e:
            self.logger.error(f"serial error: {e}")
            return ""

    # ── Properties ──────────────────────────────────────────

    @property
    @topic_config()
    def status(self) -> str:
        return self.data.get("status", "Offline")

    @property
    @topic_config()
    def laser_on(self) -> str:
        return self.data.get("laser_on", "false")

    @property
    @topic_config()
    def power(self) -> float:
        return float(self.data.get("power", 0.0))

    @property
    @topic_config()
    def power_percentage(self) -> float:
        return float(self.data.get("power_percentage", 0.0))

    @property
    @topic_config()
    def wavelength(self) -> float:
        return float(self.data.get("wavelength", 532.0))

    @action(description="初始化设备")
    async def initialize(self) -> bool:
        """打开串口并验证 Arduino 固件。"""
        return self._connect_serial()

    @action(description="打开激光器")
    async def turn_on(self) -> bool:
        """Turn on laser, restore last power setting."""
        if self._last_set_percent <= 0:
            self._last_set_percent = 50  # default to 50% if never set
        resp = self._send_command(f"SET {self._last_set_percent}")
        if resp.startswith("OK"):
            pct = float(self._last_set_percent)
            self.data["status"] = "Emitting"
            self.data["laser_on"] = "true"
            self.data["power_percentage"] = pct
            self.data["power"] = pct / 100.0 * self._max_power_mw
            self.logger.info(f"turn_on: SET {self._last_set_percent} -> {resp}")
            return True
        else:
            self.logger.error(f"turn_on failed: {resp}")
            return False

    @action(description="关闭激光器")
    async def turn_off(self) -> bool:
        """Turn off laser (DAC = 0V)."""
        resp = self._send_command("SET 0")
        if resp.startswith("OK"):
            self.data["status"] = "Idle"
            self.data["laser_on"] = "false"
            self.data["power"] = 0.0
            self.data["power_percentage"] = 0.0
            self.logger.info(f"turn_off: SET 0 -> {resp}")
            return True
        else:
            self.logger.error(f"turn_off failed: {resp}")
            return False

    @action(description="设置激光功率(mW)")
    async def set_power(self, power: float) -> bool:
        """Set laser power in mW (0 ~ max_power_mw).

        Converts to percentage (0-100) for Arduino firmware.
        """
        power = max(0.0, min(float(power), self._max_power_mw))
        pct = int(round(power / self._max_power_mw * 100.0))
        resp = self._send_command(f"SET {pct}")
        if resp.startswith("OK"):
            self._last_set_percent = pct
            self.data["power_percentage"] = float(pct)
            self.data["power"] = float(pct) / 100.0 * self._max_power_mw
            if pct > 0:
                self.data["status"] = "Emitting"
                self.data["laser_on"] = "true"
            else:
                self.data["status"] = "Idle"
                self.data["laser_on"] = "false"
            self.logger.info(f"set_power({power}mW) -> SET {pct} -> {resp}")
            return True
        else:
            self.logger.error(f"set_power failed: {resp}")
            return False

    @action(description="按百分比设置激光功率")
    async def set_power_percentage(self, percentage: float) -> bool:
        """Set laser power by percentage (0-100%).

        Sends SET <0-100> directly to Arduino.
        """
        pct = int(round(max(0.0, min(float(percentage), 100.0))))
        resp = self._send_command(f"SET {pct}")
        if resp.startswith("OK"):
            self._last_set_percent = pct
            self.data["power_percentage"] = float(pct)
            self.data["power"] = float(pct) / 100.0 * self._max_power_mw
            if pct > 0:
                self.data["status"] = "Emitting"
                self.data["laser_on"] = "true"
            else:
                self.data["status"] = "Idle"
                self.data["laser_on"] = "false"
            self.logger.info(f"set_power_percentage({percentage}%) -> SET {pct} -> {resp}")
            return True
        else:
            self.logger.error(f"set_power_percentage failed: {resp}")
            return False

    @action(description="紧急停止")
    async def emergency_stop(self) -> bool:
        """Emergency stop - immediately set DAC to 0."""
        resp = self._send_command("SET 0")
        self._last_set_percent = 0
        self.data["status"] = "Idle"
        self.data["laser_on"] = "false"
        self.data["power"] = 0.0
        self.data["power_percentage"] = 0.0
        self.logger.info(f"emergency_stop: SET 0 -> {resp}")
        return True

    @action(description="清理资源")
    async def cleanup(self) -> bool:
        """Cleanup - turn off laser and close serial."""
        try:
            if self._serial and self._serial.is_open:
                self._send_command("SET 0")
                self._serial.close()
                self.logger.info("cleanup: serial closed")
        except Exception as e:
            self.logger.error(f"cleanup error: {e}")
        self._serial = None
        self.data["status"] = "Offline"
        self.data["laser_on"] = "false"
        self.data["power"] = 0.0
        self.data["power_percentage"] = 0.0
        return True


# ========== 本地硬件冒烟==========
# python cni_laser_msl_u_532.py --port COM13 [-v]
# 注意：仅验证串口通信与固件握手，不会开启激光


def _smoke_main():
    import argparse
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from smoke_runner import add_common_args, add_serial_args, run_smoke, setup_logging, smoke_lifecycle

    parser = argparse.ArgumentParser(description="CNI 532nm 激光器 - 本地硬件冒烟")
    add_serial_args(parser, default_port="COM13", default_baudrate=9600)
    add_common_args(parser)
    args = parser.parse_args()
    setup_logging(args.verbose)

    async def run():
        dev = CNILaserMSLU532(
            device_id="smoke_test",
            config={"port": args.port, "baudrate": args.baudrate},
        )

        def read_state(d):
            return {
                "status": d.status,
                "laser_on": d.laser_on,
                "power": d.power,
                "wavelength": d.wavelength,
            }

        return await smoke_lifecycle(dev, read_fn=read_state)

    run_smoke(run)


if __name__ == "__main__":
    _smoke_main()
