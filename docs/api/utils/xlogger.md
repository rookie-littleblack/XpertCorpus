# 日志系统 (xlogger)

`xpertcorpus.utils.xlogger` 模块提供结构化日志记录系统，支持JSON格式输出、彩色控制台显示和自动文件轮转功能。

## 模块概述

日志系统提供统一的日志记录功能，支持JSON格式的文件输出和彩色的控制台输出，具备自动文件轮转能力。

## 核心组件

### Colors

颜色定义类，用于控制台输出的颜色显示。

```python
class Colors:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
```

### ColoredFormatter

彩色格式化器，为不同日志级别提供颜色显示。

```python
class ColoredFormatter(logging.Formatter):
    """为控制台输出添加颜色"""
    
    COLORS = {
        'DEBUG': Colors.BLUE,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.MAGENTA
    }
```

### CustomTimedRotatingFileHandler

自定义的定时轮转文件处理器，支持按时间轮转日志文件。

```python
class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """自定义定时轮转文件处理器"""
    
    def __init__(self, log_dir, log_filename, when='midnight', interval=1, backupCount=7, encoding='utf-8'):
        """初始化文件处理器"""
```

### CustomJSONLogger

主要的日志记录器类，提供结构化JSON日志输出。

```python
class CustomJSONLogger:
    """JSON格式日志记录器"""
    
    @classmethod
    def get_instance(cls, log_dir="logs", log_filename="xapp.log", version="1.0", console_output=True):
        """获取单例实例"""
    
    def __init__(self, log_dir="logs", log_filename="xapp.log", version="1.0", console_output=True):
        """初始化日志器"""
```

#### 主要方法

```python
def log(self, message, data=None, log_level=None, category=None, version=None, tags=None):
    """核心日志记录方法"""
    
def debug(self, message, data=None, category=None, version=None, tags=None):
    """调试级别日志"""
    
def info(self, message, data=None, category=None, version=None, tags=None):
    """信息级别日志"""
    
def success(self, message, data=None, category=None, version=None, tags=None):
    """成功级别日志（等同于info）"""
    
def warning(self, message, data=None, category=None, version=None, tags=None):
    """警告级别日志"""
    
def error(self, message, data=None, category=None, version=None, tags=None):
    """错误级别日志"""
    
def exceptions(self, message, category=None, version=None, tags=None):
    """异常日志"""
```

## 全局实例

模块提供了一个全局的日志器实例：

```python
from xpertcorpus.utils.xlogger import xlogger

# xlogger 是 CustomJSONLogger 的全局单例实例
xlogger = CustomJSONLogger.get_instance()
```

## 使用示例

### 基本日志记录

```python
from xpertcorpus.utils.xlogger import xlogger

# 不同级别的日志
xlogger.debug("调试信息")
xlogger.info("开始处理数据")
xlogger.success("处理成功")
xlogger.warning("检测到潜在问题")
xlogger.error("处理失败")
```

### 带数据的结构化日志

```python
# 记录带有附加数据的日志
xlogger.info("处理完成", data={
    "processed_count": 1000,
    "success_rate": 0.95,
    "duration": 120.5
})

xlogger.error("处理失败", data={
    "error_code": "ERR_001",
    "file_path": "/path/to/file.txt",
    "line_number": 42
})
```

### 自定义日志实例

```python
from xpertcorpus.utils.xlogger import CustomJSONLogger

# 创建自定义日志实例
custom_logger = CustomJSONLogger(
    log_dir="custom_logs",
    log_filename="custom.log",
    version="2.0",
    console_output=True
)

custom_logger.info("自定义日志消息")
```

## 日志格式

### 文件输出格式（JSON）

日志文件以JSON格式存储，包含以下字段：

```json
{
  "time": "2025-08-13 14:30:45.123456",
  "version": "1.0",
  "level": "INFO",
  "category": "script_name.py",
  "tags": null,
  "env": "dev",
  "message": {
    "text": "处理完成",
    "processed_count": 1000,
    "success_rate": 0.95
  }
}
```

### 控制台输出格式

控制台输出为简化的彩色格式：

```
2025-08-13 14:30:45.123456 - INFO - script_name.py: 处理完成
```

## 文件管理

### 自动轮转

- 默认按天轮转（midnight）
- 保留7天的备份文件
- 轮转文件存储在 `daily_backup` 子目录

### 目录结构

```
logs/
├── xapp.log                    # 当前日志文件
└── daily_backup/
    ├── 20250813_xapp.log      # 历史日志文件
    ├── 20250812_xapp.log
    └── ...
```

## 特性说明

### 单例模式
`CustomJSONLogger` 使用单例模式，确保全局只有一个日志实例。

### 调用者信息
错误日志会自动记录调用者的文件名、行号和类名信息。

### 字符编码处理
内置字符编码处理，防止Unicode错误。

### 环境感知
自动检测 `PROJ_ENV` 环境变量，默认为 'dev'。

## 相关文档

- [异常处理 (xerror_handler)](xerror_handler.md)
- [配置管理 (xconfig)](xconfig.md)

---

[返回 Utils 模块首页](README.md) | [返回 API 文档首页](../README.md) 