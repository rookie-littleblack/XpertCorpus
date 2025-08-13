# 框架层 API 文档

框架层是 XpertCorpus 架构的顶层，提供端到端的业务解决方案。每个框架都是完整的数据处理管道，专注于特定的训练数据生成场景。

## 架构概述

框架层基于统一的 `FrameworkABC` 抽象基类，提供标准化的接口和生命周期管理。所有框架都支持：

- **🔄 生命周期管理** - 8种状态的完整生命周期
- **⚙️ 配置驱动** - 灵活的配置系统
- **🛡️ 错误处理** - 统一异常处理和恢复
- **📊 性能监控** - 内置指标收集和报告
- **🔌 组件管理** - 算子和管道的统一管理

## 框架列表

### 🚀 [预训练框架 (xframe_pt)](xframe_pt.md)
从原始语料生成预训练数据的完整解决方案。

**适用场景：**
- 大规模语料预处理
- 文本清洗和标准化
- 智能文本分割
- 质量过滤和去重

**核心功能：**
- 原始语料处理（txt/md → jsonl）
- LLM驱动的文本清洗
- 多阶段清理管道
- 语义感知的文本分割
- 完整的处理链路

**支持格式：**
- 输入：原始文本目录或JSONL文件
- 输出：标准化的训练数据

### 🎯 [监督微调框架 (xframe_sft)](xframe_sft.md)
生成监督微调（SFT）训练数据的专用框架。

**适用场景：**
- 指令微调数据构建
- 对话数据生成
- 任务特化数据准备

**核心功能：**
- 指令-响应对生成
- 对话格式标准化
- 质量评估和过滤
- 多轮对话支持

### 🧠 [思维链框架 (xframe_cot)](xframe_cot.md)
专注于推理链数据生成的框架。

**适用场景：**
- 逻辑推理数据构建
- 数学问题求解链
- 复杂推理过程展示

**核心功能：**
- 推理步骤分解
- 思维链格式化
- 逻辑一致性检查
- 推理质量评估

### 🎨 [多模态框架 (xframe_multimodal)](xframe_multimodal.md)
处理图像、文本等多模态数据的综合框架。

**适用场景：**
- 图文配对数据处理
- 多模态对话数据
- 视觉问答数据构建

**核心功能：**
- 多模态数据对齐
- 图像特征提取
- 文本-图像关联
- 多模态质量检测

## 框架基类

### FrameworkABC

所有框架的抽象基类，定义了统一的接口和行为模式。

```python
from xpertcorpus.modules.others.xframework import FrameworkABC, FrameworkType

class CustomFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
    REQUIRED_OPERATORS = ["cleaner", "splitter"]
    REQUIRED_PIPELINES = ["preprocessing"]
    
    def _on_init(self):
        """框架特定初始化"""
        pass
    
    def _prepare_components(self):
        """准备组件"""
        pass
    
    def _execute_pipeline(self):
        """执行管道"""
        return {"status": "completed"}
    
    def get_desc(self, lang="zh"):
        """获取描述"""
        return "自定义框架"
```

## 使用模式

### 标准使用流程

```python
from xpertcorpus.modules.frameworks import XFramework_PT

# 1. 创建框架实例
framework = XFramework_PT(
    input_file="corpus_directory/",
    output_dir="./output",
    max_workers=4,
    config={
        "text_splitter": {
            "chunk_size": 1024,
            "split_method": "semantic"
        },
        "processing": {
            "enable_compression": True,
            "validate_on_write": True
        }
    }
)

# 2. 准备组件
framework.prepare()

# 3. 执行处理
results = framework.run()

# 4. 获取结果信息
print(f"输出路径: {results['output_path']}")
print(f"处理统计: {framework.get_metrics()}")
```

### 生命周期管理

```python
# 检查状态
print(f"当前状态: {framework.get_state()}")

# 获取详细信息
info = framework.get_info()
print(f"框架信息: {info}")

# 获取性能指标
metrics = framework.get_metrics()
print(f"执行时间: {metrics['total_processing_time']}s")
print(f"处理文件: {metrics['files_processed']}")
```

