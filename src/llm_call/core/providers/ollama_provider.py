"""
Ollama provider implementation.
Module: ollama_provider.py

This provider handles direct Ollama API calls.

Links:
- Ollama API documentation: https://github.com/ollama/ollama/blob/main/docs/api.md

Sample usage:
    provider = OllamaProvider()
    response = await provider.complete(messages=[...], model="phi3:mini")

Expected output:
    Standard response object with Ollama output
"""

from typing import Dict, Any, List, Optional
import httpx
import asyncio
from loguru import logger

from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.config.loader import load_configuration

# Load settings at module level
settings = load_configuration()


class OllamaProvider(BaseLLMProvider):
    """Provider for direct Ollama API calls."""
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        response_format: Any = None,
        **kwargs
    ) -> Any:
        """
        Complete a chat conversation using Ollama.
        
        Args:
            messages: List of message dictionaries
            response_format: Optional response format (not used by Ollama)
            **kwargs: Additional parameters (model, temperature, etc.)
            
        Returns:
            Response object compatible with OpenAI format
        """
        # Extract model name - remove "ollama/" prefix if present
        model = kwargs.get("model", "phi3:mini")
        if model.startswith("ollama/"):
            model = model[7:]  # Remove "ollama/" prefix
            
        # Get API base from kwargs or environment
        api_base = kwargs.get("api_base", "http://localhost:11434")
        
        # Convert messages to single prompt (Ollama format)
        prompt = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        
        # Add final assistant prompt
        prompt += "Assistant: "
        
        logger.debug(f"[OllamaProvider] Calling model: {model} at {api_base}")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{api_base}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": kwargs.get("temperature", 0.1),
                    }
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Format response to match OpenAI structure
                return {
                    "id": f"ollama-{model}",
                    "object": "chat.completion",
                    "created": 0,
                    "model": f"ollama/{model}",
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": data.get("response", "")
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                }
                
        except Exception as e:
            logger.error(f"[OllamaProvider] Error calling {model}: {e}")
            raise


# Test function
if __name__ == "__main__":
    import sys
    
    async def test():
        provider = OllamaProvider()
        try:
            response = await provider.complete(
                messages=[{"role": "user", "content": "Say hello"}],
                model="phi3:mini"
            )
            logger.success(f"✅ Response: {response['choices'][0]['message']['content']}")
            return True
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise
    
    success = asyncio.run(test())
    sys.exit(0 if success else 1)