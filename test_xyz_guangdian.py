#!/usr/bin/env python3
"""
XYZ光电设备测试脚本
测试串口连接和基本功能
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加设备包路径
sys.path.insert(0, str(Path(__file__).parent / "device_package_example"))

from devices.xyz_guangdian.xyz_guangdian import XYZGuangdian

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_xyz_device():
    """测试XYZ光电设备"""

    # 设备配置
    config = {
        'port': '/dev/tty.usbserial-BG02ANBF',  # macOS串口
        'baudrate': 9600,
        'timeout': 2.0,
        'retry_count': 3,
        'retry_delay': 0.1
    }

    print("=" * 60)
    print("XYZ光电设备测试")
    print("=" * 60)
    print(f"串口: {config['port']}")
    print(f"波特率: {config['baudrate']}")
    print("-" * 60)

    # 创建设备实例
    device = XYZGuangdian(
        device_id="xyz_test_001",
        config=config
    )

    try:
        # 1. 初始化设备
        print("\n[1/6] 初始化设备...")
        success = await device.initialize()
        if not success:
            print("❌ 初始化失败")
            print(f"状态: {device.data['status']}")
            print(f"错误码: {device.data['error_code']}")
            return False
        print("✅ 初始化成功")

        # 2. 读取当前状态
        print("\n[2/6] 读取设备状态...")
        print(f"状态: {device.data['status']}")
        print(f"X轴位置: {device.data['position_x']:.2f} mm")
        print(f"Y轴位置: {device.data['position_y']:.2f} mm")
        print(f"Z轴位置: {device.data['position_z']:.2f} mm")
        print(f"推杆状态: {device.data['push_rod_status']}")
        print(f"是否使能: {device.data['is_enabled']}")
        print(f"是否回零: {device.data['is_homed']}")

        # 3. 使能设备
        print("\n[3/6] 使能设备...")
        success = await device.enable()
        if success:
            print("✅ 使能成功")
        else:
            print("❌ 使能失败")

        # 4. 测试获取位置
        print("\n[4/6] 获取当前位置...")
        position = await device.get_position()
        if position:
            print(f"✅ 位置读取成功: X={position['x']:.2f}, Y={position['y']:.2f}, Z={position['z']:.2f} mm")
        else:
            print("❌ 位置读取失败")

        # 5. 测试推杆释放
        print("\n[5/6] 测试推杆释放...")
        success = await device.release_glass()
        if success:
            print("✅ 推杆释放成功")
        else:
            print("⚠️  推杆释放失败（可能已经是释放状态）")

        # 6. 禁用设备
        print("\n[6/6] 禁用设备...")
        success = await device.disable()
        if success:
            print("✅ 禁用成功")
        else:
            print("❌ 禁用失败")

        # 清理
        print("\n[清理] 关闭连接...")
        await device.cleanup()
        print("✅ 清理完成")

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 确保清理
        try:
            await device.cleanup()
        except:
            pass

if __name__ == "__main__":
    result = asyncio.run(test_xyz_device())
    sys.exit(0 if result else 1)
