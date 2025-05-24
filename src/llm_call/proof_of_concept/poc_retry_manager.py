"""
POC Retry Manager Implementation for LLM Calls.

This module provides a sophisticated retry mechanism that matches the complex
requirements described in the POC documentation, including:
- Staged retry with tool suggestion after N attempts
- Human escalation after M attempts  
- Dynamic MCP config injection for tools
- Complex validation context passing
- Agent-based validators that make recursive LLM calls

Documentation:
- Original POC design: See docs/memory_bank/guides/
- Retry patterns: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from loguru import logger
from pydantic import BaseModel

from llm_call.core.base import ValidationResult, AsyncValidationStrategy


class PoCHumanReviewNeededError(Exception):
    """Raised when human review is required after staged retry thresholds."""
    
    def __init__(self, message: str, context: Dict[str, Any], validation_errors: List[ValidationResult]):
        super().__init__(message)
        self.context = context
        self.validation_errors = validation_errors
        self.last_response = context.get("last_response")


@dataclass
class PoCRetryConfig:
    """Configuration for POC retry behavior with staged escalation."""
    
    max_attempts: int = 3
    backoff_factor: float = 2.0
    initial_delay: float = 1.0
    max_delay: float = 60.0
    debug_mode: bool = False    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay for retry attempt."""
        delay = self.initial_delay * (self.backoff_factor ** attempt)
        return min(delay, self.max_delay)


