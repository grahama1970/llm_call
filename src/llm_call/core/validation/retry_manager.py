"""
Staged Retry Manager with Escalation
Module: retry_manager.py

This module implements a sophisticated retry mechanism with three stages:
1. Basic retry attempts (standard retries)
2. Tool-assisted retry stage (with additional capabilities)
3. Human review escalation (final stage)

Based on research findings:
- Tenacity for flexible retry patterns
- Context preservation across attempts
- Traffic multiplication awareness
- Progressive escalation with clear triggers

Documentation:
- Tenacity: https://tenacity.readthedocs.io/
- Retry patterns: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

Sample input:
{
    "max_attempts": 5,
    "max_attempts_before_tool_use": 2,
    "max_attempts_before_human": 4,
    "backoff_base": 2.0,
    "backoff_max": 60.0
}

Expected output:
RetryResult with stage info, context, and final result or HumanReviewNeededError
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel, Field
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_chain,
    wait_fixed
)


class RetryStage(Enum):
    """Enumeration of retry stages"""
    BASIC = "basic"
    TOOL_ASSISTED = "tool_assisted"
    HUMAN_REVIEW = "human_review"


class HumanReviewNeededError(Exception):
    """Raised when human review is required after all retry attempts"""
    
    def __init__(self, message: str, context: Dict[str, Any], validation_errors: List[str]):
        super().__init__(message)
        self.context = context
        self.validation_errors = validation_errors
        self.timestamp = datetime.utcnow()


class ValidationError(Exception):
    """Base validation error with structured information"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class RetryConfig(BaseModel):
    """Configuration for staged retry behavior"""
    
    max_attempts: int = Field(default=5, description="Total maximum retry attempts")
    max_attempts_before_tool_use: int = Field(default=2, description="Attempts before enabling tools")
    max_attempts_before_human: int = Field(default=4, description="Attempts before human review")
    backoff_base: float = Field(default=2.0, description="Base for exponential backoff")
    backoff_max: float = Field(default=60.0, description="Maximum backoff time in seconds")
    debug_mode: bool = Field(default=False, description="Enable detailed logging")
    
    def model_post_init(self, __context):
        """Validate configuration logic"""
        if self.max_attempts_before_tool_use >= self.max_attempts_before_human:
            raise ValueError("Tool use must come before human review")
        if self.max_attempts_before_human > self.max_attempts:
            raise ValueError("Human review threshold cannot exceed max attempts")


@dataclass
class RetryContext:
    """Context preserved across retry attempts"""
    
    original_request: Dict[str, Any]
    validation_errors: List[str] = field(default_factory=list)
    stage_history: List[RetryStage] = field(default_factory=list)
    attempt_count: int = 0
    current_stage: RetryStage = RetryStage.BASIC
    tool_results: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, error: str, stage: Optional[RetryStage] = None):
        """Add validation error with stage information"""
        stage = stage or self.current_stage
        self.validation_errors.append(f"[{stage.value}] {error}")
        
    def transition_stage(self, new_stage: RetryStage):
        """Transition to new retry stage"""
        self.stage_history.append(self.current_stage)
        self.current_stage = new_stage
        logger.info(f"Retry stage transition: {self.stage_history[-1].value} → {new_stage.value}")
        
    def build_retry_message(self) -> str:
        """Build context message for retry attempt"""
        parts = [
            f"Retry attempt {self.attempt_count + 1}",
            f"Current stage: {self.current_stage.value}",
            f"Previous errors: {len(self.validation_errors)}"
        ]
        
        if self.validation_errors:
            recent_errors = self.validation_errors[-3:]  # Last 3 errors
            parts.append("Recent validation errors:")
            parts.extend(f"  - {error}" for error in recent_errors)
            
        if self.tool_results:
            parts.append(f"Tool assistance available: {list(self.tool_results.keys())}")
            
        return "\n".join(parts)


