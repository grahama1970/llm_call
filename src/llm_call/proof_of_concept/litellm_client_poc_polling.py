"""
LiteLLM Client POC with Polling Support

This version adds polling support for long-running LLM calls, particularly
useful for Claude agent calls that may take 30+ seconds.

Usage:
    # Synchronous mode (default) - waits for completion
    response = await llm_call(config)
    
    # Async polling mode - returns immediately with task_id
    response = await llm_call(config, polling_mode=True)
    # Returns: {"task_id": "task_abc123", "status": "pending"}
    
    # Check status
    status = await get_task_status("task_abc123")
    
    # Wait for completion
    result = await wait_for_task("task_abc123", timeout=300)
"""

import asyncio
import httpx
import litellm
import json
import os
import copy
from typing import Dict, Any, Union, Optional, List
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path

# Import the original POC implementation
from llm_call.proof_of_concept.litellm_client_poc import (
    determine_llm_route_and_params,
    _execute_proxy_call_for_retry_loop,
    _execute_litellm_call_for_retry_loop,
    _recursive_llm_caller,
    FASTAPI_PROXY_URL
)

# Import retry and validation components
from llm_call.proof_of_concept.poc_retry_manager import (
    retry_with_validation_poc as retry_with_validation,
    PoCRetryConfig as RetryConfig,
    PoCHumanReviewNeededError
)
from tenacity import RetryError

# Import validation strategies
from llm_call.proof_of_concept.poc_validation_strategies import (
    PoCResponseNotEmptyValidator,
    poc_strategy_registry
)

# Import polling manager
from llm_call.proof_of_concept.polling_manager import (
    get_polling_manager,
    TaskStatus
)

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, 
          format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
          level="INFO")


# Initialize polling manager
polling_manager = get_polling_manager()


async def llm_call_with_polling(
    llm_config_input: Dict[str, Any],
    polling_mode: bool = False,
    timeout: Optional[float] = None
) -> Union[Dict[str, Any], litellm.ModelResponse, None]:
    """
    Enhanced LLM call with optional polling support.
    
    Args:
        llm_config_input: LLM configuration
        polling_mode: If True, returns immediately with task_id for polling
        timeout: Maximum time to wait (only used if polling_mode=False)
        
    Returns:
        - If polling_mode=True: {"task_id": "...", "status": "pending"}
        - If polling_mode=False: Normal LLM response (waits for completion)
    """
    # Determine if this is a long-running call
    model_name = llm_config_input.get('model', '')
    is_long_running = (
        model_name.startswith('max/') or  # Claude proxy calls
        'agent_task' in str(llm_config_input.get('validation', []))  # Agent validation
    )
    
    # Set default timeout based on call type
    if timeout is None:
        timeout = 300.0 if is_long_running else 60.0
    
    # If polling mode or long-running call, submit to background
    if polling_mode or (is_long_running and timeout > 30):
        logger.info(f"Submitting {model_name} to background execution")
        
        # Submit task
        task_id = await polling_manager.submit_task(llm_config_input)
        
        if polling_mode:
            # Return immediately with task ID
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Task submitted for background execution"
            }
        else:
            # Wait for completion
            logger.info(f"Waiting for task {task_id} to complete...")
            try:
                result = await polling_manager.wait_for_completion(
                    task_id, 
                    timeout=timeout,
                    poll_interval=3.0
                )
                return result
            except TimeoutError:
                logger.error(f"Task {task_id} timed out after {timeout}s")
                return {
                    "error": "Task timeout",
                    "task_id": task_id,
                    "timeout": timeout
                }
    else:
        # Execute directly for fast calls
        return await _llm_call_direct(llm_config_input)


