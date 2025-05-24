#!/usr/bin/env python3
"""POC: Complete async polling with SQLite and proper serialization"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.async_polling_manager import AsyncPollingManager
from loguru import logger

# Simple logging
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

async def test_complete_flow():
    """Test the complete async polling flow with SQLite"""
    
    print("=== POC: Complete Async Polling with SQLite ===")
    
    # Create manager
    manager = AsyncPollingManager()
    
    # Define a mock LLM executor that returns a serializable result
    async def mock_llm_executor(config):
        """Mock LLM call that returns a dict (not ModelResponse)"""
        await asyncio.sleep(1)  # Simulate processing
        
        # Return a dict that mimics LiteLLM response structure
        return {
            "id": "mock-response-001",
            "choices": [{
                "message": {
                    "content": f"Response to: {config.get('messages', [{}])[0].get('content', 'unknown')}"
                }
            }],
            "model": config.get("model", "mock-model"),
            "created": 1234567890
        }
    
    # Set the executor
    manager.set_executor(mock_llm_executor)
    
    # Test 1: Submit a task
    print("\nTest 1: Submit task")
    task_id = await manager.submit_task({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "What is 2+2?"}]
    })
    print(f"✓ Submitted task: {task_id}")
    
    # Test 2: Check immediate status
    print("\nTest 2: Check immediate status")
    status = await manager.get_status(task_id)
    print(f"✓ Status: {status.status.value}")
    print(f"  Task ID type: {type(status.task_id)}")
    
    # Test 3: List active tasks
    print("\nTest 3: List active tasks")
    active_tasks = await manager.get_active_tasks()
    print(f"✓ Active tasks: {len(active_tasks)}")
    for task in active_tasks:
        print(f"  - {task.task_id}: {task.status.value}")
    
    # Test 4: Wait for completion
    print("\nTest 4: Wait for completion")
    result = await manager.wait_for_task(task_id, timeout=5)
    print(f"✓ Task completed")
    print(f"  Result type: {type(result)}")
    print(f"  Result content: {result['choices'][0]['message']['content']}")
    
    # Test 5: Verify SQLite storage
    print("\nTest 5: Verify SQLite storage")
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.execute(
        "SELECT task_id, status, result FROM tasks WHERE task_id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    if row:
        print(f"✓ Task in database: {row[0][:8]}..., status: {row[1]}")
        result_data = json.loads(row[2])
        print(f"  Stored result: {result_data['choices'][0]['message']['content']}")
    conn.close()
    
    # Test 6: Submit multiple tasks
    print("\nTest 6: Multiple concurrent tasks")
    task_ids = []
    for i in range(3):
        tid = await manager.submit_task({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"Task {i}"}]
        })
        task_ids.append(tid)
    print(f"✓ Submitted {len(task_ids)} tasks")
    
    # Wait for all to complete
    results = await asyncio.gather(*[
        manager.wait_for_task(tid, timeout=5) for tid in task_ids
    ])
    print(f"✓ All tasks completed")
    for i, result in enumerate(results):
        print(f"  Task {i}: {result['choices'][0]['message']['content']}")
    
    print("\n✓ All tests passed!")

if __name__ == "__main__":
    # Clean up any existing database
    import os
    if os.path.exists("llm_polling_tasks.db"):
        os.remove("llm_polling_tasks.db")
    
    # Run the test
    asyncio.run(test_complete_flow())
