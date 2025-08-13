# 存储管理 (xstorage)

`xpertcorpus.utils.xstorage` 模块提供多格式文件读写和数据存储管理功能，支持压缩、验证、流式处理等高级特性。

## 模块概述

存储管理模块是 XpertCorpus 框架的核心基础设施，负责：
- 多格式数据文件的读写操作
- 数据压缩和完整性验证
- 大文件的流式处理
- 存储缓存和元数据管理
- 统一的存储接口抽象

## 核心类

### XpertCorpusStorage (抽象基类)

数据存储的抽象基类，定义了统一的存储接口。

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator

class XpertCorpusStorage(ABC):
    """XpertCorpus 存储抽象基类"""
    
    @abstractmethod
    def read(self, input_file: str, **kwargs) -> Iterator[Dict[str, Any]]:
        """读取数据文件"""
        pass
    
    @abstractmethod  
    def write(self, data: Iterator[Dict[str, Any]], output_file: str, **kwargs) -> bool:
        """写入数据文件"""
        pass
    
    @abstractmethod
    def step(self) -> 'XpertCorpusStorage':
        """步进到下一步存储状态"""
        pass
```

### FileStorage (文件存储实现)

`FileStorage` 是 `XpertCorpusStorage` 的具体实现，提供完整的文件存储功能。

#### 构造函数

```python
def __init__(
    self,
    output_dir: str = "./output",
    output_format: str = "jsonl",
    step_name: str = "corpusflow_cache",
    enable_compression: bool = False,
    enable_validation: bool = True,
    cache_cleanup_threshold: int = 100,
    stream_chunk_size: int = 1000,
    max_workers: int = 1
)
```

**参数：**
- `output_dir`: 输出目录路径
- `output_format`: 输出格式 (`jsonl`, `csv`, `parquet`, `pickle`)
- `step_name`: 步骤名称（用于文件命名）
- `enable_compression`: 是否启用 gzip 压缩
- `enable_validation`: 是否启用完整性验证
- `cache_cleanup_threshold`: 缓存清理阈值
- `stream_chunk_size`: 流式处理块大小
- `max_workers`: 最大工作线程数

#### 核心方法

##### read()

读取数据文件，支持多种格式和流式处理。

```python
def read(
    self, 
    input_file: str, 
    limit: int = 0, 
    start_idx: int = 0,
    **kwargs
) -> Iterator[Dict[str, Any]]
```

**参数：**
- `input_file`: 输入文件路径
- `limit`: 读取行数限制（0 表示无限制）
- `start_idx`: 起始索引
- `**kwargs`: 其他参数

**返回：** 数据迭代器

**使用示例：**
```python
storage = FileStorage(output_dir="./data")

# 读取 JSONL 文件
for record in storage.read("input.jsonl", limit=1000):
    print(record)

# 读取压缩文件
for record in storage.read("input.jsonl.gz"):
    print(record)
```

##### write()

写入数据到文件，支持压缩和验证。

```python
def write(
    self, 
    data: Union[Iterator[Dict[str, Any]], List[Dict[str, Any]]], 
    output_file: str,
    **kwargs
) -> bool
```

**参数：**
- `data`: 数据（迭代器或列表）
- `output_file`: 输出文件路径
- `**kwargs`: 其他参数

**返回：** 写入是否成功

**使用示例：**
```python
data = [{"text": "Hello"}, {"text": "World"}]
success = storage.write(data, "output.jsonl")

# 启用压缩
storage_compressed = FileStorage(enable_compression=True)
success = storage_compressed.write(data, "output.jsonl")  # 自动生成 .gz 文件
```

##### step()

步进到下一步存储状态，用于管道式处理。

```python
def step(self) -> 'FileStorage'
```

**返回：** 新的存储实例（步骤号递增）

**使用示例：**
```python
storage = FileStorage(step_name="process")

