"""
Exception handling utilities for XpertCorpus.

This module provides unified exception handling, retry mechanisms, and error reporting
capabilities for the entire XpertCorpus framework.

@author: rookielittleblack
@date:   2025-08-13
"""
import sys
import time
import uuid
import inspect
import traceback
import threading

from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union, Type
from datetime import datetime
from functools import wraps
from dataclasses import dataclass, field
from xpertcorpus.utils import xlogger


class ErrorSeverity(Enum):
    """Error severity levels for classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    """Error categories for classification."""
    SYSTEM = "SYSTEM"           # 系统错误（内存、磁盘等）
    NETWORK = "NETWORK"         # 网络错误（API调用、连接等）
    DATA = "DATA"              # 数据错误（格式、缺失等）
    LOGIC = "LOGIC"            # 逻辑错误（业务逻辑错误）
    CONFIG = "CONFIG"          # 配置错误（参数、设置等）
    UNKNOWN = "UNKNOWN"        # 未知错误


@dataclass
class ErrorInfo:
    """Error information data structure."""
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.UNKNOWN
    exception_type: str = ""
    message: str = ""
    traceback: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    module: str = ""
    function: str = ""
    line_number: int = 0
    retry_count: int = 0
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error info to dictionary for logging."""
        return {
            "error_id": self.error_id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
            "category": self.category.value,
            "exception_type": self.exception_type,
            "message": self.message,
            "traceback": self.traceback,
            "context": self.context,
            "module": self.module,
            "function": self.function,
            "line_number": self.line_number,
            "retry_count": self.retry_count,
            "resolved": self.resolved
        }


class XRetryMechanism:
    """
    Retry mechanism for handling transient failures.
    Provides configurable retry strategies with exponential backoff.
    """
    
    def __init__(self, 
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True):
        """
        Initialize retry mechanism.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to prevent thundering herd
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        import random
        
        delay = min(self.base_delay * (self.exponential_base ** attempt), self.max_delay)
        
        if self.jitter:
            # Add random jitter of ±25%
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
            
        return max(0, delay)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determine if the operation should be retried based on exception type and attempt count.
        
        Args:
            exception: The exception that occurred
            attempt: Current attempt number (0-based)
            
        Returns:
            True if should retry, False otherwise
        """
        if attempt >= self.max_retries:
            return False
            
        # Define retryable exceptions
        retryable_exceptions = (
            ConnectionError,
            TimeoutError,
            OSError,
            IOError,
        )
        
        # Add specific exceptions that are usually transient
        import requests
        if hasattr(requests, 'ConnectionError'):
            retryable_exceptions = retryable_exceptions + (requests.ConnectionError,)
        if hasattr(requests, 'Timeout'):
            retryable_exceptions = retryable_exceptions + (requests.Timeout,)
            
        return isinstance(exception, retryable_exceptions)
    
    def retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if not self.should_retry(e, attempt):
                    break
                    
                if attempt < self.max_retries:
                    delay = self.calculate_delay(attempt)
                    xlogger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    
        raise last_exception


def retry_on_failure(max_retries: int = 3, 
                    base_delay: float = 1.0,
                    max_delay: float = 60.0,
                    exponential_base: float = 2.0):
    """
    Decorator for automatic retry on function failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_mechanism = XRetryMechanism(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base
            )
            return retry_mechanism.retry(func, *args, **kwargs)
        return wrapper
    return decorator


class XErrorReporter:
    """
    Error reporter for collecting and managing error information.
    Provides centralized error tracking and reporting capabilities.
    """
    
    def __init__(self):
        """Initialize error reporter."""
        self.errors: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}
        self._lock = threading.Lock()
        
    def classify_error(self, exception: Exception) -> tuple[ErrorSeverity, ErrorCategory]:
        """
        Classify error by severity and category.
        
        Args:
            exception: Exception to classify
            
        Returns:
            Tuple of (severity, category)
        """
        severity = ErrorSeverity.MEDIUM
        category = ErrorCategory.UNKNOWN
        
        # Classification logic based on exception type
        if isinstance(exception, (MemoryError, OSError)):
            severity = ErrorSeverity.CRITICAL
            category = ErrorCategory.SYSTEM
        elif isinstance(exception, (ConnectionError, TimeoutError)):
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.NETWORK
        elif isinstance(exception, (ValueError, TypeError, KeyError)):
            severity = ErrorSeverity.MEDIUM
            category = ErrorCategory.DATA
        elif isinstance(exception, (AssertionError, AttributeError)):
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.LOGIC
        elif isinstance(exception, (FileNotFoundError, PermissionError)):
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.CONFIG
        
        return severity, category
    
    def extract_context(self, frame_info: Optional[inspect.FrameInfo] = None) -> Dict[str, Any]:
        """
        Extract context information from the current call stack.
        
        Args:
            frame_info: Optional frame information
            
        Returns:
            Context dictionary
        """
        context = {}
        
        try:
            if frame_info is None:
                frame_info = inspect.currentframe().f_back.f_back
                
            # Extract local variables (limit to simple types for safety)
            local_vars = {}
            if hasattr(frame_info, 'f_locals'):
                for key, value in frame_info.f_locals.items():
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        if len(str(value)) < 1000:  # Limit size
                            local_vars[key] = value
                            
            context["local_variables"] = local_vars
            
            # Extract function arguments
            if hasattr(frame_info, 'f_code'):
                arg_names = frame_info.f_code.co_varnames[:frame_info.f_code.co_argcount]
                args = {name: frame_info.f_locals.get(name) for name in arg_names 
                       if name in frame_info.f_locals}
                context["function_args"] = args
                
        except Exception:
            # If context extraction fails, continue without context
            pass
            
        return context
    
    def report_error(self, 
                    exception: Exception,
                    context: Optional[Dict[str, Any]] = None,
                    severity: Optional[ErrorSeverity] = None,
                    category: Optional[ErrorCategory] = None) -> ErrorInfo:
        """
        Report an error and create error information.
        
        Args:
            exception: Exception that occurred
            context: Additional context information
            severity: Error severity (auto-classified if None)
            category: Error category (auto-classified if None)
            
        Returns:
            ErrorInfo object
        """
        with self._lock:
            # Auto-classify if not provided
            if severity is None or category is None:
                auto_severity, auto_category = self.classify_error(exception)
                severity = severity or auto_severity
                category = category or auto_category
            
            # Extract caller information
            frame = inspect.currentframe().f_back
            caller_info = inspect.getframeinfo(frame) if frame else None
            
            # Create error info
            error_info = ErrorInfo(
                severity=severity,
                category=category,
                exception_type=type(exception).__name__,
                message=str(exception),
                traceback=traceback.format_exc(),
                context=context or self.extract_context(frame),
                module=caller_info.filename if caller_info else "",
                function=caller_info.function if caller_info else "",
                line_number=caller_info.lineno if caller_info else 0
            )
            
            # Store error
            self.errors.append(error_info)
            
            # Update error counts
            error_key = f"{error_info.exception_type}:{error_info.message}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            return error_info
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all reported errors."""
        with self._lock:
            total_errors = len(self.errors)
            if total_errors == 0:
                return {"total_errors": 0}
                
            # Count by severity
            severity_counts = {}
            for error in self.errors:
                severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1
            
            # Count by category
            category_counts = {}
            for error in self.errors:
                category_counts[error.category.value] = category_counts.get(error.category.value, 0) + 1
            
            # Recent errors
            recent_errors = sorted(self.errors, key=lambda x: x.timestamp, reverse=True)[:5]
            
            return {
                "total_errors": total_errors,
                "severity_distribution": severity_counts,
                "category_distribution": category_counts,
                "most_frequent_errors": dict(sorted(self.error_counts.items(), 
                                                  key=lambda x: x[1], reverse=True)[:10]),
                "recent_errors": [error.to_dict() for error in recent_errors]
            }
    
    def clear_errors(self):
        """Clear all stored errors."""
        with self._lock:
            self.errors.clear()
            self.error_counts.clear()


