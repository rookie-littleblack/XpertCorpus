# 注册系统 (xregistry)

`xpertcorpus.modules.others.xregistry` 模块提供组件注册和动态加载管理功能。

## 模块概述

注册系统为 XpertCorpus 提供组件的动态注册、缓存和懒加载功能，支持线程安全操作和 TTL 缓存机制。

## 核心组件

### RegistryCache

注册缓存系统，支持 TTL（生存时间）机制。

```python
class RegistryCache:
    def __init__(self, default_ttl: int = 3600):
        """初始化缓存"""
```

#### 主要方法

```python
def get(self, key: str) -> Optional[Any]:
    """获取缓存值（如果未过期）"""
    
def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
    """设置缓存值"""
    
def clear(self) -> None:
    """清空所有缓存"""
    
def cleanup_expired(self) -> int:
    """清理过期缓存项，返回清理数量"""
    
def get_stats(self) -> Dict[str, Any]:
    """获取缓存统计信息"""
```

### Registry

主要的注册器类，支持组件注册、获取和管理。

```python
class Registry:
    def __init__(self, name: str, enable_cache: bool = True, cache_ttl: int = 3600):
        """初始化注册器"""
```

#### 注册和获取方法

```python
def register(self, obj: Optional[Type] = None, name: Optional[str] = None, 
             metadata: Optional[Dict[str, Any]] = None):
    """
    注册组件，支持作为函数调用或装饰器使用。
    """
    
def get(self, name: str) -> Optional[Type]:
    """获取组件（支持懒加载）"""
    
def unregister(self, name: str) -> bool:
    """注销组件"""
```

#### 迭代和信息方法

```python
def keys(self) -> List[str]:
    """获取所有注册的键名"""
    
def values(self) -> List[Type]:
    """获取所有注册的值"""
    
def items(self) -> List[tuple]:
    """获取所有键值对"""
    
def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
    """获取组件元数据"""
    
def get_stats(self) -> Dict[str, Any]:
    """获取注册器统计信息"""
    
def cleanup(self) -> None:
    """清理过期缓存"""
```

### LazyLoader

懒加载模块类，支持按需导入。

```python
class LazyLoader(types.ModuleType):
    def __init__(self, name: str, path: str, import_structure: Dict[str, str]):
        """初始化懒加载器"""
```

#### 主要方法

```python
def __getattr__(self, item: str) -> Type:
    """动态加载并返回属性"""

def get_loaded_classes(self) -> List[str]:
    """获取已加载的类名列表"""
    
def get_available_classes(self) -> List[str]:
    """获取所有可用的类名列表"""
    
def preload_class(self, class_name: str) -> bool:
    """预加载指定类"""
    
def get_stats(self) -> Dict[str, Any]:
    """获取加载统计信息"""

def clear_cache(self) -> None:
    """清空已加载的类缓存"""
```

## 全局注册器

模块提供了一个全局的算子注册器实例：

```python
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY

# OPERATOR_REGISTRY 是一个预配置的 Registry 实例
OPERATOR_REGISTRY = Registry('operator')
```

## 工具函数

```python
def create_registry(name: str, enable_cache: bool = True, cache_ttl: int = 3600) -> Registry:
    """创建新的注册器实例"""
    
def get_global_registry_stats() -> Dict[str, Any]:
    """获取全局注册器统计信息"""
```

## 使用示例

### 基本注册和获取

```python
from xpertcorpus.modules.others.xregistry import Registry

# 创建注册器
registry = Registry(name="my_registry")

# 使用装饰器注册组件
@registry.register
class MyComponent:
    pass

# 使用函数调用注册
class AnotherComponent:
    pass
registry.register(AnotherComponent, name="custom_name")

# 获取组件
ComponentClass = registry.get("MyComponent")
AnotherClass = registry.get("custom_name")
```

### 使用全局算子注册器

```python
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY

@OPERATOR_REGISTRY.register
class MyAwesomeOperator:
    def run(self):
        return "Awesome result"

# 获取算子
OperatorClass = OPERATOR_REGISTRY.get("MyAwesomeOperator")
operator = OperatorClass()
result = operator.run()
```

### 元数据和统计

```python
# 注册时添加元数据
@OPERATOR_REGISTRY.register(metadata={"version": "2.0"})
class AdvancedOperator:
    pass

# 获取元数据
metadata = OPERATOR_REGISTRY.get_metadata("AdvancedOperator")
print(f"Version: {metadata['version']}")

# 获取注册器统计
stats = get_global_registry_stats()
print(f"Total registered operators: {stats['total_registered']}")
```

## 内置特性

### 线程安全
所有注册器操作都是线程安全的，使用内部锁机制保护。

### TTL 缓存
支持组件级别的 TTL 缓存，自动清理过期项。

### 懒加载
`get` 方法在 `operator` 注册表中支持懒加载，当首次请求一个未注册的算子时，会尝试从标准的算子模块路径中动态导入。

### 统计和监控
提供详细的使用统计和性能监控信息。

## 相关文档

- [算子基类 (xoperator)](xoperator.md)
- [框架系统 (xframework)](xframework.md)
- [异常处理 (xerror_handler)](../utils/xerror_handler.md)

---

[返回 Others 模块首页](README.md) | [返回 API 文档首页](../README.md) 