"""
Real-world test for POC retry manager - uses actual LLM calls.

Documentation:
- POC Retry Manager: src/llm_call/proof_of_concept/poc_retry_manager.py
- LiteLLM: https://docs.litellm.ai/

Sample input: LLM configuration with validation
Expected output: Validated LLM response after retries
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from loguru import logger

from llm_call.proof_of_concept.litellm_client_poc import llm_call
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, 
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
           level="INFO")


async def test_basic_retry_with_real_llm():
    """Test 1: Basic retry with validation feedback using real LLM."""
    logger.info("\n=== Test 1: Basic Retry with Real LLM ===")
    
    config = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Always respond with valid, non-empty text."},
            {"role": "user", "content": "Say 'Hello World' exactly"}
        ],
        "temperature": 0.1,
        "max_tokens": 50,
        "validation": [
            {"type": "response_not_empty"}
        ],
        "retry_config": {
            "max_attempts": 2,
            "debug_mode": True
        }
    }    
    try:
        result = await llm_call(config)
        if result:
            # Extract content based on response type
            if isinstance(result, dict) and result.get("choices"):
                content = result["choices"][0].get("message", {}).get("content", "")
            elif hasattr(result, "choices") and result.choices:
                content = result.choices[0].message.content
            else:
                content = str(result)
            
            logger.success(f"✓ Basic retry test passed! Response: {content}")
            return True
        else:
            logger.error("✗ Basic retry test failed - no response")
            return False
    except Exception as e:
        logger.error(f"✗ Basic retry test failed with error: {e}")
        return False


async def test_json_validation_with_retry():
    """Test 2: JSON validation with retry using real LLM."""
    logger.info("\n=== Test 2: JSON Validation with Retry ===")
    
    config = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Return a JSON object with fields: name (string) and age (number). Example: {\"name\": \"John\", \"age\": 30}"}
        ],
        "temperature": 0.1,
        "max_tokens": 100,
        "response_format": {"type": "json_object"},
        "validation": [
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "name"}},
            {"type": "field_present", "params": {"field_name": "age"}}
        ],
        "retry_config": {
            "max_attempts": 3,
            "debug_mode": True,
            "initial_delay": 0.5
        }
    }    
    try:
        result = await llm_call(config)
        if result:
            if isinstance(result, dict) and result.get("choices"):
                content = result["choices"][0].get("message", {}).get("content", "")
            elif hasattr(result, "choices") and result.choices:
                content = result.choices[0].message.content
            else:
                content = str(result)
            
            logger.success(f"✓ JSON validation test passed! Response: {content}")
            return True
        else:
            logger.error("✗ JSON validation test failed - no response")
            return False
    except Exception as e:
        logger.error(f"✗ JSON validation test failed with error: {e}")
        return False


async def test_human_escalation():
    """Test 3: Human escalation after configured attempts."""
    logger.info("\n=== Test 3: Human Escalation Test ===")
    
    # This config will always fail validation to trigger human escalation
    config = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You must always respond with plain text, never JSON."},
            {"role": "user", "content": "What is 2+2?"}
        ],
        "temperature": 0.0,
        "max_tokens": 50,
        "validation": [
            {"type": "json_string"}  # This will always fail on plain text
        ],
        "retry_config": {
            "max_attempts": 4,
            "debug_mode": True,
            "initial_delay": 0.3
        },
        "max_attempts_before_human": 2,  # Escalate after 2 attempts
        "original_user_prompt": "Testing human escalation"
    }    
    result = await llm_call(config)
    
    # Check if we got the expected human review error response
    if result and isinstance(result, dict) and result.get("error") == "Human review needed":
        logger.success(f"✓ Human escalation test passed! Got human review response: {result.get('details')}")
        return True
    else:
        logger.error(f"✗ Human escalation test failed - expected human review response, got: {result}")
        return False


async def main():
    """Run all real-world POC retry tests."""
    logger.info("Starting Real-World POC Retry Manager Tests")
    logger.info("=" * 60)
    
    # Initialize LiteLLM cache - REQUIRED per CLAUDE.md
    try:
        initialize_litellm_cache()
        logger.info("✓ LiteLLM cache initialized")
    except Exception as e:
        logger.warning(f"LiteLLM cache initialization warning: {e}")
    
    # Track all validation failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic retry
    total_tests += 1
    if not await test_basic_retry_with_real_llm():
        all_validation_failures.append("Basic retry test failed")
    await asyncio.sleep(1)  # Small delay between tests
    
    # Test 2: JSON validation
    total_tests += 1
    if not await test_json_validation_with_retry():
        all_validation_failures.append("JSON validation test failed")
    await asyncio.sleep(1)    
    # Test 3: Human escalation
    total_tests += 1
    if not await test_human_escalation():
        all_validation_failures.append("Human escalation test failed")
    
    # Final validation result - per CLAUDE.md requirements
    logger.info("\n" + "=" * 60)
    if all_validation_failures:
        logger.error(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)  # Exit with error code
    else:
        logger.success(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC retry manager is validated with real LLM calls")
        sys.exit(0)  # Exit with success code


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check for required API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("❌ OPENAI_API_KEY not found in environment")
        logger.info("Please set OPENAI_API_KEY to run real LLM tests")
        sys.exit(1)
    
    # Run tests
    asyncio.run(main())