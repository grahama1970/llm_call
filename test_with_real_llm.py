#!/usr/bin/env python3
"""Test with real LLM call through the async system"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import (
    llm_call,
    get_polling_manager
)
from loguru import logger

# Configure logging  
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

async def test_with_real_llm():
    """Test with a real LLM call"""
    
    # Test 1: Direct call (no polling) with GPT
    logger.info("Test 1: Direct GPT call (no polling expected)\n")
    result1 = await llm_call({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'hello'"}]
    })
    logger.info(f"Result type: {type(result1)}")
    if hasattr(result1, 'choices'):
        logger.info(f"Content: {result1.choices[0].message.content}\n")
    
    # Test 2: Force polling with wait_for_completion
    logger.info("Test 2: Forced polling with wait\n")
    result2 = await llm_call({
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say 'world'"}],
        "polling": True,  # Force polling
        "wait_for_completion": True,
        "timeout": 10
    })
    logger.info(f"Result type: {type(result2)}")
    if hasattr(result2, 'choices'):
        logger.info(f"Content: {result2.choices[0].message.content}\n")
    elif isinstance(result2, dict) and 'choices' in result2:
        logger.info(f"Content: {result2['choices'][0]['message']['content']}\n")
    
    # Check database
    manager = get_polling_manager()
    import sqlite3
    conn = sqlite3.connect(manager.db_path)
    cursor = conn.execute("SELECT task_id, status, substr(result, 1, 50) FROM tasks ORDER BY created_at DESC LIMIT 5")
    logger.info("Recent tasks in database:")
    for row in cursor.fetchall():
        logger.info(f"  - {row[0]}: {row[1]} - {row[2]}...")
    conn.close()

if __name__ == "__main__":
    asyncio.run(test_with_real_llm())
