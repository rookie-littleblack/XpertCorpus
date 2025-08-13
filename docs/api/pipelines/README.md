# 管道层 API 文档

管道层为 XpertCorpus 提供多算子编排功能，实现复杂的数据处理流程。

## 模块概述

管道层位于框架层和算子层之间，专注于将多个算子组合成有序的处理流程。每个管道都继承自 `PipelineABC`，提供统一的接口和生命周期管理。

## 设计理念

### 职责定位
- **算子编排**：将多个原子操作组合成完整的处理流程
- **流程控制**：管理数据在不同算子间的流转
- **并行协调**：支持多线程并行处理
- **状态管理**：跟踪管道执行状态和性能指标

### 架构层次
```
FrameworkABC (框架层) - 完整业务流程
    ↓
PipelineABC (管道层) - 多算子编排 ← 当前层
    ↓  
OperatorABC (算子层) - 单一功能实现
```

## 现有管道

### 🧹 [文本清洗管道 (xcleaning_pipe)](xcleaning_pipe.md)
专用于文本清洗的处理管道。

**核心特性：**
- 集成多种文本清洗微操作
- 支持多线程并行处理
- 表情符号和emoji移除
- 可配置的处理限制

**使用场景：**
- 原始文本数据预处理
- 社交媒体文本清洗
- 语料库标准化

**性能特点：**
- 并行处理，显著提升性能
- 流式处理，内存使用稳定
- 错误容错，单行失败不影响整体

## 管道开发指南

### 创建新管道

```python
from xpertcorpus.modules.others.xpipeline import PipelineABC, PipelineState, register_pipeline

@register_pipeline("custom_pipeline")
class CustomPipeline(PipelineABC):
    """自定义处理管道"""
    
    VERSION = "1.0.0"
    
    def _configure_operators(self):
        """配置管道中的算子"""
        self.add_operator(RemoveEmoticonsMicroops())
        self.add_operator(RemoveEmojiMicroops())
        self.add_operator(RemoveExtraSpacesMicroops())
    
    def get_desc(self, lang="zh"):
        """获取管道描述"""
        return "自定义数据处理管道"
    
    def run(self, storage, input_key="raw_content", output_key=None):
        """执行管道处理"""
        try:
            self.state = PipelineState.RUNNING
            
            # 数据处理逻辑
            dataframe = storage.read('dataframe')
            
            # 应用所有算子
            for operator in self.operators:
                # 处理逻辑
                pass
            
            # 保存结果
            storage.write(dataframe)
            self.state = PipelineState.COMPLETED
            
            return output_key
            
        except Exception as e:
            self.state = PipelineState.FAILED
            raise
```

### 最佳实践

#### 1. 算子组织
```python
# ✅ 推荐：相关功能的算子组合
class TextNormalizationPipeline(PipelineABC):
    def _configure_operators(self):
        self.add_operator(RemoveEmoticonsMicroops())
        self.add_operator(RemoveEmojiMicroops())
        self.add_operator(RemoveExtraSpacesMicroops())

# ❌ 不推荐：无关功能混合
class EverythingPipeline(PipelineABC):
    def _configure_operators(self):
        self.add_operator(RemoveEmoticonsMicroops())  # 文本清洗
        self.add_operator(SomeImageProcessor())       # ❌ 图像处理 - 职责不相关
        self.add_operator(SomeDatabaseQuery())        # ❌ 数据库查询 - 职责不相关
```

#### 2. 状态管理
```python
def run(self, storage, input_key, output_key):
    start_time = datetime.now()
    
    try:
        # 设置运行状态
        self.state = PipelineState.RUNNING
        self.metrics["execution_count"] += 1
        
        # 处理逻辑
        result = self._process_data(storage, input_key, output_key)
        
        # 更新指标
        execution_time = (datetime.now() - start_time).total_seconds()
        self.metrics["total_processing_time"] += execution_time
        self.metrics["last_execution_time"] = execution_time
        
        # 设置完成状态
        self.state = PipelineState.COMPLETED
        return result
        
    except Exception as e:
        # 错误处理
        self.state = PipelineState.FAILED
        self.metrics["error_count"] += 1
        raise
```

