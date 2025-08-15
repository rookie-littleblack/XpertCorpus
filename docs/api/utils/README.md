# 工具层 API 文档

工具层为 XpertCorpus 框架提供基础支撑功能，包括日志、配置、存储、异常处理等核心服务。

## 模块列表

### 🚨 [异常处理 (xerror_handler)](xerror_handler.md)
提供统一的异常处理、重试机制和错误报告功能。

**核心类：**
- `XErrorHandler` - 统一异常处理器
- `XRetryMechanism` - 重试机制
- `XErrorReporter` - 错误报告器
- `ErrorInfo` - 错误信息数据结构

**主要功能：**
- 异常分类和严重性评估
- 自动重试机制（支持指数退避）
- 错误上下文收集
- 统计报告和分析


### 📋 [日志系统 (xlogger)](xlogger.md)
结构化日志记录系统，支持JSON格式和彩色控制台输出。

**核心类：**
- `CustomJSONLogger` - JSON格式日志器
- `CustomTimedRotatingFileHandler` - 定时轮转文件处理器
- `ColoredFormatter` - 彩色格式化器

**主要功能：**
- 结构化JSON日志输出
- 日志文件自动轮转
- 彩色控制台输出
- 多级别日志支持

### ⚙️ [配置管理 (xconfig)](xconfig.md)
YAML配置文件加载和管理。

**核心类：**
- `XConfigLoader` - 配置加载器

**主要功能：**
- YAML配置文件解析
- 配置参数验证
- 环境变量支持
- 配置热加载

### 💾 [存储管理 (xstorage)](xstorage.md)
多格式文件读写和数据存储管理。

**核心类：**
- `XpertCorpusStorage` - 存储抽象基类
- `FileStorage` - 文件存储实现

**主要功能：**
- 多格式支持（JSONL, CSV, Parquet, Pickle）
- 数据压缩和验证功能
- 流式处理大文件
- 完整性检查和元数据管理

### 🔧 [工具函数 (xutils)](xutils.md)
通用工具函数和令牌计数功能。

**核心函数：**
- `get_xtokenizer()` - 获取分词器
- `count_tokens()` - 令牌计数

**主要功能：**
- 文本令牌化
- 令牌数量统计
- 文本处理工具函数

### 📊 [数据可视化工具 (xvis)](xvis.md)
基于Streamlit的JSONL语料文件可视化查看工具。

**核心类：**
- `JSONLViewer` - JSONL文件查看器
- `main()` - Streamlit应用入口

**主要功能：**
- 多文件批量加载和浏览
- 字段搜索和过滤
- 智能导航和跳转
- Tokens字段自动合并
- 数据统计和源文件追踪

**相关脚本：**
- [`vis.py`](vis_entry.md) - 可视化工具启动器

## 使用模式

### 单独导入
```python
from xpertcorpus.utils.xerror_handler import XErrorHandler
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xconfig import XConfigLoader
```

### 批量导入
```python
from xpertcorpus.utils import (
    XErrorHandler,
    xlogger,
    XConfigLoader,
    FileStorage,
    count_tokens,
    JSONLViewer
)
```

### 全局实例
```python
from xpertcorpus.utils.xerror_handler import error_handler
from xpertcorpus.utils.xlogger import xlogger

# 使用全局单例
error_handler.handle_error(exception)
xlogger.info("Processing completed")
```

## 最佳实践

### 1. 异常处理
```python
from xpertcorpus.utils import error_handler, safe_execute

# 使用装饰器
@safe_execute(fallback_value="default", retry_enabled=True)
def risky_operation():
    # 可能失败的操作
    pass

# 手动处理
try:
    result = some_operation()
except Exception as e:
    error_handler.handle_error(e, should_raise=False)
```

### 2. 日志记录
```python
from xpertcorpus.utils import xlogger

# 结构化日志
xlogger.info("Processing started", data={
    "file_count": 100,
    "batch_size": 32
})

# 错误日志
xlogger.error("Processing failed", data={
    "error_code": "DATA_001",
    "file_path": "/path/to/file"
})
```

### 3. 配置管理
```python
from xpertcorpus.utils import XConfigLoader

config_loader = XConfigLoader()
config = config_loader.load_config("config.yaml")

# 访问配置
model_config = config_loader.get_model_config()
api_config = config_loader.get_api_config()
```

### 4. 数据可视化
```python
from xpertcorpus.utils import JSONLViewer

# 创建查看器
viewer = JSONLViewer()

# 加载文件
file_paths = ["/path/to/corpus1.jsonl", "/path/to/corpus2.jsonl"]
success = viewer.load_files(file_paths, max_records=1000)

# 搜索和导航
results = viewer.search("content", "关键词")
current_record = viewer.navigate(1)
```

### 5. Web界面启动
```bash
# 启动可视化工具
python -m xpertcorpus.vis

# 或直接运行
streamlit run xpertcorpus/utils/xvis.py
```

## 依赖关系

```
工具层内部依赖：

xstorage → xerror_handler → xlogger    # 存储系统依赖错误处理和日志
xutils → xlogger                       # 工具函数依赖日志系统

外部依赖：
- PyYAML (配置管理)
- pandas (存储管理) 
- transformers (工具函数)
- streamlit (数据可视化)
- markdown (可视化渲染)
```

## 版本历史

- **v0.1.0** (2025-08-13)
  - 初始版本
  - 实现基础的异常处理、日志、配置、存储功能
  - 添加令牌计数工具函数
  - 完善存储系统（压缩、验证、流式处理）
  - 添加JSONL数据可视化工具（xvis）
  - 集成Streamlit Web界面和智能字段合并功能


---

[返回 API 文档首页](../README.md) 