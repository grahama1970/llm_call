#!/usr/bin/env python3
"""
POC 30: Debug Mode Integration
Task: Implement comprehensive debug mode for retry and validation flows
Expected Output: Detailed debug information for troubleshooting validation failures
Links:
- https://docs.python.org/3/library/logging.html
- https://github.com/Delgan/loguru
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import inspect
import traceback
from loguru import logger
import sys

# Configure logger for debug mode
logger.remove()
logger.add(
    sys.stdout, 
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
    level="DEBUG"
)


@dataclass
class DebugEvent:
    """Represents a debug event in the validation flow"""
    timestamp: datetime
    event_type: str
    component: str
    details: Dict[str, Any]
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    stack_trace: Optional[str] = None


@dataclass
class DebugContext:
    """Maintains debug context throughout validation flow"""
    session_id: str
    debug_enabled: bool = True
    capture_stack_traces: bool = True
    log_payloads: bool = True
    events: List[DebugEvent] = field(default_factory=list)
    timers: Dict[str, float] = field(default_factory=dict)
    
    def start_timer(self, name: str):
        """Start a named timer"""
        self.timers[name] = time.time()
    
    def stop_timer(self, name: str) -> float:
        """Stop a timer and return duration in ms"""
        if name in self.timers:
            duration = (time.time() - self.timers[name]) * 1000
            del self.timers[name]
            return duration
        return 0.0
    
    def add_event(self, event_type: str, component: str, details: Dict[str, Any], error: Exception = None):
        """Add a debug event"""
        event = DebugEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            component=component,
            details=details,
            error=str(error) if error else None,
            stack_trace=traceback.format_exc() if error and self.capture_stack_traces else None
        )
        self.events.append(event)
        
        # Log based on event type
        if error:
            logger.error(f"[{component}] {event_type}: {error}")
            if self.capture_stack_traces:
                logger.debug(f"Stack trace:\n{event.stack_trace}")
        elif event_type.startswith("WARNING"):
            logger.warning(f"[{component}] {event_type}: {details}")
        else:
            logger.debug(f"[{component}] {event_type}: {details}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get debug session summary"""
        error_events = [e for e in self.events if e.error]
        warning_events = [e for e in self.events if e.event_type.startswith("WARNING")]
        
        return {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "errors": len(error_events),
            "warnings": len(warning_events),
            "components": list(set(e.component for e in self.events)),
            "duration_ms": self.events[-1].timestamp - self.events[0].timestamp if self.events else 0,
            "error_summary": [{"component": e.component, "error": e.error} for e in error_events]
        }


class DebugValidationWrapper:
    """Wraps validation functions with debug instrumentation"""
    
    def __init__(self, debug_context: DebugContext):
        self.debug_context = debug_context
    
    async def wrap_validation(self, 
                            validator_name: str,
                            validation_func: Callable,
                            input_data: Any) -> Dict[str, Any]:
        """Wrap a validation function with debug logging"""
        
        # Start timing
        self.debug_context.start_timer(f"validation_{validator_name}")
        
        # Log input
        self.debug_context.add_event(
            "VALIDATION_START",
            validator_name,
            {
                "input_type": type(input_data).__name__,
                "input_size": len(str(input_data)) if input_data else 0,
                "input_preview": str(input_data)[:200] if self.debug_context.log_payloads else "<redacted>"
            }
        )
        
        try:
            # Execute validation
            result = await validation_func(input_data) if asyncio.iscoroutinefunction(validation_func) else validation_func(input_data)
            
            # Stop timing
            duration = self.debug_context.stop_timer(f"validation_{validator_name}")
            
            # Log result
            self.debug_context.add_event(
                "VALIDATION_COMPLETE",
                validator_name,
                {
                    "valid": result.get("valid", False),
                    "duration_ms": duration,
                    "result_preview": str(result)[:200] if self.debug_context.log_payloads else "<redacted>"
                }
            )
            
            return result
            
        except Exception as e:
            # Stop timing
            duration = self.debug_context.stop_timer(f"validation_{validator_name}")
            
            # Log error
            self.debug_context.add_event(
                "VALIDATION_ERROR",
                validator_name,
                {
                    "duration_ms": duration,
                    "error_type": type(e).__name__
                },
                error=e
            )
            raise


