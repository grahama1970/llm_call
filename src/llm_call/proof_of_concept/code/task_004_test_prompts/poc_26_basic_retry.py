#!/usr/bin/env python3
"""
POC 20: Retry Strategies Implementation
Task: Implement various retry strategies for validation failures
Expected Output: Successful retries with appropriate backoff and jitter
Links:
- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- https://github.com/litl/backoff
"""

import asyncio
import random
import time
from typing import Dict, Any, Optional, Callable, List, Union
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


class RetryableError(Exception):
    """Error that can be retried"""
    pass


class NonRetryableError(Exception):
    """Error that should not be retried"""
    pass


class RetryStrategy(Enum):
    """Available retry strategies"""
    IMMEDIATE = "immediate"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"
    FIBONACCI = "fibonacci"
    CUSTOM = "custom"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_JITTER
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter_range: float = 0.3  # ±30% jitter
    retry_on: List[type] = field(default_factory=lambda: [RetryableError, asyncio.TimeoutError])
    custom_backoff: Optional[Callable[[int], float]] = None


@dataclass
class RetryResult:
    """Result of a retry operation"""
    success: bool
    attempts: int
    total_time: float
    final_result: Optional[Any] = None
    final_error: Optional[Exception] = None
    delays: List[float] = field(default_factory=list)


class RetryManager:
    """Manages retry logic with various strategies"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self._fibonacci_cache = {}
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay based on strategy"""
        if self.config.strategy == RetryStrategy.IMMEDIATE:
            return 0
        
        elif self.config.strategy == RetryStrategy.LINEAR:
            delay = self.config.initial_delay * attempt
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.config.initial_delay * (self.config.exponential_base ** (attempt - 1))
        
        elif self.config.strategy == RetryStrategy.EXPONENTIAL_JITTER:
            base_delay = self.config.initial_delay * (self.config.exponential_base ** (attempt - 1))
            jitter = base_delay * self.config.jitter_range
            delay = base_delay + random.uniform(-jitter, jitter)
        
        elif self.config.strategy == RetryStrategy.FIBONACCI:
            delay = self.config.initial_delay * self._fibonacci(attempt)
        
        elif self.config.strategy == RetryStrategy.CUSTOM and self.config.custom_backoff:
            delay = self.config.custom_backoff(attempt)
        
        else:
            delay = self.config.initial_delay
        
        # Cap at max delay
        return min(delay, self.config.max_delay)
    
    def _fibonacci(self, n: int) -> int:
        """Calculate fibonacci number with caching"""
        if n in self._fibonacci_cache:
            return self._fibonacci_cache[n]
        
        if n <= 1:
            return n
        
        result = self._fibonacci(n - 1) + self._fibonacci(n - 2)
        self._fibonacci_cache[n] = result
        return result
    
    def should_retry(self, error: Exception) -> bool:
        """Determine if error is retryable"""
        return any(isinstance(error, error_type) for error_type in self.config.retry_on)
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> RetryResult:
        """Execute function with retry logic"""
        start_time = time.time()
        attempts = 0
        delays = []
        
        for attempt in range(1, self.config.max_attempts + 1):
            attempts = attempt
            
            try:
                # Execute the function
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                total_time = time.time() - start_time
                logger.success(f"✅ Success on attempt {attempt}")
                
                return RetryResult(
                    success=True,
                    attempts=attempts,
                    total_time=total_time,
                    final_result=result,
                    delays=delays
                )
                
            except Exception as e:
                if not self.should_retry(e) or attempt == self.config.max_attempts:
                    # Non-retryable error or max attempts reached
                    total_time = time.time() - start_time
                    logger.error(f"❌ Failed after {attempt} attempts: {e}")
                    
                    return RetryResult(
                        success=False,
                        attempts=attempts,
                        total_time=total_time,
                        final_error=e,
                        delays=delays
                    )
                
                # Calculate and apply delay
                delay = self.calculate_delay(attempt)
                delays.append(delay)
                
                logger.warning(f"⚠️  Attempt {attempt} failed: {e}")
                logger.info(f"⏱️  Waiting {delay:.2f}s before retry...")
                
                await asyncio.sleep(delay) if asyncio.iscoroutinefunction(func) else time.sleep(delay)


# Test functions for demonstration
class MockValidationService:
    """Mock service for testing retry logic"""
    
    def __init__(self):
        self.call_count = 0
        self.fail_until = 0
        self.error_sequence = []
    
    def reset(self):
        """Reset service state"""
        self.call_count = 0
        self.fail_until = 0
        self.error_sequence = []
    
    async def validate_with_transient_error(self, data: str) -> Dict[str, Any]:
        """Simulates transient errors that resolve"""
        self.call_count += 1
        
        if self.call_count <= self.fail_until:
            raise RetryableError(f"Transient error on call {self.call_count}")
        
        return {"valid": True, "data": data}
    
    async def validate_with_error_sequence(self, data: str) -> Dict[str, Any]:
        """Simulates specific error sequence"""
        self.call_count += 1
        
        if self.error_sequence and self.call_count <= len(self.error_sequence):
            error_type = self.error_sequence[self.call_count - 1]
            if error_type:
                raise error_type(f"Error on call {self.call_count}")
        
        return {"valid": True, "data": data}
    
    def validate_sync(self, data: str) -> Dict[str, Any]:
        """Synchronous validation for testing"""
        self.call_count += 1
        
        if self.call_count <= self.fail_until:
            raise RetryableError(f"Sync error on call {self.call_count}")
        
        return {"valid": True, "data": data}


