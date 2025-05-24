#!/usr/bin/env python3
"""
POC 21: Circuit Breaker Pattern
Task: Implement circuit breaker for preventing cascading failures
Expected Output: Circuit state transitions and failure prevention
Links:
- https://martinfowler.com/bliki/CircuitBreaker.html
- https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures exceeded threshold
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: float = 60.0  # Seconds before trying half-open
    window_size: float = 60.0  # Time window for counting failures
    half_open_max_calls: int = 3
    excluded_exceptions: List[type] = field(default_factory=list)


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    state_transitions: List[Tuple[CircuitState, datetime]] = field(default_factory=list)
    last_failure_time: Optional[datetime] = None
    consecutive_successes: int = 0
    consecutive_failures: int = 0


class CircuitOpenError(Exception):
    """Raised when circuit is open"""
    pass


class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self.failure_timestamps: List[datetime] = []
        self.half_open_calls = 0
        self.state_changed_at = datetime.now()
        
        # Record initial state
        self.stats.state_transitions.append((self.state, self.state_changed_at))
    
    def _change_state(self, new_state: CircuitState) -> None:
        """Change circuit state and log transition"""
        if new_state != self.state:
            old_state = self.state
            self.state = new_state
            self.state_changed_at = datetime.now()
            self.stats.state_transitions.append((new_state, self.state_changed_at))
            
            if new_state == CircuitState.HALF_OPEN:
                self.half_open_calls = 0
            
            logger.info(f"🔄 Circuit '{self.name}' state: {old_state.value} → {new_state.value}")
    
    def _record_success(self) -> None:
        """Record successful call"""
        self.stats.total_calls += 1
        self.stats.successful_calls += 1
        self.stats.consecutive_successes += 1
        self.stats.consecutive_failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.stats.consecutive_successes >= self.config.success_threshold:
                self._change_state(CircuitState.CLOSED)
                logger.success(f"✅ Circuit '{self.name}' recovered - closing circuit")
    
    def _record_failure(self, error: Exception) -> None:
        """Record failed call"""
        self.stats.total_calls += 1
        self.stats.failed_calls += 1
        self.stats.consecutive_failures += 1
        self.stats.consecutive_successes = 0
        self.stats.last_failure_time = datetime.now()
        
        # Add to failure window
        self.failure_timestamps.append(datetime.now())
        self._clean_failure_window()
        
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            self._change_state(CircuitState.OPEN)
            logger.warning(f"⚠️  Circuit '{self.name}' test failed - reopening")
        
        elif self.state == CircuitState.CLOSED:
            if len(self.failure_timestamps) >= self.config.failure_threshold:
                self._change_state(CircuitState.OPEN)
                logger.error(f"❌ Circuit '{self.name}' opened - threshold exceeded")
    
    def _clean_failure_window(self) -> None:
        """Remove old failures outside the window"""
        cutoff = datetime.now() - timedelta(seconds=self.config.window_size)
        self.failure_timestamps = [
            ts for ts in self.failure_timestamps if ts > cutoff
        ]
    
    def _should_attempt_reset(self) -> bool:
        """Check if timeout has passed for reset attempt"""
        return (
            self.state == CircuitState.OPEN and
            (datetime.now() - self.state_changed_at).total_seconds() > self.config.timeout
        )
    
    def _is_excluded_exception(self, error: Exception) -> bool:
        """Check if exception should be excluded from circuit breaker"""
        return any(isinstance(error, exc_type) for exc_type in self.config.excluded_exceptions)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        # Check if we should try to reset
        if self._should_attempt_reset():
            self._change_state(CircuitState.HALF_OPEN)
            logger.info(f"🔄 Circuit '{self.name}' attempting reset")
        
        # Check circuit state
        if self.state == CircuitState.OPEN:
            self.stats.rejected_calls += 1
            raise CircuitOpenError(
                f"Circuit breaker '{self.name}' is OPEN. "
                f"Waiting {self.config.timeout}s before retry."
            )
        
        # Check half-open call limit
        if (self.state == CircuitState.HALF_OPEN and 
            self.half_open_calls >= self.config.half_open_max_calls):
            self.stats.rejected_calls += 1
            raise CircuitOpenError(
                f"Circuit breaker '{self.name}' half-open call limit reached"
            )
        
        # Execute the function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            self._record_success()
            return result
            
        except Exception as e:
            if not self._is_excluded_exception(e):
                self._record_failure(e)
            raise
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current circuit breaker state information"""
        self._clean_failure_window()
        
        return {
            "name": self.name,
            "state": self.state.value,
            "stats": {
                "total_calls": self.stats.total_calls,
                "successful_calls": self.stats.successful_calls,
                "failed_calls": self.stats.failed_calls,
                "rejected_calls": self.stats.rejected_calls,
                "success_rate": (
                    self.stats.successful_calls / self.stats.total_calls * 100
                    if self.stats.total_calls > 0 else 0
                ),
                "consecutive_successes": self.stats.consecutive_successes,
                "consecutive_failures": self.stats.consecutive_failures,
                "recent_failures": len(self.failure_timestamps),
            },
            "time_in_state": (datetime.now() - self.state_changed_at).total_seconds(),
            "state_transitions": len(self.stats.state_transitions)
        }
    
    def reset(self) -> None:
        """Manually reset the circuit breaker"""
        self._change_state(CircuitState.CLOSED)
        self.failure_timestamps.clear()
        self.stats.consecutive_failures = 0
        self.stats.consecutive_successes = 0
        logger.info(f"🔄 Circuit '{self.name}' manually reset")


