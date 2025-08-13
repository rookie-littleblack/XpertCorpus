# 日志系统 (xlogger)

`xpertcorpus.utils.xlogger` 模块提供结构化日志记录系统，支持JSON格式输出、彩色控制台显示和自动文件轮转功能。

## 模块概述

日志系统是 XpertCorpus 框架的核心基础设施，负责：
- 结构化JSON格式日志输出
- 彩色控制台日志显示
- 自动日志文件轮转管理
- 多级别日志记录支持
- 统一的日志接口抽象

## 核心类

### CustomJSONLogger (JSON日志器)

核心的日志记录器，提供结构化JSON格式的日志输出。

#### 主要方法

##### 基础日志方法

```python
def debug(self, message: str, data: Optional[Dict] = None) -> None
def info(self, message: str, data: Optional[Dict] = None) -> None  
def warning(self, message: str, data: Optional[Dict] = None) -> None
def error(self, message: str, data: Optional[Dict] = None) -> None
def critical(self, message: str, data: Optional[Dict] = None) -> None
```

**参数：**
- `message`: 日志消息
- `data`: 附加的结构化数据（可选）

**使用示例：**
```python
from xpertcorpus.utils.xlogger import xlogger

# 基础日志记录
xlogger.info("开始处理数据")
xlogger.warning("检测到潜在问题")
xlogger.error("处理失败")

# 带结构化数据的日志
xlogger.info("处理完成", data={
    "processed_count": 1000,
    "success_rate": 0.95,
    "duration": 120.5
})

# 错误日志包含异常信息
try:
    risky_operation()
except Exception as e:
    xlogger.error("操作失败", data={
        "error_type": type(e).__name__,
        "error_message": str(e),
        "stack_trace": traceback.format_exc()
    })
```

#### JSON输出格式

日志输出为标准JSON格式，包含以下字段：

```json
{
    "timestamp": "2025-08-13T10:30:45.123456",
    "level": "INFO",
    "logger": "xpertcorpus",
    "message": "处理完成",
    "module": "xoperator.py",
    "function": "execute",
    "line": 156,
    "data": {
        "processed_count": 1000,
        "success_rate": 0.95,
        "duration": 120.5
    }
}
```

### CustomTimedRotatingFileHandler (定时轮转文件处理器)

自动轮转日志文件的处理器，避免单个日志文件过大。

#### 特性

- **自动轮转**：按时间间隔自动创建新日志文件
- **文件命名**：带时间戳的日志文件命名
- **压缩支持**：可选择压缩旧日志文件
- **文件清理**：自动删除过期日志文件

#### 配置参数

```python
# 在日志系统初始化时配置
handler = CustomTimedRotatingFileHandler(
    filename="logs/xpertcorpus.log",
    when="midnight",        # 轮转时机：midnight, H, D, W0-W6
    interval=1,             # 轮转间隔
    backupCount=30,         # 保留文件数量
    encoding="utf-8"        # 文件编码
)
```

### ColoredFormatter (彩色格式化器)

为控制台输出提供彩色日志显示的格式化器。

#### 颜色方案

- **DEBUG**: 蓝色
- **INFO**: 绿色  
- **WARNING**: 黄色
- **ERROR**: 红色
- **CRITICAL**: 紫色高亮

#### 使用示例

```python
import logging
from xpertcorpus.utils.xlogger import ColoredFormatter

# 为控制台处理器添加彩色格式
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())

logger = logging.getLogger("my_logger")
logger.addHandler(console_handler)
```

## 全局日志实例

### xlogger (全局日志器)

预配置的全局日志器实例，可直接使用。

```python
from xpertcorpus.utils.xlogger import xlogger

# 直接使用全局日志器
xlogger.info("系统启动")
xlogger.debug("调试信息", data={"debug_data": "value"})
xlogger.error("系统错误")
```

## 使用模式

### 基础日志记录

```python
from xpertcorpus.utils.xlogger import xlogger

def process_data(data_file):
    """数据处理函数示例"""
    
    xlogger.info("开始处理数据文件", data={"file": data_file})
    
    try:
        # 数据处理逻辑
        records = load_data(data_file)
        xlogger.debug("数据加载完成", data={"record_count": len(records)})
        
        processed_records = []
        for i, record in enumerate(records):
            processed_record = process_record(record)
            processed_records.append(processed_record)
            
            # 定期记录进度
            if i % 1000 == 0:
                xlogger.info("处理进度", data={
                    "processed": i,
                    "total": len(records),
                    "progress": f"{i/len(records)*100:.1f}%"
                })
        
        xlogger.info("数据处理完成", data={
            "input_count": len(records),
            "output_count": len(processed_records),
            "success_rate": len(processed_records) / len(records)
        })
        
        return processed_records
        
    except Exception as e:
        xlogger.error("数据处理失败", data={
            "file": data_file,
            "error": str(e),
            "error_type": type(e).__name__
        })
        raise
```

