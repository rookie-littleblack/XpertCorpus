# XpertCorpus API 参考文档

本目录包含 XpertCorpus 框架所有模块的详细 API 文档。

## 架构层次

XpertCorpus 采用四层架构设计，从底层到顶层分别是：

### 🔧 [工具层 (Utils)](utils/README.md)
基础工具和服务模块，为上层提供支撑功能。

- **[异常处理 (xerror_handler)](utils/xerror_handler.md)** - 统一异常处理、重试机制、错误报告
- **[日志系统 (xlogger)](utils/xlogger.md)** - 结构化日志记录
- **[配置管理 (xconfig)](utils/xconfig.md)** - YAML 配置加载和管理
- **[存储管理 (xstorage)](utils/xstorage.md)** - 多格式文件读写
- **[工具函数 (xutils)](utils/xutils.md)** - 令牌计数等通用工具

### 🔩 [基础设施层 (Others)](others/README.md)
核心抽象基类和基础设施组件，为整个框架提供架构支撑。

- **[框架基础系统 (xframework)](others/xframework.md)** - 框架抽象基类和生命周期管理
- **[算子基类 (xoperator)](others/xoperator.md)** - 算子抽象基类和管理功能
- **[注册系统 (xregistry)](others/xregistry.md)** - 组件注册和动态加载管理

### ⚛️ [微操作层 (Microops)](microops/README.md)
原子级数据处理操作，功能单一且可复用。

- **文本清洗类** - HTML 标签、URL、邮箱、特殊字符清理等
- **文本标准化类** - Unicode、标点符号、编码标准化等  
- **语言处理类** - 语言检测、过滤、音译转换等
- **内容过滤类** - 长短文本、重复内容过滤等
- **格式转换类** - 大小写、引号、破折号转换等
- **数据验证类** - UTF-8、JSON、Markdown 验证等
- **安全隐私类** - PII 清理、敏感数据脱敏等

### 🎯 [算子层 (Operators)](operators/README.md)
复合数据处理操作，组合多个微操作实现复杂逻辑。

- **[文本分割器 (xsplitter)](operators/xsplitter.md)** - 多策略文本分割
- **[LLM 清洗器 (xllmcleaner)](operators/xllmcleaner.md)** - 基于大模型的文本清洗
- **[质量评估器 (xquality_assessor)](operators/xquality_assessor.md)** - 数据质量评估
- **[内容过滤器 (xcontent_filter)](operators/xcontent_filter.md)** - 智能内容过滤
- **[格式转换器 (xformat_converter)](operators/xformat_converter.md)** - 训练格式转换

### 🔄 [管道层 (Pipelines)](pipelines/README.md)
数据处理流水线，组合多个算子形成完整的处理流程。

- **[基础清洗管道 (xcleaning_pipe)](pipelines/xcleaning_pipe.md)** - 基础文本清洗流程
- **[深度清洗管道 (xdeep_cleaning_pipe)](pipelines/xdeep_cleaning_pipe.md)** - 全方位深度清洗
- **[质量过滤管道 (xquality_filter_pipe)](pipelines/xquality_filter_pipe.md)** - 数据质量控制
- **[去重管道 (xdeduplication_pipe)](pipelines/xdeduplication_pipe.md)** - 多层次数据去重

### 🏗️ [框架层 (Frameworks)](frameworks/README.md)
端到端业务框架，提供完整的数据生成解决方案。

- **[预训练框架 (xframe_pt)](frameworks/xframe_pt.md)** - 预训练数据生成
- **[监督微调框架 (xframe_sft)](frameworks/xframe_sft.md)** - SFT 数据生成
- **[思维链框架 (xframe_cot)](frameworks/xframe_cot.md)** - CoT 数据生成
- **[多模态框架 (xframe_multimodal)](frameworks/xframe_multimodal.md)** - 多模态数据处理

## 使用指南

### 快速查找
- 如果您需要基础功能（日志、配置、异常处理等），请查看 [工具层](utils/README.md)
- 如果您需要简单的数据处理操作，请查看 [微操作层](microops/README.md)
- 如果您需要复杂的数据处理逻辑，请查看 [算子层](operators/README.md)
- 如果您需要完整的处理流程，请查看 [管道层](pipelines/README.md)
- 如果您需要端到端的解决方案，请查看 [框架层](frameworks/README.md)

### 文档约定
- **类名** 使用 PascalCase
- **函数名** 使用 snake_case
- **参数** 包含类型注解和详细说明
- **示例** 提供实际的代码片段
- **异常** 列出可能抛出的异常类型

### 版本信息
- API 版本：v0.1.0
- 最后更新：2025-08-13
- Python 版本要求：3.10+

---

**提示**：建议结合[架构文档](../architecture/README.md)和[教程](../tutorials/README.md)一起阅读，以更好地理解各层之间的关系和使用方式。 