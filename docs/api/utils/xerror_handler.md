# 异常处理模块 (xerror_handler)

`xerror_handler` 模块为 XpertCorpus 框架提供统一的异常处理、重试机制和错误报告功能。该模块采用现代 Python 设计模式，支持异步处理、自动重试、错误分类和统计分析。

## 模块概览

```python
from xpertcorpus.utils.xerror_handler import (
    XErrorHandler,      # 统一异常处理器
    XRetryMechanism,    # 重试机制
    XErrorReporter,     # 错误报告器
    ErrorSeverity,      # 错误严重性枚举
    ErrorCategory,      # 错误类别枚举
    ErrorInfo,          # 错误信息数据结构
    retry_on_failure,   # 重试装饰器
    safe_execute,       # 安全执行装饰器
    error_handler       # 全局错误处理器实例
)
```

## 枚举类型

### ErrorSeverity

错误严重性级别枚举，用于对错误进行优先级分类。

```python
class ErrorSeverity(Enum):
    LOW = "LOW"           # 低优先级错误
    MEDIUM = "MEDIUM"     # 中等优先级错误  
    HIGH = "HIGH"         # 高优先级错误
    CRITICAL = "CRITICAL" # 严重错误，需要立即处理
```

**使用示例：**
```python
from xpertcorpus.utils.xerror_handler import ErrorSeverity

# 根据业务需求设置错误级别
if memory_usage > 90:
    severity = ErrorSeverity.CRITICAL
elif memory_usage > 70:
    severity = ErrorSeverity.HIGH
else:
    severity = ErrorSeverity.MEDIUM
```

### ErrorCategory

错误类别枚举，用于对错误进行功能性分类。

```python
class ErrorCategory(Enum):
    SYSTEM = "SYSTEM"     # 系统错误（内存、磁盘等）
    NETWORK = "NETWORK"   # 网络错误（API调用、连接等）
    DATA = "DATA"         # 数据错误（格式、缺失等）
    LOGIC = "LOGIC"       # 逻辑错误（业务逻辑错误）
    CONFIG = "CONFIG"     # 配置错误（参数、设置等）
    UNKNOWN = "UNKNOWN"   # 未知错误
```

**自动分类规则：**
- `MemoryError`, `OSError` → `SYSTEM` + `CRITICAL`
- `ConnectionError`, `TimeoutError` → `NETWORK` + `HIGH`
- `ValueError`, `TypeError`, `KeyError` → `DATA` + `MEDIUM`
- `AssertionError`, `AttributeError` → `LOGIC` + `HIGH`
- `FileNotFoundError`, `PermissionError` → `CONFIG` + `HIGH`

## 数据结构

### ErrorInfo

错误信息的完整数据结构，包含错误的所有上下文信息。

```python
@dataclass
class ErrorInfo:
    error_id: str                    # 唯一错误ID
    timestamp: datetime              # 错误发生时间
    severity: ErrorSeverity          # 错误严重性
    category: ErrorCategory          # 错误类别
    exception_type: str              # 异常类型名称
    message: str                     # 错误消息
    traceback: str                   # 完整堆栈跟踪
    context: Dict[str, Any]          # 上下文信息
    module: str                      # 发生错误的模块
    function: str                    # 发生错误的函数
    line_number: int                 # 错误行号
    retry_count: int                 # 重试次数
    resolved: bool                   # 是否已解决
```

**方法：**
- `to_dict() -> Dict[str, Any]`: 转换为字典格式，便于日志记录和序列化

**使用示例：**
```python
# 错误信息会自动填充大部分字段
error_info = error_handler.reporter.report_error(
    exception, 
    context={"operation": "data_processing", "batch_id": 123}
)

# 转换为字典用于日志
log_data = error_info.to_dict()
print(f"错误ID: {error_info.error_id}")
print(f"严重性: {error_info.severity.value}")
```

## 核心类

### XRetryMechanism

重试机制类，提供智能重试功能，支持指数退避和抖动。

#### 初始化参数

