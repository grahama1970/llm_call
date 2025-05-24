#!/usr/bin/env python3
"""
Verify V4 implementation setup.

Checks:
1. Can import required modules
2. Proxy server is reachable
3. Environment variables are set
4. Basic Claude call works
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def check_imports():
    """Check all required imports work."""
    print("Checking imports...")
    try:
        from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
        print("✅ Can import llm_call")
    except Exception as e:
        print(f"❌ Failed to import llm_call: {e}")
        return False
    
    try:
        from src.llm_call.proof_of_concept.poc_validation_strategies import (
            PoCAgentTaskValidator,
            poc_strategy_registry
        )
        print("✅ Can import validation strategies")
        print(f"   Available validators: {list(poc_strategy_registry.keys())}")
    except Exception as e:
        print(f"❌ Failed to import validators: {e}")
        return False
    
    try:
        from src.llm_call.proof_of_concept.poc_retry_manager import (
            retry_with_validation_poc,
            PoCHumanReviewNeededError
        )
        print("✅ Can import retry manager")
    except Exception as e:
        print(f"❌ Failed to import retry manager: {e}")
        return False
    
    return True

async def check_proxy_server():
    """Check if proxy server is running."""
    print("\nChecking proxy server...")
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://127.0.0.1:3010/health", timeout=2.0)
            response.raise_for_status()
            data = response.json()
            print("✅ Proxy server is running")
            print(f"   Claude CLI: {data.get('claude_cli_path', 'Unknown')}")
            print(f"   Working dir: {data.get('working_directory', 'Unknown')}")
            print(f"   MCP support: {data.get('mcp_support', False)}")
            return True
    except Exception as e:
        print(f"❌ Proxy server not reachable: {e}")
        print("   Start it with: python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return False

def check_environment():
    """Check environment variables."""
    print("\nChecking environment...")
    
    required_vars = {
        "PERPLEXITY_API_KEY": "For perplexity-ask MCP tool",
        "ANTHROPIC_API_KEY": "For Claude API calls (if using direct)",
    }
    
    optional_vars = {
        "OPENAI_API_KEY": "For OpenAI calls",
        "VERTEX_AI_PROJECT": "For Vertex AI/Gemini calls",
        "GITHUB_TOKEN": "For GitHub MCP tool",
        "BRAVE_API_KEY": "For Brave search MCP tool"
    }
    
    all_good = True
    
    for var, desc in required_vars.items():
        if os.getenv(var):
            print(f"✅ {var} is set ({desc})")
        else:
            print(f"❌ {var} is NOT set ({desc})")
            all_good = False
    
    print("\nOptional variables:")
    for var, desc in optional_vars.items():
        if os.getenv(var):
            print(f"✅ {var} is set ({desc})")
        else:
            print(f"⚠️  {var} is not set ({desc})")
    
    return all_good

async def test_basic_claude_call():
    """Test a basic Claude call through the proxy."""
    print("\nTesting basic Claude call...")
    
    from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
    
    config = {
        "model": "max/test-basic",
        "messages": [
            {"role": "user", "content": "Say 'Hello, V4 implementation is working!' and nothing else."}
        ],
        "temperature": 0.0,
        "max_tokens": 50
    }
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict) and response.get("choices"):
                content = response["choices"][0]["message"]["content"]
                print(f"✅ Got response: {content}")
                return True
            else:
                print(f"❌ Unexpected response format: {response}")
                return False
        else:
            print("❌ No response received")
            return False
            
    except Exception as e:
        print(f"❌ Call failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mcp_availability():
    """Test if Claude can see MCP tools."""
    print("\nTesting MCP tool availability...")
    
    from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
    
    config = {
        "model": "max/test-mcp-list",
        "messages": [
            {"role": "user", "content": "List all the MCP tools you have available. Just list their names."}
        ],
        "temperature": 0.0
    }
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict) and response.get("choices"):
                content = response["choices"][0]["message"]["content"]
                print(f"✅ Claude reported available tools:")
                print(f"   {content[:200]}...")
                return True
        
        print("❌ Could not get tool list")
        return False
        
    except Exception as e:
        print(f"❌ Call failed: {e}")
        return False

async def main():
    """Run all checks."""
    print("V4 Implementation Setup Verification")
    print("=" * 50)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    results = {
        "imports": check_imports(),
        "proxy": await check_proxy_server(),
        "environment": check_environment()
    }
    
    # Only test calls if basics are working
    if results["imports"] and results["proxy"]:
        results["basic_call"] = await test_basic_claude_call()
        results["mcp_tools"] = await test_mcp_availability()
    else:
        print("\n⚠️ Skipping Claude calls due to setup issues")
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check}: {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 V4 setup is ready!")
        print("You can now run: python src/llm_call/proof_of_concept/run_v4_tests.py")
    else:
        print("\n❌ Setup has issues that need to be fixed")

if __name__ == "__main__":
    asyncio.run(main())