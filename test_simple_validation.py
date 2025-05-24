#!/usr/bin/env python3
"""Test simple validation flow."""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

# More verbose logging
logger.remove()
logger.add(sys.stdout, level="DEBUG", format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_with_retry():
    """Test with retry and debug output."""
    config = {
        "model": "max/text-general",
        "messages": [
            {
                "role": "user",
                "content": "Generate exactly 3 words."
            }
        ],
        "validation": [
            {
                "type": "response_not_empty"
            }
        ],
        "retry_config": {
            "max_attempts": 2,
            "debug_mode": True
        }
    }
    
    logger.info("Testing simple validation with retry...")
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict) and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                logger.success(f"✅ Got response: {content}")
            else:
                logger.info(f"Response: {response}")
        else:
            logger.error("No response")
            
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_with_retry())