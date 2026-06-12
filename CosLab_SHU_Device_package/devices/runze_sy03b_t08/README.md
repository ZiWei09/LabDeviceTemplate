# 润泽注射泵


## 本地快速验证

插上硬件后，在设备目录执行：

```bash
python runze_sy03b_t08.py --port COM4 -v
```

加 `-v` 查看详细日志；部分设备支持 `--demo` 做低风险写操作验证。完整说明见 [SMOKE_TEST.md](../../SMOKE_TEST.md)。

## 简介

润泽 SY-03B 陶瓷注射泵（T-08 八通分配阀）驱动，ASCII DT 格式 RS232/RS485 通信，25 mL 注射器。

## 设备 ID

`runze_sy03b_t08`

## 通信方式

- 协议：ASCII DT 格式
- 默认：9600 baud

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM4` | 串口号 |
| `baudrate` | `9600` | 波特率 |
| `address` | `0` | 设备地址开关值 (0–15) |
| `syringe_volume` | `25.0` | 注射器体积 (mL) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- 吸液、分液、阀位切换、复位等（见驱动与 YAML）

## 状态属性

`status`、`mode`、`position`、`valve_port` 等

## Graph 示例

`graph_runze_sy03b_t08.json`

## 注意事项

- 全行程约 6000 步（25 mL）
- T-08 阀为 8 口分配阀，C 口连通 1–8

## 产品资料

### 产品简介

南京润泽 **SY-03B** 是高精度工业陶瓷注射泵，本配置配 **T-08 八通分配阀**（C 口可选择连通 1–8 号端口）。采用 ASCII DT 协议经 RS485 控制，标准注射器 25 mL（6000 步全行程）。

### 技术参数

| 项目 | 参数 |
|---|---|
| 型号 | ZSB-SY03B-T08 |
| 额定行程 | 60 mm（6000 步标准 / 48000 步微步） |
| 液量准确度 | ≤ 1%（额定行程） |
| 重复性 | 0.3 ~ 0.5% |
| 线速度 | 0.01 ~ 60 mm/s |
| 适配注射器 | 25 μl ~ 25 ml |
| 通信 | RS232/RS485，9600~115200 bps |
| 协议 | ASCII DT / Modbus（视固件） |
| 电源 | DC 24 V / 3 A |
| 重量 | 约 2.2 kg |
| 生产厂家 | 南京润泽流体控制设备有限公司 |

### 资料链接

- [SY-03B 产品页（中文）](https://www.runzefluidsystem.com/list_19/1904.html)
- [SY-03B 英文手册 PDF](https://www.runzefluid.com/uploads/file/sy-03b-syringe-pump.pdf)
- [SY-03 V2.4 协议说明 PDF](https://www.runzefluid.com/uploads/file/sy-03-v2-1.pdf)
