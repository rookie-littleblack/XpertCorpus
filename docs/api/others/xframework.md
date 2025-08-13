# Framework 基础框架系统 (xframework)

`xpertcorpus.modules.others.xframework` 模块提供了 XpertCorpus 框架的抽象基类和框架管理功能。

## 概述

Framework 基础框架系统是 XpertCorpus 的核心架构组件，为所有数据处理框架提供了统一的抽象接口和生命周期管理。通过定义标准的框架生命周期、配置管理、组件管理和错误处理机制，确保了框架的一致性和可扩展性。

### 核心特性

- **8种状态的生命周期管理**：从初始化到完成的完整状态追踪
- **配置驱动的组件管理**：灵活的组件装配和配置系统
- **错误处理和性能监控**：集成的错误处理和性能统计
- **钩子系统和事件机制**：可扩展的事件处理架构

## 核心组件

### FrameworkState

框架生命周期状态枚举。

```python
from xpertcorpus.modules.others.xframework import FrameworkState

class FrameworkState(Enum):
    INITIALIZED = "INITIALIZED"    # 已初始化
    CONFIGURED = "CONFIGURED"      # 已配置
    PREPARING = "PREPARING"        # 准备中
    RUNNING = "RUNNING"           # 运行中
    COMPLETED = "COMPLETED"       # 已完成
    FAILED = "FAILED"             # 失败
    STOPPED = "STOPPED"           # 已停止
    PAUSED = "PAUSED"             # 已暂停
```

**使用示例：**
```python
# 检查框架状态
if framework.get_state() == FrameworkState.RUNNING:
    print("Framework is currently running")

# 状态转换
framework.pause()  # RUNNING -> PAUSED
framework.resume() # PAUSED -> RUNNING
```

### FrameworkType

框架类型枚举。

```python
from xpertcorpus.modules.others.xframework import FrameworkType

class FrameworkType(Enum):
    PRETRAINING = "PRETRAINING"   # 预训练框架
    SFT = "SFT"                   # 监督微调框架
    COT = "COT"                   # 思维链框架
    MULTIMODAL = "MULTIMODAL"     # 多模态框架
    CUSTOM = "CUSTOM"             # 自定义框架
```

**使用示例：**
```python
class MyCustomFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
```

## 核心抽象类

### FrameworkABC

框架抽象基类，定义了所有框架必须实现的核心接口。

```python
class FrameworkABC(ABC):
    """
    框架抽象基类，提供标准化的框架接口和生命周期管理。
    
    所有数据处理框架都应该继承此类并实现抽象方法。
    """
    
    # 框架元数据
    FRAMEWORK_TYPE: FrameworkType = FrameworkType.CUSTOM
    VERSION: str = "1.0.0"
    REQUIRED_OPERATORS: List[str] = []
    REQUIRED_PIPELINES: List[str] = []
    
    def __init__(self, 
                 input_file: str,
                 output_dir: str = "./output",
                 max_workers: int = 1,
                 limit: int = 0,
                 config: Optional[Dict[str, Any]] = None):
        """
        初始化框架。
        
        Args:
            input_file: 输入文件或目录路径
            output_dir: 输出目录路径
            max_workers: 工作线程数
            limit: 处理限制（0表示无限制）
            config: 可选配置字典
        """
```

**核心方法：**

#### 抽象方法（必须实现）

```python
@abstractmethod
def _on_init(self) -> None:
    """框架特定初始化逻辑"""
    pass

@abstractmethod
def _prepare_components(self) -> None:
    """准备框架组件（操作符、管道等）"""
    pass

@abstractmethod
def _execute_pipeline(self) -> Dict[str, Any]:
    """执行主要处理管道"""
    pass

@abstractmethod
def get_desc(self, lang: str = "zh") -> str:
    """获取框架描述"""
    pass
```

#### 配置管理

```python
def configure(self, config: Dict[str, Any]) -> 'FrameworkABC':
    """配置框架设置"""
    
def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
    """获取配置值"""
    
def set_config(self, key: str, value: Any) -> 'FrameworkABC':
    """设置配置值"""
```

#### 组件管理

```python
def add_operator(self, name: str, operator: OperatorABC) -> 'FrameworkABC':
    """添加操作符"""
    
def get_operator(self, name: str) -> Optional[OperatorABC]:
    """获取操作符"""
    
def add_pipeline(self, name: str, pipeline: Any) -> 'FrameworkABC':
    """添加管道"""
    
def get_pipeline(self, name: str) -> Optional[Any]:
    """获取管道"""
```

#### 生命周期控制

```python
def prepare(self) -> 'FrameworkABC':
    """准备框架执行"""
    
def run(self) -> Dict[str, Any]:
    """执行框架管道"""
    
def pause(self) -> 'FrameworkABC':
    """暂停执行"""
    
def resume(self) -> 'FrameworkABC':
    """恢复执行"""
    
def stop(self) -> 'FrameworkABC':
    """停止执行"""
    
def reset(self) -> 'FrameworkABC':
    """重置框架状态"""
```

