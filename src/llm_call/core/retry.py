"""
Retry mechanism with validation for LLM calls.
Module: retry.py

This module provides a sophisticated retry logic that integrates with validation strategies,
including staged retry with tool assistance and human escalation.

Key Features:
- Clear extraction of response content from various formats
- Proper error feedback to LLMs for self-correction
- Staged retry with tool injection after N attempts
- Human escalation after M attempts
- Dynamic MCP configuration injection
- Easy integration of custom validation strategies
- Comprehensive logging for debugging

Documentation:
- LiteLLM ModelResponse: https://docs.litellm.ai/docs/completion/response_object
- Retry patterns: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

## Usage Flow:

1. User calls make_llm_request(llm_config) with configuration dict
2. caller.py extracts validation and retry_config from llm_config
3. retry_with_validation is called with:
   - llm_call: provider.complete method
   - messages: from llm_config
   - response_format: from llm_config (optional)
   - validation_strategies: list of validators
   - config: RetryConfig from llm_config["retry_config"]
   - **kwargs: cleaned API parameters (model, temperature, etc.)

## LLM Config Structure:

llm_config = {
    # Required
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    
    # Optional API parameters
    "temperature": 0.7,
    "max_tokens": 150,
    
    # Optional validation
    "validation": [
        {"type": "response_not_empty"},
        {"type": "json_string"},
        {"type": "agent_task", "params": {...}}
    ],
    
    # Optional retry configuration
    "retry_config": {
        "max_attempts": 5,
        "backoff_factor": 2.0,
        "initial_delay": 1.0,
        "debug_mode": true
    },
    
    # Staged retry parameters
    "max_attempts_before_tool_use": 2,
    "max_attempts_before_human": 4,
    "debug_tool_name": "perplexity-ask",
    "debug_tool_mcp_config": {...},
    "original_user_prompt": "Original request for context"
}
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import litellm
from litellm import completion
from loguru import logger
from pydantic import BaseModel

from llm_call.core.utils.auth_diagnostics import diagnose_auth_error

from llm_call.core.base import ValidationResult, ValidationStrategy
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache


class HumanReviewNeededError(Exception):
    """Raised when human review is required after all retry attempts"""
    
    def __init__(self, message: str, context: Dict[str, Any], validation_errors: List[ValidationResult]):
        super().__init__(message)
        self.context = context
        self.validation_errors = validation_errors
        self.last_response = context.get("last_response")


@dataclass
class RetryConfig:
    """Configuration for retry behavior with enhanced features."""
    
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    debug_mode: bool = False
    enable_cache: bool = True
    # Enhanced features from POC 27
    use_jitter: bool = True
    jitter_range: float = 0.1  # ±10% jitter
    enable_circuit_breaker: bool = False
    circuit_breaker_config: Optional['CircuitBreakerConfig'] = None
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with optional jitter."""
        # Base exponential backoff
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        delay = min(delay, self.max_delay)
        
        # Add jitter if enabled (from POC 27)
        if self.use_jitter:
            jitter = delay * self.jitter_range
            delay = delay + random.uniform(-jitter, jitter)
            delay = max(0.1, delay)  # Ensure positive delay
        
        return delay


