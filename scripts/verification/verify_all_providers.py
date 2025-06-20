#!/usr/bin/env python3
"""
Verify ALL providers are actually working - with real output checks.
"""
import httpx
import json
import asyncio
from datetime import datetime

async def test_provider(model: str, provider_name: str):
    """Test a single provider with actual content verification."""
    print(f"\n{'='*60}")
    print(f"Testing {provider_name}: {model}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8001/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": "What is the capital of France? Answer in one sentence."}],
                    "temperature": 0.1,
                    "max_tokens": 100
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # REAL verification - not just checking for non-null
                if content is None:
                    print(f"❌ FAILED - Content is null")
                    return False
                elif len(content.strip()) == 0:
                    print(f"❌ FAILED - Content is empty")
                    return False
                elif "paris" not in content.lower():
                    print(f"❌ FAILED - Wrong answer: {repr(content)}")
                    return False
                else:
                    print(f"✅ PASSED - Got: {repr(content)}")
                    print(f"   Length: {len(content)} chars")
                    return True
            else:
                print(f"❌ HTTP ERROR {response.status_code}: {response.text[:100]}...")
                return False
                
        except Exception as e:
            print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)[:100]}...")
            return False

async def main():
    """Test all providers with honest results."""
    print(f"Testing all providers at {datetime.now()}")
    
    providers = [
        ("gpt-3.5-turbo", "OpenAI GPT-3.5"),
        ("gpt-4o-mini", "OpenAI GPT-4o-mini"),
        ("claude-3-haiku-20240307", "Claude 3 Haiku"),
        ("ollama/llama3.2:3b", "Ollama Llama 3.2"),
        ("perplexity/llama-3.1-sonar-small-128k-online", "Perplexity"),
        ("deepseek/deepseek-chat", "DeepSeek"),
        ("vertex_ai/gemini-2.5-flash-preview-05-20", "Vertex AI Gemini"),
    ]
    
    results = []
    for model, name in providers:
        passed = await test_provider(model, name)
        results.append((name, passed))
    
    # HONEST summary
    print(f"\n{'='*60}")
    print("HONEST TEST RESULTS:")
    print(f"{'Provider':<25} {'Result':<10}")
    print("-"*35)
    
    passed_count = 0
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:<25} {status:<10}")
        if passed:
            passed_count += 1
    
    print(f"\nTotal: {passed_count}/{len(providers)} providers working")
    
    if passed_count < len(providers):
        print("\n⚠️  Some providers are failing - this needs to be fixed")
        return 1
    else:
        print("\n✅ All providers are working correctly")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)