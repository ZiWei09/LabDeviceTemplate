# Bronkhorst MFC


## 本地快速验证

插上硬件后，在设备目录执行：

```bash
python bronkhorst_el_flow.py --port COM12 -v
```

加 `-v` 查看详细日志；部分设备支持 `--demo` 做低风险写操作验证。完整说明见 [SMOKE_TEST.md](../../SMOKE_TEST.md)。

## 简介

Bronkhorst EL-FLOW Prestige 质量流量控制器（MFC）驱动，支持读取流量/温度、设置设定值与用户标签。

## 设备 ID

`bronkhorst_el_flow`

## 通信方式

- 协议：RS232/RS485（`propar` 库）
- 默认：38400 baud，从站地址 3

## 依赖

- `propar`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM12` | 串口号 |
| `baudrate` | `38400` | 波特率 |
| `address` | `3` | 设备地址 |
| `channel` | `1` | 通道号 |
| `threshold` | `2.0` | 流量偏差阈值（%） |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- `read_value`：读取流量、设定值、温度
- `set_setpoint` / `set_setpoint_percent` / `stop`：流量控制
- `set_threshold` / `set_user_tag`：参数设置

## 状态属性

`status`、`flow`、`setpoint`、`temperature`、`valve_output`、`capacity_unit`、`user_tag`、`level`、`rssi`、`value`

## Graph 示例

`graph_example_bronkhorst_el_flow.json`

## 启动验证

```bash
unilab --check_mode --devices ./device_package_example --external_devices_only
unilab --devices ./device_package_example --external_devices_only \
  -g device_package_example/devices/bronkhorst_el_flow/graph_example_bronkhorst_el_flow.json
```

## 产品资料

### 产品简介

Bronkhorst EL-FLOW Prestige 是面向实验室与工业应用的高端气体质量流量控制器/流量计（MFC/MFM），内置 100 种气体数据库，支持实时温压补偿，精度与长期稳定性较高。

### 产品特点

- 量程约 0.014 mlₙ/min ~ 100 ln/min（视具体型号）
- 精度：±0.5% Rd + ±0.1% FS（标准）
- 工作压力最高 100 bar；工作温度 -10 ~ +70 ℃
- 通信：RS232 标准，可选 Modbus/PROFIBUS/EtherCAT 等
- 防护等级 IP40

### 资料链接

- [Bronkhorst 官方产品页](https://www.bronkhorst.com/products/gas-flow/el-flow-prestige/)
- [EL-FLOW Prestige 数据手册 PDF](https://pdf.directindustry.com/pdf/bronkhorst/el-flow-prestige-mass-flow-meters-controllers-gas/15524-624442.html)

> 说明：本驱动通过 `propar` 库经 RS232 通信，请确认现场仪表接口与地址配置。