def extract_content_from_response(response: Any) -> str:
    """
    Extract content from various LLM response formats.
    
    Handles:
    - Dict responses (Claude proxy): response["choices"][0]["message"]["content"]
    - LiteLLM ModelResponse: response.choices[0].message.content
    - Raw strings
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
            first_choice = response.choices[0]
            if hasattr(first_choice, "message") and hasattr(first_choice.message, "content"):
                return first_choice.message.content or ""
        
        # Handle string responses
        elif isinstance(response, str):
            return response
            
    except Exception as e:
        logger.warning(f"Failed to extract content: {e}")
    
    # Fallback
    return str(response)

def build_retry_feedback_message(
    validation_errors: List[ValidationResult],
    attempt: int,
    max_attempts: int,
    original_prompt: Optional[str] = None,
    use_tool: Optional[str] = None,
    tool_instruction: Optional[str] = None
) -> str:
    """Build actionable feedback for the LLM including tool suggestions."""
    parts = [
        f"Your response did not pass validation (attempt {attempt + 1}/{max_attempts}).",
        "\nValidation errors found:"
    ]
    
    # Add validation errors
    for i, error in enumerate(validation_errors, 1):
        parts.append(f"\n{i}. {error.error}")
        
        if error.suggestions:
            parts.append("   Suggestions to fix:")
            for suggestion in error.suggestions:
                parts.append(f"   - {suggestion}")
    
    # Add tool usage suggestion if threshold reached
    if use_tool:
        parts.append(f"\n🔧 IMPORTANT: You should use the '{use_tool}' tool to help debug and fix these issues.")
        if tool_instruction:
            parts.append(f"   {tool_instruction}")
        else:
            parts.append(f"   Use '{use_tool}' to research the error or find the correct solution.")
    
    # Add original context
    if original_prompt:
        parts.append(f"\nOriginal request: {original_prompt}")
    
    parts.append("\nPlease provide a corrected response that addresses these validation errors.")
    
    return "\n".join(parts)

async def retry_with_validation_poc(
    llm_call_func: Callable,
    messages: List[Dict[str, str]],
    response_format: Optional[BaseModel],
    validation_strategies: List[AsyncValidationStrategy],
    config: PoCRetryConfig = None,
    original_llm_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Any:
    """
    POC retry mechanism with validation and staged escalation.
    
    This implements the sophisticated retry logic from the POC design:
    1. Makes LLM call
    2. Validates response using strategies (which may make recursive LLM calls)
    3. On failure, adds feedback to conversation
    4. After N attempts, suggests tool usage (with MCP config injection)
    5. After M attempts, escalates to human review
    6. Continues until validation passes or limits reached
    
    Args:
        llm_call_func: The async LLM function to call
        messages: Initial conversation messages
        response_format: Optional structured output format
        validation_strategies: List of validators to apply
        config: Retry configuration with thresholds
        original_llm_config: Full original config dict with staged retry params
        **kwargs: Additional args for llm_call_func (model, temp, etc.)
    
    Returns:
        The validated LLM response
        
    Raises:
        PoCHumanReviewNeededError: When human review threshold reached
        Exception: If all attempts fail with validation details
    """
    if config is None:
        config = PoCRetryConfig()
    
    if original_llm_config is None:
        original_llm_config = {}
    
    # Extract POC-specific staged retry parameters
    max_attempts_before_tool_use = original_llm_config.get("max_attempts_before_tool_use")
    max_attempts_before_human = original_llm_config.get("max_attempts_before_human", config.max_attempts)
    debug_tool_name = original_llm_config.get("debug_tool_name")
    debug_tool_mcp_config = original_llm_config.get("debug_tool_mcp_config")
    original_user_prompt = original_llm_config.get("original_user_prompt")    
    # Store original prompt if not provided
    if not original_user_prompt:
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            original_user_prompt = user_messages[-1].get("content", "")
    
    # Track conversation for retry context
    conversation_messages = list(messages)  # Copy to avoid modifying original
    
    last_validation_errors = []
    last_response = None
    
    for attempt in range(config.max_attempts):
        try:
            # Check human escalation threshold
            if max_attempts_before_human and attempt >= max_attempts_before_human:
                raise PoCHumanReviewNeededError(
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
            
            # Inject MCP config if tool use threshold reached
            if (max_attempts_before_tool_use and 
                attempt >= max_attempts_before_tool_use and 
                debug_tool_mcp_config):
                
                if config.debug_mode:
                    logger.debug(f"Injecting MCP config for tool '{debug_tool_name}' at attempt {attempt + 1}")
                
                attempt_kwargs["mcp_config"] = debug_tool_mcp_config
            
            if config.debug_mode:
                logger.debug(f"Attempt {attempt + 1}/{config.max_attempts}")
                logger.debug(f"Conversation has {len(conversation_messages)} messages")            
            # Make the LLM call
            if response_format:
                response = await llm_call_func(
                    messages=conversation_messages,
                    response_format=response_format,
                    **attempt_kwargs
                )
            else:
                response = await llm_call_func(
                    messages=conversation_messages,
                    **attempt_kwargs
                )
            
            last_response = response
            
            if config.debug_mode:
                logger.debug(f"Got response type: {type(response)}")
            
            # Apply validation strategies
            all_valid = True
            validation_errors = []
            validation_details = {}
            
            for strategy in validation_strategies:
                # Build context for validators - includes full original config
                context = {
                    "attempt": attempt,
                    "messages": conversation_messages,
                    "config": config,
                    "original_prompt": original_user_prompt,
                    "original_llm_config": original_llm_config  # Full context
                }
                
                # Validate (handles both sync/async strategies)
                result = await validate_response(strategy, response, context)
                
                if config.debug_mode:
                    logger.debug(f"Validation '{strategy.name}': valid={result.valid}, error={result.error}")
                
                validation_details[strategy.name] = result
                
                if not result.valid:
                    all_valid = False
                    validation_errors.append(result)            
            # Success - all validations passed
            if all_valid:
                if config.debug_mode:
                    logger.success(f"All validations passed on attempt {attempt + 1}")
                return response
            
            # Store errors for potential escalation
            last_validation_errors = validation_errors
            
            # Prepare retry if attempts remain
            if attempt < config.max_attempts - 1:
                # Extract content from failed response
                response_content = extract_content_from_response(response)
                
                if config.debug_mode:
                    logger.debug(f"Extracted {len(response_content)} chars from response")
                
                # Add failed response to conversation
                conversation_messages.append({
                    "role": "assistant",
                    "content": response_content
                })
                
                # Check if we should suggest tool usage
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
                
                if config.debug_mode:
                    logger.debug(f"Added feedback ({len(feedback_message)} chars)")
                    if use_tool:
                        logger.debug(f"Suggested tool: {use_tool}")
                
                # Apply backoff delay
                delay = config.calculate_delay(attempt)
                if config.debug_mode:
                    logger.debug(f"Waiting {delay:.1f}s before retry...")
                await asyncio.sleep(delay)
            
        except PoCHumanReviewNeededError:
            # Re-raise human review errors
            raise
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            
            # Check human escalation on error
            if max_attempts_before_human and attempt + 1 >= max_attempts_before_human:
                raise PoCHumanReviewNeededError(
                    f"Human review required after error: {str(e)}",
                    context={
                        "original_llm_config": original_llm_config,
                        "last_response": last_response,
                        "error": str(e),
                        "attempt": attempt
                    },
                    validation_errors=last_validation_errors
                )
            
            # Re-raise on last attempt
            if attempt == config.max_attempts - 1:
                raise
            
            # Wait before retry
            delay = config.calculate_delay(attempt)
            await asyncio.sleep(delay)    
    # All attempts exhausted
    error_summary = [f"{e.error}" for e in last_validation_errors]
    
    # Final human escalation check
    if max_attempts_before_human and config.max_attempts >= max_attempts_before_human:
        raise PoCHumanReviewNeededError(
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
    strategy: AsyncValidationStrategy,
    response: Any,
    context: Dict[str, Any]
) -> ValidationResult:
    """
    Validate response using the given strategy.
    
    Handles both sync and async validation strategies transparently.
    """
    try:
        # Check if strategy has async validate
        if hasattr(strategy, '__avalidate__') or asyncio.iscoroutinefunction(strategy.validate):
            return await strategy.validate(response, context)
        else:
            # Run sync validation in executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, strategy.validate, response, context)
    except Exception as e:
        logger.error(f"Validation error in {strategy.name}: {e}")
        return ValidationResult(
            valid=False,
            error=f"Validation failed with error: {str(e)}",
            debug_info={"error_type": type(e).__name__}
        )

# Validation block for testing
if __name__ == "__main__":
    """Test the POC retry manager implementation."""
    
    async def test_poc_retry():
        logger.info("Testing POC retry manager...")
        
        # Test 1: Content extraction
        test_responses = [
            # Claude proxy format
            {"choices": [{"message": {"content": "Test content 1"}}]},
            # LiteLLM format (mock)
            type('MockResponse', (), {
                'choices': [type('Choice', (), {
                    'message': type('Message', (), {'content': "Test content 2"})()
                })()]
            })(),
            # String
            "Test content 3"
        ]
        
        for i, resp in enumerate(test_responses, 1):
            content = extract_content_from_response(resp)
            assert f"Test content {i}" in content, f"Failed to extract from format {i}"
        
        logger.success("✓ Content extraction works for all formats")
        
        # Test 2: Feedback message with tool suggestion
        errors = [
            ValidationResult(
                valid=False,
                error="Missing required field 'name'",
                suggestions=["Add a 'name' field to the JSON"]
            )
        ]
        
        feedback = build_retry_feedback_message(
            errors, 2, 5, "Create a user object",
            use_tool="perplexity-ask",
            tool_instruction="Search for JSON schema examples"
        )
        
        assert "attempt 3/5" in feedback
        assert "Missing required field" in feedback
        assert "perplexity-ask" in feedback
        assert "Create a user object" in feedback
        
        logger.success("✓ Feedback message generation works")        
        # Test 3: Config delay calculation
        config = PoCRetryConfig(initial_delay=1.0, backoff_factor=2.0, max_delay=10.0)
        assert config.calculate_delay(0) == 1.0
        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(2) == 4.0
        assert config.calculate_delay(10) == 10.0  # Max delay cap
        
        logger.success("✓ Retry delay calculation works")
        
        # Test 4: Human review error
        try:
            raise PoCHumanReviewNeededError(
                "Test escalation",
                context={"test": True},
                validation_errors=errors
            )
        except PoCHumanReviewNeededError as e:
            assert e.context["test"] == True
            assert len(e.validation_errors) == 1
            logger.success("✓ Human review error works")
        
        logger.info("\nAll POC retry manager tests passed!")
    
    # Run tests
    import asyncio
    asyncio.run(test_poc_retry())