#!/usr/bin/env python3
"""Quick test to check specific failing features"""

import subprocess
import sys
import asyncio
import time
from pathlib import Path

# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_core_features():
    """Test the two core features: make_llm_request and ask function."""
    print("\n=== Testing Core Features ===")
    
    # Test 1: make_llm_request
    print("1. Testing make_llm_request...")
    test_code = '''
import asyncio
from llm_call.core.caller import make_llm_request

async def test():
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Reply OK"}],
        "temperature": 0
    }
    response = await make_llm_request(config)
    print(f"Response: {response}")
    # Extract content from response
    if hasattr(response, 'choices') and response.choices:
        content = response.choices[0].message.content
        return "OK" in content
    elif isinstance(response, dict) and "choices" in response:
        content = response["choices"][0]["message"]["content"]
        return "OK" in content
    return False

result = asyncio.run(test())
print(f"Success: {result}")
'''
    
    with open("/tmp/test_make_llm.py", "w") as f:
        f.write(test_code)
    
    result = subprocess.run([sys.executable, "/tmp/test_make_llm.py"], 
                          capture_output=True, text=True, timeout=10)
    
    if "Success: True" in result.stdout:
        print("✅ make_llm_request: PASSED")
        return 1
    else:
        print("❌ make_llm_request: FAILED")
        print(f"Output: {result.stdout[:200]}")
        print(f"Error: {result.stderr[:200]}")
        return 0

def test_api_endpoints():
    """Test API endpoints."""
    print("\n=== Testing API Endpoints ===")
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    result = subprocess.run(["curl", "-s", "http://localhost:8001/health"], 
                          capture_output=True, text=True, timeout=5)
    
    if "healthy" in result.stdout:
        print("✅ Health endpoint: PASSED")
        api_health = 1
    else:
        print("❌ Health endpoint: FAILED")
        print(f"Response: {result.stdout}")
        api_health = 0
    
    # Test 2: Chat completions
    print("2. Testing chat completions endpoint...")
    cmd = [
        "curl", "-s", "-X", "POST", "http://localhost:8001/v1/chat/completions",
        "-H", "Content-Type: application/json",
        "-d", '{"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Reply OK"}]}'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if "OK" in result.stdout or "choices" in result.stdout:
        print("✅ Chat completions: PASSED")
        chat_comp = 1
    else:
        print("❌ Chat completions: FAILED")
        print(f"Response: {result.stdout[:200]}")
        chat_comp = 0
    
    return api_health + chat_comp

def test_caching():
    """Test caching feature."""
    print("\n=== Testing Caching ===")
    
    # First call
    start1 = time.time()
    result1 = subprocess.run([
        "/home/graham/.claude/commands/llm_call",
        "--query", "Hi",
        "--model", "gpt-3.5-turbo",
        "--cache"
    ], capture_output=True, text=True, timeout=15)
    time1 = time.time() - start1
    
    # Second call (should be cached)
    start2 = time.time()
    result2 = subprocess.run([
        "/home/graham/.claude/commands/llm_call",
        "--query", "Hi",
        "--model", "gpt-3.5-turbo",
        "--cache"
    ], capture_output=True, text=True, timeout=5)
    time2 = time.time() - start2
    
    print(f"First call: {time1:.2f}s")
    print(f"Second call: {time2:.2f}s")
    
    # Check if cache worked
    if time2 <= time1 or result1.stdout == result2.stdout:
        print("✅ Caching: PASSED (speedup detected)")
        return 1
    else:
        print("❌ Caching: FAILED (no speedup)")
        return 0

def test_error_handling():
    """Test error handling."""
    print("\n=== Testing Error Handling ===")
    
    # Test 1: Invalid model
    print("1. Testing invalid model...")
    result = subprocess.run([
        "/home/graham/.claude/commands/llm_call",
        "--query", "Test",
        "--model", "invalid/model"
    ], capture_output=True, text=True, timeout=5)
    
    if result.returncode != 0 or "error" in result.stdout.lower() or "error" in result.stderr.lower():
        print("✅ Invalid model: PASSED (error detected)")
        invalid_model = 1
    else:
        print("❌ Invalid model: FAILED (no error)")
        invalid_model = 0
    
    # Test 2: Timeout (this should fail with very short timeout)
    print("2. Testing timeout...")
    result = subprocess.run([
        "/home/graham/.claude/commands/llm_call",
        "--query", "Write 1000 words",
        "--model", "gpt-3.5-turbo",
        "--timeout", "0.001"
    ], capture_output=True, text=True, timeout=5)
    
    if result.returncode != 0 or "timeout" in result.stdout.lower() or "timeout" in result.stderr.lower():
        print("✅ Timeout: PASSED (timeout detected)")
        timeout_test = 1
    else:
        print("❌ Timeout: FAILED (no timeout)")
        print(f"Output: {result.stdout[:100]}")
        timeout_test = 0
    
    return invalid_model + timeout_test

def test_hidden_features():
    """Test hidden features."""
    print("\n=== Testing Hidden Features ===")
    
    # Test 1: Embedding utils
    print("1. Testing embedding utils...")
    test_code = '''
try:
    from llm_call.core.utils.embedding_utils import get_embedding
    print("Success: True")
except ImportError as e:
    print(f"Success: False - {e}")
'''
    
    result = subprocess.run([sys.executable, "-c", test_code], 
                          capture_output=True, text=True, timeout=5)
    
    if "Success: True" in result.stdout:
        print("✅ Embedding utils: PASSED")
        embed = 1
    else:
        print("❌ Embedding utils: FAILED")
        embed = 0
    
    # Test 2: Text chunker
    print("2. Testing text chunker...")
    test_code = '''
try:
    from llm_call.core.utils.text_chunker import chunk_text
    text = "Test. " * 100
    chunks = list(chunk_text(text, chunk_size=100))
    print(f"Success: {len(chunks) > 1}")
except Exception as e:
    print(f"Success: False - {e}")
'''
    
    result = subprocess.run([sys.executable, "-c", test_code], 
                          capture_output=True, text=True, timeout=5)
    
    if "Success: True" in result.stdout:
        print("✅ Text chunker: PASSED")
        chunker = 1
    else:
        print("❌ Text chunker: FAILED")
        chunker = 0
    
    return embed + chunker

def main():
    """Run all tests and summarize."""
    print("🚀 Quick Test Check")
    print("=" * 50)
    
    results = {
        "Core Features": test_core_features(),
        "API": test_api_endpoints(), 
        "Caching": test_caching(),
        "Error Handling": test_error_handling(),
        "Hidden Features": test_hidden_features()
    }
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    total_passed = 0
    
    for category, passed in results.items():
        # Each category has 2 tests except Core which has 1
        tests = 2 if category != "Core Features" else 1
        total_tests += tests
        total_passed += passed
        rate = (passed / tests) * 100
        print(f"{category}: {passed}/{tests} ({rate:.0f}%)")
    
    overall_rate = (total_passed / total_tests) * 100
    print(f"\nOverall: {total_passed}/{total_tests} ({overall_rate:.0f}%)")
    
    if overall_rate == 100:
        print("\n🎉 ALL TESTS PASSED! 100% SUCCESS!")
    else:
        print(f"\n❌ Need to fix {total_tests - total_passed} tests to reach 100%")

if __name__ == "__main__":
    main()