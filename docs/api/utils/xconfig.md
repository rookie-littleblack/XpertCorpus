# 配置管理 (xconfig)

`xpertcorpus.utils.xconfig` 模块提供YAML配置文件加载和管理功能，支持配置验证、环境变量支持和热加载机制。

## 模块概述

配置管理模块是 XpertCorpus 框架的核心基础设施，负责：
- YAML配置文件的解析和加载
- 配置参数的验证和默认值处理
- 环境变量的集成和覆盖
- 配置文件的热加载和更新
- 多层级配置的合并和管理

## 核心类

### XConfigLoader (配置加载器)

主要的配置加载和管理类，提供完整的配置文件处理功能。

#### 构造函数

```python
def __init__(
    self,
    config_file: str = None,
    auto_reload: bool = False,
    env_prefix: str = "XPERTCORPUS_",
    encoding: str = "utf-8"
)
```

**参数：**
- `config_file`: 配置文件路径
- `auto_reload`: 是否启用自动重载
- `env_prefix`: 环境变量前缀
- `encoding`: 文件编码

#### 主要方法

##### load_config()

加载配置文件并返回配置字典。

```python
def load_config(
    self,
    config_file: str = None,
    merge_env: bool = True,
    validate: bool = True
) -> Dict[str, Any]
```

**参数：**
- `config_file`: 配置文件路径（可选）
- `merge_env`: 是否合并环境变量
- `validate`: 是否执行配置验证

**返回：** 配置字典

**使用示例：**
```python
from xpertcorpus.utils.xconfig import XConfigLoader

# 基础使用
loader = XConfigLoader("config/app.yaml")
config = loader.load_config()

# 高级选项
config = loader.load_config(
    merge_env=True,    # 合并环境变量
    validate=True      # 验证配置
)

print(f"数据库主机: {config['database']['host']}")
print(f"日志级别: {config['logging']['level']}")
```

##### get()

获取指定路径的配置值。

```python
def get(
    self,
    key_path: str,
    default: Any = None,
    config: Dict[str, Any] = None
) -> Any
```

**参数：**
- `key_path`: 配置键路径（支持点号分隔）
- `default`: 默认值
- `config`: 配置字典（可选，使用当前配置）

**使用示例：**
```python
loader = XConfigLoader("config.yaml")

# 获取嵌套配置
database_host = loader.get("database.host", default="localhost")
log_level = loader.get("logging.level", default="INFO")
max_workers = loader.get("processing.max_workers", default=4)

# 获取数组元素
first_model = loader.get("models.0.name")
```

##### set()

设置指定路径的配置值。

```python
def set(
    self,
    key_path: str,
    value: Any,
    config: Dict[str, Any] = None
) -> None
```

**使用示例：**
```python
loader = XConfigLoader()

# 设置配置值
loader.set("database.host", "new-host.example.com")
loader.set("processing.batch_size", 256)
loader.set("features.enable_gpu", True)
```

##### validate_config()

验证配置的有效性。

```python
def validate_config(
    self,
    config: Dict[str, Any],
    schema: Dict[str, Any] = None
) -> Tuple[bool, List[str]]
```

**返回：** (是否有效, 错误列表)

##### reload_config()

重新加载配置文件。

```python
def reload_config(self) -> Dict[str, Any]
```

##### save_config()

保存配置到文件。

```python
def save_config(
    self,
    config: Dict[str, Any],
    output_file: str = None
) -> bool
```

## 使用模式

### 基础配置加载

```yaml
# config/app.yaml
application:
  name: "XpertCorpus"
  version: "0.1.0"
  debug: false

database:
  host: "localhost"
  port: 5432
  name: "xpertcorpus"
  username: "user"
  password: "password"

logging:
  level: "INFO"
  file: "logs/app.log"
  max_size: "100MB"
  backup_count: 5

processing:
  max_workers: 4
  batch_size: 128
  timeout: 300

models:
  - name: "gpt-3.5-turbo"
    provider: "openai"
    max_tokens: 4096
  - name: "claude-3"
    provider: "anthropic"
    max_tokens: 8192
```

