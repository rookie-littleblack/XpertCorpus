# RemoveURLsMicroops API 文档

## 概述

`RemoveURLsMicroops` 是一个智能的 URL 链接检测和清理微算子，能够识别并处理各种格式的 URL 链接。支持多种协议、域名过滤、邮箱保护等高级功能，是文本清洗中的重要组件。

## 类定义

```python
@register_operator("remove_urls")
class RemoveURLsMicroops(OperatorABC):
    """
    URL removal micro-operation with comprehensive URL detection
    and unified error handling.
    """
```

## 核心特性

### 🌐 全面协议支持
- **标准协议**：http, https, ftp, ftps, sftp
- **文件协议**：file, data, mailto
- **通信协议**：tel, sms, ssh
- **自动检测**：支持20+种常见URL协议

### 🎯 智能检测算法
- **完整URL**：带协议的完整URL地址
- **部分URL**：www.example.com 格式
- **域名验证**：基于TLD列表的域名有效性验证
- **上下文感知**：避免误删除邮箱中的域名

### 🛡️ 隐私保护
- **邮箱保护**：自动保护邮箱地址中的域名部分
- **域名保留**：可选择保留域名而非完全删除
- **白名单机制**：支持域名白名单和黑名单

## 配置参数

### 基础配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `replacement_text` | str | '' | URL替换文本 |
| `preserve_domains` | bool | False | 是否保留域名 |
| `remove_partial_urls` | bool | True | 是否移除部分URL |
| `case_sensitive` | bool | False | 域名匹配是否大小写敏感 |

### 高级配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `whitelist_domains` | List[str] | [] | 域名白名单 |
| `blacklist_domains` | List[str] | [] | 域名黑名单 |
| `preserve_email_domains` | bool | True | 保护邮箱域名 |

## 使用示例

### 基础用法

```python
from xpertcorpus.modules.microops import RemoveURLsMicroops

# 创建微算子实例
url_cleaner = RemoveURLsMicroops()

# 清理URL
text = "Visit https://example.com or www.test.org for more info"
cleaned = url_cleaner.run(text)
print(cleaned)  # 输出: "Visit  or  for more info"
```

### 保留域名

```python
# 保留域名配置
config = {
    'preserve_domains': True,
    'remove_partial_urls': True
}

url_cleaner = RemoveURLsMicroops(config)
text = "Check https://github.com and www.google.com"
result = url_cleaner.run(text)
print(result)  # 输出: "Check github.com and google.com"
```

### 域名白名单

```python
# 只保留白名单域名
config = {
    'whitelist_domains': ['github.com', 'stackoverflow.com'],
    'preserve_domains': True
}

url_cleaner = RemoveURLsMicroops(config)
text = "Visit https://github.com, https://example.com, and https://stackoverflow.com"
result = url_cleaner.run(text)
print(result)  # 输出: "Visit github.com,  and stackoverflow.com"
```

## 支持的URL格式

### 协议类型

| 协议 | 示例 | 检测支持 |
|------|------|----------|
| HTTP/HTTPS | `https://example.com` | ✅ |
| FTP | `ftp://files.example.com` | ✅ |
| SFTP | `sftp://secure.example.com` | ✅ |
| File | `file:///path/to/file` | ✅ |
| Mailto | `mailto:user@example.com` | ✅ |
| Tel | `tel:+1234567890` | ✅ |
| SSH | `ssh://server.example.com` | ✅ |

### URL格式

| 格式类型 | 示例 | 说明 |
|----------|------|------|
| 完整URL | `https://www.example.com/path?query=1` | 包含协议的完整地址 |
| 简化URL | `www.example.com` | 以www开头的地址 |
| 域名 | `example.com` | 纯域名格式 |
| 带端口 | `example.com:8080` | 包含端口号 |
| 带路径 | `example.com/path/to/page` | 包含路径信息 |

### 常见TLD支持

支持200+种顶级域名，包括：
- **通用TLD**：.com, .org, .net, .edu, .gov
- **国家TLD**：.cn, .uk, .de, .fr, .jp, .au
- **新通用TLD**：.io, .ai, .dev, .app, .tech

