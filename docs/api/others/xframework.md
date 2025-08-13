# Framework 基础框架系统 (xframework)

`xpertcorpus.modules.others.xframework` 模块提供了 XpertCorpus 框架的抽象基类和框架管理功能。

## 模块概述

框架基础系统为 XpertCorpus 提供统一的框架抽象接口，定义了框架的生命周期管理、配置管理和组件管理标准。

## 核心组件

### FrameworkState

框架生命周期状态枚举。

```python
from xpertcorpus.modules.others.xframework import FrameworkState

class FrameworkState(Enum):
    INITIALIZED = "INITIALIZED"    # 已初始化
    CONFIGURED = "CONFIGURED"      # 已配置
    PREPARING = "PREPARING"        # 准备中
    RUNNING = "RUNNING"           # 运行中
    COMPLETED = "COMPLETED"       # 已完成
    FAILED = "FAILED"             # 失败
    STOPPED = "STOPPED"           # 已停止
    PAUSED = "PAUSED"             # 已暂停
```

#### 状态详细说明

| 状态 | 含义 | 进入时机 | 可用操作 |
|------|------|----------|----------|
| **INITIALIZED** | 🚀 框架刚初始化完成 | `__init__()` 完成后 | `prepare()`, `configure()`, `run()` (自动准备) |
| **CONFIGURED** | ✅ 组件已准备好，可运行 | `prepare()` 成功完成后 | `run()`, 重新 `prepare()` |
| **PREPARING** | ⚙️ 正在准备组件 | `prepare()` 执行过程中 | 内部状态，用户不应干预 |
| **RUNNING** | 🏃 正在执行管道 | `run()` 执行过程中 | `pause()`, `stop()` |
| **COMPLETED** | 🎉 执行成功完成 | `run()` 成功结束后 | 查看结果, 重新 `prepare()` |
| **FAILED** | ❌ 执行失败 | 任何阶段出错后 | `reset()` 重新开始 |
| **STOPPED** | ⏹️ 用户主动停止 | 调用 `stop()` 后 | `reset()`, `resume()` |
| **PAUSED** | ⏸️ 暂停执行 | 调用 `pause()` 后 | `resume()` 继续执行 |

#### 状态转换流程

```
INITIALIZED → prepare() → CONFIGURED → run() → RUNNING → COMPLETED/FAILED
     ↑                         ↑                            ↓
     └─────── reset() ←────────────────────────── ──────────┘
     
自动模式：INITIALIZED → run() (自动调用prepare()) → CONFIGURED → RUNNING → COMPLETED/FAILED
```

### FrameworkType

框架类型枚举。

```python
from xpertcorpus.modules.others.xframework import FrameworkType

class FrameworkType(Enum):
    PRETRAINING = "PRETRAINING"   # 预训练框架
    SFT = "SFT"                   # 监督微调框架
    COT = "COT"                   # 思维链框架
    MULTIMODAL = "MULTIMODAL"     # 多模态框架
    CUSTOM = "CUSTOM"             # 自定义框架
```

## 核心抽象类

### FrameworkABC

框架抽象基类，定义了所有框架必须实现的核心接口。

```python
class FrameworkABC(ABC):
    """Abstract base class for all frameworks in XpertCorpus."""
    
    # 框架元数据
    FRAMEWORK_TYPE: FrameworkType = FrameworkType.CUSTOM
    VERSION: str = "1.0.0"
    REQUIRED_OPERATORS: List[str] = []
    REQUIRED_PIPELINES: List[str] = []
```

#### 构造函数

```python
def __init__(self, 
             input_file: str,
             output_dir: str = "./output",
             max_workers: int = 1,
             limit: int = 0,
             config: Optional[Dict[str, Any]] = None):
    """
    初始化框架。
    
    Args:
        input_file: 输入文件或目录路径
        output_dir: 输出目录路径
        max_workers: 工作线程数
        limit: 处理限制（0表示无限制）
        config: 可选配置字典
    """
```

#### 抽象方法（必须实现）

```python
@abstractmethod
def _on_init(self) -> None:
    """框架特定初始化逻辑"""
    pass

@abstractmethod
def _prepare_components(self) -> None:
    """准备框架组件（算子、管道等）"""
    pass

@abstractmethod
def _execute_pipeline(self) -> Dict[str, Any]:
    """执行主要处理管道"""
    pass

@abstractmethod
def get_desc(self, lang: str = "zh") -> str:
    """获取框架描述"""
    pass
```

