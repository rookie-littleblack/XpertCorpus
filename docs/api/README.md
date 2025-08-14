# XpertCorpus API 文档概览

## 项目概述

XpertCorpus 是一个轻量级的大模型语料构建端到端框架，采用模块化分层架构设计，从原始语料到训练数据的全流程处理。本文档提供了完整的 API 参考和使用指南。

## 📊 API 覆盖状态 

### 🎯 总体进度

| 层级 | 已完成 | 总计划 | 完成率 | 状态 |
|------|---------|---------|---------|------|
| **微操作层** | 10 | 34 | 29.4% | 🚧 进行中 |
| **算子层** | 2 | 25 | 8% | ⏳ 待开发 |
| **管道层** | 1 | 13 | 7.7% | ⏳ 待开发 |
| **框架层** | 1 | 6 | 16.7% | ⏳ 待开发 |
| **工具层** | 4 | 10 | 40% | ⏳ 待开发 |
| **总计** | **18** | **88** | **20.5%** | **🚧 开发中** |

---

## 🏗️ 架构层次

XpertCorpus 采用四层架构设计，自底向上分别为：

### 1. 微操作层 (Microops)
**定义**: 最小粒度的原子操作，执行单一的数据处理任务
- **继承**: `OperatorABC` 抽象类
- **特点**: 无状态、可复用、功能单一
- **职责**: 基础数据清洗、格式化、转换等原子操作

### 2. 算子层 (Operators)
**定义**: 复合操作，可能调用多个微操作或实现复杂逻辑
- **继承**: `OperatorABC` 抽象类  
- **特点**: 有状态、可配置、逻辑复杂
- **职责**: 文本分割、LLM清洗、质量评估等复合操作

### 3. 管道层 (Pipelines)
**定义**: 算子组合器，将多个算子串联成处理流水线
- **继承**: `OperatorABC` 抽象类
- **特点**: 流程化、可配置、可复用
- **职责**: 预定义的处理流程，如清洗管道、质量管道等

### 4. 框架层 (Frameworks)
**定义**: 最高层抽象，定义完整的数据处理框架
- **继承**: 可选择继承 `FrameworkABC` 抽象类
- **特点**: 端到端、可扩展、业务导向
- **职责**: PT、SFT、CoT等完整的数据生成框架

---

## 📚 模块文档索引

### 🔬 微操作层 (Microops) - **10/34 完成**

#### ✅ 已完成优化 (3个)
| 微操作 | 文档链接 | 功能 | 性能提升 |
|--------|----------|------|----------|
| RemoveEmoticonsMicroops | [📖 API文档](./microops/remove_emoticons_microops.md) | 表情符号清理 | 10-50x |
| RemoveEmojiMicroops | [📖 API文档](./microops/remove_emoji_microops.md) | Unicode表情符清理 | 5-15x |
| RemoveExtraSpacesMicroops | [📖 API文档](./microops/remove_extra_spaces_microops.md) | 智能空格清理 | 3-8x |

#### ✅ 文本清洗类 (7个)
| 微操作 | 文档链接 | 功能 | 特性 |
|--------|----------|------|------|
| RemoveHTMLTagsMicroops | [📖 API文档](./microops/remove_html_tags_microops.md) | HTML标签清理 | 实体解码、链接提取 |
| RemoveURLsMicroops | [📖 API文档](./microops/remove_urls_microops.md) | URL链接清理 | 域名白名单、协议检测 |
| RemoveEmailsMicroops | [📖 API文档](./microops/remove_emails_microops.md) | 邮箱地址处理 | 脱敏、域名过滤 |
| RemovePhoneNumbersMicroops | [📖 API文档](./microops/remove_phone_numbers_microops.md) | 电话号码处理 | 国际格式、脱敏 |
| RemoveSpecialCharsMicroops | [📖 API文档](./microops/remove_special_chars_microops.md) | 特殊字符清理 | 可配置保留策略 |
| RemoveNonPrintableMicroops | [📖 API文档](./microops/remove_non_printable_microops.md) | 非打印字符清理 | Unicode分类过滤 |
| RemoveFooterHeaderMicroops | [📖 API文档](./microops/remove_footer_header_microops.md) | 页眉页脚清理 | 智能模式识别 |

#### ⏳ 规划中 (24个)
| 类别 | 数量 | 主要功能 |
|------|------|----------|
| 文本标准化类 | 5 | 空白字符、Unicode、标点、数字、编码标准化 |
| 语言处理类 | 3 | 语言检测、过滤、音译转换 |
| 内容过滤类 | 4 | 长短文本、重复行、样板文本过滤 |
| 格式转换类 | 3 | 大小写、引号、破折号转换 |
| 数据验证类 | 3 | UTF-8、JSON、Markdown验证 |
| 安全隐私类 | 3 | PII清理、敏感数据脱敏、有害内容检测 |
| 统计分析类 | 3 | 文本统计、元数据提取、可读性分析 |

