#!/usr/bin/env python3
"""Test proxy directly with httpx."""

import asyncio
import httpx
import json

async def test_proxy():
    """Test the proxy directly."""
    url = "http://localhost:3010/v1/chat/completions"
    
    payload = {
        "model": "max/text-general",
        "messages": [
            {
                "role": "user",
                "content": "Say hello in 5 words or less."
            }
        ],
        "temperature": 0.1,
        "max_tokens": 50
    }
    
    print(f"Sending request to proxy...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            print(f"\nStatus: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                if data.get("choices"):
                    content = data["choices"][0]["message"]["content"]
                    print(f"\nContent: {content}")
            else:
                print(f"Error: {response.text}")
                
        except httpx.TimeoutException:
            print("Request timed out!")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_proxy())