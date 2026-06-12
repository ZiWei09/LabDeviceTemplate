"""
Bronkhorst EL-FLOW Prestige 质量流量控制器 (MFC) 驱动
"""

import logging
from typing import Dict, Any

try:
    from unilabos.ros.nodes.base_device_node import BaseROS2DeviceNode
except ImportError:
    BaseROS2DeviceNode = None

try:
    import propar
except ImportError:
    propar = None

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
    id="bronkhorst_el_flow",
    category=["sensor", "bronkhorst_el_flow"],
    description="Bronkhorst EL-FLOW Prestige 质量流量控制器",
    display_name="Bronkhorst MFC",
)
class BronkhorstElFlow:
    _ros_node: "BaseROS2DeviceNode"

    def __init__(self, device_id: str = None, config: Dict[str, Any] = None, **kwargs):
        if device_id is None and "id" in kwargs:
            device_id = kwargs.pop("id")
        if config is None and "config" in kwargs:
            config = kwargs.pop("config")

        self.device_id = device_id or "unknown_device"
        self.config = config or {}
        self.logger = logging.getLogger(f"BronkhorstElFlow.{self.device_id}")

        self.data = {
            "status": "Idle",
            "flow": 0.0,
            "setpoint": 0.0,
            "temperature": 0.0,
            "valve_output": 0.0,
            "capacity_unit": "",
            "user_tag": "",
            "level": False,
            "rssi": 0,
            "value": 0.0,
        }

        self._port = self.config.get("port") or kwargs.get("port", "COM12")
        self._baudrate = int(self.config.get("baudrate") or kwargs.get("baudrate", 38400))
        self._address = int(self.config.get("address") or kwargs.get("address", 3))
        self._channel = int(self.config.get("channel") or kwargs.get("channel", 1))
        self._threshold_pct = float(self.config.get("threshold") or kwargs.get("threshold", 2.0))

        self._instrument = None

    @not_action
    def post_init(self, ros_node: "BaseROS2DeviceNode"):
        self._ros_node = ros_node

    async def _sleep(self, seconds: float):
        if getattr(self, "_ros_node", None) is not None:
            await self._ros_node.sleep(seconds)
        else:
            import time as _time
            _time.sleep(seconds)

    @action(description="初始化设备")
    async def initialize(self) -> bool:
        self.logger.debug("initialize called, instrument=%s", self._instrument)
        if self._instrument is not None:
            self.data["status"] = "Idle"
            self.logger.debug("设备已在 initialize 前连接")
            return True
        if propar is None:
            self.data["status"] = "Offline"
            return False
        try:
            self._instrument = propar.instrument(
                self._port,
                self._address,
                baudrate=self._baudrate,
            )
            unit = self._instrument.readParameter(129)
            if unit is not None:
                self.data["capacity_unit"] = str(unit)
            tag = self._instrument.readParameter(115)
            if tag is not None:
                self.data["user_tag"] = str(tag)
            self._poll_values()
            self.data["status"] = "Idle"
            self.logger.info("Bronkhorst MFC 连接成功")
            return True
        except Exception as e:
            self.logger.error(f"连接失败: {e}")
            self.data["status"] = "Offline"
            return False

    @action(description="清理资源")
    async def cleanup(self) -> bool:
        try:
            if self._instrument is not None:
                try:
                    self._instrument.writeParameter(206, 0.0)
                except Exception:
                    pass
                self._instrument = None
            self.data["status"] = "Offline"
            return True
        except Exception as e:
            self.data["status"] = "Offline"
            return False

    def _poll_values(self):
        if self._instrument is None:
            return
        try:
            flow_val = self._instrument.readParameter(205)
            if flow_val is not None:
                self.data["flow"] = float(flow_val)
                self.data["value"] = float(flow_val)
            sp_val = self._instrument.readParameter(206)
            if sp_val is not None:
                self.data["setpoint"] = float(sp_val)
            temp_val = self._instrument.readParameter(142)
            if temp_val is not None:
                self.data["temperature"] = float(temp_val)
            sp = self.data["setpoint"]
            fl = self.data["flow"]
            if sp > 0:
                self.data["level"] = abs(fl - sp) / sp * 100.0 <= self._threshold_pct
            else:
                self.data["level"] = abs(fl) < 0.01
        except Exception as e:
            self.logger.warning(f"读取设备数据失败: {e}")

    @action(description="读取流量值")
    async def read_value(self, **kwargs) -> Dict[str, Any]:
        self.data["status"] = "Busy"
        try:
            self._poll_values()
            self.data["status"] = "Idle"
            return {
                "success": True,
                "value": self.data["flow"],
                "unit": self.data["capacity_unit"],
                "setpoint": self.data["setpoint"],
                "temperature": self.data["temperature"],
            }
        except Exception as e:
            self.data["status"] = "Idle"
            return {"success": False, "message": str(e)}

    @action(description="设置阈值百分比")
    async def set_threshold(self, threshold: float, **kwargs) -> bool:
        self._threshold_pct = float(threshold)
        self._poll_values()
        return True

    @action(description="设置流量设定值")
    async def set_setpoint(self, setpoint: float, **kwargs) -> bool:
        setpoint = float(setpoint)
        if self._instrument is None:
            self.logger.error("设备未连接")
            return False
        self.data["status"] = "Busy"
        try:
            self._instrument.writeParameter(206, setpoint)
            self.data["setpoint"] = setpoint
            await self._sleep(0.5)
            self._poll_values()
            self.data["status"] = "Idle"
            return True
        except Exception as e:
            self.logger.error(f"set_setpoint 失败: {e}")
            self.data["status"] = "Idle"
            return False

    @action(description="停止流量输出")
    async def stop(self, **kwargs) -> bool:
        return await self.set_setpoint(0.0)

    @action(description="按百分比设置设定值")
    async def set_setpoint_percent(self, percent: float, **kwargs) -> bool:
        percent = float(percent)
        if self._instrument is None:
            return False
        self.data["status"] = "Busy"
        try:
            raw_value = int(percent / 100.0 * 32000)
            raw_value = max(0, min(32000, raw_value))
            self._instrument.setpoint = raw_value
            await self._sleep(0.5)
            self._poll_values()
            self.data["status"] = "Idle"
            return True
        except Exception as e:
            self.data["status"] = "Idle"
            return False

    @action(description="设置用户标签")
    async def set_user_tag(self, tag: str, **kwargs) -> bool:
        tag = str(tag)[:12]
        if self._instrument is None:
            return False
        try:
            self._instrument.writeParameter(115, tag)
            self.data["user_tag"] = tag
            return True
        except Exception as e:
            return False

    @property
    @topic_config()
    def status(self) -> str:
        return self.data.get("status", "Idle")

    @property
    @topic_config()
    def flow(self) -> float:
        return self.data.get("flow", 0.0)

    @property
    @topic_config()
    def setpoint(self) -> float:
        return self.data.get("setpoint", 0.0)

    @property
    @topic_config()
    def temperature(self) -> float:
        return self.data.get("temperature", 0.0)

    @property
    @topic_config()
    def valve_output(self) -> float:
        return self.data.get("valve_output", 0.0)

    @property
    @topic_config()
    def capacity_unit(self) -> str:
        return self.data.get("capacity_unit", "")

    @property
    @topic_config()
    def user_tag(self) -> str:
        return self.data.get("user_tag", "")

    @property
    @topic_config()
    def level(self) -> bool:
        return self.data.get("level", False)

    @property
    @topic_config()
    def rssi(self) -> float:
        return float(self.data.get("rssi", 0))

    @property
    @topic_config()
    def value(self) -> float:
        return self.data.get("value", 0.0)