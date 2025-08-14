# XpertCorpus 项目文档

欢迎来到 XpertCorpus 项目文档！本目录包含了项目的完整文档体系。

## 文档结构

```
docs/
├── README.md                   # 文档导航（本文件）
├── api/                        # API 参考文档
│   ├── README.md              # API 文档导航
│   ├── utils/                 # 工具层 API 文档
│   ├── others/                # 基础设施层 API 文档
│   ├── microops/              # 微算子层 API 文档
│   ├── operators/             # 算子层 API 文档
│   ├── pipelines/             # 管道层 API 文档
│   └── frameworks/            # 框架层 API 文档
├── tutorials/                  # 教程文档
│   ├── README.md              # 教程导航
│   ├── getting-started/       # 快速入门
│   ├── basic-usage/           # 基础使用
│   ├── advanced-usage/        # 高级使用
│   └── best-practices/        # 最佳实践
├── examples/                   # 示例文档
│   ├── README.md              # 示例导航
│   ├── simple-examples/       # 简单示例
│   ├── complex-pipelines/     # 复杂管道示例
│   └── custom-development/    # 自定义开发示例
├── architecture/               # 架构文档
│   ├── README.md              # 架构概览
│   ├── design-principles.md   # 设计原则
│   ├── four-layer-arch.md     # 四层架构详解
│   ├── registry-pattern.md    # 注册器模式
│   └── data-flow.md          # 数据流设计
├── development/                # 开发文档
│   ├── README.md              # 开发指南
│   ├── contributing.md        # 贡献指南
│   ├── coding-standards.md    # 编码规范
│   ├── testing.md            # 测试指南
│   └── deployment.md         # 部署指南
└── reference/                  # 参考文档
    ├── README.md              # 参考导航
    ├── configuration.md       # 配置参考
    ├── error-codes.md         # 错误代码
    ├── performance.md         # 性能优化
    └── faq.md                # 常见问题
```

## 快速导航

### 🚀 新用户
- [快速入门教程](tutorials/getting-started/README.md)
- [基础使用指南](tutorials/basic-usage/README.md)
- [简单示例](examples/simple-examples/README.md)

### 📚 API 文档
- [工具层 API](api/utils/README.md) - 日志、配置、存储、异常处理等
- [基础设施层 API](api/others/README.md) - 框架基类、算子基类、注册系统等
- [微算子层 API](api/microops/README.md) - 原子级数据处理操作
- [算子层 API](api/operators/README.md) - 复合数据处理操作
- [管道层 API](api/pipelines/README.md) - 数据处理流水线
- [框架层 API](api/frameworks/README.md) - 端到端业务框架

### 🏗️ 架构理解
- [四层架构设计](architecture/four-layer-arch.md)
- [设计原则](architecture/design-principles.md)
- [数据流设计](architecture/data-flow.md)

### 🔧 开发者
- [开发指南](development/README.md)
- [编码规范](development/coding-standards.md)
- [贡献指南](development/contributing.md)

### 📖 参考资料
- [配置参考](reference/configuration.md)
- [错误代码参考](reference/error-codes.md)
- [常见问题](reference/faq.md)

## 文档版本

当前文档版本：v0.1.0  
对应项目版本：v0.1.0  
最后更新：2025-08-13

## 贡献文档

如果您发现文档中有错误或需要改进的地方，欢迎提交 Issue 或 Pull Request。详见[贡献指南](development/contributing.md)。

---

**XpertCorpus** - 轻量级大模型语料构建端到端框架  
项目地址：https://github.com/rookie-littleblack/XpertCorpus 