async def _llm_call_direct(llm_config_input: Dict[str, Any]) -> Union[Dict[str, Any], litellm.ModelResponse, None]:
    """Direct LLM call implementation (original logic)."""
    global _recursive_llm_caller
    if _recursive_llm_caller is None:
        _recursive_llm_caller = llm_call_with_polling
        
    model_name_for_logging = llm_config_input.get('model', 'N/A')
    
    try:
        if not llm_config_input:
            logger.error("❌ 'llm_config_input' (user input) cannot be empty.")
            return None
        
        # Handle "question" format (convert to messages)
        if "question" in llm_config_input and "messages" not in llm_config_input:
            question = llm_config_input.pop("question")
            llm_config_input["messages"] = [
                {"role": "user", "content": question}
            ]
            logger.debug(f"Converted 'question' to 'messages' format")
            
        route_info = determine_llm_route_and_params(llm_config_input)
        
        if route_info["route_type"] == "skip_claude_multimodal":
            return {"error": f"Claude CLI (via proxy for model '{route_info['model_name_original']}') does not support multimodal image inputs.", 
                    "model": route_info['model_name_original']}

        actual_llm_call_func: Optional[callable] = None
        kwargs_for_retry_loop = route_info["llm_call_kwargs"].copy() 
        kwargs_for_retry_loop.pop("messages", None)

        if route_info["route_type"] == "proxy":
            actual_llm_call_func = _execute_proxy_call_for_retry_loop
            kwargs_for_retry_loop["proxy_url_actual"] = route_info["proxy_url"]
        elif route_info["route_type"] == "litellm":
            actual_llm_call_func = _execute_litellm_call_for_retry_loop
        else:
            logger.error(f"🚨 Unknown route type: {route_info.get('route_type')} for model '{model_name_for_logging}'")
            return None

        validation_config_list = llm_config_input.get("validation", [])
        if not isinstance(validation_config_list, list):
            validation_config_list = [validation_config_list] if validation_config_list else []
            
        active_validation_strategies = []
        if validation_config_list:
            logger.info(f"Found {len(validation_config_list)} validation configs for '{model_name_for_logging}'.")
        
        for val_conf in validation_config_list:
            if not isinstance(val_conf, dict): 
                logger.warning(f"Skipping invalid validation config item (not a dict): {val_conf}")
                continue
            strategy_type_name = val_conf.get("type")
            strategy_params = val_conf.get("params", {})
            
            ValidatorClass = poc_strategy_registry.get(strategy_type_name)
            if ValidatorClass:
                try:
                    validator_instance = ValidatorClass(**strategy_params)
                    if hasattr(validator_instance, "set_llm_caller") and _recursive_llm_caller:
                         validator_instance.set_llm_caller(_recursive_llm_caller) 
                    active_validation_strategies.append(validator_instance)
                    logger.info(f"Loaded validator for '{model_name_for_logging}': {strategy_type_name} with params: {strategy_params}")
                except Exception as e_val_init:
                    logger.error(f"Failed to instantiate validator '{strategy_type_name}' with params {strategy_params} for '{model_name_for_logging}': {e_val_init}")
            else:
                logger.warning(f"Unknown validation strategy type: '{strategy_type_name}' for model '{model_name_for_logging}'")
        
        if not active_validation_strategies and llm_config_input.get("default_validate", True):
             logger.info(f"No specific validators for '{model_name_for_logging}', adding default PoCResponseNotEmptyValidator.")
             active_validation_strategies.append(PoCResponseNotEmptyValidator())

        # Retry Configuration
        retry_settings_from_config = llm_config_input.get("retry_config", {})
        if "debug_mode" not in retry_settings_from_config and "debug_mode" in llm_config_input:
            retry_settings_from_config["debug_mode"] = llm_config_input["debug_mode"]
        
        current_poc_retry_config = RetryConfig(**retry_settings_from_config)

        # Extract response_format
        response_format_value = kwargs_for_retry_loop.pop("response_format", None)

        # Add progress tracking if available
        task_id = llm_config_input.get('_task_id')
        if task_id and hasattr(polling_manager, '_update_progress'):
            progress_callback = lambda p: polling_manager._update_progress(task_id, p)
            llm_config_input['_progress_callback'] = progress_callback

        final_response = await retry_with_validation(
            llm_call_func=actual_llm_call_func,
            messages=route_info["processed_messages"],
            response_format=response_format_value,
            validation_strategies=active_validation_strategies,
            config=current_poc_retry_config,
            original_llm_config=llm_config_input,
            **kwargs_for_retry_loop
        )
        
        return final_response
            
    except ValueError as ve: 
        logger.error(f"Configuration error for model '{model_name_for_logging}': {ve}")
    except PoCHumanReviewNeededError as hrne: 
        logger.error(f"🚫 HUMAN REVIEW NEEDED for model '{model_name_for_logging}': {hrne.args[0]}")
        return {"error": "Human review needed", "details": str(hrne.args[0]), 
                "last_response": hrne.last_response, 
                "validation_errors": [ve.error for ve in hrne.validation_errors if hasattr(ve, 'error')]}
    except RetryError as re_outer:
        final_exception = re_outer.last_attempt.exception()
        logger.error(f"❌ Call for model '{model_name_for_logging}' FAILED AFTER MAX RETRIES (Tenacity outer loop).")
        logger.error(f"   Last exception type: {type(final_exception).__name__}")
        logger.error(f"   Last exception details: {final_exception}")
    except Exception as e:
        logger.error(f"💥 Unexpected error in llm_call orchestrator for model '{model_name_for_logging}': {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
    return None


# Set executor for polling manager
polling_manager.set_executor(_llm_call_direct)


# Public API functions
async def llm_call(
    llm_config_input: Dict[str, Any],
    polling_mode: bool = False,
    timeout: Optional[float] = None
) -> Union[Dict[str, Any], litellm.ModelResponse, None]:
    """
    Main entry point for LLM calls with optional polling.
    
    See module docstring for usage examples.
    """
    return await llm_call_with_polling(llm_config_input, polling_mode, timeout)


async def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a background task."""
    return await polling_manager.get_task_status(task_id)


async def wait_for_task(task_id: str, timeout: float = 300.0) -> Dict[str, Any]:
    """Wait for a background task to complete."""
    return await polling_manager.wait_for_completion(task_id, timeout)


async def cancel_task(task_id: str) -> bool:
    """Cancel a background task."""
    return await polling_manager.cancel_task(task_id)


# Cleanup on shutdown
async def shutdown():
    """Shutdown polling manager."""
    await polling_manager.shutdown()


# Initialize on import
def _init():
    """Initialize module."""
    load_dotenv()
    # Start cleanup job
    asyncio.create_task(polling_manager.start_cleanup_job())


# Run initialization
_init()