async def main():
    """Test retry strategies with various scenarios"""
    
    # Test scenarios
    test_cases = [
        {
            "name": "Exponential Backoff with Jitter",
            "config": RetryConfig(
                strategy=RetryStrategy.EXPONENTIAL_JITTER,
                max_attempts=4,
                initial_delay=0.5
            ),
            "fail_until": 2,
            "expected_success": True
        },
        {
            "name": "Linear Backoff",
            "config": RetryConfig(
                strategy=RetryStrategy.LINEAR,
                max_attempts=3,
                initial_delay=0.3
            ),
            "fail_until": 2,
            "expected_success": True
        },
        {
            "name": "Immediate Retry",
            "config": RetryConfig(
                strategy=RetryStrategy.IMMEDIATE,
                max_attempts=5
            ),
            "fail_until": 3,
            "expected_success": True
        },
        {
            "name": "Fibonacci Backoff",
            "config": RetryConfig(
                strategy=RetryStrategy.FIBONACCI,
                max_attempts=4,
                initial_delay=0.2
            ),
            "fail_until": 3,
            "expected_success": True
        },
        {
            "name": "Max Attempts Exceeded",
            "config": RetryConfig(
                strategy=RetryStrategy.EXPONENTIAL,
                max_attempts=2
            ),
            "fail_until": 3,
            "expected_success": False
        },
        {
            "name": "Custom Backoff Function",
            "config": RetryConfig(
                strategy=RetryStrategy.CUSTOM,
                max_attempts=3,
                custom_backoff=lambda attempt: 0.1 * (attempt ** 2)
            ),
            "fail_until": 2,
            "expected_success": True
        }
    ]
    
    logger.info("=" * 60)
    logger.info("RETRY STRATEGIES TESTING")
    logger.info("=" * 60)
    
    service = MockValidationService()
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        logger.info(f"\n🧪 Testing: {test_case['name']}")
        logger.info("-" * 40)
        
        # Reset service
        service.reset()
        service.fail_until = test_case["fail_until"]
        
        # Create retry manager
        retry_manager = RetryManager(test_case["config"])
        
        # Execute with retry
        result = await retry_manager.execute_with_retry(
            service.validate_with_transient_error,
            "test_data"
        )
        
        # Verify result
        if result.success == test_case["expected_success"]:
            passed += 1
            logger.success(f"✅ Test passed: {test_case['name']}")
            logger.info(f"   Attempts: {result.attempts}")
            logger.info(f"   Total time: {result.total_time:.2f}s")
            if result.delays:
                logger.info(f"   Delays: {[f'{d:.2f}s' for d in result.delays]}")
        else:
            failed += 1
            logger.error(f"❌ Test failed: {test_case['name']}")
            logger.error(f"   Expected success={test_case['expected_success']}, got {result.success}")
    
    # Test mixed error types
    logger.info("\n" + "=" * 60)
    logger.info("TESTING ERROR TYPE HANDLING")
    logger.info("=" * 60)
    
    # Configure to retry only specific errors
    retry_config = RetryConfig(
        strategy=RetryStrategy.EXPONENTIAL_JITTER,
        max_attempts=3,
        retry_on=[RetryableError]  # Won't retry NonRetryableError
    )
    retry_manager = RetryManager(retry_config)
    
    # Test retryable errors
    service.reset()
    service.error_sequence = [RetryableError, RetryableError, None]  # Succeeds on 3rd
    
    result = await retry_manager.execute_with_retry(
        service.validate_with_error_sequence,
        "test_data"
    )
    
    if result.success and result.attempts == 3:
        passed += 1
        logger.success("✅ Retryable errors handled correctly")
    else:
        failed += 1
        logger.error("❌ Retryable error handling failed")
    
    # Test non-retryable errors
    service.reset()
    service.error_sequence = [NonRetryableError]
    
    result = await retry_manager.execute_with_retry(
        service.validate_with_error_sequence,
        "test_data"
    )
    
    if not result.success and result.attempts == 1:
        passed += 1
        logger.success("✅ Non-retryable errors stopped immediately")
    else:
        failed += 1
        logger.error("❌ Non-retryable error handling failed")
    
    # Test synchronous function retry
    logger.info("\n" + "=" * 60)
    logger.info("TESTING SYNCHRONOUS RETRY")
    logger.info("=" * 60)
    
    service.reset()
    service.fail_until = 2
    
    # Note: For sync functions, we need to use sync sleep
    sync_config = RetryConfig(
        strategy=RetryStrategy.LINEAR,
        max_attempts=3,
        initial_delay=0.1
    )
    sync_retry_manager = RetryManager(sync_config)
    
    # Execute sync function with retry
    result = await sync_retry_manager.execute_with_retry(
        service.validate_sync,
        "sync_test"
    )
    
    if result.success:
        passed += 1
        logger.success("✅ Synchronous retry works correctly")
    else:
        failed += 1
        logger.error("❌ Synchronous retry failed")
    
    # Performance comparison
    logger.info("\n" + "=" * 60)
    logger.info("STRATEGY PERFORMANCE COMPARISON")
    logger.info("=" * 60)
    
    strategies = [
        RetryStrategy.IMMEDIATE,
        RetryStrategy.LINEAR,
        RetryStrategy.EXPONENTIAL,
        RetryStrategy.EXPONENTIAL_JITTER,
        RetryStrategy.FIBONACCI
    ]
    
    for strategy in strategies:
        config = RetryConfig(strategy=strategy, max_attempts=5)
        manager = RetryManager(config)
        
        # Calculate total delay for 4 retries
        total_delay = sum(manager.calculate_delay(i) for i in range(1, 5))
        logger.info(f"{strategy.value:<20} - Total delay for 4 retries: {total_delay:.2f}s")
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    total_tests = passed + failed
    if failed == 0:
        logger.success(f"✅ ALL TESTS PASSED: {passed}/{total_tests}")
        return 0
    else:
        logger.error(f"❌ TESTS FAILED: {failed}/{total_tests} failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))