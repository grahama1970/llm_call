#!/usr/bin/env python3
"""Debug the polling system - Fixed version"""

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
    
    for task_dict in tasks:
        # Extract the task_id from the dictionary
        task_id = task_dict['task_id']
        print(f"\nTask ID: {task_id}")
        print(f"Task info: {task_dict}")
        
        # Get detailed status using the string task_id
        status = await get_task_status(task_id)
        print(f"Detailed status: {status}")
        
        if status and status['status'] == 'completed':
            print(f"Result preview: {str(status.get('result', 'No result'))[:200]}...")
        elif status and status['status'] == 'error':
            print(f"Error: {status.get('error', 'No error message')}")
            
        # Try to wait for completion
        try:
            result = await wait_for_task(task_id, timeout=5)
            print(f"Wait result type: {type(result)}")
            if hasattr(result, 'choices'):
                print("Has choices attribute")
                if result.choices:
                    print(f"First choice content: {result.choices[0].message.content[:100]}...")
            elif isinstance(result, dict):
                print(f"Dict keys: {list(result.keys())}")
            elif isinstance(result, str):
                print(f"String result: {result[:200]}...")
        except asyncio.TimeoutError:
            print(f"Task timed out after 5 seconds")
        except Exception as e:
            print(f"Wait error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