```python
def __init__(self, 
             max_retries: int = 3,
             base_delay: float = 1.0,
             max_delay: float = 60.0,
             exponential_base: float = 2.0,
             jitter: bool = True):
```

**参数说明：**
- `max_retries`: 最大重试次数（默认: 3）
- `base_delay`: 基础延迟时间（秒，默认: 1.0）
- `max_delay`: 最大延迟时间（秒，默认: 60.0）
- `exponential_base`: 指数退避的底数（默认: 2.0）
- `jitter`: 是否添加随机抖动以防止雷群效应（默认: True）

#### 主要方法

##### calculate_delay(attempt: int) -> float

计算指定重试次数的延迟时间。

```python
retry_mechanism = XRetryMechanism(base_delay=1.0, exponential_base=2.0)

# 计算各次重试的延迟时间
for i in range(4):
    delay = retry_mechanism.calculate_delay(i)
    print(f"第{i+1}次重试延迟: {delay:.2f}秒")
    
# 输出示例（带抖动）:
# 第1次重试延迟: 0.85秒
# 第2次重试延迟: 1.73秒
# 第3次重试延迟: 4.21秒
# 第4次重试延迟: 7.94秒
```

##### should_retry(exception: Exception, attempt: int) -> bool

判断是否应该重试操作。

```python
# 可重试的异常类型
retryable_exceptions = (
    ConnectionError,        # 连接错误
    TimeoutError,          # 超时错误
    OSError,               # 系统IO错误
    IOError,               # 文件IO错误
    requests.ConnectionError, # requests库连接错误
    requests.Timeout       # requests库超时
)

# 使用示例
try:
    api_call()
except Exception as e:
    if retry_mechanism.should_retry(e, current_attempt):
        # 执行重试
        pass
    else:
        # 不重试，直接抛出异常
        raise
```

##### retry(func: Callable, *args, **kwargs) -> Any

执行带重试逻辑的函数调用。

```python
def unreliable_api_call():
    # 模拟不稳定的API调用
    if random.random() < 0.7:
        raise ConnectionError("网络连接失败")
    return {"status": "success", "data": "..."}

retry_mechanism = XRetryMechanism(max_retries=3, base_delay=0.5)

try:
    result = retry_mechanism.retry(unreliable_api_call)
    print(f"API调用成功: {result}")
except Exception as e:
    print(f"所有重试均失败: {e}")
```

### XErrorReporter

错误报告器，负责收集、分类和管理错误信息。

#### 主要方法

##### classify_error(exception: Exception) -> tuple[ErrorSeverity, ErrorCategory]

自动分类错误的严重性和类别。

```python
reporter = XErrorReporter()

# 测试不同类型的异常分类
exceptions = [
    MemoryError("内存不足"),
    ConnectionError("连接失败"),
    ValueError("数据格式错误"),
    FileNotFoundError("配置文件不存在")
]

for exc in exceptions:
    severity, category = reporter.classify_error(exc)
    print(f"{type(exc).__name__}: {severity.value} - {category.value}")

# 输出:
# MemoryError: CRITICAL - SYSTEM
# ConnectionError: HIGH - NETWORK  
# ValueError: MEDIUM - DATA
# FileNotFoundError: HIGH - CONFIG
```

##### extract_context(frame_info: Optional[inspect.FrameInfo] = None) -> Dict[str, Any]

从调用栈中提取上下文信息。

```python
def process_data(batch_id, data_list):
    batch_size = len(data_list)
    processing_mode = "fast"
    
    try:
        # 处理数据...
        raise ValueError("数据格式错误")
    except Exception as e:
        # 自动提取当前函数的上下文
        context = reporter.extract_context()
        print("提取的上下文:", context)
        
# 输出示例:
# {
#   "local_variables": {
#     "batch_id": 123,
#     "batch_size": 100, 
#     "processing_mode": "fast"
#   },
#   "function_args": {
#     "batch_id": 123,
#     "data_list": [...]
#   }
# }
```

##### report_error(exception, context=None, severity=None, category=None) -> ErrorInfo

报告错误并创建错误信息记录。

