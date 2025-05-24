#!/usr/bin/env python3
"""POC: Test LiteLLM integration with proper serialization"""

import asyncio
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.async_polling_manager import AsyncPollingManager
from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc import llm_call as original_llm_call
from loguru import logger

# Simple logging
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

async def test_litellm_integration():
    """Test integration with real LiteLLM calls"""
    
    print("=== POC: LiteLLM Integration with Serialization ===")
    
    # Create manager
    manager = AsyncPollingManager()
    
    # Create a wrapper that handles serialization
    async def litellm_executor_with_serialization(config):
        """Execute LiteLLM call and serialize ModelResponse"""
        # Remove polling-specific parameters
        clean_config = {k: v for k, v in config.items() 
                       if k not in ['polling', 'wait_for_completion', 'timeout']}
        
        # Call original LiteLLM
        result = await original_llm_call(clean_config)
        
        # Handle serialization based on result type
        if hasattr(result, 'model_dump_json'):
            # Pydantic v2 ModelResponse
            return json.loads(result.model_dump_json())
        elif hasattr(result, 'dict'):
            # Pydantic v1
            return result.dict()
        elif isinstance(result, dict):
            # Already a dict
            return result
        else:
            # Try to convert
            return {"result": str(result)}
    
    # Set the executor
    manager.set_executor(litellm_executor_with_serialization)
    
    # Test 1: Simple LiteLLM call through polling
    print("\nTest 1: Simple LiteLLM call")
    task_id = await manager.submit_task({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'Hello from POC'"}],
        "max_tokens": 10
    })
    print(f"✓ Submitted task: {task_id}")
    
    # Wait for result
    try:
        result = await manager.wait_for_task(task_id, timeout=10)
        print(f"✓ Got result: {result['choices'][0]['message']['content']}")
        
        # Verify it's in SQLite
        import sqlite3
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.execute(
            "SELECT status, result FROM tasks WHERE task_id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        if row and row[0] == "completed":
            stored_result = json.loads(row[1])
            print(f"✓ Verified in SQLite: {stored_result['choices'][0]['message']['content']}")
        conn.close()
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {e}")
    
    # Test 2: Error handling
    print("\nTest 2: Error handling")
    error_task_id = await manager.submit_task({
        "model": "invalid-model-xxx",
        "messages": [{"role": "user", "content": "This should fail"}]
    })
    
    try:
        await manager.wait_for_task(error_task_id, timeout=10)
    except Exception as e:
        print(f"✓ Error handled correctly: {type(e).__name__}")
        
        # Check error in SQLite
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.execute(
            "SELECT status, error FROM tasks WHERE task_id = ?",
            (error_task_id,)
        )
        row = cursor.fetchone()
        if row and row[0] == "failed":
            print(f"✓ Error stored in SQLite: {row[1][:50]}...")
        conn.close()
    
    print("\n✓ POC Complete!")

if __name__ == "__main__":
    # Clean up database
    import os
    if os.path.exists("llm_polling_tasks.db"):
        os.remove("llm_polling_tasks.db")
    
    # Run test
    asyncio.run(test_litellm_integration())