class DebugRetryManager:
    """Retry manager with comprehensive debug support"""
    
    def __init__(self, debug_context: DebugContext):
        self.debug_context = debug_context
        self.validation_wrapper = DebugValidationWrapper(debug_context)
    
    async def retry_with_debug(self,
                             func: Callable,
                             validators: List[Dict[str, Any]],
                             max_attempts: int = 3,
                             backoff_factor: float = 2.0) -> Any:
        """Execute with retry and comprehensive debugging"""
        
        self.debug_context.add_event(
            "RETRY_FLOW_START",
            "RetryManager",
            {
                "max_attempts": max_attempts,
                "backoff_factor": backoff_factor,
                "validators": [v.get("name", "unknown") for v in validators]
            }
        )
        
        for attempt in range(max_attempts):
            self.debug_context.add_event(
                "ATTEMPT_START",
                "RetryManager",
                {"attempt": attempt + 1, "max_attempts": max_attempts}
            )
            
            try:
                # Execute function
                self.debug_context.start_timer(f"execution_attempt_{attempt}")
                result = await func() if asyncio.iscoroutinefunction(func) else func()
                exec_duration = self.debug_context.stop_timer(f"execution_attempt_{attempt}")
                
                self.debug_context.add_event(
                    "EXECUTION_COMPLETE",
                    "RetryManager",
                    {
                        "attempt": attempt + 1,
                        "duration_ms": exec_duration,
                        "result_type": type(result).__name__,
                        "result_size": len(str(result)) if result else 0
                    }
                )
                
                # Run validators
                all_valid = True
                validation_results = []
                
                for validator in validators:
                    validator_name = validator.get("name", "unknown")
                    validation_func = validator.get("func")
                    
                    if validation_func:
                        val_result = await self.validation_wrapper.wrap_validation(
                            validator_name,
                            validation_func,
                            result
                        )
                        validation_results.append({
                            "validator": validator_name,
                            "valid": val_result.get("valid", False),
                            "errors": val_result.get("errors", [])
                        })
                        
                        if not val_result.get("valid", False):
                            all_valid = False
                
                # Log validation summary
                self.debug_context.add_event(
                    "VALIDATION_SUMMARY",
                    "RetryManager",
                    {
                        "attempt": attempt + 1,
                        "all_valid": all_valid,
                        "results": validation_results
                    }
                )
                
                if all_valid:
                    self.debug_context.add_event(
                        "RETRY_FLOW_SUCCESS",
                        "RetryManager",
                        {"total_attempts": attempt + 1}
                    )
                    return result
                else:
                    # Calculate backoff
                    if attempt < max_attempts - 1:
                        delay = backoff_factor ** attempt
                        self.debug_context.add_event(
                            "BACKOFF_DELAY",
                            "RetryManager",
                            {
                                "attempt": attempt + 1,
                                "delay_seconds": delay,
                                "next_attempt": attempt + 2
                            }
                        )
                        await asyncio.sleep(delay)
                        
            except Exception as e:
                self.debug_context.add_event(
                    "ATTEMPT_ERROR",
                    "RetryManager",
                    {"attempt": attempt + 1},
                    error=e
                )
                
                if attempt >= max_attempts - 1:
                    raise
        
        # Max attempts reached
        self.debug_context.add_event(
            "RETRY_FLOW_FAILED",
            "RetryManager",
            {"total_attempts": max_attempts}
        )
        raise Exception("Max retry attempts reached")


def create_debug_report(debug_context: DebugContext) -> str:
    """Create a comprehensive debug report"""
    
    report = []
    report.append("=" * 80)
    report.append("DEBUG SESSION REPORT")
    report.append("=" * 80)
    
    summary = debug_context.get_summary()
    report.append(f"Session ID: {summary['session_id']}")
    report.append(f"Total Events: {summary['total_events']}")
    report.append(f"Errors: {summary['errors']}")
    report.append(f"Warnings: {summary['warnings']}")
    report.append(f"Components: {', '.join(summary['components'])}")
    report.append("")
    
    # Timeline
    report.append("EVENT TIMELINE:")
    report.append("-" * 80)
    
    for event in debug_context.events:
        timestamp = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
        level = "ERROR" if event.error else "WARN" if event.event_type.startswith("WARNING") else "INFO"
        report.append(f"{timestamp} [{level}] {event.component}: {event.event_type}")
        
        if event.details:
            for key, value in event.details.items():
                report.append(f"    {key}: {value}")
        
        if event.error:
            report.append(f"    ERROR: {event.error}")
    
    # Performance Summary
    report.append("")
    report.append("PERFORMANCE SUMMARY:")
    report.append("-" * 80)
    
    execution_events = [e for e in debug_context.events if "duration_ms" in e.details]
    if execution_events:
        total_time = sum(e.details.get("duration_ms", 0) for e in execution_events)
        report.append(f"Total Execution Time: {total_time:.2f}ms")
        
        # Breakdown by component
        component_times = {}
        for event in execution_events:
            component = event.component
            duration = event.details.get("duration_ms", 0)
            if component not in component_times:
                component_times[component] = 0
            component_times[component] += duration
        
        report.append("Time by Component:")
        for component, time_ms in sorted(component_times.items(), key=lambda x: x[1], reverse=True):
            percentage = (time_ms / total_time * 100) if total_time > 0 else 0
            report.append(f"  {component}: {time_ms:.2f}ms ({percentage:.1f}%)")
    
    # Error Details
    if summary['errors'] > 0:
        report.append("")
        report.append("ERROR DETAILS:")
        report.append("-" * 80)
        
        for event in debug_context.events:
            if event.error:
                report.append(f"\n{event.component} - {event.event_type}:")
                report.append(f"Error: {event.error}")
                if event.stack_trace:
                    report.append("Stack Trace:")
                    report.append(event.stack_trace)
    
    report.append("=" * 80)
    
    return "\n".join(report)