```python
from xpertcorpus.utils.xconfig import XConfigLoader

# 加载配置
loader = XConfigLoader("config/app.yaml")
config = loader.load_config()

# 使用配置
app_name = config['application']['name']
db_config = config['database']
max_workers = config['processing']['max_workers']

print(f"应用: {app_name}")
print(f"数据库: {db_config['host']}:{db_config['port']}")
print(f"工作线程: {max_workers}")
```

### 环境变量集成

```python
import os

# 设置环境变量（覆盖配置文件）
os.environ['XPERTCORPUS_DATABASE_HOST'] = 'prod-db.example.com'
os.environ['XPERTCORPUS_DATABASE_PORT'] = '5433'
os.environ['XPERTCORPUS_PROCESSING_MAX_WORKERS'] = '8'

# 加载配置（环境变量会覆盖文件配置）
loader = XConfigLoader("config/app.yaml", env_prefix="XPERTCORPUS_")
config = loader.load_config(merge_env=True)

print(f"数据库主机: {config['database']['host']}")  # prod-db.example.com
print(f"数据库端口: {config['database']['port']}")  # 5433
print(f"最大工作线程: {config['processing']['max_workers']}")  # 8
```

### 配置路径访问

```python
loader = XConfigLoader("config.yaml")

# 点号路径访问
app_name = loader.get("application.name")
db_host = loader.get("database.host", default="localhost")
log_level = loader.get("logging.level", default="INFO")

# 数组访问
first_model = loader.get("models.0.name")
second_model_tokens = loader.get("models.1.max_tokens")

# 复杂路径
nested_value = loader.get("complex.nested.deep.value", default="default")

# 设置值
loader.set("application.debug", True)
loader.set("processing.batch_size", 256)
```

### 配置验证

```python
# 定义配置模式
config_schema = {
    "application": {
        "name": {"type": "string", "required": True},
        "version": {"type": "string", "required": True},
        "debug": {"type": "boolean", "default": False}
    },
    "database": {
        "host": {"type": "string", "required": True},
        "port": {"type": "integer", "min": 1, "max": 65535},
        "name": {"type": "string", "required": True}
    },
    "processing": {
        "max_workers": {"type": "integer", "min": 1, "max": 32, "default": 4},
        "batch_size": {"type": "integer", "min": 1, "default": 128}
    }
}

# 验证配置
loader = XConfigLoader("config.yaml")
config = loader.load_config()

is_valid, errors = loader.validate_config(config, config_schema)

if not is_valid:
    print("配置验证失败:")
    for error in errors:
        print(f"  - {error}")
else:
    print("配置验证通过")
```

### 多环境配置

```python
import os

class EnvironmentConfigLoader:
    """多环境配置加载器"""
    
    def __init__(self, base_config_dir="config"):
        self.base_dir = base_config_dir
        self.environment = os.getenv("ENVIRONMENT", "development")
    
    def load_config(self):
        """加载环境特定的配置"""
        
        # 加载基础配置
        base_config_file = os.path.join(self.base_dir, "base.yaml")
        loader = XConfigLoader(base_config_file)
        config = loader.load_config()
        
        # 加载环境特定配置
        env_config_file = os.path.join(self.base_dir, f"{self.environment}.yaml")
        if os.path.exists(env_config_file):
            env_loader = XConfigLoader(env_config_file)
            env_config = env_loader.load_config()
            
            # 合并配置
            config = self._merge_configs(config, env_config)
        
        # 加载本地覆盖配置
        local_config_file = os.path.join(self.base_dir, "local.yaml")
        if os.path.exists(local_config_file):
            local_loader = XConfigLoader(local_config_file)
            local_config = local_loader.load_config()
            config = self._merge_configs(config, local_config)
        
        return config
    
    def _merge_configs(self, base_config, override_config):
        """深度合并配置字典"""
        merged = base_config.copy()
        
        for key, value in override_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged

# 使用多环境配置
env_loader = EnvironmentConfigLoader()
config = env_loader.load_config()

print(f"当前环境: {env_loader.environment}")
print(f"数据库配置: {config['database']}")
```

### 热加载配置