#### 配置管理方法

```python
def configure(self, config: Dict[str, Any]) -> 'FrameworkABC':
    """配置框架设置"""

def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
    """获取配置值"""
    
def set_config(self, key: str, value: Any) -> 'FrameworkABC':
    """设置配置值"""
```

#### 组件管理方法

```python
def add_operator(self, name: str, operator: OperatorABC) -> 'FrameworkABC':
    """添加算子"""
    
def get_operator(self, name: str) -> Optional[OperatorABC]:
    """获取算子"""
    
def add_pipeline(self, name: str, pipeline: Any) -> 'FrameworkABC':
    """添加管道"""
    
def get_pipeline(self, name: str) -> Optional[Any]:
    """获取管道"""
```

#### 钩子管理方法

```python
def add_hook(self, event: str, callback: callable) -> 'FrameworkABC':
    """添加钩子回调函数"""
```

支持的钩子事件：
- `before_init`, `after_init`
- `before_prepare`, `after_prepare` 
- `before_run`, `after_run`
- `on_error`, `on_complete`
- `on_pause`, `on_resume`

#### 生命周期控制方法

```python
def prepare(self) -> 'FrameworkABC':
    """
    准备框架执行，初始化所有必要组件。
    可从 INITIALIZED 或 CONFIGURED 状态调用。
    """
    
def run(self) -> Dict[str, Any]:
    """
    执行框架管道。
    
    智能状态管理：
    - INITIALIZED 状态：自动调用 prepare() 然后执行
    - CONFIGURED 状态：直接执行
    - 其他状态：抛出异常
    
    Returns:
        Dict: 包含管道执行结果的字典
    """
    
def forward(self) -> Dict[str, Any]:
    """
    run() 方法的向后兼容版本。
    
    注意：此方法已弃用，建议使用 run() 方法。
    提供与 run() 相同的智能状态管理功能。
    """
    
def pause(self) -> 'FrameworkABC':
    """暂停执行（仅在 RUNNING 状态可用）"""
    
def resume(self) -> 'FrameworkABC':
    """恢复执行（仅在 PAUSED 状态可用）"""
    
def stop(self) -> 'FrameworkABC':
    """停止执行"""
    
def reset(self) -> 'FrameworkABC':
    """重置框架到初始状态"""
```

#### 信息获取方法

```python
def get_state(self) -> FrameworkState:
    """获取当前状态"""
    
def get_metadata(self) -> Dict[str, Any]:
    """获取框架元数据"""
    
def get_metrics(self) -> Dict[str, Any]:
    """获取性能指标"""
    
def get_info(self) -> Dict[str, Any]:
    """获取完整框架信息"""
    
def get_progress(self) -> Dict[str, Any]:
    """获取当前进度信息"""
```

## 框架管理器

### FrameworkManager

框架注册和管理器。

```python
class FrameworkManager:
    """框架注册和生命周期管理器"""
    
    @classmethod
    def register_framework(cls, name: str, framework_class: Type[FrameworkABC]) -> None:
        """注册框架类"""
    
    @classmethod
    def get_framework(cls, name: str) -> Optional[Type[FrameworkABC]]:
        """获取框架类"""
    
    @classmethod
    def list_frameworks(cls) -> List[str]:
        """列出所有注册的框架"""
    
    @classmethod
    def create_framework(cls, 
                        name: str,
                        input_file: str,
                        output_dir: str = "./output",
                        max_workers: int = 1,
                        limit: int = 0,
                        config: Optional[Dict[str, Any]] = None) -> FrameworkABC:
        """创建框架实例"""
```

### register_framework 装饰器

```python
def register_framework(name: str):
    """框架注册装饰器"""
    def decorator(framework_class: Type[FrameworkABC]):
        FrameworkManager.register_framework(name, framework_class)
        return framework_class
    return decorator
```

## 使用示例

### 基本框架实现

```python
from xpertcorpus.modules.others.xframework import (
    FrameworkABC, FrameworkType, register_framework
)

@register_framework("custom_framework")
class CustomFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
    
    def _on_init(self):
        # 框架特定初始化
        pass
        
    def _prepare_components(self):
        # 准备组件
        pass
        
    def _execute_pipeline(self):
        # 执行管道
        return {"status": "completed"}
    
    def get_desc(self, lang="zh"):
        return "自定义处理框架"
```

