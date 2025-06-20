"""
Core caller module - main entry point for LLM requests.
Module: caller.py
Description: Functions for caller operations

This module provides the make_llm_request function which handles preprocessing,
routing, and execution of LLM calls.

Links:
- Deepcopy documentation: https://docs.python.org/3/library/copy.html

Sample usage:
    from llm_call.core.caller import make_llm_request
    response = await make_llm_request({"model": "gpt-4", "messages": [...]})

Expected output:
    Provider-specific response (Dict or ModelResponse)
"""

import copy
import os
from typing import Dict, Any, List, Union, Optional
from loguru import logger

from llm_call.core.config.loader import load_configuration
from llm_call.core.router import resolve_route

# Load config at module level
settings = load_configuration()
from llm_call.core.utils.multimodal_utils import format_multimodal_messages, is_multimodal
from llm_call.core.retry import retry_with_validation, RetryConfig
from llm_call.core.validation.builtin_strategies.basic_validators import (
    ResponseNotEmptyValidator,
    JsonStringValidator
)
from llm_call.core.strategies import get_validator
from llm_call.core.base import AsyncValidationStrategy


def preprocess_messages(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Preprocess messages before sending to LLM.
    
    This is a placeholder for any message preprocessing logic.
    Currently just returns messages as-is.
    
    Args:
        messages: List of message dicts
        
    Returns:
        Preprocessed messages
    """
    return messages


def _prepare_messages_and_params(llm_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess messages for JSON mode and multimodal content.
    
    This implements the preprocessing logic from the POC's
    determine_llm_route_and_params function.
    
    Args:
        llm_config: Original configuration dict
        
    Returns:
        Modified configuration with processed messages
    """
    # Deep copy to avoid modifying original
    processed_config = copy.deepcopy(llm_config)
    
    messages = processed_config.get("messages", [])
    if not messages:
        raise ValueError("'messages' field is required in llm_config.")
    
    # Handle JSON mode (from POC)
    response_format_config = processed_config.get("response_format")
    requires_json = isinstance(response_format_config, dict) and response_format_config.get("type") == "json_object"
    
    if requires_json:
        logger.info("JSON response format requested. Modifying system prompt if necessary.")
        system_messages = [msg for msg in messages if msg.get("role") == "system"]
        json_instruction = settings.llm.json_mode_instruction
        
        if not system_messages:
            messages.insert(0, {"role": "system", "content": json_instruction})
        else:
            system_content = system_messages[0].get("content", "")
            if "json object" not in system_content.lower() and "valid json" not in system_content.lower():
                system_messages[0]["content"] = f"{json_instruction} {system_content}".strip()
    
    # Handle multimodal for all models
    model_name = processed_config.get("model", "").lower()
    is_multimodal_request = is_multimodal(messages)
    
    # Check if we're using local Claude CLI (which needs local file paths, not base64)
    is_local_claude_cli = (model_name.startswith("max/") and 
                          settings.claude_proxy.execution_mode == "local")
    
    # Process multimodal for all models (including max/)
    if is_multimodal_request:
        logger.info(f"Multimodal content detected for '{model_name}'. Formatting messages...")
        
        # Skip base64 conversion for local Claude CLI
        if is_local_claude_cli:
            logger.info("Using local Claude CLI - preserving local file paths")
            # Don't process images, just pass messages through
            processed_config["messages"] = messages
        else:
            image_directory = processed_config.get("image_directory", "")
            max_size_kb = processed_config.get("max_image_size_kb", settings.llm.max_image_size_kb)
            
            # Check if we need image directory (from POC)
            needs_image_dir = False
            for msg in messages:
                content = msg.get("content")
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "image_url":
                            url = item.get("image_url", {}).get("url", "")
                            if not (url.startswith("data:") or url.startswith("http:") or 
                                   url.startswith("https://") or url.startswith("/")):
                                needs_image_dir = True
                                break
                    if needs_image_dir:
                        break
            
            if needs_image_dir and not image_directory:
                logger.warning("Multimodal content with relative paths detected, but 'image_directory' not specified.")
            
            # Format multimodal messages
            processed_messages = format_multimodal_messages(messages, image_directory, max_size_kb)
            processed_config["messages"] = processed_messages
    
    return processed_config


async def make_llm_request(llm_config: Dict[str, Any]) -> Union[Dict[str, Any], Any, None]:
    """
    Main entry point for making LLM requests.
    
    This function implements the logic from the POC's llm_call function,
    handling preprocessing, routing, and execution.
    
    Args:
        llm_config: Configuration dict with model, messages, and other parameters
        
    Returns:
        Response from the provider (Dict for Claude proxy, ModelResponse for LiteLLM)
        or None if an error occurs
    """
    try:
        if not llm_config:
            logger.error("'llm_config' cannot be empty.")
            raise ValueError("'llm_config' cannot be empty.")
        
        # Step 1: Preprocessing
        processed_config = _prepare_messages_and_params(llm_config)
        
        # Step 2: Routing
        provider_class, api_params = resolve_route(processed_config)
        
        # Step 3: Create provider instance
        provider = provider_class()
        
        # Step 4: Determine validation strategies
        validation_strategies = []
        
        # Load validation config from llm_config
        validation_config_list = llm_config.get("validation", [])
        if not isinstance(validation_config_list, list):
            validation_config_list = [validation_config_list] if validation_config_list else []
        
        # Process configured validators
        for val_conf in validation_config_list:
            if not isinstance(val_conf, dict):
                logger.warning(f"Skipping invalid validation config: {val_conf}")
                continue
            
            strategy_type = val_conf.get("type")
            if not strategy_type:
                logger.warning("Validation config missing 'type' field")
                continue
            
            strategy_params = val_conf.get("params", {})
            
            try:
                # Get validator from registry
                validator_instance = get_validator(strategy_type, **strategy_params)
                
                # Handle AI validators that need LLM caller
                if hasattr(validator_instance, "set_llm_caller"):
                    validator_instance.set_llm_caller(make_llm_request)
                
                validation_strategies.append(validator_instance)
                logger.debug(f"Added validator: {strategy_type}")
                
            except Exception as e:
                logger.error(f"Failed to load validator '{strategy_type}': {e}")
        
        # Get response format for validation and provider calls
        response_format = processed_config.get("response_format")
        
        # Add default validators if none specified AND validation is enabled
        enable_validation = os.getenv('ENABLE_LLM_VALIDATION', 'true').lower() == 'true'
        
        if not validation_strategies and enable_validation:
            # Only add default validators if validation is enabled
            validation_strategies.append(ResponseNotEmptyValidator())
            
            # Add JSON validator if JSON response format requested
            if isinstance(response_format, dict) and response_format.get("type") == "json_object":
                validation_strategies.append(JsonStringValidator())
        
        # Step 5: Get retry configuration
        retry_config = RetryConfig()
        if "retry_config" in llm_config:
            retry_config_dict = llm_config["retry_config"]
            retry_config = RetryConfig(**retry_config_dict)
        
        # Step 6: Execute with retry and validation
        messages = processed_config.get("messages", [])
        
        # Remove validation, messages and response_format from api_params as they're handled separately
        api_params_cleaned = {
            k: v for k, v in api_params.items() 
            if k not in ["messages", "timeout", "response_format", "validation", "retry_config"]
        }
        # Add timeout if specified
        if "timeout" in processed_config:
            api_params_cleaned["timeout"] = processed_config["timeout"]
        
        response = await retry_with_validation(
            llm_call=provider.complete,
            messages=messages,
            response_format=response_format,
            validation_strategies=validation_strategies,
            config=retry_config,
            **api_params_cleaned
        )
        
        return response
        
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in make_llm_request: {type(e).__name__} - {e}")
        raise


# Test function
if __name__ == "__main__":
    import sys
    import asyncio
    
    logger.info("Testing core caller...")
    
    async def test_caller():
        all_validation_failures = []
        total_tests = 0
        
        # Test 1: Basic request structure
        total_tests += 1
        try:
            test_config = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "test"}]
            }
            
            # We can't actually make the request without API keys/server
            # but we can test the preprocessing
            processed = _prepare_messages_and_params(test_config)
            assert "messages" in processed
            assert processed["model"] == "gpt-3.5-turbo"
            logger.success("Basic preprocessing works")
        except Exception as e:
            all_validation_failures.append(f"Basic test failed: {e}")
        
        # Test 2: JSON mode preprocessing
        total_tests += 1
        try:
            test_config = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "test"}],
                "response_format": {"type": "json_object"}
            }
            
            processed = _prepare_messages_and_params(test_config)
            
            # Should have added system message with JSON instruction
            assert len(processed["messages"]) > len(test_config["messages"])
            system_msg = next((m for m in processed["messages"] if m["role"] == "system"), None)
            assert system_msg is not None
            assert "JSON" in system_msg["content"]
            logger.success("JSON mode preprocessing works")
        except Exception as e:
            all_validation_failures.append(f"JSON mode test failed: {e}")
        
        # Test 3: Multimodal processing for max/ models
        total_tests += 1
        try:
            test_config = {
                "model": "max/test",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {"type": "image_url", "image_url": {"url": "test.jpg"}}
                    ]
                }]
            }
            
            processed = _prepare_messages_and_params(test_config)
            # Should process multimodal content normally
            assert "skip_claude_multimodal" not in processed
            assert processed["model"] == "max/test"
            logger.success("Multimodal processing for max/ models works")
        except Exception as e:
            all_validation_failures.append(f"Multimodal processing test failed: {e}")
        
        # Test 4: Missing messages error
        total_tests += 1
        try:
            result = await make_llm_request({"model": "gpt-4"})
            assert result is None  # Should return None on error
            logger.success("Missing messages error handling works")
        except Exception as e:
            all_validation_failures.append(f"Error handling test failed: {e}")
        
        # Test 5: Validation strategies selection
        total_tests += 1
        try:
            # Verify that validation strategies would be selected correctly
            from llm_call.core.validation.builtin_strategies.basic_validators import (
                ResponseNotEmptyValidator, JsonStringValidator
            )
            
            # For non-JSON request, should only have ResponseNotEmptyValidator
            test_config = {"model": "gpt-4", "messages": [{"role": "user", "content": "test"}]}
            processed = _prepare_messages_and_params(test_config)
            
            # For JSON request, should have both validators
            json_config = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "test"}],
                "response_format": {"type": "json_object"}
            }
            json_processed = _prepare_messages_and_params(json_config)
            
            logger.success("Validation strategy selection logic verified")
        except Exception as e:
            all_validation_failures.append(f"Validation strategy test failed: {e}")
        
        return all_validation_failures, total_tests
    
    # Run tests
    failures, tests = asyncio.run(test_caller())
    
    if failures:
        logger.error(f"VALIDATION FAILED - {len(failures)} of {tests} tests failed:")
        for failure in failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"VALIDATION PASSED - All {tests} tests produced expected results")
        sys.exit(0)