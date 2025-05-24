#!/usr/bin/env python3
"""Run all v4 validation tests directly without subprocess."""

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

async def run_single_test(test_case):
    """Run a single test case."""
    test_id = test_case['test_case_id']
    logger.info(f"Running test: {test_id}")
    logger.info(f"Description: {test_case['description']}")
    
    try:
        # Extract the llm_config
        llm_config = test_case['llm_config']
        
        # Add validation strategies if specified
        if 'validation_strategies' in test_case:
            llm_config['validation'] = test_case['validation_strategies']
        
        # Add retry config if specified
        if 'retry_config' in test_case:
            llm_config['retry_config'] = test_case['retry_config']
        
        # Run the LLM call
        start_time = time.time()
        response = await llm_call(llm_config)
        elapsed = time.time() - start_time
        
        if response:
            if isinstance(response, dict):
                if "error" in response:
                    logger.error(f"❌ Test {test_id} FAILED - Error: {response['error']}")
                    return False
                elif "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    logger.success(f"✅ Test {test_id} PASSED in {elapsed:.1f}s")
                    logger.info(f"Response preview: {content[:150]}...")
                    return True
                else:
                    logger.warning(f"Unexpected response format: {json.dumps(response, indent=2)[:200]}")
                    return False
            else:
                # LiteLLM ModelResponse
                if hasattr(response, 'choices'):
                    content = response.choices[0].message.content
                    logger.success(f"✅ Test {test_id} PASSED in {elapsed:.1f}s")
                    logger.info(f"Response preview: {content[:150]}...")
                    return True
                else:
                    logger.error(f"❌ Test {test_id} FAILED - Unexpected response type: {type(response)}")
                    return False
        else:
            logger.error(f"❌ Test {test_id} FAILED - No response received")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test {test_id} FAILED - Exception: {type(e).__name__}: {e}")
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
    logger.info("Checking if proxy server is running...")
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
    
    # Run tests one by one
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        logger.info(f"\n{'='*60}")
        logger.info(f"Test {i+1}/{len(test_cases)}")
        
        if await run_single_test(test_case):
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.success(f"Passed: {passed}")
    logger.error(f"Failed: {failed}")
    logger.info(f"Total:  {len(test_cases)}")
    
    if failed == 0:
        logger.success("✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        logger.error(f"❌ {failed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())