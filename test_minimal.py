#!/usr/bin/env python3
"""Minimal test to debug timeout issues."""

import asyncio
import httpx
import time

async def test_proxy_direct():
    """Test proxy directly."""
    print("Testing proxy directly...")
    
    url = "http://localhost:3010/v1/chat/completions"
    payload = {
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "Say hi"}],
        "temperature": 0.1,
        "max_tokens": 10
    }
    
    start = time.time()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            elapsed = time.time() - start
            print(f"Response in {elapsed:.1f}s: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                print(f"Content: {content}")
                return True
        except Exception as e:
            print(f"Error: {e}")
    return False

async def test_health():
    """Test health endpoint."""
    print("\nTesting health endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:3010/health", timeout=2.0)
            print(f"Health status: {response.status_code}")
            print(f"Health data: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check error: {e}")
    return False

async def main():
    health_ok = await test_health()
    if health_ok:
        proxy_ok = await test_proxy_direct()
        if proxy_ok:
            print("\n✅ Proxy is working correctly")
        else:
            print("\n❌ Proxy call failed")
    else:
        print("\n❌ Health check failed")

if __name__ == "__main__":
    asyncio.run(main())