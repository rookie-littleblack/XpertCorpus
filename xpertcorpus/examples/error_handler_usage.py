"""
Example usage of XpertCorpus error handling utilities.

This example demonstrates how to use the error handling features
including error reporting, retry mechanisms, and safe execution.

@author: rookielittleblack
@date:   2025-08-13
"""
import time
import random

from xpertcorpus.utils import (
    XErrorHandler, 
    XRetryMechanism, 
    XErrorReporter,
    retry_on_failure,
    safe_execute,
    error_handler
)


def unreliable_network_call():
    """Simulate an unreliable network call that fails randomly."""
    if random.random() < 0.7:  # 70% failure rate
        raise ConnectionError("Network connection failed")
    return "Success!"


def data_processing_function(data):
    """Simulate data processing that might fail with various errors."""
    if not data:
        raise ValueError("Data cannot be empty")
    if not isinstance(data, list):
        raise TypeError("Data must be a list")
    if len(data) > 100:
        raise MemoryError("Data too large to process")
    return f"Processed {len(data)} items"


@retry_on_failure(max_retries=3, base_delay=0.5)
def network_operation_with_retry():
    """Network operation with automatic retry."""
    return unreliable_network_call()


@safe_execute(fallback_value="Default result", retry_enabled=True)
def safe_network_operation():
    """Network operation with safe execution."""
    return unreliable_network_call()


def main():
    """Demonstrate error handling features."""
    print("=== XpertCorpus Error Handler Demo ===\n")
    
    # 1. Basic error reporting
    print("1. Basic Error Reporting:")
    reporter = XErrorReporter()
    
    try:
        data_processing_function(None)
    except Exception as e:
        error_info = reporter.report_error(e, context={"operation": "data_validation"})
        print(f"   Error reported: {error_info.error_id}")
        print(f"   Severity: {error_info.severity.value}")
        print(f"   Category: {error_info.category.value}")
    
    # 2. Retry mechanism
    print("\n2. Retry Mechanism:")
    retry_mechanism = XRetryMechanism(max_retries=3, base_delay=0.1)
    
    try:
        result = retry_mechanism.retry(unreliable_network_call)
        print(f"   Retry successful: {result}")
    except Exception as e:
        print(f"   Retry failed after all attempts: {e}")
    
    # 3. Decorator-based retry
    print("\n3. Decorator-based Retry:")
    try:
        result = network_operation_with_retry()
        print(f"   Decorated retry successful: {result}")
    except Exception as e:
        print(f"   Decorated retry failed: {e}")
    
    # 4. Safe execution
    print("\n4. Safe Execution:")
    result = safe_network_operation()
    print(f"   Safe execution result: {result}")
    
    # 5. Manual error handling
    print("\n5. Manual Error Handling:")
    try:
        data_processing_function("invalid_data")
    except Exception as e:
        error_info = error_handler.handle_error(
            e, 
            context={"input_type": type("invalid_data").__name__},
            should_raise=False
        )
        if error_info:
            print(f"   Error handled: {error_info.message}")
    
    # 6. Safe execution with fallback
    print("\n6. Safe Execution with Fallback:")
    result = error_handler.safe_execute(
        data_processing_function,
        [],  # Valid empty list
        fallback_value="Processing failed"
    )
    print(f"   Safe execution result: {result}")
    
    # 7. Error summary
    print("\n7. Error Summary:")
    summary = error_handler.get_error_summary()
    print(f"   Total errors: {summary.get('total_errors', 0)}")
    if summary.get('severity_distribution'):
        print(f"   Severity distribution: {summary['severity_distribution']}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main() 