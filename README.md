# CosLab-SHU-DeviceTemplate

上海大学 MGI-CosLab 的 Uni-Lab-OS 外部设备包仓库。基于 [LabDeviceTemplate](https://github.com/Xuwznln/LabDeviceTemplate) fork 并扩展。

**创建时间**: 2026-03

## 功能

- 提供 CosLab 实验室设备驱动（16 个设备）
- 内置本地硬件冒烟测试（`smoke_runner.py`）
- 内置 GitHub Actions CI，自动验证注册表

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
# 或按需安装
pip install -r requirements.txt
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
pip install pyserial   # 按设备 README 安装依赖

cd CosLab_SHU_Device_package
python devices/hk_a0/hk_a0.py --port COM3 -v
```

成功时会看到 `✓ 连接成功` 和只读验证结果。完整命令列表见 [`CosLab_SHU_Device_package/SMOKE_TEST.md`](CosLab_SHU_Device_package/SMOKE_TEST.md)。

### 4. 本地开发与 Uni-Lab 集成

```bash
# 创建 conda 环境并安装 unilabos（需要 ROS2 完整环境）
mamba create -n unilab python=3.11.14 -c conda-forge -y
mamba activate unilab
mamba install uni-lab::unilabos -c uni-lab -c robostack-staging -c conda-forge -y

# 验证注册表（check mode，会自动检测并安装 requirements.txt 中的依赖）
unilab --check_mode --devices ./CosLab_SHU_Device_package --external_devices_only

# 启动服务（带实验图）
unilab --devices ./CosLab_SHU_Device_package --external_devices_only \
  -g CosLab_SHU_Device_package/graph_combined_lab.json
```

> **依赖自动安装**: unilabos 在启动时会自动检测 `--devices` 目录下的 `requirements.txt`，缺失的包会通过 `uv`（优先）或 `pip` 自动安装。

### 5. CI 验证

Push 代码后，GitHub Actions 会自动运行 `--check_mode` 验证设备定义是否正确。

## 目录结构

```
├── README.md                          # 本文件
├── requirements.txt                   # Python 依赖
├── pyproject.toml                     # 包配置（pip install -e .）
├── .github/workflows/check_registry.yml
└── CosLab_SHU_Device_package/         # 正式设备包（唯一源码目录）
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
