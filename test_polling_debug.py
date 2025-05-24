#!/usr/bin/env python3
"""Debug the polling system"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import (
    list_active_tasks,
    get_task_status,
    wait_for_task
)

async def main():
    # Check active tasks
    tasks = await list_active_tasks()
    print(f"\nActive tasks: {len(tasks)}")
    
    for task_id in tasks:
        print(f"\nTask ID: {task_id}")
        status = await get_task_status(task_id)
        print(f"Status: {status}")
        
        if status and status['status'] == 'completed':
            print(f"Result: {status.get('result', 'No result')[:200]}")
        elif status and status['status'] == 'error':
            print(f"Error: {status.get('error', 'No error message')}")
            
        # Try to wait for completion
        try:
            result = await wait_for_task(task_id, timeout=5)
            print(f"Wait result type: {type(result)}")
            if hasattr(result, 'choices'):
                print("Has choices attribute")
            elif isinstance(result, dict):
                print(f"Dict keys: {result.keys()}")
        except Exception as e:
            print(f"Wait error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