```python
reporter = XErrorReporter()

try:
    result = risky_operation()
except Exception as e:
    # 基础错误报告
    error_info = reporter.report_error(e)
    
    # 带自定义上下文的错误报告
    error_info = reporter.report_error(
        e,
        context={
            "operation": "data_processing",
            "batch_id": 123,
            "input_size": 1000
        },
        severity=ErrorSeverity.HIGH
    )
    
    print(f"错误已记录，ID: {error_info.error_id}")
```

##### get_error_summary() -> Dict[str, Any]

获取错误统计摘要。

```python
# 报告一些错误后...
summary = reporter.get_error_summary()

print("错误统计摘要:")
print(f"总错误数: {summary['total_errors']}")
print(f"严重性分布: {summary['severity_distribution']}")
print(f"类别分布: {summary['category_distribution']}")
print(f"最频繁错误: {summary['most_frequent_errors']}")

# 输出示例:
# {
#   "total_errors": 15,
#   "severity_distribution": {
#     "HIGH": 8,
#     "MEDIUM": 5, 
#     "CRITICAL": 2
#   },
#   "category_distribution": {
#     "NETWORK": 7,
#     "DATA": 5,
#     "SYSTEM": 3
#   },
#   "most_frequent_errors": {
#     "ConnectionError:网络连接超时": 5,
#     "ValueError:数据格式错误": 3
#   },
#   "recent_errors": [...]
# }
```

### XErrorHandler

统一错误处理器，是框架的核心错误处理组件，采用单例模式。

#### 初始化和获取实例

```python
# 方式1: 直接创建（推荐使用全局实例）
from xpertcorpus.utils.xerror_handler import error_handler

# 方式2: 手动创建实例
handler = XErrorHandler()  # 自动返回单例实例
```

#### 主要方法

##### handle_error(exception, context=None, should_raise=True, recovery_action=None) -> Optional[ErrorInfo]

处理错误的核心方法，提供完整的错误处理流程。

**参数说明：**
- `exception`: 要处理的异常对象
- `context`: 额外的上下文信息
- `should_raise`: 处理后是否重新抛出异常（默认: True）
- `recovery_action`: 可选的恢复操作函数

```python
def recovery_function():
    """错误恢复函数示例"""
    print("执行数据恢复操作...")
    # 执行恢复逻辑
    return "恢复成功"

try:
    risky_operation()
except Exception as e:
    # 基础错误处理
    error_handler.handle_error(e)
    
    # 不重新抛出异常
    error_info = error_handler.handle_error(
        e, 
        should_raise=False
    )
    
    # 带恢复操作的错误处理
    error_info = error_handler.handle_error(
        e,
        context={"operation_id": "OP123"},
        should_raise=False,
        recovery_action=recovery_function
    )
    
    if error_info is None:
        print("错误已通过恢复操作解决")
    else:
        print(f"错误处理完成，ID: {error_info.error_id}")
```

##### safe_execute(func, *args, fallback_value=None, retry_enabled=False, **kwargs) -> Any

安全执行函数，自动处理异常并可选择重试。

```python
# 基础安全执行
result = error_handler.safe_execute(
    risky_function,
    arg1, arg2,
    fallback_value="默认值"
)

# 启用重试的安全执行
result = error_handler.safe_execute(
    network_operation,
    url="https://api.example.com",
    retry_enabled=True,
    fallback_value={"error": "操作失败"}
)

# 复杂参数的安全执行
def process_data(data, mode="strict", timeout=30):
    # 处理逻辑
    return result

result = error_handler.safe_execute(
    process_data,
    my_data,                    # 位置参数
    mode="lenient",            # 关键字参数
    timeout=60,                # 关键字参数
    fallback_value=None,       # 失败时返回None
    retry_enabled=True         # 启用重试
)
```

## 装饰器

### @retry_on_failure

自动重试装饰器，为函数添加重试功能。

