"""
Task 3 Verification: Test Core Caller and Providers

This script verifies that all Task 3 components work correctly together.
"""

import sys
import asyncio
from loguru import logger

from llm_call.core.config.loader import load_configuration
from llm_call.core.caller import make_llm_request, _prepare_messages_and_params

# Load config at module level
config = load_configuration()
from llm_call.core.router import resolve_route
from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
from llm_call.core.providers.litellm_provider import LiteLLMProvider


async def test_task3_components():
    """Test all Task 3 components."""
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: All components import successfully
    total_tests += 1
    try:
        # All imports are at the top - if we get here, they worked
        logger.success("✅ All components import successfully")
    except Exception as e:
        all_validation_failures.append(f"Import test failed: {e}")
    
    # Test 2: Provider hierarchy
    total_tests += 1
    try:
        # Verify providers inherit from base
        assert issubclass(ClaudeCLIProxyProvider, BaseLLMProvider)
        assert issubclass(LiteLLMProvider, BaseLLMProvider)
        logger.success("✅ Provider hierarchy correct")
    except Exception as e:
        all_validation_failures.append(f"Provider hierarchy test failed: {e}")
    
    # Test 3: Router integration
    total_tests += 1
    try:
        # Test Claude routing
        claude_config = {"model": "max/test", "messages": [{"role": "user", "content": "hi"}]}
        provider_class, params = resolve_route(claude_config)
        assert provider_class == ClaudeCLIProxyProvider
        
        # Test LiteLLM routing
        llm_config = {"model": "gpt-4", "messages": [{"role": "user", "content": "hi"}]}
        provider_class, params = resolve_route(llm_config)
        assert provider_class == LiteLLMProvider
        
        logger.success("✅ Router correctly selects providers")
    except Exception as e:
        all_validation_failures.append(f"Router integration test failed: {e}")
    
    # Test 4: Message preprocessing
    total_tests += 1
    try:
        # Test JSON mode preprocessing
        config_with_json = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "test"}],
            "response_format": {"type": "json_object"}
        }
        processed = _prepare_messages_and_params(config_with_json)
        
        # Should have system message with JSON instruction
        system_msgs = [m for m in processed["messages"] if m["role"] == "system"]
        assert len(system_msgs) > 0
        assert "JSON" in system_msgs[0]["content"]
        
        logger.success("✅ Message preprocessing works")
    except Exception as e:
        all_validation_failures.append(f"Preprocessing test failed: {e}")
    
    # Test 5: Multimodal handling
    total_tests += 1
    try:
        # Test Claude multimodal support (now supported)
        multimodal_config = {
            "model": "max/claude",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's this?"},
                    {"type": "image_url", "image_url": {"url": "image.jpg"}}
                ]
            }]
        }
        
        # Preprocess to verify multimodal is processed
        processed = _prepare_messages_and_params(multimodal_config)
        assert "skip_claude_multimodal" not in processed
        
        # Note: We can't test the full request without a running server
        # but we can verify the routing works
        provider_class, params = resolve_route(processed)
        assert provider_class == ClaudeCLIProxyProvider
        
        logger.success("✅ Multimodal handling works correctly")
    except Exception as e:
        all_validation_failures.append(f"Multimodal test failed: {e}")
    
    # Test 6: POC compatibility
    total_tests += 1
    try:
        # Verify key POC behaviors are preserved
        
        # From POC: model name routing
        assert resolve_route({"model": "max/anything", "messages": []})[0] == ClaudeCLIProxyProvider
        assert resolve_route({"model": "vertex_ai/gemini", "messages": []})[0] == LiteLLMProvider
        
        # From POC: JSON instruction text
        assert config.llm.json_mode_instruction == "You MUST respond with a valid JSON object. Do not include any text outside of the JSON structure."
        
        # From POC: default values
        assert config.llm.default_temperature == 0.1
        assert config.llm.default_max_tokens == 250
        
        logger.success("✅ POC compatibility maintained")
    except Exception as e:
        all_validation_failures.append(f"POC compatibility test failed: {e}")
    
    return all_validation_failures, total_tests


if __name__ == "__main__":
    # Run tests
    failures, tests = asyncio.run(test_task3_components())
    
    # Final validation result
    if failures:
        logger.error(f"❌ VALIDATION FAILED - {len(failures)} of {tests} tests failed:")
        for failure in failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"✅ VALIDATION PASSED - All {tests} tests produced expected results")
        logger.info("\n" + "="*60)
        logger.success("TASK 3 COMPLETE: Core Caller and Providers")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info("  ✅ core/providers/base_provider.py - Abstract base class")
        logger.info("  ✅ core/providers/claude_cli_proxy.py - Claude proxy provider")
        logger.info("  ✅ core/providers/litellm_provider.py - LiteLLM provider")
        logger.info("  ✅ core/router.py - Request routing logic")
        logger.info("  ✅ core/caller.py - Main entry point with preprocessing")
        logger.info("  ✅ All components integrated and POC-compatible")
        sys.exit(0)