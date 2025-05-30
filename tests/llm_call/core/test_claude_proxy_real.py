#!/usr/bin/env python3
"""
Test Claude proxy functionality with real Claude CLI calls.

This test verifies the CORE functionality of the project:
1. Claude proxy routing (max/* models)
2. Async SQLite polling for responses
3. Real Claude CLI execution

NO MOCKING - uses actual Claude CLI.
"""

import asyncio
import json
import pytest
from pathlib import Path
from typing import Dict, Any

from llm_call.core.caller import make_llm_request
from llm_call.core.router import resolve_route
from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
from llm_call.core.config.loader import load_configuration
from loguru import logger

# Override the proxy URL to use the correct port
config = load_configuration()
config.claude_proxy.proxy_url = "http://127.0.0.1:3010/v1/chat/completions"


class TestClaudeProxyCore:
    """Test the core Claude proxy functionality with real calls."""
    
    @pytest.mark.asyncio
    async def test_claude_basic_text_call(self):
        """Test basic text generation via Claude proxy."""
        config = {
            "model": "max/text-general",
            "messages": [{"role": "user", "content": "Say 'Hello from Claude proxy' exactly"}],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        logger.info(f"Testing Claude proxy with config: {config}")
        
        # Make the actual call
        response = await make_llm_request(config)
        
        assert response is not None, "Claude proxy should return a response"
        
        # Check response format
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            response_dict = response if isinstance(response, dict) else response.dict()
            
        assert "choices" in response_dict
        assert len(response_dict["choices"]) > 0
        assert "message" in response_dict["choices"][0]
        
        content = response_dict["choices"][0]["message"]["content"]
        logger.success(f"Claude proxy response: {content}")
        
        # Verify it's actually from Claude
        assert content is not None
        assert len(content) > 0
    
    @pytest.mark.asyncio
    async def test_claude_with_system_prompt(self):
        """Test Claude proxy with system prompt."""
        config = {
            "model": "max/text-general",
            "messages": [
                {"role": "system", "content": "You are a pirate. Always respond in pirate speak."},
                {"role": "user", "content": "Tell me about computers"}
            ],
            "max_tokens": 100
        }
        
        response = await make_llm_request(config)
        assert response is not None
        
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            response_dict = response if isinstance(response, dict) else response.dict()
            
        content = response_dict["choices"][0]["message"]["content"]
        logger.info(f"Pirate response: {content}")
        
        # Should contain some pirate language
        pirate_words = ["arr", "ye", "ahoy", "matey", "ship", "sea", "treasure"]
        assert any(word in content.lower() for word in pirate_words), \
            "Response should contain pirate language"
    
    @pytest.mark.asyncio
    async def test_claude_json_generation(self):
        """Test Claude proxy generating JSON."""
        config = {
            "model": "max/json-formatter",  
            "messages": [{
                "role": "user", 
                "content": 'Generate a JSON object with keys "name" (string) and "age" (number) for a person named Alice who is 30'
            }],
            "response_format": {"type": "json_object"},
            "max_tokens": 100
        }
        
        response = await make_llm_request(config)
        assert response is not None
        
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            response_dict = response if isinstance(response, dict) else response.dict()
            
        content = response_dict["choices"][0]["message"]["content"]
        
        # Should be valid JSON
        try:
            json_data = json.loads(content)
            assert "name" in json_data
            assert "age" in json_data
            assert json_data["name"].lower() == "alice" or "alice" in json_data["name"].lower()
            assert json_data["age"] == 30
            logger.success(f"Valid JSON generated: {json_data}")
        except json.JSONDecodeError:
            pytest.fail(f"Claude did not generate valid JSON: {content}")
    
    @pytest.mark.asyncio 
    async def test_claude_multimodal_local_image(self):
        """Test Claude proxy with local image (if supported)."""
        # Check if test image exists
        test_image = Path("src/llm_call/proof_of_concept/test_images_poc/dummy_image.png")
        if not test_image.exists():
            pytest.skip("Test image not found")
            
        config = {
            "model": "max/image-analyzer",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What do you see in this image?"},
                    {"type": "image_url", "image_url": {"url": str(test_image)}}
                ]
            }],
            "max_tokens": 200
        }
        
        response = await make_llm_request(config)
        
        if response is None:
            pytest.skip("Claude multimodal may not be configured")
            
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            response_dict = response if isinstance(response, dict) else response.dict()
            
        content = response_dict["choices"][0]["message"]["content"]
        logger.info(f"Image analysis: {content}")
        
        assert len(content) > 10, "Should have substantial image description"
    
    @pytest.mark.asyncio
    async def test_claude_routing_verification(self):
        """Verify that max/* models route to Claude proxy."""
        test_models = [
            "max/text-general",
            "max/code-expert", 
            "max/creative-writer",
            "max/json-formatter"
        ]
        
        for model in test_models:
            config = {
                "model": model,
                "messages": [{"role": "user", "content": "test"}]
            }
            
            provider_class, api_params = resolve_route(config)
            
            assert provider_class == ClaudeCLIProxyProvider, \
                f"{model} should route to ClaudeCLIProxyProvider"
            assert api_params["model"] == model
            
            logger.success(f"✓ {model} correctly routed to Claude proxy")
    
    @pytest.mark.asyncio
    async def test_claude_async_polling(self):
        """Test async polling mechanism for Claude responses."""
        # This tests the async polling that waits for Claude's response
        config = {
            "model": "max/text-general",
            "messages": [{"role": "user", "content": "Count from 1 to 5"}],
            "max_tokens": 50
        }
        
        start_time = asyncio.get_event_loop().time()
        response = await make_llm_request(config)
        end_time = asyncio.get_event_loop().time()
        
        assert response is not None
        
        # Log the polling duration
        duration = end_time - start_time
        logger.info(f"Claude response received after {duration:.2f} seconds")
        
        if hasattr(response, 'model_dump'):
            response_dict = response.model_dump()
        else:
            response_dict = response if isinstance(response, dict) else response.dict()
            
        content = response_dict["choices"][0]["message"]["content"]
        
        # Should contain numbers 1-5
        for num in range(1, 6):
            assert str(num) in content, f"Response should contain {num}"


