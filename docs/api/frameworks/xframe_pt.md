# 预训练框架 (xframe_pt)

`xpertcorpus.modules.frameworks.xframe_pt` 模块提供了专用于预训练数据生成的端到端框架。

## 概述

XFramework_PT 是 XpertCorpus 的核心框架之一，专门用于处理原始语料并生成高质量的预训练数据。该框架集成了文本清洗、格式转换、智能分割等完整的处理链路。

### 核心特性

- **🗂️ 原始语料处理** - 支持从文本目录到JSONL的自动转换
- **🤖 LLM驱动清洗** - 基于大语言模型的智能文本清洗
- **🔄 多阶段管道** - 清洗、过滤、分割的完整处理流程
- **📊 质量保证** - 内置数据验证和质量检测
- **⚡ 高性能处理** - 多线程并发和流式处理支持
- **🧠 智能状态管理** - 自动状态检测和管道准备
- **🔧 配置驱动** - 灵活的配置系统和组件管理

## 类定义

### XFramework_PT

预训练数据生成框架的主类。

```python
@register_framework("pretraining")
class XFramework_PT(FrameworkABC):
    """预训练数据生成框架"""
    
    # 框架元数据
    FRAMEWORK_TYPE = FrameworkType.PRETRAINING
    VERSION = "1.0.0"
    REQUIRED_OPERATORS = ["llm_cleaner", "text_splitter"]
    REQUIRED_PIPELINES = ["cleaning_pipe"]
```

#### 构造方法

```python
def __init__(self, 
             input_file: str, 
             output_dir: str = "./output", 
             max_workers: int = 1, 
             limit: int = 0,
             config: Optional[Dict[str, Any]] = None):
    """
    初始化预训练框架。

    Args:
        input_file: 输入文件或目录路径
        output_dir: 输出目录路径
        max_workers: 工作线程数
        limit: 处理限制（0表示无限制）
        config: 可选配置字典

    Examples:
        >>> # 处理原始文本目录
        >>> framework = XFramework_PT(
        ...     input_file="corpus_directory/",
        ...     output_dir="./output",
        ...     max_workers=4
        ... )
        
        >>> # 处理JSONL文件
        >>> framework = XFramework_PT(
        ...     input_file="data.jsonl",
        ...     output_dir="./output"
        ... )
    """
```

## 配置系统

XFramework_PT 支持丰富的配置选项，采用层次化结构：

### 默认配置

```python
default_config = {
    # 文本分割器配置
    "text_splitter": {
        "chunk_size": 512,                    # 分块大小
        "chunk_overlap": 200,                 # 重叠长度
        "split_method": "markdown",           # 分割方法：markdown/semantic
        "min_tokens_per_chunk": 20           # 最小令牌数
    },
    
    # LLM清洗器配置
    "llm_cleaner": {
        "enable_token_tracking": True,        # 启用令牌追踪
        "reset_tokens_on_start": True        # 开始时重置令牌
    },
    
    # 存储配置
    "storage": {
        "enable_compression": False,          # 启用压缩
        "validate_on_write": True,           # 写入时验证
        "cache_type": "jsonl"                # 缓存类型
    },
    
    # 处理配置
    "processing": {
        "auto_detect_raw_corpus": True,      # 自动检测原始语料
        "supported_extensions": [".txt", ".md"],  # 支持的文件扩展名
        "exclude_patterns": [".bak"]         # 排除的文件模式
    }
}
```

### 配置使用示例

```python
# 自定义配置
custom_config = {
    "text_splitter": {
        "chunk_size": 1024,
        "split_method": "semantic"
    },
    "storage": {
        "enable_compression": True
    },
    "processing": {
        "supported_extensions": [".txt", ".md", ".rst"]
    }
}

framework = XFramework_PT(
    input_file="corpus/",
    config=custom_config
)
```

## 核心方法

### 处理流程方法

#### prepare()
准备框架组件。

