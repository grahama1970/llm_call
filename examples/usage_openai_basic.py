#!/usr/bin/env python3
"""
Module: usage_openai_basic.py
Description: Usage function to verify basic OpenAI functionality for llm_call

External Dependencies:
- openai: https://platform.openai.com/docs/api-reference
- llm_call: Local package

Sample Input:
>>> result = test_openai_basic_math()
>>> print(result)
{"passed": True, "response": "4", "model": "gpt-3.5-turbo"}

Expected Output:
The response should contain "4" when asked "What is 2+2?"

Example Usage:
>>> python usage_openai_basic.py
>>> echo $?  # Should be 0 on success, 1 on failure
"""

import sys
import os
import json
from datetime import datetime

# Add src to path if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from llm_call import make_llm_request
except ImportError as e:
    print(f"❌ FAIL: Cannot import llm_call: {e}")
    print("Make sure PYTHONPATH=./src is set and llm_call is installed")
    sys.exit(1)


def test_openai_basic_math():
    """Test basic OpenAI math calculation (Test ID: F1.1)"""
    print("\n" + "="*60)
    print("TEST F1.1: Basic OpenAI Math (2+2)")
    print("="*60)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ FAIL: OPENAI_API_KEY not set")
        return False
    
    try:
        # Make the actual request
        print(f"Calling OpenAI API with model: gpt-3.5-turbo")
        print(f"Prompt: 'What is 2+2?'")
        print("-"*40)
        
        response = make_llm_request(
            prompt="What is 2+2?",
            model="gpt-3.5-turbo",
            temperature=0.1  # Low temp for consistent results
        )
        
        # Print raw response for debugging
        print(f"Raw response type: {type(response)}")
        print(f"Raw response: {response}")
        print("-"*40)
        
        # Extract content based on response type
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, dict) and 'content' in response:
            content = response['content']
        elif isinstance(response, dict) and 'choices' in response:
            # OpenAI format
            content = response['choices'][0]['message']['content']
        else:
            content = str(response)
        
        print(f"Extracted content: {content}")
        print("-"*40)
        
        # Verify the response contains "4"
        if "4" in str(content):
            print("✅ PASS: Response contains '4'")
            print(f"Full response: {content}")
            return True
        else:
            print(f"❌ FAIL: Expected '4' in response, got: {content}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during API call: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_openai_creative_writing():
    """Test OpenAI creative writing (Test ID: F1.2)"""
    print("\n" + "="*60)
    print("TEST F1.2: OpenAI Creative Writing") 
    print("="*60)
    
    try:
        print(f"Calling OpenAI API with model: gpt-4")
        print(f"Prompt: 'Write a haiku about Python programming'")
        print("-"*40)
        
        response = make_llm_request(
            prompt="Write a haiku about Python programming",
            model="gpt-4",
            temperature=0.7
        )
        
        # Extract content
        if hasattr(response, 'content'):
            content = response.content
        elif isinstance(response, dict) and 'content' in response:
            content = response['content']
        elif isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
        else:
            content = str(response)
        
        print(f"Response: {content}")
        print("-"*40)
        
        # Basic haiku validation (3 lines, mentions Python)
        lines = content.strip().split('\n')
        has_python = "python" in content.lower() or "code" in content.lower()
        
        if len(lines) >= 3 and has_python:
            print(f"✅ PASS: Valid haiku with {len(lines)} lines")
            return True
        else:
            print(f"❌ FAIL: Invalid haiku - Lines: {len(lines)}, Has Python ref: {has_python}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception during API call: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    """Run all tests and report results"""
    print(f"\nLLM Call Usage Tests - OpenAI Provider")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: OPENAI_API_KEY={'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET'}")
    
    # Track results
    results = []
    
    # Run tests
    tests = [
        ("F1.1", "Basic Math", test_openai_basic_math),
        ("F1.2", "Creative Writing", test_openai_creative_writing)
    ]
    
    for test_id, test_name, test_func in tests:
        try:
            passed = test_func()
            results.append({
                "id": test_id,
                "name": test_name,
                "passed": passed
            })
        except Exception as e:
            print(f"\n❌ CRITICAL FAIL in {test_id}: {e}")
            results.append({
                "id": test_id,
                "name": test_name,
                "passed": False
            })
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{result['id']}: {result['name']} - {status}")
    
    print("-"*60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Exit with appropriate code
    exit_code = 0 if passed == total else 1
    print(f"\nExiting with code: {exit_code}")
    sys.exit(exit_code)