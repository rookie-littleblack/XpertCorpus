# 异常处理 (xerror_handler)

`xpertcorpus.utils.xerror_handler` 模块为 XpertCorpus 框架提供统一的异常处理、重试机制和错误报告功能。

## 模块概述

该模块的核心是提供一套健壮的工具来捕获、分类、记录和处理异常，确保框架的稳定性和可维护性。

```python
from xpertcorpus.utils.xerror_handler import (
    ErrorSeverity,      # 错误严重性枚举
    ErrorCategory,      # 错误类别枚举
    ErrorInfo,          # 错误信息数据结构
    XRetryMechanism,    # 重试机制
    XErrorReporter,     # 错误报告器
    XErrorHandler,      # 统一异常处理器
    retry_on_failure,   # 重试装饰器
    safe_execute,       # 安全执行装饰器
    error_handler       # 全局错误处理器实例
)
```

## 枚举与数据结构

### ErrorSeverity

错误严重性级别，用于对错误进行分类。

```python
class ErrorSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
```

### ErrorCategory

错误类别，用于对错误进行功能性分类。

```python
class ErrorCategory(Enum):
    SYSTEM = "SYSTEM"
    NETWORK = "NETWORK"
    DATA = "DATA"
    LOGIC = "LOGIC"
    CONFIG = "CONFIG"
    UNKNOWN = "UNKNOWN"
```

### ErrorInfo

封装错误信息的标准数据结构。

```python
@dataclass
class ErrorInfo:
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    exception_type: str
    message: str
    traceback: str
    context: Dict[str, Any]
    module: str
    function: str
    line_number: int
    retry_count: int
    resolved: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """将错误信息转换为字典"""
```

## 核心类

### XRetryMechanism

提供可配置的重试策略，支持指数退避和随机抖动。

#### 构造函数
```python
def __init__(self, 
             max_retries: int = 3,
             base_delay: float = 1.0,
             max_delay: float = 60.0,
             exponential_base: float = 2.0,
             jitter: bool = True):
```

#### 主要方法
- `calculate_delay(attempt: int) -> float`: 计算下一次重试的延迟时间。
- `should_retry(exception: Exception, attempt: int) -> bool`: 判断是否应重试特定异常。
- `retry(func: Callable, *args, **kwargs) -> Any`: 执行带重试逻辑的函数。

### XErrorReporter

负责收集、分类和统计错误信息。

#### 主要方法
- `classify_error(exception: Exception) -> tuple[ErrorSeverity, ErrorCategory]`: 根据异常类型自动分类。
- `extract_context(frame_info=None) -> Dict`: 从调用栈中提取上下文信息。
- `report_error(exception, context=None, ...) -> ErrorInfo`: 报告一个新错误。
- `get_error_summary() -> Dict`: 获取错误统计摘要。
- `clear_errors()`: 清除所有已记录的错误。

### XErrorHandler

统一的错误处理器，采用单例模式，是框架错误处理的中心。

#### 主要方法
- `handle_error(exception, context=None, should_raise=True, recovery_action=None)`: 处理错误的核心方法。
- `safe_execute(func, *args, fallback_value=None, retry_enabled=False, **kwargs)`: 安全地执行函数，自动处理异常。
- `get_error_summary() -> Dict`: 获取错误摘要。
- `clear_errors()`: 清理错误记录。

## 装饰器

### @retry_on_failure

为函数添加自动重试功能。

```python
@retry_on_failure(max_retries=3, base_delay=1.0)
def unstable_network_call():
    # ... 可能失败的网络请求 ...
    pass
```

### @safe_execute

安全地执行函数，自动捕获异常并可返回一个备用值。

```python
@safe_execute(fallback_value="default_value")
def operation_that_might_fail():
    # ... 可能失败的操作 ...
    pass
```

## 全局实例

### error_handler

框架提供的全局错误处理器单例，推荐在整个应用中使用。

## 使用示例

### 基本错误处理

```python
from xpertcorpus.utils.xerror_handler import error_handler

try:
    # 执行一个可能失败的操作
    result = 10 / 0
except Exception as e:
    # 使用全局处理器处理错误
    error_handler.handle_error(
        e,
        context={"operation": "division", "value": 10},
        should_raise=False  # 处理后不重新抛出异常
    )

# 打印错误摘要
summary = error_handler.get_error_summary()
print(summary)
```

### 使用安全执行装饰器

```python
from xpertcorpus.utils.xerror_handler import safe_execute

@safe_execute(fallback_value=-1)
def parse_integer(value: str) -> int:
    """一个可能会因为无效输入而失败的函数"""
    return int(value)

# 调用
result1 = parse_integer("123")  # 返回 123
result2 = parse_integer("abc")  # 失败，返回备用值 -1

print(f"Result 1: {result1}")
print(f"Result 2: {result2}")
```

### 使用重试装饰器

```python
import random
from xpertcorpus.utils.xerror_handler import retry_on_failure

@retry_on_failure(max_retries=3)
def fetch_data_from_unstable_api():
    """模拟一个不稳定的API调用"""
    if random.random() > 0.3:
        raise ConnectionError("Failed to connect to the API")
    print("Successfully fetched data!")
    return {"data": "some important data"}

# 调用
fetch_data_from_unstable_api()
```

## 相关文档

- [日志系统 (xlogger)](xlogger.md)

---

[返回 Utils 模块首页](README.md) | [返回 API 文档首页](../README.md) 