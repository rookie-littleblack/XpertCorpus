# 存储管理 (xstorage)

`xpertcorpus.utils.xstorage` 模块提供多格式文件读写和数据存储管理功能。

## 模块概述

存储管理模块为 XpertCorpus 提供统一的数据存储接口，支持多种文件格式、数据压缩、流式处理和完整性验证。

## 核心抽象类

### XpertCorpusStorage

数据存储的抽象基类，定义了统一的存储接口。

```python
class XpertCorpusStorage(ABC):
    """Abstract base class for data storage."""

    @abstractmethod
    def read(self, output_type: Literal["dataframe", "dict", "iterator"]) -> Any:
        """读取数据"""
        pass
    
    @abstractmethod
    def write(self, data: Union[pd.DataFrame, List[Dict], Dict]) -> str:
        """写入数据"""
        pass
    
    @abstractmethod
    def validate_integrity(self, file_path: str) -> bool:
        """验证数据完整性"""
        pass
```

## 核心实现类

### FileStorage

文件系统存储的具体实现，支持多种高级功能。

#### 构造函数

```python
def __init__(self, 
             first_entry_file_name: str,
             cache_path: str = "./output",
             file_name_prefix: str = "corpusflow_cache_step",
             cache_type: Literal["json", "jsonl", "csv", "parquet", "pickle"] = "jsonl",
             enable_compression: bool = False,
             chunk_size: int = 10000,
             validate_on_write: bool = True):
    """
    初始化 FileStorage。
    
    Args:
        first_entry_file_name: 初始输入文件路径
        cache_path: 缓存文件目录
        file_name_prefix: 缓存文件名前缀
        cache_type: 缓存文件格式
        enable_compression: 是否启用压缩
        chunk_size: 流式处理的块大小
        validate_on_write: 写入后是否验证
    """
```

#### 核心方法

```python
def step(self) -> 'FileStorage':
    """步进到下一个处理步骤"""
    
def reset(self) -> 'FileStorage':
    """重置到初始步骤"""
    
def read(self, output_type: Literal["dataframe", "dict", "iterator"] = "dataframe") -> Any:
    """读取当前步骤的数据"""
    
def write(self, data: Union[pd.DataFrame, List[Dict], Dict]) -> str:
    """写入数据到下一步"""
    
def validate_integrity(self, file_path: str) -> bool:
    """验证文件完整性"""
```

#### 信息和管理方法

```python
def get_file_info(self, step: Optional[int] = None) -> Dict:
    """获取指定步骤的文件信息"""
    
def cleanup_cache(self, keep_steps: int = 1) -> None:
    """清理旧的缓存文件"""
    
def get_storage_stats(self) -> Dict:
    """获取存储统计信息"""
```

## 使用示例

### 基础使用

```python
from xpertcorpus.utils.xstorage import FileStorage

# 初始化存储，指定初始输入文件
storage = FileStorage(
    first_entry_file_name="data/input.jsonl",
    cache_path="./output_data",
    enable_compression=True
)

# 步进到第一步
storage.step()

# 读取第一步的输入数据 (input.jsonl)
# 注意：read() 读取的是 self.operator_step 的数据
# 由于我们刚从-1步进到0，所以这里读取的是第0步的文件
input_data = storage.read(output_type="dataframe")

# 假设我们处理了数据
processed_data = input_data.head(10)

# 写入处理结果到下一步（第1步）
output_file = storage.write(processed_data)
print(f"数据已写入到: {output_file}")

# 步进到第二步
storage.step()

# 读取上一步（第1步）的结果
step1_result = storage.read(output_type="dict")
print(f"读取到 {len(step1_result)} 条记录")
```

### 多格式支持

```python
# 使用 Parquet 格式进行缓存
storage = FileStorage(
    first_entry_file_name="data/input.jsonl",
    cache_type="parquet"
)
```

支持的格式：`json`, `jsonl`, `csv`, `parquet`, `pickle`

### 流式处理

```python
# 读取数据为迭代器
for record in storage.read(output_type="iterator"):
    # 逐条处理记录，避免内存占用过高
    process_record(record)
```

### 完整性验证

```python
# 写入时会自动计算哈希并存储元数据
storage.write(my_data)

# 手动验证文件
is_valid = storage.validate_integrity("path/to/file.jsonl")
if is_valid:
    print("文件完整性验证通过")
```

### 缓存管理

```python
# 清理旧的缓存文件，只保留最近的2个步骤
storage.cleanup_cache(keep_steps=2)

# 获取存储统计信息
stats = storage.get_storage_stats()
print(f"当前步骤: {stats['current_step']}")
print(f"总文件数: {stats['total_files']}")
```

## 内置特性

### 多格式支持
支持 JSON, JSONL, CSV, Parquet, Pickle 格式的读写。

### 压缩
支持 `gzip` 压缩，通过 `enable_compression` 参数控制。

### 流式处理
通过将 `output_type` 设置为 `iterator` 来支持大文件的流式读取。

### 完整性验证
写入文件时可自动计算并存储 MD5 哈希值，用于后续验证。

### 错误处理
集成了 `xerror_handler`，提供健壮的错误处理和重试机制。

### 管道式处理
通过 `step()` 和 `reset()` 方法支持多步骤的数据处理管道。

## 相关文档

- [异常处理 (xerror_handler)](xerror_handler.md)
- [日志系统 (xlogger)](xlogger.md)

---

[返回 Utils 模块首页](README.md) | [返回 API 文档首页](../README.md) 