### 结构化数据记录

```python
# 性能监控日志
def log_performance_metrics(operation_name, start_time, end_time, **metrics):
    duration = end_time - start_time
    
    xlogger.info("性能指标", data={
        "operation": operation_name,
        "duration_seconds": duration,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        **metrics
    })

# 业务事件日志
def log_business_event(event_type, user_id=None, **event_data):
    xlogger.info("业务事件", data={
        "event_type": event_type,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "event_data": event_data
    })

# 使用示例
import time
from datetime import datetime

start = datetime.now()
# ... 执行操作 ...
end = datetime.now()

log_performance_metrics(
    "data_processing",
    start, end,
    records_processed=1000,
    memory_used_mb=256,
    cpu_percent=45.2
)

log_business_event(
    "corpus_generation_completed",
    user_id="user123",
    corpus_type="pretraining",
    output_size_mb=1024,
    quality_score=0.95
)
```

### 条件日志记录

```python
def debug_enabled_function():
    """在调试模式下记录详细信息"""
    
    # 检查日志级别
    if xlogger.isEnabledFor(logging.DEBUG):
        detailed_data = collect_debug_info()  # 可能耗时的调试信息收集
        xlogger.debug("详细调试信息", data=detailed_data)
    
    # 普通信息日志
    xlogger.info("函数执行")

# 性能敏感的日志记录
def performance_critical_operation(data):
    operation_id = generate_operation_id()
    
    # 只在必要时记录
    if len(data) > 10000:  # 大数据集时记录
        xlogger.info("开始处理大数据集", data={
            "operation_id": operation_id,
            "data_size": len(data)
        })
    
    result = process_data(data)
    
    # 记录结果摘要
    xlogger.info("操作完成", data={
        "operation_id": operation_id,
        "input_size": len(data),
        "output_size": len(result),
        "processing_time": get_processing_time()
    })
    
    return result
```

### 异常和错误处理

```python
def robust_operation_with_logging():
    """带完整日志记录的健壮操作"""
    
    operation_context = {
        "operation_id": str(uuid.uuid4()),
        "start_time": datetime.now().isoformat(),
        "component": "data_processor"
    }
    
    xlogger.info("开始执行操作", data=operation_context)
    
    try:
        # 主要业务逻辑
        result = execute_main_logic()
        
        # 成功日志
        xlogger.info("操作成功完成", data={
            **operation_context,
            "result_summary": summarize_result(result),
            "end_time": datetime.now().isoformat()
        })
        
        return result
        
    except ValidationError as e:
        # 业务验证错误
        xlogger.warning("数据验证失败", data={
            **operation_context,
            "validation_error": str(e),
            "error_fields": e.error_fields if hasattr(e, 'error_fields') else None
        })
        raise
        
    except ConnectionError as e:
        # 网络连接错误
        xlogger.error("网络连接失败", data={
            **operation_context,
            "connection_error": str(e),
            "retry_recommended": True
        })
        raise
        
    except Exception as e:
        # 未预期的系统错误
        xlogger.critical("系统异常", data={
            **operation_context,
            "exception_type": type(e).__name__,
            "exception_message": str(e),
            "stack_trace": traceback.format_exc(),
            "system_info": get_system_info()
        })
        raise

# 错误恢复日志
def operation_with_retry():
    max_retries = 3
    
    for attempt in range(max_retries + 1):
        try:
            return execute_operation()
            
        except Exception as e:
            if attempt == max_retries:
                xlogger.error("重试次数耗尽，操作最终失败", data={
                    "total_attempts": attempt + 1,
                    "final_error": str(e)
                })
                raise
            else:
                xlogger.warning("操作失败，准备重试", data={
                    "attempt": attempt + 1,
                    "max_retries": max_retries,
                    "error": str(e),
                    "retry_delay": 2 ** attempt
                })
                time.sleep(2 ** attempt)  # 指数退避
```

## 配置和自定义

### 日志级别配置

```python
import logging
from xpertcorpus.utils.xlogger import xlogger

# 设置日志级别
xlogger.setLevel(logging.DEBUG)    # 显示所有日志
xlogger.setLevel(logging.INFO)     # 显示INFO及以上级别
xlogger.setLevel(logging.WARNING)  # 只显示WARNING、ERROR、CRITICAL
xlogger.setLevel(logging.ERROR)    # 只显示ERROR和CRITICAL
```

### 自定义日志格式

