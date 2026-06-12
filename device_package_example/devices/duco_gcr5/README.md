# DUCO 协作机器人


## 本地快速验证

插上硬件后，在设备目录执行：

```bash
python duco_gcr5.py --ip 192.168.1.10 -v
```

加 `-v` 查看详细日志；部分设备支持 `--demo` 做低风险写操作验证。完整说明见 [SMOKE_TEST.md](../../SMOKE_TEST.md)。

## 简介

新松 DUCO GCR5-910 协作机器人驱动，TCP 2000 端口纯文本协议，支持上电、使能、运行程序与速度调节。

> 多可（DUCO）源自中科新松有限公司，为国内新松旗下智能机器人子品牌。

## 设备 ID

`duco_gcr5`

## 通信方式

- 协议：TCP 文本命令
- 默认：命令端口 2000，状态端口 2001

## 依赖

无额外 Python 包（标准库 `socket`）

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `ip` | `192.168.1.10` | 机器人 IP |
| `cmd_port` | `2000` | 命令端口 |
| `status_port` | `2001` | 状态推送端口 |
| `timeout` | `5.0` | 连接超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与断开
- `power_on` / `power_off` / `enable` / `disable`：电源与使能
- `run_program` / `stop` / `set_speed`：程序与速度控制

## 状态属性

机器人状态、程序状态、操作模式等（见驱动 `data` 字段）

## Graph 示例

`graph_example_duco_gcr5.json`

## 注意事项

- 需与机器人在同一网段
- 运行程序前需完成上电与使能流程

## 产品资料

### 产品简介

**多可（DUCO）** 源自中科新松有限公司，是国内新松旗下智能机器人子品牌。**GCR5-910** 为其 6 轴协作机器人，额定负载 5 kg，工作半径 917 mm，适用于涂胶、装配、检测、上下料等场景。本驱动通过 TCP 2000 端口文本协议控制。

### 技术参数

| 项目 | 参数 |
|---|---|
| 自由度 | 6 |
| 额定负载 | 5 kg |
| 工作半径 | 917 mm |
| 重复定位精度 | ±0.02 mm |
| 末端最大速度 | 3.6 m/s |
| 直线最大速度 | 1.5 m/s |
| 关节速度 | 225 °/s |
| 防护等级 | IP54 / IP65 |
| 典型功耗 | 200 W |
| 通信 | TCP/IP、Modbus/TCP、Profinet、Ethernet/IP |
| 净重 | 22 kg |
| 品牌/厂商 | 多可 DUCO（中科新松 / 新松智能机器人子品牌） |

### 资料链接

- [DUCO 多可 GCR5-910 官网](https://ducorobots.cn/prodetail/2.html)
- [DUCO GCR5-910 英文规格](https://www.ducorobots.com/Gcr-series-cobot/gcr5-910)
