# 数据可视化工具 (xvis)

`xpertcorpus.utils.xvis` 模块提供JSONL语料文件的可视化查看工具，支持多文件加载、字段搜索、导航浏览等功能。

## 模块概述

该模块基于 Streamlit 构建了一个交互式的Web界面，专门用于浏览和查看XpertCorpus项目中的JSONL格式语料文件。支持大文件处理、智能字段合并、实时搜索等功能。

## 核心类

### JSONLViewer

JSONL文件查看器的核心类，负责数据加载、搜索、导航等功能。

```python
class JSONLViewer:
    """JSONL file viewer for browsing corpus data."""
    
    def __init__(self):
        self.data: List[Dict] = []
        self.filtered_data: List[Dict] = []
        self.current_index: int = 0
        self.max_records: int = 1000
        self.total_records_in_files: int = 0
```

#### 主要方法

##### load_files()

加载JSONL文件到查看器中。

```python
def load_files(self, file_paths: List[str], max_records: int = 1000) -> bool:
    """
    Load JSONL files into the viewer.
    
    Args:
        file_paths: List of file paths to load
        max_records: Maximum total number of records to load
        
    Returns:
        bool: Whether the files were successfully loaded
    """
```

**功能特性：**
- 支持多文件批量加载
- 自动分配每个文件的最大记录数
- 统计源文件的真实总记录数
- 添加源文件标识符到每条记录
- 容错处理无效JSON行

##### search()

在指定字段中搜索关键词。

```python
def search(self, field: str, keyword: str) -> List[Dict]:
    """
    Search for keywords in the specified field.
    
    Args:
        field: Field name to search in
        keyword: Keyword to search for
        
    Returns:
        List[Dict]: List of matching records
    """
```

##### navigate()

导航到指定方向的记录。

```python
def navigate(self, direction: int) -> Optional[Dict]:
    """
    Navigate to a record in the specified direction.
    
    Args:
        direction: Direction to navigate (-1: previous, 1: next)
        
    Returns:
        Optional[Dict]: Current record after navigation
    """
```

##### get_available_fields()

获取所有可用的字段名。

```python
def get_available_fields(self) -> List[str]:
    """Get all available field names from loaded data."""
```

##### render_field()

以Markdown格式渲染字段内容。

```python
def render_field(self, field_name: str, field_value: Any) -> str:
    """
    Render field content in Markdown format.
    
    Args:
        field_name: Name of the field
        field_value: Value of the field
        
    Returns:
        str: Rendered HTML content
    """
```

## 主要函数

### main()

Streamlit应用的主入口函数。

```python
def main():
    """Main function - Streamlit application entry point."""
```

构建完整的Web界面，包括：
- 文件加载控制面板
- 数据统计显示
- 搜索和重置功能
- 记录导航和详情显示
- 智能字段合并

## 核心功能

### 1. 多文件加载

**支持特性：**
- 同时加载多个JSONL文件
- 自动统计源文件真实记录总数
- 按比例分配加载限制
- 显示加载进度和结果

**使用方式：**
```
文件路径输入框（每行一个）：
/path/to/file1.jsonl
/path/to/file2.jsonl
/path/to/file3.jsonl
```

### 2. 智能字段合并

**Tokens字段合并：**
- 自动识别 `field_name_tokens` 和 `field_name` 的配对关系
- 将tokens信息合并到对应字段的内容前方
- 格式：`[Tokens count] xxx\n\n---\n\noriginal_content`

**示例：**
```json
原始数据：
{
    "content": "这是文本内容...",
    "content_tokens": 1250
}

显示效果：
[Tokens count] 1250

---

这是文本内容...
```

### 3. 数据统计显示

**统计信息：**
- `📚 Total in Files`: 源文件中的实际总记录数
- `📄 Source Files`: 加载的源文件数量
- `🔍 Filtered`: 搜索过滤后的记录数

### 4. 高级导航

**导航控件：**
- `⬅️ Prev` / `➡️ Next`: 前后导航按钮
- `📍 位置信息`: 当前记录位置显示
- `Jump to` + `🎯 Go`: 快速跳转功能

**智能状态管理：**
- 自动同步导航状态
- 边界保护（首页禁用Prev，末页禁用Next）
- 实时页面刷新

### 5. 搜索功能

