# 注册系统 (xregistry)

`xpertcorpus.modules.others.xregistry` 模块提供组件注册和动态加载管理功能，支持高性能缓存、线程安全操作和懒加载机制。

## 模块概述

注册系统是 XpertCorpus 框架的核心基础设施，负责：
- 动态组件注册和管理
- 高性能缓存系统（TTL支持）
- 线程安全的组件访问
- 懒加载和按需导入
- 组件元数据和统计信息

## 核心类

### Registry (组件注册器)

主要的组件注册和管理类，提供线程安全的组件存储和检索功能。

#### 构造函数

```python
def __init__(
    self,
    name: str = "default",
    enable_cache: bool = True,
    cache_ttl: float = 3600.0,  # 1小时
    lazy_loading: bool = True
)
```

**参数：**
- `name`: 注册器名称
- `enable_cache`: 是否启用缓存
- `cache_ttl`: 缓存生存时间（秒）
- `lazy_loading`: 是否启用懒加载

#### 核心方法

##### register()

注册组件到注册器中。

```python
def register(
    self,
    name: str,
    obj: Any,
    override: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> bool
```

**参数：**
- `name`: 组件名称（唯一标识符）
- `obj`: 要注册的组件对象
- `override`: 是否允许覆盖现有组件
- `metadata`: 组件元数据

**返回：** 注册是否成功

**使用示例：**
```python
from xpertcorpus.modules.others.xregistry import Registry

registry = Registry(name="operators")

# 注册组件
success = registry.register(
    name="text_cleaner",
    obj=TextCleanerClass,
    metadata={"version": "1.0", "author": "team"}
)

# 覆盖注册
success = registry.register(
    name="text_cleaner",
    obj=NewTextCleanerClass,
    override=True
)
```

##### get()

获取已注册的组件。

```python
def get(
    self,
    name: str,
    default: Any = None,
    **kwargs
) -> Any
```

**参数：**
- `name`: 组件名称
- `default`: 默认返回值（如果未找到）
- `**kwargs`: 传递给懒加载的参数

**返回：** 组件对象或默认值

**使用示例：**
```python
# 获取组件
text_cleaner = registry.get("text_cleaner")

# 使用默认值
unknown_component = registry.get("unknown", default=None)

# 懒加载参数
component = registry.get("lazy_component", param1="value1")
```

##### unregister()

取消注册组件。

```python
def unregister(self, name: str) -> bool
```

**使用示例：**
```python
success = registry.unregister("old_component")
```

##### keys(), values(), items()

获取注册器内容的视图。

```python
def keys(self) -> List[str]
def values(self) -> List[Any]
def items(self) -> List[Tuple[str, Any]]
```

**使用示例：**
```python
# 列出所有组件名称
component_names = registry.keys()

# 获取所有组件对象
components = registry.values()

# 获取名称-对象对
items = registry.items()
```

##### get_metadata()

获取组件的元数据信息。

```python
def get_metadata(self, name: str) -> Optional[Dict[str, Any]]
```

**使用示例：**
```python
metadata = registry.get_metadata("text_cleaner")
print(f"版本: {metadata['version']}")
print(f"作者: {metadata['author']}")
```

##### get_stats()

获取注册器统计信息。

```python
def get_stats(self) -> Dict[str, Any]
```

**返回信息：**
- 注册组件数量
- 缓存命中率
- 内存使用情况
- 访问统计

**使用示例：**
```python
stats = registry.get_stats()
print(f"组件数量: {stats['component_count']}")
print(f"缓存命中率: {stats['cache_hit_rate']:.2%}")
```

##### cleanup()

清理过期缓存和无效组件。

```python
def cleanup(self) -> Dict[str, Any]
```

**使用示例：**
```python
cleanup_result = registry.cleanup()
print(f"清理组件数: {cleanup_result['cleaned_count']}")
```

### RegistryCache (注册缓存)

高性能的TTL缓存实现，支持线程安全操作。

#### 构造函数

```python
def __init__(self, ttl: float = 3600.0)
```

**参数：**
- `ttl`: 缓存生存时间（秒）

#### 主要方法

```python
def get(self, key: str) -> Any
def set(self, key: str, value: Any) -> None
def delete(self, key: str) -> bool
def clear(self) -> None
def size(self) -> int
def is_expired(self, key: str) -> bool
```

**使用示例：**
```python
cache = RegistryCache(ttl=1800)  # 30分钟TTL

# 缓存操作
cache.set("key1", "value1")
value = cache.get("key1")
cache.delete("key1")
```

### LazyLoader (懒加载器)