```python
def prepare(self) -> 'XFramework_PT':
    """
    准备框架执行。
    
    初始化所有必需的组件：
    - LLM清洗器
    - 清洗管道
    - 文本分割器
    - 限制器（如果设置了limit）
    
    Returns:
        Self（支持方法链）
    
    Raises:
        ValueError: 如果必需组件初始化失败
    """
```

#### run()
执行完整的处理管道。

```python
def run(self) -> Dict[str, Any]:
    """
    执行预训练数据生成流程。
    
    智能状态管理：
    - INITIALIZED 状态：自动调用 prepare() 然后执行
    - CONFIGURED 状态：直接执行，无需重复准备
    - 其他状态：抛出 ValueError
    
    处理步骤：
    1. 数据限制（如果配置）
    2. LLM文本清洗
    3. 多阶段清理管道
    4. 智能文本分割
    
    Returns:
        包含处理结果的字典：
        {
            "output_path": str,              # 输出路径
            "final_output_key": str,         # 最终输出键
            "token_usage": dict,             # 令牌使用统计
            "storage_stats": dict,           # 存储统计信息
            "pipeline_outputs": dict         # 各步骤输出
        }
    
    Raises:
        FileNotFoundError: 输入文件不存在
        ValueError: 输入文件格式不正确或状态无效
    """
```

### 信息获取方法

#### get_desc()
获取框架描述。

```python
def get_desc(self, lang: str = "zh") -> str:
    """
    获取框架描述信息。
    
    Args:
        lang: 语言代码（"zh" 或 "en"）
    
    Returns:
        框架描述字符串
    """
```

#### get_pipeline_info()
获取管道详细信息。

```python
def get_pipeline_info(self) -> Dict[str, Any]:
    """
    获取管道详细信息。
    
    Returns:
        包含以下信息的字典：
        {
            "framework_type": str,           # 框架类型
            "version": str,                  # 版本号
            "is_raw_corpus": bool,           # 是否为原始语料
            "preprocessed_file": str,        # 预处理文件路径
            "components": dict,              # 组件状态
            "configuration": dict,           # 配置信息
            "metrics": dict,                 # 性能指标
            "state": str                     # 当前状态
        }
    """
```

### 向后兼容方法

#### forward()
传统执行方法（已弃用）。

```python
def forward(self) -> Dict[str, Any]:
    """
    传统的执行方法，保持向后兼容性。
    
    自动状态管理：
    - INITIALIZED 状态：调用 prepare() 然后 run()
    - CONFIGURED 状态：直接调用 run()
    - 其他状态：抛出 ValueError
    
    注意：此方法已弃用，建议使用 run() 方法获得更好的
          状态管理和更清晰的语义。
    
    Returns:
        管道执行结果
    """
```

## 使用示例

### 基本使用（推荐）

```python
from xpertcorpus.modules.frameworks import XFramework_PT

# 最简单的使用方式 - 自动状态管理
framework = XFramework_PT(
    input_file="./corpus_directory",
    output_dir="./output",
    max_workers=2
)

# 一键执行 - 自动准备和运行
results = framework.run()  # 自动调用 prepare() 然后执行

print(f"处理完成！输出路径: {results['output_path']}")
```

### 手动控制（可选）

```python
from xpertcorpus.modules.frameworks import XFramework_PT

# 手动控制生命周期
framework = XFramework_PT(
    input_file="./corpus_directory",
    output_dir="./output",
    max_workers=2
)

# 手动准备组件
framework.prepare()

# 执行处理管道
results = framework.run()

print(f"处理完成！输出路径: {results['output_path']}")
```

### 高级配置使用