class CircuitState(Enum):
    """Circuit breaker states from POC 27"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Rejecting calls
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration from POC 27"""
    failure_threshold: int = 5
    window_size: int = 60  # seconds
    timeout: int = 30  # seconds before trying half-open
    success_threshold: int = 3  # successes needed to close from half-open
    excluded_exceptions: List[type] = field(default_factory=list)


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreaker:
    """Simple circuit breaker implementation based on POC 27"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_timestamps: List[datetime] = []
        self.consecutive_successes = 0
        self.state_changed_at = datetime.now()
    
    def can_execute(self) -> bool:
        """Check if request can proceed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if (datetime.now() - self.state_changed_at).total_seconds() > self.config.timeout:
                self._change_state(CircuitState.HALF_OPEN)
                return True
            return False
        
        # HALF_OPEN - allow limited testing
        return True
    
    def record_success(self) -> None:
        """Record successful execution"""
        self.consecutive_successes += 1
        
        if self.state == CircuitState.HALF_OPEN:
            if self.consecutive_successes >= self.config.success_threshold:
                self._change_state(CircuitState.CLOSED)
                logger.info(f"Circuit '{self.name}' recovered - closing")
    
    def record_failure(self, error: Exception) -> None:
        """Record failed execution"""
        if type(error) in self.config.excluded_exceptions:
            return
        
        self.consecutive_successes = 0
        self.failure_timestamps.append(datetime.now())
        self._clean_failure_window()
        
        if self.state == CircuitState.HALF_OPEN:
            self._change_state(CircuitState.OPEN)
            logger.warning(f"Circuit '{self.name}' test failed - reopening")
        
        elif self.state == CircuitState.CLOSED:
            if len(self.failure_timestamps) >= self.config.failure_threshold:
                self._change_state(CircuitState.OPEN)
                logger.error(f"Circuit '{self.name}' opened - threshold exceeded")
    
    def _clean_failure_window(self) -> None:
        """Remove old failures outside the window"""
        cutoff = datetime.now() - timedelta(seconds=self.config.window_size)
        self.failure_timestamps = [ts for ts in self.failure_timestamps if ts > cutoff]
    
    def _change_state(self, new_state: CircuitState) -> None:
        """Change circuit state"""
        if new_state != self.state:
            logger.debug(f"Circuit '{self.name}': {self.state.value} → {new_state.value}")
            self.state = new_state
            self.state_changed_at = datetime.now()
            if new_state == CircuitState.CLOSED:
                self.failure_timestamps = []


def extract_content_from_response(response: Any) -> str:
    """
    Extract the actual content string from various LLM response formats.
    
    This handles:
    - Dict responses (from Claude proxy): response["choices"][0]["message"]["content"]
    - ModelResponse objects (from LiteLLM): response.choices[0].message.content
    - Fallback to string representation for unknown formats
    
    Args:
        response: The LLM response in any supported format
        
    Returns:
        The extracted content string
    """
    try:
        # Handle dict responses (Claude proxy format)
        if isinstance(response, dict):
            choices = response.get("choices", [])
            if choices and isinstance(choices[0], dict):
                message = choices[0].get("message", {})
                if isinstance(message, dict):
                    return message.get("content", "")
        
        # Handle ModelResponse objects (LiteLLM format)
        elif hasattr(response, "choices") and response.choices:
            # Access the first choice's message content
            first_choice = response.choices[0]
            if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
                return first_choice.message.content or ""
        
        # Handle string responses directly
        elif isinstance(response, str):
            return response
            
    except Exception as e:
        logger.warning(f"Failed to extract content from response: {e}")
    
    # Fallback: convert entire response to string
    logger.debug(f"Using fallback string conversion for response type: {type(response)}")
    return str(response)


def build_retry_feedback_message(
    validation_errors: List[ValidationResult],
    attempt: int,
    max_attempts: int,
    original_prompt: Optional[str] = None,
    use_tool: Optional[str] = None,
    tool_instruction: Optional[str] = None
) -> str:
    """
    Build a clear, actionable feedback message for the LLM to correct its response.
    
    Args:
        validation_errors: List of validation results that failed
        attempt: Current attempt number (0-based)
        max_attempts: Maximum number of attempts allowed
        original_prompt: Optional original user prompt for context
        use_tool: Optional tool name to suggest for debugging
        tool_instruction: Optional custom instruction for tool usage
        
    Returns:
        A well-formatted feedback message
    """
    parts = [
        f"Your response did not pass validation (attempt {attempt + 1}/{max_attempts}).",
        "\nValidation errors found:"
    ]
    
    # Add each error with its suggestions
    for i, error in enumerate(validation_errors, 1):
        parts.append(f"\n{i}. {error.error}")
        
        # Add suggestions if available
        if error.suggestions:
            parts.append("   Suggestions to fix:")
            for suggestion in error.suggestions:
                parts.append(f"   - {suggestion}")
        
        # Add debug info if available (only in debug mode)
        if error.debug_info and logger.level <= 10:  # DEBUG level
            parts.append(f"   Debug info: {error.debug_info}")
    
    # Add tool usage suggestion if we've hit the threshold
    if use_tool:
        parts.append(f"\n IMPORTANT: You should use the '{use_tool}' tool to help debug and fix these issues.")
        if tool_instruction:
            parts.append(f"   {tool_instruction}")
        else:
            parts.append(f"   Use '{use_tool}' to research the error or find the correct solution.")
    
    # Add original context if available
    if original_prompt:
        parts.append(f"\nOriginal request: {original_prompt}")
    
    # Add clear instruction
    parts.append("\nPlease provide a corrected response that addresses these validation errors.")
    
    return "\n".join(parts)


