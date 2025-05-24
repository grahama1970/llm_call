#!/usr/bin/env python3
"""Run all essential v4 tests with proper error handling."""

import asyncio
import json
import sys
import os
import time
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# Track test results
test_results = []

async def run_single_test(test_case):
    """Run a single test case with timeout."""
    test_id = test_case['test_case_id']
    logger.info(f"\nRunning: {test_id}")
    
    try:
        # Extract the llm_config
        llm_config = test_case['llm_config'].copy()
        
        # Add validation strategies if specified
        if 'validation_strategies' in test_case:
            llm_config['validation'] = test_case['validation_strategies']
        
        # Add retry config if specified
        if 'retry_config' in test_case:
            llm_config['retry_config'] = test_case['retry_config']
        
        # Run the LLM call with timeout
        start_time = time.time()
        
        # Create task with timeout
        task = asyncio.create_task(llm_call(llm_config))
        response = await asyncio.wait_for(task, timeout=90.0)  # 90 second timeout per test
        
        elapsed = time.time() - start_time
        
        if response:
            if isinstance(response, dict):
                if "error" in response:
                    logger.error(f"❌ FAILED - Error: {response.get('error', 'Unknown error')}")
                    if "Human review needed" in response.get('error', ''):
                        logger.info(f"   Details: {response.get('details', 'N/A')}")
                    test_results.append((test_id, False, f"Error: {response.get('error')}", elapsed))
                    return False
                elif "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    logger.success(f"✅ PASSED in {elapsed:.1f}s")
                    logger.info(f"   Preview: {content[:100]}...")
                    test_results.append((test_id, True, "Success", elapsed))
                    return True
                else:
                    logger.warning(f"⚠️  FAILED - Unexpected response format")
                    test_results.append((test_id, False, "Unexpected response format", elapsed))
                    return False
            else:
                # LiteLLM ModelResponse
                if hasattr(response, 'choices'):
                    content = response.choices[0].message.content
                    logger.success(f"✅ PASSED in {elapsed:.1f}s")
                    logger.info(f"   Preview: {content[:100]}...")
                    test_results.append((test_id, True, "Success", elapsed))
                    return True
                else:
                    logger.error(f"❌ FAILED - Unexpected response type: {type(response)}")
                    test_results.append((test_id, False, f"Unexpected type: {type(response)}", elapsed))
                    return False
        else:
            logger.error(f"❌ FAILED - No response received")
            test_results.append((test_id, False, "No response", elapsed))
            return False
            
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        logger.error(f"❌ FAILED - Timeout after {elapsed:.1f}s")
        test_results.append((test_id, False, "Timeout", elapsed))
        return False
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ FAILED - Exception: {type(e).__name__}: {str(e)[:100]}")
        test_results.append((test_id, False, f"Exception: {type(e).__name__}", elapsed))
        return False

async def main():
    """Run all essential tests."""
    # Load test cases
    test_file = Path("src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json")
    logger.info(f"Loading tests from: {test_file}")
    
    with open(test_file, 'r') as f:
        test_cases = json.load(f)
    
    logger.info(f"Found {len(test_cases)} test cases")
    
    # Check if proxy is running
    logger.info("\nChecking proxy server...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3010/health", timeout=2.0)
            if response.status_code == 200:
                logger.success("✅ Proxy server is running")
            else:
                logger.warning("⚠️  Proxy server returned non-200 status")
    except:
        logger.error("❌ Proxy server is not running! Start it with:")
        logger.error("   python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return
    
    # Run tests
    logger.info("\n" + "="*60)
    logger.info("STARTING TEST EXECUTION")
    logger.info("="*60)
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        logger.info(f"\nTest {i+1}/{len(test_cases)}: {test_case['test_case_id']}")
        
        if await run_single_test(test_case):
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    # Detailed results table
    logger.info("\nDetailed Results:")
    logger.info(f"{'Test ID':<40} {'Result':<10} {'Time':<8} {'Details'}")
    logger.info("-" * 80)
    
    for test_id, success, details, elapsed in test_results:
        status = "PASS" if success else "FAIL"
        logger.info(f"{test_id:<40} {status:<10} {elapsed:>6.1f}s  {details}")
    
    logger.info("\n" + "-" * 80)
    logger.success(f"Passed: {passed}")
    logger.error(f"Failed: {failed}") 
    logger.info(f"Total:  {len(test_cases)}")
    
    success_rate = (passed / len(test_cases)) * 100 if test_cases else 0
    logger.info(f"Success Rate: {success_rate:.1f}%")
    
    if failed == 0:
        logger.success("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        logger.error(f"\n❌ {failed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())