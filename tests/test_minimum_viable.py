"""
Module: test_minimum_viable.py
Description: Absolute minimum test - one real API call

This is Phase 1 of progressive testing. Makes exactly ONE real API call
to prove basic connectivity works.

External Dependencies:
- openai: https://platform.openai.com/docs/

Sample Input:
>>> python test_minimum_viable.py

Expected Output:
>>> ✅ SUCCESS: Hello
>>> Duration: 0.XXXs
>>> Response ID: chatcmpl-XXXX

Example Usage:
>>> python tests/test_minimum_viable.py
"""

import os
import time
import asyncio
from datetime import datetime


async def test_one_openai_call():
    """Make exactly ONE real API call - the absolute minimum."""
    print("=== Minimum Viable Test: One OpenAI Call ===")
    print(f"Time: {datetime.now().isoformat()}")
    
    evidence = {
        "test_start": datetime.now().isoformat(),
        "duration": None,
        "success": False
    }
    
    start = time.time()
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("❌ No OPENAI_API_KEY found in environment")
            return evidence
        
        print(f"Using API key: {api_key[:4]}...{api_key[-4:]}")
        
        # Import ONLY what we need
        from openai import AsyncOpenAI
        
        # Create client with explicit API key
        client = AsyncOpenAI(api_key=api_key)
        
        # Make the simplest possible call
        print("\nMaking API call...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello' and nothing else"}],
            max_tokens=10,
            temperature=0
        )
        
        # Collect evidence
        evidence["response_id"] = response.id
        evidence["content"] = response.choices[0].message.content
        evidence["model"] = response.model
        evidence["duration"] = time.time() - start
        evidence["success"] = True
        
        print(f"\n✅ SUCCESS: {evidence['content']}")
        print(f"Duration: {evidence['duration']:.3f}s")
        print(f"Response ID: {evidence['response_id']}")
        print(f"Model: {evidence['model']}")
        
        # Verify it was a real API call
        if evidence["duration"] < 0.05:
            print(f"\n⚠️  WARNING: Response too fast ({evidence['duration']:.3f}s) - might not be real API")
        
    except Exception as e:
        evidence["error"] = str(e)
        evidence["error_type"] = type(e).__name__
        evidence["duration"] = time.time() - start
        print(f"\n❌ FAILED: {type(e).__name__}: {e}")
        
        # Provide helpful debugging
        if "401" in str(e):
            print("\n💡 API key is invalid. Check your OPENAI_API_KEY in .env")
        elif "connection" in str(e).lower():
            print("\n💡 Connection error. Check your internet connection")
        elif "module" in str(e).lower():
            print("\n💡 Import error. Run: pip install openai")
    
    print(f"\nTotal time: {time.time() - start:.3f}s")
    return evidence


def main():
    """Run the minimum viable test."""
    # Run async function
    result = asyncio.run(test_one_openai_call())
    
    # Summary
    print("\n" + "="*50)
    if result["success"]:
        print("✅ Minimum viable test PASSED!")
        print("\nWhat this proves:")
        print("- Environment is set up correctly")
        print("- API key is valid")
        print("- Network connectivity works")
        print("- OpenAI client works")
        print("\nNext step: Run test_core_functionality.py")
    else:
        print("❌ Minimum viable test FAILED!")
        print("\nDebug information:")
        for key, value in result.items():
            if value is not None:
                print(f"  {key}: {value}")
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)