"""
jidianqi_tuigan.py

RS485 Modbus relay / linear-actuator controller for CX5208W-style relay module.
This version DOES NOT use pyserial. It reuses the WinSerial object from
xyz_control_shulab.py, so it can share the same COM port with the XYZ platform.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol
import time


class WinSerialLike(Protocol):
    def reset_buffers(self) -> None: ...
    def write(self, data: bytes): ...
    def read(self, size: int) -> bytes: ...


def relay_modbus_crc(data: Iterable[int]) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b & 0xFF
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
            crc &= 0xFFFF
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def build_write_single_coil(slave_addr: int, coil_addr: int, on: bool) -> bytes:
    payload = bytes([
        slave_addr & 0xFF,
        0x05,
        (coil_addr >> 8) & 0xFF,
        coil_addr & 0xFF,
        0xFF if on else 0x00,
        0x00,
    ])
    return payload + relay_modbus_crc(payload)


def hex_bytes(data: bytes | bytearray | Iterable[int]) -> str:
    return " ".join(f"{b & 0xFF:02X}" for b in data)


@dataclass
class RelayActuatorConfig:
    slave_addr: int = 0x04
    response_wait_s: float = 0.08
    command_gap_s: float = 0.05
    strict_ack: bool = False
    do1_coil: int = 0x0000
    do2_coil: int = 0x0001


class RelayActuatorController:
    def __init__(
        self,
        serial_port: WinSerialLike,
        config: Optional[RelayActuatorConfig] = None,
        *,
        debug: bool = False,
    ):
        self.ser = serial_port
        self.config = config or RelayActuatorConfig()
        self.debug = debug
        self.state = "unknown"

    def send_frame(self, frame: bytes, expected_len: int = 8) -> bytes:
        self.ser.reset_buffers()
        written = self.ser.write(frame)
        if written is not None and int(written) != len(frame):
            raise IOError(f"继电器发送不完整：{written}/{len(frame)} bytes")

        if self.debug:
            print("[Relay TX]", hex_bytes(frame))

        time.sleep(self.config.response_wait_s)
        resp = self.ser.read(expected_len)

        if self.debug:
            print("[Relay RX]", hex_bytes(resp) if resp else "<no response>")

        if self.config.strict_ack:
            if len(resp) != expected_len:
                raise TimeoutError(f"继电器响应长度不足，期望 {expected_len}，实际 {len(resp)}，响应={hex_bytes(resp)}")
            if resp[-2:] != relay_modbus_crc(resp[:-2]):
                raise ValueError(f"继电器 CRC 校验失败，响应={hex_bytes(resp)}")
            if resp[:6] != frame[:6]:
                raise RuntimeError(f"继电器写线圈回包异常，发送={hex_bytes(frame)}，响应={hex_bytes(resp)}")

        time.sleep(self.config.command_gap_s)
        return resp

    def write_coil(self, coil_addr: int, on: bool) -> bytes:
        frame = build_write_single_coil(self.config.slave_addr, coil_addr, on)
        return self.send_frame(frame, expected_len=8)

    def set_do1(self, on: bool) -> bytes:
        return self.write_coil(self.config.do1_coil, on)

    def set_do2(self, on: bool) -> bytes:
        return self.write_coil(self.config.do2_coil, on)

    def stop(self) -> None:
        self.set_do1(False)
        self.set_do2(False)
        self.state = "stop"

    def forward(self, duration_s: float | None = None, stop_after: bool = False) -> None:
        self.set_do2(False)
        self.set_do1(True)
        self.state = "push"
        if duration_s is not None:
            time.sleep(duration_s)
            if stop_after:
                self.stop()

    def backward(self, duration_s: float | None = None, stop_after: bool = False) -> None:
        self.set_do1(False)
        self.set_do2(True)
        self.state = "pull"
        if duration_s is not None:
            time.sleep(duration_s)
            if stop_after:
                self.stop()

    def push(self, duration_s: float | None = None, stop_after: bool = False) -> None:
        self.forward(duration_s=duration_s, stop_after=stop_after)

    def pull(self, duration_s: float | None = None, stop_after: bool = False) -> None:
        self.backward(duration_s=duration_s, stop_after=stop_after)

    def go_origin_state(self) -> None:
        self.pull()


LinearActuator485 = RelayActuatorController
LinearActuatorConfig = RelayActuatorConfig


def interactive_main() -> None:
    from xyz_control_shulab import WinSerial, PORT, BAUDRATE

    shared_serial = WinSerial(PORT, BAUDRATE)
    try:
        shared_serial.open()
        actuator = RelayActuatorController(shared_serial, debug=True)
        print("推杆/继电器测试启动。命令：push / pull / stop / q")
        actuator.go_origin_state()
        while True:
            cmd = input("actuator > ").strip().lower()
            if cmd in {"q", "quit", "exit"}:
                actuator.go_origin_state()
                break
            if cmd in {"push", "f", "forward"}:
                actuator.push()
                print("已前推。")
            elif cmd in {"pull", "b", "backward"}:
                actuator.pull()
                print("已后退/回拉。")
            elif cmd in {"stop", "s"}:
                actuator.stop()
                print("已停止。")
            else:
                print("无法识别。可用：push / pull / stop / q")
    finally:
        shared_serial.close()
        print("串口已关闭。")


if __name__ == "__main__":
    interactive_main()
