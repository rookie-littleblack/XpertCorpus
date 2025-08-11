# XpertCorpus - 轻量级大模型语料处理工作流

## 框架说明

XpertCorpus 是一款轻量级的用于大模型语料构建的端到端框架。

## 快速使用

```bash
# 拉取项目代码
git clone https://github.com/rookie-littleblack/XpertCorpus.git
cd XpertCorpus

# 创建虚拟环境
conda create -n xpertcorpus -y python=3.10

# 激活虚拟环境
conda activate xpertcorpus

# 安装依赖
pip install -r requirements

# 基于实例数据运行脚本
python -m xpertcorpus.main
```

## 鸣谢

本项目受 [DataFlow](https://github.com/OpenDCAI/DataFlow) 项目的启发而来，并参考了其部分设计思路和实现方式，在此表示感谢。