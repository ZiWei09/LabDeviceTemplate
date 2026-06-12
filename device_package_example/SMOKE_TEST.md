# 本地硬件冒烟测试

插上硬件后，进入设备目录执行对应命令，几秒内即可看到连接与读数反馈。

## 通用参数

| 参数 | 说明 |
|------|------|
| `-v` / `--verbose` | 输出详细日志，排查串口/协议问题 |
| `--demo` | 执行低风险写操作（部分设备支持，注意安全） |
| `--port COMx` | 覆盖默认串口 |

## 各设备命令

```bash
# 安装依赖（按设备 README 为准，常见为 pyserial / pymodbus）
pip install pyserial pymodbus

# 华控模拟量输出
python devices/hk_a0/hk_a0.py --port COM3 -v
python devices/hk_a0/hk_a0.py --port COM3 --demo   # Ch1 输出 0.1V 后归零

# JY-HSM 温度变送器
python devices/jyhsm_temperature_transmitter/jyhsm_temperature_transmitter.py --port COM4 -v

# 兰格蠕动泵 BT100-2J
python devices/longer_bt100/longer_bt100.py --port COM4 -v
python devices/longer_bt100/longer_bt100.py --port COM4 --demo   # 低速运转数秒后停止

# Bronkhorst 流量计
python devices/bronkhorst_el_flow/bronkhorst_el_flow.py --port COM12 -v

# Runze SY-03B 注射泵（initialize 含归零，约 10~60 秒）
python devices/runze_sy03b_t08/runze_sy03b_t08.py --port COM4 -v

# XYZ 光电台
python devices/xyz_guangdian/xyz_guangdian.py --port COM35 -v

# Duco GCR5 机械臂（网口）
python devices/duco_gcr5/duco_gcr5.py --ip 192.168.1.10 -v

# 4V110 电磁阀
python devices/solenoid_valve_4v110/solenoid_valve_4v110.py --port COM3 -v
python devices/solenoid_valve_4v110/solenoid_valve_4v110.py --port COM3 --demo

# 大恒 GCI060505 光源
python devices/daheng_gci060505/daheng_gci060505.py --port COM14 -v
python devices/daheng_gci060505/daheng_gci060505.py --port COM14 --demo

# CNI 532nm 激光器（仅握手，不开启激光）
python devices/cni_laser_msl_u_532/cni_laser_msl_u_532.py --port COM13 -v

# DHJF 循环浴
python devices/dhjf_circulation_bath/dhjf_circulation_bath.py --port COM4 -v

# CHI760E 电化学工作站（验证软件路径，不跑实验）
python devices/chi760e/chi760e.py --chi-exe-path "C:/CHI/chi760e.exe" --data-folder ./chi_data -v

# Zolix Omni-λ 单色仪
python devices/zolix_omni_lambda/zolix_omni_lambda.py --port COM11 -v

# CMOS 探测器
python devices/cmos_detector/cmos_detector.py --port COM10 -v
python devices/cmos_detector/cmos_detector.py --port COM10 --demo   # 采集一帧

# 大恒 HD-R630c 相机（需 Galaxy SDK）
python devices/daheng_hd_r630c/daheng_hd_r630c.py -v
python devices/daheng_hd_r630c/daheng_hd_r630c.py --demo   # 拍一张图

# 电解池夹爪
python devices/electrolytic_cell_gripper/electrolytic_cell_gripper.py --port COM29 -v
```

## 成功输出示例

```
==================================================
连接设备...
✓ 连接成功
==================================================
只读验证...
  结果: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
✓ 只读验证完成
✓ 已断开连接
==================================================
冒烟测试通过
```

## 与 Uni-Lab 的关系

| 阶段 | 命令 | 目的 |
|------|------|------|
| 1. 硬件冒烟 | `python <驱动>.py` | 确认驱动能控制本机硬件 |
| 2. Schema 校验 | `unilab --check_mode --devices ./device_package_example --external_devices_only` | CI / 注册表 |
| 3. 框架集成 | `unilab -g graph.json --backend simple` | 接入 Uni-Lab |

冒烟脚本仅在 `python <驱动>.py` 时执行，**不影响** `import` 与 registry 扫描。
