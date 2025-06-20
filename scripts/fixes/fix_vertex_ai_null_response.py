#!/usr/bin/env python3
"""
Fix Vertex AI null response issue.

This script will:
1. Test the current Vertex AI implementation
2. Show exactly what's happening with the response
3. Implement a fix if the response is being incorrectly parsed
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

async def test_vertex_ai_direct():
    """Test Vertex AI directly through LiteLLM."""
    
    # Ensure we're using the service account
    service_account_path = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"
    if not Path(service_account_path).exists():
        logger.error(f"Service account file not found: {service_account_path}")
        return
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
    
    # Simple test message
    messages = [{"role": "user", "content": "What is 2+2? Reply in exactly 5 words."}]
    
    logger.info("Testing Vertex AI with direct LiteLLM call...")
    logger.info(f"Model: vertex_ai/gemini-2.5-flash-preview-05-20")
    logger.info(f"Service account: {service_account_path}")
    
    try:
        # Make the call
        response = await acompletion(
            model="vertex_ai/gemini-2.5-flash-preview-05-20",
            messages=messages,
            temperature=0.1,
            max_tokens=100
        )
        
        logger.info("Raw response type: " + str(type(response)))
        logger.info("Raw response: " + str(response))
        
        # Check if response has content
        if hasattr(response, 'choices') and response.choices:
            choice = response.choices[0]
            logger.info(f"Choice type: {type(choice)}")
            logger.info(f"Choice: {choice}")
            
            if hasattr(choice, 'message'):
                message = choice.message
                logger.info(f"Message type: {type(message)}")
                logger.info(f"Message: {message}")
                
                if hasattr(message, 'content'):
                    content = message.content
                    logger.info(f"Content type: {type(content)}")
                    logger.info(f"Content value: {repr(content)}")
                    
                    if content is None:
                        logger.error("❌ CONTENT IS NULL - This is the bug!")
                        
                        # Try to access raw response data
                        if hasattr(response, '_raw_response'):
                            logger.info("Raw response data: " + str(response._raw_response))
                        
                        # Try to get the actual text from the response
                        if hasattr(choice, 'text'):
                            logger.info(f"Choice.text: {choice.text}")
                        
                        # Check model_response attributes
                        logger.info("All response attributes:")
                        for attr in dir(response):
                            if not attr.startswith('_'):
                                try:
                                    value = getattr(response, attr)
                                    if not callable(value):
                                        logger.info(f"  {attr}: {repr(value)}")
                                except:
                                    pass
                    else:
                        logger.success(f"✅ Got content: {content}")
                        
        # Check usage
        if hasattr(response, 'usage'):
            logger.info(f"Token usage: {response.usage}")
            
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

async def test_through_api():
    """Test through our API to see the difference."""
    import httpx
    
    logger.info("\n" + "="*60)
    logger.info("Testing through llm_call API...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/v1/chat/completions",
                json={
                    "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
                    "messages": [{"role": "user", "content": "What is 2+2? Reply in exactly 5 words."}],
                    "temperature": 0.1,
                    "max_tokens": 100
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info("API Response: " + json.dumps(data, indent=2))
                
                if data["choices"][0]["message"]["content"] is None:
                    logger.error("❌ API also returns null content!")
                else:
                    logger.success(f"✅ API returns content: {data['choices'][0]['message']['content']}")
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                
    except Exception as e:
        logger.error(f"API test error: {e}")

async def main():
    """Run all tests."""
    await test_vertex_ai_direct()
    await test_through_api()

if __name__ == "__main__":
    asyncio.run(main())