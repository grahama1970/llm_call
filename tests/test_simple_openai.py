#!/usr/bin/env python3
"""
Super simple OpenAI test without any complex imports.
Tests if we can make a real API call.
"""

import os
import json
import time
import urllib.request
import urllib.error

def test_openai_directly():
    """Test OpenAI API with urllib only - no dependencies."""
    print("=== Direct OpenAI API Test ===")
    
    # Load API key from .env manually
    api_key = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ No OPENAI_API_KEY found in .env")
        return False
    
    print(f"API Key: {api_key[:4]}...{api_key[-4:]}")
    
    # Prepare request
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'Hello' and nothing else"}],
        "max_tokens": 10,
        "temperature": 0
    }
    
    # Make request
    start = time.time()
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers
        )
        
        print("\nMaking API call...")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        duration = time.time() - start
        
        # Extract response
        content = result['choices'][0]['message']['content']
        response_id = result['id']
        model = result['model']
        
        print(f"\n✅ SUCCESS!")
        print(f"Response: {content}")
        print(f"Duration: {duration:.3f}s")
        print(f"Response ID: {response_id}")
        print(f"Model: {model}")
        
        if duration > 0.05:
            print(f"\n✅ Confirmed real API call (duration > 50ms)")
        
        return True
        
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        if e.code == 401:
            print("💡 Invalid API key")
        return False
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_directly()
    print("\n" + "="*50)
    if success:
        print("✅ OpenAI API is working!")
        print("\nThis proves:")
        print("- API key is valid")
        print("- Network connectivity works") 
        print("- OpenAI service is accessible")
    else:
        print("❌ OpenAI API test failed")
        print("\nTroubleshooting:")
        print("1. Check your OPENAI_API_KEY in .env")
        print("2. Ensure key starts with 'sk-'")
        print("3. Check internet connection")
    
    exit(0 if success else 1)