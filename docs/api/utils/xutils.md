# 工具函数 (xutils)

`xpertcorpus.utils.xutils` 模块提供通用工具函数和令牌计数功能，包括文本处理、分词和各种实用工具函数。

## 模块概述

工具函数模块为 XpertCorpus 框架提供基础工具支持，包括：
- 文本令牌化和计数功能
- 分词器的获取和管理
- 通用文本处理工具
- 数据验证和转换函数
- 系统实用工具函数

## 核心函数

### get_xtokenizer()

获取框架标准分词器实例。

```python
def get_xtokenizer(
    tokenizer_name: str = "cl100k_base",
    cache: bool = True
) -> Any
```

**参数：**
- `tokenizer_name`: 分词器名称（默认：cl100k_base）
- `cache`: 是否缓存分词器实例

**返回：** 分词器实例

**支持的分词器：**
- `cl100k_base`: OpenAI GPT-3.5/GPT-4 使用的分词器
- `p50k_base`: OpenAI GPT-3 使用的分词器
- `r50k_base`: OpenAI Codex 使用的分词器

**使用示例：**
```python
from xpertcorpus.utils.xutils import get_xtokenizer

# 获取默认分词器
tokenizer = get_xtokenizer()

# 获取特定分词器
gpt3_tokenizer = get_xtokenizer("p50k_base")
codex_tokenizer = get_xtokenizer("r50k_base")

# 禁用缓存
fresh_tokenizer = get_xtokenizer(cache=False)
```

### count_tokens()

计算文本的令牌数量。

```python
def count_tokens(
    text: str,
    tokenizer_name: str = "cl100k_base"
) -> int
```

**参数：**
- `text`: 待计算的文本
- `tokenizer_name`: 使用的分词器名称

**返回：** 令牌数量

**使用示例：**
```python
from xpertcorpus.utils.xutils import count_tokens

# 基础令牌计数
text = "Hello, world! This is a test."
token_count = count_tokens(text)
print(f"令牌数量: {token_count}")

# 使用不同分词器
gpt3_count = count_tokens(text, "p50k_base")
gpt4_count = count_tokens(text, "cl100k_base")

print(f"GPT-3 令牌数: {gpt3_count}")
print(f"GPT-4 令牌数: {gpt4_count}")

# 计算大文本的令牌数
with open("large_text.txt", "r", encoding="utf-8") as f:
    large_text = f.read()
    large_token_count = count_tokens(large_text)
    print(f"大文本令牌数: {large_token_count}")
```

## 扩展工具函数

虽然当前模块主要提供分词功能，但根据框架的发展需要，通常还会包含以下类型的工具函数：

### 文本处理工具

```python
def normalize_text(text: str, **kwargs) -> str:
    """标准化文本内容"""
    pass

def clean_whitespace(text: str) -> str:
    """清理多余的空白字符"""
    pass

def extract_sentences(text: str) -> List[str]:
    """提取句子列表"""
    pass

def detect_language(text: str) -> str:
    """检测文本语言"""
    pass
```

### 数据验证工具

```python
def validate_json(data: str) -> bool:
    """验证JSON格式"""
    pass

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pass

def validate_url(url: str) -> bool:
    """验证URL格式"""
    pass
```

### 系统工具

```python
def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    pass

def check_memory_usage() -> Dict[str, float]:
    """检查内存使用情况"""
    pass

def format_bytes(bytes_value: int) -> str:
    """格式化字节数显示"""
    pass
```

## 使用模式

### 令牌计数应用

```python
from xpertcorpus.utils.xutils import count_tokens, get_xtokenizer

class TokenCounter:
    """令牌计数器类"""
    
    def __init__(self, tokenizer_name="cl100k_base"):
        self.tokenizer_name = tokenizer_name
        self.tokenizer = get_xtokenizer(tokenizer_name)
    
    def count_text(self, text: str) -> int:
        """计算单个文本的令牌数"""
        return count_tokens(text, self.tokenizer_name)
    
    def count_batch(self, texts: List[str]) -> List[int]:
        """批量计算令牌数"""
        return [self.count_text(text) for text in texts]
    
    def count_file(self, file_path: str) -> int:
        """计算文件的令牌数"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.count_text(content)
    
    def analyze_dataset(self, texts: List[str]) -> Dict[str, Any]:
        """分析数据集的令牌统计"""
        token_counts = self.count_batch(texts)
        
        return {
            "total_texts": len(texts),
            "total_tokens": sum(token_counts),
            "avg_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
            "min_tokens": min(token_counts) if token_counts else 0,
            "max_tokens": max(token_counts) if token_counts else 0,
            "median_tokens": sorted(token_counts)[len(token_counts)//2] if token_counts else 0
        }

# 使用示例
counter = TokenCounter("cl100k_base")

# 单个文本计数
text = "This is a sample text for token counting."
tokens = counter.count_text(text)
print(f"令牌数: {tokens}")

# 批量计数
texts = [
    "First text sample.",
    "Second text sample with more content.",
    "Third text sample with even more detailed content."
]
batch_counts = counter.count_batch(texts)
print(f"批量计数: {batch_counts}")

# 数据集分析
analysis = counter.analyze_dataset(texts)
print(f"数据集分析: {analysis}")
```

