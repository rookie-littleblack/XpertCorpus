# 管道基础系统 (xpipeline)

`xpertcorpus.modules.others.xpipeline` 模块提供了 XpertCorpus 管道的抽象基类和管道管理功能。

## 模块概述

管道基础系统为 XpertCorpus 提供简单而实用的管道抽象接口，用于编排多个算子按顺序执行复杂的数据处理任务。

## 核心组件

### PipelineState

管道生命周期状态枚举。

```python
from xpertcorpus.modules.others.xpipeline import PipelineState

class PipelineState(Enum):
    INITIALIZED = "INITIALIZED"    # 已初始化
    CONFIGURED = "CONFIGURED"      # 已配置
    RUNNING = "RUNNING"           # 运行中
    COMPLETED = "COMPLETED"       # 已完成
    FAILED = "FAILED"             # 失败
    STOPPED = "STOPPED"           # 已停止
```

#### 状态说明

| 状态 | 含义 | 进入时机 | 可用操作 |
|------|------|----------|----------|
| **INITIALIZED** | 🚀 管道已初始化 | `__init__()` 完成后 | `run()` |
| **CONFIGURED** | ✅ 算子已配置完成 | `_configure_operators()` 后 | `run()` |
| **RUNNING** | 🏃 正在执行处理 | `run()` 执行过程中 | `stop()` |
| **COMPLETED** | 🎉 执行成功完成 | `run()` 成功结束后 | 查看结果, 重新 `run()` |
| **FAILED** | ❌ 执行失败 | 任何阶段出错后 | `reset()` 重新开始 |
| **STOPPED** | ⏹️ 用户主动停止 | 调用 `stop()` 后 | `reset()` |

## 核心抽象类

### PipelineABC

管道抽象基类，定义了所有管道必须实现的核心接口。

```python
class PipelineABC(ABC):
    """Abstract base class for data processing pipelines."""
    
    VERSION: str = "1.0.0"  # 可选的版本号
```

#### 构造函数

```python
def __init__(self, 
             max_workers: int = 1, 
             limit: int = 0, 
             config: Optional[Dict[str, Any]] = None):
    """
    初始化管道。
    
    Args:
        max_workers: 工作线程数
        limit: 处理限制（0表示无限制）
        config: 可选配置字典
    """
```

#### 抽象方法（必须实现）

```python
@abstractmethod
def _configure_operators(self) -> None:
    """配置管道中的算子。在子类中实现。"""
    pass

@abstractmethod
def run(self, storage, input_key: str = "raw_content", output_key: Optional[str] = None) -> str:
    """
    执行管道处理。
    
    Args:
        storage: 存储实例
        input_key: 输入数据键
        output_key: 输出数据键（为空时自动生成）
        
    Returns:
        输出数据键
    """
    pass

@abstractmethod
def get_desc(self, lang: str = "zh") -> str:
    """获取管道描述"""
    pass
```

#### 算子管理方法

```python
def add_operator(self, operator: OperatorABC) -> 'PipelineABC':
    """添加算子到管道"""
    
def get_operators(self) -> List[OperatorABC]:
    """获取管道中的算子列表"""
```

#### 状态管理方法

```python
def get_state(self) -> PipelineState:
    """获取当前状态"""
    
def reset(self) -> 'PipelineABC':
    """重置管道到初始状态"""
    
def stop(self) -> None:
    """停止管道执行"""
```

#### 信息获取方法

```python
def get_metadata(self) -> Dict[str, Any]:
    """获取管道元数据"""
    
def get_metrics(self) -> Dict[str, Any]:
    """获取性能指标"""
```

## 使用示例

### 基本管道实现

