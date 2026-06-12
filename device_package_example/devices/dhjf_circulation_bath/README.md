# DHJF 循环水浴


## 本地快速验证

插上硬件后，在设备目录执行：

```bash
python dhjf_circulation_bath.py --port COM4 -v
```

加 `-v` 查看详细日志；部分设备支持 `--demo` 做低风险写操作验证。完整说明见 [SMOKE_TEST.md](../../SMOKE_TEST.md)。

## 简介

DHJF-2005A 低温恒温搅拌反应浴驱动，Modbus RTU 通信，支持温度设定、搅拌控制与多段程序。

## 设备 ID

`dhjf_circulation_bath`

## 通信方式

- 协议：Modbus RTU（RS485）
- 默认：9600 baud，8N1，从站 ID 1

## 依赖

- `pymodbus`
- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM4` | 串口号 |
| `slave_id` | `1` | Modbus 从站地址 |
| `baudrate` | `9600` | 波特率 |
| `timeout` | `1.0` | 通信超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- 温度/搅拌设定、程序段控制（见驱动与 YAML）

## 状态属性

`status`、`temp`、`temp_target`、`stir_speed`、`temp_warning` 等

## Graph 示例

`graph_dhjf_circulation_bath.json`

## 注意事项

- 温度寄存器为 ×100 整型写入
- 兼容 pymodbus 2.x / 3.x

## 产品资料

### 产品简介

DHJF-2005A 低温恒温搅拌反应浴（郑州长城科工贸）向外部提供恒温冷源或作为恒温槽使用，适用于化学、生物、物理检测等实验室，可冷却/加热烧瓶、试管等反应容器，也可为其他设备提供冷热源。

### 产品特点

- 温度控制采用 PID，控温精度高；内置磁力搅拌，转速 100–1000 rpm
- 全封闭风冷进口压缩机，304 不锈钢储液槽
- RS485 接口，遵循 Modbus RTU 协议（与本驱动一致）
- 支持多段程序温度控制

### 技术参数（DHJF-2005A，参考）

| 项目 | 参数 |
|---|---|
| 型号 | DHJF-2005A |
| 温度范围 | -20 ~ 99 ℃ |
| 温度稳定性 | ±0.2 ℃ |
| 显示精度 | 0.01 ℃ |
| 储液槽容积 | 5 L |
| 储液槽尺寸 | Φ250×130 mm |
| 开口尺寸 | Φ210 mm |
| 加热功率 | 1500 W |
| 整机功率 | 2210 W |
| 制冷剂 | R404A |
| 电源 | 220 V~，50 Hz |
| 外形尺寸 | 385×560×735 mm（W×D×H） |
| 生产厂家 | 郑州长城科工贸有限公司 |

### 资料链接

- [仪器网：DHJF-2005A 产品页](https://www.yiqi.com/product/detail_13619818.html)
- [长城科工贸：DHJF-2005 系列参数表](http://www.zzgwsit.com.cn/products/dwhwjb2005.html)
