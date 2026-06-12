import logging
import time as time_module
from typing import Dict, Any

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
    id="daheng_gci060505",
    category=["custom", "daheng_gci060505"],
    description="大恒 GCI-060505 LED 光源，Arduino + MCP4725 DAC 控制",
    display_name="GCI-060505 LED 光源",
)
class DahengGCI060505:
    """大恒光电 GCI-060505 LED光源驱动（通过 Arduino + MCP4725 DAC 控制）"""

    _ros_node: "BaseROS2DeviceNode"

    def __init__(self, device_id: str = None, config: Dict[str, Any] = None, **kwargs):
        if device_id is None and 'id' in kwargs:
            device_id = kwargs.pop('id')
        if config is None and 'config' in kwargs:
            config = kwargs.pop('config')
        self.device_id = device_id or "unknown_device"
        self.config = config or {}
        self.logger = logging.getLogger(f"DahengGCI060505.{self.device_id}.daheng_gci060505")

        self._port = self.config.get("port", "COM14")
        self._baudrate = self.config.get("baudrate", 115200)
        self._timeout = self.config.get("timeout", 2)
        self._ser = None

        self.data = {
            "status": "Idle",
            "brightness": 0.0,
            "light_on": False,
            "max_brightness": 100.0,
        }

    @not_action
    def post_init(self, ros_node: "BaseROS2DeviceNode"):
        self._ros_node = ros_node

    def _open_serial(self) -> bool:
        if self._ser is not None and self._ser.is_open:
            return True
        if serial is None:
            self.logger.error("pyserial 未安装，请运行: pip install pyserial")
            return False
        try:
            self._ser = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
            )
            time_module.sleep(2)
            self._ser.reset_input_buffer()
            self.logger.info(f"串口 {self._port} 已打开")
            return True
        except Exception as e:
            self.logger.error(f"串口打开失败: {e}")
            self._ser = None
            return False

    def _send_command(self, cmd: str) -> str:
        if self._ser is None or not self._ser.is_open:
            if not self._open_serial():
                return ""
        try:
            self._ser.reset_input_buffer()
            self._ser.write(f"{cmd}\n".encode("ascii"))
            self._ser.flush()
            response = self._ser.readline().decode("ascii", errors="ignore").strip()
            self.logger.debug(f"TX: {cmd} → RX: {response}")
            return response
        except Exception as e:
            self.logger.error(f"通信失败: {e}")
            return ""

    def _close_serial(self):
        if self._ser is not None and self._ser.is_open:
            try:
                self._ser.close()
            except Exception:
                pass
            self._ser = None

    def _refresh_from_arduino(self):
        response = self._send_command("STATUS")
        if "OK:STATUS:" in response:
            try:
                parts = response.split(":")
                idx = parts.index("STATUS")
                on_off = parts[idx + 1]
                bright = int(parts[idx + 2])
                self.data["light_on"] = (on_off == "ON")
                self.data["brightness"] = float(bright)
                self.data["status"] = "On" if self.data["light_on"] else "Idle"
            except (ValueError, IndexError) as e:
                self.logger.warning(f"STATUS 解析失败: {response}, 错误: {e}")

    @action(description="初始化设备")
    async def initialize(self) -> bool:
        """打开串口并验证 Arduino 通信。"""
        if not self._open_serial():
            self.data["status"] = "Error"
            return False
        response = self._send_command("PING")
        if "PONG" in response:
            self.logger.info("Arduino 通信正常")
            self.data["status"] = "Idle"
            self._refresh_from_arduino()
            return True
        self.logger.error(f"PING 测试失败，响应: {response}")
        self.data["status"] = "Error"
        return False

    @action(description="清理资源")
    async def cleanup(self) -> bool:
        """关灯并关闭串口。"""
        try:
            self._send_command("OFF")
        except Exception:
            pass
        self._close_serial()
        self.data["status"] = "Offline"
        self.data["light_on"] = False
        return True

    @property
    @topic_config()
    def status(self) -> str:
        return self.data.get("status", "Idle")

    @property
    @topic_config()
    def brightness(self) -> float:
        return self.data.get("brightness", 0.0)

    @property
    @topic_config()
    def light_on(self) -> bool:
        return self.data.get("light_on", False)

    @property
    @topic_config()
    def max_brightness(self) -> float:
        return self.data.get("max_brightness", 100.0)

    @action(description="开灯")
    async def turn_on(self) -> bool:
        self.data["status"] = "Busy"
        response = self._send_command("ON")
        ok = "OK" in response
        if ok:
            self.data["light_on"] = True
            if self.data["brightness"] == 0.0:
                self.data["brightness"] = 100.0
            self.data["status"] = "On"
        else:
            self.data["status"] = "Error"
        return ok

    @action(description="关灯")
    async def turn_off(self) -> bool:
        self.data["status"] = "Busy"
        response = self._send_command("OFF")
        ok = "OK" in response
        if ok:
            self.data["light_on"] = False
            self.data["status"] = "Idle"
        else:
            self.data["status"] = "Error"
        return ok

    @action(description="设置亮度")
    async def set_brightness(self, brightness: float) -> bool:
        brightness = max(0.0, min(100.0, float(brightness)))
        self.data["status"] = "Busy"
        response = self._send_command(f"BRIGHT:{int(brightness)}")
        ok = "OK" in response
        if ok:
            self.data["brightness"] = brightness
            self.data["light_on"] = brightness > 0
            self.data["status"] = "On" if brightness > 0 else "Idle"
        else:
            self.data["status"] = "Error"
        return ok

    @action(description="刷新设备状态", always_free=True)
    async def refresh_status(self) -> bool:
        self._refresh_from_arduino()
        return True
