"""
本地硬件冒烟测试通用工具。

各设备驱动底部的 ``if __name__ == "__main__"`` 块使用本模块；
仅在 ``python <driver>.py`` 时加载，不影响 import 与 registry 扫描。
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import logging
import sys
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional, Union

AsyncMainFn = Callable[[], Awaitable[int]]


def setup_smoke_path() -> None:
    """将 CosLab_SHU_Device_package 加入 sys.path，便于各驱动 import 本模块。"""
    pkg_root = Path(__file__).resolve().parent
    root_str = str(pkg_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def setup_logging(verbose: bool = False) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def section(title: str) -> None:
    print("=" * 50)
    print(title)


def ok(msg: str) -> None:
    print(f"✓ {msg}")


def fail(msg: str) -> None:
    print(f"✗ {msg}")


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-v", "--verbose", action="store_true", help="输出详细日志")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="执行低风险 demo 写操作（注意安全）",
    )


def add_serial_args(
    parser: argparse.ArgumentParser,
    *,
    default_port: str = "COM4",
    default_baudrate: int = 9600,
) -> None:
    parser.add_argument("--port", default=default_port, help="串口号")
    parser.add_argument("--baudrate", type=int, default=default_baudrate, help="波特率")


def add_ip_args(
    parser: argparse.ArgumentParser,
    *,
    default_ip: str = "192.168.1.10",
    default_port: int = 2000,
) -> None:
    parser.add_argument("--ip", default=default_ip, help="设备 IP")
    parser.add_argument("--cmd-port", type=int, default=default_port, dest="cmd_port", help="命令端口")


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


async def smoke_lifecycle(
    dev: Any,
    *,
    read_fn: Optional[Callable[[Any], Union[Any, Awaitable[Any]]]] = None,
    demo_fn: Optional[Callable[[Any], Union[Any, Awaitable[Any]]]] = None,
    do_demo: bool = False,
) -> int:
    """标准冒烟流程：initialize → 只读验证 → 可选 demo → cleanup。"""
    section("连接设备...")
    init_ok = await _maybe_await(dev.initialize())
    if not init_ok:
        fail("initialize 失败")
        return 1
    ok("连接成功")

    try:
        if read_fn is not None:
            section("只读验证...")
            result = await _maybe_await(read_fn(dev))
            print(f"  结果: {result}")
            ok("只读验证完成")

        if do_demo and demo_fn is not None:
            section("Demo 操作（--demo）...")
            result = await _maybe_await(demo_fn(dev))
            print(f"  结果: {result}")
            ok("Demo 完成")
    finally:
        await _maybe_await(dev.cleanup())
        ok("已断开连接")

    section("冒烟测试通过")
    return 0


def run_smoke(main_fn: AsyncMainFn) -> None:
    sys.exit(asyncio.run(main_fn()))
