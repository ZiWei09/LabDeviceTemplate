# CMOS 线阵检测器

## 简介

LCAMV8 CMOS 线阵检测器（S11639-01，2048 像素）驱动，支持积分时间、增益、单帧/连续采集及波长矫正。

## 设备 ID

`cmos_detector`

## 通信方式

- 协议：USB 虚拟串口 ASCII 帧
- 默认：115200 baud，8N1

## 依赖

- `pyserial`

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `port` | `COM10` | 串口号 |
| `baudrate` | `115200` | 波特率 |
| `save_dir` | `./cmos_data` | CSV 数据保存目录 |

## 主要动作

- `initialize` / `cleanup`：打开/关闭串口
- `start_single_acquisition` / `start_continuous_acquisition` / `stop_acquisition` / `read_frame`：采集控制
- `set_integration_time` / `set_gain` / `set_offset` 等：参数设置
- `read_correction_coefficients` / `save_data_to_file`：波长映射与数据导出

## 状态属性

`status`、`level`、`value`（JSON 像素数组）、`integration_time`、`gain`、`version_info` 等

## Graph 示例

`graph_example_cmos_detector.json`

## 注意事项

- 单次采集（0x01）无响应，驱动使用连续采集 + 停止实现单帧
- 布尔状态以字符串 `"true"` / `"false"` 表示

## 产品资料

### 产品简介

LCAMV8-S11639 线阵检测器模组基于滨松（Hamamatsu）**S11639-01** CMOS 线阵传感器，集成 ARM+FPGA 驱动板，通过 USB 虚拟串口通信，适用于光谱分析、紫外/近红外检测等场景。

### 传感器核心参数（S11639-01）

| 项目 | 参数 |
|---|---|
| 像素数 | 2048 × 1 |
| 像元尺寸 | 14 × 200 μm |
| 有效感光长度 | 28.672 mm |
| 光谱响应 | 200 ~ 1000 nm |
| 灵敏度 | 1300 V/(lx·s) |
| 行速率（最大） | 4672 lines/s |
| 供电 | 5 V 单电源 |

### 模组特点（LCAMV8 系列）

- 接口：USB Type-C、TTL，支持外触发
- 最高帧率可达 200 fps 以上（视配置）
- 16 bit 专业 CCD 处理器

### 资料链接

- [Hamamatsu S11639-01 官方页](https://www.hamamatsu.com/eu/en/product/optical-sensors/image-sensor/ccd-cmos-nmos-image-sensor/line-sensor/for-spectrophotometry/S11639-01.html)
- [S11639-01 数据手册 PDF](https://www.hamamatsu.com/content/dam/hamamatsu-photonics/sites/documents/99_SALES_LIBRARY/ssd/s11639-01_kmpd1163e.pdf)
- [依迈光电 LCAMV8 模组介绍](http://www.imaioptics.com/index.php?a=index&aid=55&c=view&m=home)