#### 监控和信息

```python
def get_state(self) -> FrameworkState:
    """获取当前状态"""
    
def get_metadata(self) -> Dict[str, Any]:
    """获取框架元数据"""
    
def get_metrics(self) -> Dict[str, Any]:
    """获取性能指标"""
    
def get_info(self) -> Dict[str, Any]:
    """获取完整框架信息"""
    
def get_progress(self) -> Dict[str, Any]:
    """获取当前进度信息"""
```

### FrameworkManager

框架管理器，提供框架注册和实例化功能。

```python
class FrameworkManager:
    """框架注册和生命周期管理器"""
    
    @classmethod
    def register_framework(cls, name: str, framework_class: Type[FrameworkABC]) -> None:
        """注册框架类"""
    
    @classmethod
    def get_framework(cls, name: str) -> Optional[Type[FrameworkABC]]:
        """获取框架类"""
    
    @classmethod
    def list_frameworks(cls) -> List[str]:
        """列出所有注册的框架"""
    
    @classmethod
    def create_framework(cls, 
                        name: str,
                        input_file: str,
                        output_dir: str = "./output",
                        max_workers: int = 1,
                        limit: int = 0,
                        config: Optional[Dict[str, Any]] = None) -> FrameworkABC:
        """创建框架实例"""
```

**使用示例：**
```python
from xpertcorpus.modules.others.xframework import FrameworkManager

# 注册框架
FrameworkManager.register_framework("my_framework", MyFramework)

# 创建框架实例
framework = FrameworkManager.create_framework(
    "my_framework",
    input_file="data.jsonl",
    output_dir="./output",
    config={"batch_size": 32}
)

# 列出所有框架
available_frameworks = FrameworkManager.list_frameworks()
```

## 装饰器函数

### register_framework

框架注册装饰器。

```python
def register_framework(name: str):
    """
    框架注册装饰器。
    
    Args:
        name: 框架注册名称
    
    Returns:
        装饰器函数
    """
    def decorator(framework_class: Type[FrameworkABC]):
        FrameworkManager.register_framework(name, framework_class)
        return framework_class
    return decorator
```

**使用示例：**
```python
from xpertcorpus.modules.others.xframework import FrameworkABC, FrameworkType, register_framework

@register_framework("pretraining")
class PretrainingFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.PRETRAINING
    VERSION = "1.0.0"
    
    def _on_init(self):
        # 预训练框架特定初始化
        pass
```

## 使用示例

### 基础框架开发

```python
from xpertcorpus.modules.others.xframework import (
    FrameworkABC, 
    FrameworkType, 
    FrameworkState,
    register_framework
)
from xpertcorpus.modules.others.xoperator import OperatorABC

@register_framework("text_processing")
class TextProcessingFramework(FrameworkABC):
    """文本处理框架示例"""
    
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
    REQUIRED_OPERATORS = ["cleaner", "splitter"]
    
    def _on_init(self):
        """框架初始化"""
        self.processed_count = 0
        
    def _prepare_components(self):
        """准备组件"""
        # 添加必需的操作符
        from xpertcorpus.modules.operators import XLlmCleaner, XPlitter
        
        self.add_operator("cleaner", XLlmCleaner())
        self.add_operator("splitter", XPlitter())
        
    def _execute_pipeline(self) -> Dict[str, Any]:
        """执行处理管道"""
        try:
            # 步骤1：清洗数据
            cleaner = self.get_operator("cleaner")
            cleaned_data = cleaner.run(self.storage)
            
            # 步骤2：分割文本
            splitter = self.get_operator("splitter")
            split_data = splitter.run(self.storage.step())
            
            # 更新指标
            self.metrics["files_processed"] = 1
            self.metrics["records_processed"] = len(split_data)
            
            return {
                "status": "success",
                "processed_files": 1,
                "output_records": len(split_data)
            }
            
        except Exception as e:
            self.metrics["errors_count"] += 1
            raise
    
    def get_desc(self, lang: str = "zh") -> str:
        """获取框架描述"""
        if lang == "zh":
            return "文本处理框架：支持文本清洗和智能分割"
        return "Text Processing Framework: Supports text cleaning and intelligent splitting"

# 使用框架
framework = TextProcessingFramework(
    input_file="input.jsonl",
    output_dir="./output",
    config={
        "batch_size": 100,
        "enable_compression": True
    }
)

# 准备并运行
results = framework.prepare().run()
print(f"处理完成：{results}")
```

### 高级配置和钩子系统

