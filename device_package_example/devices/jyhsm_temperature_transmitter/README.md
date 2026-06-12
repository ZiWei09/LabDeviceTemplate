# JY-HSM 温度变送器


## 本地快速验证

插上硬件后，在设备目录执行：

```bash
python jyhsm_temperature_transmitter.py --port COM4 -v
```

加 `-v` 查看详细日志；部分设备支持 `--demo` 做低风险写操作验证。完整说明见 [SMOKE_TEST.md](../../SMOKE_TEST.md)。

## 简介

安徽久跃 JY-HSM 一体化温度变送器驱动，Modbus RTU 读取实时温度，支持阈值监控与提醒。

## 设备 ID

`jyhsm_temperature_transmitter`

## 通信方式

- 协议：Modbus RTU（RS485）
- 默认：9600 baud，8N1，从站地址 1

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM4` | 串口号 |
| `baudrate` | `9600` | 波特率 |
| `slave_address` | `1` | Modbus 从站地址 |
| `timeout` | `1.0` | 通信超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- 温度读取、阈值设置与监控（见驱动与 YAML）

## 状态属性

`status`、`temperature`、`target_temperature`、`alarm` 等

## Graph 示例

`graph_example_jyhsm_temperature_transmitter.json`

## 注意事项

- 寄存器 0x0000 为实时值 ×100（有符号整型）
- 浮点温度见 0x0002–0x0003（ABCD 格式）

## 产品资料

### 产品简介

**JY-HSM** 一体化温度变送器由安徽久跃仪表有限公司生产，将 Pt100/Pt1000 或热电偶信号转换为 Modbus 数字量或 4–20 mA 等输出，适用于工业现场温度监测。

### 产品特点

- 不锈钢封装，体积小巧，抗震性好
- 支持 RS485 Modbus RTU（本驱动）
- 可选 4–20 mA、0–10 V、0–5 V 输出型号

### 技术参数（JY-HSM 系列参考）

| 项目 | 参数 |
|---|---|
| 测量范围 | -200 ~ 1200 ℃（视传感器） |
| 准确度 | 0.2 ~ 0.5 ℃ / FS |
| 供电 | 12 ~ 36 V DC（常用 24 V） |
| 输出 | 4–20 mA / RS485 / 0–10 V 等 |
| 防护等级 | IP65 |
| 外壳材质 | 不锈钢 |
| 生产厂家 | 安徽久跃仪表有限公司 |

### 资料链接

- [久跃 JY-HSM 赫斯曼温度变送器](http://www.jiuyueyb.com/Products-14629713.html)
- [久跃一体化防爆温度变送器系列](http://www.jiuyueyb.com/SonList-620537.html)
