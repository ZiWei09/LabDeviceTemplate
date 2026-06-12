# GCI-060505 LED 光源

## 简介

大恒 GCI-060505 LED 光源驱动，通过 Arduino + MCP4725 DAC 控制亮度，支持 PING/ON/OFF/BRIGHT/STATUS 指令。

## 设备 ID

`daheng_gci060505`

## 通信方式

- 协议：Arduino 串口 ASCII
- 默认：115200 baud

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM14` | 串口号 |
| `baudrate` | `115200` | 波特率 |
| `timeout` | `2` | 读超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- `turn_on` / `turn_off`：开关光源
- `set_brightness`：设置亮度 0–100%
- `refresh_status`：从 Arduino 读取当前状态

## 状态属性

`status`、`brightness`、`light_on`、`max_brightness`

## Graph 示例

`graph_example_daheng_gci060505.json`

## 注意事项

- 打开串口后 Arduino 会 DTR 复位，需等待约 2 s

## 产品资料

### 产品简介

大恒光电 **GCI** 系列为光学仪器配件产品线。本实验室 **GCI-060505** 为 LED 光源模组，经 **Arduino + MCP4725 DAC** 二次开发，通过串口 ASCII 指令控制开关与亮度（0–100%）。

### 集成方案特点

- 通信：115200 baud 串口（PING / ON / OFF / BRIGHT / STATUS）
- 亮度：0–100% PWM/DAC 模拟调光
- 适用于显微照明、相机校正等场景

### 资料链接

- [大恒光电官网](https://www.golight.com.cn/)（GCI 系列产品）

> 说明：未找到 GCI-060505 公开详细规格书；光源 LED 电气参数取决于具体灯珠与驱动电路，请以实验室 BOM 为准。