async def retry_with_validation(
    llm_call: Callable,
    messages: List[Dict[str, str]],
    response_format: Optional[BaseModel],
    validation_strategies: List[ValidationStrategy],
    config: RetryConfig = None,
    original_llm_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Retry LLM calls with validation - async version with staged retry support.
    
    This function:
    1. Makes an LLM call
    2. Validates the response using provided strategies
    3. If validation fails, adds the response and error feedback to conversation
    4. After N attempts, suggests tool usage
    5. After M attempts, escalates to human review
    6. Continues until validation passes or max attempts reached
    
    Enhanced features:
    - Exponential backoff with jitter
    - Circuit breaker pattern for fault tolerance
    - Human escalation support
    
    Args:
        llm_call: The LLM completion function to call (async)
        messages: Initial conversation messages
        response_format: Optional Pydantic model for structured outputs
        validation_strategies: List of validation strategies to apply
        config: Retry configuration (uses defaults if None)
        original_llm_config: Original user config for context (includes staged retry params)
        **kwargs: Additional arguments passed to llm_call
    
    Returns:
        The validated LLM response
        
    Raises:
        CircuitOpenError: If circuit breaker is open
        HumanReviewNeededError: If human review threshold is reached
        Exception: If all retry attempts fail with details of last errors
    """
    if config is None:
        config = RetryConfig()
    
    if original_llm_config is None:
        original_llm_config = {}
    
    # Extract staged retry parameters
    max_attempts_before_tool_use = original_llm_config.get("max_attempts_before_tool_use")
    max_attempts_before_human = original_llm_config.get("max_attempts_before_human", config.max_attempts)
    debug_tool_name = original_llm_config.get("debug_tool_name")
    debug_tool_mcp_config = original_llm_config.get("debug_tool_mcp_config")
    original_user_prompt = original_llm_config.get("original_user_prompt")
    
    # Initialize circuit breaker if enabled
    circuit_breaker = None
    if config.enable_circuit_breaker:
        cb_config = config.circuit_breaker_config or CircuitBreakerConfig()
        circuit_breaker = CircuitBreaker(
            name=kwargs.get("model", "default"),
            config=cb_config
        )
    
    # Initialize caching if enabled
    if config.enable_cache:
        try:
            initialize_litellm_cache()
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
    
    # Enable JSON schema validation if response format is provided
    if response_format:
        litellm.enable_json_schema_validation = True
    
    # Keep track of the conversation for retry context
    conversation_messages = list(messages)  # Create a copy to avoid modifying original
    
    # Store original prompt for context if not provided
    if not original_user_prompt:
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            original_user_prompt = user_messages[-1].get("content", "")
    
    last_validation_errors = []
    last_response = None
    
    for attempt in range(config.max_attempts):
        try:
            # Check circuit breaker if enabled
            if circuit_breaker and not circuit_breaker.can_execute():
                raise CircuitOpenError(
                    f"Circuit breaker is open for model {kwargs.get('model', 'unknown')}. "
                    f"Too many failures in recent calls."
                )
            
            # Check if we should escalate to human review
            if max_attempts_before_human and attempt >= max_attempts_before_human:
                raise HumanReviewNeededError(
                    f"Human review required after {attempt} failed attempts",
                    context={
                        "original_llm_config": original_llm_config,
                        "last_response": last_response,
                        "attempt": attempt
                    },
                    validation_errors=last_validation_errors
                )
            
            # Prepare kwargs for this attempt
            attempt_kwargs = kwargs.copy()
            
            # Inject MCP config if we've hit the tool use threshold
            if (max_attempts_before_tool_use and 
                attempt >= max_attempts_before_tool_use and 
                debug_tool_mcp_config):
                
                if config.debug_mode:
                    logger.debug(f"Injecting MCP config for tool '{debug_tool_name}' at attempt {attempt + 1}")
                
                attempt_kwargs["mcp_config"] = debug_tool_mcp_config
            
            if config.debug_mode:
                logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}")
                logger.debug(f"Conversation length: {len(conversation_messages)} messages")
            
            # Make the LLM call
            if response_format:
                response = await llm_call(
                    messages=conversation_messages,
                    response_format=response_format,
                    **attempt_kwargs
                )
            else:
                response = await llm_call(
                    messages=conversation_messages,
                    **attempt_kwargs
                )
            
            last_response = response
            
            if config.debug_mode:
                logger.debug(f"Received response type: {type(response)}")
            
            # Apply validation strategies
            all_valid = True
            validation_errors = []
            validation_details = {}
            
            for strategy in validation_strategies:
                # Prepare context for validator - include full original config
                context = {
                    "attempt": attempt,
                    "messages": conversation_messages,
                    "config": config,
                    "original_prompt": original_user_prompt,
                    "original_llm_config": original_llm_config  # Full context for validators
                }
                
                # Validate the response
                result = await validate_response(strategy, response, context)
                
                if config.debug_mode:
                    logger.debug(f"Validation '{strategy.name}': valid={result.valid}, error={result.error}")
                
                validation_details[strategy.name] = result
                
                if not result.valid:
                    all_valid = False
                    validation_errors.append(result)
            
            # If all validations passed, return the response
            if all_valid:
                if config.debug_mode:
                    logger.success(f"All validations passed on attempt {attempt + 1}")
                # Record success in circuit breaker
                if circuit_breaker:
                    circuit_breaker.record_success()
                return response
            
            # Store last validation errors
            last_validation_errors = validation_errors
            
            # If validation failed and we have retries left, add feedback
            if attempt < config.max_attempts - 1:
                # Extract the actual content from the failed response
                response_content = extract_content_from_response(response)
                
                if config.debug_mode:
                    logger.debug(f"Extracted content length: {len(response_content)}")
                
                # Add the failed response to conversation
                conversation_messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Determine if we should suggest tool usage
                use_tool = None
                tool_instruction = None
                if (max_attempts_before_tool_use and 
                    attempt + 1 >= max_attempts_before_tool_use and 
                    debug_tool_name):
                    use_tool = debug_tool_name
                    tool_instruction = f"Use the '{debug_tool_name}' tool to help resolve the validation errors."
                
                # Build and add feedback message
                feedback_message = build_retry_feedback_message(
                    validation_errors,
                    attempt,
                    config.max_attempts,
                    original_user_prompt,
                    use_tool=use_tool,
                    tool_instruction=tool_instruction
                )
                
                conversation_messages.append({
                    "role": "user",
                    "content": feedback_message
                })
                
                if config.debug_mode:
                    logger.debug(f"Added feedback message ({len(feedback_message)} chars)")
                    if use_tool:
                        logger.debug(f"Suggested tool usage: {use_tool}")
                
                # Calculate and apply delay before retry
                delay = config.calculate_delay(attempt)
                if config.debug_mode:
                    logger.debug(f"Waiting {delay:.1f} seconds before retry...")
                await asyncio.sleep(delay)
            
        except HumanReviewNeededError:
            # Re-raise human review errors
            raise
        except CircuitOpenError:
            # Re-raise circuit breaker errors
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {type(e).__name__}: {e}")
            
            # Check if this is an authentication error
            error_str = str(e).lower()
            is_auth_error = any(auth_term in error_str for auth_term in ["jwt", "token", "auth", "credential", "forbidden", "unauthorized", "403", "401"])
            
            if is_auth_error:
                # Diagnose authentication error with detailed information
                model_name = kwargs.get("model", "unknown")
                diagnose_auth_error(e, model_name, context={"attempt": attempt + 1, "llm_config": original_llm_config})
                
                # Authentication errors should not be retried
                logger.error("Authentication errors cannot be resolved by retrying. Fix the issue and try again.")
                raise
            
            # Record failure in circuit breaker
            if circuit_breaker:
                circuit_breaker.record_failure(e)
            
            # Check if we should escalate to human review
            if max_attempts_before_human and attempt + 1 >= max_attempts_before_human:
                raise HumanReviewNeededError(
                    f"Human review required after error: {str(e)}",
                    context={
                        "original_llm_config": original_llm_config,
                        "last_response": last_response,
                        "error": str(e),
                        "attempt": attempt
                    },
                    validation_errors=last_validation_errors
                )
            
            # If this is the last attempt, re-raise the exception
            if attempt == config.max_attempts - 1:
                raise
            
            # Otherwise, wait and retry
            delay = config.calculate_delay(attempt)
            await asyncio.sleep(delay)
    
    # If we get here, all attempts failed validation
    error_summary = [f"{e.error}" for e in last_validation_errors]
    
    # Final check for human escalation
    if max_attempts_before_human and config.max_attempts >= max_attempts_before_human:
        raise HumanReviewNeededError(
            f"Human review required after {config.max_attempts} failed validation attempts",
            context={
                "original_llm_config": original_llm_config,
                "last_response": last_response,
                "attempt": config.max_attempts - 1
            },
            validation_errors=last_validation_errors
        )
    
    raise Exception(
        f"Failed validation after {config.max_attempts} attempts. "
        f"Last errors: {'; '.join(error_summary)}"
    )


def retry_with_validation_sync(
    llm_call: Callable,
    messages: List[Dict[str, str]],
    response_format: Optional[BaseModel],
    validation_strategies: List[ValidationStrategy],
    config: RetryConfig = None,
    original_llm_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    Synchronous version of retry_with_validation.
    
    See retry_with_validation for full documentation.
    """
    if config is None:
        config = RetryConfig()
    
    if original_llm_config is None:
        original_llm_config = {}
    
    # Extract staged retry parameters
    max_attempts_before_tool_use = original_llm_config.get("max_attempts_before_tool_use")
    max_attempts_before_human = original_llm_config.get("max_attempts_before_human", config.max_attempts)
    debug_tool_name = original_llm_config.get("debug_tool_name")
    debug_tool_mcp_config = original_llm_config.get("debug_tool_mcp_config")
    original_user_prompt = original_llm_config.get("original_user_prompt")
    
    # Initialize caching if enabled
    if config.enable_cache:
        try:
            initialize_litellm_cache()
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
    
    # Initialize circuit breaker if enabled
    circuit_breaker = None
    if config.enable_circuit_breaker:
        cb_config = config.circuit_breaker_config or CircuitBreakerConfig()
        circuit_breaker = CircuitBreaker(
            name=kwargs.get("model", "default"),
            config=cb_config
        )
    
    # Enable JSON schema validation if response format is provided
    if response_format:
        litellm.enable_json_schema_validation = True
    
    conversation_messages = list(messages)
    
    # Store original prompt for context if not provided
    if not original_user_prompt:
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            original_user_prompt = user_messages[-1].get("content", "")
    
    last_validation_errors = []
    last_response = None
    
    for attempt in range(config.max_attempts):
        try:
            # Check circuit breaker if enabled
            if circuit_breaker and not circuit_breaker.can_execute():
                raise CircuitOpenError(
                    f"Circuit breaker is open for model {kwargs.get('model', 'unknown')}. "
                    f"Too many failures in recent calls."
                )
            
            # Check if we should escalate to human review
            if max_attempts_before_human and attempt >= max_attempts_before_human:
                raise HumanReviewNeededError(
                    f"Human review required after {attempt} failed attempts",
                    context={
                        "original_llm_config": original_llm_config,
                        "last_response": last_response,
                        "attempt": attempt
                    },
                    validation_errors=last_validation_errors
                )
            
            # Prepare kwargs for this attempt
            attempt_kwargs = kwargs.copy()
            
            # Inject MCP config if we've hit the tool use threshold
            if (max_attempts_before_tool_use and 
                attempt >= max_attempts_before_tool_use and 
                debug_tool_mcp_config):
                
                if config.debug_mode:
                    logger.debug(f"Injecting MCP config for tool '{debug_tool_name}'")
                
                attempt_kwargs["mcp_config"] = debug_tool_mcp_config
            
            if config.debug_mode:
                logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}")
            
            # Make the LLM call
            if response_format:
                response = llm_call(
                    messages=conversation_messages,
                    response_format=response_format,
                    **attempt_kwargs
                )
            else:
                response = llm_call(
                    messages=conversation_messages,
                    **attempt_kwargs
                )
            
            last_response = response
            
            # Apply validation strategies
            all_valid = True
            validation_errors = []
            
            for strategy in validation_strategies:
                context = {
                    "attempt": attempt,
                    "messages": conversation_messages,
                    "config": config,
                    "original_prompt": original_user_prompt,
                    "original_llm_config": original_llm_config
                }
                
                # Synchronous validation
                result = strategy.validate(response, context)
                
                if config.debug_mode:
                    logger.debug(f"Validation '{strategy.name}': valid={result.valid}")
                
                if not result.valid:
                    all_valid = False
                    validation_errors.append(result)
            
            if all_valid:
                # Record success if circuit breaker is enabled
                if circuit_breaker:
                    circuit_breaker.record_success()
                return response
            
            last_validation_errors = validation_errors
            
            # Record validation failure if circuit breaker is enabled
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            # Add feedback for retry
            if attempt < config.max_attempts - 1:
                # Extract content from response
                response_content = extract_content_from_response(response)
                
                conversation_messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Determine if we should suggest tool usage
                use_tool = None
                tool_instruction = None
                if (max_attempts_before_tool_use and 
                    attempt + 1 >= max_attempts_before_tool_use and 
                    debug_tool_name):
                    use_tool = debug_tool_name
                    tool_instruction = f"Use the '{debug_tool_name}' tool to help resolve the validation errors."
                
                # Build feedback message
                feedback_message = build_retry_feedback_message(
                    validation_errors,
                    attempt,
                    config.max_attempts,
                    original_user_prompt,
                    use_tool=use_tool,
                    tool_instruction=tool_instruction
                )
                
                conversation_messages.append({
                    "role": "user",
                    "content": feedback_message
                })
                
                # Apply delay
                delay = config.calculate_delay(attempt)
                time.sleep(delay)
                
        except HumanReviewNeededError:
            raise
        except CircuitOpenError:
            # Re-raise circuit open errors without recording failure
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            
            # Record failure if circuit breaker is enabled
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            if max_attempts_before_human and attempt + 1 >= max_attempts_before_human:
                raise HumanReviewNeededError(
                    f"Human review required after error: {str(e)}",
                    context={
                        "original_llm_config": original_llm_config,
                        "last_response": last_response,
                        "error": str(e),
                        "attempt": attempt
                    },
                    validation_errors=last_validation_errors
                )
            
            if attempt == config.max_attempts - 1:
                raise
            
            delay = config.calculate_delay(attempt)
            time.sleep(delay)
    
    # All attempts failed
    error_summary = [f"{e.error}" for e in last_validation_errors]
    
    if max_attempts_before_human and config.max_attempts >= max_attempts_before_human:
        raise HumanReviewNeededError(
            f"Human review required after {config.max_attempts} failed validation attempts",
            context={
                "original_llm_config": original_llm_config,
                "last_response": last_response,
                "attempt": config.max_attempts - 1
            },
            validation_errors=last_validation_errors
        )
    
    raise Exception(
        f"Failed validation after {config.max_attempts} attempts. "
        f"Last errors: {'; '.join(error_summary)}"
    )