```python
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ConfigReloadHandler(FileSystemEventHandler):
    """配置文件变化处理器"""
    
    def __init__(self, config_loader, callback=None):
        self.config_loader = config_loader
        self.callback = callback
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.yaml'):
            print(f"配置文件变化: {event.src_path}")
            
            try:
                # 重新加载配置
                new_config = self.config_loader.reload_config()
                
                if self.callback:
                    self.callback(new_config)
                    
                print("配置重新加载成功")
                
            except Exception as e:
                print(f"配置重新加载失败: {e}")

class HotReloadConfigLoader:
    """支持热加载的配置加载器"""
    
    def __init__(self, config_file, auto_reload=True):
        self.config_loader = XConfigLoader(config_file)
        self.config = self.config_loader.load_config()
        self.callbacks = []
        
        if auto_reload:
            self._setup_hot_reload(config_file)
    
    def _setup_hot_reload(self, config_file):
        """设置热加载监控"""
        config_dir = os.path.dirname(os.path.abspath(config_file))
        
        event_handler = ConfigReloadHandler(
            self.config_loader,
            callback=self._on_config_reload
        )
        
        observer = Observer()
        observer.schedule(event_handler, config_dir, recursive=False)
        observer.start()
        
        self.observer = observer
    
    def _on_config_reload(self, new_config):
        """配置重新加载回调"""
        old_config = self.config
        self.config = new_config
        
        # 通知所有回调函数
        for callback in self.callbacks:
            try:
                callback(old_config, new_config)
            except Exception as e:
                print(f"配置变化回调失败: {e}")
    
    def add_reload_callback(self, callback):
        """添加配置重新加载回调"""
        self.callbacks.append(callback)
    
    def get(self, key_path, default=None):
        """获取配置值"""
        return self.config_loader.get(key_path, default, self.config)
    
    def stop(self):
        """停止热加载监控"""
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()

# 使用热加载配置
def on_config_change(old_config, new_config):
    print("配置发生变化:")
    print(f"  旧值: {old_config.get('processing', {}).get('max_workers', 'N/A')}")
    print(f"  新值: {new_config.get('processing', {}).get('max_workers', 'N/A')}")

hot_loader = HotReloadConfigLoader("config/app.yaml")
hot_loader.add_reload_callback(on_config_change)

# 使用配置
max_workers = hot_loader.get("processing.max_workers", 4)
print(f"当前最大工作线程: {max_workers}")

# 配置文件变化时会自动重新加载
```

### 配置模板生成

```python
def generate_config_template(output_file="config_template.yaml"):
    """生成配置文件模板"""
    
    template_config = {
        "application": {
            "name": "XpertCorpus",
            "version": "0.1.0",
            "debug": False,
            "log_level": "INFO"
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "xpertcorpus_db",
            "username": "username",
            "password": "password",
            "pool_size": 10,
            "timeout": 30
        },
        "storage": {
            "output_dir": "./output",
            "format": "jsonl",
            "compression": False,
            "backup_enabled": True,
            "cleanup_days": 30
        },
        "processing": {
            "max_workers": 4,
            "batch_size": 128,
            "timeout": 300,
            "retry_attempts": 3,
            "memory_limit_mb": 1024
        },
        "models": {
            "llm_cleaner": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "max_tokens": 4096,
                "temperature": 0.1,
                "api_key": "${OPENAI_API_KEY}"
            },
            "text_splitter": {
                "chunk_size": 1000,
                "overlap": 100,
                "separator": "\\n\\n"
            }
        },
        "logging": {
            "level": "INFO",
            "file": "logs/xpertcorpus.log",
            "max_size": "100MB",
            "backup_count": 5,
            "format": "json",
            "console_output": True
        }
    }
    
    loader = XConfigLoader()
    success = loader.save_config(template_config, output_file)
    
    if success:
        print(f"配置模板已生成: {output_file}")
    else:
        print("配置模板生成失败")
    
    return template_config

# 生成配置模板
template = generate_config_template("config/template.yaml")
```

### 配置加密和安全

