#!/usr/bin/env python3
"""Test Claude proxy directly."""

import requests
import json

print("Testing Claude proxy directly at http://localhost:3010...")

# Test the max/opus model
payload = {
    "model": "max/claude-3-opus-20240229",
    "messages": [
        {"role": "user", "content": "Say exactly: Hello World!"}
    ],
    "temperature": 0.1,
    "max_tokens": 100
}

try:
    response = requests.post(
        "http://localhost:3010/v1/chat/completions",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        if 'choices' in data and data['choices']:
            content = data['choices'][0]['message']['content']
            print(f"\n✅ Success! Response: '{content}'")
        else:
            print(f"\n❌ Unexpected response format: {data}")
    else:
        print(f"\n❌ Error response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")
    import traceback
    traceback.print_exc()