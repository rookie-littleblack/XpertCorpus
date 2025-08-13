"""
Operator abstract base class and utilities for XpertCorpus.

This module defines the core operator interface and provides utilities for
operator management, lifecycle handling, and configuration.

@author: rookielittleblack
@date:   2025-08-13
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, Union, List
from datetime import datetime
from xpertcorpus.utils.xlogger import xlogger
from xpertcorpus.utils.xerror_handler import error_handler, safe_execute
from xpertcorpus.modules.others.xregistry import OPERATOR_REGISTRY


class OperatorState(Enum):
    """Operator lifecycle states."""
    INITIALIZED = "INITIALIZED"
    CONFIGURED = "CONFIGURED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


class OperatorABC(ABC):
    """
    Abstract base class for all operators in XpertCorpus.
    
    Provides standardized interface for data processing operations with
    lifecycle management, error handling, and configuration support.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize operator with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.state = OperatorState.INITIALIZED
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "operator_name": self.__class__.__name__,
            "version": getattr(self, 'VERSION', '1.0.0')
        }
        self.metrics = {
            "execution_count": 0,
            "total_processing_time": 0.0,
            "last_execution_time": None,
            "error_count": 0
        }
        self._hooks = {
            "before_run": [],
            "after_run": [],
            "on_error": [],
            "on_complete": []
        }
        
        # Call initialization hook
        self._on_init()
    
    def _on_init(self) -> None:
        """Hook called during initialization. Override in subclasses."""
        pass
    
    def _on_configure(self) -> None:
        """Hook called during configuration. Override in subclasses."""
        pass
    
    def _on_before_run(self) -> None:
        """Hook called before run execution. Override in subclasses."""
        pass
    
    def _on_after_run(self, result: Any) -> None:
        """Hook called after successful run execution. Override in subclasses."""
        pass
    
    def _on_error(self, error: Exception) -> None:
        """Hook called when error occurs. Override in subclasses."""
        pass
    
    def _on_complete(self) -> None:
        """Hook called when operation completes. Override in subclasses."""
        pass

    @abstractmethod
    def run(self) -> Any:
        """
        Main function to run the operator.
        
        Returns:
            Result of the operation
        """
        pass
    
    @abstractmethod
    def get_desc(self, lang: str = "zh") -> str:
        """
        Get description of the operator.
        
        Args:
            lang: Language for description ("zh" for Chinese, "en" for English)
            
        Returns:
            Description string
        """
        pass
    
    def configure(self, config: Dict[str, Any]) -> 'OperatorABC':
        """
        Configure the operator with provided settings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Self for method chaining
        """
        try:
            self.config.update(config)
            self.state = OperatorState.CONFIGURED
            self._on_configure()
            xlogger.info(f"Operator {self.__class__.__name__} configured successfully")
            return self
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "operator": self.__class__.__name__,
                    "config_keys": list(config.keys())
                },
                should_raise=True
            )
    
    def validate_config(self) -> bool:
        """
        Validate operator configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        return True  # Override in subclasses for specific validation
    
    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (None to get all config)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        if key is None:
            return self.config.copy()
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> 'OperatorABC':
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            Self for method chaining
        """
        self.config[key] = value
        return self
    
    def add_hook(self, event: str, callback: callable) -> 'OperatorABC':
        """
        Add hook for operator events.
        
        Args:
            event: Event name ("before_run", "after_run", "on_error", "on_complete")
            callback: Callback function
            
        Returns:
            Self for method chaining
        """
        if event in self._hooks:
            self._hooks[event].append(callback)
        else:
            xlogger.warning(f"Unknown hook event: {event}")
        return self
    
    def _execute_hooks(self, event: str, *args, **kwargs) -> None:
        """Execute hooks for given event."""
        for hook in self._hooks.get(event, []):
            try:
                hook(self, *args, **kwargs)
            except Exception as e:
                xlogger.error(f"Hook execution failed for {event}: {e}")
    
    @safe_execute(fallback_value=None, retry_enabled=False)
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the operator with full lifecycle management.
        
        Returns:
            Result of the operation
        """
        start_time = datetime.now()
        
        try:
            # Pre-execution setup
            self.state = OperatorState.RUNNING
            self.metrics["execution_count"] += 1
            
            # Execute hooks
            self._execute_hooks("before_run")
            self._on_before_run()
            
            xlogger.info(f"Starting execution of {self.__class__.__name__}")
            
            # Execute main operation
            result = self.run(*args, **kwargs)
            
            # Post-execution handling
            self.state = OperatorState.COMPLETED
            execution_time = (datetime.now() - start_time).total_seconds()
            self.metrics["total_processing_time"] += execution_time
            self.metrics["last_execution_time"] = execution_time
            
            self._execute_hooks("after_run", result)
            self._on_after_run(result)
            self._execute_hooks("on_complete")
            self._on_complete()
            
            xlogger.success(f"Completed execution of {self.__class__.__name__} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            # Error handling
            self.state = OperatorState.FAILED
            self.metrics["error_count"] += 1
            
            self._execute_hooks("on_error", e)
            self._on_error(e)
            
            error_handler.handle_error(
                e,
                context={
                    "operator": self.__class__.__name__,
                    "execution_count": self.metrics["execution_count"],
                    "config": self.config
                },
                should_raise=True
            )
    
    def stop(self) -> None:
        """Stop the operator execution."""
        self.state = OperatorState.STOPPED
        xlogger.info(f"Operator {self.__class__.__name__} stopped")
    
    def reset(self) -> 'OperatorABC':
        """
        Reset operator to initial state.
        
        Returns:
            Self for method chaining
        """
        self.state = OperatorState.INITIALIZED
        self.metrics = {
            "execution_count": 0,
            "total_processing_time": 0.0,
            "last_execution_time": None,
            "error_count": 0
        }
        xlogger.info(f"Operator {self.__class__.__name__} reset")
        return self
    
    def get_state(self) -> OperatorState:
        """Get current operator state."""
        return self.state
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get operator metadata."""
        return {
            **self.metadata,
            "current_state": self.state.value,
            "config": self.config.copy()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get operator performance metrics."""
        metrics = self.metrics.copy()
        if metrics["execution_count"] > 0:
            metrics["average_execution_time"] = (
                metrics["total_processing_time"] / metrics["execution_count"]
            )
        else:
            metrics["average_execution_time"] = 0.0
        
        return metrics
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive operator information.
        
        Returns:
            Dictionary with operator details
        """
        return {
            "name": self.__class__.__name__,
            "description": self.get_desc(),
            "metadata": self.get_metadata(),
            "metrics": self.get_metrics(),
            "state": self.state.value,
            "config": self.config.copy()
        }
    
    def __str__(self) -> str:
        """String representation of operator."""
        return f"{self.__class__.__name__}(state={self.state.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of operator."""
        return (f"{self.__class__.__name__}("
                f"state={self.state.value}, "
                f"executions={self.metrics['execution_count']}, "
                f"errors={self.metrics['error_count']})")


class OperatorManager:
    """
    Manager for operator lifecycle and registry operations.
    """
    
    @staticmethod
    def create_operator(operator_name: str, 
                       config: Optional[Dict[str, Any]] = None,
                       **kwargs) -> OperatorABC:
        """
        Create operator instance with error handling.
        
        Args:
            operator_name: Name of operator to create
            config: Optional configuration
            **kwargs: Additional arguments
            
        Returns:
            Operator instance
        """
        try:
            xlogger.info(f"Creating operator: {operator_name}")
            
            # Get operator class from registry
            operator_class = OPERATOR_REGISTRY.get(operator_name)
            
            # Create instance
            if config:
                operator = operator_class(config, **kwargs)
            else:
                operator = operator_class(**kwargs)
            
            # Configure if config provided
            if config:
                operator.configure(config)
            
            xlogger.success(f"Successfully created operator: {operator_name}")
            return operator
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={
                    "operator_name": operator_name,
                    "config": config,
                    "kwargs": kwargs
                },
                should_raise=True
            )
    
    @staticmethod
    def list_operators() -> List[str]:
        """
        List all available operators.
        
        Returns:
            List of operator names
        """
        return list(OPERATOR_REGISTRY.keys())
    
    @staticmethod
    def get_operator_info(operator_name: str) -> Dict[str, Any]:
        """
        Get information about an operator.
        
        Args:
            operator_name: Name of operator
            
        Returns:
            Operator information dictionary
        """
        try:
            operator_class = OPERATOR_REGISTRY.get(operator_name)
            
            # Create temporary instance to get info
            temp_operator = operator_class()
            info = {
                "name": operator_name,
                "class": operator_class.__name__,
                "description": temp_operator.get_desc(),
                "module": operator_class.__module__,
                "version": getattr(operator_class, 'VERSION', '1.0.0')
            }
            
            return info
            
        except Exception as e:
            error_handler.handle_error(
                e,
                context={"operator_name": operator_name},
                should_raise=False
            )
            return {"name": operator_name, "error": str(e)}