# Test service for demonstration
class TestService:
    """Mock service for testing circuit breaker"""
    
    def __init__(self):
        self.call_count = 0
        self.fail_count = 0
        self.should_fail = False
        self.fail_pattern = []
    
    async def make_request(self, data: str) -> Dict[str, Any]:
        """Simulate API request"""
        self.call_count += 1
        
        # Use fail pattern if provided
        if self.fail_pattern and self.call_count <= len(self.fail_pattern):
            should_fail = self.fail_pattern[self.call_count - 1]
        else:
            should_fail = self.should_fail
        
        if should_fail:
            self.fail_count += 1
            raise Exception(f"Service error on call {self.call_count}")
        
        return {"success": True, "data": data, "call": self.call_count}


async def main():
    """Test circuit breaker functionality"""
    
    logger.info("=" * 60)
    logger.info("CIRCUIT BREAKER TESTING")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    
    # Test 1: Basic circuit opening on threshold
    logger.info("\n🧪 Test 1: Circuit opens after failure threshold")
    logger.info("-" * 40)
    
    config = CircuitBreakerConfig(
        failure_threshold=3,
        timeout=2.0,
        window_size=10.0
    )
    breaker = CircuitBreaker("test1", config)
    service = TestService()
    service.should_fail = True
    
    # Make calls until circuit opens
    for i in range(4):
        try:
            await breaker.call(service.make_request, f"data_{i}")
        except CircuitOpenError:
            logger.info(f"Call {i+1}: Circuit is open")
            if i == 3:  # Should be open on 4th call
                passed += 1
                logger.success("✅ Circuit opened correctly after threshold")
            break
        except Exception as e:
            logger.warning(f"Call {i+1}: {e}")
    else:
        failed += 1
        logger.error("❌ Circuit did not open as expected")
    
    # Test 2: Circuit recovery in half-open state
    logger.info("\n🧪 Test 2: Circuit recovery through half-open state")
    logger.info("-" * 40)
    
    # Wait for timeout
    logger.info("Waiting for timeout...")
    await asyncio.sleep(2.5)
    
    # Service should succeed now
    service.should_fail = False
    
    # Make successful calls to close circuit
    for i in range(3):
        try:
            result = await breaker.call(service.make_request, f"recovery_{i}")
            logger.success(f"Call {i+1}: Success - {result}")
        except Exception as e:
            logger.error(f"Call {i+1}: {e}")
    
    if breaker.state == CircuitState.CLOSED:
        passed += 1
        logger.success("✅ Circuit recovered and closed")
    else:
        failed += 1
        logger.error(f"❌ Circuit did not close, state: {breaker.state.value}")
    
    # Test 3: Half-open failure returns to open
    logger.info("\n🧪 Test 3: Half-open failure returns to open")
    logger.info("-" * 40)
    
    config2 = CircuitBreakerConfig(
        failure_threshold=2,
        success_threshold=2,
        timeout=1.0
    )
    breaker2 = CircuitBreaker("test3", config2)
    service2 = TestService()
    
    # Open the circuit
    service2.should_fail = True
    for i in range(3):
        try:
            await breaker2.call(service2.make_request, "fail")
        except:
            pass
    
    # Wait for timeout
    await asyncio.sleep(1.5)
    
    # Still failing - should return to open
    try:
        await breaker2.call(service2.make_request, "still_fail")
    except Exception:
        pass
    
    if breaker2.state == CircuitState.OPEN:
        passed += 1
        logger.success("✅ Circuit returned to OPEN after half-open failure")
    else:
        failed += 1
        logger.error(f"❌ Circuit state incorrect: {breaker2.state.value}")
    
    # Test 4: Sliding window for failures
    logger.info("\n🧪 Test 4: Sliding window for failure counting")
    logger.info("-" * 40)
    
    config3 = CircuitBreakerConfig(
        failure_threshold=3,
        window_size=2.0  # 2 second window
    )
    breaker3 = CircuitBreaker("test4", config3)
    service3 = TestService()
    
    # Pattern: fail, wait, fail, wait, fail (spread over time)
    service3.fail_pattern = [True, True, False, True, True]
    
    for i in range(5):
        try:
            await breaker3.call(service3.make_request, f"window_{i}")
            logger.success(f"Call {i+1}: Success")
        except CircuitOpenError:
            logger.info(f"Call {i+1}: Circuit open")
        except Exception as e:
            logger.warning(f"Call {i+1}: {e}")
        
        if i < 4:
            await asyncio.sleep(0.8)  # Spread calls over time
    
    # Check that old failures were cleaned from window
    state_info = breaker3.get_state_info()
    if state_info["stats"]["recent_failures"] <= 3:
        passed += 1
        logger.success("✅ Sliding window correctly limits failure count")
    else:
        failed += 1
        logger.error("❌ Sliding window not working correctly")
    
    # Test 5: Excluded exceptions
    logger.info("\n🧪 Test 5: Excluded exceptions don't affect circuit")
    logger.info("-" * 40)
    
    class BusinessError(Exception):
        """Business logic error - not a system failure"""
        pass
    
    config4 = CircuitBreakerConfig(
        failure_threshold=2,
        excluded_exceptions=[BusinessError]
    )
    breaker4 = CircuitBreaker("test5", config4)
    
    # Raise excluded exceptions
    async def raise_business_error():
        raise BusinessError("Business validation failed")
    
    for i in range(3):
        try:
            await breaker4.call(raise_business_error)
        except BusinessError:
            logger.info(f"Call {i+1}: Business error (excluded)")
    
    if breaker4.state == CircuitState.CLOSED:
        passed += 1
        logger.success("✅ Excluded exceptions don't open circuit")
    else:
        failed += 1
        logger.error("❌ Circuit opened on excluded exception")
    
    # Display final statistics
    logger.info("\n" + "=" * 60)
    logger.info("CIRCUIT BREAKER STATISTICS")
    logger.info("=" * 60)
    
    for breaker_instance in [breaker, breaker2, breaker3, breaker4]:
        info = breaker_instance.get_state_info()
        logger.info(f"\nCircuit: {info['name']}")
        logger.info(f"  State: {info['state']}")
        logger.info(f"  Total calls: {info['stats']['total_calls']}")
        logger.info(f"  Success rate: {info['stats']['success_rate']:.1f}%")
        logger.info(f"  Rejected calls: {info['stats']['rejected_calls']}")
        logger.info(f"  State transitions: {info['state_transitions']}")
    
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