```python
from xpertcorpus.modules.others.xpipeline import PipelineABC, register_pipeline
from xpertcorpus.modules.microops import RemoveEmoticonsMicroops, RemoveEmojiMicroops

@register_pipeline("custom_pipeline")
class CustomPipeline(PipelineABC):
    """自定义文本处理管道"""
    
    VERSION = "1.0.0"
    
    def _configure_operators(self):
        """配置管道算子"""
        # 添加多个微算子
        self.add_operator(RemoveEmoticonsMicroops())
        self.add_operator(RemoveEmojiMicroops())
    
    def get_desc(self, lang="zh"):
        if lang == "zh":
            return "自定义文本处理管道"
        else:
            return "Custom text processing pipeline"
    
    def run(self, storage, input_key="raw_content", output_key=None):
        """执行管道处理"""
        try:
            self.state = PipelineState.RUNNING
            
            # 获取数据
            dataframe = storage.read('dataframe')
            
            # 处理逻辑...
            # 应用所有算子
            for operator in self.operators:
                # 处理数据
                pass
            
            # 保存结果
            output_file = storage.write(dataframe)
            self.state = PipelineState.COMPLETED
            
            return output_key
            
        except Exception as e:
            self.state = PipelineState.FAILED
            raise
```

### 使用管道

```python
# 创建管道实例
pipeline = CustomPipeline(max_workers=4, limit=1000)

# 查看管道状态
print(f"管道状态: {pipeline.get_state()}")
print(f"算子数量: {len(pipeline.get_operators())}")

# 执行管道
result_key = pipeline.run(storage, input_key="raw_content")

# 查看执行结果
print(f"执行完成，输出键: {result_key}")
print(f"性能指标: {pipeline.get_metrics()}")
```

### 错误处理

```python
try:
    result = pipeline.run(storage)
except Exception as e:
    print(f"管道执行失败: {e}")
    print(f"管道状态: {pipeline.get_state()}")
    
    # 重置管道
    pipeline.reset()
```

## 设计特点

### 简单实用
- 🎯 **专注核心功能**：专注于算子编排，避免过度复杂
- 📝 **清晰接口**：简单明确的抽象方法
- 🔧 **易于扩展**：通过添加算子轻松扩展功能

### 状态管理
- 📊 **基础状态跟踪**：6种核心状态覆盖主要场景
- 📈 **性能监控**：内置执行次数、时间等基础指标
- 🔄 **生命周期管理**：支持重置和停止操作

### 组件协调
- 🔗 **算子编排**：统一管理多个算子的执行顺序
- ⚡ **并行支持**：内置多线程处理能力
- 🎛️ **配置驱动**：支持通过配置控制行为

## 与其他抽象类的关系

```
数据处理层次:
FrameworkABC (框架层) - 完整业务流程
    ↓
PipelineABC (管道层) - 多算子编排
    ↓  
OperatorABC (算子层) - 单一功能实现
```

### 职责对比

| 抽象类 | 职责 | 复杂度 | 使用场景 |
|--------|------|---------|----------|
| **FrameworkABC** | 端到端业务流程 | 高 | 预训练、微调等完整工作流 |
| **PipelineABC** | 多算子编排 | 中 | 文本清洗、格式转换等处理流程 |
| **OperatorABC** | 单一功能实现 | 低 | LLM调用、文本分割等具体操作 |

## 最佳实践

### 1. 管道设计

```python
# ✅ 推荐：职责明确的管道
class TextCleaningPipeline(PipelineABC):
    def _configure_operators(self):
        self.add_operator(RemoveEmoticonsMicroops())
        self.add_operator(RemoveEmojiMicroops())
        self.add_operator(RemoveExtraSpacesMicroops())

# ❌ 不推荐：职责过于复杂
class EverythingPipeline(PipelineABC):
    def _configure_operators(self):
        # 包含太多不相关的操作
        self.add_operator(...)  # 50+ operators
```

### 2. 错误处理

```python
def run(self, storage, input_key, output_key):
    try:
        self.state = PipelineState.RUNNING
        # 处理逻辑
        self.state = PipelineState.COMPLETED
        return output_key
    except Exception as e:
        self.state = PipelineState.FAILED
        self.metrics["error_count"] += 1
        raise  # 重新抛出异常
```

### 3. 性能监控

```python
def run(self, storage, input_key, output_key):
    start_time = datetime.now()
    try:
        # 处理逻辑
        execution_time = (datetime.now() - start_time).total_seconds()
        self.metrics["total_processing_time"] += execution_time
        self.metrics["last_execution_time"] = execution_time
    except Exception:
        # 错误处理
```

## 相关文档

- [算子基类 (xoperator)](xoperator.md)
- [框架基类 (xframework)](xframework.md)
- [注册系统 (xregistry)](xregistry.md)

---

[返回 Others 模块首页](README.md) | [返回 API 文档首页](../README.md) 