### 框架使用方式

#### 方式一：简单使用（推荐）

```python
# 最简单的使用方式 - 自动状态管理
framework = CustomFramework(
    input_file="input.jsonl",
    output_dir="./output"
)
results = framework.run()  # 自动调用 prepare() 然后执行
```

#### 方式二：手动控制

```python
# 手动控制生命周期
framework = CustomFramework(
    input_file="input.jsonl",
    output_dir="./output"
)
framework.prepare()  # 手动准备组件
results = framework.run()  # 执行管道
```

#### 方式三：配置驱动

```python
# 带配置的使用方式
config = {
    "custom_setting": "value",
    "batch_size": 100
}
framework = CustomFramework(
    input_file="input.jsonl",
    output_dir="./output",
    config=config
)
results = framework.run()
```

#### 方式四：生命周期监控

```python
# 状态监控和错误处理
framework = CustomFramework(input_file="input.jsonl")

# 添加生命周期钩子
framework.add_hook("before_run", lambda fw: print("开始执行"))
framework.add_hook("on_complete", lambda fw: print("执行完成"))

try:
    results = framework.run()
    print(f"框架状态: {framework.get_state()}")
    print(f"性能指标: {framework.get_metrics()}")
except Exception as e:
    print(f"执行失败: {e}")
    framework.reset()  # 重置状态
```

### 框架管理器使用

```python
from xpertcorpus.modules.others.xframework import FrameworkManager

# 列出可用框架
available = FrameworkManager.list_frameworks()

# 创建框架实例
framework = FrameworkManager.create_framework(
    "custom_framework",
    input_file="data.jsonl"
)
```

## 内置属性和状态

框架实例包含以下重要属性：

- `state`: 当前框架状态
- `metadata`: 框架元数据字典
- `metrics`: 性能指标字典
- `config`: 配置字典
- `operators`: 已注册算子字典
- `pipelines`: 已注册管道字典
- `storage`: 存储实例

## 最佳实践

### 1. 优先使用 run() 方法

```python
# ✅ 推荐：简单直接
framework = MyFramework(input_file="data.jsonl")
results = framework.run()

# ❌ 不推荐：过度复杂
framework = MyFramework(input_file="data.jsonl")
framework.prepare()
results = framework.run()
```

### 2. 合理使用配置

```python
# ✅ 推荐：配置驱动
config = {
    "batch_size": 100,
    "enable_cache": True
}
framework = MyFramework(input_file="data.jsonl", config=config)

# ❌ 不推荐：硬编码
framework = MyFramework(input_file="data.jsonl")
framework.batch_size = 100  # 直接修改属性
```

### 3. 适当的错误处理

```python
# ✅ 推荐：优雅的错误处理
try:
    results = framework.run()
except Exception as e:
    logger.error(f"Framework execution failed: {e}")
    framework.reset()  # 重置状态以便重试
```

### 4. 监控执行状态

```python
# ✅ 推荐：状态监控
framework.add_hook("on_complete", lambda fw: 
    print(f"处理完成，耗时: {fw.get_metrics()['total_processing_time']:.2f}s"))
```

## 注意事项

### 状态管理

- **自动准备**：`run()` 方法会在 `INITIALIZED` 状态自动调用 `prepare()`
- **重复准备**：在 `CONFIGURED` 状态可以重新调用 `prepare()` 重新配置组件
- **状态检查**：使用 `get_state()` 检查当前状态，避免在错误状态下调用方法

### 性能优化

- **避免重复准备**：已经是 `CONFIGURED` 状态时，`run()` 不会重复调用 `prepare()`
- **合理设置工作线程**：根据 CPU 核心数和任务特性设置 `max_workers`
- **监控指标**：使用 `get_metrics()` 监控性能指标

### 错误恢复

- **状态重置**：出错后使用 `reset()` 重置到初始状态
- **钩子清理**：在钩子函数中进行必要的资源清理
- **异常传播**：框架会适当传播异常，便于上层处理

## 相关文档

- [算子基类 (xoperator)](xoperator.md)
- [注册系统 (xregistry)](xregistry.md)
- [异常处理 (xerror_handler)](../utils/xerror_handler.md)

---

[返回 Others 模块首页](README.md) | [返回 API 文档首页](../README.md) 