### 文本预处理管道

```python
from xpertcorpus.utils.xutils import count_tokens

class TextPreprocessor:
    """文本预处理器"""
    
    def __init__(self, max_tokens=4096, tokenizer_name="cl100k_base"):
        self.max_tokens = max_tokens
        self.tokenizer_name = tokenizer_name
    
    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """预处理单个文本"""
        # 基础清理
        cleaned_text = self._clean_text(text)
        
        # 计算令牌数
        token_count = count_tokens(cleaned_text, self.tokenizer_name)
        
        # 处理过长文本
        if token_count > self.max_tokens:
            cleaned_text = self._truncate_text(cleaned_text)
            token_count = count_tokens(cleaned_text, self.tokenizer_name)
        
        return {
            "original_text": text,
            "processed_text": cleaned_text,
            "token_count": token_count,
            "truncated": token_count != count_tokens(text, self.tokenizer_name)
        }
    
    def _clean_text(self, text: str) -> str:
        """基础文本清理"""
        # 移除多余空白
        text = " ".join(text.split())
        
        # 其他清理规则
        # ...
        
        return text
    
    def _truncate_text(self, text: str) -> str:
        """截断过长文本"""
        # 简单截断策略：按句子截断
        sentences = text.split('.')
        truncated_text = ""
        
        for sentence in sentences:
            temp_text = truncated_text + sentence + "."
            if count_tokens(temp_text, self.tokenizer_name) <= self.max_tokens:
                truncated_text = temp_text
            else:
                break
        
        return truncated_text.strip()
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批量处理文本"""
        return [self.preprocess_text(text) for text in texts]

# 使用示例
preprocessor = TextPreprocessor(max_tokens=2048)

text = "This is a long text that might exceed the token limit..."
result = preprocessor.preprocess_text(text)

print(f"原始令牌数: {count_tokens(result['original_text'])}")
print(f"处理后令牌数: {result['token_count']}")
print(f"是否被截断: {result['truncated']}")
```

### 成本估算工具

```python
from xpertcorpus.utils.xutils import count_tokens

class CostEstimator:
    """API成本估算器"""
    
    def __init__(self):
        # OpenAI API 价格（每1K令牌）
        self.pricing = {
            "gpt-3.5-turbo": {
                "input": 0.0015,   # $0.0015 per 1K tokens
                "output": 0.002    # $0.002 per 1K tokens
            },
            "gpt-4": {
                "input": 0.03,     # $0.03 per 1K tokens
                "output": 0.06     # $0.06 per 1K tokens
            },
            "gpt-4-turbo": {
                "input": 0.01,     # $0.01 per 1K tokens
                "output": 0.03     # $0.03 per 1K tokens
            }
        }
    
    def estimate_cost(
        self,
        input_text: str,
        expected_output_tokens: int,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, float]:
        """估算API调用成本"""
        
        if model not in self.pricing:
            raise ValueError(f"未知模型: {model}")
        
        # 计算输入令牌数
        input_tokens = count_tokens(input_text, "cl100k_base")
        
        # 计算成本
        input_cost = (input_tokens / 1000) * self.pricing[model]["input"]
        output_cost = (expected_output_tokens / 1000) * self.pricing[model]["output"]
        total_cost = input_cost + output_cost
        
        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": expected_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def estimate_batch_cost(
        self,
        texts: List[str],
        avg_output_tokens: int,
        model: str = "gpt-3.5-turbo"
    ) -> Dict[str, Any]:
        """估算批量处理成本"""
        
        total_input_tokens = sum(count_tokens(text, "cl100k_base") for text in texts)
        total_output_tokens = len(texts) * avg_output_tokens
        
        input_cost = (total_input_tokens / 1000) * self.pricing[model]["input"]
        output_cost = (total_output_tokens / 1000) * self.pricing[model]["output"]
        total_cost = input_cost + output_cost
        
        return {
            "model": model,
            "batch_size": len(texts),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "avg_input_tokens": total_input_tokens / len(texts),
            "avg_output_tokens": avg_output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "cost_per_text": total_cost / len(texts)
        }

# 使用示例
estimator = CostEstimator()

# 单个请求成本估算
text = "Please analyze this text and provide insights..."
cost_info = estimator.estimate_cost(
    input_text=text,
    expected_output_tokens=200,
    model="gpt-3.5-turbo"
)

print(f"输入令牌: {cost_info['input_tokens']}")
print(f"预期输出令牌: {cost_info['output_tokens']}")
print(f"预估总成本: ${cost_info['total_cost']:.4f}")

# 批量处理成本估算
texts = [
    "First text to process...",
    "Second text to process...",
    "Third text to process..."
]

batch_cost = estimator.estimate_batch_cost(
    texts=texts,
    avg_output_tokens=150,
    model="gpt-4"
)

print(f"批量大小: {batch_cost['batch_size']}")
print(f"总成本: ${batch_cost['total_cost']:.4f}")
print(f"平均每条成本: ${batch_cost['cost_per_text']:.4f}")
```

