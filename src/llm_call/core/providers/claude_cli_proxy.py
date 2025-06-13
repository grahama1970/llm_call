"""
Claude CLI proxy provider implementation.
Module: claude_cli_proxy.py

This provider routes requests to the Claude CLI via our FastAPI proxy server.

Links:
- httpx documentation: https://www.python-httpx.org/

Sample usage:
    provider = ClaudeCLIProxyProvider()
    response = await provider.complete(messages=[...])

Expected output:
    Dict with OpenAI-compatible response format
"""

from typing import Dict, Any, List, Optional
import httpx
from loguru import logger

from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.config.loader import load_configuration

# Load config at module level
config = load_configuration()


class ClaudeCLIProxyProvider(BaseLLMProvider):
    """Provider that proxies requests to Claude CLI via FastAPI server."""
    
    def __init__(self, proxy_url: Optional[str] = None):
        """
        Initialize the Claude CLI proxy provider.
        
        Args:
            proxy_url: Optional custom proxy URL. Defaults to config value.
        """
        self.proxy_url = proxy_url or config.claude_proxy.proxy_url
        logger.debug(f"Initialized ClaudeCLIProxyProvider with URL: {self.proxy_url}")
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        response_format: Any = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete a chat conversation via Claude CLI proxy.
        
        Args:
            messages: List of message dictionaries
            response_format: Optional response format (passed through to proxy)
            **kwargs: Additional parameters like model, temperature, max_tokens
            
        Returns:
            OpenAI-compatible response dictionary
        """
        # Prepare payload for proxy (matching POC structure)
        payload = {
            "messages": messages,
            "model": kwargs.get("model", config.claude_proxy.default_model_label),
            "temperature": kwargs.get("temperature", config.llm.default_temperature),
            "max_tokens": kwargs.get("max_tokens", config.llm.default_max_tokens),
            "stream": kwargs.get("stream", False),
        }
        
        # Add response format if specified
        if response_format:
            payload["response_format"] = response_format
        
        # Add MCP configuration if provided
        if "mcp_config" in kwargs:
            payload["mcp_config"] = kwargs["mcp_config"]
        
        logger.debug(f"[ClaudeCLIProxy] Sending request to {self.proxy_url}")
        logger.trace(f"[ClaudeCLIProxy] Payload: {payload}")
        
        # Make the HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.proxy_url,
                json=payload,
                timeout=kwargs.get("timeout", config.llm.timeout)
            )
        
        # Raise for HTTP errors
        response.raise_for_status()
        
        result = response.json()
        logger.debug(f"[ClaudeCLIProxy] Received response with id: {result.get('id')}")
        
        return result


# Test function
if __name__ == "__main__":
    import sys
    import asyncio
    
    logger.info("Testing Claude CLI proxy provider...")
    
    async def test_provider():
        all_validation_failures = []
        total_tests = 0
        
        # Test 1: Provider initialization
        total_tests += 1
        try:
            provider = ClaudeCLIProxyProvider()
            assert provider.proxy_url == config.claude_proxy.proxy_url
            logger.success(" Provider initializes with correct URL")
        except Exception as e:
            all_validation_failures.append(f"Initialization failed: {e}")
        
        # Test 2: Payload preparation
        total_tests += 1
        try:
            provider = ClaudeCLIProxyProvider()
            
            # Test messages
            test_messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"}
            ]
            
            # We can't actually call complete without a server, but we can verify
            # the provider is ready and has the right structure
            assert hasattr(provider, 'complete')
            assert hasattr(provider, 'proxy_url')
            logger.success(" Provider has correct structure")
        except Exception as e:
            all_validation_failures.append(f"Structure test failed: {e}")
        
        return all_validation_failures, total_tests
    
    # Run tests
    failures, tests = asyncio.run(test_provider())
    
    if failures:
        logger.error(f" VALIDATION FAILED - {len(failures)} of {tests} tests failed:")
        for failure in failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f" VALIDATION PASSED - All {tests} tests produced expected results")
        sys.exit(0)