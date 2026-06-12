# XYZ 三维平台

## 简介

XYZ 光电工作台驱动，控制三轴运动平台与推杆装置，Modbus RTU 通信，支持绝对/相对移动与推杆夹紧/释放。

## 设备 ID

`xyz_guangdian`

## 通信方式

- 协议：Modbus RTU（RS485）
- 默认：9600 baud
- 从站：X=0x01，Y=0x02，Z=0x03，推杆=0x04

## 依赖

- `pyserial`（或 pymodbus，见驱动实现）

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM35` | 串口号 |
| `baudrate` | `9600` | 波特率 |
| `timeout` | `2.0` | 通信超时 (s) |
| `retry_count` | `3` | 重试次数 |
| `retry_delay` | `0.1` | 重试间隔 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- 三轴移动、回零、推杆夹紧/释放/停止（见驱动与 YAML）

## 状态属性

`status`、`x_position`、`y_position`、`z_position`、`push_rod_status`、`error_code` 等

## Graph 示例

`graph_example_xyz_guangdian.json`

## 注意事项

- 推杆控制已内嵌在驱动中，无需额外脚本
- 多轴共用同一 RS485 总线时注意从站地址

## 产品资料

### 产品简介

**XYZ 光电工作台**为本实验室定制三轴运动平台 + 推杆系统，采用 Modbus RTU（RS485）控制。X/Y/Z 三轴步进电机与推杆装置共用总线，从站地址分别为 0x01、0x02、0x03、0x04。

### 系统组成

| 从站 | 地址 | 功能 |
|---|---|---|
| X 轴 | 0x01 | 水平运动 |
| Y 轴 | 0x02 | 进给运动 |
| Z 轴 | 0x03 | 升降运动 |
| 推杆 | 0x04 | 夹紧/释放 |

### 说明

- 无公开商用型号与说明书；参数与限位以实验室机械设计为准
- 推杆控制已内嵌于 `xyz_guangdian` 驱动，无需额外脚本
