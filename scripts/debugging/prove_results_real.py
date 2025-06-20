#!/usr/bin/env python3
"""
Prove these results are REAL by showing full API responses.
"""
import httpx
import json
from datetime import datetime

print(f"PROOF OF REAL API CALLS - {datetime.now()}")
print("="*70)

# Make a simple call and show FULL response
response = httpx.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "What is the capital of France?"}],
        "temperature": 0,
        "max_tokens": 50
    },
    timeout=30.0
)

print(f"\nHTTP Status: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print("\nFULL JSON RESPONSE:")
print(json.dumps(response.json(), indent=2))

# Save to file for verification
with open("proof_of_real_api_response.json", "w") as f:
    json.dump(response.json(), f, indent=2)
    
print("\nResponse saved to proof_of_real_api_response.json")

# Test another provider
print("\n" + "="*70)
print("Testing Vertex AI:")

response2 = httpx.post(
    "http://localhost:8001/v1/chat/completions",
    json={
        "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
        "messages": [{"role": "user", "content": "Say 'Hello World'"}],
        "max_tokens": 50
    }
)

print(f"HTTP Status: {response2.status_code}")
if response2.status_code == 200:
    data = response2.json()
    content = data["choices"][0]["message"]["content"]
    print(f"Vertex AI response: {repr(content)}")
    print(f"Response is None: {content is None}")
    print(f"Response length: {len(content) if content else 0}")