### 数据质量检查

```python
from xpertcorpus.utils.xutils import count_tokens

class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self, min_tokens=10, max_tokens=4096):
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
    
    def check_text_quality(self, text: str) -> Dict[str, Any]:
        """检查单个文本的质量"""
        issues = []
        
        # 基础检查
        if not text or not text.strip():
            issues.append("empty_text")
        
        if len(text.strip()) < 10:
            issues.append("too_short")
        
        # 令牌数检查
        token_count = count_tokens(text, "cl100k_base")
        
        if token_count < self.min_tokens:
            issues.append("insufficient_tokens")
        
        if token_count > self.max_tokens:
            issues.append("excessive_tokens")
        
        # 字符质量检查
        if self._has_encoding_issues(text):
            issues.append("encoding_issues")
        
        if self._is_mostly_repetitive(text):
            issues.append("repetitive_content")
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "token_count": token_count,
            "character_count": len(text),
            "issues": issues,
            "is_valid": len(issues) == 0,
            "quality_score": self._calculate_quality_score(text, issues)
        }
    
    def _has_encoding_issues(self, text: str) -> bool:
        """检查编码问题"""
        # 检查常见的编码问题字符
        problem_chars = ['�', '\ufffd']
        return any(char in text for char in problem_chars)
    
    def _is_mostly_repetitive(self, text: str, threshold=0.7) -> bool:
        """检查内容是否过于重复"""
        words = text.split()
        if len(words) < 10:
            return False
        
        unique_words = len(set(words))
        repetition_ratio = unique_words / len(words)
        
        return repetition_ratio < (1 - threshold)
    
    def _calculate_quality_score(self, text: str, issues: List[str]) -> float:
        """计算质量分数 (0-1)"""
        base_score = 1.0
        
        # 根据问题类型扣分
        penalty_map = {
            "empty_text": 1.0,
            "too_short": 0.5,
            "insufficient_tokens": 0.3,
            "excessive_tokens": 0.2,
            "encoding_issues": 0.3,
            "repetitive_content": 0.4
        }
        
        for issue in issues:
            base_score -= penalty_map.get(issue, 0.1)
        
        return max(0.0, base_score)
    
    def check_batch_quality(self, texts: List[str]) -> Dict[str, Any]:
        """批量检查文本质量"""
        results = [self.check_text_quality(text) for text in texts]
        
        valid_texts = [r for r in results if r["is_valid"]]
        invalid_texts = [r for r in results if not r["is_valid"]]
        
        # 统计问题类型
        issue_counts = {}
        for result in results:
            for issue in result["issues"]:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        return {
            "total_texts": len(texts),
            "valid_texts": len(valid_texts),
            "invalid_texts": len(invalid_texts),
            "validity_rate": len(valid_texts) / len(texts) if texts else 0,
            "avg_quality_score": sum(r["quality_score"] for r in results) / len(results) if results else 0,
            "issue_distribution": issue_counts,
            "detailed_results": results
        }

# 使用示例
checker = DataQualityChecker(min_tokens=5, max_tokens=2048)

# 单个文本检查
text = "This is a sample text for quality checking."
quality_result = checker.check_text_quality(text)

print(f"文本质量: {quality_result}")
print(f"是否有效: {quality_result['is_valid']}")
print(f"质量分数: {quality_result['quality_score']:.2f}")

# 批量质量检查
texts = [
    "Good quality text with sufficient content.",
    "",  # 空文本
    "Short",  # 太短
    "Repetitive repetitive repetitive repetitive repetitive repetitive repetitive repetitive."  # 重复内容
]

batch_result = checker.check_batch_quality(texts)
print(f"批量检查结果:")
print(f"有效率: {batch_result['validity_rate']:.2%}")
print(f"平均质量分数: {batch_result['avg_quality_score']:.2f}")
print(f"问题分布: {batch_result['issue_distribution']}")
```

