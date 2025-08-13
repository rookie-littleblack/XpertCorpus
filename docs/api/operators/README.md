# 算子层 API 文档

算子层为 XpertCorpus 提供核心的数据处理功能，实现具体的数据转换和处理操作。

## 模块概述

算子层是 XpertCorpus 四层架构中的核心处理层，每个算子都继承自 `OperatorABC`，负责执行特定的数据处理任务。算子具有良好的可复用性，可以在不同的管道和框架中使用。

## 设计理念

### 职责定位
- **原子操作**：每个算子执行单一、明确的数据处理任务
- **高内聚**：相关功能聚合在一个算子中
- **低耦合**：算子之间相互独立，可以自由组合
- **可复用**：同一个算子可以在多个管道中重复使用

### 架构层次
```
FrameworkABC (框架层) - 完整业务流程
    ↓
PipelineABC (管道层) - 多算子编排
    ↓  
OperatorABC (算子层) - 原子操作 ← 当前层
```

## 现有算子

### 🤖 文本处理算子

#### XLlmCleaner - LLM文本清洗器
**功能**: 使用大语言模型进行智能文本清洗和优化

**核心特性**:
- 基于 LLM 的智能文本清洗
- 支持多种清洗策略
- 内置 token 使用统计
- 并发处理支持

**使用场景**:
- 原始文本数据清洗
- 内容质量提升
- 格式标准化

**注册名**: `llm_cleaner`

#### XTextSplitter - 智能文本分割器
**功能**: 将长文本智能分割为合适大小的文本块

**核心特性**:
- 多种分割策略（语义分割、Markdown分割）
- 可配置的块大小和重叠
- 保持语义完整性
- Token 计数支持

**使用场景**:
- 长文档处理
- 向量化预处理
- 模型输入准备

**注册名**: `text_splitter`

**注意**: 数据限制器 `XLimitor` 实际上位于基础设施层 (`xpertcorpus.modules.others.xlimitor`)，详见 [XLimitor 文档](../others/xlimitor.md)。

## 算子开发指南

### 创建新算子

```python
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator

@register_operator("my_operator")
class MyOperator(OperatorABC):
    """自定义算子示例"""
    
    VERSION = "1.0.0"
    
    def __init__(self, param1="default", config=None):
        super().__init__(config)
        self.param1 = param1
    
    def run(self, input_data):
        """执行核心处理逻辑"""
        # 处理输入数据
        processed_data = self._process(input_data)
        return processed_data
    
    def get_desc(self, lang="zh"):
        """获取算子描述"""
        if lang == "zh":
            return "自定义数据处理算子"
        else:
            return "Custom data processing operator"
    
    def _process(self, data):
        """具体的处理逻辑"""
        # 实现具体处理
        return data
```

### 最佳实践

#### 1. 单一职责
```python
# ✅ 推荐：专注单一功能
@register_operator("text_normalizer")
class TextNormalizer(OperatorABC):
    def run(self, text):
        return self._normalize_text(text)

# ❌ 不推荐：功能过于复杂
@register_operator("everything_processor")
class EverythingProcessor(OperatorABC):
    def run(self, data):
        # 同时做清洗、分割、格式化... 职责不清
        pass
```

#### 2. 状态管理
```python
def run(self, input_data):
    try:
        self.state = OperatorState.RUNNING
        result = self._process_data(input_data)
        self.state = OperatorState.COMPLETED
        return result
    except Exception as e:
        self.state = OperatorState.FAILED
        raise
```

#### 3. 错误处理
```python
def run(self, input_data):
    try:
        # 验证输入
        self._validate_input(input_data)
        
        # 处理数据
        result = self._process_data(input_data)
        
        # 验证输出
        self._validate_output(result)
        
        return result
    except Exception as e:
        self.metrics["error_count"] += 1
        raise
```

## 配置系统

### 算子配置
```python
# 创建配置
config = {
    "batch_size": 100,
    "enable_validation": True,
    "processing_mode": "fast"
}

# 使用配置
operator = MyOperator(config=config)
```

### 动态配置
```python
class ConfigurableOperator(OperatorABC):
    def run(self, input_data):
        # 根据配置调整行为
        if self.config.get("enable_detailed_processing", False):
            return self._detailed_process(input_data)
        else:
            return self._fast_process(input_data)
```

## 性能优化

### 批处理
```python
def run(self, input_data):
    batch_size = self.config.get("batch_size", 100)
    
    # 分批处理大数据集
    results = []
    for i in range(0, len(input_data), batch_size):
        batch = input_data[i:i + batch_size]
        batch_result = self._process_batch(batch)
        results.extend(batch_result)
    
    return results
```

### 缓存机制
```python
def __init__(self, config=None):
    super().__init__(config)
    self._cache = {}
    
def run(self, input_data):
    # 使用缓存避免重复计算
    cache_key = self._get_cache_key(input_data)
    if cache_key in self._cache:
        return self._cache[cache_key]
    
    result = self._process_data(input_data)
    self._cache[cache_key] = result
    return result
```

## 测试和调试

### 单元测试
```python
import pytest
from your_operator import MyOperator

def test_my_operator():
    operator = MyOperator()
    
    # 测试正常输入
    result = operator.run("test input")
    assert result == "expected output"
    
    # 测试异常情况
    with pytest.raises(ValueError):
        operator.run(None)
```

### 性能测试
```python
import time

def test_operator_performance():
    operator = MyOperator()
    
    start_time = time.time()
    result = operator.run(large_dataset)
    end_time = time.time()
    
    processing_time = end_time - start_time
    assert processing_time < 10.0  # 应在10秒内完成
```

## 监控和指标

### 性能监控
```python
# 获取算子性能指标
metrics = operator.get_metrics()
print(f"执行次数: {metrics['execution_count']}")
print(f"平均执行时间: {metrics['average_execution_time']:.2f}s")
print(f"错误次数: {metrics['error_count']}")
```

### 状态检查
```python
# 检查算子状态
print(f"算子状态: {operator.get_state()}")
if operator.get_state() == OperatorState.FAILED:
    print("算子执行失败，需要重置")
    operator.reset()
```

## 扩展性

### 算子组合
```python
# 多个算子串联使用
text_cleaner = XLlmCleaner()
text_splitter = XTextSplitter(chunk_size=512)

# 处理流程
cleaned_text = text_cleaner.run(raw_text)
chunks = text_splitter.run(cleaned_text)
```

### 继承扩展
```python
class EnhancedTextSplitter(XTextSplitter):
    """增强的文本分割器"""
    
    def run(self, input_text):
        # 预处理
        preprocessed = self._preprocess(input_text)
        
        # 使用父类分割
        chunks = super().run(preprocessed)
        
        # 后处理
        enhanced_chunks = self._postprocess(chunks)
        
        return enhanced_chunks
```

## 相关文档

- [微操作层 (microops)](../microops/) - 微操作文档
- [算子基类 (xoperator)](../others/xoperator.md) - 算子抽象基类文档
- [管道层 (pipelines)](../pipelines/) - 管道编排文档
- [框架层 (frameworks)](../frameworks/) - 框架系统文档

---

[返回 API 文档首页](../README.md) 