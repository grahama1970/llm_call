#!/usr/bin/env python3
"""
Test Gemini WITHOUT max_tokens parameter.
"""
import httpx

print("Testing Gemini WITHOUT max_tokens...")

# Test 1: Simple query without max_tokens
response = httpx.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
        "messages": [{"role": "user", "content": "What is the capital of France? Give a detailed answer."}],
        "temperature": 0.1
        # NO max_tokens!
    },
    timeout=30.0
)

if response.status_code == 200:
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    
    print(f"\nContent is null: {content is None}")
    print(f"Content length: {len(content) if content else 0}")
    
    if content:
        print(f"\nActual content:")
        print(content)
    
    print(f"\nToken usage:")
    print(f"  Total: {usage.get('total_tokens')}")
    print(f"  Completion: {usage.get('completion_tokens')}")
    
    details = usage.get('completion_tokens_details', {})
    print(f"  Reasoning tokens: {details.get('reasoning_tokens', 0)}")
    print(f"  Text tokens: {details.get('text_tokens', 0)}")
else:
    print(f"Error: {response.status_code}")