## 性能优化

### 分词器缓存

```python
from functools import lru_cache
from xpertcorpus.utils.xutils import get_xtokenizer

class OptimizedTokenCounter:
    """优化的令牌计数器"""
    
    def __init__(self):
        self._tokenizer_cache = {}
    
    @lru_cache(maxsize=1000)
    def count_tokens_cached(self, text: str, tokenizer_name: str = "cl100k_base") -> int:
        """带缓存的令牌计数"""
        if tokenizer_name not in self._tokenizer_cache:
            self._tokenizer_cache[tokenizer_name] = get_xtokenizer(tokenizer_name)
        
        tokenizer = self._tokenizer_cache[tokenizer_name]
        return len(tokenizer.encode(text))
    
    def count_tokens_batch(self, texts: List[str], tokenizer_name: str = "cl100k_base") -> List[int]:
        """批量令牌计数（优化版）"""
        if tokenizer_name not in self._tokenizer_cache:
            self._tokenizer_cache[tokenizer_name] = get_xtokenizer(tokenizer_name)
        
        tokenizer = self._tokenizer_cache[tokenizer_name]
        
        # 批量编码，减少函数调用开销
        return [len(tokenizer.encode(text)) for text in texts]

# 使用优化的计数器
counter = OptimizedTokenCounter()

# 重复文本会命中缓存
text = "This is a test text."
count1 = counter.count_tokens_cached(text)  # 首次计算
count2 = counter.count_tokens_cached(text)  # 从缓存获取

# 批量处理更高效
texts = ["Text 1", "Text 2", "Text 3"] * 100
batch_counts = counter.count_tokens_batch(texts)
```

## 最佳实践

### 1. 分词器选择

```python
# 根据模型选择合适的分词器
MODEL_TOKENIZERS = {
    "gpt-3.5-turbo": "cl100k_base",
    "gpt-4": "cl100k_base", 
    "gpt-3": "p50k_base",
    "codex": "r50k_base"
}

def get_model_tokenizer(model_name: str) -> str:
    """根据模型名获取对应的分词器"""
    return MODEL_TOKENIZERS.get(model_name, "cl100k_base")

# 使用示例
model = "gpt-4"
tokenizer_name = get_model_tokenizer(model)
token_count = count_tokens(text, tokenizer_name)
```

### 2. 错误处理

```python
from xpertcorpus.utils.xutils import count_tokens

def safe_count_tokens(text: str, tokenizer_name: str = "cl100k_base") -> int:
    """安全的令牌计数，包含错误处理"""
    try:
        if not isinstance(text, str):
            raise ValueError("输入必须是字符串")
        
        if not text.strip():
            return 0
        
        return count_tokens(text, tokenizer_name)
        
    except Exception as e:
        print(f"令牌计数失败: {e}")
        return 0  # 返回默认值

# 使用安全计数
count = safe_count_tokens("test text")
count = safe_count_tokens("")  # 空字符串
count = safe_count_tokens(None)  # 错误输入
```

### 3. 内存管理

```python
def count_large_file_tokens(file_path: str, chunk_size: int = 1000000) -> int:
    """分块计算大文件的令牌数，避免内存溢出"""
    total_tokens = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            chunk_tokens = count_tokens(chunk)
            total_tokens += chunk_tokens
    
    return total_tokens
```

## 注意事项

### 1. 性能考虑

- 分词器初始化有一定开销，建议复用实例
- 大文本的令牌计数可能较慢，考虑分块处理
- 频繁计数可以使用缓存机制

### 2. 准确性

- 不同分词器对同一文本的令牌数可能不同
- 确保使用与目标模型匹配的分词器
- 注意特殊字符和编码问题

### 3. 内存使用

- 避免一次性加载过大的文本
- 注意分词器的内存占用
- 及时清理不需要的分词器缓存

---

**更多信息：**
- [错误处理 (xerror_handler)](xerror_handler.md)
- [日志系统 (xlogger)](xlogger.md)
- [配置管理 (xconfig)](xconfig.md) 