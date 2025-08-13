# 操作符基类 (xoperator)

`xpertcorpus.modules.others.xoperator` 模块提供操作符抽象基类和生命周期管理功能。

## 模块概述

操作符基类模块定义了 XpertCorpus 框架中所有操作符的统一接口，提供生命周期管理、配置管理和钩子系统。

## 核心组件

### OperatorState

操作符生命周期状态枚举。

```python
from xpertcorpus.modules.others.xoperator import OperatorState

class OperatorState(Enum):
    INITIALIZED = "INITIALIZED"    # 已初始化
    CONFIGURED = "CONFIGURED"      # 已配置
    RUNNING = "RUNNING"           # 运行中
    COMPLETED = "COMPLETED"       # 已完成
    FAILED = "FAILED"             # 失败
    STOPPED = "STOPPED"           # 已停止
```

### OperatorABC

操作符抽象基类，所有操作符都应继承此类。

```python
class OperatorABC(ABC):
    """Abstract base class for all operators in XpertCorpus."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化操作符"""
```

#### 抽象方法（必须实现）

```python
@abstractmethod
def run(self) -> Any:
    """执行操作符的主要逻辑，子类必须实现"""
    pass

@abstractmethod
def get_desc(self, lang: str = "zh") -> str:
    """获取操作符描述，子类必须实现"""
    pass
```

#### 生命周期钩子方法

```python
def _on_init(self) -> None:
    """初始化钩子，在构造函数中调用"""
    
def _on_configure(self) -> None:
    """配置钩子，在配置时调用"""
    
def _on_before_run(self) -> None:
    """运行前钩子"""
    
def _on_after_run(self, result: Any) -> None:
    """运行后钩子"""
    
def _on_error(self, error: Exception) -> None:
    """错误处理钩子"""
    
def _on_complete(self) -> None:
    """完成钩子"""
```

#### 配置管理方法

```python
def configure(self, config: Dict[str, Any]) -> 'OperatorABC':
    """配置操作符"""
    
def validate_config(self) -> bool:
    """验证配置（默认返回 True）"""
    
def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
    """获取配置值"""
    
def set_config(self, key: str, value: Any) -> 'OperatorABC':
    """设置配置值"""
```

#### 钩子管理方法

```python
def add_hook(self, event: str, callback: callable) -> 'OperatorABC':
    """添加钩子回调函数"""
```

支持的钩子事件：
- `before_run` - 运行前
- `after_run` - 运行后  
- `on_error` - 错误时
- `on_complete` - 完成时

#### 执行控制方法

```python
def execute(self, *args, **kwargs) -> Any:
    """完整的执行流程，包含生命周期管理"""
    
def stop(self) -> None:
    """停止操作符执行"""
    
def reset(self) -> 'OperatorABC':
    """重置操作符状态"""
```

#### 信息获取方法

```python
def get_state(self) -> OperatorState:
    """获取当前状态"""
    
def get_metadata(self) -> Dict[str, Any]:
    """获取元数据"""
    
def get_metrics(self) -> Dict[str, Any]:
    """获取性能指标"""
    
def get_info(self) -> Dict[str, Any]:
    """获取完整信息"""
```

## 操作符管理器

### OperatorManager

提供操作符创建和管理功能。

```python
class OperatorManager:
    """操作符管理器"""
    
    @staticmethod
    def create_operator(operator_name: str,
                       config: Optional[Dict[str, Any]] = None,
                       **kwargs) -> OperatorABC:
        """创建操作符实例"""
    
    @staticmethod
    def list_operators() -> List[str]:
        """列出所有已注册的操作符"""
    
    @staticmethod
    def get_operator_info(operator_name: str) -> Dict[str, Any]:
        """获取操作符信息"""
```

### 工具函数

```python
def get_operator(operator_name: str,
                config: Optional[Dict[str, Any]] = None,
                **kwargs) -> OperatorABC:
    """获取操作符实例（推荐使用）"""

def get_operator_legacy(operator_name: str, args: Any) -> OperatorABC:
    """兼容旧版本的操作符获取方法"""
```

## 使用示例

### 基本操作符实现

```python
from xpertcorpus.modules.others.xoperator import OperatorABC, OperatorState

class CustomOperator(OperatorABC):
    """自定义操作符示例"""
    
    def _on_init(self):
        # 初始化逻辑
        self.processed_count = 0
    
    def run(self) -> Any:
        # 实现具体的处理逻辑
        self.processed_count += 1
        return {"processed": self.processed_count}
    
    def get_desc(self, lang="zh") -> str:
        return "自定义操作符"

# 使用操作符
operator = CustomOperator(config={"batch_size": 100})
result = operator.execute()
```

### 使用操作符管理器

```python
from xpertcorpus.modules.others.xoperator import OperatorManager, get_operator

# 列出可用操作符
available_operators = OperatorManager.list_operators()

# 创建操作符
operator = OperatorManager.create_operator(
    "custom_operator",
    config={"param1": "value1"}
)

# 或使用便捷函数
operator = get_operator(
    "custom_operator", 
    config={"param1": "value1"}
)
```

### 钩子系统使用

```python
def before_run_hook(operator, *args, **kwargs):
    print(f"开始执行 {operator.__class__.__name__}")

def after_run_hook(operator, result, *args, **kwargs):
    print(f"执行完成，结果: {result}")

# 添加钩子
operator = CustomOperator()
operator.add_hook("before_run", before_run_hook)
operator.add_hook("after_run", after_run_hook)

# 执行操作符（会触发钩子）
result = operator.execute()
```

## 内置属性和状态

操作符实例包含以下重要属性：

- `config`: 配置字典
- `state`: 当前操作符状态
- `metadata`: 元数据字典（包含创建时间、名称、版本等）
- `metrics`: 性能指标字典（执行次数、处理时间、错误次数等）

## 相关文档

- [框架系统 (xframework)](xframework.md)
- [注册系统 (xregistry)](xregistry.md)
- [异常处理 (xerror_handler)](../utils/xerror_handler.md)

---

[返回 Others 模块首页](README.md) | [返回 API 文档首页](../README.md) 