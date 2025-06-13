"""
Request router for LLM providers.
Module: router.py

This module determines which provider to use based on the model name
and prepares the appropriate parameters.

Links:
- Provider pattern documentation: https://refactoring.guru/design-patterns/strategy

Sample usage:
    provider_class, api_params = resolve_route(llm_config)
    provider = provider_class()

Expected output:
    Tuple of (provider class, prepared parameters dict)
"""

import os
from typing import Dict, Any, Tuple, Type
from loguru import logger

from llm_call.core.config.loader import load_configuration

# Load config at module level
config = load_configuration()
from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
from llm_call.core.providers.litellm_provider import LiteLLMProvider


def resolve_route(llm_config: Dict[str, Any]) -> Tuple[Type[BaseLLMProvider], Dict[str, Any]]:
    """
    Determine the appropriate provider and prepare parameters.
    
    This function implements the routing logic from the POC's
    determine_llm_route_and_params function.
    
    Args:
        llm_config: Configuration dict with model, messages, etc.
        
    Returns:
        Tuple of (provider class, prepared API parameters)
    """
    model_name_original = llm_config.get("model", "")
    model_name_lower = model_name_original.lower()
    
    if not model_name_original:
        raise ValueError(" 'model' field is required in llm_config.")
    
    logger.debug(f"[Router] Resolving route for model: {model_name_original}")
    
    # Route to Claude CLI proxy for "max/" models (from POC)
    if model_name_lower.startswith("max/"):
        logger.info(f"️ Determined route: PROXY for model '{model_name_original}'")
        
        # Prepare parameters for Claude proxy
        api_params = {
            "model": model_name_original,
            "temperature": llm_config.get("temperature", config.llm.default_temperature),
            "max_tokens": llm_config.get("max_tokens", config.llm.default_max_tokens),
            "stream": llm_config.get("stream", False),
        }
        
        # Add response format if present
        if "response_format" in llm_config:
            api_params["response_format"] = llm_config["response_format"]
        
        return ClaudeCLIProxyProvider, api_params
    
    # Route to LiteLLM for all other models
    else:
        logger.info(f"️ Determined route: LITELLM for model '{model_name_original}'")
        
        # Start with a copy of llm_config for LiteLLM
        api_params = llm_config.copy()
        
        # Remove utility keys not meant for LiteLLM (from POC)
        api_params.pop("image_directory", None)
        api_params.pop("max_image_size_kb", None)
        api_params.pop("vertex_credentials_path", None)
        api_params.pop("retry_config", None)  # Remove retry config
        api_params.pop("skip_claude_multimodal", None)  # Remove internal flag
        api_params.pop("provider", None)  # Remove provider key - not an API param
        
        # Handle Runpod endpoints (OpenAI-compatible)
        if model_name_lower.startswith("runpod/"):
            # Extract the actual model name and pod ID
            # Format: runpod/{pod_id}/{model_name} or runpod/{model_name}
            parts = model_name_original.split("/", 2)
            
            if len(parts) == 3:
                # runpod/{pod_id}/{model_name}
                pod_id = parts[1]
                actual_model = parts[2]
            else:
                # runpod/{model_name} - require api_base to be provided
                actual_model = parts[1]
                pod_id = None
            
            # Set up OpenAI-compatible routing for Runpod
            api_params["model"] = f"openai/{actual_model}"
            
            # Set api_base from pod_id or use provided api_base
            if pod_id and "api_base" not in api_params:
                api_params["api_base"] = f"https://{pod_id}-8000.proxy.runpod.net/v1"
            elif "api_base" not in api_params:
                raise ValueError(
                    "Runpod model requires either pod_id in model name (runpod/{pod_id}/{model}) "
                    "or api_base parameter"
                )
            
            # Runpod uses empty API key
            if "api_key" not in api_params:
                api_params["api_key"] = "EMPTY"
            
            logger.info(f"Routing Runpod model '{actual_model}' via {api_params.get('api_base')}")
        
        # Handle Vertex AI specific parameters (from POC)
        elif model_name_lower.startswith("vertex_ai/"):
            if "vertex_project" not in api_params:
                project = os.getenv("LITELLM_VERTEX_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT"))
                if project:
                    api_params["vertex_project"] = project
            
            if "vertex_location" not in api_params:
                location = os.getenv("LITELLM_VERTEX_LOCATION", os.getenv("GOOGLE_CLOUD_REGION"))
                if location:
                    api_params["vertex_location"] = location
        
        return LiteLLMProvider, api_params