def get_operator(operator_name: str, 
                config: Optional[Dict[str, Any]] = None,
                **kwargs) -> OperatorABC:
    """
    Get operator instance with enhanced error handling.
    
    Args:
        operator_name: Name of operator to get
        config: Optional configuration dictionary
        **kwargs: Additional arguments
        
    Returns:
        Operator instance
        
    Raises:
        KeyError: If operator not found
        Exception: If operator creation fails
    """
    return OperatorManager.create_operator(operator_name, config, **kwargs)


# Legacy function for backward compatibility
def get_operator_legacy(operator_name: str, args: Any) -> OperatorABC:
    """
    Legacy get_operator function for backward compatibility.
    
    Args:
        operator_name: Name of operator
        args: Arguments (legacy format)
        
    Returns:
        Operator instance
    """
    xlogger.warning("Using legacy get_operator function. Consider migrating to new format.")
    
    try:
        # Get operator class
        operator_class = OPERATOR_REGISTRY.get(operator_name)
        
        # Create instance with legacy args
        operator = operator_class(args)
        
        xlogger.info(f"Successfully created operator {operator_name} with legacy args")
        return operator
        
    except Exception as e:
        error_handler.handle_error(
            e,
            context={
                "operator_name": operator_name,
                "args": args,
                "legacy_mode": True
            },
            should_raise=True
        )
