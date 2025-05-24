#!/usr/bin/env python3
"""Test polling functionality for long-running LLM calls."""

import asyncio
import sys
import os
import time
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc_polling import (
    llm_call, get_task_status, wait_for_task, cancel_task, shutdown
)
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")


async def test_immediate_mode():
    """Test immediate mode (waits for completion)."""
    logger.info("\n=== Test 1: Immediate Mode (Simple Call) ===")
    
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'Hello from immediate mode' in 10 words or less"}]
    }
    
    start = time.time()
    response = await llm_call(config)
    elapsed = time.time() - start
    
    if response and hasattr(response, 'choices'):
        content = response.choices[0].message.content
        logger.success(f"✅ Got response in {elapsed:.1f}s: {content}")
    else:
        logger.error(f"❌ Failed: {response}")


async def test_polling_mode():
    """Test polling mode (returns immediately)."""
    logger.info("\n=== Test 2: Polling Mode (Background Execution) ===")
    
    config = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "Count from 1 to 5 slowly"}]
    }
    
    # Submit in polling mode
    response = await llm_call(config, polling_mode=True)
    
    if response and "task_id" in response:
        task_id = response["task_id"]
        logger.info(f"✅ Task submitted: {task_id}")
        
        # Poll for status
        for i in range(10):
            await asyncio.sleep(2)
            status = await get_task_status(task_id)
            if status:
                logger.info(f"   Status: {status['status']}, Progress: {status.get('progress', 0)}%")
                if status['status'] in ['completed', 'failed']:
                    break
        
        # Get final result
        if status['status'] == 'completed':
            result = status.get('result', {})
            if result and 'choices' in result:
                content = result['choices'][0]['message']['content']
                logger.success(f"✅ Result: {content}")
        else:
            logger.error(f"❌ Task failed: {status.get('error', 'Unknown error')}")
    else:
        logger.error(f"❌ Failed to submit: {response}")


async def test_wait_for_task():
    """Test wait_for_task functionality."""
    logger.info("\n=== Test 3: Wait for Task ===")
    
    config = {
        "model": "max/code-expert",
        "messages": [{"role": "user", "content": "Write a Python function to reverse a string"}],
        "validation": [{
            "type": "agent_task",
            "params": {
                "task_prompt_to_claude": "Is this valid Python code?\n\n{CODE_TO_VALIDATE}\n\nRespond with JSON: {\"validation_passed\": true, \"reasoning\": \"explanation\", \"details\": \"VALID\"}",
                "validation_model_alias": "max/text-general",
                "success_criteria": {"must_contain_in_details": "VALID"}
            }
        }]
    }
    
    # Submit task
    response = await llm_call(config, polling_mode=True)
    
    if response and "task_id" in response:
        task_id = response["task_id"]
        logger.info(f"✅ Task submitted: {task_id}")
        
        try:
            # Wait for completion
            logger.info("⏳ Waiting for task to complete...")
            result = await wait_for_task(task_id, timeout=60)
            
            if result and 'choices' in result:
                content = result['choices'][0]['message']['content']
                logger.success("✅ Task completed with validation!")
                print("\nGenerated code:")
                print("-" * 60)
                print(content)
                print("-" * 60)
        except TimeoutError:
            logger.error("❌ Task timed out")
        except Exception as e:
            logger.error(f"❌ Task failed: {e}")
    else:
        logger.error(f"❌ Failed to submit: {response}")


async def test_automatic_polling():
    """Test automatic polling for long-running calls."""
    logger.info("\n=== Test 4: Automatic Polling (Long-Running Call) ===")
    
    config = {
        "model": "max/json-expert",
        "messages": [{
            "role": "user",
            "content": "Generate a JSON object with fields: name (string), age (number), city (string)"
        }],
        "validation": [
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "name"}},
            {"type": "field_present", "params": {"field_name": "age"}},
            {"type": "field_present", "params": {"field_name": "city"}}
        ]
    }
    
    logger.info("📤 Submitting long-running call (will automatically use polling)...")
    start = time.time()
    
    # This will automatically use polling internally due to validation
    response = await llm_call(config)
    elapsed = time.time() - start
    
    if response and 'choices' in response:
        content = response['choices'][0]['message']['content']
        logger.success(f"✅ Completed in {elapsed:.1f}s")
        print("\nGenerated JSON:")
        try:
            data = json.loads(content)
            print(json.dumps(data, indent=2))
        except:
            print(content)
    else:
        logger.error(f"❌ Failed: {response}")


async def test_task_cancellation():
    """Test task cancellation."""
    logger.info("\n=== Test 5: Task Cancellation ===")
    
    config = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "Count from 1 to 100 very slowly"}]
    }
    
    # Submit task
    response = await llm_call(config, polling_mode=True)
    
    if response and "task_id" in response:
        task_id = response["task_id"]
        logger.info(f"✅ Task submitted: {task_id}")
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Cancel task
        cancelled = await cancel_task(task_id)
        if cancelled:
            logger.success("✅ Task cancelled successfully")
        else:
            logger.warning("⚠️  Failed to cancel task")
        
        # Check final status
        status = await get_task_status(task_id)
        logger.info(f"Final status: {status['status']}")
    else:
        logger.error(f"❌ Failed to submit: {response}")


async def main():
    """Run all tests."""
    logger.info("Polling Functionality Tests")
    logger.info("=" * 60)
    
    # Check proxy health
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
        logger.info("Start it with: python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return
    
    # Run tests
    try:
        await test_immediate_mode()
        await asyncio.sleep(2)
        
        await test_polling_mode()
        await asyncio.sleep(2)
        
        await test_wait_for_task()
        await asyncio.sleep(2)
        
        await test_automatic_polling()
        await asyncio.sleep(2)
        
        await test_task_cancellation()
        
    finally:
        # Cleanup
        await shutdown()
        logger.info("\n✅ All tests completed")


if __name__ == "__main__":
    asyncio.run(main())