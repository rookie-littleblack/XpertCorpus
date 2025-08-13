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
**功能描述**：高效移除文本中的表情符号（文本式表情）

**核心特性**：
- 支持超过 5000 种表情符号模式
- 基于正则表达式的优化匹配算法（替代原有的逐个替换）
- 集成统一错误处理系统（xerror_handler）
- 支持配置参数自定义行为
- 包含常见表情符号变体的自动检测

**性能改进**：
- 使用单一正则表达式替代逐个字符串替换，性能提升 **10-50 倍**
- 按长度排序匹配，确保正确处理重叠模式
- 支持大小写敏感/不敏感配置

**配置参数**：
- `replacement_text`：替换文本（默认：''）
- `case_sensitive`：大小写敏感（默认：False）
- `preserve_spacing`：保留原始间距（默认：False）

**注册名称**：`remove_emoticons`

**使用场景**：
- 清理社交媒体文本
- 标准化聊天记录
- 准备机器学习训练数据

### RemoveEmojiMicroops
**功能描述**：全面移除文本中的 Unicode 表情符号，支持肤色修饰符和 ZWJ 序列

**核心特性**：
- **扩展 Unicode 支持**：覆盖 Unicode 15.0 标准
- **智能序列处理**：支持肤色修饰符、ZWJ（零宽连字符）序列
- **边缘情况处理**：键盘符号、标志序列、变异选择器
- **配置化替换**：支持自定义替换行为
- **性能优化**：预编译正则表达式模式

**Unicode 覆盖范围**：
- 基础表情符号：`\U0001F600-\U0001F64F`
- 杂项符号：`\U0001F300-\U0001F5FF`
- 交通地图符号：`\U0001F680-\U0001F6FF`
- 国旗符号：`\U0001F1E0-\U0001F1FF`
- 扩展符号：`\U0001F900-\U0001F9FF`、`\U0001FA00-\U0001FAFF`
- 装饰符号：`\U00002600-\U000026FF`、`\U00002700-\U000027BF`

**新增特性**：
- 肤色修饰符处理：`\U0001F3FB-\U0001F3FF`
- ZWJ 序列支持：复杂表情符号组合
- 键盘符号：数字键、特殊键等
- 文本表情符号可选保留

**配置参数**：
- `replacement_text`：替换文本（默认：''）
- `preserve_text_emoji`：保留文本表情符号（默认：True）
- `remove_skin_tones`：移除肤色修饰符（默认：True）
- `remove_zwj_sequences`：移除 ZWJ 序列（默认：True）

**注册名称**：`remove_emoji`

**使用场景**：
- 文本标准化处理
- 移除视觉干扰元素
- 改善文本分析准确性
- 多语言文本清理

### RemoveExtraSpacesMicroops
**功能描述**：智能移除文本中的多余空格和换行符，保护代码块格式

**核心特性**：
- **增强代码检测**：改进的代码块识别算法
- **配置化处理**：支持自定义处理参数
- **性能优化**：预编译正则表达式，优化处理逻辑
- **统一错误处理**：集成 xerror_handler 系统
- **智能格式保护**：更精确的代码和文本区分

**处理策略**：
1. **代码保护（增强）**：
   - 围栏式代码块（```、~~~）
   - 缩进代码块（4+ 空格开头）
   - 行内代码（反引号包围）
   - HTML pre/code 标签
   - 编程语言特征检测（扩展关键词库）
   - 编程字符模式识别

2. **文本清理（优化）**：
   - 移除 `\r` 字符
   - 压缩连续换行符（3+ → 2）
   - 清理多余空格（可配置最大缩进保留）
   - 标准化制表符和空格混合
   - 可选的行尾空格移除

3. **智能判断（改进）**：
   - 可配置的代码检测阈值（默认 0.3）
   - 关键词集合优化查找
   - 分层次的模式匹配
   - 上下文感知的格式判断

**配置参数**：
- `max_indent_preservation`：最大缩进保留（默认：4）
- `code_detection_threshold`：代码检测阈值（默认：0.3）
- `preserve_code_blocks`：是否保护代码块（默认：True）
- `remove_trailing_spaces`：是否移除行尾空格（默认：True）

**性能提升**：
- 预编译正则表达式模式缓存
- 优化的文本分段处理
- 减少重复计算和字符串操作

**注册名称**：`remove_extra_spaces`

**使用场景**：
- 文档格式标准化
- 减少存储空间占用
- 改善文本处理效果
- 保护代码块格式完整性
- 技术文档处理

## 微操作开发指南

### 优化后的基础结构

每个微操作都应该遵循以下优化的基本结构：

```python
from typing import Dict, Any, Optional
from xpertcorpus.utils import xlogger
from xpertcorpus.utils.xerror_handler import XErrorHandler, XRetryMechanism
from xpertcorpus.modules.others.xoperator import OperatorABC, register_operator