**详细信息**: [微操作层完整文档](./microops/)

---

### ⚙️ 算子层 (Operators) - **2/25 完成**

#### ✅ 已完成 (2个)
| 算子 | 文档链接 | 功能 | 状态 |
|------|----------|------|------|
| XLlmCleaner | 🚧 文档待更新 | LLM清洗器 | 需要优化 |
| XTextSplitter | 🚧 文档待更新 | 文本分割器 | 需要优化 |

#### ⏳ 规划中 (23个)
| 类别 | 数量 | 主要功能 |
|------|------|----------|
| 格式转换算子 | 6 | SFT、对话、CoT、推理链、格式转换器 |
| 质量评估算子 | 4 | 质量评估、内容过滤、重复检测、语言检测 |
| 数据增强算子 | 3 | 数据增强、释义生成、合成数据生成 |
| 高级分割算子 | 3 | 语义分割、上下文感知分割、自适应分割 |
| 批处理算子 | 3 | 批处理器、分布式处理器、内存优化器 |
| 监控算子 | 2 | 指标收集器、性能监控器 |
| 多模态算子 | 2 | 图文对处理器、视觉指令构建器 |

**详细信息**: [算子层完整文档](./operators/)

---

### 🔄 管道层 (Pipelines) - **1/13 完成**

#### ✅ 已完成 (1个)
| 管道 | 文档链接 | 功能 | 状态 |
|------|----------|------|------|
| XCleaningPipe | 🚧 文档待更新 | 基础文本清洗管道 | 需要扩展 |

#### ⏳ 规划中 (12个)
| 类别 | 数量 | 主要功能 |
|------|------|----------|
| 清洗管道 | 3 | 深度清洗、标准化、语言处理 |
| 质量管道 | 3 | 质量过滤、内容验证、去重 |
| 转换管道 | 3 | 格式转换、结构提取、数据增强 |
| 特定领域管道 | 3 | 代码处理、科学文本、多模态 |

**详细信息**: [管道层完整文档](./pipelines/)

---

### 🎯 框架层 (Frameworks) - **1/6 完成**

#### ✅ 已完成 (1个)
| 框架 | 文档链接 | 功能 | 状态 |
|------|----------|------|------|
| XFramework_PT | 🚧 文档待更新 | 预训练数据生成框架 | 已优化 |

#### ⏳ 规划中 (5个)
| 框架 | 功能 | 优先级 |
|------|------|---------|
| XFramework_SFT | 监督微调数据生成 | P0 |
| XFramework_CoT | 思维链数据生成 | P0 |
| XFramework_Multimodal | 多模态数据生成 | P1 |
| XFramework_DPO | DPO数据生成 | P1 |
| XFramework_RLHF | RLHF数据生成 | P2 |

**详细信息**: [框架层完整文档](./frameworks/)

---

### 🛠️ 工具层 (Utils) - **4/10 完成**

#### ✅ 已完成 (4个)
| 工具 | 文档链接 | 功能 | 状态 |
|------|----------|------|------|
| XLogger | 🚧 文档待创建 | 结构化日志系统 | 已优化 |
| XStorage | 🚧 文档待创建 | 多格式存储管理 | 已优化 |
| XConfig | 🚧 文档待创建 | 配置加载管理 | 已完成 |
| XErrorHandler | 🚧 文档待创建 | 统一错误处理 | 已完成 |

#### ⏳ 规划中 (6个)
| 工具 | 功能 | 优先级 |
|------|------|---------|
| XMetrics | 指标计算工具 | P1 |
| XValidation | 数据验证工具 | P1 |
| XVisualization | 可视化工具 | P2 |
| XDistributed | 分布式处理工具 | P2 |
| XPerformance | 性能监控工具 | P2 |
| XUtils | 通用工具函数扩展 | P1 |

**详细信息**: [工具层完整文档](./utils/)

---

### 🔗 通用组件 (Others)

| 组件 | 文档链接 | 功能 | 状态 |
|------|----------|------|------|
| OperatorABC | 🚧 文档待创建 | 算子抽象基类 | ✅ 已完成 |
| FrameworkABC | 🚧 文档待创建 | 框架抽象基类 | ✅ 已完成 |
| XRegistry | 🚧 文档待创建 | 注册器管理 | ✅ 已完成 |
| XLimitor | 🚧 文档待创建 | 数据限制器 | ✅ 已完成 |
| XPrompts | 🚧 文档待创建 | 提示词模板 | ✅ 已完成 |
| XAPI | 🚧 文档待创建 | API调用封装 | ✅ 已完成 |

**详细信息**: [通用组件完整文档](./others/)

---

## 🚀 快速开始

### 基础使用示例

