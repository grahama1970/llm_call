#!/usr/bin/env python3
"""Test JSON generation case."""

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

logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

async def test_json_gen():
    """Test JSON generation with validation."""
    config = {
        "model": "max/json-expert",
        "messages": [
            {
                "role": "user",
                "content": "Generate a JSON object representing a person with name 'John Doe', age 30, and city 'New York'."
            }
        ],
        "validation": [
            {
                "type": "json_string"
            },
            {
                "type": "field_present",
                "params": {
                    "field_name": "name"
                }
            },
            {
                "type": "field_present",
                "params": {
                    "field_name": "age"
                }
            },
            {
                "type": "field_present",
                "params": {
                    "field_name": "city"
                }
            }
        ]
    }
    
    logger.info("Testing JSON generation with field validation...")
    
    try:
        response = await llm_call(config)
        
        if response:
            if isinstance(response, dict):
                if "error" in response:
                    logger.error(f"Error: {response}")
                elif "choices" in response:
                    content = response["choices"][0]["message"]["content"]
                    logger.success("✅ Got valid JSON response!")
                    print("\nGenerated JSON:")
                    print("-" * 80)
                    print(content)
                    print("-" * 80)
                    
                    # Parse and verify
                    try:
                        data = json.loads(content)
                        print("\nParsed data:")
                        print(json.dumps(data, indent=2))
                    except:
                        print("(Could not parse as JSON)")
                else:
                    logger.info(f"Unexpected response: {json.dumps(response, indent=2)}")
        else:
            logger.error("No response received")
            
    except Exception as e:
        logger.error(f"Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_gen())