```python
from xpertcorpus.utils.xerror_handler import retry_on_failure

# 基础重试装饰器
@retry_on_failure(max_retries=3, base_delay=1.0)
def api_call():
    # 可能失败的API调用
    response = requests.get("https://api.example.com/data")
    return response.json()

# 自定义重试参数
@retry_on_failure(
    max_retries=5,
    base_delay=0.5,
    max_delay=30.0,
    exponential_base=1.5
)
def database_operation():
    # 数据库操作
    return db.query("SELECT * FROM table")

# 使用示例
try:
    data = api_call()
    print("API调用成功:", data)
except Exception as e:
    print("所有重试均失败:", e)
```

### @safe_execute

安全执行装饰器，自动处理异常并提供fallback值。

```python
from xpertcorpus.utils.xerror_handler import safe_execute

# 基础安全执行
@safe_execute(fallback_value="默认值")
def get_config_value():
    return config.get("some_key")

# 启用重试的安全执行
@safe_execute(fallback_value=[], retry_enabled=True)
def fetch_data_list():
    return api.get_data_list()

# 复杂fallback值
@safe_execute(fallback_value={"status": "error", "data": None})
def complex_operation():
    # 复杂操作
    return {"status": "success", "data": result}

# 使用示例
value = get_config_value()  # 失败时返回"默认值"
data_list = fetch_data_list()  # 失败时返回[]，会自动重试
result = complex_operation()  # 失败时返回错误状态字典
```

## 全局实例

### error_handler

框架提供的全局错误处理器实例，推荐在整个应用中使用。

```python
from xpertcorpus.utils.xerror_handler import error_handler

# 处理异常
try:
    operation()
except Exception as e:
    error_handler.handle_error(e, should_raise=False)

# 安全执行
result = error_handler.safe_execute(operation, fallback_value="default")

# 获取错误统计
summary = error_handler.get_error_summary()

# 清理错误记录
error_handler.clear_errors()
```

## 使用模式和最佳实践

### 1. 在算子中使用错误处理

```python
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.utils.xerror_handler import error_handler, safe_execute

class CustomOperator(OperatorABC):
    """自定义算子示例"""
    
    @safe_execute(fallback_value=None, retry_enabled=True)
    def process_batch(self, batch_data):
        """批处理方法，自动处理异常和重试"""
        try:
            # 处理逻辑
            result = self._internal_process(batch_data)
            return result
        except Exception as e:
            # 记录详细错误信息
            error_handler.handle_error(
                e,
                context={
                    "operator": self.__class__.__name__,
                    "batch_size": len(batch_data),
                    "batch_id": getattr(batch_data, 'id', 'unknown')
                },
                should_raise=False
            )
            return None
    
    def run(self):
        """主运行方法"""
        batches = self.get_data_batches()
        results = []
        
        for batch in batches:
            result = self.process_batch(batch)
            if result is not None:
                results.append(result)
        
        return results
```

### 2. 在管道中使用错误处理

```python
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.utils.xerror_handler import error_handler

class ProcessingPipeline(OperatorABC):
    """处理管道示例"""
    
    def __init__(self, operators):
        self.operators = operators
        self.error_tolerance = 0.1  # 10%的错误容忍率
    
    def run(self):
        """运行管道，统计错误情况"""
        total_items = len(self.input_data)
        processed_items = 0
        error_count = 0
        
        for item in self.input_data:
            try:
                # 通过所有算子处理数据
                result = item
                for operator in self.operators:
                    result = operator.process(result)
                
                processed_items += 1
                
            except Exception as e:
                error_count += 1
                error_handler.handle_error(
                    e,
                    context={
                        "pipeline": self.__class__.__name__,
                        "item_id": getattr(item, 'id', 'unknown'),
                        "operator": operator.__class__.__name__,
                        "progress": f"{processed_items}/{total_items}"
                    },
                    should_raise=False
                )
                
                # 检查是否超过错误容忍率
                error_rate = error_count / (processed_items + error_count)
                if error_rate > self.error_tolerance:
                    raise RuntimeError(f"错误率过高: {error_rate:.2%}")
        
        # 返回处理结果和统计信息
        return {
            "processed_items": processed_items,
            "error_count": error_count,
            "error_rate": error_count / total_items,
            "error_summary": error_handler.get_error_summary()
        }
```