class StagedRetryManager:
    """Manages staged retry logic with escalation"""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self._retry_callbacks: Dict[RetryStage, List[Callable]] = {
            stage: [] for stage in RetryStage
        }
        
    def register_stage_callback(self, stage: RetryStage, callback: Callable):
        """Register callback for stage transition"""
        self._retry_callbacks[stage].append(callback)
        
    async def _execute_stage_callbacks(self, stage: RetryStage, context: RetryContext):
        """Execute all callbacks for a stage"""
        for callback in self._retry_callbacks[stage]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(context)
                else:
                    callback(context)
            except Exception as e:
                logger.error(f"Stage callback error: {e}")
                
    def _determine_stage(self, attempt: int) -> RetryStage:
        """Determine retry stage based on attempt count"""
        if attempt >= self.config.max_attempts_before_human:
            return RetryStage.HUMAN_REVIEW
        elif attempt >= self.config.max_attempts_before_tool_use:
            return RetryStage.TOOL_ASSISTED
        return RetryStage.BASIC
        
    def _create_wait_strategy(self):
        """Create Tenacity wait strategy based on stages"""
        # Basic stage: exponential backoff
        basic_waits = [
            wait_exponential(
                multiplier=self.config.backoff_base,
                max=self.config.backoff_max
            )
        ] * self.config.max_attempts_before_tool_use
        
        # Tool-assisted stage: longer waits for tool processing
        tool_waits = [
            wait_fixed(5)  # Fixed 5s for tool calls
        ] * (self.config.max_attempts_before_human - self.config.max_attempts_before_tool_use)
        
        # Human review stage: minimal wait
        human_waits = [wait_fixed(1)]
        
        return wait_chain(*(basic_waits + tool_waits + human_waits))
        
    async def execute_with_retry(
        self,
        func: Callable,
        context: RetryContext,
        validation_func: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """Execute function with staged retry logic"""
        
        wait_strategy = self._create_wait_strategy()
        
        async def before_retry(retry_state: RetryCallState):
            """Handle retry logic before each attempt"""
            attempt = retry_state.attempt_number
            context.attempt_count = attempt
            
            # Determine and transition stage
            new_stage = self._determine_stage(attempt)
            if new_stage != context.current_stage:
                context.transition_stage(new_stage)
                await self._execute_stage_callbacks(new_stage, context)
                
            # Log retry information
            if self.config.debug_mode:
                logger.debug(f"Retry attempt {attempt}: {context.build_retry_message()}")
                
        async def after_retry(retry_state: RetryCallState):
            """Handle post-retry logic"""
            if retry_state.outcome.failed:
                error = str(retry_state.outcome.exception())
                context.add_error(error)
                
        async def wrapped_func():
            """Wrapped function with validation"""
            # Check if we should escalate to human review
            if context.current_stage == RetryStage.HUMAN_REVIEW:
                raise HumanReviewNeededError(
                    "Human review required after retry exhaustion",
                    context=context.original_request,
                    validation_errors=context.validation_errors
                )
                
            # Execute the function
            result = await func(**kwargs, retry_context=context)
            
            # Validate if validation function provided
            if validation_func:
                validation_result = await validation_func(result, context)
                if not validation_result.get("valid", False):
                    error_msg = validation_result.get("error", "Validation failed")
                    raise ValidationError(error_msg, validation_result)
                    
            return result
            
        # Create retrying instance
        retrying = AsyncRetrying(
            stop=stop_after_attempt(self.config.max_attempts),
            wait=wait_strategy,
            retry=retry_if_exception_type((ValidationError, Exception)),
            before=before_retry,
            after=after_retry,
            reraise=True
        )
        
        try:
            return await retrying(wrapped_func)
        except HumanReviewNeededError:
            # Re-raise human review errors
            raise
        except Exception as e:
            # Check if we should escalate to human review
            if context.attempt_count >= self.config.max_attempts_before_human:
                raise HumanReviewNeededError(
                    f"Human review required: {str(e)}",
                    context=context.original_request,
                    validation_errors=context.validation_errors
                )
            raise


# Validation function for testing
if __name__ == "__main__":
    import json
    
    async def test_function(value: int, retry_context: RetryContext) -> Dict[str, Any]:
        """Test function that fails based on value"""
        # Simulate different behaviors based on retry stage
        if retry_context.current_stage == RetryStage.TOOL_ASSISTED:
            # Tool assistance might help
            if value < 5 and retry_context.attempt_count >= 3:
                # Tool assistance successfully fixes the value
                return {"success": True, "value": value * 3, "stage": "tool_assisted"}
                
        # Basic attempts fail for low values
        if value < 10:
            raise ValueError(f"Value {value} too low")
            
        return {"success": True, "value": value, "stage": "basic"}
        
    async def validate_result(result: Dict[str, Any], context: RetryContext) -> Dict[str, bool]:
        """Validate the result"""
        if result.get("value", 0) < 5:
            return {"valid": False, "error": "Result value still too low"}
        return {"valid": True}
        
    async def tool_callback(context: RetryContext):
        """Callback when entering tool-assisted stage"""
        print(f" Entering tool-assisted stage after {context.attempt_count} attempts")
        context.tool_results = {"multiplier_tool": "available"}
        
    async def human_callback(context: RetryContext):
        """Callback when entering human review stage"""
        print(f" Escalating to human review after {context.attempt_count} attempts")
        print(f"Validation errors: {len(context.validation_errors)}")
        
    async def main():
        """Test the retry manager"""
        # Test configuration
        config = RetryConfig(
            max_attempts=5,
            max_attempts_before_tool_use=2,
            max_attempts_before_human=4,
            debug_mode=True
        )
        
        manager = StagedRetryManager(config)
        manager.register_stage_callback(RetryStage.TOOL_ASSISTED, tool_callback)
        manager.register_stage_callback(RetryStage.HUMAN_REVIEW, human_callback)
        
        # Test 1: Success in basic stage
        print("\n=== Test 1: Basic Success ===")
        context1 = RetryContext(original_request={"test": 1})
        try:
            result = await manager.execute_with_retry(
                test_function,
                context1,
                validate_result,
                value=15
            )
            print(f" Success: {result}")
            print(f"Final stage: {context1.current_stage.value}")
        except Exception as e:
            print(f" Failed: {e}")
            
        # Test 2: Success with tool assistance
        print("\n=== Test 2: Tool-Assisted Success ===")
        context2 = RetryContext(original_request={"test": 2})
        try:
            result = await manager.execute_with_retry(
                test_function,
                context2,
                validate_result,
                value=3
            )
            print(f" Success: {result}")
            print(f"Final stage: {context2.current_stage.value}")
            print(f"Total attempts: {context2.attempt_count}")
        except Exception as e:
            print(f" Failed: {e}")
            
        # Test 3: Human review needed
        print("\n=== Test 3: Human Review Escalation ===")
        context3 = RetryContext(original_request={"test": 3})
        try:
            result = await manager.execute_with_retry(
                test_function,
                context3,
                validate_result,
                value=1
            )
            print(f" Success: {result}")
        except HumanReviewNeededError as e:
            print(f" Human review required: {e}")
            print(f"Total errors: {len(e.validation_errors)}")
            print(f"Stage history: {[s.value for s in context3.stage_history]}")
        except Exception as e:
            print(f" Unexpected error: {e}")
            
        # Test 4: Configuration validation
        print("\n=== Test 4: Config Validation ===")
        try:
            bad_config = RetryConfig(
                max_attempts=5,
                max_attempts_before_tool_use=4,
                max_attempts_before_human=3  # Invalid: tool > human
            )
        except ValueError as e:
            print(f" Config validation caught error: {e}")
            
        print("\n All tests completed")
        
    asyncio.run(main())