# 当前步骤：process_step_0.jsonl
storage_step1 = storage.step()  # process_step_1.jsonl  
storage_step2 = storage_step1.step()  # process_step_2.jsonl
```

#### 高级功能

##### validate_integrity()

验证文件完整性（MD5 校验）。

```python
def validate_integrity(self, file_path: str) -> bool
```

**使用示例：**
```python
if storage.validate_integrity("data.jsonl"):
    print("文件完整性验证通过")
```

##### get_file_info()

获取文件元数据信息。

```python
def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]
```

**返回信息：**
- 文件大小
- 创建时间
- MD5 哈希值
- 记录数量
- 格式信息

**使用示例：**
```python
info = storage.get_file_info("data.jsonl")
print(f"文件大小: {info['size']} bytes")
print(f"记录数: {info['record_count']}")
```

##### cleanup_cache()

清理存储缓存和临时文件。

```python
def cleanup_cache(self, max_age_days: int = 7) -> Dict[str, Any]
```

**使用示例：**
```python
cleanup_result = storage.cleanup_cache(max_age_days=3)
print(f"清理了 {cleanup_result['files_removed']} 个文件")
```

##### get_storage_stats()

获取存储统计信息。

```python
def get_storage_stats(self) -> Dict[str, Any]
```

**返回信息：**
- 总文件数
- 总存储大小
- 各格式文件统计
- 缓存使用情况

## 支持的格式

### JSONL (默认)

```python
# 读取
for record in storage.read("data.jsonl"):
    print(record["text"])

# 写入
data = [{"text": "Hello"}, {"text": "World"}]
storage.write(data, "output.jsonl")
```

### CSV

```python
storage = FileStorage(output_format="csv")

# 自动检测 CSV 列
storage.write(data, "output.csv")
```

### Parquet

```python
storage = FileStorage(output_format="parquet")

# 高性能列式存储
storage.write(data, "output.parquet")
```

### Pickle

```python
storage = FileStorage(output_format="pickle")

# Python 对象序列化
storage.write(data, "output.pkl")
```

## 压缩支持

### 启用压缩

```python
# 创建时启用
storage = FileStorage(enable_compression=True)

# 自动处理压缩文件
storage.write(data, "output.jsonl")  # 生成 output.jsonl.gz

# 自动解压读取
for record in storage.read("input.jsonl.gz"):
    print(record)
```

### 压缩级别控制

```python
# 在写入时指定压缩级别
storage.write(data, "output.jsonl", compression_level=6)
```

## 流式处理

### 大文件处理

```python
# 设置块大小
storage = FileStorage(stream_chunk_size=5000)

# 流式读取大文件
for chunk in storage.read("large_file.jsonl"):
    # 逐块处理，避免内存溢出
    process_chunk(chunk)
```

### 生成器写入

```python
def data_generator():
    for i in range(1000000):
        yield {"id": i, "text": f"Record {i}"}

# 流式写入
storage.write(data_generator(), "large_output.jsonl")
```

## 完整性验证

### MD5 校验

```python
# 启用验证
storage = FileStorage(enable_validation=True)

# 写入时自动计算哈希
storage.write(data, "output.jsonl")

# 读取时验证完整性
if storage.validate_integrity("output.jsonl"):
    for record in storage.read("output.jsonl"):
        process_record(record)
```

### 元数据管理

```python
# 获取文件元数据
metadata = storage.get_file_info("data.jsonl")
print(f"MD5: {metadata['md5_hash']}")
print(f"记录数: {metadata['record_count']}")
```

## 错误处理

### 异常处理

存储模块集成了 `xerror_handler`，提供robust的错误处理：

```python
from xpertcorpus.utils.xstorage import FileStorage

storage = FileStorage()

try:
    data = list(storage.read("nonexistent.jsonl"))
except FileNotFoundError:
    print("文件不存在")
except Exception as e:
    print(f"读取错误: {e}")
```

### 重试机制

```python
# 启用自动重试
@safe_execute(retry_enabled=True, max_retries=3)
def write_data():
    return storage.write(data, "output.jsonl")

