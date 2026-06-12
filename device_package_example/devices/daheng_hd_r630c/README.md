# HD-R630C 工业相机

## 简介

大恒图像 **HD-R630C-U3** USB3.0 彩色工业相机驱动，基于 Harvesters + GenICam（USB3 Vision）接口。

## 设备 ID

`daheng_hd_r630c`

## 通信方式

- 协议：USB3 Vision（GenTL Producer）
- 默认 CTI：`C:\Program Files (x86)\Do3think\DVP2 x64\DVPCameraTL64.cti`

## 依赖

- `harvesters`
- `numpy`
- `opencv-python-headless` 或 `pillow`（保存图片）

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `cti_path` | 见上 | GenTL Producer 路径 |
| `device_index` | `0` | 相机索引 |
| `default_exposure_time` | `10000.0` | 默认曝光 (μs) |
| `default_gain` | `0.0` | 默认增益 (dB) |
| `save_dir` | `./captured_images` | 截图保存目录 |

## 主要动作

- `initialize` / `cleanup`：打开/关闭相机
- `snap`：单帧采集，返回图片文件路径
- `start_stream` / `stop_stream`：连续采集
- `set_exposure_time` / `set_gain`：参数调节

## 状态属性

`status`、`exposure_time`、`gain`、`frame_rate`、`image_width`、`image_height`、`is_streaming`、`last_frame_id`、`last_image_path`

## Graph 示例

`graph_example_daheng_hd_r630c.json`

## 注意事项

- 需安装相机 SDK 及 GenTL `.cti` 文件（本实验室使用度申 DVP GenTL）
- 默认路径为 Windows，Linux/macOS 需修改 `cti_path`

## 产品资料

### 产品简介

**HD-R630C-U3** 为大恒图像（Daheng Imaging）6.3 MP USB3.0 彩色工业面阵相机，体积 29 mm 立方，适用于机器视觉与实验室成像。与同平台度申 M3ST630-H-O2C 规格相近，本驱动通过 GenICam 接口控制，与具体销售品牌无关。

### 产品特点

- 3072 × 2048 分辨率，最高 70 FPS
- 1/1.8" 卷帘快门 CMOS，像元 2.4 μm
- 软件/硬件触发，12 bit 输出
- USB 3.0 带锁紧螺口，5 V 供电

### 技术参数（HD-R630C-U3，参考大恒图像规格）

| 项目 | 参数 |
|---|---|
| 型号 | HD-R630C-U3 |
| 生产厂家 | 大恒图像（Daheng Imaging） |
| 分辨率 | 3072 × 2048 |
| 靶面 | 1/1.8" |
| 快门类型 | 卷帘快门 |
| 像元尺寸 | 2.4 μm |
| 最大帧率 | 70 FPS |
| 黑白/彩色 | 彩色 |
| 感光区面积 | 7.37 × 4.91 mm |
| 信噪比 | 36.99 dB |
| 灵敏度 | 0.425 V/lux·s（1/30 s，F5.6） |
| 位深 | 12 bit |
| 触发方式 | 软件触发 / 硬件触发 |
| 动态范围 | 71 dB |
| 光谱响应 | 390 ~ 650 nm |
| 曝光时间 | 6 μs ~ 约 6 s |
| 增益范围 | 1 ~ 15.875×（步进 0.125×） |
| 供电 | USB 5 V |
| 典型功耗 | 工作 1.64 W / 待机 1.12 W |
| 传输接口 | USB 3.0（带紧固螺口） |
| 镜头接口 | C-Mount |
| 外形尺寸 | 29 × 29 × 29 mm |
| 工作温度 | -10 ~ 50 ℃ |
| 重量 | 40 g |

### 资料链接

- [大恒图像官网](https://www.daheng-imaging.com/)
- [度申 M3ST630-H-O2C（同平台参考）](https://en.do3think.com/product/m3st630-h-o2c-area-scan-camera)
- [度申 M3ST 系列概览](https://www.do3think.com/M3S/)

> 说明：本实验室驱动使用 Harvesters + 度申 GenTL（`DVPCameraTL64.cti`）。若使用大恒官方 SDK，需相应调整 `cti_path`。
