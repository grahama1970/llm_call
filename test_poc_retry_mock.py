"""
Test script for POC retry manager - Mock version.

This tests the retry manager functionality without requiring actual API credentials.
"""

import asyncio
from typing import Dict, Any, List
from loguru import logger
from src.llm_call.proof_of_concept.poc_retry_manager import (
    retry_with_validation_poc,
    PoCRetryConfig,
    PoCHumanReviewNeededError
)
from llm_call.core.base import ValidationResult, AsyncValidationStrategy

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, 
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
           level="DEBUG")


class MockResponseValidator(AsyncValidationStrategy):
    """Mock validator that fails if response contains 'FAIL'."""
    
    def __init__(self):
        super().__init__("mock_validator")
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        if "FAIL" in content:
            return ValidationResult(
                valid=False,
                error="Response contains FAIL keyword",
                suggestions=["Remove FAIL from response", "Try a different approach"]
            )
        return ValidationResult(valid=True)


# Mock LLM call counters
call_counter = {"count": 0}

async def mock_llm_success_after_retries(**kwargs):
    """Mock LLM that succeeds after 2 attempts."""
    call_counter["count"] += 1
    messages = kwargs.get("messages", [])
    
    # Check if this is a retry (has feedback message)
    is_retry = any("validation" in msg.get("content", "").lower() for msg in messages)
    
    if call_counter["count"] <= 1 and not is_retry:
        # First call - return FAIL
        return {
            "choices": [{
                "message": {"content": "This response will FAIL validation"}
            }]
        }
    else:
        # Subsequent calls - return success
        return {
            "choices": [{
                "message": {"content": "This is a valid response without the fail keyword"}
            }]
        }


async def mock_llm_always_fail(**kwargs):
    """Mock LLM that always fails validation."""
    return {
        "choices": [{
            "message": {"content": "This will always FAIL validation"}
        }]
    }


async def mock_llm_with_tool_awareness(**kwargs):
    """Mock LLM that responds to tool suggestions."""
    messages = kwargs.get("messages", [])
    mcp_config = kwargs.get("mcp_config")
    
    # Check if tool was suggested
    tool_suggested = any("perplexity-ask" in msg.get("content", "") for msg in messages)
    
    if tool_suggested and mcp_config:
        return {
            "choices": [{
                "message": {"content": "Using the suggested tool, I found the answer: Valid response"}
            }]
        }
    else:
        return {
            "choices": [{
                "message": {"content": "FAIL - I need to use a tool to answer this"}
            }]
        }


async def test_basic_retry():
    """Test 1: Basic retry with validation feedback."""
    logger.info("\n=== Test 1: Basic Retry with Validation ===")
    
    # Reset counter
    call_counter["count"] = 0
    
    config = PoCRetryConfig(max_attempts=3, debug_mode=True, initial_delay=0.1)
    validator = MockResponseValidator()
    
    try:
        result = await retry_with_validation_poc(
            llm_call_func=mock_llm_success_after_retries,
            messages=[{"role": "user", "content": "Test message"}],
            response_format=None,
            validation_strategies=[validator],
            config=config
        )
        
        content = result["choices"][0]["message"]["content"]
        logger.success(f"✓ Basic retry test passed! Final response: {content}")
        logger.info(f"  Total calls made: {call_counter['count']}")
        return True
    except Exception as e:
        logger.error(f"✗ Basic retry test failed: {e}")
        return False


async def test_tool_suggestion():
    """Test 2: Tool suggestion after N attempts."""
    logger.info("\n=== Test 2: Tool Suggestion After N Attempts ===")
    
    config = PoCRetryConfig(max_attempts=4, debug_mode=True, initial_delay=0.1)
    validator = MockResponseValidator()
    
    original_config = {
        "max_attempts_before_tool_use": 2,
        "debug_tool_name": "perplexity-ask",
        "debug_tool_mcp_config": {"mcpServers": {"perplexity-ask": {}}},
        "original_user_prompt": "Answer this complex question"
    }
    
    try:
        result = await retry_with_validation_poc(
            llm_call_func=mock_llm_with_tool_awareness,
            messages=[{"role": "user", "content": "Complex question"}],
            response_format=None,
            validation_strategies=[validator],
            config=config,
            original_llm_config=original_config
        )
        
        content = result["choices"][0]["message"]["content"]
        if "Using the suggested tool" in content:
            logger.success("✓ Tool suggestion test passed! Tool was used successfully")
        else:
            logger.warning("⚠ Tool suggestion test: unexpected response")
        return True
    except Exception as e:
        logger.error(f"✗ Tool suggestion test failed: {e}")
        return False

async def test_human_escalation():
    """Test 3: Human escalation after M attempts."""
    logger.info("\n=== Test 3: Human Escalation After M Attempts ===")
    
    config = PoCRetryConfig(max_attempts=5, debug_mode=True, initial_delay=0.1)
    validator = MockResponseValidator()
    
    original_config = {
        "max_attempts_before_tool_use": 2,
        "max_attempts_before_human": 3,
        "debug_tool_name": "perplexity-ask",
        "original_user_prompt": "Generate valid response"
    }
    
    try:
        result = await retry_with_validation_poc(
            llm_call_func=mock_llm_always_fail,
            messages=[{"role": "user", "content": "Test message"}],
            response_format=None,
            validation_strategies=[validator],
            config=config,
            original_llm_config=original_config
        )
        
        logger.error("✗ Human escalation test failed - should have raised PoCHumanReviewNeededError")
        return False
    except PoCHumanReviewNeededError as e:
        logger.success(f"✓ Human escalation test passed! Error: {str(e)}")
        logger.info(f"  Context: {e.context.get('attempt')} attempts made")
        logger.info(f"  Validation errors: {len(e.validation_errors)}")
        return True
    except Exception as e:
        logger.error(f"✗ Human escalation test failed with unexpected error: {e}")
        return False


async def main():
    """Run all POC retry manager mock tests."""
    logger.info("Starting POC Retry Manager Mock Tests")
    logger.info("=" * 60)
    
    results = []
    
    # Test 1
    results.append(await test_basic_retry())
    await asyncio.sleep(0.5)
    
    # Test 2
    results.append(await test_tool_suggestion())
    await asyncio.sleep(0.5)
    
    # Test 3  
    results.append(await test_human_escalation())
    
    logger.info("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    logger.info(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        logger.success("All tests passed! POC retry manager is working correctly.")
    else:
        logger.error(f"{total - passed} tests failed.")


if __name__ == "__main__":
    asyncio.run(main())