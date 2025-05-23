"""
Integration tests for llm_call core functionality.

This module tests the complete flow of making LLM requests through the core system.

Sample usage:
    pytest tests/test_core_integration.py

Expected output:
    All tests pass
"""

import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from llm_call.core.caller import make_llm_request
from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.base import ValidationResult


class MockSuccessProvider(BaseLLMProvider):
    """Mock provider that returns successful responses."""
    
    async def complete(self, messages, response_format=None, **kwargs):
        return {
            "id": "test-123",
            "object": "chat.completion",
            "created": 1234567890,
            "model": kwargs.get("model", "test-model"),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response"
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }


class MockJSONProvider(BaseLLMProvider):
    """Mock provider that returns JSON responses."""
    
    async def complete(self, messages, response_format=None, **kwargs):
        content = '{"result": "success", "data": {"key": "value"}}'
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                }
            }]
        }


class MockEmptyProvider(BaseLLMProvider):
    """Mock provider that returns empty responses."""
    
    async def complete(self, messages, response_format=None, **kwargs):
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": ""
                }
            }]
        }



async def test_basic_request():
    """Test basic LLM request flow."""
    config = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Hello, world!"}
        ]
    }
    
    with patch("llm_call.core.router.resolve_route") as mock_route:
        mock_route.return_value = (MockSuccessProvider, {"model": "gpt-4"})
        
        response = await make_llm_request(config)
        
        assert response is not None
        assert response["choices"][0]["message"]["content"] == "This is a test response"



async def test_json_validation():
    """Test JSON response validation."""
    config = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Return JSON"}
        ],
        "response_format": {"type": "json_object"}
    }
    
    with patch("llm_call.core.router.resolve_route") as mock_route:
        mock_route.return_value = (MockJSONProvider, {"model": "gpt-4"})
        
        response = await make_llm_request(config)
        
        assert response is not None
        # The response should pass JSON validation
        import json
        content = response["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        assert parsed["result"] == "success"



async def test_empty_response_retry():
    """Test that empty responses trigger retry."""
    config = {
        "model": "gpt-4",
        "messages": [
            {"role": "user", "content": "Test"}
        ],
        "retry_config": {
            "max_attempts": 2,
            "initial_delay": 0.1
        }
    }
    
    # Create a provider that returns empty first, then success
    call_count = 0
    
    class RetryTestProvider(BaseLLMProvider):
        async def complete(self, messages, response_format=None, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                # First call returns empty
                return {"choices": [{"message": {"content": ""}}]}
            else:
                # Second call returns success
                return {"choices": [{"message": {"content": "Success after retry"}}]}
    
    with patch("llm_call.core.router.resolve_route") as mock_route:
        mock_route.return_value = (RetryTestProvider, {"model": "gpt-4"})
        
        response = await make_llm_request(config)
        
        assert response is not None
        assert call_count == 2  # Should have retried
        assert response["choices"][0]["message"]["content"] == "Success after retry"



async def test_multimodal_claude_skip():
    """Test that multimodal requests for Claude are skipped."""
    config = {
        "model": "max/claude",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "test.jpg"}}
            ]
        }]
    }
    
    response = await make_llm_request(config)
    
    assert response is not None
    assert "error" in response
    assert "does not support multimodal" in response["error"]



async def test_missing_required_fields():
    """Test error handling for missing required fields."""
    # Missing messages
    response = await make_llm_request({"model": "gpt-4"})
    assert response is None
    
    # Missing model
    response = await make_llm_request({"messages": [{"role": "user", "content": "test"}]})
    assert response is None


# Test runner
if __name__ == "__main__":
    import sys
    from loguru import logger
    
    logger.info("Running integration tests...")
    
    # Run all test functions
    test_functions = [
        test_basic_request,
        test_json_validation,
        test_empty_response_retry,
        test_multimodal_claude_skip,
        test_missing_required_fields
    ]
    
    all_passed = True
    for test_func in test_functions:
        try:
            asyncio.run(test_func())
            logger.success(f"✅ {test_func.__name__} passed")
        except AssertionError as e:
            logger.error(f"❌ {test_func.__name__} failed: {e}")
            all_passed = False
        except Exception as e:
            logger.error(f"❌ {test_func.__name__} error: {e}")
            all_passed = False
    
    if all_passed:
        logger.success("✅ All integration tests passed")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed")
        sys.exit(1)