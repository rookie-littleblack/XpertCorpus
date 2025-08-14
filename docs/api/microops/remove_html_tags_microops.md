# RemoveHTMLTagsMicroops API 文档

## 概述

`RemoveHTMLTagsMicroops` 是一个智能的 HTML 标签清理微算子，专门用于从文本中移除 HTML 和 XML 标签，同时保留纯文本内容。该微算子支持复杂的 HTML 结构处理，包括嵌套标签、畸形 HTML、HTML 实体解码等高级功能。

## 类定义

```python
@register_operator("remove_html_tags")
class RemoveHTMLTagsMicroops(OperatorABC):
    """
    HTML tags removal micro-operation with comprehensive tag detection
    and unified error handling.
    """
```

## 核心特性

### 🔧 智能检测与清理
- **全面标签识别**：自动检测各种 HTML 和 XML 标签
- **嵌套结构处理**：正确处理复杂的嵌套标签结构
- **畸形 HTML 容错**：能够处理不规范的 HTML 代码
- **样式脚本清理**：自动移除 `<style>` 和 `<script>` 标签及其内容

### 🛡️ 高级功能
- **HTML 实体解码**：将 `&amp;`, `&lt;`, `&gt;` 等实体转换为对应字符
- **链接信息保留**：可选择将 `<a>` 标签转换为 "文本 (URL)" 格式
- **白名单机制**：支持保留指定的 HTML 标签
- **注释清理**：自动移除 HTML 注释

### ⚡ 性能优化
- **预编译正则表达式**：提高匹配效率
- **分层处理策略**：按优先级处理不同类型的标签
- **内存友好**：避免创建大量中间对象

## 配置参数

### 基础配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `preserve_formatting` | bool | False | 是否保留基本文本格式 |
| `replace_with_space` | bool | True | 用空格替代标签而非完全删除 |
| `decode_entities` | bool | True | 是否解码 HTML 实体 |
| `remove_style_script` | bool | True | 是否移除样式和脚本内容 |

### 高级配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `whitelist_tags` | List[str] | [] | 需要保留的 HTML 标签列表 |
| `preserve_links` | bool | False | 是否保留链接信息 |

## 使用示例

### 基础用法

```python
from xpertcorpus.modules.microops import RemoveHTMLTagsMicroops

# 创建微算子实例
html_cleaner = RemoveHTMLTagsMicroops()

# 清理 HTML 文本
html_text = '<p>Hello <b>world</b>!</p><script>alert("test")</script>'
cleaned = html_cleaner.run(html_text)
print(cleaned)  # 输出: "Hello world!"
```

### 高级配置使用

```python
# 保留链接信息的配置
config = {
    'preserve_links': True,
    'decode_entities': True,
    'preserve_formatting': True
}

html_cleaner = RemoveHTMLTagsMicroops(config)
text = 'Visit <a href="https://example.com">our website</a> for more info'
result = html_cleaner.run(text)
print(result)  # 输出: "Visit our website (https://example.com) for more info"
```

### 白名单标签保留

```python
# 保留特定标签
config = {
    'whitelist_tags': ['strong', 'em'],
    'decode_entities': True
}

html_cleaner = RemoveHTMLTagsMicroops(config)
text = '<p>This is <strong>important</strong> and <em>emphasized</em> text.</p>'
result = html_cleaner.run(text)
print(result)  # 输出: "This is <strong>important</strong> and <em>emphasized</em> text."
```

## 处理流程

### 1. 预处理阶段
```
输入HTML文本
    ↓
移除HTML注释
    ↓
处理样式和脚本标签（可选）
```

### 2. 链接处理阶段
```
检测 <a> 标签
    ↓
提取链接URL和文本
    ↓
转换为 "文本 (URL)" 格式（可选）
```

### 3. 标签处理阶段
```
检测白名单标签
    ↓
保护白名单标签
    ↓
移除其他所有HTML标签
    ↓
恢复白名单标签（如果有）
```

### 4. 后处理阶段
```
解码HTML实体（可选）
    ↓
标准化空白字符
    ↓
返回清理后的文本
```

## 支持的HTML特性

