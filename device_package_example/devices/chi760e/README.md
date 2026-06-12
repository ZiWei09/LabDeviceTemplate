# CHI760E 电化学工作站

## 简介

辰华 CHI760E 电化学工作站驱动，通过 CHI 软件宏命令（`.mcr`）控制，支持 CV / LSV / CA / OCP / NPV / EIS 等实验。

## 设备 ID

`chi760e`

## 通信方式

- 方式：本地 subprocess 调用 `chi760e.exe /runmacro`
- 平台：**仅 Windows**

## 依赖

- `numpy`（可选，用于解析数据文件）

## 配置参数

| 参数 | 默认值 | 说明 |
|---|---|---|
| `chi_exe_path` | — | CHI 软件可执行文件路径（必填） |
| `data_folder` | — | 实验数据与宏文件目录（必填） |
| `default_sens` | `1e-6` | 默认灵敏度 (A/V) |

## 主要动作

- `initialize` / `cleanup`：验证路径与目录
- `run_cv` / `run_lsv` / `run_ca` / `run_ocp` / `run_npv` / `run_eis`：电化学实验
- `stop_operation`：强制结束 CHI 进程
- `list_data_files` / `read_data`：数据文件管理

## 状态属性

`status`、`technique`、`last_data_file`、`last_experiment_time`、`data_folder`

## Graph 示例

`graph_example_chi760e.json`

## 注意事项

- 需在 Windows 上安装 CHI760E 软件
- 实验为阻塞式 subprocess，单次实验可能耗时较长

## 产品资料

### 产品简介

上海辰华 CHI760E 是通用**双恒电位仪**电化学工作站，可同时控制同一电解池中的两个工作电极，典型应用为旋转环盘电极（RRDE），集成 CV、LSV、CA、OCP、NPV、EIS 等多种电化学技术。

### 主要特点

- 双通道同步扫描/采样，最高扫速 10,000 V/s
- 16 位数据采集，双通道同步采样最高 1 MHz
- 交流阻抗范围 0.00001 Hz ~ 1 MHz
- 超微电极稳态电流测量（电流下限 < 50 pA）

### 技术参数（参考）

| 项目 | 参数 |
|---|---|
| 电位范围 | ±10 V |
| 最大电流 | ±250 mA（双通道合计），峰值 ±350 mA |
| 槽压 | ±13 V |
| 电流测量 | ±10 pA ~ ±0.25 A（12 量程） |
| CV/LSV 扫速 | 1×10⁻⁶ ~ 10,000 V/s |
| EIS 频率 | 0.00001 ~ 1 MHz |
| 生产厂家 | 上海辰华仪器有限公司 |

### 资料链接

- [北京化工大学设备介绍](https://nhca3.buct.edu.cn/2021/0126/c1365a144584/page.htm)
- [鑫视科 CHI760E 产品页](https://www.shinsco.cn/products/2101/)

> 说明：驱动通过 Windows 下 CHI 软件宏命令（`.mcr`）控制，需安装 `chi760e.exe`。
