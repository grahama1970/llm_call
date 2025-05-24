#!/usr/bin/env python3
"""Test direct call without polling"""

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

async def test_direct_call():
    """Test a simple direct call to the model"""
    
    try:
        logger.info("Making direct LiteLLM call...")
        
        response = await litellm.acompletion(
            model="max/text-general",
            messages=[{
                "role": "user",
                "content": "What is the primary function of a CPU in a computer?"
            }],
            api_base="http://localhost:3010"
        )
        
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Has choices: {hasattr(response, 'choices')}")
        
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            logger.info(f"Content preview: {content[:200]}...")
            logger.info("✅ Direct call successful!")
        else:
            logger.error("No choices in response")
            
    except Exception as e:
        logger.error(f"Direct call failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")

async def main():
    await test_direct_call()

if __name__ == "__main__":
    asyncio.run(main())