```python
import base64
from cryptography.fernet import Fernet

class SecureConfigLoader(XConfigLoader):
    """支持加密的安全配置加载器"""
    
    def __init__(self, config_file, encryption_key=None):
        super().__init__(config_file)
        
        if encryption_key:
            self.cipher = Fernet(encryption_key)
        else:
            # 从环境变量获取密钥
            key = os.getenv('CONFIG_ENCRYPTION_KEY')
            if key:
                self.cipher = Fernet(key.encode())
            else:
                self.cipher = None
    
    def load_config(self, **kwargs):
        """加载并解密配置"""
        config = super().load_config(**kwargs)
        
        if self.cipher:
            config = self._decrypt_sensitive_fields(config)
        
        return config
    
    def _decrypt_sensitive_fields(self, config):
        """解密敏感字段"""
        sensitive_fields = ['password', 'api_key', 'secret', 'token']
        
        def decrypt_recursive(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in sensitive_fields and isinstance(value, str):
                        if value.startswith('enc:'):
                            try:
                                encrypted_data = base64.b64decode(value[4:])
                                obj[key] = self.cipher.decrypt(encrypted_data).decode()
                            except Exception as e:
                                print(f"解密字段 {key} 失败: {e}")
                    elif isinstance(value, (dict, list)):
                        decrypt_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    decrypt_recursive(item)
        
        decrypt_recursive(config)
        return config
    
    def encrypt_field(self, value):
        """加密字段值"""
        if self.cipher:
            encrypted = self.cipher.encrypt(value.encode())
            return f"enc:{base64.b64encode(encrypted).decode()}"
        return value

# 使用加密配置
# 首先生成加密密钥
encryption_key = Fernet.generate_key()

# 创建安全配置加载器
secure_loader = SecureConfigLoader("config/secure.yaml", encryption_key)

# 加密敏感信息
encrypted_password = secure_loader.encrypt_field("secret_password")
print(f"加密后的密码: {encrypted_password}")

# 在配置文件中使用加密值
secure_config = {
    "database": {
        "password": encrypted_password,
        "api_key": secure_loader.encrypt_field("secret_api_key")
    }
}

# 保存加密配置
secure_loader.save_config(secure_config, "config/secure.yaml")

# 加载时自动解密
loaded_config = secure_loader.load_config()
print(f"解密后的密码: {loaded_config['database']['password']}")
```

## 最佳实践

### 1. 配置文件组织

```
config/
├── base.yaml           # 基础配置
├── development.yaml    # 开发环境配置
├── testing.yaml        # 测试环境配置
├── production.yaml     # 生产环境配置
├── local.yaml         # 本地覆盖配置（不提交到git）
└── schema.yaml        # 配置模式定义
```

### 2. 环境变量映射

```python
# 标准的环境变量命名约定
XPERTCORPUS_DATABASE_HOST=localhost
XPERTCORPUS_DATABASE_PORT=5432
XPERTCORPUS_PROCESSING_MAX_WORKERS=8
XPERTCORPUS_LOGGING_LEVEL=DEBUG

# 在配置中使用
loader = XConfigLoader("config.yaml", env_prefix="XPERTCORPUS_")
config = loader.load_config(merge_env=True)
```

### 3. 配置验证

```python
def validate_required_config(config):
    """验证必需的配置项"""
    required_paths = [
        "application.name",
        "database.host",
        "database.name",
        "processing.max_workers"
    ]
    
    loader = XConfigLoader()
    missing = []
    
    for path in required_paths:
        if loader.get(path, config=config) is None:
            missing.append(path)
    
    if missing:
        raise ValueError(f"缺少必需的配置项: {', '.join(missing)}")
```

### 4. 配置缓存

```python
class CachedConfigLoader:
    """带缓存的配置加载器"""
    
    def __init__(self, config_file, cache_ttl=300):
        self.config_file = config_file
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.last_load = 0
    
    def get_config(self):
        current_time = time.time()
        
        if (current_time - self.last_load) > self.cache_ttl:
            loader = XConfigLoader(self.config_file)
            self.cache = loader.load_config()
            self.last_load = current_time
        
        return self.cache.copy()
```

## 注意事项

### 1. 安全考虑

- 不要在配置文件中存储明文密码
- 使用环境变量或加密存储敏感信息
- 限制配置文件的访问权限

### 2. 性能考虑

- 避免频繁重新加载大型配置文件
- 使用配置缓存机制
- 考虑配置的内存占用

### 3. 维护性

- 保持配置结构的清晰和一致
- 为配置项提供合理的默认值
- 建立配置变更的版本管理

### 4. 错误处理

- 提供清晰的配置错误消息
- 实现配置回退机制
- 记录配置加载和变更日志

---

**更多信息：**
- [日志系统 (xlogger)](xlogger.md)
- [错误处理 (xerror_handler)](xerror_handler.md)
- [存储管理 (xstorage)](xstorage.md) 