#!/usr/bin/env python3
"""
Fix Vertex AI thinking tokens issue.

The problem: Gemini 2.5 Flash is using all tokens for "thinking" and not outputting text.
Solution: Increase max_tokens significantly to allow for both thinking and output.
"""

import asyncio
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import litellm
from litellm import acompletion
from loguru import logger

# Enable debug logging
litellm.set_verbose = True

async def test_with_proper_tokens():
    """Test Vertex AI with enough tokens for both thinking and output."""
    
    # Ensure we're using the service account
    service_account_path = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
    
    test_cases = [
        {
            "prompt": "What is 2+2?",
            "max_tokens": 10,  # Very low, should fail
            "expected": "fail"
        },
        {
            "prompt": "What is 2+2?",
            "max_tokens": 200,  # Should be enough for thinking + output
            "expected": "success"
        },
        {
            "prompt": "Answer in one word: What is 2+2?",
            "max_tokens": 150,  # Simple prompt, less thinking needed
            "expected": "success"
        },
        {
            "prompt": "2+2=",
            "max_tokens": 100,  # Very simple, minimal thinking
            "expected": "success"
        }
    ]
    
    for i, test in enumerate(test_cases):
        logger.info(f"\nTest {i+1}: {test['prompt']} (max_tokens={test['max_tokens']})")
        
        try:
            response = await acompletion(
                model="vertex_ai/gemini-2.5-flash-preview-05-20",
                messages=[{"role": "user", "content": test["prompt"]}],
                temperature=0,
                max_tokens=test["max_tokens"]
            )
            
            content = response.choices[0].message.content
            if content is None:
                logger.error(f"❌ NULL content (expected: {test['expected']})")
                if hasattr(response, 'usage'):
                    usage = response.usage
                    logger.info(f"   Thinking tokens: {getattr(usage.completion_tokens_details, 'reasoning_tokens', 'N/A')}")
                    logger.info(f"   Text tokens: {getattr(usage.completion_tokens_details, 'text_tokens', 'N/A')}")
                    logger.info(f"   Total completion: {usage.completion_tokens}")
            else:
                logger.success(f"✅ Got content: {repr(content)} (expected: {test['expected']})")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")

async def test_api_with_fix():
    """Test through API with the fix."""
    import httpx
    
    logger.info("\n" + "="*60)
    logger.info("Testing API with increased max_tokens...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test with low tokens (should fail)
            response1 = await client.post(
                "http://localhost:8001/v1/chat/completions",
                json={
                    "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
                    "messages": [{"role": "user", "content": "What is the capital of France?"}],
                    "temperature": 0,
                    "max_tokens": 50  # Too low for thinking + output
                },
                timeout=30.0
            )
            
            if response1.status_code == 200:
                data1 = response1.json()
                content1 = data1["choices"][0]["message"]["content"]
                logger.info(f"Low tokens (50): content = {repr(content1)}")
                
            # Test with high tokens (should work)
            response2 = await client.post(
                "http://localhost:8001/v1/chat/completions",
                json={
                    "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
                    "messages": [{"role": "user", "content": "What is the capital of France?"}],
                    "temperature": 0,
                    "max_tokens": 300  # Enough for thinking + output
                },
                timeout=30.0
            )
            
            if response2.status_code == 200:
                data2 = response2.json()
                content2 = data2["choices"][0]["message"]["content"]
                if content2:
                    logger.success(f"✅ High tokens (300): content = {repr(content2)}")
                else:
                    logger.error(f"❌ Still null with 300 tokens!")
                    
    except Exception as e:
        logger.error(f"API test error: {e}")

async def main():
    """Run all tests."""
    await test_with_proper_tokens()
    await test_api_with_fix()
    
    logger.info("\n" + "="*60)
    logger.info("SOLUTION: Vertex AI Gemini 2.5 Flash uses 'thinking tokens'")
    logger.info("You MUST set max_tokens high enough for BOTH thinking AND output")
    logger.info("Recommended: max_tokens >= 200 for simple prompts, >= 500 for complex")

if __name__ == "__main__":
    asyncio.run(main())