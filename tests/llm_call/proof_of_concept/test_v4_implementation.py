#!/usr/bin/env python3
"""
Test script for V4 Claude Validator Implementation.

This script tests the key features of the v4 implementation:
1. MCP-enhanced Claude proxy server
2. AI-assisted validation with PoCAgentTaskValidator
3. Multi-stage retry with tool escalation
4. Recursive LLM calls via llm_call_tool

Run the proxy server first:
    python src/llm_call/proof_of_concept/poc_claude_proxy_server.py

Then run this test:
    python src/llm_call/proof_of_concept/test_v4_implementation.py
"""

import asyncio
import json
import os
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Import the enhanced components
from llm_call.proof_of_concept.litellm_client_poc import llm_call
from llm_call.proof_of_concept.poc_claude_proxy_server import DEFAULT_ALL_TOOLS_MCP_CONFIG

# Configure logger
logger.remove()
logger.add(
    lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Test cases based on v4 features
async def test_basic_mcp_call():
    """Test 1: Basic call to Claude proxy with default MCP config."""
    logger.info("\n🧪 Test 1: Basic MCP Call with Default Tools")
    
    config = {
        "model": "max/test-default-tools",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What MCP tools do you have available? List them."}
        ],
        "temperature": 0.0
    }
    
    response = await llm_call(config)
    
    if response:
        content = extract_content(response)
        logger.success(f"✅ Got response: {content[:200]}...")
        return True
    else:
        logger.error("❌ No response received")
        return False


async def test_custom_mcp_config():
    """Test 2: Custom MCP config with only specific tools."""
    logger.info("\n🧪 Test 2: Custom MCP Config (Only Perplexity)")
    
    config = {
        "model": "max/test-custom-mcp",
        "messages": [
            {"role": "user", "content": "Use perplexity to search for 'Model Context Protocol MCP Anthropic'"}
        ],
        "mcp_config": {
            "mcpServers": {
                "perplexity-ask": DEFAULT_ALL_TOOLS_MCP_CONFIG["mcpServers"]["perplexity-ask"]
            }
        }
    }
    
    response = await llm_call(config)
    
    if response:
        content = extract_content(response)
        logger.success(f"✅ Got response: {content[:200]}...")
        return True
    else:
        logger.error("❌ No response received")
        return False


async def test_ai_validation_contradiction():
    """Test 3: AI-assisted validation for contradiction checking."""
    logger.info("\n🧪 Test 3: AI Validation - Contradiction Check")
    
    # Text with obvious contradictions
    contradictory_text = """
    The Earth is flat and disk-shaped. The Earth is also a perfect sphere.
    Water always flows downhill due to gravity. Water can flow uphill naturally.
    The sun orbits around the Earth. The Earth orbits around the sun.
    """
    
    config = {
        "model": "meta-task/validate-contradictions",
        "messages": [
            {"role": "assistant", "content": contradictory_text}
        ],
        "validation": [{
            "type": "agent_task",
            "params": {
                "validation_model_alias": "max/contradiction-checker",
                "task_prompt_to_claude": (
                    "Analyze this text for internal contradictions: '{TEXT_TO_VALIDATE}'. "
                    "You should use logical reasoning to identify contradictory statements. "
                    "Respond with JSON: {\"validation_passed\": false if contradictions found, "
                    "\"reasoning\": \"explanation\", \"details\": {\"contradictions\": [list of contradictions]}}"
                ),
                "success_criteria": {"agent_must_report_true": "validation_passed"}
            }
        }],
        "default_validate": False
    }
    
    response = await llm_call(config)
    
    if response:
        if isinstance(response, dict) and "error" in response:
            # Expected - validation should fail due to contradictions
            logger.success(f"✅ Validation correctly failed: {response.get('error', '')}")
            return True
        else:
            logger.warning("⚠️ Validation unexpectedly passed")
            return False
    else:
        logger.error("❌ No response received")
        return False


async def test_code_validation():
    """Test 4: Code syntax validation with agent task."""
    logger.info("\n🧪 Test 4: Code Validation with Agent")
    
    # Deliberately broken Python code
    bad_code = """
def calculate_sum(a, b)  # Missing colon
    result = a + b
    return result
"""
    
    config = {
        "model": "meta-task/validate-python-code",
        "messages": [
            {"role": "assistant", "content": bad_code}
        ],
        "validation": [{
            "type": "agent_task",
            "params": {
                "validation_model_alias": "max/python-validator",
                "task_prompt_to_claude": (
                    "Check this Python code for syntax errors: '{CODE_TO_VALIDATE}'. "
                    "Analyze the code structure and syntax. "
                    "Respond with JSON: {\"validation_passed\": true if syntax is correct, "
                    "\"reasoning\": \"explanation\", \"details\": {\"syntax_errors\": [list of errors]}}"
                ),
                "success_criteria": {"agent_must_report_true": "validation_passed"}
            }
        }],
        "default_validate": False,
        "original_user_prompt": "Validate Python syntax"
    }
    
    response = await llm_call(config)
    
    if response:
        if isinstance(response, dict) and "error" in response:
            logger.success(f"✅ Validation correctly detected syntax error: {response.get('error', '')[:100]}...")
            return True
        else:
            logger.warning("⚠️ Validation missed syntax error")
            return False
    else:
        logger.error("❌ No response received")
        return False


