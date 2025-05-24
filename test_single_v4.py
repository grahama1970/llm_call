#!/usr/bin/env python3
"""Test a single v4 validation case directly."""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

async def test_simple_question():
    """Test the simplest case."""
    logger.info("Testing simple question to Claude proxy...")
    
    config = {
        "model": "max/text-general",
        "question": "What is the primary function of a CPU in a computer?"
    }
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict):
                if "error" in response:
                    logger.error(f"Error response: {response}")
                elif "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    logger.success(f"✅ Got response: {content[:100]}...")
                else:
                    logger.info(f"Unexpected response format: {response}")
            else:
                logger.info(f"Response type: {type(response)}")
                if hasattr(response, 'choices'):
                    content = response.choices[0].message.content
                    logger.success(f"✅ Got response: {content[:100]}...")
        else:
            logger.error("No response received")
            
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_question())