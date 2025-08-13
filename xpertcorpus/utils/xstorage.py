"""
Storage for XpertCorpus.

This module provides unified data storage interfaces with support for multiple
formats, error handling, and efficient processing of large files.

@author: rookielittleblack  
@date:   2025-08-13
"""
import os
import gzip
import hashlib
import pandas as pd
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Union, Iterator
from datetime import datetime
from pathlib import Path

from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xerror_handler import error_handler, safe_execute


class XpertCorpusStorage(ABC):
    """
    Abstract base class for data storage.
    
    Provides unified interface for reading and writing data in various formats
    with error handling and validation capabilities.
    """
    
    @abstractmethod
    def read(self, output_type: Literal["dataframe", "dict", "iterator"]) -> Any:
        """
        Read data from storage.
        
        Args:
            output_type: Type of output format ("dataframe", "dict", "iterator")
            
        Returns:
            Data in the specified format
            
        Raises:
            ValueError: If output_type is not supported
            FileNotFoundError: If source file doesn't exist
        """
        pass
    
    @abstractmethod
    def write(self, data: Union[pd.DataFrame, List[Dict], Dict]) -> str:
        """
        Write data to storage.
        
        Args:
            data: Data to write (DataFrame, list of dicts, or single dict)
            
        Returns:
            Path to the written file
            
        Raises:
            ValueError: If data type is not supported
            PermissionError: If write permissions are insufficient
        """
        pass
    
    @abstractmethod
    def validate_integrity(self, file_path: str) -> bool:
        """
        Validate data integrity of stored file.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        pass


class FileStorage(XpertCorpusStorage):
    """
    File system storage implementation with advanced features.
    
    Features:
    - Multiple format support (JSON, JSONL, CSV, Parquet, Pickle)
    - Data compression options
    - Streaming support for large files
    - Integrity validation
    - Error handling and recovery
    """
    
    def __init__(self, 
                 first_entry_file_name: str,
                 cache_path: str = "./output",
                 file_name_prefix: str = "corpusflow_cache_step",
                 cache_type: Literal["json", "jsonl", "csv", "parquet", "pickle"] = "jsonl",
                 enable_compression: bool = False,
                 chunk_size: int = 10000,
                 validate_on_write: bool = True):
        """
        Initialize FileStorage.
        
        Args:
            first_entry_file_name: Path to initial input file
            cache_path: Directory for cache files (default: "./output")
            file_name_prefix: Prefix for cache file names
            cache_type: File format for caching
            enable_compression: Whether to compress files
            chunk_size: Number of records per chunk for streaming
            validate_on_write: Whether to validate files after writing
        """
        self.first_entry_file_name = first_entry_file_name
        self.cache_path = cache_path
        self.file_name_prefix = file_name_prefix
        self.cache_type = cache_type
        self.enable_compression = enable_compression
        self.chunk_size = chunk_size
        self.validate_on_write = validate_on_write
        self.operator_step = -1
        
        # Track file metadata
        self.file_metadata: Dict[str, Dict] = {}
        
        # Prepare output directory
        self._prepare_output_directory()

    def _prepare_output_directory(self) -> None:
        """Prepare output directory with timestamp if needed."""
        try:
            if self.cache_path == "./output":
                self.cache_path = os.path.join(
                    self.cache_path, 
                    datetime.now().strftime("%Y%m%d-%H%M%S")
                )
            
            Path(self.cache_path).mkdir(parents=True, exist_ok=True)
            xlogger.info(f"Output directory prepared: {self.cache_path}")
            
        except Exception as e:
            error_handler.handle_error(
                e, 
                context={"cache_path": self.cache_path},
                should_raise=True
            )

    def _get_cache_file_path(self, step: int) -> str:
        """
        Get cache file path for given step.
        
        Args:
            step: Processing step number
            
        Returns:
            Path to cache file
        """
        if step == 0:
            return self.first_entry_file_name
        else:
            file_name = f"{self.file_name_prefix}_{step}.{self.cache_type}"
            if self.enable_compression:
                file_name += ".gz"
            return os.path.join(self.cache_path, file_name)

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file for integrity checking."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            xlogger.warning(f"Failed to calculate hash for {file_path}: {e}")
            return ""

    def _store_file_metadata(self, file_path: str, record_count: int) -> None:
        """Store metadata about written file."""
        self.file_metadata[file_path] = {
            "record_count": record_count,
            "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            "created_at": datetime.now().isoformat(),
            "file_hash": self._calculate_file_hash(file_path),
            "compressed": self.enable_compression
        }

    @safe_execute(fallback_value=pd.DataFrame(), retry_enabled=True)
    def _load_local_file(self, file_path: str, file_type: str) -> pd.DataFrame:
        """
        Load local file with error handling and format detection.
        
        Args:
            file_path: Path to file to load
            file_type: Expected file type
            
        Returns:
            DataFrame containing the data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Handle compressed files
        if file_path.endswith('.gz'):
            file_type = file_type.replace('.gz', '')
            open_func = gzip.open
            mode = 'rt'
        else:
            open_func = open
            mode = 'r'
        
        xlogger.info(f"Loading file: {file_path} (type: {file_type})")
        
        try:
            if file_type == "json":
                return pd.read_json(file_path, encoding='utf-8')
            elif file_type == "jsonl":
                return pd.read_json(file_path, lines=True, encoding='utf-8')
            elif file_type == "csv":
                return pd.read_csv(file_path, encoding='utf-8')
            elif file_type == "parquet":
                return pd.read_parquet(file_path)
            elif file_type == "pickle":
                return pd.read_pickle(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            error_context = {
                "file_path": file_path,
                "file_type": file_type,
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            error_handler.handle_error(e, context=error_context, should_raise=True)

    def _convert_output(self, dataframe: pd.DataFrame, output_type: str) -> Any:
        """
        Convert DataFrame to requested output format.
        
        Args:
            dataframe: Source DataFrame
            output_type: Target format
            
        Returns:
            Data in requested format
        """
        if output_type == "dataframe":
            return dataframe
        elif output_type == "dict":
            return dataframe.to_dict(orient="records")
        elif output_type == "iterator":
            return self._create_iterator(dataframe)
        else:
            raise ValueError(f"Unsupported output type: {output_type}")

    def _create_iterator(self, dataframe: pd.DataFrame) -> Iterator[Dict]:
        """Create iterator for streaming large datasets."""
        for _, row in dataframe.iterrows():
            yield row.to_dict()

    def step(self) -> 'FileStorage':
        """Advance to next processing step."""
        self.operator_step += 1
        xlogger.debug(f"Advanced to step: {self.operator_step}")
        return self
    
    def reset(self) -> 'FileStorage':
        """Reset to initial step."""
        self.operator_step = -1
        xlogger.debug("Reset to initial step")
        return self
    
    def read(self, output_type: Literal["dataframe", "dict", "iterator"] = "dataframe") -> Any:
        """
        Read data from current step file.
        
        Args:
            output_type: Format for returned data
            
        Returns:
            Data in specified format
        """
        file_path = self._get_cache_file_path(self.operator_step)
        
        # Determine file type
        if file_path.endswith('.gz'):
            file_type = Path(file_path).stem.split('.')[-1]
        else:
            file_type = Path(file_path).suffix[1:]  # Remove the '.'
        
        # Load data
        dataframe = self._load_local_file(file_path, file_type)
        
        # Log read operation
        xlogger.success(f"Read {len(dataframe)} records from {file_path}")
        
        return self._convert_output(dataframe, output_type)
        
    def write(self, data: Union[pd.DataFrame, List[Dict], Dict]) -> str:
        """
        Write data to next step file.
        
        Args:
            data: Data to write
            
        Returns:
            Path to written file
        """
        # Convert data to DataFrame
        try:
            if isinstance(data, list):
                if data and isinstance(data[0], dict):
                    dataframe = pd.DataFrame(data)
                else:
                    raise ValueError(f"Unsupported list content type: {type(data[0]) if data else 'empty'}")
            elif isinstance(data, dict):
                dataframe = pd.DataFrame([data])
            elif isinstance(data, pd.DataFrame):
                dataframe = data
            else:
                raise ValueError(f"Unsupported data type: {type(data)}")
        except Exception as e:
            error_handler.handle_error(
                e, 
                context={"data_type": type(data), "data_length": len(data) if hasattr(data, '__len__') else 'unknown'},
                should_raise=True
            )

        # Get output file path
        file_path = self._get_cache_file_path(self.operator_step + 1)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write data
        try:
            record_count = len(dataframe)
            xlogger.info(f"Writing {record_count} records to {file_path} (type: {self.cache_type})")
            
            # Choose write method based on compression and format
            if self.enable_compression and self.cache_type in ["json", "jsonl", "csv"]:
                self._write_compressed(dataframe, file_path)
            else:
                self._write_uncompressed(dataframe, file_path)
            
            # Store metadata
            self._store_file_metadata(file_path, record_count)
            
            # Validate if requested
            if self.validate_on_write:
                if not self.validate_integrity(file_path):
                    xlogger.warning(f"Integrity validation failed for {file_path}")
            
            xlogger.success(f"Successfully wrote data to {file_path}")
            return file_path
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "file_path": file_path,
                    "cache_type": self.cache_type,
                    "record_count": len(dataframe),
                    "compression": self.enable_compression
                },
                should_raise=True
            )

    def _write_compressed(self, dataframe: pd.DataFrame, file_path: str) -> None:
        """Write data with compression."""
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            if self.cache_type == "json":
                dataframe.to_json(f, orient="records", force_ascii=False, indent=2)
            elif self.cache_type == "jsonl":
                dataframe.to_json(f, orient="records", lines=True, force_ascii=False)
            elif self.cache_type == "csv":
                dataframe.to_csv(f, index=False)

    def _write_uncompressed(self, dataframe: pd.DataFrame, file_path: str) -> None:
        """Write data without compression."""
        if self.cache_type == "json":
            dataframe.to_json(file_path, orient="records", force_ascii=False, indent=2)
        elif self.cache_type == "jsonl":
            dataframe.to_json(file_path, orient="records", lines=True, force_ascii=False)
        elif self.cache_type == "csv":
            dataframe.to_csv(file_path, index=False)
        elif self.cache_type == "parquet":
            dataframe.to_parquet(file_path)
        elif self.cache_type == "pickle":
            dataframe.to_pickle(file_path)
        else:
            raise ValueError(f"Unsupported cache type: {self.cache_type}")

    def validate_integrity(self, file_path: str) -> bool:
        """
        Validate file integrity.
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            True if file is valid, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                return False
            
            # Basic size check
            if os.path.getsize(file_path) == 0:
                xlogger.warning(f"File is empty: {file_path}")
                return False
            
            # Try to load the file to verify format
            file_type = self.cache_type
            if file_path.endswith('.gz'):
                file_type = file_type.replace('.gz', '')
            
            try:
                test_df = self._load_local_file(file_path, file_type)
                if len(test_df) == 0:
                    xlogger.warning(f"File contains no records: {file_path}")
                    return False
                return True
            except Exception as e:
                xlogger.error(f"File validation failed: {e}")
                return False
                
        except Exception as e:
            error_handler.handle_error(
                e, 
                context={"file_path": file_path}, 
                should_raise=False
            )
            return False

    def get_file_info(self, step: Optional[int] = None) -> Dict:
        """
        Get information about file at specified step.
        
        Args:
            step: Step number (current step if None)
            
        Returns:
            Dictionary with file information
        """
        if step is None:
            step = self.operator_step
            
        file_path = self._get_cache_file_path(step)
        
        info = {
            "file_path": file_path,
            "exists": os.path.exists(file_path),
            "step": step
        }
        
        if file_path in self.file_metadata:
            info.update(self.file_metadata[file_path])
        elif os.path.exists(file_path):
            info.update({
                "file_size": os.path.getsize(file_path),
                "modified_at": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
            })
        
        return info

    def cleanup_cache(self, keep_steps: int = 1) -> None:
        """
        Clean up old cache files, keeping only recent steps.
        
        Args:
            keep_steps: Number of recent steps to keep
        """
        try:
            current_step = self.operator_step
            for step in range(max(0, current_step - keep_steps)):
                file_path = self._get_cache_file_path(step)
                if os.path.exists(file_path) and step != 0:  # Never delete original file
                    os.remove(file_path)
                    xlogger.info(f"Cleaned up cache file: {file_path}")
                    
        except Exception as e:
            error_handler.handle_error(
                e,
                context={"current_step": self.operator_step, "keep_steps": keep_steps},
                should_raise=False
            )

    def get_storage_stats(self) -> Dict:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            "current_step": self.operator_step,
            "cache_path": self.cache_path,
            "cache_type": self.cache_type,
            "compression_enabled": self.enable_compression,
            "total_files": len(self.file_metadata),
            "total_records": sum(meta.get("record_count", 0) for meta in self.file_metadata.values()),
            "total_size_bytes": sum(meta.get("file_size", 0) for meta in self.file_metadata.values())
        }
        
        return stats 