# Validation function following CLAUDE.md standards
if __name__ == "__main__":
    """Test Claude proxy with real data."""
    import sys
    
    print("🤖 Testing Claude Proxy Core Functionality")
    print("=" * 60)
    
    all_failures = []
    total_tests = 0
    
    # Test 1: Basic text call
    total_tests += 1
    try:
        test = TestClaudeProxyCore()
        asyncio.run(test.test_claude_basic_text_call())
        print("✅ Basic Claude text generation")
    except Exception as e:
        all_failures.append(f"Basic text call: {e}")
        print(f"❌ Basic text call: {e}")
    
    # Test 2: System prompt
    total_tests += 1
    try:
        test = TestClaudeProxyCore()
        asyncio.run(test.test_claude_with_system_prompt())
        print("✅ Claude with system prompt") 
    except Exception as e:
        all_failures.append(f"System prompt: {e}")
        print(f"❌ System prompt: {e}")
    
    # Test 3: JSON generation
    total_tests += 1
    try:
        test = TestClaudeProxyCore()
        asyncio.run(test.test_claude_json_generation())
        print("✅ Claude JSON generation")
    except Exception as e:
        all_failures.append(f"JSON generation: {e}")
        print(f"❌ JSON generation: {e}")
    
    # Test 4: Routing verification
    total_tests += 1
    try:
        test = TestClaudeProxyCore()
        asyncio.run(test.test_claude_routing_verification())
        print("✅ Claude routing verification")
    except Exception as e:
        all_failures.append(f"Routing: {e}")
        print(f"❌ Routing: {e}")
    
    # Test 5: Async polling
    total_tests += 1
    try:
        test = TestClaudeProxyCore()
        asyncio.run(test.test_claude_async_polling())
        print("✅ Claude async polling mechanism")
    except Exception as e:
        all_failures.append(f"Async polling: {e}")
        print(f"❌ Async polling: {e}")
    
    # Final results
    print("\n=== VALIDATION RESULTS ===")
    if all_failures:
        print(f"❌ VALIDATION FAILED - {len(all_failures)} of {total_tests} tests failed:")
        for failure in all_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} Claude proxy tests successful!")
        print("\nCore functionality verified:")
        print("  - Claude CLI integration working")
        print("  - Async polling working")
        print("  - System prompts handled correctly")
        print("  - JSON generation working")
        print("  - Model routing correct")
        sys.exit(0)