### 事件钩子

```python
def on_start(framework):
    print(f"开始执行 {framework.__class__.__name__}")

def on_complete(framework):
    metrics = framework.get_metrics()
    print(f"执行完成，耗时 {metrics['total_processing_time']:.2f}s")

framework.add_hook("before_run", on_start)
framework.add_hook("on_complete", on_complete)
```

### 错误处理

```python
try:
    results = framework.run()
except Exception as e:
    # 获取错误信息
    error_info = framework.get_info()
    print(f"执行失败: {error_info}")
    
    # 检查错误指标
    metrics = framework.get_metrics()
    print(f"错误次数: {metrics['errors_count']}")
```

## 配置系统

每个框架都支持层次化的配置系统：

```python
config = {
    # 存储配置
    "storage": {
        "enable_compression": True,
        "validate_on_write": True,
        "cache_type": "jsonl"
    },
    
    # 处理配置
    "processing": {
        "batch_size": 100,
        "max_retries": 3,
        "timeout": 300
    },
    
    # 组件特定配置
    "text_splitter": {
        "chunk_size": 1024,
        "chunk_overlap": 200,
        "split_method": "semantic"
    },
    
    "llm_cleaner": {
        "enable_token_tracking": True,
        "temperature": 0.7
    }
}

framework = XFramework_PT(
    input_file="data.jsonl",
    config=config
)
```

## 性能监控

框架提供丰富的性能指标：

```python
metrics = framework.get_metrics()

# 时间指标
print(f"总执行时间: {metrics['total_processing_time']:.2f}s")
print(f"平均文件处理时间: {metrics.get('files_per_second', 0):.2f} files/s")

# 数据指标
print(f"处理文件数: {metrics['files_processed']}")
print(f"处理记录数: {metrics['records_processed']}")
print(f"处理令牌数: {metrics['tokens_processed']}")

# 质量指标
print(f"错误次数: {metrics['errors_count']}")
print(f"管道步骤: {metrics['pipeline_steps_completed']}")
```

## 最佳实践

### 1. 配置管理

```python
# 推荐：使用配置文件
import yaml

with open("framework_config.yaml", "r") as f:
    config = yaml.safe_load(f)

framework = XFramework_PT(input_file="data.jsonl", config=config)
```

### 2. 错误处理

```python
# 推荐：使用钩子处理错误
def error_handler(framework, error):
    print(f"框架执行出错: {error}")
    # 保存中间结果
    framework.save_checkpoint()

framework.add_hook("on_error", error_handler)
```

### 3. 资源管理

```python
# 推荐：使用上下文管理器
class FrameworkContext:
    def __init__(self, framework):
        self.framework = framework
    
    def __enter__(self):
        self.framework.prepare()
        return self.framework
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.framework.cleanup()

with FrameworkContext(framework) as f:
    results = f.run()
```

## 扩展开发

### 自定义框架

```python
from xpertcorpus.modules.others.xframework import FrameworkABC, FrameworkType, register_framework

@register_framework("custom")
class CustomFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
    
    def _on_init(self):
        # 框架特定初始化
        pass
    
    def _prepare_components(self):
        # 初始化算子和管道
        pass
    
    def _execute_pipeline(self):
        # 执行处理逻辑
        return {"results": "success"}
    
    def get_desc(self, lang="zh"):
        return "自定义处理框架"
```

## 版本兼容性

- **API 版本**: v0.1.0
- **Python 版本**: 3.10+
- **框架基类版本**: v0.1.0

## 依赖关系

```
框架层依赖：
├── modules.others.xframework (框架基类)
├── operators.* (各种算子)
├── pipelines.* (各种管道)
└── utils.xerror_handler (错误处理)
```

---

**提示**: 建议结合具体框架的文档和[教程](../../tutorials/README.md)一起学习，以更好地理解框架的使用方式和最佳实践。 