#### 3. 并行处理
```python
from concurrent.futures import ThreadPoolExecutor

def run(self, storage, input_key, output_key):
    # 准备数据
    items = list(dataframe.iterrows())
    
    def process_item(row):
        content = row[1].get(input_key, '')
        # 应用所有算子
        for operator in self.operators:
            content = operator.run(content)
        return content
    
    # 并行处理
    with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
        results = list(executor.map(process_item, items))
    
    return results
```

## 配置系统

### 管道配置
```python
# 创建配置
config = {
    "batch_size": 1000,
    "enable_logging": True,
    "operator_configs": {
        "first_op": {"param1": "value1"},
        "second_op": {"param2": "value2"}
    }
}

# 使用配置
pipeline = CustomPipeline(
    max_workers=4,
    limit=50000,
    config=config
)
```

### 动态配置
```python
class ConfigurablePipeline(PipelineABC):
    def _configure_operators(self):
        # 根据配置动态添加算子
        if self.config.get("enable_cleaning", True):
            self.add_operator(CleaningMicroops())
        
        if self.config.get("enable_normalization", False):
            self.add_operator(NormalizationMicroops())
        
        # 可选的高级算子
        if self.config.get("enable_advanced", False):
            self.add_operator(AdvancedMicroops())
```

## 性能优化

### 并行处理策略
- **CPU密集型**：设置 `max_workers = cpu_count - 1`
- **IO密集型**：设置 `max_workers = cpu_count * 2`
- **内存限制**：使用 `limit` 参数分批处理

### 内存管理
```python
# 大数据集处理
pipeline = CustomPipeline(
    max_workers=4,
    limit=10000,  # 分批处理
    config={
        "use_streaming": True,
        "buffer_size": 1000
    }
)
```

## 错误处理

### 容错设计
```python
def process_item(self, item):
    try:
        # 处理单个项目
        for operator in self.operators:
            item = operator.run(item)
        return item
    except Exception as e:
        # 记录错误但继续处理
        xlogger.error(f"Error processing item: {e}")
        return item  # 返回原始数据
```

### 管道级错误
```python
def run(self, storage, input_key, output_key):
    try:
        # 管道处理逻辑
        return self._execute_pipeline(storage, input_key, output_key)
    except Exception as e:
        # 管道级错误处理
        self.state = PipelineState.FAILED
        self.metrics["error_count"] += 1
        xlogger.error(f"Pipeline {self.__class__.__name__} failed: {e}")
        raise
```

## 监控和调试

### 性能监控
```python
# 获取管道性能信息
metrics = pipeline.get_metrics()
print(f"执行次数: {metrics['execution_count']}")
print(f"平均执行时间: {metrics['average_execution_time']:.2f}s")
print(f"错误次数: {metrics['error_count']}")
```

### 状态跟踪
```python
# 执行前检查
print(f"执行前状态: {pipeline.get_state()}")

# 执行处理
result = pipeline.run(storage)

# 执行后检查
print(f"执行后状态: {pipeline.get_state()}")
if pipeline.get_state() == PipelineState.COMPLETED:
    print("管道执行成功")
```

## 扩展性

### 算子扩展
```python
class ExtendedPipeline(XCleaningPipe):
    """扩展现有管道"""
    
    def _configure_operators(self):
        # 保留原有算子
        super()._configure_operators()
        
        # 添加新算子
        self.add_operator(RemoveExtraSpacesMicroops())
```

### 配置扩展
```python
# 支持更多配置选项
extended_config = {
    "text_cleaning": {
        "remove_emoticons": True,
        "remove_emojis": True,
        "remove_extra_spaces": True
    },
    "performance": {
        "parallel_processing": True,
        "batch_size": 5000,
        "max_workers": 8
    }
}
```

## 相关文档

- [管道基类 (xpipeline)](../others/xpipeline.md) - 管道抽象基类文档
- [算子基类 (xoperator)](../others/xoperator.md) - 算子抽象基类文档
- [微操作模块 (microops)](../microops/) - 微操作实现文档
- [框架系统 (frameworks)](../frameworks/) - 框架层文档

---

[返回 API 文档首页](../README.md) 