**搜索特性：**
- 字段选择下拉菜单
- 关键词模糊匹配
- 实时结果统计
- 一键重置功能

**控制按钮：**
- `🔍 Search`: 执行搜索（主按钮）
- `🔄 Reset`: 清空搜索，恢复全部数据（辅助按钮）

### 6. 界面优化

**视觉设计：**
- 隐藏Streamlit默认header和菜单
- 减少页面空白，优化布局
- 渐变背景的导航控制栏
- 两列式布局（控制面板 + 内容显示）

**响应式体验：**
- 实时状态同步
- 智能文件信息显示
- 倒序字段显示（重要字段优先）

## 使用方式

### 1. 作为Streamlit应用运行

```python
# 直接运行
python -m streamlit run xpertcorpus/utils/xvis.py

# 或使用入口脚本
python xpertcorpus/vis.py
```

### 2. 编程方式使用

```python
from xpertcorpus.utils.xvis import JSONLViewer

# 创建查看器实例
viewer = JSONLViewer()

# 加载文件
file_paths = ["/path/to/file1.jsonl", "/path/to/file2.jsonl"]
success = viewer.load_files(file_paths, max_records=1000)

# 获取可用字段
fields = viewer.get_available_fields()

# 搜索数据
results = viewer.search("content", "关键词")

# 导航浏览
current_record = viewer.navigate(1)  # 下一条
current_record = viewer.navigate(-1)  # 上一条
```

## 配置选项

### 环境要求

**必需依赖：**
```
streamlit>=1.28.0
pandas>=1.5.0
markdown>=3.4.0
```

**可选依赖：**
```
xpertcorpus.utils.xlogger  # 日志记录
```

### 界面配置

**页面设置：**
- 页面标题：XpertCorpus-Vis
- 布局模式：宽屏模式 (layout="wide")
- 侧边栏：默认折叠状态

**样式定制：**
- 导航栏渐变背景
- 隐藏Streamlit默认UI元素
- 自定义按钮样式和颜色

## 性能特性

### 内存优化

- **流式读取**：逐行读取JSONL文件，避免一次性加载
- **记录限制**：支持最大记录数限制，防止内存溢出
- **智能分配**：多文件按比例分配加载量

### 处理能力

- **大文件支持**：能够处理GB级别的JSONL文件
- **实时响应**：搜索和导航操作实时响应
- **错误恢复**：容错处理无效JSON行，不中断整体加载

## 最佳实践

### 1. 文件组织

```
建议的文件路径格式：
/data/corpus/
├── train_data.jsonl
├── valid_data.jsonl
└── test_data.jsonl
```

### 2. 数据格式

```json
推荐的JSONL记录格式：
{
    "id": "unique_identifier",
    "content": "主要文本内容",
    "content_tokens": 1250,
    "metadata": {...},
    "source": "data_source"
}
```

### 3. 使用建议

- **数据预览**：首次使用建议设置较小的max_records进行预览
- **字段命名**：使用 `fieldname_tokens` 格式命名token计数字段
- **文件大小**：单个文件建议不超过2GB，多个小文件比一个大文件更易处理

## 错误处理

### 常见错误

| 错误类型 | 原因 | 解决方案 |
|---------|------|----------|
| `FileNotFoundError` | 文件路径不存在 | 检查文件路径是否正确 |
| `json.JSONDecodeError` | 无效JSON格式 | 检查JSONL文件格式，工具会跳过无效行 |
| `MemoryError` | 数据量过大 | 减少max_records设置 |
| `ImportError` | 缺少依赖包 | 安装streamlit、pandas、markdown |

### 日志记录

工具集成了项目的xlogger系统，记录关键操作：

```python
# 文件加载日志
xlogger.info(f"Loaded {len(viewer.data)} records from {len(file_paths)} files")

# 搜索操作日志  
xlogger.info(f"Search completed: {len(results)} results for '{keyword}' in field '{field}'")

# 错误日志
xlogger.error("Failed to load JSONL files")
```

## 版本历史

- **v0.1.0** (2025-08-15)
  - 初始版本发布
  - 实现基础的JSONL文件可视化功能
  - 支持多文件加载和字段搜索
  - 添加智能导航和字段合并功能
  - 集成项目日志系统
  - 优化界面布局和用户体验

---

[返回工具层文档](README.md) | [返回 API 文档首页](../README.md) 