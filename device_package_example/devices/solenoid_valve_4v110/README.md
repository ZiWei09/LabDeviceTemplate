# 4V110 电磁阀

## 简介

亚德客 4V110-06 DC24V 二位五通电磁阀驱动，通过 Arduino Uno GPIO + 继电器模块控制 24 V 线圈。

## 设备 ID

`solenoid_valve_4v110`

## 通信方式

- 协议：Arduino 串口 ASCII
- 指令：`VALVE ON` / `VALVE OFF` / `VALVE?`
- 默认：9600 baud

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM3` | 串口号 |
| `baudrate` | `9600` | 波特率 |
| `timeout` | `1` | 读超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放（初始化时关闭阀门）
- `open` / `close`：开/关电磁阀
- `set_valve_position`：设置 `"Open"` / `"Closed"`
- `is_open` / `is_closed`：查询状态
- `send_command`：发送自定义指令

## 状态属性

`status`、`valve_position`

## Graph 示例

`graph_example_solenoid_valve_4v110.json`

## 注意事项

- 可与 CNI 激光器共用同一 Arduino 固件（不同指令集）
- 未知位置参数时默认关闭（安全策略）

## 产品资料

### 产品简介

亚德客（Airtac）**4V110-06** 是五口二位单电控电磁阀，进气/出气口径 PT1/8（G1/8），用于控制气缸或流体换向。本实验室通过 Arduino 继电器模块经 24 V 线圈驱动。

### 技术参数

| 项目 | 参数 |
|---|---|
| 型号 | 4V110-06 |
| 型式 | 五口二位，内先导 |
| 接管口径 | PT1/8（G1/8） |
| 有效截面积 | 10 ~ 12 mm²（Cv ≈ 0.56–0.67） |
| 使用压力 | 0.15 ~ 0.8 MPa |
| 耐压 | 1.2 MPa |
| 工作介质 | 经 40 μm 过滤的压缩空气 |
| 工作温度 | -20 ~ 70 ℃ / 5 ~ 50 ℃ |
| 线圈功耗 | 2.5 ~ 3 W（DC 24 V 常见） |
| 防护等级 | IP65 |
| 重量 | 约 120 g |
| 品牌 | 亚德客 Airtac |

### 资料链接

- [亚德客 4V110-06 参数（代理商）](http://www.herionimi.com/Products-36341907.html)
- [AirTAC 4V110-06 规格表](https://mech-mall.com/product/4v110-06-solenoid-valve)

> 说明：本驱动经 Arduino 串口发送 `VALVE ON/OFF`，非直接驱动电磁阀线圈。
