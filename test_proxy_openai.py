#!/usr/bin/env python3
"""Test proxy with OpenAI format"""

import asyncio
import litellm
from loguru import logger

# Configure logging
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)

async def test_proxy_call():
    """Test call to proxy as OpenAI endpoint"""
    
    try:
        logger.info("Making proxy call as OpenAI endpoint...")
        
        response = await litellm.acompletion(
            model="openai/max/text-general",
            messages=[{
                "role": "user",
                "content": "What is the primary function of a CPU in a computer?"
            }],
            api_base="http://localhost:3010",
            api_key="dummy"  # Proxy doesn't need real key
        )
        
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Has choices: {hasattr(response, 'choices')}")
        
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            logger.info(f"Content length: {len(content)} chars")
            logger.info(f"Content preview: {content[:200]}...")
            logger.info("✅ Proxy call successful!")
            return True
        else:
            logger.error("No choices in response")
            return False
            
    except Exception as e:
        logger.error(f"Proxy call failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return False

async def main():
    success = await test_proxy_call()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
