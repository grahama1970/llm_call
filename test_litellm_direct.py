#!/usr/bin/env python3
"""Test direct LiteLLM call."""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_litellm():
    """Test standard LiteLLM call."""
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "What is 2 + 2?"
            }
        ],
        "validation": [
            {
                "type": "response_not_empty"
            }
        ]
    }
    
    logger.info("Testing LiteLLM direct call...")
    
    try:
        response = await llm_call(config)
        
        if response:
            if hasattr(response, 'choices'):
                content = response.choices[0].message.content
                logger.success(f"✅ Got response: {content}")
            else:
                logger.info(f"Response type: {type(response)}")
                logger.info(f"Response: {response}")
        else:
            logger.error("No response received")
            
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_litellm())