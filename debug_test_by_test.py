#!/usr/bin/env python3
"""Debug v4 tests one by one with detailed output."""

import asyncio
import json
import sys
import os
import time
from pathlib import Path

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

# Configure logger for detailed output
logger.remove()
logger.add(sys.stdout, level="DEBUG", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def debug_test(test_case):
    """Run a single test with detailed debugging."""
    test_id = test_case['test_case_id']
    print(f"\n{'='*80}")
    print(f"DEBUGGING TEST: {test_id}")
    print(f"Description: {test_case['description']}")
    print(f"{'='*80}\n")
    
    # Extract the llm_config
    llm_config = test_case['llm_config'].copy()
    
    # Add validation strategies if specified
    if 'validation_strategies' in test_case:
        llm_config['validation'] = test_case['validation_strategies']
    
    # Add retry config if specified
    if 'retry_config' in test_case:
        llm_config['retry_config'] = test_case['retry_config']
    
    print(f"LLM Config: {json.dumps(llm_config, indent=2)}")
    print(f"\nExpected behavior: {test_case.get('expected_behavior', 'Not specified')}")
    print("\n" + "-"*80 + "\n")
    
    try:
        # Run the LLM call
        start_time = time.time()
        response = await llm_call(llm_config)
        elapsed = time.time() - start_time
        
        print(f"\nElapsed time: {elapsed:.1f}s")
        
        if response:
            if isinstance(response, dict):
                if "error" in response:
                    print(f"\n❌ ERROR RESPONSE:")
                    print(json.dumps(response, indent=2))
                    return False
                elif "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    print(f"\n✅ SUCCESS - Got response from proxy:")
                    print(f"Content: {content}")
                    return True
                else:
                    print(f"\n⚠️  Unexpected response format:")
                    print(json.dumps(response, indent=2))
                    return False
            else:
                # LiteLLM ModelResponse
                if hasattr(response, 'choices'):
                    content = response.choices[0].message.content
                    print(f"\n✅ SUCCESS - Got response from LiteLLM:")
                    print(f"Content: {content}")
                    return True
                else:
                    print(f"\n❌ Unexpected response type: {type(response)}")
                    print(f"Response: {response}")
                    return False
        else:
            print("\n❌ No response received")
            return False
            
    except Exception as e:
        print(f"\n❌ EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run specific tests for debugging."""
    # Load test cases
    test_file = Path("src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json")
    with open(test_file, 'r') as f:
        test_cases = json.load(f)
    
    # Check if proxy is running
    print("Checking if proxy server is running...")
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3010/health", timeout=2.0)
            if response.status_code == 200:
                print("✅ Proxy server is running\n")
            else:
                print("⚠️  Proxy server returned non-200 status\n")
    except:
        print("❌ Proxy server is not running! Start it with:")
        print("   python src/llm_call/proof_of_concept/poc_claude_proxy_server.py\n")
        return
    
    # Test specific test cases
    # Start with the ones that were failing
    test_ids_to_debug = [
        "max_code_001_simple_code",  # This one has agent_task validation
        "max_mcp_001_file_operations",  # This one uses MCP
        "max_json_001_structured_output",  # This one needs JSON validation
    ]
    
    for test_case in test_cases:
        if test_case['test_case_id'] in test_ids_to_debug:
            await debug_test(test_case)
            await asyncio.sleep(2)  # Delay between tests

if __name__ == "__main__":
    asyncio.run(main())