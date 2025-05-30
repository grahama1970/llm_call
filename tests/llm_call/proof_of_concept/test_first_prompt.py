#!/usr/bin/env python3
"""Test the first prompt from test_prompts.json"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

async def test_first_prompt():
    """Test the simplest Claude proxy call."""
    
    # First test case from test_prompts.json
    config = {
        "model": "max/text-general",
        "question": "What is the primary function of a CPU in a computer?"
    }
    
    logger.info(f"Testing with config: {config}")
    
    try:
        response = await llm_call(config)
        
        if response:
            logger.success("Got response!")
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response: {response}")
            
            # Extract content
            if isinstance(response, dict) and response.get("choices"):
                content = response["choices"][0]["message"]["content"]
                logger.success(f"Content: {content}")
            else:
                logger.warning(f"Unexpected response format")
        else:
            logger.error("No response received")
            
    except Exception as e:
        logger.exception(f"Test failed with exception: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(test_first_prompt())