实现按需加载组件的懒加载机制。

#### 构造函数

```python
def __init__(
    self,
    module_path: str,
    class_name: str,
    cache_enabled: bool = True
)
```

**参数：**
- `module_path`: 模块路径
- `class_name`: 类名
- `cache_enabled`: 是否启用缓存

#### 主要方法

##### load()

加载并返回组件实例。

```python
def load(self, *args, **kwargs) -> Any
```

**使用示例：**
```python
# 创建懒加载器
loader = LazyLoader(
    module_path="xpertcorpus.operators.xllmcleaner",
    class_name="XLlmCleaner"
)

# 懒加载组件
cleaner = loader.load(config={"model": "gpt-3.5"})
```

## 全局注册器

### OPERATOR_REGISTRY

预定义的全局算子注册器，用于管理所有操作算子。

```python
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY

# 注册算子
OPERATOR_REGISTRY.register("my_operator", MyOperatorClass)

# 获取算子
operator = OPERATOR_REGISTRY.get("my_operator")
```

## 工具函数

### create_registry()

创建新的注册器实例。

```python
def create_registry(
    name: str,
    **kwargs
) -> Registry
```

**使用示例：**
```python
from xpertcorpus.modules.others.xregistry import create_registry

custom_registry = create_registry(
    name="custom_components",
    enable_cache=True,
    cache_ttl=7200  # 2小时
)
```

### get_global_registry_stats()

获取所有注册器的全局统计信息。

```python
def get_global_registry_stats() -> Dict[str, Dict[str, Any]]
```

**使用示例：**
```python
global_stats = get_global_registry_stats()
for registry_name, stats in global_stats.items():
    print(f"{registry_name}: {stats['component_count']} 个组件")
```

## 使用模式

### 基础注册和获取

```python
from xpertcorpus.modules.others.xregistry import Registry

# 创建注册器
registry = Registry(name="my_components")

# 注册组件
class MyComponent:
    def process(self, data):
        return f"处理: {data}"

registry.register("my_component", MyComponent)

# 获取并使用组件
component_class = registry.get("my_component")
component = component_class()
result = component.process("test data")
```

### 懒加载模式

```python
# 注册懒加载组件
lazy_loader = LazyLoader(
    module_path="my_module.components",
    class_name="HeavyComponent"
)

registry.register("heavy_component", lazy_loader)

# 首次访问时才加载
heavy_component = registry.get("heavy_component")
instance = heavy_component.load(config={"setting": "value"})
```

### 元数据管理

```python
# 注册时添加元数据
registry.register(
    name="advanced_component",
    obj=AdvancedComponentClass,
    metadata={
        "version": "2.1.0",
        "author": "development_team",
        "description": "高级数据处理组件",
        "dependencies": ["numpy", "pandas"],
        "performance": {"cpu": "medium", "memory": "high"}
    }
)

# 查询元数据
metadata = registry.get_metadata("advanced_component")
if metadata["performance"]["memory"] == "high":
    print("警告: 该组件内存使用较高")
```

### 缓存优化

```python
# 高性能注册器配置
high_perf_registry = Registry(
    name="high_performance",
    enable_cache=True,
    cache_ttl=7200,  # 2小时缓存
    lazy_loading=True
)

# 批量注册
components = {
    "tokenizer": TokenizerClass,
    "embedder": EmbedderClass,
    "classifier": ClassifierClass
}

for name, component_class in components.items():
    high_perf_registry.register(name, component_class)

# 高频访问组件会被缓存
tokenizer = high_perf_registry.get("tokenizer")
```

### 动态组件管理

```python
# 运行时注册新组件
def register_plugin(plugin_name, plugin_class):
    success = registry.register(
        name=plugin_name,
        obj=plugin_class,
        override=True,  # 允许热更新
        metadata={"type": "plugin", "loaded_at": time.time()}
    )
    return success

# 动态卸载组件
def unload_plugin(plugin_name):
    return registry.unregister(plugin_name)

# 列出所有插件
def list_plugins():
    plugins = []
    for name in registry.keys():
        metadata = registry.get_metadata(name)
        if metadata and metadata.get("type") == "plugin":
            plugins.append(name)
    return plugins
```

## 性能优化

### 缓存策略

```python
# 针对不同使用场景的缓存配置

# 短期高频访问
short_term_registry = Registry(
    name="short_term",
    cache_ttl=300,  # 5分钟
    enable_cache=True
)

# 长期稳定组件
long_term_registry = Registry(
    name="long_term", 
    cache_ttl=86400,  # 24小时
    enable_cache=True
)

# 实时组件（无缓存）
realtime_registry = Registry(
    name="realtime",
    enable_cache=False
)
```