@register_operator("your_microop_name")
class YourMicroops(OperatorABC):
    """
    Enhanced micro-operation with unified error handling.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize with configuration support.
        
        Args:
            config: Configuration dictionary with optional parameters
        """
        super().__init__(config)
        self.error_handler = XErrorHandler()
        self.retry_mechanism = XRetryMechanism(max_retries=2, base_delay=0.1)
        
        # Configuration parameters
        self.param1 = self.config.get('param1', default_value)
        self.param2 = self.config.get('param2', default_value)
        
        xlogger.info(f"Initializing {self.__class__.__name__} with config: {self.config}")
        
        # Pre-compile patterns for performance
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance."""
        # Pre-compile complex regex patterns
        pass
    
    @staticmethod
    def get_desc(lang: str = "zh") -> str:
        """Get description of the micro-operation."""
        return (
            "中文描述" 
            if lang == "zh" 
            else "English description"
        )
    
    def run(self, input_string: str) -> str:
        """
        Enhanced run method with error handling and performance optimization.
        
        Args:
            input_string: Input text to process
            
        Returns:
            Processed text
        """
        if not input_string:
            return input_string

        def _process_text() -> str:
            return self._process(input_string)

        try:
            # Use retry mechanism for processing
            result = self.retry_mechanism.execute(_process_text)
            
            # Log processing statistics
            original_length = len(input_string)
            processed_length = len(result)
            if original_length != processed_length:
                xlogger.debug(
                    f"Processing: {original_length} -> {processed_length} characters"
                )
            
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_error(
                e,
                context=f"Processing text with length {len(input_string)}",
                operation="your_microop_name"
            )
            xlogger.error(f"Error in {self.__class__.__name__}: {error_info}")
            return input_string  # Return original on error
    
    def _process(self, text: str) -> str:
        """
        Actual processing implementation.
        
        Args:
            text: Input text
            
        Returns:
            Processed text
        """
        # Implementation here
        return text
```

### 开发最佳实践

#### 1. 统一错误处理
- **集成 XErrorHandler**：使用统一的错误处理系统
- **重试机制**：对瞬时错误自动重试
- **上下文记录**：提供详细的错误上下文信息
- **优雅降级**：异常情况下返回原始输入

#### 2. 性能优化策略
- **预编译模式**：在 `__init__` 中预编译所有正则表达式
- **模式缓存**：缓存复杂计算结果
- **批量处理**：避免逐个元素处理
- **内存管理**：及时释放大型临时对象

#### 3. 配置化设计
- **参数化行为**：通过配置控制处理行为
- **默认值设计**：提供合理的默认配置
- **向后兼容**：保持接口兼容性
- **验证机制**：验证配置参数有效性

#### 4. 测试与验证
- **边界情况**：测试空字符串、特殊字符等
- **性能基准**：建立性能基准测试
- **配置测试**：测试各种配置组合
- **集成测试**：确保与其他组件的兼容性

### 配置管理增强

支持更丰富的配置选项：

```python
# 配置文件示例 (YAML)
microops:
  remove_extra_spaces:
    enabled: true
    max_indent_preservation: 4
    code_detection_threshold: 0.3
    preserve_code_blocks: true
    remove_trailing_spaces: true
  
  remove_emoji:
    enabled: true
    replacement_text: ""
    preserve_text_emoji: true
    remove_skin_tones: true
    remove_zwj_sequences: true
  
  remove_emoticons:
    enabled: true
    replacement_text: ""
    case_sensitive: false
    preserve_spacing: false
```

### 性能监控和指标

#### 性能指标收集
```python
# 在微操作中记录性能指标
def run(self, input_string: str) -> str:
    start_time = time.time()
    
    # 处理逻辑
    result = self._process(input_string)
    
    # 记录性能指标
    processing_time = time.time() - start_time
    xlogger.debug(f"Processing time: {processing_time:.4f}s")
    
    return result
```

#### 处理统计
- 处理字符数变化
- 执行时间统计
- 错误频率监控
- 内存使用情况

## 架构集成

### 与错误处理系统集成
- 使用 `XErrorHandler` 进行统一错误分类和处理
- 支持 `XRetryMechanism` 自动重试机制
- 提供详细的错误上下文和恢复建议

### 与注册系统集成
- 通过 `@register_operator` 装饰器自动注册
- 支持 `OPERATOR_REGISTRY` 动态发现和加载
- 提供标准化的操作符接口

### 与配置系统集成
- 支持 YAML 配置文件参数传递
- 运行时配置验证和调整
- 配置热重载支持

## 扩展性与维护

### 版本演进
**当前版本**: 1.1.0
- ✅ 集成统一错误处理系统
- ✅ 性能优化和算法改进
- ✅ 配置化参数支持
- ✅ 扩展 Unicode 支持

**下一版本规划**: 1.2.0
- 🔄 添加更多基础微操作
- 🔄 支持异步处理
- 🔄 增强性能监控
- 🔄 国际化支持

### 添加新微操作
1. **需求分析**：确定功能范围和性能要求
2. **接口设计**：遵循标准接口和配置规范
3. **算法实现**：选择最优的处理算法
4. **错误处理**：集成统一错误处理系统
5. **性能测试**：建立性能基准和压力测试
6. **文档更新**：完善 API 文档和使用示例

### 质量保证
- **代码审查**：遵循项目编码规范
- **单元测试**：覆盖率 ≥ 90%
- **集成测试**：与上层组件兼容性测试
- **性能基准**：建立性能回归检测

---

**注意**：微操作层是整个文本处理架构的基础，其稳定性和性能直接影响上层组件的表现。新版本在保持向后兼容的同时，显著提升了性能和可靠性。 