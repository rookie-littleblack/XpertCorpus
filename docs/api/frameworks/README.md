# 框架层 API 文档

框架层是 XpertCorpus 架构的顶层，提供端到端的业务解决方案。每个框架都是一个完整的数据处理管道，专注于特定的训练数据生成场景。

## 架构概述

框架层基于统一的 `FrameworkABC` 抽象基类，提供标准化的接口和生命周期管理。所有框架都支持：

- **🔄 生命周期管理** - 定义了框架从初始化到完成的完整状态流。
- **⚙️ 配置驱动** - 通过灵活的字典配置来控制框架和其组件的行为。
- **🛡️ 错误处理** - 集成了统一的异常处理和恢复机制。
- **📊 性能监控** - 内置了对处理时间、数量和错误的指标收集。
- **🔌 组件管理** - 提供了对算子（Operators）和管道（Pipelines）的统一管理接口。

## 框架列表

### 🚀 [预训练框架 (xframe_pt)](xframe_pt.md)
从原始语料生成预训练数据的完整解决方案。

**适用场景：**
- 大规模语料的预处理
- 文本清洗和标准化
- 智能文本分割

**核心功能：**
- 原始语料处理（支持从文本目录自动转换为JSONL）
- 基于大语言模型的文本清洗
- 多阶段、可定制的清理管道
- 语义感知的文本分割

**支持格式：**
- 输入：原始文本目录或JSONL文件
- 输出：标准化的JSONL训练数据

## 框架基类 (FrameworkABC)

所有框架的抽象基类，定义了统一的接口和行为模式。开发者可以通过继承此类来创建自定义框架。

```python
from xpertcorpus.modules.others.xframework import FrameworkABC, FrameworkType

class CustomFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
    
    def _on_init(self):
        """框架的特定初始化逻辑"""
        pass
    
    def _prepare_components(self):
        """准备框架所需的组件，如操作符和管道"""
        pass
    
    def _execute_pipeline(self):
        """执行框架的核心处理管道"""
        return {"status": "completed"}
    
    def get_desc(self, lang="zh"):
        """获取框架的中英文描述"""
        return "这是一个自定义框架"
```

## 使用模式

### 标准使用流程

```python
from xpertcorpus.modules.frameworks import XFramework_PT

# 1. 创建框架实例并传入配置
framework = XFramework_PT(
    input_file="path/to/your/corpus_directory/",
    output_dir="./output",
    max_workers=4,
    config={
        "text_splitter": {
            "chunk_size": 1024
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

### 事件钩子

通过事件钩子，可以在框架生命周期的关键节点执行自定义逻辑。

```python
def on_start(framework):
    print(f"开始执行 {framework.__class__.__name__}")

def on_complete(framework):
    metrics = framework.get_metrics()
    print(f"执行完成，耗时 {metrics['total_processing_time']:.2f}s")

# 添加钩子
framework.add_hook("before_run", on_start)
framework.add_hook("on_complete", on_complete)

# 执行框架时会自动触发钩子
framework.run()
```

---

[返回 API 文档首页](../README.md) 