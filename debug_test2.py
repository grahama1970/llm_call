# Debug script to see what's happening in Test 2

import asyncio
import os
import sys
from loguru import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
from dotenv import load_dotenv

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, 
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
           level="INFO")

async def test_json_generation():
    load_dotenv()
    initialize_litellm_cache()
    
    config = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a JSON generator. Always respond with valid JSON."},
            {"role": "user", "content": "Generate a JSON object with a 'name' field containing 'test'."}
        ],
        "temperature": 0.0,
        "max_tokens": 50,
        "response_format": {"type": "json_object"},
        "validation": [
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "name"}}
        ],
        "retry_config": {
            "max_attempts": 3,
            "debug_mode": True,
            "initial_delay": 0.5
        }
    }
    
    result = await llm_call(config)
    print(f"\nResult type: {type(result)}")
    print(f"Result: {result}")
    
    if result:
        try:
            if hasattr(result, 'choices'):
                content = result.choices[0].message.content
                print(f"\nContent: {content}")
            else:
                print(f"\nResult is dict: {isinstance(result, dict)}")
        except Exception as e:
            print(f"\nError: {e}")

asyncio.run(test_json_generation())