```python
# 详细配置
config = {
    "text_splitter": {
        "chunk_size": 2048,
        "chunk_overlap": 512,
        "split_method": "semantic",
        "min_tokens_per_chunk": 50
    },
    "storage": {
        "enable_compression": True,
        "validate_on_write": True
    },
    "processing": {
        "supported_extensions": [".txt", ".md", ".rst", ".doc"],
        "exclude_patterns": [".bak", ".tmp", ".cache"]
    }
}

framework = XFramework_PT(
    input_file="large_corpus/",
    output_dir="./processed_output",
    max_workers=8,
    limit=10000,  # 处理前10000个文件
    config=config
)

# 添加钩子监控进度
def progress_hook(framework):
    metrics = framework.get_metrics()
    print(f"已处理: {metrics['files_processed']} 文件")

framework.add_hook("after_run", progress_hook)

# 执行处理
results = framework.run()
```

### 错误处理和恢复

```python
import os
from xpertcorpus.modules.frameworks import XFramework_PT

def safe_process_corpus(input_path, output_path):
    """安全处理语料的封装函数"""
    framework = XFramework_PT(
        input_file=input_path,
        output_dir=output_path,
        max_workers=4
    )
    
    try:
        # 检查输入
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入路径不存在: {input_path}")
        
        # 准备框架
        framework.prepare()
        
        # 执行处理
        results = framework.run()
        
        # 验证结果
        if results.get("final_output_key"):
            print("✅ 处理成功完成")
            return results
        else:
            print("⚠️ 处理完成但无输出")
            return None
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        
        # 获取错误信息
        error_info = framework.get_info()
        print(f"错误详情: {error_info}")
        
        # 获取已处理的部分
        metrics = framework.get_metrics()
        if metrics['files_processed'] > 0:
            print(f"已处理文件: {metrics['files_processed']}")
            print(f"输出目录: {framework.output_dir}")
        
        return None

# 使用示例
results = safe_process_corpus("./corpus", "./output")
```

### 批处理模式

```python
import glob
from pathlib import Path

def batch_process_directories(corpus_dirs, output_base):
    """批量处理多个语料目录"""
    results = []
    
    for corpus_dir in corpus_dirs:
        corpus_name = Path(corpus_dir).name
        output_dir = os.path.join(output_base, f"processed_{corpus_name}")
        
        print(f"处理语料: {corpus_dir} -> {output_dir}")
        
        framework = XFramework_PT(
            input_file=corpus_dir,
            output_dir=output_dir,
            max_workers=2,
            config={
                "storage": {"enable_compression": True},
                "processing": {"supported_extensions": [".txt", ".md"]}
            }
        )
        
        try:
            framework.prepare()
            result = framework.run()
            results.append({
                "corpus": corpus_dir,
                "output": output_dir,
                "success": True,
                "metrics": framework.get_metrics(),
                "result": result
            })
            print(f"✅ {corpus_name} 处理完成")
            
        except Exception as e:
            results.append({
                "corpus": corpus_dir,
                "output": output_dir,
                "success": False,
                "error": str(e)
            })
            print(f"❌ {corpus_name} 处理失败: {e}")
    
    return results

# 批量处理示例
corpus_directories = glob.glob("./data/corpus_*")
batch_results = batch_process_directories(corpus_directories, "./batch_output")

# 统计结果
successful = sum(1 for r in batch_results if r["success"])
print(f"批处理完成: {successful}/{len(batch_results)} 成功")
```

## 性能优化

### 多线程配置

```python
# CPU密集型任务优化
import multiprocessing

cpu_count = multiprocessing.cpu_count()
framework = XFramework_PT(
    input_file="large_corpus/",
    max_workers=cpu_count - 1,  # 保留一个核心给系统
    config={
        "processing": {"batch_size": 100},
        "storage": {"enable_compression": True}
    }
)
```

### 内存优化

```python
# 大文件处理优化
config = {
    "text_splitter": {
        "chunk_size": 512,  # 较小的块大小
        "chunk_overlap": 100
    },
    "storage": {
        "enable_compression": True,  # 启用压缩减少磁盘占用
        "validate_on_write": False   # 跳过验证提升速度
    }
}

framework = XFramework_PT(
    input_file="very_large_corpus/",
    config=config
)
results = framework.run()  # 一键执行
```

