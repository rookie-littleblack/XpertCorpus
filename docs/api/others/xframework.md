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
    """准备框架执行"""
    
def run(self) -> Dict[str, Any]:
    """执行框架管道"""
    
def forward(self) -> Dict[str, Any]:
    """run() 方法的别名，用于向后兼容"""
    
def pause(self) -> 'FrameworkABC':
    """暂停执行"""
    
def resume(self) -> 'FrameworkABC':
    """恢复执行"""
    
def stop(self) -> 'FrameworkABC':
    """停止执行"""
    
def reset(self) -> 'FrameworkABC':
    """重置框架状态"""
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

# 使用框架
framework = CustomFramework(
    input_file="input.jsonl",
    output_dir="./output"
)
results = framework.prepare().run()
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

## 相关文档

- [算子基类 (xoperator)](xoperator.md)
- [注册系统 (xregistry)](xregistry.md)
- [异常处理 (xerror_handler)](../utils/xerror_handler.md)

---

[返回 Others 模块首页](README.md) | [返回 API 文档首页](../README.md) 