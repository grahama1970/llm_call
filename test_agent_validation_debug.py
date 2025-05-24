#!/usr/bin/env python3
"""Debug agent task validation."""

import asyncio
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

# Very verbose logging
logger.remove()
logger.add(sys.stdout, level="DEBUG", format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_agent_validation():
    """Test agent task validation with debugging."""
    config = {
        "model": "max/text-general",
        "messages": [
            {
                "role": "user", 
                "content": "Write a simple Python function that adds two numbers."
            }
        ],
        "validation": [
            {
                "type": "agent_task",
                "params": {
                    "task_prompt_to_claude": "Check if this is valid Python code:\n\n{CODE_TO_VALIDATE}\n\nRespond ONLY with JSON: {\"validation_passed\": true, \"reasoning\": \"It's valid Python\", \"details\": \"VALID\"}",
                    "validation_model_alias": "max/text-general",
                    "success_criteria": {"must_contain_in_details": "VALID"}
                }
            }
        ],
        "retry_config": {
            "max_attempts": 1,
            "debug_mode": True
        }
    }
    
    logger.info("Testing agent task validation...")
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict) and "choices" in response:
                content = response["choices"][0]["message"]["content"]
                logger.success(f"✅ Validation passed! Got response:")
                print(content)
            else:
                logger.info(f"Response: {response}")
        else:
            logger.error("No response")
            
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_validation())