"""
Pipeline abstract base class for XpertCorpus.

This module defines a simple pipeline interface for orchestrating
multiple operators in sequence.

@author: rookielittleblack
@date:   2025-08-13
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from xpertcorpus.utils import xlogger, error_handler, safe_execute
from xpertcorpus.modules.others.xoperator import OperatorABC


# Create pipeline registration decorator at module level
def register_pipeline(name: str):
    """
    Decorator for registering pipeline classes.
    
    Args:
        name: Pipeline name for registration
        
    Example:
        @register_pipeline("text_cleaning")
        class TextCleaningPipeline(PipelineABC):
            pass
    """
    def decorator(pipeline_class):
        from xpertcorpus.modules.others.xregistry import PIPELINE_REGISTRY
        PIPELINE_REGISTRY.register(pipeline_class, name)
        return pipeline_class
    return decorator


class PipelineState(Enum):
    """Pipeline lifecycle states."""
    INITIALIZED = "INITIALIZED"
    CONFIGURED = "CONFIGURED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"


class PipelineABC(ABC):
    """
    Abstract base class for data processing pipelines.
    
    Provides a simple interface for orchestrating multiple operators
    in sequence with basic lifecycle management.
    """
    
    def __init__(self, max_workers: int = 1, limit: int = 0, config: Optional[Dict[str, Any]] = None):
        """
        Initialize pipeline with basic parameters.
        
        Args:
            max_workers: Number of worker threads
            limit: Processing limit (0 for no limit)
            config: Optional configuration dictionary
        """
        self.max_workers = max_workers
        self.limit = limit
        self.config = config or {}
        self.state = PipelineState.INITIALIZED
        
        # Basic metadata
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "pipeline_name": self.__class__.__name__,
            "version": getattr(self, 'VERSION', '1.0.0')
        }
        
        # Simple metrics
        self.metrics = {
            "execution_count": 0,
            "total_processing_time": 0.0,
            "last_execution_time": None,
            "error_count": 0
        }
        
        # Operators managed by this pipeline
        self.operators: List[OperatorABC] = []
        
        # Initialize pipeline-specific components
        self._configure_operators()
    
    @abstractmethod
    def _configure_operators(self) -> None:
        """Configure and add operators to the pipeline. Override in subclasses."""
        pass
    
    @abstractmethod
    def run(self, storage, input_key: str = "raw_content", output_key: Optional[str] = None) -> str:
        """
        Execute the pipeline.
        
        Args:
            storage: Storage instance for data management
            input_key: Input data key
            output_key: Output data key (auto-generated if None)
            
        Returns:
            Output key for the processed data
        """
        pass
    
    @abstractmethod
    def get_desc(self, lang: str = "zh") -> str:
        """Get pipeline description."""
        pass
    
    def add_operator(self, operator: OperatorABC) -> 'PipelineABC':
        """
        Add operator to pipeline.
        
        Args:
            operator: Operator to add
            
        Returns:
            Self for method chaining
        """
        self.operators.append(operator)
        xlogger.debug(f"Added operator {operator.__class__.__name__} to pipeline")
        return self
    
    def get_operators(self) -> List[OperatorABC]:
        """Get list of operators in pipeline."""
        return self.operators.copy()
    
    def get_state(self) -> PipelineState:
        """Get current pipeline state."""
        return self.state
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get pipeline metadata."""
        return {
            **self.metadata,
            "current_state": self.state.value,
            "config": self.config.copy(),
            "operators_count": len(self.operators)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get pipeline performance metrics."""
        metrics = self.metrics.copy()
        if metrics["execution_count"] > 0:
            metrics["average_execution_time"] = (
                metrics["total_processing_time"] / metrics["execution_count"]
            )
        else:
            metrics["average_execution_time"] = 0.0
        return metrics
    
    def reset(self) -> 'PipelineABC':
        """
        Reset pipeline to initial state.
        
        Returns:
            Self for method chaining
        """
        self.state = PipelineState.INITIALIZED
        self.metrics = {
            "execution_count": 0,
            "total_processing_time": 0.0,
            "last_execution_time": None,
            "error_count": 0
        }
        xlogger.info(f"Pipeline {self.__class__.__name__} reset")
        return self
    
    def stop(self) -> None:
        """Stop the pipeline execution."""
        self.state = PipelineState.STOPPED
        xlogger.info(f"Pipeline {self.__class__.__name__} stopped")
    
    def __str__(self) -> str:
        """String representation of pipeline."""
        return f"{self.__class__.__name__}(state={self.state.value}, operators={len(self.operators)})"
    
    def __repr__(self) -> str:
        """Detailed string representation of pipeline."""
        return (f"{self.__class__.__name__}("
                f"state={self.state.value}, "
                f"operators={len(self.operators)}, "
                f"executions={self.metrics['execution_count']})") 