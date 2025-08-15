# 可视化工具启动器 (vis.py)

`xpertcorpus/vis.py` 是数据可视化工具的入口脚本，提供便捷的启动方式来运行JSONL语料可视化界面。

## 脚本概述

该脚本是 [xvis 数据可视化工具](utils/xvis.md) 的命令行启动器，负责检查依赖、配置Streamlit参数并启动Web应用。

## 主要功能

### 依赖检查
- 自动检测 `streamlit` 是否安装
- 提供明确的安装指引
- 验证 `xvis.py` 文件路径

### 启动配置
- 默认服务器地址：`0.0.0.0`（支持外部访问）
- 默认端口：`8501`
- 自动打开浏览器

### 用户指引
- 显示详细的使用说明
- 提供工具路径信息
- 集成日志记录

## 使用方式

### 基本启动

```bash
# 在项目根目录下执行
python xpertcorpus/vis.py
```

### 启动过程
1. **检查依赖**：验证streamlit等必需包
2. **路径验证**：确认xvis.py文件存在
3. **显示指引**：输出使用说明
4. **启动服务**：运行Streamlit应用
5. **打开浏览器**：自动访问 http://localhost:8501

## 输出信息

### 启动提示
```
🚀 Starting JSONL corpus visualization tool...
📍 Tool path: /path/to/xpertcorpus/utils/xvis.py

📝 Usage Instructions:
1. Enter full paths to JSONL files on the left (one per line)
2. Set maximum number of records (default: 1000)
3. Click 'Load Files'
4. Use search and navigation features to browse data

🌐 Browser will open automatically. If not, please visit the displayed URL manually
--------------------------------------------------
```

### 错误处理
```bash
# 缺少依赖时
❌ Error: Streamlit not installed
Please run: pip install streamlit pandas markdown

# 文件路径错误时
Error: Cannot find xvis.py file: /path/to/file
```

## 配置选项

### 服务器配置
```python
# 默认启动参数
--server.address 0.0.0.0      # 允许外部访问
--server.port 8501             # 默认端口
--browser.serverAddress 0.0.0.0  # 浏览器访问地址
```

### 自定义配置
如需修改配置，可直接编辑脚本中的启动参数：

```python
subprocess.run([
    sys.executable, "-m", "streamlit", "run", 
    str(xvis_path),
    "--server.address", "localhost",  # 仅本地访问
    "--server.port", "8502",          # 自定义端口
    "--browser.serverAddress", "localhost"
], check=True)
```

## 网络访问

### 本地访问
- URL: http://localhost:8501
- 适用于个人开发和调试

### 远程访问
- URL: http://[服务器IP]:8501
- 支持团队协作和远程查看
- 默认配置支持外部访问

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `ModuleNotFoundError: streamlit` | 未安装streamlit | `pip install streamlit pandas markdown` |
| `Address already in use` | 端口8501被占用 | 修改端口或关闭占用进程 |
| `Permission denied` | 权限不足 | 使用管理员权限运行 |
| `Browser doesn't open` | 浏览器配置问题 | 手动访问显示的URL |

### 日志记录
脚本集成了xlogger系统，记录关键操作：

```python
# 启动日志
xlogger.info("🚀 Starting JSONL corpus visualization tool...")
xlogger.info(f"📍 Tool path: {xvis_path}")

# 依赖检查日志
xlogger.info("Streamlit dependency check passed")

# 错误日志
xlogger.error("Failed to load JSONL files")
```

## 与xvis.py的关系

```
vis.py (启动器)
    ↓
启动 streamlit run xpertcorpus/utils/xvis.py
    ↓
加载 JSONLViewer 类和 main() 函数
    ↓
显示 Web 界面
```

### 直接调用对比

| 方式 | 命令 | 优势 |
|------|------|------|
| **启动器** | `python xpertcorpus/vis.py` | 依赖检查、用户指引、日志记录 |
| **直接调用** | `streamlit run xpertcorpus/utils/xvis.py` | 更直接、参数可控 |

## 开发和部署

### 开发环境
```bash
# 本地开发
python xpertcorpus/vis.py
```

### 生产部署
```bash
# 服务器部署（后台运行）
nohup python xpertcorpus/vis.py &

# Docker部署
docker run -p 8501:8501 xpertcorpus python vis.py

# 云平台部署
# 支持 Streamlit Cloud、Heroku、AWS 等平台
```

## 最佳实践

### 1. 依赖管理
确保安装完整依赖：
```bash
pip install streamlit>=1.28.0 pandas>=1.5.0 markdown>=3.4.0
```

### 2. 网络配置
- **开发环境**：使用默认配置（localhost:8501）
- **团队环境**：修改为具体IP地址
- **生产环境**：配置反向代理和SSL

### 3. 性能优化
- 限制max_records避免内存溢出
- 使用多个小文件替代单个大文件
- 定期清理浏览器缓存

## 版本历史

- **v0.1.0** (2025-08-15)
  - 初始版本发布
  - 实现基础的启动器功能
  - 添加依赖检查和用户指引
  - 集成xlogger日志系统
  - 支持外部访问配置

---

[返回xvis文档](xvis.md) | [返回工具层文档](README.md) | [返回 API 文档首页](../README.md) 