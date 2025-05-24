#!/usr/bin/env python3
"""Test just the code generation test case."""

import asyncio
import sys
import os
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_code_gen():
    """Test code generation with agent validation."""
    config = {
        "model": "max/code-expert",
        "question": "Write a Python function to calculate the factorial of a number.",
        "validation": [
            {
                "type": "response_not_empty"
            },
            {
                "type": "agent_task",
                "params": {
                    "task_prompt_to_claude": "Check if the following response contains valid Python code for calculating factorial:\n\n{CODE_TO_VALIDATE}\n\nAnalyze the code and respond ONLY with JSON: {\"validation_passed\": true, \"reasoning\": \"explanation\", \"details\": \"VALID\" or \"INVALID\"}",
                    "validation_model_alias": "max/text-general",
                    "success_criteria": {"must_contain_in_details": "VALID"}
                }
            }
        ]
    }
    
    logger.info("Testing code generation with agent validation...")
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict):
                if "error" in response:
                    logger.error(f"Error: {response}")
                elif "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    logger.success("✅ Got valid code response!")
                    print("\nGenerated code:")
                    print("-" * 80)
                    print(content)
                    print("-" * 80)
                else:
                    logger.info(f"Unexpected response: {json.dumps(response, indent=2)}")
        else:
            logger.error("No response received")
            
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_code_gen())