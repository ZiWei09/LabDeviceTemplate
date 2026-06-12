# 兰格蠕动泵


## 本地快速验证

插上硬件后，在设备目录执行：

```bash
python longer_bt100.py --port COM4 -v
```

加 `-v` 查看详细日志；部分设备支持 `--demo` 做低风险写操作验证。完整说明见 [SMOKE_TEST.md](../../SMOKE_TEST.md)。

## 简介

兰格 BT100-2J 蠕动泵驱动，WJ/RJ ASCII 协议，RS485 通信，支持转速、方向与启停控制。

## 设备 ID

`longer_bt100`

## 通信方式

- 协议：RS485 自定义帧（flag E9 + 地址 + PDU + FCS）
- 默认：1200 baud，8N1E（偶校验）

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM4` | 串口号 |
| `baudrate` | `1200` | 波特率 |
| `address` | `1` | 设备地址 |
| `serial_timeout` | `0.5` | 读超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- `start_pump` / `stop_pump`：启停
- `set_speed` / `set_direction`：转速与方向

## 状态属性

`status`、`speed`、`direction`、`is_fullspeed`

## Graph 示例

`graph_longer_bt100.json`

## 注意事项

- 1200 baud 下帧传输较慢，建议 `serial_timeout` ≥ 0.5 s
- 字节填充规则：E8→E8 00，E9→E8 01

## 产品资料

### 产品简介

保定兰格 **BT100-2J** 是实验室常用精密蠕动泵，支持 RS485 通信及外控启停/调速，流量范围宽，可配多种泵头（YZ1515x、DG 系列等）。

### 技术参数

| 项目 | 参数 |
|---|---|
| 转速范围 | 0.1 ~ 100 rpm（正反转） |
| 流量范围 | 0.0002 ~ 380 ml/min（单管，视泵头/管径） |
| 转速分辨率 | 0.1 rpm |
| 通信 | RS485（本驱动 1200 baud WJ/RJ 协议） |
| 外控 | 启停、方向、0–5V/4–20mA/0–10kHz 调速 |
| 电源 | AC 90–260 V / 30 W |
| 防护等级 | IP31 |
| 外形尺寸 | 232 × 142 × 149 mm |
| 重量 | 2.3 kg |
| 生产厂家 | 保定兰格恒流泵有限公司 |

### 资料链接

- [兰格 BT100-2J 官方产品页](http://shop.longerpump.com.cn/ProductShow_6824.html)
- [BT100-2J 使用说明书](https://rudongbeng.com/article-68.html)
