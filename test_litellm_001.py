#!/usr/bin/env python3
"""
Test runner for Task 017 - Test litellm_001_openai_compatible
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import (
    llm_call,
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

async def test_litellm_001():
    """Test the litellm_001_openai_compatible case"""
    
    # Load test case
    test_file = Path('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json')
    with open(test_file, 'r') as f:
        test_cases = json.load(f)
    
    # Get the litellm test case (index 6)
    test_case = test_cases[6]
    assert test_case['test_case_id'] == 'litellm_001_openai_compatible'
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Running: {test_case['test_case_id']}")
    logger.info(f"Description: {test_case['description']}")
    logger.info(f"Model: {test_case['llm_config']['model']}")
    logger.info(f"Messages: {test_case['llm_config']['messages']}")
    
    # Track execution time
    start_time = time.time()
    
    try:
        # Make the LLM call - this should be quick and not use polling
        logger.info("\nMaking LLM call (should not use polling)...")
        
        response = await llm_call(test_case['llm_config'])
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        logger.info(f"\nResponse received in {execution_time:.2f} seconds")
        logger.info(f"Response type: {type(response)}")
        
        # Check if polling was used
        used_polling = isinstance(response, str) and len(response) == 36  # UUID length
        logger.info(f"Polling used: {'Yes' if used_polling else 'No'} (should be No)")
        
        # Validate response structure
        validation_results = []
        
        # Check response_not_empty
        if response:
            validation_results.append(("response_not_empty", True, "Response is not empty"))
        else:
            validation_results.append(("response_not_empty", False, "Response is empty"))
        
        # Extract content
        content = None
        if hasattr(response, 'choices') and len(response.choices) > 0:
            content = response.choices[0].message.content
            logger.info(f"\nContent: {content}")
            
            # Check if content contains '4' or 'four'
            if '4' in str(content).lower() or 'four' in str(content).lower():
                logger.info("✅ Content contains the expected answer (4)")
            else:
                logger.warning(f"⚠️  Content does not contain '4': {content}")
        elif isinstance(response, dict) and 'error' in response:
            logger.error(f"Error response: {response['error']}")
            validation_results.append(("response_not_empty", False, f"Error: {response['error']}"))
        
        # Report validation results
        logger.info(f"\n{'='*60}")
        logger.info("Validation Results:")
        all_passed = True
        for validation_name, passed, message in validation_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"  {validation_name}: {status} - {message}")
            if not passed:
                all_passed = False
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Test Case: {test_case['test_case_id']}")
        logger.info(f"Execution Time: {execution_time:.2f}s")
        logger.info(f"Polling Used: {'Yes' if used_polling else 'No'}")
        logger.info(f"Overall Result: {'✅ PASS' if all_passed else '❌ FAIL'}")
        
        return all_passed
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"\nTest failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Execution time before error: {execution_time:.2f}s")
        
        import traceback
        logger.error(traceback.format_exc())
        
        return False

async def main():
    """Main entry point"""
    logger.info("Starting Task 017 - Test Case: litellm_001_openai_compatible")
    
    # Check for active tasks before starting
    active_tasks = await list_active_tasks()
    if active_tasks:
        logger.warning(f"Found {len(active_tasks)} active tasks before starting")
    
    # Run the test
    passed = await test_litellm_001()
    
    # Check for active tasks after completion
    active_tasks_after = await list_active_tasks()
    if active_tasks_after:
        logger.warning(f"Found {len(active_tasks_after)} active tasks after completion")
    else:
        logger.info("✅ No active tasks remaining")
    
    # Exit with appropriate code
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    asyncio.run(main())