### 3. 错误监控和报警

```python
import time
from xpertcorpus.utils.xerror_handler import error_handler
from xpertcorpus.utils.xlogger import xlogger

class ErrorMonitor:
    """错误监控类"""
    
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.last_error_count = 0
        
    def monitor_errors(self):
        """监控错误情况并发出警报"""
        while True:
            summary = error_handler.get_error_summary()
            current_error_count = summary.get('total_errors', 0)
            
            # 检查新增错误
            new_errors = current_error_count - self.last_error_count
            if new_errors > 0:
                xlogger.warning(f"检测到 {new_errors} 个新错误", data={
                    "total_errors": current_error_count,
                    "severity_distribution": summary.get('severity_distribution', {}),
                    "category_distribution": summary.get('category_distribution', {})
                })
                
                # 检查严重错误
                critical_errors = summary.get('severity_distribution', {}).get('CRITICAL', 0)
                if critical_errors > 0:
                    xlogger.error(f"发现 {critical_errors} 个严重错误！", data={
                        "recent_errors": summary.get('recent_errors', [])
                    })
                    # 这里可以添加报警逻辑（邮件、短信等）
            
            self.last_error_count = current_error_count
            time.sleep(self.check_interval)
    
    def generate_error_report(self):
        """生成错误报告"""
        summary = error_handler.get_error_summary()
        
        report = f"""
        错误统计报告
        ============
        总错误数: {summary.get('total_errors', 0)}
        
        严重性分布:
        {self._format_distribution(summary.get('severity_distribution', {}))}
        
        类别分布:
        {self._format_distribution(summary.get('category_distribution', {}))}
        
        最频繁错误:
        {self._format_frequent_errors(summary.get('most_frequent_errors', {}))}
        """
        
        return report
    
    def _format_distribution(self, distribution):
        """格式化分布统计"""
        if not distribution:
            return "  无数据"
        
        lines = []
        for key, count in distribution.items():
            lines.append(f"  {key}: {count}")
        return "\n".join(lines)
    
    def _format_frequent_errors(self, frequent_errors):
        """格式化频繁错误"""
        if not frequent_errors:
            return "  无数据"
        
        lines = []
        for error_key, count in list(frequent_errors.items())[:5]:
            lines.append(f"  {error_key}: {count}次")
        return "\n".join(lines)

# 使用示例
monitor = ErrorMonitor(check_interval=30)
# monitor.monitor_errors()  # 在后台线程中运行
```

## 配置和定制

### 自定义重试策略

```python
class CustomRetryMechanism(XRetryMechanism):
    """自定义重试机制"""
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """自定义重试判断逻辑"""
        if attempt >= self.max_retries:
            return False
        
        # 自定义可重试的异常类型
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return True
        
        # 根据错误消息判断
        if "temporary" in str(exception).lower():
            return True
        
        # 特定业务异常的处理
        if isinstance(exception, CustomBusinessException):
            return exception.is_retryable
        
        return False
    
    def calculate_delay(self, attempt: int) -> float:
        """自定义延迟计算"""
        # 实现自定义的延迟策略
        if attempt < 2:
            return 1.0  # 前两次重试快速
        else:
            return super().calculate_delay(attempt)  # 后续使用指数退避

# 使用自定义重试机制
custom_retry = CustomRetryMechanism(max_retries=5)
error_handler.retry_mechanism = custom_retry
```

### 自定义错误分类

