# 配置管理 (xconfig)

`xpertcorpus.utils.xconfig` 模块提供YAML配置文件加载功能。

## 模块概述

配置管理模块提供简单的YAML配置文件加载功能，用于读取和管理XpertCorpus的配置信息。

## 核心类

### XConfigLoader

配置加载器类，用于加载和访问YAML配置文件。

```python
from xpertcorpus.utils.xconfig import XConfigLoader

class XConfigLoader:
    """Config loader for CorpusFlow."""
    
    def __init__(self, config_path="xpertcorpus/config/config.yaml"):
        """初始化配置加载器"""
```

#### 构造函数

```python
def __init__(self, config_path="xpertcorpus/config/config.yaml"):
    """
    初始化配置加载器。
    
    Args:
        config_path: 配置文件路径，默认为 xpertcorpus/config/config.yaml
    """
```

#### 主要方法

```python
def load_config(self):
    """加载配置文件"""
    
def get_llm_model_config(self):
    """获取LLM模型配置"""
    
def get_vision_model_config(self):
    """获取视觉模型配置"""
    
def get_embedding_model_config(self):
    """获取嵌入模型配置"""
    
def get_rarank_model_config(self):
    """获取重排序模型配置"""
```

## 使用示例

### 基本使用

```python
from xpertcorpus.utils.xconfig import XConfigLoader

# 使用默认配置文件路径
config_loader = XConfigLoader()

# 获取不同模型的配置
llm_config = config_loader.get_llm_model_config()
vision_config = config_loader.get_vision_model_config()
embedding_config = config_loader.get_embedding_model_config()
rerank_config = config_loader.get_rarank_model_config()

print("LLM配置:", llm_config)
print("视觉模型配置:", vision_config)
```

### 自定义配置文件

```python
# 使用自定义配置文件路径
config_loader = XConfigLoader("path/to/your/config.yaml")

# 手动加载配置
config = config_loader.load_config()

# 获取特定模型配置
llm_config = config_loader.get_llm_model_config()
```

### 配置文件格式

配置文件应为YAML格式，包含以下结构：

```yaml
llm_model:
  provider: "openai"
  model: "gpt-3.5-turbo"
  api_key: "your_api_key"

vision_model:
  provider: "openai"
  model: "gpt-4-vision"
  
embedding_model:
  provider: "openai"
  model: "text-embedding-ada-002"
  
rarank_model:
  provider: "cohere"
  model: "rerank-multilingual-v2.0"
```

## 错误处理

配置加载器会自动处理以下错误情况：

- 配置文件不存在时抛出 `FileNotFoundError`
- YAML解析错误时抛出相应异常
- 错误信息会记录到日志系统

## 相关文档

- [日志系统 (xlogger)](xlogger.md)
- [异常处理 (xerror_handler)](xerror_handler.md)

---

[返回 Utils 模块首页](README.md) | [返回 API 文档首页](../README.md) 