async def validate_response(
    strategy: ValidationStrategy,
    response: Any,
    context: Dict[str, Any]
) -> ValidationResult:
    """
    Validate a response using the given strategy.
    
    Handles both sync and async validation strategies transparently.
    
    Args:
        strategy: The validation strategy to use
        response: The response to validate
        context: Additional context for validation
        
    Returns:
        ValidationResult with validation outcome
    """
    try:
        # Check if strategy has async validate method
        if hasattr(strategy, '__avalidate__') or asyncio.iscoroutinefunction(strategy.validate):
            return await strategy.validate(response, context)
        else:
            # Run sync validation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, strategy.validate, response, context)
    except Exception as e:
        logger.error(f"Validation error in {strategy.name}: {e}")
        return ValidationResult(
            valid=False,
            error=f"Validation failed with error: {str(e)}",
            debug_info={"error_type": type(e).__name__}
        )


# Example usage and testing
if __name__ == "__main__":
    """
    Test the retry mechanism with various response formats and staged retry.
    """
    
    async def test_retry_logic():
        logger.info("Testing retry logic with various response formats...")
        
        # Test 1: Extract content from dict response
        dict_response = {
            "choices": [{
                "message": {
                    "content": "This is the actual content",
                    "role": "assistant"
                }
            }]
        }
        content = extract_content_from_response(dict_response)
        assert content == "This is the actual content", f"Expected content, got: {content}"
        logger.success(" Dict response extraction works")
        
        # Test 2: Extract content from object-like response
        class MockMessage:
            content = "Object-based content"
        
        class MockChoice:
            message = MockMessage()
        
        class MockResponse:
            choices = [MockChoice()]
        
        obj_response = MockResponse()
        content = extract_content_from_response(obj_response)
        assert content == "Object-based content", f"Expected content, got: {content}"
        logger.success(" Object response extraction works")
        
        # Test 3: Fallback for unknown format
        unknown_response = {"unknown": "format"}
        content = extract_content_from_response(unknown_response)
        assert "unknown" in content, f"Expected stringified response, got: {content}"
        logger.success(" Fallback extraction works")
        
        # Test 4: Build feedback message with tool suggestion
        from llm_call.core.base import ValidationResult
        
        errors = [
            ValidationResult(
                valid=False,
                error="Response is too short",
                suggestions=["Provide more detail", "Include examples"]
            ),
            ValidationResult(
                valid=False,
                error="Missing required JSON structure",
                suggestions=["Return valid JSON"]
            )
        ]
        
        feedback = build_retry_feedback_message(
            errors, 2, 5, "Original prompt", 
            use_tool="perplexity-ask",
            tool_instruction="Research the correct JSON format"
        )
        assert "attempt 3/5" in feedback
        assert "Response is too short" in feedback
        assert "Provide more detail" in feedback
        assert "Original prompt" in feedback
        assert "perplexity-ask" in feedback
        assert "Research the correct JSON format" in feedback
        logger.success(" Feedback message generation with tool suggestion works")
        
        # Test 5: HumanReviewNeededError structure
        try:
            raise HumanReviewNeededError(
                "Test error",
                context={"test": "context"},
                validation_errors=errors
            )
        except HumanReviewNeededError as e:
            assert e.context["test"] == "context"
            assert len(e.validation_errors) == 2
            logger.success(" HumanReviewNeededError works correctly")
        
        # Test 6: Exponential backoff with jitter
        config = RetryConfig(
            initial_delay=1.0,
            backoff_factor=2.0,
            max_delay=10.0,
            use_jitter=True,
            jitter_range=0.1
        )
        
        # Test delays are within expected ranges
        for attempt in range(5):
            delay = config.calculate_delay(attempt)
            expected_base = min(1.0 * (2.0 ** attempt), 10.0)
            expected_min = expected_base * 0.9  # -10% jitter
            expected_max = expected_base * 1.1  # +10% jitter
            
            assert expected_min <= delay <= expected_max, \
                f"Delay {delay} not in range [{expected_min}, {expected_max}] for attempt {attempt}"
        
        logger.success(" Exponential backoff with jitter works correctly")
        
        # Test 7: Circuit breaker
        cb_config = CircuitBreakerConfig(
            failure_threshold=3,
            window_size=60,
            timeout=5,
            success_threshold=2
        )
        circuit = CircuitBreaker("test", cb_config)
        
        # Initially closed
        assert circuit.can_execute() == True
        assert circuit.state == CircuitState.CLOSED
        
        # Record failures to open circuit
        for i in range(3):
            circuit.record_failure(Exception("Test failure"))
        
        assert circuit.state == CircuitState.OPEN
        assert circuit.can_execute() == False
        
        # Wait for timeout (simulate)
        circuit.state_changed_at = datetime.now() - timedelta(seconds=6)
        assert circuit.can_execute() == True  # Should transition to half-open
        assert circuit.state == CircuitState.HALF_OPEN
        
        # Record successes to close circuit
        circuit.record_success()
        circuit.record_success()
        assert circuit.state == CircuitState.CLOSED
        
        logger.success(" Circuit breaker works correctly")
        
        logger.info("\nAll tests passed! Enhanced retry logic is working correctly.")
    
    # Run tests
    import asyncio
    asyncio.run(test_retry_logic())