### 标准HTML标签
- **文本格式**：`<p>`, `<div>`, `<span>`, `<h1-h6>`
- **样式相关**：`<b>`, `<i>`, `<strong>`, `<em>`, `<u>`
- **列表结构**：`<ul>`, `<ol>`, `<li>`
- **表格结构**：`<table>`, `<tr>`, `<td>`, `<th>`

### 特殊内容处理
- **脚本内容**：`<script>` 标签及内容完全移除
- **样式内容**：`<style>` 标签及内容完全移除
- **注释内容**：`<!-- -->` 注释完全移除
- **链接处理**：`<a>` 标签可转换为文本+URL格式

### HTML实体支持
- **常见实体**：`&amp;` → `&`, `&lt;` → `<`, `&gt;` → `>`
- **引号实体**：`&quot;` → `"`, `&#39;` → `'`
- **空格实体**：`&nbsp;` → ` `, `&emsp;` → 空格
- **特殊字符**：`&copy;` → `©`, `&reg;` → `®`

## 错误处理

### 统一错误处理
集成 `XErrorHandler` 系统，提供：
- **自动重试**：处理失败时自动重试（最多2次）
- **异常容错**：出现异常时返回原始文本
- **详细日志**：记录处理错误和上下文信息

### 常见问题处理
- **畸形HTML**：容错处理不规范的标签结构
- **编码问题**：自动处理不同编码的HTML内容
- **嵌套过深**：避免递归过深导致的性能问题

## 性能指标

### 处理能力
- **小文本** (< 1KB)：< 1ms
- **中等文本** (1-10KB)：1-5ms  
- **大文本** (10-100KB)：5-20ms
- **超大文本** (> 100KB)：20-100ms

### 内存使用
- **基础模式**：约 2-5MB
- **复杂HTML**：约 5-15MB
- **大量标签**：约 10-30MB

## 统计信息

微算子执行后可通过 `get_stats()` 方法获取处理统计：

```python
stats = html_cleaner.get_stats()
print(stats)
# 输出示例:
# {
#     'microop_name': 'RemoveHTMLTagsMicroops',
#     'tags_removed': 245,
#     'entities_decoded': 12,
#     'processing_errors': 0,
#     'config': {...}
# }
```

## 最佳实践

### 配置建议
1. **网页内容**：启用实体解码和样式脚本移除
2. **文档处理**：启用链接保留功能
3. **性能优先**：关闭格式保留以提高速度
4. **内容安全**：使用白名单而非黑名单

### 使用场景
- **网页内容清洗**：清理爬取的网页内容
- **富文本处理**：处理来自编辑器的富文本
- **文档转换**：HTML到纯文本的转换
- **数据预处理**：为机器学习准备干净的文本数据

### 注意事项
1. **白名单标签**：谨慎选择保留的标签，避免安全风险
2. **链接处理**：大量链接时可能影响可读性
3. **实体解码**：某些场景下可能需要保留原始实体格式
4. **性能考虑**：超大HTML文件建议分块处理

## 扩展开发

### 自定义模式
```python
# 扩展自定义清理模式
class CustomHTMLCleaner(RemoveHTMLTagsMicroops):
    def _compile_patterns(self):
        super()._compile_patterns()
        # 添加自定义正则表达式模式
        self.custom_pattern = re.compile(r'<custom-tag[^>]*>.*?</custom-tag>')
```

### 与其他微算子组合
```python
# 组合使用多个微算子
from xpertcorpus.modules.microops import RemoveURLsMicroops, RemoveExtraSpacesMicroops

def comprehensive_cleaning(text):
    # 1. 移除HTML标签
    html_cleaner = RemoveHTMLTagsMicroops({'preserve_links': True})
    text = html_cleaner.run(text)
    
    # 2. 移除URLs
    url_cleaner = RemoveURLsMicroops()
    text = url_cleaner.run(text)
    
    # 3. 清理多余空格
    space_cleaner = RemoveExtraSpacesMicroops()
    text = space_cleaner.run(text)
    
    return text
```

---

**总结**：`RemoveHTMLTagsMicroops` 提供了全面的 HTML 清理功能，通过智能检测和配置化设计，能够满足各种文本清洗需求，是构建文本处理管道的重要基础组件。 