# Test function
if __name__ == "__main__":
    import sys
    
    logger.info("Testing router...")
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Claude proxy routing
    total_tests += 1
    try:
        test_config = {
            "model": "max/test-model",
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 0.5
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == ClaudeCLIProxyProvider
        assert params["model"] == "max/test-model"
        assert params["temperature"] == 0.5
        logger.success(" Claude proxy routing works")
    except Exception as e:
        all_validation_failures.append(f"Claude routing failed: {e}")
    
    # Test 2: LiteLLM routing
    total_tests += 1
    try:
        test_config = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 100
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["model"] == "gpt-4"
        assert params["max_tokens"] == 100
        assert "messages" in params
        logger.success(" LiteLLM routing works")
    except Exception as e:
        all_validation_failures.append(f"LiteLLM routing failed: {e}")
    
    # Test 3: Vertex AI parameter injection
    total_tests += 1
    try:
        test_config = {
            "model": "vertex_ai/gemini-pro",
            "messages": [{"role": "user", "content": "test"}]
        }
        
        # Set env vars for test
        os.environ["LITELLM_VERTEX_PROJECT"] = "test-project"
        os.environ["LITELLM_VERTEX_LOCATION"] = "us-central1"
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["vertex_project"] == "test-project"
        assert params["vertex_location"] == "us-central1"
        logger.success(" Vertex AI parameter injection works")
    except Exception as e:
        all_validation_failures.append(f"Vertex AI routing failed: {e}")
    
    # Test 4: Runpod routing with pod ID
    total_tests += 1
    try:
        test_config = {
            "model": "runpod/abc123xyz/llama-3-70b",
            "messages": [{"role": "user", "content": "test"}],
            "temperature": 0.7
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["model"] == "openai/llama-3-70b"
        assert params["api_base"] == "https://abc123xyz-8000.proxy.runpod.net/v1"
        assert params["api_key"] == "EMPTY"
        logger.success(" Runpod routing with pod ID works")
    except Exception as e:
        all_validation_failures.append(f"Runpod routing with pod ID failed: {e}")
    
    # Test 5: Runpod routing with api_base
    total_tests += 1
    try:
        test_config = {
            "model": "runpod/llama-3-70b",
            "messages": [{"role": "user", "content": "test"}],
            "api_base": "https://custom-8000.proxy.runpod.net/v1"
        }
        
        provider_class, params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider
        assert params["model"] == "openai/llama-3-70b"
        assert params["api_base"] == "https://custom-8000.proxy.runpod.net/v1"
        assert params["api_key"] == "EMPTY"
        logger.success(" Runpod routing with api_base works")
    except Exception as e:
        all_validation_failures.append(f"Runpod routing with api_base failed: {e}")
    
    # Test 6: Runpod without pod ID or api_base (should fail)
    total_tests += 1
    try:
        test_config = {
            "model": "runpod/llama-3-70b",
            "messages": [{"role": "user", "content": "test"}]
        }
        
        provider_class, params = resolve_route(test_config)
        all_validation_failures.append("Should have raised ValueError for Runpod without pod ID or api_base")
    except ValueError as e:
        if "Runpod model requires" in str(e):
            logger.success(" Runpod error handling works")
        else:
            all_validation_failures.append(f"Wrong error message: {e}")
    except Exception as e:
        all_validation_failures.append(f"Wrong exception type: {e}")
    
    # Test 7: Missing model error
    total_tests += 1
    try:
        test_config = {"messages": [{"role": "user", "content": "test"}]}
        provider_class, params = resolve_route(test_config)
        all_validation_failures.append("Should have raised ValueError for missing model")
    except ValueError as e:
        if "'model' field is required" in str(e):
            logger.success(" Missing model error handling works")
        else:
            all_validation_failures.append(f"Wrong error message: {e}")
    except Exception as e:
        all_validation_failures.append(f"Wrong exception type: {e}")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f" VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f" VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)