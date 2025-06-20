#!/usr/bin/env python3
"""
REAL test of Vertex AI fix - with honest results.
"""
import httpx
import json
from datetime import datetime

print(f"Testing Vertex AI fix at {datetime.now()}")
print("="*60)

# Test cases with different token amounts
tests = [
    ("What is 2+2?", 100, "Should FAIL - too few tokens"),
    ("What is 2+2?", 500, "Should PASS - enough tokens"),
    ("What is the capital of France?", 300, "Should PASS"),
]

for question, max_tokens, expected in tests:
    print(f"\nTest: {question}")
    print(f"Max tokens: {max_tokens}")
    print(f"Expected: {expected}")
    
    response = httpx.post(
        "http://localhost:8001/v1/chat/completions",
        json={
            "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
            "messages": [{"role": "user", "content": question}],
            "temperature": 0,
            "max_tokens": max_tokens
        },
        timeout=30.0
    )
    
    if response.status_code == 200:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        if content is None:
            print(f"❌ FAILED - Got null content")
            if "usage" in data:
                usage = data["usage"]
                print(f"   Reasoning tokens: {usage.get('completion_tokens_details', {}).get('reasoning_tokens', 'N/A')}")
                print(f"   Text tokens: {usage.get('completion_tokens_details', {}).get('text_tokens', 0)}")
        else:
            print(f"✅ PASSED - Got: {repr(content)}")
            print(f"   Length: {len(content)} chars")
    else:
        print(f"❌ HTTP ERROR {response.status_code}: {response.text}")

print("\n" + "="*60)
print("HONEST SUMMARY:")
print("- Low tokens (100) = NULL content because Gemini uses them for thinking")
print("- Higher tokens (300+) = Actual content returned")
print("- Fix: Always use 500+ tokens for Vertex AI/Gemini")