## 处理流程

### 1. 邮箱保护阶段
```
检测邮箱地址
    ↓
临时替换为占位符
    ↓
保护邮箱中的域名部分
```

### 2. 协议URL处理
```
检测带协议的URL
    ↓
验证域名有效性
    ↓
应用白名单/黑名单规则
    ↓
执行替换或域名保留
```

### 3. 部分URL处理
```
检测www.domain和domain.tld格式
    ↓
验证TLD有效性
    ↓
应用过滤规则
    ↓
执行替换操作
```

### 4. 恢复邮箱
```
恢复之前保护的邮箱地址
    ↓
清理多余空白字符
    ↓
返回处理结果
```

## 智能特性

### 邮箱域名保护
自动识别并保护邮箱地址，避免误删：
```python
text = "Contact us at support@example.com or visit https://example.com"
# 输出: "Contact us at support@example.com or visit "
# 邮箱中的example.com被保护，URL中的被移除
```

### 上下文感知
智能区分不同上下文中的域名：
```python
text = "Email: user@github.com, Website: https://github.com"
# 可以只移除Website中的URL，保留邮箱
```

### 域名提取算法
使用 `urlparse` 和正则表达式结合的方式：
```python
def _extract_domain(self, url: str) -> Optional[str]:
    # 自动添加协议以便解析
    # 移除端口号和www前缀
    # 返回清洁的域名
```

## 性能优化

### 预编译模式
- **协议检测**：预编译协议正则表达式
- **TLD验证**：预编译常见TLD模式
- **域名提取**：优化的域名解析算法

### 批量处理
- **模式匹配**：使用单次遍历检测所有URL
- **缓存机制**：缓存域名解析结果
- **内存优化**：避免重复字符串创建

## 错误处理

### 异常情况
- **恶意URL**：过长或包含特殊字符的URL
- **编码问题**：不同编码的域名处理
- **解析失败**：畸形URL的容错处理

### 统一错误处理
```python
return self.error_handler.execute_with_retry(
    func=self._remove_urls,
    args=(input_string,),
    max_retries=2,
    operation_name="URL removal"
)
```

## 统计信息

```python
stats = url_cleaner.get_stats()
print(stats)
# 输出示例:
# {
#     'microop_name': 'RemoveURLsMicroops',
#     'urls_removed': 15,
#     'domains_preserved': 3,
#     'partial_urls_removed': 8,
#     'processing_errors': 0,
#     'config': {...}
# }
```

## 实际应用场景

### 1. 社交媒体清洗
```python
# 移除社交媒体中的分享链接
config = {
    'preserve_domains': False,
    'remove_partial_urls': True
}
cleaner = RemoveURLsMicroops(config)
```

### 2. 学术文本处理
```python
# 保留重要网站域名
config = {
    'preserve_domains': True,
    'whitelist_domains': ['doi.org', 'arxiv.org', 'pubmed.gov']
}
cleaner = RemoveURLsMicroops(config)
```

### 3. 新闻内容清理
```python
# 移除新闻中的广告链接
config = {
    'blacklist_domains': ['ads.com', 'tracker.com'],
    'preserve_email_domains': True
}
cleaner = RemoveURLsMicroops(config)
```

## 最佳实践

### 配置建议
1. **保护邮箱**：始终启用邮箱域名保护
2. **性能优先**：大文本处理时关闭域名保留
3. **隐私安全**：使用黑名单过滤已知恶意域名
4. **内容质量**：根据文本类型调整部分URL检测

### 注意事项
1. **误删风险**：部分URL检测可能误删正常词汇
2. **性能影响**：大量URL的文本处理较慢
3. **编码问题**：国际化域名需要特殊处理
4. **上下文理解**：某些缩写可能被误识别为域名

---

**总结**：`RemoveURLsMicroops` 提供了全面的URL检测和清理功能，通过智能算法和丰富配置，能够精确处理各种URL格式，是文本清洗中不可缺少的重要工具。 