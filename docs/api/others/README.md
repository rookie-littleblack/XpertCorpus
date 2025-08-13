# Others 模块 API 文档

Others 模块为 XpertCorpus 框架提供核心的抽象基类和基础设施组件。

## 模块列表

### 🏗️ [框架基础系统 (xframework)](xframework.md)
提供框架抽象基类和框架管理功能。

**核心类：**
- `FrameworkABC` - 框架抽象基类
- `FrameworkManager` - 框架管理器
- `FrameworkState` - 框架状态枚举
- `FrameworkType` - 框架类型枚举

**主要功能：**
- 8种状态的生命周期管理
- 配置驱动的组件管理
- 错误处理和性能监控
- 钩子系统和事件机制

### ⚙️ [操作符基类 (xoperator)](xoperator.md)
操作符抽象基类和生命周期管理。

**核心类：**
- `OperatorABC` - 操作符抽象基类
- `OperatorManager` - 操作符管理器
- `OperatorState` - 操作符状态枚举

**主要功能：**
- 生命周期管理和状态追踪
- 配置管理和验证
- 性能监控和钩子系统
- 错误处理和恢复机制

### 📝 [注册系统 (xregistry)](xregistry.md)
组件注册和动态加载管理。

**核心类：**
- `Registry` - 组件注册器
- `LazyLoader` - 懒加载器
- `RegistryCache` - 注册缓存

**主要功能：**
- 带TTL的高性能缓存
- 线程安全的组件管理
- 懒加载和动态导入
- 注册验证和元数据

### 🔧 [其他组件]
- `xlimitor.py` - 限制器组件
- `xapi.py` - API基类
- `xprompts.py` - 提示模板

## 使用模式

### 单独导入
```python
from xpertcorpus.modules.others.xframework import FrameworkABC
from xpertcorpus.modules.others.xoperator import OperatorABC
from xpertcorpus.modules.others.xregistry import Registry
```

### 批量导入
```python
from xpertcorpus.modules.others import (
    FrameworkABC,
    FrameworkManager,
    OperatorABC,
    OperatorManager,
    Registry
)
```

## 依赖关系

```
Others 模块内部依赖：

xframework → xoperator → xregistry  # 框架基类依赖操作符和注册系统
xoperator → xregistry               # 操作符基类依赖注册系统

外部依赖（工具层）：
xframework → xerror_handler → xlogger  # 框架基类依赖错误处理和日志
xoperator → xerror_handler → xlogger   # 操作符基类依赖错误处理和日志
xregistry → xerror_handler → xlogger   # 注册系统依赖错误处理和日志
```

## 最佳实践

### 1. 框架开发
```python
from xpertcorpus.modules.others.xframework import FrameworkABC, FrameworkType, register_framework

@register_framework("my_framework")
class MyFramework(FrameworkABC):
    FRAMEWORK_TYPE = FrameworkType.CUSTOM
    VERSION = "1.0.0"
    
    def _on_init(self):
        # 框架特定初始化
        pass
    
    def _prepare_components(self):
        # 准备组件
        pass
    
    def _execute_pipeline(self):
        # 执行管道
        pass
```

### 2. 操作符开发
```python
from xpertcorpus.modules.others.xoperator import OperatorABC

class MyOperator(OperatorABC):
    def process(self, data):
        # 数据处理逻辑
        return processed_data
```

### 3. 组件注册
```python
from xpertcorpus.modules.others.xregistry import Registry

# 创建注册器
registry = Registry(enable_cache=True, lazy_loading=True)

# 注册组件
registry.register("my_operator", MyOperator)

# 获取组件
operator_class = registry.get("my_operator")
```

## 版本历史

### v0.1.0 (2025-08-13)
- ✨ **新增框架基础系统** (`xframework`)：框架抽象基类和生命周期管理
- 🔧 **优化操作符系统** (`xoperator`)：增加生命周期管理、配置验证、钩子机制等功能
- 🔧 **优化注册系统** (`xregistry`)：增加缓存、懒加载、性能统计等功能
- 📝 **完善文档系统**：新增完整的API文档和使用示例

---

[返回 API 文档首页](../README.md) 