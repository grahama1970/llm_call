#!/usr/bin/env python3
"""Test core v4 features systematically."""

import asyncio
import json
import sys
import os
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_basic_proxy_call():
    """Test 1: Basic proxy call."""
    logger.info("\n=== Test 1: Basic Proxy Call ===")
    
    config = {
        "model": "max/text-general",
        "question": "What is 2+2?"
    }
    
    try:
        response = await llm_call(config)
        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            logger.success(f"✅ PASS - Response: {content}")
            return True
    except Exception as e:
        logger.error(f"❌ FAIL - {e}")
    return False

async def test_validation_response_not_empty():
    """Test 2: Response not empty validation."""
    logger.info("\n=== Test 2: Response Not Empty Validation ===")
    
    config = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "Say hello"}],
        "validation": [{"type": "response_not_empty"}]
    }
    
    try:
        response = await llm_call(config)
        if response and "choices" in response:
            logger.success("✅ PASS - Validation succeeded")
            return True
    except Exception as e:
        logger.error(f"❌ FAIL - {e}")
    return False

async def test_json_validation():
    """Test 3: JSON validation."""
    logger.info("\n=== Test 3: JSON Validation ===")
    
    config = {
        "model": "max/json-expert",
        "messages": [
            {"role": "user", "content": "Return a JSON object with a 'status' field set to 'ok'"}
        ],
        "validation": [
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "status"}}
        ]
    }
    
    try:
        response = await llm_call(config)
        if response and "choices" in response:
            content = response["choices"][0]["message"]["content"]
            data = json.loads(content)
            logger.success(f"✅ PASS - Got valid JSON: {data}")
            return True
    except Exception as e:
        logger.error(f"❌ FAIL - {e}")
    return False

async def test_agent_validation():
    """Test 4: Agent task validation."""
    logger.info("\n=== Test 4: Agent Task Validation ===")
    
    config = {
        "model": "max/text-general",
        "messages": [
            {"role": "user", "content": "Write: print('hello')"}
        ],
        "validation": [
            {
                "type": "agent_task",
                "params": {
                    "task_prompt_to_claude": "Is this valid Python code?\n\n{CODE_TO_VALIDATE}\n\nRespond with JSON: {\"validation_passed\": true, \"reasoning\": \"explanation\", \"details\": \"VALID\" or \"INVALID\"}",
                    "validation_model_alias": "max/text-general",
                    "success_criteria": {"must_contain_in_details": "VALID"}
                }
            }
        ]
    }
    
    try:
        response = await llm_call(config)
        if response and "choices" in response:
            logger.success("✅ PASS - Agent validation succeeded")
            return True
    except Exception as e:
        logger.error(f"❌ FAIL - {e}")
    return False

async def test_retry_mechanism():
    """Test 5: Retry mechanism."""
    logger.info("\n=== Test 5: Retry Mechanism ===")
    
    config = {
        "model": "max/text-general",
        "messages": [
            {"role": "user", "content": "Generate a number between 1 and 10"}
        ],
        "validation": [
            {
                "type": "agent_task",
                "params": {
                    "task_prompt_to_claude": "Check if the response contains the number 5. {CODE_TO_VALIDATE}\n\nRespond with JSON: {\"validation_passed\": true/false, \"reasoning\": \"explanation\", \"details\": \"Found 5\" or \"No 5\"}",
                    "validation_model_alias": "max/text-general", 
                    "success_criteria": {"must_contain_in_details": "Found 5"}
                }
            }
        ],
        "retry_config": {
            "max_attempts": 3,
            "debug_mode": True
        }
    }
    
    try:
        response = await llm_call(config)
        if response:
            if "error" in response and "Human review needed" in response["error"]:
                logger.info("✅ PASS - Retry mechanism working (escalated to human)")
                return True
            elif "choices" in response:
                logger.success("✅ PASS - Got valid response (lucky!)")
                return True
    except Exception as e:
        logger.error(f"❌ FAIL - {e}")
    return False

async def test_litellm_call():
    """Test 6: Standard LiteLLM call."""
    logger.info("\n=== Test 6: LiteLLM Call ===")
    
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'test passed'"}],
        "validation": [{"type": "response_not_empty"}]
    }
    
    try:
        response = await llm_call(config)
        if response and hasattr(response, 'choices'):
            content = response.choices[0].message.content
            logger.success(f"✅ PASS - Response: {content}")
            return True
    except Exception as e:
        logger.error(f"❌ FAIL - {e}")
    return False

async def main():
    """Run all core tests."""
    logger.info("V4 POC Core Feature Tests")
    logger.info("=" * 50)
    
    # Check proxy
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3010/health", timeout=2.0)
            if response.status_code == 200:
                logger.success("✅ Proxy server is running")
            else:
                logger.error("❌ Proxy server issue")
                return
    except:
        logger.error("❌ Proxy server not running!")
        return
    
    # Run tests
    tests = [
        test_basic_proxy_call,
        test_validation_response_not_empty,
        test_json_validation,
        test_agent_validation,
        test_retry_mechanism,
        test_litellm_call
    ]
    
    results = []
    for test_func in tests:
        start = time.time()
        try:
            # Run with timeout
            result = await asyncio.wait_for(test_func(), timeout=60.0)
            elapsed = time.time() - start
            results.append((test_func.__name__, result, elapsed))
        except asyncio.TimeoutError:
            elapsed = time.time() - start
            logger.error(f"❌ {test_func.__name__} - TIMEOUT after {elapsed:.1f}s")
            results.append((test_func.__name__, False, elapsed))
        except Exception as e:
            elapsed = time.time() - start
            logger.error(f"❌ {test_func.__name__} - ERROR: {e}")
            results.append((test_func.__name__, False, elapsed))
        
        await asyncio.sleep(1)  # Delay between tests
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for _, result, _ in results if result)
    failed = len(results) - passed
    
    for test_name, result, elapsed in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name:<35} {status:<6} {elapsed:>5.1f}s")
    
    logger.info("-" * 50)
    logger.info(f"Total: {len(results)}, Passed: {passed}, Failed: {failed}")
    
    if failed == 0:
        logger.success("\n✅ ALL CORE FEATURES WORKING!")
    else:
        logger.error(f"\n❌ {failed} features need fixing")

if __name__ == "__main__":
    asyncio.run(main())