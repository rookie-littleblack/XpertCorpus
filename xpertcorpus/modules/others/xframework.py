"""
Framework abstract base class for XpertCorpus.

This module defines the core framework interface and provides utilities for
framework lifecycle management, configuration, and data processing pipelines.

@author: rookielittleblack
@date:   2025-08-13
"""
import os
import time

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Type
from pathlib import Path
from datetime import datetime
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xerror_handler import error_handler, safe_execute
from xpertcorpus.utils.xstorage import FileStorage
from xpertcorpus.modules.others.xoperator import OperatorABC


class FrameworkState(Enum):
    """Framework lifecycle states."""
    INITIALIZED = "INITIALIZED"
    CONFIGURED = "CONFIGURED"
    PREPARING = "PREPARING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    PAUSED = "PAUSED"


class FrameworkType(Enum):
    """Framework types."""
    PRETRAINING = "PRETRAINING"
    SFT = "SFT"
    COT = "COT"
    MULTIMODAL = "MULTIMODAL"
    CUSTOM = "CUSTOM"


class FrameworkABC(ABC):
    """
    Abstract base class for all frameworks in XpertCorpus.
    
    Provides standardized interface for data processing frameworks with
    lifecycle management, configuration, and pipeline execution.
    """
    
    # Framework metadata
    FRAMEWORK_TYPE: FrameworkType = FrameworkType.CUSTOM
    VERSION: str = "1.0.0"
    REQUIRED_OPERATORS: List[str] = []
    REQUIRED_PIPELINES: List[str] = []
    
    def __init__(self, 
                 input_file: str,
                 output_dir: str = "./output",
                 max_workers: int = 1,
                 limit: int = 0,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize framework with basic parameters.
        
        Args:
            input_file: Input file or directory path
            output_dir: Output directory path
            max_workers: Number of worker threads
            limit: Processing limit (0 for no limit)
            config: Optional configuration dictionary
        """
        # Core parameters
        self.input_file = input_file
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.limit = limit
        self.config = config or {}
        
        # Framework state
        self.state = FrameworkState.INITIALIZED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Processing metadata
        self.metadata = {
            "framework_name": self.__class__.__name__,
            "framework_type": self.FRAMEWORK_TYPE.value,
            "version": self.VERSION,
            "created_at": datetime.now().isoformat(),
            "input_file": input_file,
            "output_dir": output_dir,
            "max_workers": max_workers,
            "limit": limit
        }
        
        # Performance metrics
        self.metrics = {
            "total_processing_time": 0.0,
            "files_processed": 0,
            "records_processed": 0,
            "tokens_processed": 0,
            "errors_count": 0,
            "pipeline_steps_completed": 0
        }
        
        # Components
        self.storage: Optional[FileStorage] = None
        self.operators: Dict[str, OperatorABC] = {}
        self.pipelines: Dict[str, Any] = {}
        
        # Hooks for lifecycle events
        self._hooks = {
            "before_init": [],
            "after_init": [],
            "before_prepare": [],
            "after_prepare": [],
            "before_run": [],
            "after_run": [],
            "on_error": [],
            "on_complete": [],
            "on_pause": [],
            "on_resume": []
        }
        
        # Initialize framework
        self._initialize()
    
    def _initialize(self) -> None:
        """Internal initialization process."""
        try:
            xlogger.info(f"Initializing {self.__class__.__name__} framework...")
            
            # Execute before_init hooks
            self._execute_hooks("before_init")
            
            # Validate and prepare paths
            self._validate_paths()
            
            # Initialize storage
            self._initialize_storage()
            
            # Framework-specific initialization
            self._on_init()
            
            # Execute after_init hooks
            self._execute_hooks("after_init")
            
            xlogger.success(f"{self.__class__.__name__} framework initialized successfully")
            
        except Exception as e:
            self.state = FrameworkState.FAILED
            self.metrics["errors_count"] += 1
            error_handler.handle_error(
                e,
                context={
                    "framework": self.__class__.__name__,
                    "stage": "initialization",
                    "input_file": self.input_file,
                    "output_dir": self.output_dir
                },
                should_raise=True
            )
    
    def _validate_paths(self) -> None:
        """Validate and prepare input/output paths."""
        # Validate input path
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input path not found: {self.input_file}")
        
        # Prepare output directory with timestamp if default
        if self.output_dir == "./output":
            self.output_dir = os.path.join(
                self.output_dir, 
                datetime.now().strftime("%Y%m%d-%H%M%S")
            )
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        xlogger.info(f"Paths validated - Input: {self.input_file}, Output: {self.output_dir}")
    
    def _initialize_storage(self) -> None:
        """Initialize storage system."""
        try:
            self.storage = FileStorage(
                first_entry_file_name=self.input_file,
                cache_path=self.output_dir,
                enable_compression=self.config.get("enable_compression", False),
                validate_on_write=self.config.get("validate_on_write", True)
            )
            xlogger.debug("Storage system initialized")
        except Exception as e:
            error_handler.handle_error(
                e,
                context={"stage": "storage_initialization"},
                should_raise=True
            )
    
    def _execute_hooks(self, event: str, *args, **kwargs) -> None:
        """Execute hooks for given event."""
        for hook in self._hooks.get(event, []):
            try:
                hook(self, *args, **kwargs)
            except Exception as e:
                xlogger.error(f"Hook execution failed for {event}: {e}")
    
    # Abstract methods that must be implemented by subclasses
    
    @abstractmethod
    def _on_init(self) -> None:
        """Framework-specific initialization. Override in subclasses."""
        pass
    
    @abstractmethod
    def _prepare_components(self) -> None:
        """Prepare framework components (operators, pipelines). Override in subclasses."""
        pass
    
    @abstractmethod
    def _execute_pipeline(self) -> Dict[str, Any]:
        """Execute the main processing pipeline. Override in subclasses."""
        pass
    
    @abstractmethod
    def get_desc(self, lang: str = "zh") -> str:
        """Get framework description."""
        pass
    
    # Configuration management
    
    def configure(self, config: Dict[str, Any]) -> 'FrameworkABC':
        """
        Configure framework with provided settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Self for method chaining
        """
        try:
            self.config.update(config)
            self.state = FrameworkState.CONFIGURED
            xlogger.info(f"Framework {self.__class__.__name__} configured")
            return self
        except Exception as e:
            error_handler.handle_error(
                e,
                context={"framework": self.__class__.__name__, "config": config},
                should_raise=True
            )
    
    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """Get configuration value."""
        if key is None:
            return self.config.copy()
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> 'FrameworkABC':
        """Set configuration value."""
        self.config[key] = value
        return self
    
    # Component management
    
    def add_operator(self, name: str, operator: OperatorABC) -> 'FrameworkABC':
        """Add operator to framework."""
        self.operators[name] = operator
        xlogger.debug(f"Added operator: {name}")
        return self
    
    def get_operator(self, name: str) -> Optional[OperatorABC]:
        """Get operator by name."""
        return self.operators.get(name)
    
    def add_pipeline(self, name: str, pipeline: Any) -> 'FrameworkABC':
        """Add pipeline to framework."""
        self.pipelines[name] = pipeline
        xlogger.debug(f"Added pipeline: {name}")
        return self
    
    def get_pipeline(self, name: str) -> Optional[Any]:
        """Get pipeline by name."""
        return self.pipelines.get(name)
    
    # Hook management
    
    def add_hook(self, event: str, callback: callable) -> 'FrameworkABC':
        """Add hook for framework events."""
        if event in self._hooks:
            self._hooks[event].append(callback)
            xlogger.debug(f"Added hook for event: {event}")
        else:
            xlogger.warning(f"Unknown hook event: {event}")
        return self
    
    # Lifecycle management
    
    def prepare(self) -> 'FrameworkABC':
        """Prepare framework for execution."""
        try:
            if self.state not in [FrameworkState.INITIALIZED, FrameworkState.CONFIGURED]:
                raise ValueError(f"Cannot prepare framework in state: {self.state}")
            
            self.state = FrameworkState.PREPARING
            xlogger.info("Preparing framework components...")
            
            # Execute before_prepare hooks
            self._execute_hooks("before_prepare")
            
            # Prepare components
            self._prepare_components()
            
            # Validate requirements
            self._validate_requirements()
            
            # Execute after_prepare hooks
            self._execute_hooks("after_prepare")
            
            self.state = FrameworkState.CONFIGURED
            xlogger.success("Framework preparation completed")
            return self
            
        except Exception as e:
            self.state = FrameworkState.FAILED
            self.metrics["errors_count"] += 1
            error_handler.handle_error(
                e,
                context={"framework": self.__class__.__name__, "stage": "preparation"},
                should_raise=True
            )
    
    def _validate_requirements(self) -> None:
        """Validate that required components are available."""
        # Check required operators
        for op_name in self.REQUIRED_OPERATORS:
            if op_name not in self.operators:
                raise ValueError(f"Required operator not found: {op_name}")
        
        # Check required pipelines
        for pipe_name in self.REQUIRED_PIPELINES:
            if pipe_name not in self.pipelines:
                raise ValueError(f"Required pipeline not found: {pipe_name}")
        
        xlogger.debug("Framework requirements validated")
    
    @safe_execute(fallback_value=None, retry_enabled=False)
    def run(self) -> Dict[str, Any]:
        """Execute the complete framework pipeline."""
        try:
            if self.state != FrameworkState.CONFIGURED:
                raise ValueError(f"Framework must be prepared before running. Current state: {self.state}")
            
            # Setup execution
            self.state = FrameworkState.RUNNING
            self.start_time = datetime.now()
            xlogger.info(f"Starting {self.__class__.__name__} framework execution...")
            
            # Execute before_run hooks
            self._execute_hooks("before_run")
            
            # Execute main pipeline
            results = self._execute_pipeline()
            
            # Calculate metrics
            self.end_time = datetime.now()
            self.metrics["total_processing_time"] = (
                self.end_time - self.start_time
            ).total_seconds()
            
            # Execute after_run hooks
            self._execute_hooks("after_run", results)
            
            # Mark as completed
            self.state = FrameworkState.COMPLETED
            self._execute_hooks("on_complete")
            
            xlogger.success(
                f"Framework execution completed in "
                f"{self.metrics['total_processing_time']:.2f}s"
            )
            
            return results
            
        except Exception as e:
            self.state = FrameworkState.FAILED
            self.metrics["errors_count"] += 1
            self._execute_hooks("on_error", e)
            
            error_handler.handle_error(
                e,
                context={
                    "framework": self.__class__.__name__,
                    "stage": "execution",
                    "metrics": self.metrics
                },
                should_raise=True
            )
    
    def forward(self) -> Dict[str, Any]:
        """Alias for run() method for backward compatibility."""
        return self.run()
    
    def pause(self) -> 'FrameworkABC':
        """Pause framework execution."""
        if self.state == FrameworkState.RUNNING:
            self.state = FrameworkState.PAUSED
            self._execute_hooks("on_pause")
            xlogger.info("Framework execution paused")
        return self
    
    def resume(self) -> 'FrameworkABC':
        """Resume framework execution."""
        if self.state == FrameworkState.PAUSED:
            self.state = FrameworkState.RUNNING
            self._execute_hooks("on_resume")
            xlogger.info("Framework execution resumed")
        return self
    
    def stop(self) -> 'FrameworkABC':
        """Stop framework execution."""
        self.state = FrameworkState.STOPPED
        xlogger.info("Framework execution stopped")
        return self
    
    def reset(self) -> 'FrameworkABC':
        """Reset framework to initial state."""
        self.state = FrameworkState.INITIALIZED
        self.start_time = None
        self.end_time = None
        self.metrics = {
            "total_processing_time": 0.0,
            "files_processed": 0,
            "records_processed": 0,
            "tokens_processed": 0,
            "errors_count": 0,
            "pipeline_steps_completed": 0
        }
        xlogger.info("Framework reset to initial state")
        return self
    
    # Information and monitoring
    
    def get_state(self) -> FrameworkState:
        """Get current framework state."""
        return self.state
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get framework metadata."""
        return {
            **self.metadata,
            "current_state": self.state.value,
            "config": self.config.copy()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get framework performance metrics."""
        metrics = self.metrics.copy()
        
        # Add derived metrics
        if self.start_time:
            if self.end_time:
                metrics["execution_duration"] = (self.end_time - self.start_time).total_seconds()
            else:
                metrics["execution_duration"] = (datetime.now() - self.start_time).total_seconds()
        
        if metrics["files_processed"] > 0 and metrics["total_processing_time"] > 0:
            metrics["files_per_second"] = metrics["files_processed"] / metrics["total_processing_time"]
        
        if metrics["tokens_processed"] > 0 and metrics["total_processing_time"] > 0:
            metrics["tokens_per_second"] = metrics["tokens_processed"] / metrics["total_processing_time"]
        
        return metrics
    
    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive framework information."""
        return {
            "name": self.__class__.__name__,
            "type": self.FRAMEWORK_TYPE.value,
            "version": self.VERSION,
            "description": self.get_desc(),
            "metadata": self.get_metadata(),
            "metrics": self.get_metrics(),
            "state": self.state.value,
            "operators": list(self.operators.keys()),
            "pipelines": list(self.pipelines.keys()),
            "config": self.config.copy()
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        progress = {
            "state": self.state.value,
            "steps_completed": self.metrics["pipeline_steps_completed"],
            "files_processed": self.metrics["files_processed"],
            "records_processed": self.metrics["records_processed"],
            "tokens_processed": self.metrics["tokens_processed"],
            "errors_count": self.metrics["errors_count"]
        }
        
        if self.start_time:
            progress["elapsed_time"] = (datetime.now() - self.start_time).total_seconds()
        
        return progress
    
    def __str__(self) -> str:
        """String representation of framework."""
        return f"{self.__class__.__name__}(state={self.state.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of framework."""
        return (
            f"{self.__class__.__name__}("
            f"type={self.FRAMEWORK_TYPE.value}, "
            f"state={self.state.value}, "
            f"files={self.metrics['files_processed']}, "
            f"errors={self.metrics['errors_count']})"
        )


class FrameworkManager:
    """
    Manager for framework registration and lifecycle operations.
    """
    
    _frameworks: Dict[str, Type[FrameworkABC]] = {}
    
    @classmethod
    def register_framework(cls, name: str, framework_class: Type[FrameworkABC]) -> None:
        """Register a framework class."""
        cls._frameworks[name] = framework_class
        xlogger.debug(f"Registered framework: {name}")
    
    @classmethod
    def get_framework(cls, name: str) -> Optional[Type[FrameworkABC]]:
        """Get framework class by name."""
        return cls._frameworks.get(name)
    
    @classmethod
    def list_frameworks(cls) -> List[str]:
        """List all registered frameworks."""
        return list(cls._frameworks.keys())
    
    @classmethod
    def create_framework(cls, 
                        name: str,
                        input_file: str,
                        output_dir: str = "./output",
                        max_workers: int = 1,
                        limit: int = 0,
                        config: Optional[Dict[str, Any]] = None) -> FrameworkABC:
        """Create framework instance."""
        framework_class = cls.get_framework(name)
        if not framework_class:
            raise ValueError(f"Framework not found: {name}")
        
        return framework_class(
            input_file=input_file,
            output_dir=output_dir,
            max_workers=max_workers,
            limit=limit,
            config=config
        )


# Utility functions
def register_framework(name: str):
    """Decorator for registering frameworks."""
    def decorator(framework_class: Type[FrameworkABC]):
        FrameworkManager.register_framework(name, framework_class)
        return framework_class
    return decorator 