```python
class CustomErrorReporter(XErrorReporter):
    """自定义错误报告器"""
    
    def classify_error(self, exception: Exception) -> tuple[ErrorSeverity, ErrorCategory]:
        """自定义错误分类逻辑"""
        
        # 优先处理自定义异常
        if isinstance(exception, CustomBusinessException):
            return exception.severity, exception.category
        
        # 针对特定模块的错误分类
        if "database" in str(exception).lower():
            return ErrorSeverity.HIGH, ErrorCategory.SYSTEM
        
        # 使用默认分类
        return super().classify_error(exception)
    
    def extract_context(self, frame_info=None):
        """扩展上下文提取"""
        context = super().extract_context(frame_info)
        
        # 添加自定义上下文信息
        context.update({
            "timestamp": datetime.now().isoformat(),
            "process_id": os.getpid(),
            "thread_id": threading.current_thread().ident,
            "memory_usage": self._get_memory_usage()
        })
        
        return context
    
    def _get_memory_usage(self):
        """获取内存使用情况"""
        import psutil
        process = psutil.Process()
        return {
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "percent": process.memory_percent()
        }

# 使用自定义错误报告器
custom_reporter = CustomErrorReporter()
error_handler.reporter = custom_reporter
```

## 性能考虑

### 异步错误处理

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncErrorHandler(XErrorHandler):
    """异步错误处理器"""
    
    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def handle_error_async(self, exception, context=None):
        """异步错误处理"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中执行错误处理
        error_info = await loop.run_in_executor(
            self.executor,
            self.reporter.report_error,
            exception,
            context
        )
        
        # 异步日志记录
        await self._log_error_async(error_info)
        
        return error_info
    
    async def _log_error_async(self, error_info):
        """异步日志记录"""
        # 这里可以实现异步日志写入
        pass

# 使用异步错误处理
async_handler = AsyncErrorHandler()

async def process_data():
    try:
        # 处理数据
        pass
    except Exception as e:
        await async_handler.handle_error_async(e)
```

### 内存优化

```python
class MemoryOptimizedErrorReporter(XErrorReporter):
    """内存优化的错误报告器"""
    
    def __init__(self, max_errors=1000):
        super().__init__()
        self.max_errors = max_errors
    
    def report_error(self, exception, context=None, severity=None, category=None):
        """报告错误，自动清理旧记录"""
        error_info = super().report_error(exception, context, severity, category)
        
        # 限制内存中保存的错误数量
        if len(self.errors) > self.max_errors:
            # 删除最旧的错误记录
            self.errors = self.errors[-self.max_errors:]
            
            # 清理错误计数器
            self._cleanup_error_counts()
        
        return error_info
    
    def _cleanup_error_counts(self):
        """清理错误计数器"""
        # 只保留最常见的错误计数
        if len(self.error_counts) > 100:
            sorted_counts = sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            self.error_counts = dict(sorted_counts[:100])
```

## 故障排除

### 常见问题

1. **重试机制不生效**
   ```python
   # 确保异常类型在可重试列表中
   retryable_exceptions = (ConnectionError, TimeoutError, OSError, IOError)
   
   # 检查重试次数设置
   retry_mechanism = XRetryMechanism(max_retries=3)  # 确保 > 0
   ```

2. **错误上下文信息缺失**
   ```python
   # 手动提供上下文信息
   error_handler.handle_error(
       exception,
       context={
           "operation": "data_processing",
           "input_size": len(data),
           "current_step": "validation"
       }
   )
   ```

3. **内存使用过高**
   ```python
   # 定期清理错误记录
   error_handler.clear_errors()
   
   # 或使用内存优化的报告器
   optimized_reporter = MemoryOptimizedErrorReporter(max_errors=500)
   error_handler.reporter = optimized_reporter
   ```

### 调试技巧

```python
# 启用详细的错误日志
import logging
logging.getLogger('xpertcorpus.utils.xerror_handler').setLevel(logging.DEBUG)

# 查看错误统计
summary = error_handler.get_error_summary()
print(f"当前错误统计: {summary}")

# 导出错误记录
import json
errors_data = [error.to_dict() for error in error_handler.reporter.errors]
with open('error_log.json', 'w') as f:
    json.dump(errors_data, f, indent=2, ensure_ascii=False)
```

## 版本历史

- **v0.1.0** (2025-08-13)
  - 初始版本发布
  - 实现基础错误处理、重试机制、错误报告功能
  - 支持错误分类、上下文收集、统计分析
  - 提供装饰器和全局实例

---

[返回工具层文档](README.md) | [返回API文档首页](../README.md) 