```python
from xpertcorpus.utils.xlogger import CustomJSONLogger
import logging

# 创建自定义日志器
custom_logger = CustomJSONLogger("custom_logger")

# 添加自定义字段
class ExtendedJSONLogger(CustomJSONLogger):
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, **kwargs):
        record = super().makeRecord(name, level, fn, lno, msg, args, exc_info, **kwargs)
        
        # 添加自定义字段
        record.application = "XpertCorpus"
        record.version = "0.1.0"
        record.environment = "production"
        
        return record

# 使用扩展日志器
extended_logger = ExtendedJSONLogger("extended")
extended_logger.info("扩展日志消息")
```

### 多目标输出

```python
import logging
from xpertcorpus.utils.xlogger import CustomJSONLogger, CustomTimedRotatingFileHandler, ColoredFormatter

# 创建多输出目标的日志器
multi_logger = CustomJSONLogger("multi_output")

# 文件输出（JSON格式）
file_handler = CustomTimedRotatingFileHandler(
    filename="logs/app.log",
    when="midnight",
    backupCount=7
)
multi_logger.addHandler(file_handler)

# 控制台输出（彩色格式）
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
multi_logger.addHandler(console_handler)

# 错误日志单独输出
error_handler = CustomTimedRotatingFileHandler(
    filename="logs/error.log",
    when="midnight", 
    backupCount=30
)
error_handler.setLevel(logging.ERROR)
multi_logger.addHandler(error_handler)
```

## 性能优化

### 延迟日志格式化

```python
# 避免不必要的字符串格式化
def expensive_debug_info():
    # 这是一个耗时的调试信息收集函数
    return {"expensive_data": "collected"}

# 错误方式：总是执行格式化
xlogger.debug(f"调试信息: {expensive_debug_info()}")

# 正确方式：使用延迟格式化
if xlogger.isEnabledFor(logging.DEBUG):
    xlogger.debug("调试信息", data=expensive_debug_info())

# 或使用lambda延迟求值
def lazy_log_debug(message_func, data_func=None):
    if xlogger.isEnabledFor(logging.DEBUG):
        data = data_func() if data_func else None
        xlogger.debug(message_func(), data=data)

# 使用示例
lazy_log_debug(
    lambda: "处理状态更新",
    lambda: {"current_state": get_expensive_state_info()}
)
```

### 批量日志记录

```python
class BatchLogger:
    """批量日志记录器，减少I/O操作"""
    
    def __init__(self, batch_size=100, flush_interval=30):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()
    
    def add_log(self, level, message, data=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "data": data
        }
        
        self.buffer.append(log_entry)
        
        # 检查是否需要刷新
        if (len(self.buffer) >= self.batch_size or 
            time.time() - self.last_flush > self.flush_interval):
            self.flush()
    
    def flush(self):
        if self.buffer:
            # 批量写入日志
            xlogger.info("批量日志记录", data={
                "batch_size": len(self.buffer),
                "logs": self.buffer
            })
            
            self.buffer.clear()
            self.last_flush = time.time()

# 使用批量日志记录器
batch_logger = BatchLogger(batch_size=50)

for i in range(1000):
    batch_logger.add_log("INFO", f"处理记录 {i}", {"record_id": i})

# 确保剩余日志被写入
batch_logger.flush()
```

## 日志分析和监控

### 结构化日志查询

```python
import json
from datetime import datetime, timedelta

def analyze_logs(log_file, start_time=None, end_time=None, level=None):
    """分析结构化日志文件"""
    
    results = []
    
    with open(log_file, 'r') as f:
        for line in f:
            try:
                log_entry = json.loads(line.strip())
                
                # 时间过滤
                if start_time or end_time:
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue
                
                # 级别过滤
                if level and log_entry['level'] != level:
                    continue
                
                results.append(log_entry)
                
            except json.JSONDecodeError:
                continue
    
    return results

# 使用示例
yesterday = datetime.now() - timedelta(days=1)
error_logs = analyze_logs(
    "logs/xpertcorpus.log",
    start_time=yesterday,
    level="ERROR"
)

print(f"昨天共有 {len(error_logs)} 个错误")
```

### 日志统计报告

