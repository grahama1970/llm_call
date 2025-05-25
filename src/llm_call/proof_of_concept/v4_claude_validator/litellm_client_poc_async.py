"""
V4 LiteLLM Client with Async Polling Support

This version integrates the async polling manager to handle long-running
Claude agent calls without timeouts, using proper async patterns.

Key improvements:
- Automatic detection of long-running calls (max/* models, agent validation)
- Seamless async execution without creating new threads
- Optional polling mode for non-blocking operation
"""

import asyncio
from typing import Dict, Any, Union, Optional, List
from loguru import logger

# Import the original v4 client
from .litellm_client_poc import (
    llm_call as original_llm_call,
    determine_llm_route_and_params,
    _execute_proxy_call_for_retry_loop,
    _execute_litellm_call_for_retry_loop,
    AsyncValidationStrategy,
    poc_strategy_registry,
    PoCResponseNotEmptyValidator,
    PoCAgentTaskValidator,
    retry_with_validation,
    RetryConfig,
    PoCHumanReviewNeededError,
    RetryError
)

# Import async polling manager
from ..async_polling_manager import AsyncPollingManager, TaskStatus


# Global polling manager instance
_polling_manager: Optional[AsyncPollingManager] = None


def get_polling_manager() -> AsyncPollingManager:
    """Get or create the global polling manager."""
    global _polling_manager
    if _polling_manager is None:
        _polling_manager = AsyncPollingManager()
        async def clean_executor(config):
            # Remove custom polling parameters before calling original
            clean_config = {k: v for k, v in config.items() 
                           if k not in ['polling', 'wait_for_completion', 'timeout']}
            result = await original_llm_call(clean_config)
            
            # Convert ModelResponse to dict for JSON serialization
            if hasattr(result, 'model_dump'):
                # Use pydantic v2 method (preferred)
                return result.model_dump(mode='json')
            elif hasattr(result, 'model_dump_json'):
                # Alternative pydantic v2 method
                import json
                return json.loads(result.model_dump_json())
            elif hasattr(result, 'dict'):
                # Use pydantic v1 method
                return result.dict()
            elif hasattr(result, 'to_dict'):
                # Some objects have a to_dict method
                return result.to_dict()
            elif hasattr(result, '__dict__'):
                # Fallback to dict conversion
                return vars(result)
            else:
                # Already a dict or basic type
                return result
                
        _polling_manager.set_executor(clean_executor)
    return _polling_manager


def is_long_running_call(llm_config: Dict[str, Any]) -> bool:
    """
    Determine if this call is likely to be long-running.
    
    Criteria:
    - Model starts with 'max/' (Claude proxy calls)
    - Has agent_task validation (recursive calls)
    - Has MCP configuration (file operations)
    - Explicit long_running flag
    """
    model = llm_config.get('model', '').lower()
    
    # Check for Claude proxy models
    if model.startswith('max/'):
        return True
        
    # Check for agent validation
    validations = llm_config.get('validation', [])
    if not isinstance(validations, list):
        validations = [validations] if validations else []
        
    for val in validations:
        if isinstance(val, dict) and val.get('type') == 'agent_task':
            return True
            
    # Check for MCP config
    if 'mcp_config' in llm_config:
        return True
        
    # Check explicit flag
    if llm_config.get('long_running', False):
        return True
        
    return False


async def llm_call(llm_config_input: Dict[str, Any], 
                  use_polling: Optional[bool] = None) -> Union[Dict[str, Any], str]:
    """
    Enhanced LLM call with automatic polling for long-running operations.
    
    Args:
        llm_config_input: Standard LLM configuration
        use_polling: Force polling mode (None=auto, True=always, False=never)
        
    Returns:
        - If not using polling: Standard LLM response
        - If using polling: Task ID string (check status with polling manager)
    """
    # Determine if we should use polling
    if use_polling is None:
        use_polling = llm_config_input.get('polling', False) or is_long_running_call(llm_config_input)
        
    if not use_polling:
        # Direct call - wait for completion
        # Clean config by removing custom parameters
        clean_config = {k: v for k, v in llm_config_input.items() 
                       if k not in ['polling', 'wait_for_completion', 'timeout']}
        result = await original_llm_call(clean_config)
        
        # Convert ModelResponse to dict if needed
        if hasattr(result, 'model_dump'):
            return result.model_dump(mode='json')
        elif hasattr(result, 'dict'):
            return result.dict()
        elif isinstance(result, dict):
            return result
        else:
            # Fallback
            return vars(result) if hasattr(result, '__dict__') else result
        
    # Submit to polling manager
    manager = get_polling_manager()
    task_id = await manager.submit_task(llm_config_input)
    
    # Check if caller wants to wait
    if llm_config_input.get('wait_for_completion', False):
        timeout = llm_config_input.get('timeout', 300)  # 5 minute default
        try:
            result = await manager.wait_for_task(task_id, timeout=timeout)
            return result
        except TimeoutError:
            logger.warning(f"Task {task_id} timed out, returning task ID for polling")
            return task_id
            
    # Return task ID for polling
    return task_id


