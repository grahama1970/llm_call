"""
Real test script for POC retry manager - No mocks, actual LLM calls.

This script tests the retry mechanism with real LLM calls, following CLAUDE.md standards:
- Real data only, no mocks
- Actual expected results verification
- Proper error tracking and reporting
- initialize_litellm_cache() usage
"""

import asyncio
import os
import sys
from typing import Dict, Any, List
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Import required modules
from src.llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from dotenv import load_dotenv

# Configure logger
logger.remove()
logger.add(
    lambda msg: print(msg, end=""), 
    colorize=True, 
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
    level="INFO"
)

# Track validation failures
all_validation_failures = []
total_tests = 0

async def test_retry_with_validation_feedback():
    """Test 1: Real retry with validation feedback using actual LLM."""
    global total_tests, all_validation_failures
    total_tests += 1
    
    logger.info("\n=== Test 1: Real Retry with Validation Feedback ===")
    
    try:
        # Configure to use a cheaper model for testing
        config = {
            "model": "openai/gpt-3.5-turbo",  # Use a cheap, fast model
            "messages": [
                {"role": "system", "content": "You are a helpful assistant. Be very brief."},
                {"role": "user", "content": "Reply with exactly: EMPTY"}
            ],
            "temperature": 0.0,  # Deterministic
            "max_tokens": 10,
            "validation": [
                {"type": "response_not_empty"},
                {
                    "type": "field_present",  # This should fail on plain text
                    "params": {"field_name": "data"}
                }
            ],
            "retry_config": {
                "max_attempts": 2,
                "debug_mode": True,
                "initial_delay": 0.5
            }
        }
        
        result = await llm_call(config)
        
        # Check if result exists
        if result:
            if isinstance(result, dict) and "error" in result:
                logger.info(f"Expected validation failure occurred: {result['error']}")
                # This is expected behavior - validation should fail
                return True
            else:
                # Extract content to verify
                try:
                    if hasattr(result, 'choices'):
                        content = result.choices[0].message.content
                    else:
                        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    logger.warning(f"Unexpected success with content: {content}")
                except:
                    logger.warning(f"Unexpected response format: {result}")
                
                all_validation_failures.append(
                    "Test 1: Expected validation to fail but got success response"
                )
                return False
        else:
            logger.info("No response received (expected behavior for failed validation)")
            return True
            
    except Exception as e:
        logger.error(f"Test 1 error: {type(e).__name__}: {e}")
        all_validation_failures.append(f"Test 1: Unexpected error - {e}")
        return False

async def test_successful_retry_after_feedback():
    """Test 2: Verify retry succeeds when validation passes after feedback."""
    global total_tests, all_validation_failures
    total_tests += 1
    
    logger.info("\n=== Test 2: Successful Retry After Feedback ===")
    
    try:
        config = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a JSON generator. Always respond with valid JSON."},
                {"role": "user", "content": "Generate a JSON object with a 'name' field containing 'test'."}
            ],
            "temperature": 0.0,
            "max_tokens": 50,
            "response_format": {"type": "json_object"},
            "validation": [
                {"type": "json_string"},
                {"type": "field_present", "params": {"field_name": "name"}}
            ],
            "retry_config": {
                "max_attempts": 3,
                "debug_mode": True,
                "initial_delay": 0.5
            }
        }
        
        result = await llm_call(config)
        
        if result:
            try:
                # Extract and verify content
                if hasattr(result, 'choices'):
                    content = result.choices[0].message.content
                else:
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Parse JSON to verify it's valid and has 'name' field
                import json
                parsed = json.loads(content)
                if "name" in parsed:
                    logger.success(f"✓ Successfully generated JSON with name field: {parsed}")
                    return True
                else:
                    all_validation_failures.append(
                        f"Test 2: JSON missing 'name' field: {parsed}"
                    )
                    return False
                    
            except json.JSONDecodeError as e:
                all_validation_failures.append(
                    f"Test 2: Invalid JSON in response: {content}"
                )
                return False
            except Exception as e:
                all_validation_failures.append(
                    f"Test 2: Error processing response: {e}"
                )
                return False
        else:
            all_validation_failures.append("Test 2: No response received")
            return False
            
    except Exception as e:
        logger.error(f"Test 2 error: {type(e).__name__}: {e}")
        all_validation_failures.append(f"Test 2: Unexpected error - {e}")
        return False

async def test_human_escalation():
    """Test 3: Verify human escalation triggers after configured attempts."""
    global total_tests, all_validation_failures
    total_tests += 1
    
    logger.info("\n=== Test 3: Human Escalation ===")
    
    try:
        config = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Always respond with plain text, never JSON."},
                {"role": "user", "content": "Say hello"}
            ],
            "temperature": 0.0,
            "max_tokens": 20,
            "validation": [
                {"type": "json_string"}  # This will always fail for plain text
            ],
            "retry_config": {
                "max_attempts": 4,
                "debug_mode": True,
                "initial_delay": 0.2
            },
            "max_attempts_before_tool_use": 2,
            "max_attempts_before_human": 3,  # Should escalate on 3rd attempt
            "debug_tool_name": "perplexity-ask",
            "original_user_prompt": "Generate valid JSON response"
        }
        
        result = await llm_call(config)
        
        if result and isinstance(result, dict) and result.get("error") == "Human review needed":
            logger.success("✓ Human escalation triggered correctly")
            logger.info(f"  Details: {result.get('details', 'N/A')}")
            logger.info(f"  Last response: {result.get('last_response', 'N/A')}")
            return True
        else:
            all_validation_failures.append(
                f"Test 3: Expected human escalation but got: {result}"
            )
            return False
            
    except Exception as e:
        logger.error(f"Test 3 error: {type(e).__name__}: {e}")
        all_validation_failures.append(f"Test 3: Unexpected error - {e}")
        return False

async def main():
    """Run all POC retry tests with real LLM calls."""
    global all_validation_failures, total_tests
    
    # Load environment variables
    load_dotenv()
    
    # Initialize LiteLLM cache - REQUIRED per CLAUDE.md
    logger.info("Initializing LiteLLM cache...")
    try:
        initialize_litellm_cache()
    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        return
    
    logger.info("\nStarting POC Retry Manager Real Tests")
    logger.info("=" * 60)
    
    # Check if we have necessary API keys
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment. Cannot run tests.")
        return
    
    # Run tests
    test_results = []
    
    # Test 1: Retry with validation feedback
    try:
        result = await test_retry_with_validation_feedback()
        test_results.append(result)
    except Exception as e:
        logger.error(f"Test 1 failed with exception: {e}")
        test_results.append(False)
        all_validation_failures.append(f"Test 1: Exception - {e}")
    
    await asyncio.sleep(1)  # Brief pause between tests
    
    # Test 2: Successful retry after feedback
    try:
        result = await test_successful_retry_after_feedback()
        test_results.append(result)
    except Exception as e:
        logger.error(f"Test 2 failed with exception: {e}")
        test_results.append(False)
        all_validation_failures.append(f"Test 2: Exception - {e}")
    
    await asyncio.sleep(1)
    
    # Test 3: Human escalation
    try:
        result = await test_human_escalation()
        test_results.append(result)
    except Exception as e:
        logger.error(f"Test 3 failed with exception: {e}")
        test_results.append(False)
        all_validation_failures.append(f"Test 3: Exception - {e}")
    
    # Report results
    logger.info("\n" + "=" * 60)
    passed = sum(test_results)
    
    if all_validation_failures:
        logger.error(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC retry manager is working correctly with real LLM calls")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())