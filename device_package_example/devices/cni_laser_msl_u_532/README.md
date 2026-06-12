# CNI 532nm 激光器

## 简介

CNI MSL-U-532-50mW 激光器驱动，通过 Arduino Nano + MCP4725 DAC 控制功率，串口发送 `SET 0-100` 指令。

## 设备 ID

`cni_laser_msl_u_532`

## 通信方式

- 协议：Arduino 串口 ASCII（9600 baud）
- 固件标识：`ArduinoUno_LaserValve`

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM13` | 串口号 |
| `baudrate` | `9600` | 波特率 |
| `timeout` | `2.0` | 通信超时 (s) |
| `max_power_mw` | `50.0` | 最大功率 (mW) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- `turn_on` / `turn_off`：开关激光
- `set_power` / `set_power_percentage`：功率设置
- `emergency_stop`：紧急关断（DAC 置 0）

## 状态属性

`status`、`laser_on`、`power`、`power_percentage`、`wavelength`

## Graph 示例

`graph_example_cni_laser_msl_u_532.json`

## 注意事项

- 上电后需等待 Arduino 复位（约 2.5 s）
- 激光器使用前请确认光路安全

## 产品资料

### 产品简介

长春新产业（CNI）**MSL-U-532** 是超紧凑单纵模 532 nm 连续绿光激光器，TEM00 模式，适用于拉曼光谱、DNA 测序、全息/干涉测量等。

### 技术参数（MSL-U-532，参考）

| 项目 | 参数 |
|---|---|
| 波长 | 532 ± 1 nm |
| 工作模式 | CW 连续 |
| 输出功率 | 1 ~ 1000 mW（视订购配置，本驱动默认 50 mW） |
| 线宽 | < 0.00001 nm |
| 相干长度 | > 50 m |
| M² | < 1.2 |
| 横模 | TEM00 |
| 功率稳定性 | < 1~5%（4 h，RMS） |
| 振幅噪声 | < 0.5%（1 Hz~20 MHz） |
| 工作温度 | 10 ~ 40 ℃ |
| 预期寿命 | ~10000 h |

### 资料链接

- [CNI 532 nm 单纵模激光系列](https://www.cnilaser.com/single_frequency_laser532.htm)
- [MSL-U-532 规格（Oceanhood)](https://en.oceanhoodtw.com/products_detail/1046)

> 说明：本实验室通过 Arduino + MCP4725 DAC 经串口 `SET 0-100` 控制功率，非原厂标准 RS232 协议。
