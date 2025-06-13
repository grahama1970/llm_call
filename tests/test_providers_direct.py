#!/usr/bin/env python3
"""
Test LLM providers directly without llm_call wrapper.
This helps identify if the issue is with llm_call or the providers.
"""

import os
import time
import asyncio
from datetime import datetime

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def test_litellm_directly():
    """Test litellm directly."""
    print("=== Testing LiteLLM Directly ===")
    
    try:
        import litellm
        litellm.set_verbose = False  # Reduce noise
        
        # Get API key
        api_key = os.environ.get("OPENAI_API_KEY")
        print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
        
        # Make direct call
        start = time.time()
        response = await litellm.acompletion(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello from LiteLLM'"}],
            api_key=api_key,
            max_tokens=20
        )
        duration = time.time() - start
        
        # Extract response
        content = response.choices[0].message.content
        print(f"✅ Success: {content}")
        print(f"Duration: {duration:.3f}s")
        print(f"Model: {response.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
        
        # Try to understand the error
        if "401" in str(e):
            print("\n💡 API key issue. Let's verify the key...")
            print(f"Key format: {'Valid' if api_key and api_key.startswith('sk-') else 'Invalid'}")
            print(f"Key length: {len(api_key) if api_key else 0}")
        
        return False


async def test_openai_sdk_directly():
    """Test OpenAI SDK directly."""
    print("\n=== Testing OpenAI SDK Directly ===")
    
    try:
        from openai import AsyncOpenAI
        
        # Get API key
        api_key = os.environ.get("OPENAI_API_KEY")
        
        # Create client
        client = AsyncOpenAI(api_key=api_key)
        
        # Make direct call
        start = time.time()
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello from OpenAI SDK'"}],
            max_tokens=20
        )
        duration = time.time() - start
        
        # Extract response
        content = response.choices[0].message.content
        print(f"✅ Success: {content}")
        print(f"Duration: {duration:.3f}s")
        print(f"Response ID: {response.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
        return False


async def test_gemini_directly():
    """Test Gemini directly."""
    print("\n=== Testing Gemini Directly ===")
    
    try:
        import google.generativeai as genai
        
        # Configure
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            print("❌ No GOOGLE_API_KEY found")
            return False
            
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Make call
        start = time.time()
        response = model.generate_content("Say 'Hello from Gemini'")
        duration = time.time() - start
        
        print(f"✅ Success: {response.text}")
        print(f"Duration: {duration:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
        return False


async def test_vertex_ai_directly():
    """Test Vertex AI directly through litellm."""
    print("\n=== Testing Vertex AI Directly ===")
    
    try:
        import litellm
        
        # Check credentials
        creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not creds_path or not os.path.exists(creds_path):
            print("❌ No GOOGLE_APPLICATION_CREDENTIALS found or file doesn't exist")
            return False
        
        print(f"Credentials: {creds_path}")
        
        # Make call
        start = time.time()
        response = await litellm.acompletion(
            model="vertex_ai/gemini-1.5-flash",
            messages=[{"role": "user", "content": "Say 'Hello from Vertex AI'"}],
            vertex_project=os.environ.get("LITELLM_VERTEX_PROJECT"),
            vertex_location=os.environ.get("LITELLM_VERTEX_LOCATION")
        )
        duration = time.time() - start
        
        content = response.choices[0].message.content
        print(f"✅ Success: {content}")
        print(f"Duration: {duration:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {e}")
        return False


async def main():
    """Test all providers directly."""
    print("DIRECT PROVIDER TESTING")
    print("="*50)
    print(f"Time: {datetime.now().isoformat()}")
    
    results = []
    
    # Test each provider
    results.append(("LiteLLM", await test_litellm_directly()))
    results.append(("OpenAI SDK", await test_openai_sdk_directly()))
    results.append(("Gemini", await test_gemini_directly()))
    results.append(("Vertex AI", await test_vertex_ai_directly()))
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY:")
    working = 0
    for provider, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {provider}")
        if success:
            working += 1
    
    print(f"\nTotal: {working}/{len(results)} providers working")
    
    if working == 0:
        print("\n⚠️  No providers working! Check:")
        print("1. API keys in .env")
        print("2. Internet connection")
        print("3. Provider status pages")
    elif working < len(results):
        print("\n💡 Some providers working. The issue might be with llm_call integration.")
    else:
        print("\n✅ All providers working! The issue is likely in llm_call code.")
    
    return working > 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)