async def main():
    """Test debug mode functionality"""
    
    # Test scenarios
    async def successful_function():
        await asyncio.sleep(0.1)
        return {"result": "success", "data": [1, 2, 3]}
    
    async def failing_function():
        await asyncio.sleep(0.05)
        raise ValueError("Simulated failure")
    
    async def flaky_function(attempt=[0]):
        attempt[0] += 1
        await asyncio.sleep(0.05)
        if attempt[0] < 3:
            return {"result": "invalid"}
        return {"result": "valid"}
    
    # Validators
    def validate_success(result):
        return {"valid": result.get("result") == "success", "errors": [] if result.get("result") == "success" else ["Not success"]}
    
    def validate_valid(result):
        return {"valid": result.get("result") == "valid", "errors": [] if result.get("result") == "valid" else ["Not valid"]}
    
    logger.info("=" * 60)
    logger.info("DEBUG MODE TESTING")
    logger.info("=" * 60)
    
    # Test 1: Successful flow
    logger.info("\n🧪 Test 1: Successful validation flow")
    debug_ctx1 = DebugContext(session_id="TEST-001")
    retry_mgr1 = DebugRetryManager(debug_ctx1)
    
    try:
        result = await retry_mgr1.retry_with_debug(
            successful_function,
            [{"name": "SuccessValidator", "func": validate_success}],
            max_attempts=3
        )
        logger.success("✅ Test 1 passed")
    except Exception as e:
        logger.error(f"❌ Test 1 failed: {e}")
    
    # Test 2: Retry with eventual success
    logger.info("\n🧪 Test 2: Retry with eventual success")
    debug_ctx2 = DebugContext(session_id="TEST-002")
    retry_mgr2 = DebugRetryManager(debug_ctx2)
    
    try:
        result = await retry_mgr2.retry_with_debug(
            flaky_function,
            [{"name": "ValidValidator", "func": validate_valid}],
            max_attempts=5
        )
        logger.success("✅ Test 2 passed")
    except Exception as e:
        logger.error(f"❌ Test 2 failed: {e}")
    
    # Test 3: Complete failure
    logger.info("\n🧪 Test 3: Complete failure with debugging")
    debug_ctx3 = DebugContext(session_id="TEST-003")
    retry_mgr3 = DebugRetryManager(debug_ctx3)
    
    try:
        result = await retry_mgr3.retry_with_debug(
            failing_function,
            [{"name": "SuccessValidator", "func": validate_success}],
            max_attempts=2
        )
        logger.error("❌ Test 3 should have failed")
    except Exception as e:
        logger.success(f"✅ Test 3 correctly failed: {e}")
    
    # Generate debug reports
    logger.info("\n" + "=" * 60)
    logger.info("DEBUG REPORTS")
    logger.info("=" * 60)
    
    for i, ctx in enumerate([debug_ctx1, debug_ctx2, debug_ctx3], 1):
        logger.info(f"\n📊 Debug Report for Test {i}:")
        print(create_debug_report(ctx))
    
    # Test debug configuration options
    logger.info("\n" + "=" * 60)
    logger.info("DEBUG CONFIGURATION OPTIONS")
    logger.info("=" * 60)
    
    # Test with minimal logging
    debug_ctx4 = DebugContext(
        session_id="TEST-004",
        capture_stack_traces=False,
        log_payloads=False
    )
    logger.info("Testing with minimal debug logging (no stack traces, no payloads)")
    
    # Test with custom event
    debug_ctx4.add_event(
        "CUSTOM_EVENT",
        "TestComponent",
        {"custom_field": "custom_value", "sensitive_data": "should_be_redacted"}
    )
    
    logger.info(f"Minimal logging summary: {debug_ctx4.get_summary()}")
    
    logger.info("\n✅ Debug mode testing complete")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))