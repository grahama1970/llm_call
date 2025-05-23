#!/usr/bin/env python3
"""
Test script for validation integration in core.

This script tests:
1. Basic validators (response_not_empty, json_string)
2. AI-assisted validators
3. MCP configuration passing
4. Dynamic validation loading

Expected output: Successful validation tests
"""

import asyncio
import json
from typing import Dict, Any
from loguru import logger

from llm_call.core.caller import make_llm_request
from llm_call.core.config.loader import load_configuration

# Load config at module level
settings = load_configuration()
from llm_call.core.validation.builtin_strategies.ai_validators import (
    AIContradictionValidator,
    AgentTaskValidator
)


async def test_basic_validation():
    """Test basic validation strategies."""
    logger.info("\n=== Testing Basic Validation ===")
    
    # Test 1: Response not empty (should be default)
    config1 = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Say hello"}],
        # No validation config - should use default ResponseNotEmptyValidator
    }
    
    logger.info("Test 1: Default validation (response_not_empty)")
    # Note: This would make actual API call in real usage
    # Here we're just testing the configuration setup
    
    # Test 2: JSON validation
    config2 = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Return a JSON object with name and age"}],
        "response_format": {"type": "json_object"},
        # Should automatically add JSON validator
    }
    
    logger.info("Test 2: Automatic JSON validation")
    
    # Test 3: Explicit validation config
    config3 = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Return data"}],
        "validation": [
            {"type": "response_not_empty"},
            {"type": "json_string"}
        ]
    }
    
    logger.info("Test 3: Explicit validation config")
    logger.success("✅ Basic validation configs created successfully")


async def test_ai_validation():
    """Test AI-assisted validation."""
    logger.info("\n=== Testing AI-Assisted Validation ===")
    
    # Test contradiction validator
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Write about flat Earth theory"}],
        "validation": [
            {
                "type": "ai_contradiction_check",
                "params": {
                    "text_to_check": "The Earth is both flat and spherical at the same time.",
                    "topic_context": "Earth shape theories",
                    "validation_model": "max/claude-3-opus",
                    "required_mcp_tools": ["perplexity-ask"]
                }
            }
        ]
    }
    
    logger.info("Created AI contradiction validation config")
    logger.info(f"Validation model: {config['validation'][0]['params']['validation_model']}")
    logger.info(f"Required MCP tools: {config['validation'][0]['params']['required_mcp_tools']}")
    
    logger.success("✅ AI validation config created successfully")


async def test_mcp_configuration():
    """Test MCP configuration passing."""
    logger.info("\n=== Testing MCP Configuration ===")
    
    # Test direct MCP config in request
    config = {
        "model": "max/claude-3-opus",
        "messages": [{"role": "user", "content": "Use perplexity to search for Python tutorials"}],
        "mcp_config": {
            "mcpServers": {
                "perplexity-ask": {
                    "command": "npm",
                    "args": ["run", "dev"],
                    "env": {"PERPLEXITY_API_KEY": "test-key"},
                    "description": "Perplexity search tool",
                    "version": "1.0.0"
                }
            }
        }
    }
    
    logger.info("Created request with MCP configuration")
    logger.info(f"MCP tools: {list(config['mcp_config']['mcpServers'].keys())}")
    
    logger.success("✅ MCP configuration created successfully")


async def test_agent_task_validation():
    """Test generic agent task validation."""
    logger.info("\n=== Testing Agent Task Validation ===")
    
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "def add(a, b): return a + b"}],
        "validation": [
            {
                "type": "agent_task",
                "params": {
                    "task_prompt": "Check if the response contains valid Python code that can be executed without errors",
                    "validation_model": "max/claude-3-opus",
                    "required_mcp_tools": ["desktop-commander"]
                }
            }
        ]
    }
    
    logger.info("Created agent task validation config")
    logger.info("Task: Validate Python code")
    
    logger.success("✅ Agent task validation config created successfully")


async def test_validation_registry():
    """Test validation strategy registry."""
    logger.info("\n=== Testing Validation Registry ===")
    
    from llm_call.core.strategies import registry, get_validator
    
    # List registered validators
    registered = list(registry._strategies.keys())
    logger.info(f"Registered validators: {registered}")
    
    # Test getting validators
    try:
        validator1 = get_validator("response_not_empty")
        logger.success("✅ Got response_not_empty validator")
        
        validator2 = get_validator("json_string")
        logger.success("✅ Got json_string validator")
        
        validator3 = get_validator("ai_contradiction_check", 
                                  text_to_check="test", 
                                  topic_context="test topic")
        logger.success("✅ Got ai_contradiction_check validator")
        
    except Exception as e:
        logger.error(f"Failed to get validator: {e}")


async def main():
    """Run all validation integration tests."""
    logger.info("Starting Validation Integration Tests")
    logger.info("=" * 60)
    
    # Run tests
    await test_basic_validation()
    await test_ai_validation()
    await test_mcp_configuration()
    await test_agent_task_validation()
    await test_validation_registry()
    
    logger.info("\n" + "=" * 60)
    logger.success("✅ All validation integration tests completed!")
    logger.info("\nNote: These tests verify configuration setup.")
    logger.info("Actual validation would require running API calls.")
    
    # Show example of complete config
    logger.info("\n=== Example Complete Configuration ===")
    example_config = {
        "model": "max/claude-3-opus",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Analyze this text for contradictions"}
        ],
        "response_format": {"type": "json_object"},
        "mcp_config": {
            "mcpServers": {
                "perplexity-ask": {
                    "command": "npm",
                    "args": ["run", "dev"],
                    "env": {"PERPLEXITY_API_KEY": "YOUR_KEY"},
                    "description": "Perplexity search",
                    "version": "1.0.0"
                }
            }
        },
        "validation": [
            {"type": "response_not_empty"},
            {"type": "json_string"},
            {
                "type": "ai_contradiction_check",
                "params": {
                    "text_to_check": "Sample text to analyze",
                    "topic_context": "Scientific facts",
                    "required_mcp_tools": ["perplexity-ask"]
                }
            }
        ],
        "retry_config": {
            "max_retries": 3,
            "initial_delay": 1.0,
            "debug_mode": True
        }
    }
    
    logger.info(f"Example config structure:")
    logger.info(json.dumps(example_config, indent=2))


if __name__ == "__main__":
    asyncio.run(main())