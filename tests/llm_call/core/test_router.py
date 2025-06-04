"""
Test router functionality, particularly max/* model routing.

Tests the routing logic from Task 018 for integrating POC patterns.
"""

import pytest
from llm_call.core.router import resolve_route
from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
from llm_call.core.providers.litellm_provider import LiteLLMProvider


def test_max_model_routing():
    """Test that max/* models are routed to Claude proxy."""
    # Test case from Task 018
    test_config = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "What is the primary function of a CPU?"}],
        "temperature": 0.7
    }
    
    provider_class, api_params = resolve_route(test_config)
    
    # Verify routing
    assert provider_class == ClaudeCLIProxyProvider, f"Expected ClaudeCLIProxyProvider, got {provider_class}"
    assert api_params["model"] == "max/text-general", f"Model not preserved: {api_params['model']}"
    assert api_params["temperature"] == 0.7, f"Temperature not preserved: {api_params['temperature']}"
    
    print(f"✅ max/text-general routed to {provider_class.__name__}")
    print(f"   API params: {api_params}")


def test_claude_max_variants():
    """Test additional max model patterns from POC."""
    # Additional patterns from POC 1
    test_variants = [
        "max/text-general",
        "max/code-expert",
        "max/creative-writer"
    ]
    
    for model in test_variants:
        test_config = {
            "model": model,
            "messages": [{"role": "user", "content": "test"}]
        }
        
        provider_class, api_params = resolve_route(test_config)
        
        assert provider_class == ClaudeCLIProxyProvider, f"{model} should route to Claude proxy"
        assert api_params["model"] == model, f"Model should be preserved: {model}"
        
        print(f"✅ {model} -> {provider_class.__name__}")


def test_claude_model_aliases():
    """Test new Claude model aliases (opus, sonnet) with max/ prefix."""
    test_variants = [
        ("max/opus", "Opus alias"),
        ("max/sonnet", "Sonnet alias"),
        ("max/claude-opus-4-20250514", "Full Opus model name"),
        ("max/claude-sonnet-4-20250514", "Full Sonnet model name"),
        ("max/", "Default to opus when no model specified"),
        ("MAX/OPUS", "Case insensitive routing"),
        ("Max/Sonnet", "Mixed case routing")
    ]
    
    for model, description in test_variants:
        test_config = {
            "model": model,
            "messages": [{"role": "user", "content": "test"}]
        }
        
        provider_class, api_params = resolve_route(test_config)
        
        assert provider_class == ClaudeCLIProxyProvider, f"{model} ({description}) should route to Claude proxy"
        assert api_params["model"] == model, f"Model should be preserved: {model}"
        
        print(f"✅ {model} ({description}) -> {provider_class.__name__}")


def test_non_max_model_routing():
    """Test that non-max models route to LiteLLM."""
    test_models = [
        "gpt-4",
        "openai/gpt-3.5-turbo",
        "vertex_ai/gemini-pro",
        "anthropic/claude-3"
    ]
    
    for model in test_models:
        test_config = {
            "model": model,
            "messages": [{"role": "user", "content": "test"}]
        }
        
        provider_class, api_params = resolve_route(test_config)
        
        assert provider_class == LiteLLMProvider, f"{model} should route to LiteLLM"
        assert api_params["model"] == model, f"Model should be preserved: {model}"
        
        print(f"✅ {model} -> {provider_class.__name__}")


def test_question_to_messages_conversion():
    """Test conversion of question format to messages format."""
    # This tests the pattern from POC's convert_message_format
    test_config = {
        "model": "max/text-general",
        "question": "What is Python?",
        "temperature": 0.5
    }
    
    # The router doesn't do message conversion, caller does
    # Just verify the router passes through the config
    provider_class, api_params = resolve_route(test_config)
    
    assert provider_class == ClaudeCLIProxyProvider
    # Router should not modify the structure
    assert "question" not in api_params, "Router should not have question field"
    assert api_params["model"] == "max/text-general"


def test_response_format_handling():
    """Test that response_format is preserved for max models."""
    test_config = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "Generate JSON"}],
        "response_format": {"type": "json_object"}
    }
    
    provider_class, api_params = resolve_route(test_config)
    
    assert provider_class == ClaudeCLIProxyProvider
    assert "response_format" in api_params, "response_format should be preserved"
    assert api_params["response_format"]["type"] == "json_object"
    
    print("✅ response_format preserved for max models")


def test_performance_benchmark():
    """Test routing performance meets POC benchmark (<50ms)."""
    import time
    
    test_config = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "test"}]
    }
    
    # Warm up
    resolve_route(test_config)
    
    # Measure
    start = time.perf_counter()
    for _ in range(100):
        provider_class, api_params = resolve_route(test_config)
    end = time.perf_counter()
    
    avg_time_ms = ((end - start) / 100) * 1000
    
    assert avg_time_ms < 50, f"Routing too slow: {avg_time_ms:.2f}ms (target: <50ms)"
    print(f"✅ Performance: {avg_time_ms:.2f}ms per routing decision")


if __name__ == "__main__":
    # Run tests directly
    print("Running router tests...")
    
    try:
        test_max_model_routing()
        test_claude_max_variants()
        test_claude_model_aliases()
        test_non_max_model_routing()
        test_question_to_messages_conversion()
        test_response_format_handling()
        test_performance_benchmark()
        
        print("\n✅ All router tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise