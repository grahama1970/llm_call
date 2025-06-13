#!/usr/bin/env python3
"""
Module: test_hello_world_simple.py
Description: Simple Hello World test showing which LLM models are working

This test provides a quick overview of which models are configured and working.

External Dependencies:
- llm_call: Core LLM interface module

Sample Input:
>>> python test_hello_world_simple.py

Expected Output:
>>> ✅ vertex_ai/gemini-2.5-flash-preview-05-20: Hello World!
>>> ❌ gemini/gemini-1.5-pro: API key invalid
>>> ❌ gpt-3.5-turbo: No API key set

Example Usage:
>>> python test_hello_world_simple.py
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Any

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Import the real llm_call module
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from llm_call.core.caller import make_llm_request
except ImportError:
    # Try with package name using underscore
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
    from llm_call.core.caller import make_llm_request

async def test_model(model: str) -> Dict[str, Any]:
    """Test a single model with Hello World prompt."""
    result = {
        "model": model,
        "status": "unknown",
        "response": None,
        "error": None,
        "duration": 0
    }
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        response = await make_llm_request({
            "model": model,
            "messages": [
                {"role": "user", "content": "Say exactly: Hello World!"}
            ],
            "temperature": 0.1,
            "max_tokens": 100
        })
        
        duration = asyncio.get_event_loop().time() - start_time
        
        if response:
            # Extract content based on response type
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            elif isinstance(response, dict):
                content = response.get('content', response.get('response', ''))
            else:
                content = str(response)
            
            result["status"] = "success"
            result["response"] = content
            result["duration"] = duration
        else:
            result["status"] = "no_response"
            result["error"] = "No response received"
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        result["duration"] = asyncio.get_event_loop().time() - start_time
    
    return result

async def main():
    """Run Hello World tests for all models."""
    print(f"\n{BLUE}=== LLM Call Hello World Test ==={RESET}")
    print(f"Testing at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Models to test
    models = [
        # Vertex AI
        ("vertex_ai/gemini-2.5-flash-preview-05-20", "Vertex AI Gemini"),
        
        # Direct Gemini API
        ("gemini/gemini-1.5-pro", "Gemini Direct API"),
        
        # OpenAI
        ("gpt-3.5-turbo", "OpenAI GPT-3.5"),
        
        # Claude via proxy
        ("max/claude-3-opus-20240229", "Claude Opus (Proxy)"),
        
        # Claude direct
        ("claude-3-sonnet-20240229", "Claude Sonnet (Direct)"),
    ]
    
    # Check environment
    print(f"{YELLOW}Environment Check:{RESET}")
    env_vars = {
        "GOOGLE_APPLICATION_CREDENTIALS": "Vertex AI",
        "GEMINI_API_KEY": "Gemini Direct",
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic"
    }
    
    for var, service in env_vars.items():
        value = os.getenv(var)
        if value:
            if var.endswith("_KEY"):
                # Show partial key for security
                display = f"***{value[-8:]}" if len(value) > 8 else "***"
            else:
                display = "Set"
            print(f"  {service}: {GREEN}✓{RESET} ({var}={display})")
        else:
            print(f"  {service}: {RED}✗{RESET} ({var} not set)")
    
    # Check Claude proxy
    try:
        import requests
        resp = requests.get("http://localhost:3010/health", timeout=1)
        if resp.status_code == 200:
            print(f"  Claude Proxy: {GREEN}✓{RESET} (port 3010)")
        else:
            print(f"  Claude Proxy: {RED}✗{RESET} (not healthy)")
    except:
        print(f"  Claude Proxy: {RED}✗{RESET} (not running)")
    
    print(f"\n{YELLOW}Testing Models:{RESET}")
    
    # Test each model
    results = []
    for model_id, model_name in models:
        print(f"\n{model_name} ({model_id}):")
        result = await test_model(model_id)
        results.append(result)
        
        if result["status"] == "success":
            print(f"  Status: {GREEN}✅ Success{RESET}")
            print(f"  Response: '{result['response']}'")
            print(f"  Duration: {result['duration']:.2f}s")
        else:
            print(f"  Status: {RED}❌ {result['status'].replace('_', ' ').title()}{RESET}")
            if result["error"]:
                # Shorten error messages
                error_msg = result["error"]
                if len(error_msg) > 100:
                    error_msg = error_msg[:100] + "..."
                print(f"  Error: {error_msg}")
    
    # Summary
    print(f"\n{BLUE}=== Summary ==={RESET}")
    success_count = sum(1 for r in results if r["status"] == "success")
    total_count = len(results)
    
    print(f"Models tested: {total_count}")
    print(f"Successful: {GREEN}{success_count}{RESET}")
    print(f"Failed: {RED}{total_count - success_count}{RESET}")
    
    if success_count > 0:
        print(f"\n{GREEN}✅ LLM Call is working with {success_count} model(s)!{RESET}")
    else:
        print(f"\n{RED}❌ No models are currently working. Check your API credentials.{RESET}")
    
    # Working models list
    working_models = [r["model"] for r in results if r["status"] == "success"]
    if working_models:
        print(f"\nWorking models:")
        for model in working_models:
            print(f"  - {model}")

if __name__ == "__main__":
    # Run with proper event loop handling
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()