```python
# 1. 使用单个微操作
from xpertcorpus.modules.microops.remove_emoticons_microops import RemoveEmoticonsMicroops

cleaner = RemoveEmoticonsMicroops()
result = cleaner.run("Hello :) How are you? :D")
print(result)  # "Hello  How are you? "

# 2. 使用清洗管道
from xpertcorpus.modules.pipelines.xcleaning_pipe import XCleaningPipe

pipeline = XCleaningPipe()
result = pipeline.run("Hello :) <p>World</p>   !")

# 3. 使用完整框架
from xpertcorpus.modules.frameworks.xframe_pt import XFramework_PT

framework = XFramework_PT()
framework.run(input_path="data.jsonl", output_path="processed/")
```

### 配置驱动使用

```python
# 配置文件方式
config = {
    'remove_emoticons': {
        'enabled': True,
        'replacement_text': ' '
    },
    'remove_html': {
        'enabled': True,
        'preserve_links': True
    }
}

pipeline = XCleaningPipe(config)
result = pipeline.run(text)
```

---

## 📈 开发路线图

### 🎯 当前阶段 (12.3 微操作层开发)

**进度**: 10/34 完成 (29.4%)

**当前焦点**:
- ✅ 完成现有微操作优化 (3个)
- ✅ 完成文本清洗类微操作 (7个)
- �� 文本标准化类微操作开发 (5个)

### 📋 下一阶段计划

1. **12.4 算子层开发** (4周)
   - 优化现有算子 (2个)
   - 开发核心处理算子 (8个)
   - 开发格式转换算子 (6个)

2. **12.5 管道层开发** (3周)
   - 扩展现有管道 (1个)
   - 开发核心清洗管道 (6个)
   - 开发高级功能管道 (6个)

3. **12.6 框架层开发** (3周)
   - 优化现有框架 (1个)
   - 开发训练数据框架 (5个)

---

## 🔧 配置参考

### 统一配置格式

所有组件都支持统一的配置格式：

```yaml
# config.yaml 示例
microops:
  remove_emoticons:
    enabled: true
    replacement_text: ""
    case_sensitive: false
    
  remove_html:
    enabled: true
    preserve_links: true
    decode_entities: true

operators:
  llm_cleaner:
    enabled: true
    model_name: "gpt-3.5-turbo"
    max_workers: 4

pipelines:
  cleaning_pipe:
    enabled: true
    microops: ["remove_emoticons", "remove_html", "remove_extra_spaces"]

frameworks:
  pt_framework:
    input_path: "data/raw/"
    output_path: "data/processed/"
    enable_parallel: true
```

### 环境变量支持

```bash
# 设置日志级别
export XPERTCORPUS_LOG_LEVEL=DEBUG

# 设置API密钥
export OPENAI_API_KEY=your_api_key

# 设置并发数
export XPERTCORPUS_MAX_WORKERS=8
```

---

## 🐛 错误处理

### 统一错误处理系统

所有组件都集成了统一的错误处理系统：

```python
from xpertcorpus.utils.xerror_handler import XErrorHandler

# 自动重试机制
handler = XErrorHandler()
result = handler.execute_with_retry(
    func=some_operation,
    max_retries=3,
    operation_name="Text processing"
)
```

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| E001 | 配置文件错误 | 检查YAML格式 |
| E002 | 文件读取失败 | 检查文件路径和权限 |
| E003 | API调用失败 | 检查网络和API密钥 |
| E004 | 内存不足 | 减少批处理大小 |

---

## 📊 性能指标

### 基准测试环境
- **CPU**: Intel i7-12700K
- **RAM**: 32GB DDR4
- **测试数据**: 1GB混合文本

### 性能基准

| 组件类型 | 处理速度 | 内存使用 | 错误率 |
|----------|----------|----------|--------|
| **微操作** | 10-100MB/s | <500MB | <0.1% |
| **算子** | 5-50MB/s | <1GB | <0.5% |
| **管道** | 2-20MB/s | <2GB | <1% |
| **框架** | 1-10MB/s | <4GB | <2% |

---

## 📝 贡献指南

### API文档贡献

1. **文档标准**: 使用Markdown格式，遵循现有模板
2. **代码示例**: 提供完整的可运行示例
3. **性能数据**: 包含基准测试结果
4. **错误处理**: 说明常见错误和解决方案

### 开发规范

1. **类型注解**: 所有函数和方法必须有类型注解
2. **文档字符串**: 使用英文编写详细的docstring
3. **错误处理**: 集成统一的错误处理系统
4. **测试覆盖**: 单元测试覆盖率≥80%

---

## 📞 技术支持

### 获取帮助

1. **文档查阅**: 首先查阅相关API文档
2. **示例代码**: 参考examples目录中的示例
3. **常见问题**: 查看FAQ文档
4. **Issue提交**: 在GitHub仓库提交问题

### 联系方式

- **项目地址**: https://github.com/rookie-littleblack/XpertCorpus
- **邮箱**: rookielittleblack@yeah.net
- **文档版本**: v0.1.0
- **最后更新**: 2025-08-13

---

**注意**: 本API文档随项目开发持续更新。标记为"🚧 开发中"的功能可能会有接口变更，请关注版本更新说明。 