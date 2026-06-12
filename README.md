# CosLab-SHU-DeviceTemplate

上海大学 MGI-CosLab 的 Uni-Lab-OS 外部设备包仓库。基于 [LabDeviceTemplate](https://github.com/Xuwznln/LabDeviceTemplate) fork 并扩展。

**创建时间**: 2026-03

## 功能

- 提供 CosLab 实验室设备驱动（16 个设备）
- 内置本地硬件冒烟测试（`smoke_runner.py`）
- 内置 GitHub Actions CI，自动验证注册表

## 设备一览

| 设备 | 设备 ID | 通信方式 | 文档 |
|------|---------|----------|------|
| Bronkhorst EL 流量计 | `bronkhorst_el_flow` | RS232/RS485（propar） | [README](CosLab_SHU_Device_package/devices/bronkhorst_el_flow/README.md) |
| 辰华 CHI760E 电化学工作站 | `chi760e` | Windows 本地调用 CHI 软件 | [README](CosLab_SHU_Device_package/devices/chi760e/README.md) |
| CMOS 线阵检测器 | `cmos_detector` | USB 虚拟串口 ASCII | [README](CosLab_SHU_Device_package/devices/cmos_detector/README.md) |
| CNI 532nm 激光器 | `cni_laser_msl_u_532` | Arduino 串口 ASCII | [README](CosLab_SHU_Device_package/devices/cni_laser_msl_u_532/README.md) |
| 大恒 GCI060505 光源 | `daheng_gci060505` | Arduino 串口 ASCII | [README](CosLab_SHU_Device_package/devices/daheng_gci060505/README.md) |
| 大恒 HD-R630C 工业相机 | `daheng_hd_r630c` | USB3 Vision（GenTL） | [README](CosLab_SHU_Device_package/devices/daheng_hd_r630c/README.md) |
| DHJF-2005A 恒温循环浴 | `dhjf_circulation_bath` | Modbus RTU（RS485） | [README](CosLab_SHU_Device_package/devices/dhjf_circulation_bath/README.md) |
| 多可 Duco GCR5 协作机械臂 | `duco_gcr5` | TCP 文本命令 | [README](CosLab_SHU_Device_package/devices/duco_gcr5/README.md) |
| 电解池夹爪工作站 | `electrolytic_cell_gripper` | Modbus RTU（RS485） | [README](CosLab_SHU_Device_package/devices/electrolytic_cell_gripper/README.md) |
| 华控模拟量输出 | `hk_a0` | Modbus RTU（RS485） | [README](CosLab_SHU_Device_package/devices/hk_a0/README.md) |
| 久跃 JY-HSM 温度变送器 | `jyhsm_temperature_transmitter` | Modbus RTU（RS485） | [README](CosLab_SHU_Device_package/devices/jyhsm_temperature_transmitter/README.md) |
| 兰格 BT100-2J 蠕动泵 | `longer_bt100` | RS485 自定义帧 | [README](CosLab_SHU_Device_package/devices/longer_bt100/README.md) |
| 润泽 SY-03B 注射泵 | `runze_sy03b_t08` | ASCII DT 格式 | [README](CosLab_SHU_Device_package/devices/runze_sy03b_t08/README.md) |
| 4V110 电磁阀 | `solenoid_valve_4v110` | Arduino 串口 ASCII | [README](CosLab_SHU_Device_package/devices/solenoid_valve_4v110/README.md) |
| XYZ 光电三轴平台 | `xyz_guangdian` | Modbus RTU（RS485） | [README](CosLab_SHU_Device_package/devices/xyz_guangdian/README.md) |
| 卓立汉光 Omni-λ 单色仪 | `zolix_omni_lambda` | 串口 ASCII | [README](CosLab_SHU_Device_package/devices/zolix_omni_lambda/README.md) |

完整实验室拓扑见 [`graph_combined_lab.json`](CosLab_SHU_Device_package/graph_combined_lab.json)。

## 依赖与安装分工

本仓库涉及两类依赖，用途不同：

| 方式 | 安装内容 | 适用场景 |
|------|----------|----------|
| `pip install -e .` | 安装 `CosLab_SHU_Device_package` 包及 **pyproject.toml 中的运行时依赖**（pyserial、pymodbus、numpy 等） | 本地开发、编辑驱动代码 |
| `pip install -r CosLab_SHU_Device_package/requirements.txt` | 仅安装设备驱动所需的 **Python 第三方包** | 冒烟测试、最小环境 |
| `mamba install uni-lab::unilabos ...` | 安装 **Uni-Lab-OS 框架**（含 `unilab` CLI、注册表扫描、ROS2 集成） | `unilab --check_mode`、接入实验图、正式运行 |

要点：

- **`pip install -e .` 不会安装 `unilabos`**。`unilabos` 仅在 `pyproject.toml` 的 `[project.optional-dependencies] dev` 中声明，需单独通过 conda/mamba 安装。
- **冒烟测试**（`python devices/xxx/xxx.py`）通常只需 `requirements.txt` 中的包，不需要完整 ROS2 环境。
- **Uni-Lab 集成**必须先有 `unilabos`，再指定 `--devices ./CosLab_SHU_Device_package`。

### requirements.txt 查找逻辑

执行 `unilab --devices ./CosLab_SHU_Device_package` 时，框架按以下顺序查找依赖文件：

1. `<devices 目录>/requirements.txt` → 即 `CosLab_SHU_Device_package/requirements.txt`（**主文件**）
2. 若不存在，回退到 `<devices 目录>/../requirements.txt` → 仓库根目录（当前通过 `-r` 引用包内文件）

因此请将依赖维护在 **`CosLab_SHU_Device_package/requirements.txt`**；根目录 `requirements.txt` 仅作转发，保持与包内文件一致。

### 特殊依赖与平台说明

以下依赖**无法**通过 `pip install` 解决，需另行准备：

| 设备 | 平台 / 额外要求 |
|------|-----------------|
| `chi760e` | **仅 Windows**；需安装辰华 CHI 软件（`chi760e.exe`）并配置 `chi_exe_path` |
| `daheng_hd_r630c` | 需安装**度申 DVP SDK** 及 GenTL 文件（`DVPCameraTL64.cti`）；Python 侧需 `harvesters`、`numpy`，保存图片需 `opencv-python-headless` 或 `pillow` |
| `duco_gcr5` | 网口 TCP 通信，无额外 Python 包；需机械臂控制器 IP 可达 |
| 其余串口 / Modbus 设备 | 通常只需 `pyserial`、`pymodbus`（已列入 requirements.txt） |

各设备更详细的参数与接线说明见上表链接的 README。

## 快速开始

### 1. 安装依赖

```bash
# 开发：安装设备包 + Python 运行时依赖
pip install -e .

# 或仅安装驱动所需的 Python 包（冒烟测试够用）
pip install -r CosLab_SHU_Device_package/requirements.txt
```

### 2. 编写 / 修改设备代码

所有设备驱动位于 `CosLab_SHU_Device_package/devices/`。使用 `@device` 装饰器编写设备类：

```python
from unilabos.registry.decorators import device, action, topic_config

@device(
    id="my_device",
    category=["custom"],
    description="我的自定义设备",
    display_name="自定义设备",
)
class MyDevice:
    def __init__(self, device_id=None, config=None, **kwargs):
        """
        初始化设备。

        Args:
            device_id[设备ID]: 设备实例 ID。
            config[设备配置]: 设备启动配置。
        """
        self.device_id = device_id or "my_device"
        self.data = {}

    @action(description="执行操作")
    def do_something(self, param: str = "") -> dict:
        """
        执行示例操作。

        Args:
            param[操作参数]: 示例操作的字符串参数。
        """
        return {"success": True}

    @property
    @topic_config()
    def status(self) -> str:
        return self.data.get("status", "idle")
```

参考 `CosLab_SHU_Device_package/counting_device.py` 查看最简示例。

### 3. 本地硬件冒烟（推荐第一步）

插上硬件后，直接运行驱动文件，几秒内验证通信与控制：

```bash
pip install -r CosLab_SHU_Device_package/requirements.txt

cd CosLab_SHU_Device_package
python devices/hk_a0/hk_a0.py --port COM3 -v
```

成功时会看到 `✓ 连接成功` 和只读验证结果。完整命令列表见 [`CosLab_SHU_Device_package/SMOKE_TEST.md`](CosLab_SHU_Device_package/SMOKE_TEST.md)。

### 4. 本地开发与 Uni-Lab 集成

```bash
# 安装 unilabos（需要 ROS2 完整环境，与 pip install -e . 分开安装）
mamba create -n unilab python=3.11.14 -c conda-forge -y
mamba activate unilab
mamba install uni-lab::unilabos -c uni-lab -c robostack-staging -c conda-forge -y

# 验证注册表（自动安装 CosLab_SHU_Device_package/requirements.txt 中的缺失包）
unilab --check_mode --devices ./CosLab_SHU_Device_package --external_devices_only

# 启动服务（带实验图）
unilab --devices ./CosLab_SHU_Device_package --external_devices_only \
  -g CosLab_SHU_Device_package/graph_combined_lab.json
```

> **依赖自动安装**: `unilab` 启动时会读取 `CosLab_SHU_Device_package/requirements.txt`（见上文查找逻辑），缺失的包会通过 `uv`（优先）或 `pip` 自动安装。

### 5. CI 验证

Push 代码后，GitHub Actions 会自动运行 `--check_mode` 验证设备定义是否正确。

## 目录结构

```
├── README.md                          # 本文件
├── requirements.txt                   # 转发至 CosLab_SHU_Device_package/requirements.txt
├── pyproject.toml                     # 包配置（pip install -e .）
├── .github/workflows/check_registry.yml
└── CosLab_SHU_Device_package/         # 正式设备包（唯一源码目录）
    ├── requirements.txt               # 设备 Python 依赖（unilab --devices 主查找路径）
    ├── __init__.py
    ├── counting_device.py             # 示例设备
    ├── smoke_runner.py                # 冒烟测试工具
    ├── SMOKE_TEST.md                  # 冒烟测试命令列表
    ├── graph_combined_lab.json        # 完整实验室拓扑
    └── devices/                       # 各设备驱动
        ├── hk_a0/
        ├── xyz_guangdian/
        └── ...
```

## 装饰器参考

| 装饰器 | 用途 | 示例 |
|---|---|---|
| `@device(id=..., category=[...])` | 标记设备类 | `@device(id="my_pump", category=["pump_and_valve"])` |
| `@action(...)` | 标记动作方法 | `@action(description="启动泵")` |
| `@topic_config()` | 标记状态属性（配合 `@property`） | 见示例代码 |
| `@not_action` | 排除公共方法（不作为动作） | `@not_action` |
| `@always_free` | 标记为不受排队限制的动作 | `@always_free` |

## 自动发现规则

- 带 `@action` 装饰器的方法 → 注册为**动作**
- 不带 `@action` 的公共方法 → 自动注册为 `auto-{方法名}` 动作
- `@property` + `@topic_config()` → 注册为**状态属性**
- `_` 开头的方法/属性 → 不会被扫描
- `@not_action` 标记的方法 → 不会被注册为动作

## 参数文档规范

在 `__init__` 和 action 方法 docstring 的 `Args:` 小节中，使用以下格式补充 schema 元数据：

```python
"""
Args:
    param[显示名称]: 参数说明，会写入 JSON Schema 的 description。
"""
```

- `param[显示名称]` 中的显示名称会写入 JSON Schema 字段的 `title`。
- `:` 后面的说明会写入 JSON Schema 字段的 `description`。
- 如果只写 `param: 参数说明`，`title` 会兜底为字段名，`description` 使用参数说明。
- 如果没有写参数文档，生成器也会兜底补齐 `title=<字段名>` 和 `description=""`，但设备包应优先写清楚显示名和说明。

## License

MIT
