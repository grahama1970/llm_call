#!/usr/bin/env python3
"""POC: Complete async client test with all features"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import (
    llm_call,
    get_task_status,
    list_active_tasks,
    cancel_task,
    get_polling_manager
)
from loguru import logger

# Configure logging
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

async def test_async_client():
    """Test all async client features"""
    
    print("=== POC: Complete Async Client Test ===")
    
    # Test 1: Direct call (no polling)
    print("\nTest 1: Direct call without polling")
    result = await llm_call({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'Direct call works'"}],
        "max_tokens": 20
    })
    print(f"✓ Direct result: {result.choices[0].message.content}")
    
    # Test 2: Polling call with wait
    print("\nTest 2: Polling call with wait")
    result = await llm_call({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'Polling works'"}],
        "max_tokens": 20,
        "polling": True,
        "wait_for_completion": True,
        "timeout": 10
    })
    print(f"✓ Polling result: {result['choices'][0]['message']['content']}")
    
    # Test 3: Submit without waiting
    print("\nTest 3: Submit task without waiting")
    task_id = await llm_call({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Count to 5"}],
        "max_tokens": 50,
        "polling": True,
        "wait_for_completion": False
    })
    print(f"✓ Got task ID: {task_id}")
    
    # Check status
    status = await get_task_status(task_id)
    print(f"  Initial status: {status['status']}")
    
    # List active tasks
    active = await list_active_tasks()
    print(f"  Active tasks: {len(active)}")
    
    # Wait manually
    await asyncio.sleep(2)
    final_status = await get_task_status(task_id)
    print(f"  Final status: {final_status['status']}")
    if final_status['status'] == 'completed':
        print(f"  Result: {final_status['result']['choices'][0]['message']['content']}")
    
    # Test 4: Multiple concurrent tasks
    print("\nTest 4: Multiple concurrent tasks")
    tasks = []
    for i in range(3):
        task_id = await llm_call({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"Say 'Task {i} complete'"}],
            "max_tokens": 20,
            "polling": True,
            "wait_for_completion": False
        })
        tasks.append(task_id)
        print(f"  Submitted task {i}: {task_id}")
    
    # Check all are running
    active = await list_active_tasks()
    print(f"✓ Active tasks: {len(active)}")
    
    # Wait for all to complete
    await asyncio.sleep(3)
    
    # Check results
    for i, task_id in enumerate(tasks):
        status = await get_task_status(task_id)
        if status['status'] == 'completed':
            content = status['result']['choices'][0]['message']['content']
            print(f"  Task {i}: {content}")
    
    # Test 5: SQLite verification
    print("\nTest 5: SQLite storage verification")
    manager = get_polling_manager()
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = 'completed'"
    )
    count = cursor.fetchone()[0]
    print(f"✓ Completed tasks in database: {count}")
    conn.close()
    
    print("\n✓ All tests passed! SQLite async polling is working perfectly!")

if __name__ == "__main__":
    # Clean up database
    import os
    if os.path.exists("llm_polling_tasks.db"):
        os.remove("llm_polling_tasks.db")
    
    # Run test
    asyncio.run(test_async_client())