```python
def before_processing_hook(framework, *args, **kwargs):
    """处理前钩子"""
    print(f"开始处理 {framework.input_file}")

def after_processing_hook(framework, results, *args, **kwargs):
    """处理后钩子"""
    print(f"处理完成，结果：{results}")

def error_handling_hook(framework, error, *args, **kwargs):
    """错误处理钩子"""
    print(f"处理出错：{error}")

# 配置框架
framework = TextProcessingFramework(
    input_file="large_dataset.jsonl",
    output_dir="./output",
    max_workers=4,
    config={
        "batch_size": 1000,
        "enable_compression": True,
        "validate_on_write": True
    }
)

# 添加钩子
framework.add_hook("before_run", before_processing_hook)
framework.add_hook("after_run", after_processing_hook)
framework.add_hook("on_error", error_handling_hook)

# 执行处理
try:
    results = framework.prepare().run()
    
    # 获取详细信息
    print("框架信息：", framework.get_info())
    print("性能指标：", framework.get_metrics())
    print("处理进度：", framework.get_progress())
    
except Exception as e:
    print(f"框架执行失败：{e}")
    print("当前状态：", framework.get_state())
```

### 框架管理器使用

```python
from xpertcorpus.modules.others.xframework import FrameworkManager

# 注册多个框架
@register_framework("data_cleaning")
class DataCleaningFramework(FrameworkABC):
    pass

@register_framework("data_splitting")  
class DataSplittingFramework(FrameworkABC):
    pass

# 列出所有可用框架
available = FrameworkManager.list_frameworks()
print("可用框架：", available)

# 动态创建框架
for framework_name in available:
    framework = FrameworkManager.create_framework(
        framework_name,
        input_file=f"data_{framework_name}.jsonl",
        output_dir=f"./output_{framework_name}"
    )
    print(f"创建了框架：{framework}")
```

## 最佳实践

### 1. 框架设计原则

```python
# ✅ 好的做法：清晰的框架结构
@register_framework("text_analysis")
class TextAnalysisFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.2.0"
    REQUIRED_OPERATORS = ["tokenizer", "analyzer"]
    
    def _on_init(self):
        # 只做框架特定的初始化
        self.analysis_config = self.config.get("analysis", {})
        
    def _prepare_components(self):
        # 明确的组件准备逻辑
        self.add_operator("tokenizer", self._create_tokenizer())
        self.add_operator("analyzer", self._create_analyzer())
        
    def _execute_pipeline(self):
        # 清晰的管道执行流程
        return self._run_analysis_pipeline()

# ❌ 避免：混乱的初始化逻辑
class BadFramework(FrameworkABC):
    def _on_init(self):
        # 不要在初始化中做太多事情
        self._prepare_components()  # 错误：应该在 prepare 阶段
        self._execute_pipeline()    # 错误：应该在 run 阶段
```

### 2. 错误处理最佳实践

```python
class RobustFramework(FrameworkABC):
    def _execute_pipeline(self):
        """robust pipeline with error handling"""
        try:
            results = {}
            
            # 使用 safe_execute 装饰器保护关键操作
            for step_name, operator in self.operators.items():
                try:
                    step_result = operator.run(self.storage.step())
                    results[step_name] = step_result
                    self.metrics["pipeline_steps_completed"] += 1
                    
                except Exception as step_error:
                    # 记录步骤错误但继续执行
                    self.metrics["errors_count"] += 1
                    results[step_name] = {"error": str(step_error)}
                    
            return results
            
        except Exception as e:
            # 全局错误处理
            self.state = FrameworkState.FAILED
            self.metrics["errors_count"] += 1
            raise
```

### 3. 性能优化

```python
class OptimizedFramework(FrameworkABC):
    def _on_init(self):
        # 预分配资源
        self.worker_pool = None
        self.batch_processor = None
        
    def _prepare_components(self):
        # 懒加载昂贵资源
        if self.max_workers > 1:
            from concurrent.futures import ThreadPoolExecutor
            self.worker_pool = ThreadPoolExecutor(max_workers=self.max_workers)
            
    def _execute_pipeline(self):
        """optimized pipeline execution"""
        if self.worker_pool:
            # 并行处理
            return self._parallel_execute()
        else:
            # 单线程处理
            return self._sequential_execute()
            
    def __del__(self):
        # 清理资源
        if self.worker_pool:
            self.worker_pool.shutdown(wait=True)
```

## 注意事项

### 性能考虑

1. **资源管理**：正确管理线程池、文件句柄等资源
2. **内存优化**：大数据处理时考虑流式处理
3. **并发安全**：多线程环境下保证状态一致性

### 错误处理

1. **异常分类**：区分可恢复和不可恢复的错误
2. **状态保护**：异常时正确设置框架状态
3. **资源清理**：异常退出时确保资源释放

### 扩展性

1. **钩子机制**：充分利用钩子系统增强框架功能
2. **配置驱动**：通过配置而非硬编码控制行为
3. **组件化设计**：保持组件间的低耦合

## 相关文档

- [操作符基类 (xoperator)](xoperator.md)
- [注册系统 (xregistry)](xregistry.md)
- [异常处理 (xerror_handler)](../utils/xerror_handler.md)
- [日志系统 (xlogger)](../utils/xlogger.md)

---

[返回 Others 模块首页](README.md) | [返回 API 文档首页](../README.md) 