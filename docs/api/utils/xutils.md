# 工具函数 (xutils)

`xpertcorpus.utils.xutils` 模块提供通用工具函数，目前主要包括分词器获取和令牌计数功能。

## 模块概述

该模块为 XpertCorpus 框架提供基础的文本处理工具，核心功能是围绕分词器进行令牌计数。

## 核心函数

### get_xtokenizer()

获取框架内置的默认分词器实例。

```python
def get_xtokenizer() -> Any:
    """
    获取 XTokenizer。
    
    备注：使用 Qwen3-8B-tokenizer 作为默认分词器进行近似令牌计数。
    """
```

**实现细节：**
- 分词器模型位于项目内的 `xpertcorpus/resources/tokenizers/qwen3-8b-tokenizer` 目录。
- 函数会自动检查该目录是否存在，如果不存在则抛出 `FileNotFoundError`。
- 使用 `transformers.AutoTokenizer` 加载分词器。

### count_tokens()

计算文本的令牌数量。

```python
def count_tokens(text: str) -> int:
    """
    计算字符串中的令牌数量。
    
    Args:
        text (str): 待计算的输入文本
        
    Returns:
        int: 文本中的令牌数量
    """
```

**实现细节：**
- 使用全局的 `xtokenizer` 实例进行编码和计数。
- 如果 `transformers` 库导入失败，会回退到简单的按空格分割进行计数。

## 全局实例

模块在初始化时会自动创建一个全局的分词器实例，供 `count_tokens` 函数使用。

```python
# xtokenizer 是一个全局的分词器实例
xtokenizer = get_xtokenizer()
```

## 使用示例

### 基本令牌计数

```python
from xpertcorpus.utils.xutils import count_tokens

# 计算英文文本的令牌数
text_en = "Hello, world! I am XpertCorpus!"
tokens_en = count_tokens(text_en)
print(f"'{text_en}' 的令牌数是: {tokens_en}")

# 计算中文文本的令牌数
text_zh = "你好啊，我是XpertCorpus！"
tokens_zh = count_tokens(text_zh)
print(f"'{text_zh}' 的令牌数是: {tokens_zh}")
```

### 与日志系统结合使用

```python
from xpertcorpus.utils.xutils import count_tokens
from xpertcorpus.utils.xlogger import xlogger

def process_and_log(text):
    """处理文本并记录令牌信息"""
    
    token_count = count_tokens(text)
    
    xlogger.info("文本处理完成", data={
        "text_snippet": text[:50] + "...",
        "token_count": token_count
    })
    
    # ... 其他处理逻辑 ...

process_and_log("这是一段用于演示的长文本，它将被处理并记录相关的令牌统计信息。")
```

## 错误处理

- **`get_xtokenizer()`**: 如果找不到分词器目录，会抛出 `FileNotFoundError`。
- **`count_tokens()`**: 如果 `transformers` 库出现问题，会记录错误日志并使用简单的空格分割方法作为备用方案。

## 注意事项

### 1. 性能考虑
- `get_xtokenizer()` 在模块加载时只调用一次，后续 `count_tokens()` 直接复用该实例，避免了重复加载模型的开销。
- 对于非常大的文本，一次性调用 `count_tokens()` 可能会消耗较多内存。

### 2. 准确性
- 使用 `Qwen3-8B-tokenizer` 进行令牌计数，这是一个近似值，与其他模型（如GPT-4）的实际令牌数可能存在差异。主要用于快速估算和比较。

## 相关文档

- [日志系统 (xlogger)](xlogger.md)

---

[返回 Utils 模块首页](README.md) | [返回 API 文档首页](../README.md) 