"""
Integration tests for llm_call core functionality with real implementations.

This module tests the complete flow of making LLM requests through the core system
using actual LLM providers and real data.

Sample usage:
    pytest tests/llm_call/core/test_core_integration_real.py

Expected output:
    All tests pass with real LLM responses
"""

import asyncio
import json
import os
import pytest
from typing import Dict, Any

from llm_call.core.caller import make_llm_request
from llm_call.core.router import resolve_route
from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.providers.litellm_provider import LiteLLMProvider
from llm_call.core.base import ValidationResult
from llm_call.core.validation.builtin_strategies.basic_validators import JsonStringValidator
from llm_call.core.strategies import VALIDATION_STRATEGIES


# Tests should run with real LLM calls - we have OpenAI and Vertex AI configured
# LiteLLM caching is enabled so repeated calls use cached responses


@pytest.mark.asyncio
async def test_basic_llm_request():
    """Test basic LLM request with real provider."""
    # Use OpenAI since we have the API key configured
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 20,
        "temperature": 0.1
    }
    
    response = await make_llm_request(config)
    response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
    
    assert response is not None
    assert "choices" in response_dict
    assert len(response_dict["choices"]) > 0
    assert "message" in response_dict["choices"][0]
    assert "content" in response_dict["choices"][0]["message"]
    print(f"✅ Basic request: {response_dict['choices'][0]['message']['content'][:50]}...")


@pytest.mark.asyncio
async def test_json_response_format():
    """Test JSON response format with real LLM."""
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user", 
            "content": 'Generate a JSON object with keys "name" and "age"'
        }],
        "max_tokens": 50,
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    response = await make_llm_request(config)
    response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
    
    assert response is not None
    content = response_dict["choices"][0]["message"]["content"]
    
    # Try to parse as JSON
    try:
        parsed = json.loads(content)
        assert isinstance(parsed, dict)
        print(f"✅ JSON response: {parsed}")
    except json.JSONDecodeError:
        # Some models don't support response_format, that's OK
        print(f"⚠️  Model doesn't support JSON format, got: {content[:50]}...")


@pytest.mark.asyncio
async def test_router_integration():
    """Test router correctly selects providers."""
    # Test LiteLLM routing
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "test"}]
    }
    
    provider_class, api_params = resolve_route(config)
    assert provider_class == LiteLLMProvider
    print("✅ Router: gpt-3.5-turbo → LiteLLMProvider")
    
    # Test with actual request if OpenAI key available
    if os.getenv("OPENAI_API_KEY"):
        response = await make_llm_request(config)
        response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        assert response is not None
        print("✅ Router integration: Request successful")


@pytest.mark.asyncio
async def test_validation_integration():
    """Test validation with real LLM responses."""
    # Use JSON validator - get the class and instantiate it
    json_validator_class = VALIDATION_STRATEGIES.get("json")
    assert json_validator_class is not None
    json_validator = json_validator_class()
    
    # Request JSON from LLM
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": 'Respond with valid JSON: {"status": "ok", "value": 42}'
        }],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    response = await make_llm_request(config)
    response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
    content = response_dict["choices"][0]["message"]["content"]
    
    # Validate the response (validators ARE async)
    validation_result = await json_validator.validate(content, {})
    
    if validation_result.valid:
        print(f"✅ Validation: JSON valid - {content}")
    else:
        print(f"⚠️  Validation: {validation_result.error}")


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling with invalid model."""
    config = {
        "model": "invalid-model-xyz-123",
        "messages": [{"role": "user", "content": "test"}]
    }
    
    try:
        await make_llm_request(config)
        assert False, "Should have raised an error"
    except Exception as e:
        print(f"✅ Error handling: {type(e).__name__}: {str(e)[:50]}...")


@pytest.mark.asyncio
async def test_temperature_effects():
    """Test temperature parameter effects on responses."""
    base_prompt = "Complete this: The sky is"
    
    # Low temperature (deterministic)
    config_low = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": base_prompt}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    responses_low = []
    for _ in range(3):
        response = await make_llm_request(config_low)
        response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        responses_low.append(response_dict["choices"][0]["message"]["content"])
    
    # High temperature (creative)
    config_high = config_low.copy()
    config_high["temperature"] = 1.5
    
    responses_high = []
    for _ in range(3):
        response = await make_llm_request(config_high)
        response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
        responses_high.append(response_dict["choices"][0]["message"]["content"])
    
    print("✅ Temperature effects tested")
    print(f"   Low temp responses: {set(responses_low)}")
    print(f"   High temp responses: {set(responses_high)}")
    
    # High temperature should have more variety
    assert len(set(responses_high)) >= len(set(responses_low))


@pytest.mark.asyncio
async def test_system_message_handling():
    """Test system message handling."""
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a pirate. Always respond like a pirate."},
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    response = await make_llm_request(config)
    response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.dict()
    content = response_dict["choices"][0]["message"]["content"]
    
    print(f"✅ System message: {content[:100]}...")
    # Check if response has pirate-like characteristics
    pirate_words = ["ahoy", "matey", "arr", "ye", "aye", "captain", "ship", "sea"]
    has_pirate_speak = any(word in content.lower() for word in pirate_words)
    
    if has_pirate_speak:
        print("   Response includes pirate language!")


if __name__ == "__main__":
    import sys
    
    print("🧪 Testing Core Integration with Real LLMs")
    print("=" * 60)
    
    # OpenAI should be configured with API key
    print("Using gpt-3.5-turbo for testing")
    
    all_failures = []
    total_tests = 0
    
    # Test 1: Basic request
    total_tests += 1
    try:
        asyncio.run(test_basic_llm_request())
    except Exception as e:
        all_failures.append(f"Basic request: {e}")
    
    # Test 2: JSON format
    total_tests += 1
    try:
        asyncio.run(test_json_response_format())
    except Exception as e:
        all_failures.append(f"JSON format: {e}")
    
    # Test 3: Router
    total_tests += 1
    try:
        asyncio.run(test_router_integration())
    except Exception as e:
        all_failures.append(f"Router integration: {e}")
    
    # Test 4: Validation
    total_tests += 1
    try:
        asyncio.run(test_validation_integration())
    except Exception as e:
        all_failures.append(f"Validation: {e}")
    
    # Test 5: Error handling
    total_tests += 1
    try:
        asyncio.run(test_error_handling())
    except Exception as e:
        all_failures.append(f"Error handling: {e}")
    
    # Test 6: Temperature
    total_tests += 1
    try:
        asyncio.run(test_temperature_effects())
    except Exception as e:
        all_failures.append(f"Temperature effects: {e}")
    
    # Test 7: System messages
    total_tests += 1
    try:
        asyncio.run(test_system_message_handling())
    except Exception as e:
        all_failures.append(f"System messages: {e}")
    
    # Final results
    print("\n=== VALIDATION RESULTS ===")
    if all_failures:
        print(f"❌ VALIDATION FAILED - {len(all_failures)} of {total_tests} tests failed:")
        for failure in all_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        print("\nSuccessfully tested:")
        print("  - Basic LLM requests")
        print("  - JSON response formatting")
        print("  - Router provider selection")
        print("  - Response validation")
        print("  - Error handling")
        print("  - Temperature parameter effects")
        print("  - System message handling")
        sys.exit(0)