result = write_data()
```

## 缓存管理

### 自动清理

```python
# 设置清理阈值
storage = FileStorage(cache_cleanup_threshold=50)

# 当缓存文件超过阈值时自动清理
```

### 手动清理

```python
# 清理 7 天前的缓存
cleanup_result = storage.cleanup_cache(max_age_days=7)

print(f"清理文件数: {cleanup_result['files_removed']}")
print(f"释放空间: {cleanup_result['space_freed']} MB")
```

## 性能优化

### 多线程支持

```python
# 启用多线程处理
storage = FileStorage(max_workers=4)

# 自动并行处理大文件
storage.write(large_data, "output.jsonl")
```

### 批量操作

```python
# 批量读取
batch_size = 1000
for i, record in enumerate(storage.read("large_file.jsonl")):
    if i % batch_size == 0:
        # 每 1000 条记录处理一次
        process_batch(batch)
        batch = []
    batch.append(record)
```

## 使用模式

### 基础使用

```python
from xpertcorpus.utils.xstorage import FileStorage

# 创建存储实例
storage = FileStorage(
    output_dir="./data",
    output_format="jsonl",
    enable_compression=True
)

# 读取数据
data = list(storage.read("input.jsonl"))

# 处理数据
processed_data = [process_record(record) for record in data]

# 写入结果
storage.write(processed_data, "output.jsonl")
```

### 管道式处理

```python
# 初始存储
storage = FileStorage(step_name="pipeline")

# 第一步处理
step1_storage = storage.step()
step1_storage.write(step1_data, f"step_1.jsonl")

# 第二步处理  
step2_storage = step1_storage.step()
step2_data = list(step1_storage.read(f"step_1.jsonl"))
step2_storage.write(process_step2(step2_data), f"step_2.jsonl")
```

### 配置驱动

```python
config = {
    "storage": {
        "output_dir": "./output",
        "format": "parquet",
        "compression": True,
        "validation": True,
        "chunk_size": 2000
    }
}

storage = FileStorage(
    output_dir=config["storage"]["output_dir"],
    output_format=config["storage"]["format"],
    enable_compression=config["storage"]["compression"],
    enable_validation=config["storage"]["validation"],
    stream_chunk_size=config["storage"]["chunk_size"]
)
```

## 最佳实践

### 1. 格式选择

- **JSONL**: 文本数据，易于调试
- **Parquet**: 大数据集，高性能读写
- **CSV**: 表格数据，兼容性好
- **Pickle**: Python 对象，最快序列化

### 2. 压缩策略

```python
# 存储空间敏感场景
storage = FileStorage(enable_compression=True)

# 性能敏感场景
storage = FileStorage(enable_compression=False)
```

### 3. 内存管理

```python
# 处理大文件时使用流式读取
def process_large_file(file_path):
    storage = FileStorage(stream_chunk_size=1000)
    
    for record in storage.read(file_path):
        # 逐条处理，避免内存溢出
        yield process_record(record)
```

### 4. 错误恢复

```python
# 启用验证确保数据完整性
storage = FileStorage(
    enable_validation=True,
    cache_cleanup_threshold=50
)

# 验证文件完整性
if not storage.validate_integrity("critical_data.jsonl"):
    # 从备份恢复
    restore_from_backup()
```

## 注意事项

### 1. 文件路径

- 支持相对路径和绝对路径
- 自动创建输出目录
- 压缩文件自动添加 `.gz` 后缀

### 2. 内存使用

- 流式处理避免大文件内存溢出
- 适当设置 `stream_chunk_size`
- 及时清理缓存文件

### 3. 线程安全

- `FileStorage` 支持多线程读写
- 元数据操作使用锁保护
- 避免同时写入同一文件

### 4. 性能考虑

- Parquet 格式适合大数据集
- 压缩权衡存储空间和CPU消耗
- 合理设置工作线程数量

---

**更多信息：**
- [错误处理 (xerror_handler)](xerror_handler.md)
- [日志系统 (xlogger)](xlogger.md)
- [框架系统 (xframework)](../others/xframework.md) 