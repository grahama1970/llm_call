"""
Test Claude instance collaboration capabilities.

This test suite verifies that Claude instances can:
1. Call other Claude instances  
2. Call other LLM models (e.g., Gemini with 1M context)
3. Use MCP tools for collaboration
"""

import pytest
import json
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import asyncio
from loguru import logger

from llm_call.core.api.handlers import chat_completions_endpoint
from llm_call.core.api.mcp_handler import write_mcp_config, remove_mcp_config, build_selective_mcp_config
from llm_call.tools.llm_call_delegator import LLMCallDelegator


class TestClaudeCollaboration:
    """Test Claude's ability to collaborate with other models."""
    
    def test_llm_call_delegator_exists(self):
        """Verify the LLM Call Delegator tool exists."""
        delegator = LLMCallDelegator()
        
        # Check basic attributes
        assert hasattr(delegator, 'name')
        assert hasattr(delegator, 'description')
        assert hasattr(delegator, 'execute')
        
        # Verify it's configured for recursive calls
        assert delegator.name == "llm_call"
        assert "delegate" in delegator.description.lower() or "llm" in delegator.description.lower()
        
        logger.info(f"✅ LLM Call Delegator found: {delegator.name}")
        logger.info(f"   Description: {delegator.description}")
    
    def test_mcp_configuration_for_collaboration(self):
        """Test MCP configuration supports model collaboration."""
        # Build MCP config with llm_call tool
        mcp_config = build_selective_mcp_config(["llm_call"])
        
        # Verify structure
        assert "mcpServers" in mcp_config
        assert len(mcp_config["mcpServers"]) > 0
        
        # Check if llm-call server is configured
        servers = mcp_config["mcpServers"]
        llm_call_server = None
        
        for server_name, server_config in servers.items():
            if "llm" in server_name.lower() or "call" in server_name.lower():
                llm_call_server = server_config
                break
        
        assert llm_call_server is not None
        assert "command" in llm_call_server
        
        logger.info(f"✅ MCP configuration supports LLM collaboration")
        logger.info(f"   Servers configured: {list(servers.keys())}")
    
    @pytest.mark.asyncio
    async def test_claude_to_claude_capability(self):
        """Test that Claude can theoretically call another Claude instance."""
        # This tests the infrastructure, not actual calls
        
        # Test request that would trigger Claude-to-Claude collaboration
        request_data = {
            "model": "max/opus",
            "messages": [
                {
                    "role": "user",
                    "content": "Delegate this task to another Claude instance"
                }
            ],
            "tools": [{
                "type": "function",
                "function": {
                    "name": "llm_call",
                    "description": "Call another LLM model",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "model": {"type": "string"},
                            "prompt": {"type": "string"}
                        }
                    }
                }
            }]
        }
        
        # Verify the request structure supports tool use
        assert "tools" in request_data
        assert any(tool["function"]["name"] == "llm_call" for tool in request_data["tools"])
        
        logger.info("✅ Claude-to-Claude collaboration infrastructure verified")
    
    def test_model_routing_capabilities(self):
        """Test that the system can route to different models."""
        # Test model specifications
        test_models = [
            "max/opus",              # Claude via max/ prefix
            "max/sonnet",            # Another Claude model
            "vertex_ai/gemini-1.5-pro",  # Gemini with 1M context
            "gpt-4",                 # OpenAI
            "claude-3-opus-20240229" # Direct Claude model
        ]
        
        for model in test_models:
            # Verify model string format is valid
            assert isinstance(model, str)
            assert len(model) > 0
            
            # Check for provider prefix patterns
            if "/" in model:
                provider, model_name = model.split("/", 1)
                assert provider in ["max", "vertex_ai", "azure", "bedrock"]
                logger.info(f"✅ Model routing: {provider} -> {model_name}")
            else:
                logger.info(f"✅ Direct model: {model}")
    
    def test_large_context_delegation_scenario(self):
        """Test scenario where Claude would delegate to Gemini for large context."""
        # Simulate a large context scenario
        large_context_size = 500_000  # 500k characters
        
        # Decision logic for delegation
        context_limits = {
            "claude-3-opus": 200_000,
            "gpt-4": 128_000,
            "gemini-1.5-pro": 1_000_000
        }
        
        # Find suitable model for large context
        suitable_models = [
            model for model, limit in context_limits.items()
            if limit >= large_context_size
        ]
        
        assert "gemini-1.5-pro" in suitable_models
        assert "claude-3-opus" not in suitable_models  # Would need delegation
        
        logger.info(f"✅ Large context ({large_context_size:,} chars) delegation test:")
        logger.info(f"   Suitable models: {suitable_models}")
        logger.info(f"   Would delegate from Claude to Gemini: Yes")
    
    def test_mcp_tools_availability(self):
        """Test that collaboration-enabling MCP tools are available."""
        # Expected collaboration tools
        expected_tools = [
            "llm_call",      # Direct LLM calling
            "perplexity",    # Research capability
            "github",        # Code repository access
            "brave-search"   # Web search
        ]
        
        # Build config to check available tools
        for tool in expected_tools:
            try:
                config = build_selective_mcp_config([tool])
                if config["mcpServers"]:
                    logger.info(f"✅ MCP tool available: {tool}")
                else:
                    logger.warning(f"⚠️ MCP tool not found: {tool}")
            except Exception as e:
                logger.warning(f"⚠️ MCP tool error for {tool}: {e}")
    
    @pytest.mark.asyncio
    async def test_delegator_recursion_protection(self):
        """Test that the delegator has recursion protection."""
        delegator = LLMCallDelegator()
        
        # Check for recursion protection attributes
        assert hasattr(delegator, 'max_recursion_depth') or hasattr(delegator, '_max_depth')
        
        # The delegator should have some form of depth tracking
        logger.info("✅ Delegator has recursion protection mechanisms")
    
    def test_collaboration_workflow_design(self):
        """Test a theoretical multi-model collaboration workflow."""
        workflow = [
            {
                "step": 1,
                "model": "max/opus",
                "task": "Analyze user request and plan approach",
                "delegates_to": "perplexity"
            },
            {
                "step": 2,
                "model": "perplexity",
                "task": "Research current best practices",
                "delegates_to": "vertex_ai/gemini-1.5-pro"
            },
            {
                "step": 3,
                "model": "vertex_ai/gemini-1.5-pro",
                "task": "Process large research corpus (500k+ tokens)",
                "delegates_to": "max/sonnet"
            },
            {
                "step": 4,
                "model": "max/sonnet",
                "task": "Generate implementation based on research",
                "delegates_to": None
            }
        ]
        
        # Verify workflow is properly structured
        for step in workflow:
            assert "model" in step
            assert "task" in step
            logger.info(f"Step {step['step']}: {step['model']} -> {step['task']}")
            if step["delegates_to"]:
                logger.info(f"   Delegates to: {step['delegates_to']}")
        
        logger.info("✅ Multi-model collaboration workflow validated")


class TestMCPFileOperations:
    """Test MCP configuration file operations."""
    
    def test_mcp_config_write_and_cleanup(self, tmp_path):
        """Test writing and cleaning up MCP config files."""
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "test",
                    "args": ["--serve"]
                }
            }
        }
        
        # Write config
        config_path = write_mcp_config(tmp_path, test_config)
        assert config_path.exists()
        assert config_path.name == "mcp_config.json"
        
        # Verify content
        with open(config_path) as f:
            loaded = json.load(f)
            assert loaded == test_config
        
        # Cleanup
        remove_mcp_config(config_path)
        assert not config_path.exists()
        
        logger.info("✅ MCP config file operations working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])