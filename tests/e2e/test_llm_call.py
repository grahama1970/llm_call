#!/usr/bin/env python3
"""
Test script to verify llm_call imports and max/opus routing
"""

import asyncio
import sys
sys.path.insert(0, '/home/graham/workspace/experiments/llm_call/src')

async def test_basic_import():
    """Test basic import functionality"""
    print("Testing basic import...")
    try:
        from llm_call import ask
        print("✅ Successfully imported ask from llm_call")
    except ImportError as e:
        print(f"❌ Failed to import ask: {e}")
        return False
    
    try:
        from llm_call import chat, call, ChatSession
        print("✅ Successfully imported other functions")
    except ImportError as e:
        print(f"❌ Failed to import other functions: {e}")
        return False
    
    return True

async def test_model_routing():
    """Test the model routing functionality"""
    print("\nTesting model routing...")
    
    from llm_call.core.router import resolve_route
    
    # Test max/ model routing
    test_cases = [
        {"model": "max/claude-3-5-sonnet", "expected_provider": "ClaudeCLIProxyProvider"},
        {"model": "max/claude-3-opus", "expected_provider": "ClaudeCLIProxyProvider"},
        {"model": "gpt-4", "expected_provider": "LiteLLMProvider"},
        {"model": "claude-3-opus-20240229", "expected_provider": "LiteLLMProvider"},
    ]
    
    for test_case in test_cases:
        config = {"model": test_case["model"], "messages": [{"role": "user", "content": "test"}]}
        provider_class, params = resolve_route(config)
        provider_name = provider_class.__name__
        
        if provider_name == test_case["expected_provider"]:
            print(f"✅ {test_case['model']} -> {provider_name}")
        else:
            print(f"❌ {test_case['model']} -> {provider_name} (expected {test_case['expected_provider']})")

async def test_simple_call():
    """Test a simple call using ask function"""
    print("\nTesting simple ask call...")
    
    try:
        from llm_call import ask
        
        # Test with a simple model (not max/ to avoid proxy errors)
        response = await ask(
            "Say exactly: Hello World!",
            model="gpt-3.5-turbo",
            max_tokens=10
        )
        print(f"✅ Response: {response}")
    except Exception as e:
        print(f"❌ Error calling ask: {e}")

async def test_proxy_config():
    """Test proxy configuration"""
    print("\nTesting proxy configuration...")
    
    from llm_call.core.config.loader import load_configuration
    config = load_configuration()
    
    print(f"Proxy URL: {config.claude_proxy.proxy_url}")
    print(f"Default model: {config.claude_proxy.default_model_label}")

async def main():
    """Run all tests"""
    print("=== LLM Call Import and Routing Test ===\n")
    
    # Test imports
    if not await test_basic_import():
        return
    
    # Test routing
    await test_model_routing()
    
    # Test proxy config
    await test_proxy_config()
    
    # Test simple call
    await test_simple_call()
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    asyncio.run(main())