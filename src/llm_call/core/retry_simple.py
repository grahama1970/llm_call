"""
Retry mechanism with validation for LLM calls.

This module provides a rock-solid retry logic that integrates with validation strategies.
The design prioritizes clarity, maintainability, and ease of use.

Key Features:
- Clear extraction of response content from various formats
- Proper error feedback to LLMs for self-correction
- Easy integration of custom validation strategies
- Comprehensive logging for debugging

Documentation:
- LiteLLM ModelResponse: https://docs.litellm.ai/docs/completion/response_object
- Retry patterns: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
"""

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
        {"type": "custom", "params": {...}}
    ],
    
    # Optional retry configuration
    "retry_config": {
        "max_attempts": 3,
        "backoff_factor": 2.0,
        "initial_delay": 1.0,
        "debug_mode": true
    }
}

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

import litellm
from litellm import completion
from loguru import logger
from pydantic import BaseModel

from llm_call.core.base import ValidationResult, ValidationStrategy
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    debug_mode: bool = False
    enable_cache: bool = True
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay for next retry attempt."""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


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
    original_prompt: Optional[str] = None
) -> str:
    """
    Build a clear, actionable feedback message for the LLM to correct its response.
    
    Args:
        validation_errors: List of validation results that failed
        attempt: Current attempt number (0-based)
        max_attempts: Maximum number of attempts allowed
        original_prompt: Optional original user prompt for context
        
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
    **kwargs
) -> Any:
    """
    Retry LLM calls with validation - async version.
    
    This function:
    1. Makes an LLM call
    2. Validates the response using provided strategies
    3. If validation fails, adds the response and error feedback to conversation
    4. Retries with the extended conversation history
    5. Continues until validation passes or max attempts reached
    
    Args:
        llm_call: The LLM completion function to call (async)
        messages: Initial conversation messages
        response_format: Optional Pydantic model for structured outputs
        validation_strategies: List of validation strategies to apply
        config: Retry configuration (uses defaults if None)
        **kwargs: Additional arguments passed to llm_call
    
    Returns:
        The validated LLM response
        
    Raises:
        Exception: If all retry attempts fail with details of last errors
    """
    if config is None:
        config = RetryConfig()
    
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
    
    # Store original prompt for context
    original_prompt = None
    user_messages = [m for m in messages if m.get("role") == "user"]
    if user_messages:
        original_prompt = user_messages[-1].get("content", "")
    
    last_validation_errors = []
    
    for attempt in range(config.max_attempts):
        try:
            if config.debug_mode:
                logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}")
                logger.debug(f"Conversation length: {len(conversation_messages)} messages")
            
            # Make the LLM call
            if response_format:
                response = await llm_call(
                    messages=conversation_messages,
                    response_format=response_format,
                    **kwargs
                )
            else:
                response = await llm_call(
                    messages=conversation_messages,
                    **kwargs
                )
            
            if config.debug_mode:
                logger.debug(f"Received response type: {type(response)}")
            
            # Apply validation strategies
            all_valid = True
            validation_errors = []
            validation_details = {}
            
            for strategy in validation_strategies:
                # Prepare context for validator
                context = {
                    "attempt": attempt,
                    "messages": conversation_messages,
                    "config": config,
                    "original_prompt": original_prompt,
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
                return response
            
            # Store last validation errors for final exception
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
                
                # Build and add feedback message
                feedback_message = build_retry_feedback_message(
                    validation_errors,
                    attempt,
                    config.max_attempts,
                    original_prompt
                )
                
                conversation_messages.append({
                    "role": "user",
                    "content": feedback_message
                })
                
                if config.debug_mode:
                    logger.debug(f"Added feedback message ({len(feedback_message)} chars)")
                
                # Calculate and apply delay before retry
                delay = config.calculate_delay(attempt)
                if config.debug_mode:
                    logger.debug(f"Waiting {delay:.1f} seconds before retry...")
                await asyncio.sleep(delay)
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {type(e).__name__}: {e}")
            
            # If this is the last attempt, re-raise the exception
            if attempt == config.max_attempts - 1:
                raise
            
            # Otherwise, wait and retry
            delay = config.calculate_delay(attempt)
            await asyncio.sleep(delay)
    
    # If we get here, all attempts failed validation
    error_summary = [f"{e.error}" for e in last_validation_errors]
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
    **kwargs
) -> Any:
    """
    Synchronous version of retry_with_validation.
    
    See retry_with_validation for full documentation.
    """
    if config is None:
        config = RetryConfig()
    
    # Initialize caching if enabled
    if config.enable_cache:
        try:
            initialize_litellm_cache()
        except Exception as e:
            logger.warning(f"Failed to initialize cache: {e}")
    
    # Enable JSON schema validation if response format is provided
    if response_format:
        litellm.enable_json_schema_validation = True
    
    conversation_messages = list(messages)
    
    # Store original prompt for context
    original_prompt = None
    user_messages = [m for m in messages if m.get("role") == "user"]
    if user_messages:
        original_prompt = user_messages[-1].get("content", "")
    
    last_validation_errors = []
    
    for attempt in range(config.max_attempts):
        try:
            if config.debug_mode:
                logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}")
            
            # Make the LLM call
            if response_format:
                response = llm_call(
                    messages=conversation_messages,
                    response_format=response_format,
                    **kwargs
                )
            else:
                response = llm_call(
                    messages=conversation_messages,
                    **kwargs
                )
            
            # Apply validation strategies
            all_valid = True
            validation_errors = []
            
            for strategy in validation_strategies:
                context = {
                    "attempt": attempt,
                    "messages": conversation_messages,
                    "config": config,
                    "original_prompt": original_prompt,
                }
                
                # Synchronous validation
                result = strategy.validate(response, context)
                
                if config.debug_mode:
                    logger.debug(f"Validation '{strategy.name}': valid={result.valid}")
                
                if not result.valid:
                    all_valid = False
                    validation_errors.append(result)
            
            if all_valid:
                return response
            
            last_validation_errors = validation_errors
            
            # Add feedback for retry
            if attempt < config.max_attempts - 1:
                # Extract content from response
                response_content = extract_content_from_response(response)
                
                conversation_messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Build feedback message
                feedback_message = build_retry_feedback_message(
                    validation_errors,
                    attempt,
                    config.max_attempts,
                    original_prompt
                )
                
                conversation_messages.append({
                    "role": "user",
                    "content": feedback_message
                })
                
                # Apply delay
                delay = config.calculate_delay(attempt)
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt == config.max_attempts - 1:
                raise
            
            delay = config.calculate_delay(attempt)
            time.sleep(delay)
    
    # All attempts failed
    error_summary = [f"{e.error}" for e in last_validation_errors]
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
    Test the retry mechanism with various response formats.
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
        logger.success("✓ Dict response extraction works")
        
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
        logger.success("✓ Object response extraction works")
        
        # Test 3: Fallback for unknown format
        unknown_response = {"unknown": "format"}
        content = extract_content_from_response(unknown_response)
        assert "unknown" in content, f"Expected stringified response, got: {content}"
        logger.success("✓ Fallback extraction works")
        
        # Test 4: Build feedback message
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
        
        feedback = build_retry_feedback_message(errors, 0, 3, "Original prompt")
        assert "attempt 1/3" in feedback
        assert "Response is too short" in feedback
        assert "Provide more detail" in feedback
        assert "Original prompt" in feedback
        logger.success("✓ Feedback message generation works")
        
        logger.info("\nAll tests passed! Retry logic is working correctly.")
    
    # Run tests
    import asyncio
    asyncio.run(test_retry_logic())
