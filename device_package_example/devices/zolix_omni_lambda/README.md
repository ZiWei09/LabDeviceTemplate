# Zolix Omni-λ

## 简介

Zolix Omni-λ 单色仪/光谱仪驱动，串口 ASCII 指令控制波长/波数移动、光栅切换与出入口选择。

## 设备 ID

`zolix_omni_lambda`

## 通信方式

- 协议：Serial ASCII，`\r` 结束符
- 默认：19200 baud，8N1
- 响应以 `OK` 或 `Exx` 结尾

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM11` | 串口号 |
| `baudrate` | `19200` | 波特率 |
| `timeout` | `5` | 通信超时 (s) |

## 主要动作

- `initialize` / `cleanup`：连接与释放
- `move_to` / `move_relative` / `move_to_wavenumber`：波长/波数移动
- `set_grating` / `grating_home` / `set_turret`：光栅控制
- `set_exit_port` / `set_entrance_port`：光路切换
- `stop` / `query_position` / `send_command`：控制与查询

## 状态属性

`status`、`wavelength`、`wavenumber`、`grating`、`turret`、`exit_port`、`entrance_port`、`system_info`

## Graph 示例

`graph_example_zolix_omni_lambda.json`

## 注意事项

- 移动类动作为阻塞式，需等待设备返回 Idle
- 动作参数类型仅支持 `float` / `str`（框架限制）

## 产品资料

### 产品简介

卓立汉光（Zolix）**Omni-λ** 系列是影像校正光栅单色仪/光谱仪，C-T 光路结构，支持计算机控制波长扫描、光栅切换与出入口选择，广泛用于荧光、拉曼、吸收光谱等。

### 产品特点

- 焦距可选 200 / 320 / 500 / 750 mm
- 杂散光抑制比约 1×10⁻⁵
- 狭缝 0.01–3 mm 手动可调（可选自动狭缝）
- 通信：USB 2.0 标准，可选 RS-232；本驱动使用 **RS232 ASCII 协议**

### 技术参数（Omni-λ300i 系列参考）

| 项目 | 参数 |
|---|---|
| 焦距 | 320 mm |
| 相对孔径 | F/4.2 |
| 光栅 | 68×68 mm，三光栅台 |
| 波长准确度 | ±0.2 nm（@1200 g/mm） |
| 扫描步距 | 0.005 nm |
| 杂散光 | 1×10⁻⁵ |
| 生产厂家 | 北京卓立汉光仪器有限公司 |

### 资料链接

- [Omni-λ 系列概览](https://zolix.com.cn/Product_desc/1324_353.html)
- [Omni-λ300i 规格](https://www.zolix.com.cn/Product_desc/1199_1564.html)
- [Omni-λ750i 规格](https://www.zolix.com.cn/Product_desc/1324_1566.html)
