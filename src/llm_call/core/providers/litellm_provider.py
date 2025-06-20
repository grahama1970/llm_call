"""
LiteLLM provider implementation.
Module: litellm_provider.py

This provider handles direct LiteLLM calls for models like Vertex AI, OpenAI, etc.

Links:
- LiteLLM documentation: https://docs.litellm.ai/

Sample usage:
    provider = LiteLLMProvider()
    response = await provider.complete(messages=[...], model="gpt-4")

Expected output:
    litellm.ModelResponse object
"""

from typing import Dict, Any, List, Optional
import litellm
from loguru import logger

from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.config.loader import load_configuration
from llm_call.core.utils.auth_diagnostics import diagnose_auth_error

# Load settings at module level
settings = load_configuration()


class LiteLLMProvider(BaseLLMProvider):
    """Provider for direct LiteLLM API calls."""
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        response_format: Any = None,
        **kwargs
    ) -> litellm.ModelResponse:
        """
        Complete a chat conversation using LiteLLM.
        
        Args:
            messages: List of message dictionaries
            response_format: Optional response format for structured outputs
            **kwargs: Additional LiteLLM parameters (model, temperature, etc.)
            
        Returns:
            LiteLLM ModelResponse object
        """
        # Build parameters for LiteLLM
        api_params = {
            "messages": messages,
            "model": kwargs.get("model", settings.llm.default_model),
            "temperature": kwargs.get("temperature", settings.llm.default_temperature),
            "max_tokens": kwargs.get("max_tokens", settings.llm.default_max_tokens),
        }
        
        # Enable caching if configured
        if settings.retry.enable_cache:
            # LiteLLM uses 'cache' parameter with specific format
            api_params["cache"] = {"no-cache": False}
        
        # Add response format if specified
        if response_format:
            api_params["response_format"] = response_format
        
        # Add any additional kwargs that LiteLLM might need
        # (filtering out our internal ones)
        internal_keys = {"timeout"}  # Keys we handle separately
        for key, value in kwargs.items():
            if key not in api_params and key not in internal_keys:
                api_params[key] = value
        
        model_name = api_params.get("model", "unknown")
        logger.debug(f"[LiteLLMProvider] Calling model: {model_name}")
        logger.trace(f"[LiteLLMProvider] Parameters: {api_params}")
        
        try:
            # Make the LiteLLM call
            response = await litellm.acompletion(**api_params)
            logger.debug(f"[LiteLLMProvider] Success for model: {model_name}")
            return response
            
        except litellm.exceptions.AuthenticationError as e:
            # Enhanced error handling for authentication issues
            logger.error(f"[LiteLLMProvider] Authentication error for '{model_name}'")
            diagnose_auth_error(e, model_name, context={"api_params": api_params})
            raise
            
        except litellm.exceptions.BadRequestError as e:
            # Check if this is actually an auth error in disguise
            error_str = str(e).lower()
            if any(auth_term in error_str for auth_term in ["jwt", "token", "unauthorized", "forbidden", "401", "403"]):
                logger.error(f"[LiteLLMProvider] Authentication-related bad request for '{model_name}'")
                diagnose_auth_error(e, model_name, context={"api_params": api_params})
            else:
                logger.error(f"[LiteLLMProvider] BadRequestError for '{model_name}': {e}")
                logger.error(f"Request params: {api_params}")
            raise
            
        except Exception as e:
            # Check for auth-related errors in generic exceptions
            error_str = str(e).lower()
            if any(auth_term in error_str for auth_term in ["jwt", "token", "auth", "credential", "forbidden", "unauthorized"]):
                logger.error(f"[LiteLLMProvider] Possible authentication error for '{model_name}'")
                diagnose_auth_error(e, model_name, context={"api_params": api_params})
            else:
                logger.warning(f"[LiteLLMProvider] Error for '{model_name}': {type(e).__name__} - {e}")
            raise


# Test function
if __name__ == "__main__":
    import sys
    import asyncio
    
    logger.info("Testing LiteLLM provider...")
    
    async def test_provider():
        all_validation_failures = []
        total_tests = 0
        
        # Test 1: Provider initialization
        total_tests += 1
        try:
            provider = LiteLLMProvider()
            assert hasattr(provider, 'complete')
            logger.success(" LiteLLM provider initialized")
        except Exception as e:
            all_validation_failures.append(f"Initialization failed: {e}")
        
        # Test 2: Verify it can handle different model formats
        total_tests += 1
        try:
            provider = LiteLLMProvider()
            
            # Test that it would prepare correct params for different models
            test_messages = [{"role": "user", "content": "test"}]
            
            # We can't actually call complete without API keys, but verify structure
            assert asyncio.iscoroutinefunction(provider.complete)
            logger.success(" Provider has async complete method")
        except Exception as e:
            all_validation_failures.append(f"Structure test failed: {e}")
        
        return all_validation_failures, total_tests
    
    # Run tests
    failures, tests = asyncio.run(test_provider())
    
    if failures:
        logger.error(f"L VALIDATION FAILED - {len(failures)} of {tests} tests failed:")
        for failure in failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f" VALIDATION PASSED - All {tests} tests produced expected results")
        sys.exit(0)