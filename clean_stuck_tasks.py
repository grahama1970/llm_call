#!/usr/bin/env python3
"""Clean up stuck tasks"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import (
    list_active_tasks,
    cancel_task
)

async def main():
    # Get all active tasks
    tasks = await list_active_tasks()
    print(f"Found {len(tasks)} active tasks to clean up")
    
    # Cancel each task
    for task_dict in tasks:
        task_id = task_dict['task_id']
        print(f"Cancelling task: {task_id}")
        try:
            result = await cancel_task(task_id)
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Verify cleanup
    remaining = await list_active_tasks()
    print(f"\nRemaining tasks: {len(remaining)}")

if __name__ == "__main__":
    asyncio.run(main())
