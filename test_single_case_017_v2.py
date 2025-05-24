#!/usr/bin/env python3
"""
Test runner for Task 017 - Test individual cases from test_prompts_essential.json
Version 2: Handles async polling properly
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

async def test_max_text_001():
    """Test the max_text_001_simple_question case"""
    
    # Load test case
    test_file = Path('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json')
    with open(test_file, 'r') as f:
        test_cases = json.load(f)
    
    # Get first test case
    test_case = test_cases[0]
    assert test_case['test_case_id'] == 'max_text_001_simple_question'
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Running: {test_case['test_case_id']}")
    logger.info(f"Description: {test_case['description']}")
    logger.info(f"Model: {test_case['llm_config']['model']}")
    logger.info(f"Question: {test_case['llm_config']['question']}")
    
    # Track execution time
    start_time = time.time()
    
    try:
        # Make the LLM call
        logger.info("\nMaking LLM call...")
        response = await llm_call(test_case['llm_config'])
        
        # Check if response is a task ID (dictionary with task_id)
        if isinstance(response, dict) and 'task_id' in response:
            task_id = response['task_id']
            logger.info(f"Got task ID: {task_id}, waiting for completion...")
            
            # Wait for the task to complete
            final_response = await wait_for_task(task_id, timeout=30)
            response = final_response
            logger.info("Task completed, got final response")
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Check if polling was used
        used_polling = execution_time > 5.0  # Assume polling if > 5 seconds
        
        logger.info(f"\nResponse received in {execution_time:.2f} seconds")
        logger.info(f"Polling used: {'Yes' if used_polling else 'No'}")
        logger.info(f"Response type: {type(response)}")
        
        # Validate response structure
        validation_results = []
        
        # Check response_not_empty
        if response:
            validation_results.append(("response_not_empty", True, "Response is not empty"))
        else:
            validation_results.append(("response_not_empty", False, "Response is empty"))
        
        # Check field_present: content
        content = None
        
        # Handle different response formats
        if hasattr(response, 'choices') and len(response.choices) > 0:
            # LiteLLM ModelResponse format
            choice = response.choices[0]
            if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                content = choice.message.content
                validation_results.append(("field_present(content)", True, f"Content field exists: {len(content)} chars"))
        elif isinstance(response, dict) and 'choices' in response:
            # Dictionary format
            choices = response.get('choices', [])
            if choices and isinstance(choices[0], dict):
                message = choices[0].get('message', {})
                content = message.get('content')
                if content:
                    validation_results.append(("field_present(content)", True, f"Content field exists: {len(content)} chars"))
                else:
                    validation_results.append(("field_present(content)", False, "Content field missing in message"))
            else:
                validation_results.append(("field_present(content)", False, "No valid choices in response"))
        elif isinstance(response, dict) and 'content' in response:
            # Direct content format
            content = response['content']
            validation_results.append(("field_present(content)", True, f"Content field exists: {len(content)} chars"))
        else:
            validation_results.append(("field_present(content)", False, f"Unexpected response format: {type(response)}"))
        
        # Log actual content preview
        if content:
            logger.info(f"\nContent preview (first 200 chars):")
            logger.info(f"{content[:200]}...")
        
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
        
        return {
            'test_case_id': test_case['test_case_id'],
            'execution_time': execution_time,
            'polling_used': used_polling,
            'all_validations_passed': all_passed,
            'validation_results': validation_results,
            'response_preview': content[:200] if content else None
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"\nTest failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Execution time before error: {execution_time:.2f}s")
        
        import traceback
        logger.error(f"\nFull traceback:")
        logger.error(traceback.format_exc())
        
        return {
            'test_case_id': test_case['test_case_id'],
            'execution_time': execution_time,
            'error': str(e),
            'error_type': type(e).__name__,
            'all_validations_passed': False
        }

async def main():
    """Main entry point"""
    logger.info("Starting Task 017 - Test Case: max_text_001_simple_question")
    
    # Check for active tasks before starting
    active_tasks = await list_active_tasks()
    if active_tasks:
        logger.warning(f"Found {len(active_tasks)} active tasks before starting")
    
    # Run the test
    result = await test_max_text_001()
    
    # Check for active tasks after completion
    active_tasks_after = await list_active_tasks()
    if active_tasks_after:
        logger.warning(f"Found {len(active_tasks_after)} active tasks after completion")
    
    # Exit with appropriate code
    if result.get('all_validations_passed', False):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