```python
def generate_log_report(log_file, report_period_hours=24):
    """生成日志统计报告"""
    
    logs = analyze_logs(log_file)
    
    # 按级别统计
    level_counts = {}
    error_types = {}
    operation_stats = {}
    
    for log in logs:
        level = log['level']
        level_counts[level] = level_counts.get(level, 0) + 1
        
        # 错误分析
        if level == 'ERROR' and 'data' in log:
            error_type = log['data'].get('error_type', 'Unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        # 操作统计
        if 'data' in log and 'operation' in log['data']:
            op = log['data']['operation']
            if op not in operation_stats:
                operation_stats[op] = {'count': 0, 'total_duration': 0}
            operation_stats[op]['count'] += 1
            
            if 'duration_seconds' in log['data']:
                operation_stats[op]['total_duration'] += log['data']['duration_seconds']
    
    # 生成报告
    report = {
        "report_period_hours": report_period_hours,
        "total_logs": len(logs),
        "level_distribution": level_counts,
        "top_errors": dict(sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:10]),
        "operation_performance": {
            op: {
                "count": stats['count'],
                "avg_duration": stats['total_duration'] / stats['count'] if stats['count'] > 0 else 0
            }
            for op, stats in operation_stats.items()
        }
    }
    
    # 记录报告
    xlogger.info("日志分析报告", data=report)
    
    return report
```

## 最佳实践

### 1. 日志消息规范

```python
# 好的日志消息
xlogger.info("用户认证成功", data={"user_id": "12345", "login_method": "oauth"})
xlogger.error("数据库连接失败", data={"database": "postgres", "retry_count": 3})

# 避免的日志消息
xlogger.info("success")  # 信息不足
xlogger.error("error occurred")  # 没有上下文
xlogger.debug("debugging stuff here...")  # 临时调试信息
```

### 2. 敏感信息处理

```python
def sanitize_sensitive_data(data):
    """清理敏感数据用于日志记录"""
    sanitized = data.copy()
    
    sensitive_fields = ['password', 'token', 'secret', 'key', 'api_key']
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "***REDACTED***"
    
    return sanitized

# 安全的日志记录
user_data = {"username": "john", "password": "secret123", "email": "john@example.com"}
xlogger.info("用户数据处理", data=sanitize_sensitive_data(user_data))
```

### 3. 上下文管理

```python
import contextvars

# 创建上下文变量
request_id = contextvars.ContextVar('request_id')
user_id = contextvars.ContextVar('user_id')

class ContextualLogger:
    """带上下文的日志记录器"""
    
    def log(self, level, message, data=None):
        # 自动添加上下文信息
        context_data = {
            "request_id": request_id.get(None),
            "user_id": user_id.get(None)
        }
        
        if data:
            context_data.update(data)
        
        getattr(xlogger, level.lower())(message, data=context_data)

# 使用上下文日志记录器
context_logger = ContextualLogger()

def handle_request():
    request_id.set("req_12345")
    user_id.set("user_67890")
    
    context_logger.log("INFO", "处理请求开始")
    # ... 处理逻辑 ...
    context_logger.log("INFO", "处理请求完成")
```

### 4. 生产环境配置

```python
# 生产环境日志配置
def configure_production_logging():
    """配置生产环境日志"""
    
    # 设置适当的日志级别
    xlogger.setLevel(logging.INFO)
    
    # 配置文件轮转
    file_handler = CustomTimedRotatingFileHandler(
        filename="/var/log/xpertcorpus/app.log",
        when="midnight",
        interval=1,
        backupCount=90,  # 保留90天
        encoding="utf-8"
    )
    
    # 错误日志单独存储
    error_handler = CustomTimedRotatingFileHandler(
        filename="/var/log/xpertcorpus/error.log", 
        when="midnight",
        backupCount=365,  # 错误日志保留1年
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    
    xlogger.addHandler(file_handler)
    xlogger.addHandler(error_handler)
    
    # 禁用控制台输出（生产环境）
    xlogger.handlers = [h for h in xlogger.handlers if not isinstance(h, logging.StreamHandler)]

# 开发环境日志配置
def configure_development_logging():
    """配置开发环境日志"""
    
    # 开发环境显示所有级别
    xlogger.setLevel(logging.DEBUG)
    
    # 保持彩色控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    xlogger.addHandler(console_handler)
```

## 注意事项

### 1. 性能影响

- 避免在紧密循环中记录大量日志
- 使用适当的日志级别
- 考虑异步日志记录以减少I/O阻塞

### 2. 存储管理

- 定期清理旧日志文件
- 监控日志文件大小和磁盘使用
- 考虑日志压缩和归档策略

### 3. 安全考虑

- 不要记录密码、令牌等敏感信息
- 控制日志文件的访问权限
- 考虑日志数据的隐私合规

### 4. 调试支持

- 保持调试级别日志的详细程度
- 使用结构化数据便于查询和分析
- 记录足够的上下文信息

---

**更多信息：**
- [错误处理 (xerror_handler)](xerror_handler.md)
- [配置管理 (xconfig)](xconfig.md)
- [存储管理 (xstorage)](xstorage.md) 