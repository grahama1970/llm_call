"""
Test script for validating POC retry manager integration.

Tests:
1. Basic retry with validation feedback
2. Tool suggestion after N attempts
3. Human escalation after M attempts
"""

import asyncio
import os
from loguru import logger
from src.llm_call.proof_of_concept.litellm_client_poc import llm_call

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, 
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", 
           level="INFO")


async def test_basic_retry():
    """Test basic retry with validation feedback."""
    logger.info("\n=== Test 1: Basic Retry with Validation ===")
    
    # This should fail validation and retry with feedback
    config = {
        "model": "vertex_ai/gemini-1.5-flash-001",
        "messages": [
            {"role": "user", "content": "Return an empty string"}
        ],
        "temperature": 0.1,
        "max_tokens": 100,
        "validation": [
            {"type": "response_not_empty"}
        ],
        "retry_config": {
            "max_attempts": 2,
            "debug_mode": True
        }
    }
    
    result = await llm_call(config)
    if result:
        logger.success("Basic retry test completed")
    else:
        logger.error("Basic retry test failed")
    
    return result


async def test_tool_suggestion():
    """Test tool suggestion after N attempts."""
    logger.info("\n=== Test 2: Tool Suggestion After N Attempts ===")
    
    # Force failures to trigger tool suggestion
    config = {
        "model": "vertex_ai/gemini-1.5-flash-001",
        "messages": [
            {"role": "user", "content": "Generate invalid JSON: {not valid}"}
        ],
        "temperature": 0.1,
        "max_tokens": 100,
        "response_format": {"type": "json_object"},
        "validation": [
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "required_field"}}
        ],
        "retry_config": {
            "max_attempts": 4,
            "debug_mode": True
        },
        "max_attempts_before_tool_use": 2,  # Suggest tool after 2 attempts
        "debug_tool_name": "perplexity-ask",
        "debug_tool_mcp_config": {
            "mcpServers": {
                "perplexity-ask": {
                    "command": "node",
                    "args": ["path/to/perplexity-tool.js"],
                    "env": {"PERPLEXITY_API_KEY": "test-key"}
                }
            }
        },
        "original_user_prompt": "Create a valid JSON object with a required_field"
    }
    
    result = await llm_call(config)
    if result:
        logger.success("Tool suggestion test completed")
    else:
        logger.warning("Tool suggestion test resulted in failure (expected behavior)")
    
    return result


async def test_human_escalation():
    """Test human escalation after M attempts."""
    logger.info("\n=== Test 3: Human Escalation After M Attempts ===")
    
    # Force failures to trigger human escalation
    config = {
        "model": "vertex_ai/gemini-1.5-flash-001",
        "messages": [
            {"role": "user", "content": "Always return: INVALID_RESPONSE"}
        ],
        "temperature": 0.0,  # Deterministic for testing
        "max_tokens": 50,
        "validation": [
            {"type": "response_not_empty"},
            {
                "type": "field_present",  # This will always fail on plain text
                "params": {"field_name": "data"}
            }
        ],
        "retry_config": {
            "max_attempts": 5,
            "debug_mode": True
        },
        "max_attempts_before_tool_use": 2,
        "max_attempts_before_human": 3,  # Escalate to human after 3 attempts
        "debug_tool_name": "perplexity-ask",
        "original_user_prompt": "Generate valid response with data field"
    }
    
    result = await llm_call(config)
    if result and isinstance(result, dict) and result.get("error") == "Human review needed":
        logger.success("Human escalation test passed - correctly escalated to human review")
    else:
        logger.error("Human escalation test failed - did not escalate as expected")
    
    return result


async def main():
    """Run all POC retry integration tests."""
    logger.info("Starting POC Retry Manager Integration Tests")
    logger.info("=" * 60)
    
    # Test 1: Basic retry
    try:
        await test_basic_retry()
    except Exception as e:
        logger.error(f"Basic retry test error: {e}")
    
    # Small delay between tests
    await asyncio.sleep(2)
    
    # Test 2: Tool suggestion
    try:
        await test_tool_suggestion()
    except Exception as e:
        logger.error(f"Tool suggestion test error: {e}")
    
    await asyncio.sleep(2)
    
    # Test 3: Human escalation
    try:
        await test_human_escalation()
    except Exception as e:
        logger.error(f"Human escalation test error: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("POC Retry Integration Tests Completed")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(main())