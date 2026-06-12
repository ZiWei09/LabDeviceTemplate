# 电解池夹爪

## 简介

电解池夹爪工作站驱动，整合 2 台**俏优灵**步进电机（水平/垂直）与 1 台**大寰** PGE 平行电爪。

对外提供两类动作：

- **工艺动作**：`pick_sample` / `place_sample`（一键完整夹取/放置）
- **手动动作**：`move_motor_mm` / `move_motor_steps` 等（实验人员单轴调试）

## 设备 ID

`electrolytic_cell_gripper`

## 通信方式

- 协议：Modbus RTU（RS485），三台设备共用同一串口
- 默认：115200 baud；电机 slave 1/2，夹爪 slave 5

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM29` | 串口号 |
| `baudrate` | `115200` | 波特率 |
| `timeout` | `0.5` | 读超时 (s) |
| `motor1_slave_id` | `1` | 水平电机地址 |
| `motor2_slave_id` | `2` | 垂直电机地址 |
| `gripper_slave_id` | `5` | 夹爪地址 |
| `motor1_steps_per_mm` | 未设 | 水平轴 mm→步 标定（用 `move_motor_mm` 时必填） |
| `motor2_steps_per_mm` | 未设 | 垂直轴 mm→步 标定（用 `move_motor_mm` 时必填） |

## 主要动作

### 工艺动作（实验常规使用）

- `pick_sample`：夹取样品完整序列
- `place_sample`：放下样品完整序列

### 手动动作（单轴 / 夹爪调试）

| 动作 | 说明 |
|---|---|
| `move_motor_steps(motor, steps)` | 绝对定位，`motor`：1=水平，2=垂直 |
| `move_motor_mm(motor, mm)` | 按 mm 绝对定位，需 config 标定 `steps_per_mm` |
| `read_motor_position(motor)` | 读当前位置（步） |
| `motor_set_zero(motor)` | 当前位置设为零点 |
| `gripper_open` / `gripper_close` | 夹爪张开 / 闭合 |

### 通用

- `initialize` / `cleanup`：串口连接与释放
- `emergency_stop`：电机急停

## 状态属性

`status`

## Graph 示例

`graph_example_electrolytic_cell_gripper.json`

## 注意事项

- **工艺动作**（pick/place）内步数/速度已硬编码，改工艺需改驱动或后续参数化
- **手动动作**用步数最可靠；mm 需先标定 `motor1_steps_per_mm`、`motor2_steps_per_mm`
- 支持 lazy serial：首次动作时自动打开串口

### mm 标定说明

俏优灵驱控底层单位为**步**。实验人员习惯用 mm 时，在 graph config 中配置：

```json
"motor1_steps_per_mm": 2000,
"motor2_steps_per_mm": 2000
```

标定方法：手动走已知距离（如 10 mm），读取 `read_motor_position` 返回的步数，除以 10 得到 `steps_per_mm`。

## 产品资料

### 产品简介

**电解池夹爪工作站**为本实验室定制集成系统，非商用整机。由 **2 台俏优灵步进电机**（水平/垂直滑台）+ **1 台大寰 PGE 平行电爪**组成，经 RS485 Modbus RTU 共用一条总线控制。

### 组成与通信

| 设备 | 品牌/系列 | Modbus 从站 | 功能 |
|---|---|---|---|
| 水平滑台电机 | 俏优灵 | 1 | X 方向 |
| 垂直滑台电机 | 俏优灵 | 2 | Z 方向 |
| 平行电爪 | 大寰 PGE | 5 | 夹爪开合 |

- 通信：115200 baud，8N1
- 高层动作：`pick_sample`（夹取）、`place_sample`（放置）

### 子设备参考（公开资料）

**大寰 PGE 系列平行电爪**

- 工业薄型平行电爪，标配 Modbus RTU（RS485）
- 常用功能码 03/06，24 V DC 供电
- 具体型号（如 PGE-5-26、PGE-8-14 等）以实验室实物为准

**俏优灵步进电机驱控**

- 深圳市俏优灵科技有限公司 RS485 步进驱控产品
- 支持 Modbus RTU 位置/速度控制（本驱动使用 FC 03/06/10）
- 具体型号以实验室实物为准

### 资料链接

- [大寰机器人 PGE 系列产品页](https://www.dh-robotics.com/product/pge)
- [大寰 PGE 系列操作手册 PDF](https://www.dh-robotics.com/wp-content/uploads/2022/12/PGE%E7%B3%BB%E5%88%97%E9%A9%B1%E6%8E%A7%E4%B8%80%E4%BD%93_%E4%BA%A7%E5%93%81%E6%93%8D%E4%BD%9C%E6%89%8B%E5%86%8C_v3.2.pdf)

### 说明

- 运动步数、速度参数已在驱动内按现场工艺硬编码
- 整机无公开说明书；调试与变更需结合实验室机械与电气文档