## 最佳实践

### 1. 状态管理最佳实践

```python
# ✅ 推荐：简单直接的使用方式
framework = XFramework_PT(input_file="data.jsonl")
results = framework.run()  # 自动处理状态

# ✅ 推荐：监控状态变化
framework = XFramework_PT(input_file="data.jsonl")
print(f"初始状态: {framework.get_state()}")  # INITIALIZED
results = framework.run()  # 自动 prepare() → CONFIGURED → RUNNING → COMPLETED
print(f"最终状态: {framework.get_state()}")  # COMPLETED

# ❌ 不推荐：手动管理简单情况
framework = XFramework_PT(input_file="data.jsonl")
framework.prepare()  # 对于简单使用是多余的
results = framework.run()

# ✅ 推荐：错误处理和状态重置
try:
    results = framework.run()
except Exception as e:
    print(f"执行失败: {e}")
    framework.reset()  # 重置到 INITIALIZED 状态
    # 可以重新尝试或修改配置
```

### 2. 输入数据准备

```python
# 检查输入数据质量
def validate_input_corpus(corpus_path):
    """验证输入语料的质量"""
    if os.path.isdir(corpus_path):
        # 检查文件数量
        file_count = len([f for f in os.listdir(corpus_path) 
                         if f.endswith(('.txt', '.md'))])
        print(f"发现 {file_count} 个文本文件")
        
        if file_count == 0:
            raise ValueError("语料目录中没有找到文本文件")
    
    elif os.path.isfile(corpus_path):
        # 检查文件大小
        file_size = os.path.getsize(corpus_path)
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        if file_size == 0:
            raise ValueError("输入文件为空")
    
    else:
        raise FileNotFoundError(f"输入路径不存在: {corpus_path}")

# 使用前验证
validate_input_corpus("./corpus")
```

### 2. 配置调优

```python
# 根据数据特征调整配置
def create_optimized_config(corpus_size, file_count):
    """根据语料规模创建优化配置"""
    config = {
        "text_splitter": {
            "chunk_size": 1024 if corpus_size > 1000000 else 512,
            "split_method": "semantic" if file_count < 1000 else "markdown"
        },
        "storage": {
            "enable_compression": corpus_size > 100000,
            "validate_on_write": file_count < 10000
        }
    }
    return config
```

### 3. 监控和日志

```python
# 添加详细监控
def add_monitoring_hooks(framework):
    """添加监控钩子"""
    
    def on_start(fw):
        print(f"🚀 开始处理: {fw.input_file}")
        
    def on_progress(fw):
        metrics = fw.get_metrics()
        print(f"📊 进度更新: {metrics}")
        
    def on_complete(fw):
        metrics = fw.get_metrics()
        print(f"✅ 处理完成，耗时: {metrics['total_processing_time']:.2f}s")
        
    def on_error(fw, error):
        print(f"❌ 处理出错: {error}")
        
    framework.add_hook("before_run", on_start)
    framework.add_hook("after_run", on_complete)
    framework.add_hook("on_error", on_error)

# 使用监控
framework = XFramework_PT(input_file="corpus/")
add_monitoring_hooks(framework)
```

## 故障排除

### 常见问题

#### 1. 内存不足
```python
# 解决方案：减少批处理大小和块大小
config = {
    "text_splitter": {"chunk_size": 256},
    "processing": {"batch_size": 50}
}
```

#### 2. 处理速度慢
```python
# 解决方案：增加线程数，禁用验证
framework = XFramework_PT(
    input_file="corpus/",
    max_workers=8,
    config={"storage": {"validate_on_write": False}}
)
```

#### 3. 输出文件为空
```python
# 检查输入数据格式
framework.get_pipeline_info()  # 查看处理状态
```

---

**版本**: v1.0.0  
**最后更新**: 2025-08-13  
**兼容性**: Python 3.10+ 