#!/usr/bin/env python3
"""Test the complete async polling cycle with SQLite"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.async_polling_manager import AsyncPollingManager
from loguru import logger

# Configure logging
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

async def dummy_llm_call(config):
    """Simulate an LLM call"""
    await asyncio.sleep(2)  # Simulate processing
    return {
        "choices": [{
            "message": {
                "content": f"Response to: {config.get('question', config.get('messages', [{}])[0].get('content', 'unknown'))}"
            }
        }]
    }

async def test_full_cycle():
    """Test the complete cycle"""
    
    # Create manager
    manager = AsyncPollingManager()
    manager.set_executor(dummy_llm_call)
    
    # Submit a task
    logger.info("Submitting task...")
    task_id = await manager.submit_task({
        "model": "test-model",
        "question": "What is 2 + 2?"
    })
    logger.info(f"Task ID: {task_id} (type: {type(task_id)})\n")
    
    # Check status immediately
    status = await manager.get_status(task_id)
    logger.info(f"Initial status: {status.status.value}\n")
    
    # List active tasks
    active_tasks = await manager.get_active_tasks()
    logger.info(f"Active tasks: {len(active_tasks)}")
    for task in active_tasks:
        logger.info(f"  - {task.task_id}: {task.status.value}\n")
    
    # Wait for completion
    logger.info("Waiting for completion...")
    result = await manager.wait_for_task(task_id, timeout=10)
    logger.info(f"Result: {result}\n")
    
    # Final status
    final_status = await manager.get_status(task_id)
    logger.info(f"Final status: {final_status.status.value}")
    logger.info(f"Result in status: {final_status.result}\n")
    
    # Check SQLite directly
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.execute("SELECT task_id, status FROM tasks")
    logger.info("Tasks in database:")
    for row in cursor.fetchall():
        logger.info(f"  - {row[0]}: {row[1]}")
    conn.close()

if __name__ == "__main__":
    asyncio.run(test_full_cycle())
