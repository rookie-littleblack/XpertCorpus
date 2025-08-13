# 微操作层 API 文档

## 模块概述

微操作层（Microops）是 XpertCorpus 架构中的最底层模块，提供最细粒度的原子级文本处理操作。这些微操作被设计为高度专一化、可复用的基础构建块，专注于单一的文本处理任务。

## 设计理念

### 原子性原则
- **单一职责**：每个微操作只负责一个特定的文本处理任务
- **最小功能单元**：不可再分的基础操作，确保功能的纯粹性
- **高度专一化**：针对特定文本模式进行优化处理

### 组合性设计
- **无状态操作**：微操作之间相互独立，不依赖外部状态
- **标准接口**：继承 `OperatorABC`，提供统一的调用方式
- **链式组合**：可以被管道层灵活组合成复杂处理流程

### 性能优化
- **高效实现**：使用正则表达式和字符串操作的最佳实践
- **内存友好**：避免创建不必要的中间对象
- **错误容忍**：异常情况下返回原始输入，保证处理链的稳定性

## 现有微操作

### RemoveEmoticonsMicroops
**功能描述**：去除文本中的表情符号（文本符号形式）

**核心特性**：
- 支持超过 5000 种表情符号模式
- 包含各种语言和文化的表情符号
- 基于字典替换的高效处理机制

**注册名称**：`remove_emoticons`

**使用场景**：
- 清理社交媒体文本
- 标准化聊天记录
- 准备机器学习训练数据

### RemoveEmojiMicroops
**功能描述**：去除文本中的 Unicode 表情符号（图形符号）

**核心特性**：
- 基于 Unicode 范围的正则表达式匹配
- 涵盖所有主要表情符号类别
- 高性能的模式匹配处理

**Unicode 覆盖范围**：
- 表情符号：`\U0001F600-\U0001F64F`
- 杂项符号：`\U0001F300-\U0001F5FF`
- 交通地图符号：`\U0001F680-\U0001F6FF`
- 国旗符号：`\U0001F1E0-\U0001F1FF`
- 装饰符号：`\U00002702-\U000027B0`
- 封闭字符：`\U000024C2-\U0001F251`

**注册名称**：`remove_emoji`

**使用场景**：
- 文本标准化处理
- 移除视觉干扰元素
- 改善文本分析准确性

### RemoveExtraSpacesMicroops
**功能描述**：智能清理文本中的多余空格和换行符

**核心特性**：
- **代码检测机制**：自动识别代码块并保护其格式
- **智能空格处理**：区分代码和自然语言文本
- **多层次清理**：处理制表符、换行符、行尾空格等

**处理策略**：
1. **代码保护**：检测并保护各种代码格式
   - 围栏式代码块（```、~~~）
   - 缩进代码块（4+ 空格开头）
   - 行内代码（反引号包围）
   - HTML pre/code 标签
   - 编程语言特征检测

2. **文本清理**：
   - 移除 `\r` 字符
   - 压缩连续换行符（3+ → 2）
   - 清理多余空格（保留合理缩进）
   - 标准化制表符和空格混合
   - 移除行尾空格

3. **智能判断**：
   - 基于代码特征的启发式检测
   - 30% 阈值判断代码可能性
   - 保护重要的格式化信息

**注册名称**：`remove_extra_spaces`

**使用场景**：
- 文档格式标准化
- 减少存储空间占用
- 改善文本处理效果
- 保护代码块格式完整性

## 微操作开发指南

### 基础结构

每个微操作都应该遵循以下基本结构：

```python
from xpertcorpus.utils import xlogger
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator

@register_operator("your_microop_name")
class YourMicroops(OperatorABC):
    def __init__(self):
        xlogger.info(f"Initializing {self.__class__.__name__} ...")
        # 初始化必要的模式、配置等
    
    @staticmethod
    def get_desc(lang: str = "zh"):
        return "中文描述" if lang == "zh" else "English description"
    
    def run(self, input_string: str) -> str:
        if not input_string:
            return input_string
        
        try:
            # 具体的处理逻辑
            processed_text = self._process(input_string)
            return processed_text
        except Exception as e:
            xlogger.error(f"Error in {self.__class__.__name__}: {e}")
            return input_string
    
    def _process(self, text: str) -> str:
        # 实际的处理实现
        pass
```

### 开发最佳实践

#### 1. 错误处理
- **容错设计**：异常情况下返回原始输入
- **日志记录**：记录错误信息以便调试
- **输入验证**：检查输入的有效性

#### 2. 性能优化
- **编译正则表达式**：在 `__init__` 中预编译复杂模式
- **避免重复计算**：缓存计算结果
- **内存管理**：及时释放大型临时对象

#### 3. 功能设计
- **单一职责**：确保每个微操作只做一件事
- **幂等性**：多次应用应该产生相同结果
- **可组合性**：与其他微操作良好配合

#### 4. 测试与验证
- **边界情况**：测试空字符串、特殊字符等
- **性能测试**：验证大文本处理能力
- **组合测试**：确保与其他微操作的兼容性

### 配置管理

微操作支持通过配置文件进行参数调整：

```python
# 在微操作中接受配置参数
def __init__(self, config: Optional[Dict[str, Any]] = None):
    self.config = config or {}
    self.enabled = self.config.get('enabled', True)
    self.strict_mode = self.config.get('strict_mode', False)
```

### 注册与发现

使用统一的注册机制：

```python
# 注册微操作
@register_operator("custom_microop")
class CustomMicroops(OperatorABC):
    pass

# 在管道中使用
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY
microop = OPERATOR_REGISTRY.get("custom_microop")()
```

### 性能考虑

#### 正则表达式优化
- 使用非捕获组 `(?:...)` 当不需要捕获时
- 避免回溯灾难，设计高效的模式
- 预编译复杂正则表达式

#### 内存使用
- 流式处理大文本而非一次性加载
- 使用生成器处理大型数据集
- 及时清理临时变量

#### 并行处理
- 设计无状态操作以支持并行执行
- 避免全局变量依赖
- 确保线程安全

## 扩展性与维护

### 添加新微操作
1. 确定功能范围和职责边界
2. 设计高效的处理算法
3. 实现标准接口和错误处理
4. 编写全面的测试用例
5. 更新相关文档

### 性能监控
- 使用日志记录处理时间
- 监控内存使用情况
- 收集处理效果统计信息

### 版本兼容性
- 保持向后兼容的接口设计
- 使用配置参数支持新功能
- 提供迁移指南和最佳实践

---

**注意**：微操作层是整个文本处理架构的基础，其稳定性和性能直接影响上层组件的表现。在开发新微操作时，务必遵循设计原则，确保代码质量和测试覆盖率。 