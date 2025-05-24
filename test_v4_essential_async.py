#!/usr/bin/env python3
"""
Test V4 Essential Cases with Async Polling

This script tests all essential cases from test_prompts_essential.json
using the async polling approach to handle long-running calls without timeouts.
"""

import asyncio
import json
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import (
    llm_call,
    llm_call_with_timeout,
    get_task_status,
    wait_for_task,
    list_active_tasks
)
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


async def run_test_case(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test case."""
    test_id = test_case['test_case_id']
    logger.info(f"\n{'='*60}")
    logger.info(f"Running: {test_id}")
    logger.info(f"Description: {test_case['description']}")
    
    start_time = time.time()
    
    try:
        llm_config = test_case['llm_config'].copy()
        
        # Add validation config
        if 'validation_strategies' in test_case:
            llm_config['validation'] = test_case['validation_strategies']
            
        # Add retry config
        if 'retry_config' in test_case:
            llm_config['retry_config'] = test_case['retry_config']
            
        # Determine timeout based on model
        model = llm_config.get('model', '')
        if model.startswith('max/'):
            # Claude calls need more time
            timeout = 60 if 'mcp' in model else 30
        else:
            timeout = 15
            
        logger.info(f"Using timeout: {timeout}s for model: {model}")
        
        # Make the call with timeout
        result = await llm_call_with_timeout(llm_config, timeout=timeout)
        
        elapsed = time.time() - start_time
        
        # Extract content
        content = None
        if isinstance(result, dict):
            content = result.get('content') or result.get('choices', [{}])[0].get('message', {}).get('content')
        elif hasattr(result, 'choices'):
            content = result.choices[0].message.content
            
        logger.success(f"✅ Test passed in {elapsed:.1f}s")
        if content:
            logger.info(f"Response preview: {content[:100]}...")
            
        return {
            'test_id': test_id,
            'status': 'passed',
            'elapsed': elapsed,
            'content': content
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Test failed after {elapsed:.1f}s: {str(e)[:200]}")
        
        return {
            'test_id': test_id,
            'status': 'failed',
            'elapsed': elapsed,
            'error': str(e)
        }


async def run_test_case_with_polling(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run a test case using explicit polling mode."""
    test_id = test_case['test_case_id']
    logger.info(f"\n{'='*60}")
    logger.info(f"Running (polling mode): {test_id}")
    
    start_time = time.time()
    
    try:
        llm_config = test_case['llm_config'].copy()
        
        # Add validation config
        if 'validation_strategies' in test_case:
            llm_config['validation'] = test_case['validation_strategies']
            
        # Force polling mode
        llm_config['polling'] = True
        
        # Submit task
        task_id = await llm_call(llm_config, use_polling=True)
        logger.info(f"Submitted task: {task_id}")
        
        # Poll for status
        while True:
            status = await get_task_status(task_id)
            if not status:
                raise ValueError(f"Task {task_id} not found")
                
            logger.info(f"Task status: {status['status']}")
            
            if status['status'] in ['completed', 'failed', 'timeout', 'cancelled']:
                break
                
            await asyncio.sleep(2)
            
        # Get final result
        if status['status'] == 'completed':
            result = status['result']
            elapsed = time.time() - start_time
            
            logger.success(f"✅ Test passed in {elapsed:.1f}s (polling mode)")
            
            return {
                'test_id': test_id,
                'status': 'passed',
                'elapsed': elapsed,
                'result': result
            }
        else:
            raise RuntimeError(f"Task failed with status: {status['status']}, error: {status.get('error')}")
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ Test failed: {e}")
        
        return {
            'test_id': test_id,
            'status': 'failed',
            'elapsed': elapsed,
            'error': str(e)
        }


async def main():
    """Run all essential tests."""
    # Load test cases
    test_file = Path('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json')
    with open(test_file) as f:
        test_cases = json.load(f)
        
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    # Separate by type
    quick_tests = []
    long_tests = []
    
    for test in test_cases:
        model = test['llm_config'].get('model', '')
        if model.startswith('max/') or 'mcp' in model.lower():
            long_tests.append(test)
        else:
            quick_tests.append(test)
            
    logger.info(f"Quick tests: {len(quick_tests)}, Long tests: {len(long_tests)}")
    
    results = []
    
    # Run quick tests first
    logger.info("\n" + "#"*60)
    logger.info("# RUNNING QUICK TESTS")
    logger.info("#"*60)
    
    for test in quick_tests:
        result = await run_test_case(test)
        results.append(result)
        
    # Run long tests with polling
    logger.info("\n" + "#"*60)
    logger.info("# RUNNING LONG TESTS (with polling)")
    logger.info("#"*60)
    
    # Run long tests concurrently since they use polling
    long_tasks = []
    for test in long_tests:
        task = asyncio.create_task(run_test_case_with_polling(test))
        long_tasks.append(task)
        
    # Wait for all long tests
    long_results = await asyncio.gather(*long_tasks, return_exceptions=True)
    
    for i, result in enumerate(long_results):
        if isinstance(result, Exception):
            results.append({
                'test_id': long_tests[i]['test_case_id'],
                'status': 'failed',
                'error': str(result)
            })
        else:
            results.append(result)
            
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for r in results if r['status'] == 'passed')
    failed = sum(1 for r in results if r['status'] == 'failed')
    total_time = sum(r.get('elapsed', 0) for r in results)
    
    logger.info(f"Total tests: {len(results)}")
    logger.info(f"Passed: {passed} ({passed/len(results)*100:.0f}%)")
    logger.info(f"Failed: {failed}")
    logger.info(f"Total time: {total_time:.1f}s")
    logger.info(f"Average time: {total_time/len(results):.1f}s per test")
    
    # Show failed tests
    if failed > 0:
        logger.info("\nFailed tests:")
        for r in results:
            if r['status'] == 'failed':
                logger.error(f"  - {r['test_id']}: {r.get('error', 'Unknown error')[:100]}...")
                
    # Check active tasks
    logger.info("\nChecking for remaining active tasks...")
    active = await list_active_tasks()
    if active:
        logger.warning(f"Found {len(active)} active tasks:")
        for task in active:
            logger.info(f"  - {task['task_id']}: {task['status']}")
    else:
        logger.info("No active tasks remaining")
        
    return passed == len(results)


if __name__ == "__main__":
    # Initialize cache
    from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
    initialize_litellm_cache()
    
    # Run tests
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
