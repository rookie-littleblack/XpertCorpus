"""
Registry and lazy loading system for XpertCorpus operators.

This module provides a flexible registry system for managing operators with
lazy loading capabilities, caching, and error handling.

@author: rookielittleblack
@date:   2025-08-13
"""
import os
import time
import types
import importlib
import importlib.util

from typing import Any, Dict, List, Optional, Type, Callable
from pathlib import Path
from datetime import datetime, timedelta
from threading import Lock
from rich.table import Table
from rich.console import Console
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xerror_handler import error_handler, safe_execute


class RegistryCache:
    """
    Cache system for registry operations with TTL support.
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache with default TTL.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get cached value if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/missing
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if datetime.now() > entry['expires_at']:
                del self._cache[key]
                return None
            
            entry['last_accessed'] = datetime.now()
            return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set cached value with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        with self._lock:
            self._cache[key] = {
                'value': value,
                'created_at': datetime.now(),
                'last_accessed': datetime.now(),
                'expires_at': expires_at,
                'ttl': ttl
            }
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()
            xlogger.info("Registry cache cleared")
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            now = datetime.now()
            expired_keys = [
                key for key, entry in self._cache.items()
                if now > entry['expires_at']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                xlogger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            return {
                'total_entries': len(self._cache),
                'cache_keys': list(self._cache.keys()),
                'oldest_entry': min(
                    (entry['created_at'] for entry in self._cache.values()),
                    default=None
                ),
                'most_recent_access': max(
                    (entry['last_accessed'] for entry in self._cache.values()),
                    default=None
                )
            }


class Registry:
    """
    Enhanced registry with caching, validation, and error handling.
    
    The registry provides name -> object mapping to support third-party
    users' custom modules with improved performance and reliability.
    """

    def __init__(self, name: str, enable_cache: bool = True, cache_ttl: int = 3600):
        """
        Initialize registry.
        
        Args:
            name: Registry name
            enable_cache: Whether to enable caching
            cache_ttl: Cache time-to-live in seconds
        """
        self._name = name
        self._obj_map: Dict[str, Type] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        
        # Cache system
        self.enable_cache = enable_cache
        self._cache = RegistryCache(cache_ttl) if enable_cache else None
        
        # Statistics
        self._stats = {
            'registrations': 0,
            'lookups': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'errors': 0
        }
        
        xlogger.info(f"Initialized registry '{name}' with cache={'enabled' if enable_cache else 'disabled'}")

    def _do_register(self, name: str, obj: Type, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Internal registration method with validation.
        
        Args:
            name: Object name
            obj: Object to register
            metadata: Optional metadata
        """
        with self._lock:
            if name in self._obj_map:
                xlogger.warning(f"Overriding existing registration for '{name}' in '{self._name}' registry")
            
            # Store object and metadata
            self._obj_map[name] = obj
            self._metadata[name] = {
                'registered_at': datetime.now().isoformat(),
                'module': getattr(obj, '__module__', 'unknown'),
                'class_name': getattr(obj, '__name__', 'unknown'),
                'version': getattr(obj, 'VERSION', '1.0.0'),
                **(metadata or {})
            }
            
            # Clear cache for this entry
            if self._cache:
                cache_key = f"{self._name}:{name}"
                self._cache.set(cache_key, obj)
            
            self._stats['registrations'] += 1
            xlogger.debug(f"Registered '{name}' in '{self._name}' registry")

    def register(self, obj: Optional[Type] = None, name: Optional[str] = None, 
                metadata: Optional[Dict[str, Any]] = None):
        """
        Register object in registry.
        
        Args:
            obj: Object to register (None for decorator usage)
            name: Custom name (uses obj.__name__ if None)
            metadata: Optional metadata
            
        Returns:
            Decorator function or None
        """
        def _register(func_or_class: Type) -> Type:
            register_name = name or func_or_class.__name__
            
            try:
                self._validate_registration(register_name, func_or_class)
                self._do_register(register_name, func_or_class, metadata)
                return func_or_class
            except Exception as e:
                self._stats['errors'] += 1
                error_handler.handle_error(
                    e,
                    context={
                        'registry': self._name,
                        'object_name': register_name,
                        'object_type': type(func_or_class).__name__
                    },
                    should_raise=True
                )

        if obj is None:
            # Used as decorator
            return _register
        else:
            # Used as function call
            return _register(obj)

    def _validate_registration(self, name: str, obj: Type) -> None:
        """
        Validate object registration.
        
        Args:
            name: Object name
            obj: Object to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not name:
            raise ValueError("Registration name cannot be empty")
        
        if not callable(obj) and not isinstance(obj, type):
            raise ValueError(f"Object '{name}' must be callable or a class")
        
        # Additional validation for specific registry types
        if self._name == 'operator':
            # Validate operator interface (if possible without importing)
            if hasattr(obj, 'run') and not callable(getattr(obj, 'run')):
                raise ValueError(f"Operator '{name}' must have callable 'run' method")

    @safe_execute(fallback_value=None, retry_enabled=True)
    def get(self, name: str) -> Optional[Type]:
        """
        Get object from registry with caching and lazy loading.
        
        Args:
            name: Object name
            
        Returns:
            Registered object or None if not found
            
        Raises:
            KeyError: If object not found after all attempts
        """
        self._stats['lookups'] += 1
        cache_key = f"{self._name}:{name}"
        
        # Try cache first
        if self._cache:
            cached_obj = self._cache.get(cache_key)
            if cached_obj is not None:
                self._stats['cache_hits'] += 1
                return cached_obj
            self._stats['cache_misses'] += 1
        
        # Try direct registry lookup
        with self._lock:
            ret = self._obj_map.get(name)
        
        if ret is not None:
            # Cache the result
            if self._cache:
                self._cache.set(cache_key, ret)
            return ret
        
        # Try lazy loading for operator registry
        if self._name == 'operator':
            ret = self._try_lazy_loading(name)
            if ret is not None:
                # Cache successful lazy load
                if self._cache:
                    self._cache.set(cache_key, ret)
                return ret
        
        # Object not found
        error_msg = f"No object named '{name}' found in '{self._name}' registry!"
        xlogger.error(error_msg)
        self._stats['errors'] += 1
        raise KeyError(error_msg)

    def _try_lazy_loading(self, name: str) -> Optional[Type]:
        """
        Attempt lazy loading for operator registry.
        
        Args:
            name: Object name to load
            
        Returns:
            Loaded object or None if not found
        """
        search_modules = ['eval', 'generate', 'process', 'refine']
        
        for module_suffix in search_modules:
            module_path = f"xpertcorpus.modules.operators.{module_suffix}"
            try:
                module_lib = importlib.import_module(module_path)
                if hasattr(module_lib, name):
                    clss = getattr(module_lib, name)
                    # Register the dynamically loaded class
                    self._do_register(name, clss, {'lazy_loaded': True, 'source_module': module_path})
                    xlogger.info(f"Lazy loaded '{name}' from '{module_path}'")
                    return clss
            except (AttributeError, ImportError):
                continue
            except Exception as e:
                xlogger.warning(f"Error during lazy loading from {module_path}: {e}")
                continue
        
        return None

    def unregister(self, name: str) -> bool:
        """
        Unregister object from registry.
        
        Args:
            name: Object name to remove
            
        Returns:
            True if object was removed, False if not found
        """
        with self._lock:
            if name in self._obj_map:
                del self._obj_map[name]
                self._metadata.pop(name, None)
                
                # Clear from cache
                if self._cache:
                    cache_key = f"{self._name}:{name}"
                    # Note: We don't have a direct remove method, but TTL will handle it
                
                xlogger.info(f"Unregistered '{name}' from '{self._name}' registry")
                return True
        return False

    def __contains__(self, name: str) -> bool:
        """Check if name is in registry."""
        with self._lock:
            return name in self._obj_map

    def __iter__(self):
        """Iterate over registry items."""
        with self._lock:
            return iter(self._obj_map.items())

    def keys(self) -> List[str]:
        """Get all registered names."""
        with self._lock:
            return list(self._obj_map.keys())
    
    def values(self) -> List[Type]:
        """Get all registered objects."""
        with self._lock:
            return list(self._obj_map.values())
    
    def items(self) -> List[tuple]:
        """Get all registry items."""
        with self._lock:
            return list(self._obj_map.items())

    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for registered object.
        
        Args:
            name: Object name
            
        Returns:
            Metadata dictionary or None if not found
        """
        return self._metadata.get(name)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats.update({
            'total_registered': len(self._obj_map),
            'registry_name': self._name,
            'cache_enabled': self.enable_cache,
            'cache_stats': self._cache.get_stats() if self._cache else None
        })
        return stats

    def cleanup(self) -> None:
        """Cleanup registry caches and expired entries."""
        if self._cache:
            expired_count = self._cache.cleanup_expired()
            xlogger.info(f"Registry '{self._name}' cleanup: removed {expired_count} expired entries")

    def __repr__(self) -> str:
        """String representation with rich table."""
        table = Table(title=f'Registry of {self._name}')
        table.add_column('Names', justify='left', style='cyan')
        table.add_column('Objects', justify='left', style='green')
        table.add_column('Module', justify='left', style='yellow')

        with self._lock:
            for name, obj in sorted(self._obj_map.items()):
                metadata = self._metadata.get(name, {})
                module = metadata.get('module', 'unknown')
                table.add_row(name, str(obj), module)

        console = Console()
        with console.capture() as capture:
            console.print(table, end='')

        return capture.get()

    def get_obj_map(self) -> Dict[str, Type]:
        """
        Get the object map of the registry.
        
        Returns:
            Copy of internal object mapping
        """
        with self._lock:
            return self._obj_map.copy()