async def test_staged_retry_with_tools():
    """Test 5: Multi-stage retry with tool suggestion."""
    logger.info("\n🧪 Test 5: Staged Retry with Tool Escalation")
    
    config = {
        "model": "max/iterative-coder",
        "messages": [
            {
                "role": "system",
                "content": "Generate code. If it fails validation, fix it. Use tools if suggested."
            },
            {
                "role": "user",
                "content": "Write a Python function that calculates factorial. First attempt should have an error."
            }
        ],
        "retry_config": {
            "max_attempts": 5,
            "debug_mode": True
        },
        "max_attempts_before_tool_use": 2,
        "max_attempts_before_human": 4,
        "debug_tool_name": "perplexity-ask",
        "debug_tool_mcp_config": {
            "mcpServers": {
                "perplexity-ask": DEFAULT_ALL_TOOLS_MCP_CONFIG["mcpServers"]["perplexity-ask"]
            }
        },
        "validation": [{
            "type": "agent_task",
            "params": {
                "validation_model_alias": "max/code-tester",
                "task_prompt_to_claude": (
                    "Validate this Python code: '{CODE_TO_VALIDATE}'. "
                    "Check: 1) Valid syntax, 2) Function named 'factorial', "
                    "3) Correctly calculates factorial(5) = 120. "
                    "Test it mentally or with logical analysis. "
                    "Respond JSON: {\"validation_passed\": bool, \"reasoning\": str, "
                    "\"details\": {\"syntax_ok\": bool, \"correct_name\": bool, \"correct_result\": bool}}"
                ),
                "success_criteria": {
                    "all_true_in_details_keys": ["syntax_ok", "correct_name", "correct_result"]
                }
            }
        }],
        "original_user_prompt": "Write a factorial function"
    }
    
    response = await llm_call(config)
    
    if response:
        content = extract_content(response)
        logger.success(f"✅ Got final response after retries: {content[:200]}...")
        return True
    else:
        logger.error("❌ No response or human escalation needed")
        return False


async def test_json_validation():
    """Test 6: JSON response validation with field checks."""
    logger.info("\n🧪 Test 6: JSON Response Validation")
    
    config = {
        "model": "max/json-generator",
        "messages": [
            {
                "role": "user",
                "content": "Generate a JSON object for a user with fields: name (string), email (string), age (integer), active (boolean)"
            }
        ],
        "response_format": {"type": "json_object"},
        "validation": [
            {"type": "response_not_empty"},
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "name"}},
            {"type": "field_present", "params": {"field_name": "email"}},
            {"type": "field_present", "params": {"field_name": "age"}},
            {"type": "field_present", "params": {"field_name": "active"}},
            {"type": "field_present", "params": {"field_name": "password", "present": False}}  # Should NOT have password
        ]
    }
    
    response = await llm_call(config)
    
    if response:
        content = extract_content(response)
        logger.success(f"✅ Valid JSON generated: {content}")
        return True
    else:
        logger.error("❌ JSON validation failed")
        return False


def extract_content(response: Any) -> str:
    """Extract content from various response formats."""
    if isinstance(response, dict):
        if response.get("choices"):
            return response["choices"][0].get("message", {}).get("content", "")
        elif "error" in response:
            return f"Error: {response['error']}"
    elif hasattr(response, "choices") and response.choices:
        return response.choices[0].message.content or ""
    return str(response)


async def run_all_tests():
    """Run all v4 implementation tests."""
    logger.info("🚀 Starting V4 Implementation Tests")
    logger.info("=" * 60)
    
    # Load environment
    load_dotenv()
    
    # Check proxy server
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get("http://127.0.0.1:3010/health", timeout=2.0)
            health.raise_for_status()
            logger.success("✅ Proxy server is running")
    except:
        logger.error("❌ Proxy server not running! Start it with:")
        logger.error("   python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return
    
    # Run tests
    tests = [
        ("Basic MCP Call", test_basic_mcp_call),
        ("Custom MCP Config", test_custom_mcp_config),
        ("AI Contradiction Validation", test_ai_validation_contradiction),
        ("Code Syntax Validation", test_code_validation),
        ("Staged Retry with Tools", test_staged_retry_with_tools),
        ("JSON Field Validation", test_json_validation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            logger.info(f"\n{'=' * 60}")
            success = await test_func()
            results.append((name, success))
        except Exception as e:
            logger.exception(f"Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    logger.info(f"\n{'=' * 60}")
    logger.info("📊 Test Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        logger.info(f"  {name}: {status}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.success("🎉 All tests passed!")
    else:
        logger.warning(f"⚠️ {total - passed} tests failed")


if __name__ == "__main__":
    asyncio.run(run_all_tests())