async def llm_call_with_timeout(llm_config_input: Dict[str, Any],
                               timeout: float = 30.0) -> Dict[str, Any]:
    """
    Call LLM with a timeout using asyncio.
    
    Falls back to polling if timeout is exceeded.
    """
    try:
        # Try direct call with timeout
        result = await asyncio.wait_for(
            original_llm_call(llm_config_input),
            timeout=timeout
        )
        # Convert ModelResponse to dict if needed
        if hasattr(result, 'model_dump'):
            return result.model_dump(mode='json')
        elif hasattr(result, 'dict'):
            return result.dict()
        elif isinstance(result, dict):
            return result
        else:
            # Fallback
            return vars(result) if hasattr(result, '__dict__') else result
    except asyncio.TimeoutError:
        logger.warning(f"Direct call timed out after {timeout}s, switching to polling mode")
        
        # Submit to polling and wait
        manager = get_polling_manager()
        task_id = await manager.submit_task(llm_config_input)
        
        # Wait for completion with extended timeout
        return await manager.wait_for_task(task_id, timeout=timeout * 10)


# Convenience functions for polling operations
async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get the status of a polling task."""
    manager = get_polling_manager()
    task_info = await manager.get_status(task_id)
    
    if not task_info:
        return None
        
    return {
        'task_id': task_info.task_id,
        'status': task_info.status.value,
        'created_at': task_info.created_at,
        'started_at': task_info.started_at,
        'completed_at': task_info.completed_at,
        'result': task_info.result,
        'error': task_info.error,
        'progress': task_info.progress
    }


async def wait_for_task(task_id: str, timeout: Optional[float] = None) -> Dict[str, Any]:
    """Wait for a task to complete."""
    manager = get_polling_manager()
    return await manager.wait_for_task(task_id, timeout=timeout)


async def cancel_task(task_id: str) -> bool:
    """Cancel a running task."""
    manager = get_polling_manager()
    return await manager.cancel_task(task_id)


async def list_active_tasks() -> List[Dict[str, Any]]:
    """List all active tasks."""
    manager = get_polling_manager()
    tasks = await manager.get_active_tasks()
    
    return [
        {
            'task_id': task.task_id,
            'status': task.status.value,
            'model': task.llm_config.get('model', 'unknown'),
            'created_at': task.created_at,
            'started_at': task.started_at
        }
        for task in tasks
    ]


# Validation function
if __name__ == "__main__":
    async def test_async_llm_call():
        """Test the async LLM call functionality."""
        
        # Test 1: Quick call (should not use polling)
        print("\nTest 1: Quick LiteLLM call")
        config1 = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say 'test'"}],
            "max_tokens": 5
        }
        
        result1 = await llm_call(config1)
        print(f"Result type: {type(result1)}")
        print(f"Result: {result1}")
        
        # Test 2: Long-running call (should use polling)
        print("\nTest 2: Long-running Claude call")
        config2 = {
            "model": "max/text-general",
            "messages": [{"role": "user", "content": "Explain quantum computing"}]
        }
        
        result2 = await llm_call(config2)
        print(f"Result type: {type(result2)}")
        
        if isinstance(result2, str):
            print(f"Got task ID: {result2}")
            
            # Check status
            status = await get_task_status(result2)
            print(f"Task status: {status['status']}")
            
            # Wait for completion
            print("Waiting for completion...")
            final_result = await wait_for_task(result2, timeout=60)
            print(f"Final result: {final_result}")
            
        # Test 3: With timeout
        print("\nTest 3: Call with timeout")
        config3 = {
            "model": "max/text-general",
            "messages": [{"role": "user", "content": "Count to 10 slowly"}]
        }
        
        try:
            result3 = await llm_call_with_timeout(config3, timeout=5)
            print(f"Got result: {result3}")
        except Exception as e:
            print(f"Error: {e}")
            
        # Test 4: List active tasks
        print("\nTest 4: List active tasks")
        active = await list_active_tasks()
        print(f"Active tasks: {len(active)}")
        for task in active:
            print(f"  - {task['task_id']}: {task['status']} ({task['model']})")
            
    # Run tests
    asyncio.run(test_async_llm_call())