# Global operator registry instance
OPERATOR_REGISTRY = Registry('operator')


class LazyLoader(types.ModuleType):
    """
    Enhanced lazy loader for dynamic module importing with caching and error handling.
    """

    def __init__(self, name: str, path: str, import_structure: Dict[str, str]):
        """
        Initialize LazyLoader module.

        Args:
            name: Module name
            path: Module path
            import_structure: Dictionary mapping class names to file paths
        """
        super().__init__(name)
        self._import_structure = import_structure
        self._loaded_classes: Dict[str, Type] = {}
        self._base_folder = Path(__file__).resolve().parents[2]
        self._lock = Lock()
        self.__path__ = [path]
        
        # Loading statistics
        self._stats = {
            'load_attempts': 0,
            'successful_loads': 0,
            'failed_loads': 0,
            'cache_hits': 0
        }
        
        xlogger.debug(f"Initialized LazyLoader for {name} with {len(import_structure)} classes")

    @safe_execute(fallback_value=None, retry_enabled=False)
    def _load_class_from_file(self, file_path: str, class_name: str) -> Optional[Type]:
        """
        Load class from specified file with error handling.

        Args:
            file_path: Path to the script file
            class_name: Name of the class

        Returns:
            Class object or None if loading fails
        """
        abs_file_path = os.path.join(self._base_folder, file_path)
        
        if not os.path.exists(abs_file_path):
            raise FileNotFoundError(f"File {abs_file_path} does not exist")
        
        xlogger.debug(f"Loading class {class_name} from {abs_file_path}")
        
        # Dynamic module loading
        try:
            spec = importlib.util.spec_from_file_location(class_name, abs_file_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Cannot create spec for {abs_file_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract class
            if not hasattr(module, class_name):
                raise AttributeError(f"Class {class_name} not found in {abs_file_path}")
            
            loaded_class = getattr(module, class_name)
            xlogger.debug(f"Successfully loaded {class_name} from {file_path}")
            return loaded_class
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    'file_path': abs_file_path,
                    'class_name': class_name,
                    'module_name': self.__name__
                },
                should_raise=False
            )
            return None

    def __getattr__(self, item: str) -> Type:
        """
        Dynamically load and return the requested attribute.
        
        Args:
            item: Name of the attribute to load
            
        Returns:
            The loaded class or attribute
            
        Raises:
            AttributeError: If attribute cannot be loaded
        """
        self._stats['load_attempts'] += 1
        
        with self._lock:
            # Check cache first
            if item in self._loaded_classes:
                self._stats['cache_hits'] += 1
                return self._loaded_classes[item]
        
        # Try to load from import structure
        if item in self._import_structure:
            file_path = self._import_structure[item]
            
            try:
                loaded_class = self._load_class_from_file(file_path, item)
                
                if loaded_class is not None:
                    with self._lock:
                        self._loaded_classes[item] = loaded_class
                    self._stats['successful_loads'] += 1
                    return loaded_class
                else:
                    self._stats['failed_loads'] += 1
                    
            except Exception as e:
                self._stats['failed_loads'] += 1
                error_handler.handle_error(
                    e,
                    context={
                        'item': item,
                        'file_path': file_path,
                        'module': self.__name__
                    },
                    should_raise=False
                )
        
        # Attribute not found
        self._stats['failed_loads'] += 1
        raise AttributeError(f"Module {self.__name__} has no attribute {item}")
    
    def get_loaded_classes(self) -> List[str]:
        """Get list of already loaded class names."""
        with self._lock:
            return list(self._loaded_classes.keys())
    
    def get_available_classes(self) -> List[str]:
        """Get list of all available class names."""
        return list(self._import_structure.keys())
    
    def preload_class(self, class_name: str) -> bool:
        """
        Preload a specific class.
        
        Args:
            class_name: Name of class to preload
            
        Returns:
            True if successful, False otherwise
        """
        try:
            getattr(self, class_name)
            return True
        except AttributeError:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        with self._lock:
            return {
                **self._stats,
                'loaded_classes_count': len(self._loaded_classes),
                'available_classes_count': len(self._import_structure),
                'loaded_classes': list(self._loaded_classes.keys())
            }
    
    def clear_cache(self) -> None:
        """Clear the loaded classes cache."""
        with self._lock:
            self._loaded_classes.clear()
            xlogger.info(f"Cleared LazyLoader cache for {self.__name__}")


# Utility functions
def create_registry(name: str, enable_cache: bool = True, cache_ttl: int = 3600) -> Registry:
    """
    Create a new registry instance.
    
    Args:
        name: Registry name
        enable_cache: Whether to enable caching
        cache_ttl: Cache TTL in seconds
        
    Returns:
        Registry instance
    """
    return Registry(name, enable_cache, cache_ttl)


def get_global_registry_stats() -> Dict[str, Any]:
    """
    Get statistics for the global operator registry.
    
    Returns:
        Statistics dictionary
    """
    return OPERATOR_REGISTRY.get_stats()