class XErrorHandler:
    """
    Unified error handler for XpertCorpus framework.
    Provides centralized exception handling, logging, and recovery mechanisms.
    """
    
    _instance: Optional['XErrorHandler'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'XErrorHandler':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize error handler."""
        if hasattr(self, '_initialized'):
            return
            
        self.reporter = XErrorReporter()
        self.retry_mechanism = XRetryMechanism()
        self._initialized = True
        
        # Install global exception handler
        self._install_global_handler()
    
    def _install_global_handler(self):
        """Install global exception handler for uncaught exceptions."""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            error_info = self.reporter.report_error(exc_value)
            xlogger.error(f"Uncaught exception: {error_info.message}", 
                         extra={"error_info": error_info.to_dict()})
            
        sys.excepthook = handle_exception
    
    def handle_error(self, 
                    exception: Exception,
                    context: Optional[Dict[str, Any]] = None,
                    should_raise: bool = True,
                    recovery_action: Optional[Callable] = None) -> Optional[ErrorInfo]:
        """
        Handle an error with comprehensive logging and optional recovery.
        
        Args:
            exception: Exception to handle
            context: Additional context information
            should_raise: Whether to re-raise the exception after handling
            recovery_action: Optional recovery function to execute
            
        Returns:
            ErrorInfo object if handled, None if recovery successful
            
        Raises:
            Exception: Original exception if should_raise is True and no recovery
        """
        # Report error
        error_info = self.reporter.report_error(exception, context)
        
        # Log error
        xlogger.error(f"Error handled: {error_info.message}, error_info: {error_info.to_dict()}")
        
        # Attempt recovery if provided
        if recovery_action:
            try:
                recovery_result = recovery_action()
                error_info.resolved = True
                xlogger.info(f"Error {error_info.error_id} resolved through recovery action")
                return None  # Recovery successful
            except Exception as recovery_exc:
                xlogger.error(f"Recovery action failed: {str(recovery_exc)}")
        
        # Re-raise if requested
        if should_raise:
            raise exception
            
        return error_info
    
    def safe_execute(self, 
                    func: Callable,
                    *args,
                    fallback_value: Any = None,
                    retry_enabled: bool = False,
                    **kwargs) -> Any:
        """
        Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Function arguments
            fallback_value: Value to return if execution fails
            retry_enabled: Whether to enable retry mechanism
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback value
        """
        try:
            if retry_enabled:
                return self.retry_mechanism.retry(func, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e, should_raise=False)
            return fallback_value
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get comprehensive error summary."""
        return self.reporter.get_error_summary()
    
    def clear_errors(self):
        """Clear all stored error information."""
        self.reporter.clear_errors()


def safe_execute(func: Optional[Callable] = None, 
                fallback_value: Any = None,
                retry_enabled: bool = False):
    """
    Decorator for safe function execution with error handling.
    
    Args:
        func: Function to decorate (for direct decoration)
        fallback_value: Value to return on error
        retry_enabled: Whether to enable retry mechanism
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            error_handler = XErrorHandler()
            return error_handler.safe_execute(
                f, *args, 
                fallback_value=fallback_value,
                retry_enabled=retry_enabled,
                **kwargs
            )
        return wrapper
    
    # Support both @safe_execute and @safe_execute() syntax
    if func is None:
        return decorator
    else:
        return decorator(func)


# Global error handler instance
error_handler = XErrorHandler() 