### 并发安全

```python
import threading
from concurrent.futures import ThreadPoolExecutor

# 线程安全的并发访问
def worker_function(worker_id):
    for i in range(100):
        # 多线程安全访问
        component = registry.get(f"worker_component_{worker_id}")
        result = component.process(f"data_{i}")
        
# 并发测试
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(worker_function, i) for i in range(10)]
    for future in futures:
        future.result()
```

### 内存管理

```python
# 定期清理过期缓存
import schedule

def cleanup_registries():
    for registry_name, registry in get_all_registries().items():
        cleanup_result = registry.cleanup()
        print(f"清理 {registry_name}: {cleanup_result}")

# 每小时清理一次
schedule.every().hour.do(cleanup_registries)
```

## 错误处理

### 异常处理

注册系统集成了 `xerror_handler`，提供robust的错误处理：

```python
from xpertcorpus.modules.others.xregistry import Registry

registry = Registry()

try:
    # 可能失败的组件获取
    component = registry.get("nonexistent_component")
except ComponentNotFoundError:
    print("组件未找到")
except Exception as e:
    print(f"注册器错误: {e}")
```

### 容错机制

```python
# 设置默认组件
default_component = DefaultProcessorClass()

# 容错获取
def safe_get_component(name):
    try:
        return registry.get(name)
    except Exception:
        # 返回默认组件
        return default_component

# 使用容错组件
processor = safe_get_component("risky_component")
```

## 最佳实践

### 1. 命名规范

```python
# 使用清晰的命名规范
registry.register("text_cleaner_v2", TextCleanerV2)
registry.register("llm_processor_openai", OpenAIProcessor)
registry.register("data_validator_strict", StrictValidator)
```

### 2. 版本管理

```python
# 版本化组件注册
def register_versioned_component(base_name, component_class, version):
    name = f"{base_name}_v{version}"
    metadata = {"version": version, "base_name": base_name}
    registry.register(name, component_class, metadata=metadata)

# 获取最新版本
def get_latest_component(base_name):
    versions = []
    for name in registry.keys():
        metadata = registry.get_metadata(name)
        if metadata and metadata.get("base_name") == base_name:
            versions.append((metadata["version"], name))
    
    if versions:
        latest_version = max(versions, key=lambda x: x[0])
        return registry.get(latest_version[1])
    return None
```

### 3. 配置驱动注册

```python
# 基于配置文件的组件注册
def register_from_config(config_file):
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    for component_config in config["components"]:
        if component_config.get("lazy_load", False):
            loader = LazyLoader(
                module_path=component_config["module"],
                class_name=component_config["class"]
            )
            registry.register(component_config["name"], loader)
        else:
            # 直接导入注册
            module = importlib.import_module(component_config["module"])
            component_class = getattr(module, component_config["class"])
            registry.register(component_config["name"], component_class)
```

### 4. 监控和调试

```python
# 注册器状态监控
def monitor_registry(registry):
    stats = registry.get_stats()
    
    print(f"组件数量: {stats['component_count']}")
    print(f"缓存大小: {stats['cache_size']}")
    print(f"命中率: {stats['cache_hit_rate']:.2%}")
    
    # 检查内存使用
    if stats['memory_usage'] > 100 * 1024 * 1024:  # 100MB
        print("警告: 注册器内存使用过高")
        
# 调试组件访问
def debug_component_access(name):
    component = registry.get(name)
    metadata = registry.get_metadata(name)
    
    print(f"组件: {name}")
    print(f"类型: {type(component)}")
    print(f"元数据: {metadata}")
```

## 注意事项

### 1. 线程安全

- `Registry` 和 `RegistryCache` 都是线程安全的
- 可以在多线程环境中并发访问
- 避免在组件初始化时进行复杂操作

### 2. 内存管理

- 合理设置缓存TTL，避免内存泄漏
- 定期调用 `cleanup()` 清理过期缓存
- 对于大型组件，考虑使用懒加载

### 3. 性能考虑

- 缓存可以显著提升组件获取速度
- 懒加载适合初始化成本高的组件
- 避免过度使用元数据存储

### 4. 错误处理

- 注册时验证组件有效性
- 为关键组件提供fallback机制
- 记录组件访问日志便于调试

---

**更多信息：**
- [错误处理 (xerror_handler)](../utils/xerror_handler.md)
- [操作符基类 (xoperator)](xoperator.md)
- [框架系统 (xframework)](xframework.md) 