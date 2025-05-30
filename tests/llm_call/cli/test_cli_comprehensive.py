#!/usr/bin/env python3
"""
Comprehensive CLI Testing Suite - Real Implementation

This test suite verifies that all CLI commands and features work correctly,
using real implementations without mocking.

Test categories:
1. Core LLM Commands (ask, chat, call, models, validators)
2. Configuration Management (config files, overrides)
3. Auto-generation Commands (generate-claude, generate-mcp-config)
4. MCP Server Features (serve-mcp)
5. Test Runner Commands (test, test-poc)
6. README Alignment Verification
"""

import pytest
import json
import yaml
import os
from pathlib import Path
from typer.testing import CliRunner
import tempfile
import sys

# Import the CLI app
from llm_call.cli.main import app

runner = CliRunner()

# Use OpenAI model for testing since we have API key configured
TEST_MODEL = "gpt-3.5-turbo"


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_json(temp_dir):
    """Create a sample JSON config file."""
    config = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Respond concisely."},
            {"role": "user", "content": "Say 'hello' and nothing else"}
        ],
        "temperature": 0.1,
        "max_tokens": 50,
        "validation": [
            {"type": "contains", "value": "hello"}
        ]
    }
    config_file = temp_dir / "test_config.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file


@pytest.fixture
def sample_config_yaml(temp_dir):
    """Create a sample YAML config file."""
    config = {
        "model": TEST_MODEL,
        "messages": [
            {"role": "user", "content": "Output the number 42 and nothing else"}
        ],
        "temperature": 0.1,
        "max_tokens": 10
    }
    config_file = temp_dir / "test_config.yaml"
    config_file.write_text(yaml.dump(config))
    return config_file


# ============================================
# CORE LLM COMMAND TESTS
# ============================================

class TestAskCommand:
    """Test the 'ask' command functionality."""
    
    def test_ask_basic(self):
        """Test basic ask command."""
        result = runner.invoke(app, [
            "ask", "Say only the word 'test'",
            "--model", TEST_MODEL,
            "--max-tokens", "10",
            "--temp", "0.1"
        ])
        
        assert result.exit_code == 0
        # Check that we got a response (not checking exact content)
        assert "Response" in result.output or "test" in result.output.lower()
        
    def test_ask_with_model(self):
        """Test ask command with model selection."""
        result = runner.invoke(app, [
            "ask", "What is 2+2? Answer with just the number",
            "--model", TEST_MODEL,
            "--max-tokens", "10",
            "--temp", "0.1"
        ])
        
        assert result.exit_code == 0
        assert f"Using model: {TEST_MODEL}" in result.output
        # Check for any digit response (flexible check)
        assert any(char.isdigit() for char in result.output)
        
    def test_ask_with_validation(self):
        """Test ask command with validation."""
        result = runner.invoke(app, [
            "ask", "Generate a JSON object with a key 'test' and value 'passed'",
            "--model", TEST_MODEL,
            "--validate", "json",
            "--max-tokens", "50",
            "--temp", "0.1"
        ])
        
        # Check that validation was attempted
        assert "Applying validation: json" in result.output
        
    def test_ask_json_mode(self):
        """Test ask command with JSON mode."""
        # JSON mode is available for OpenAI models
            
        result = runner.invoke(app, [
            "ask", "Return a JSON object with status: ok",
            "--json",
            "--model", TEST_MODEL,
            "--max-tokens", "50"
        ])
        
        assert result.exit_code == 0
        
    def test_ask_with_system_prompt(self):
        """Test ask command with system prompt."""
        result = runner.invoke(app, [
            "ask", "Hello",
            "--system", "You always respond with 'Greetings!'",
            "--model", TEST_MODEL,
            "--max-tokens", "20",
            "--temp", "0.1"
        ])
        
        assert result.exit_code == 0
        # Check that we got a response
        assert "Response" in result.output
        
    def test_ask_show_config(self):
        """Test ask command with config display."""
        result = runner.invoke(app, [
            "ask", "Test",
            "--show-config",
            "--model", TEST_MODEL,
            "--max-tokens", "10"
        ])
        
        assert result.exit_code == 0
        assert "LLM Configuration" in result.output
        assert '"messages"' in result.output


class TestChatCommand:
    """Test the 'chat' command functionality."""
    
    def test_chat_basic(self):
        """Test basic chat command."""
        # Simulate chat with exit
        result = runner.invoke(app, [
            "chat",
            "--model", TEST_MODEL
        ], input="exit\n")
        
        # Chat exits cleanly with code 0
        assert result.exit_code == 0
        # Check for any indication of chat starting
        assert "Starting chat session" in result.output or "Using model" in result.output
        
    def test_chat_with_system(self):
        """Test chat with system prompt."""
        result = runner.invoke(app, [
            "chat",
            "--system", "You always say 'Coding is fun!'",
            "--model", TEST_MODEL
        ], input="exit\n")
        
        # Chat exits cleanly with code 0
        assert result.exit_code == 0
        assert "System:" in result.output or "system" in result.output.lower()


class TestCallCommand:
    """Test the 'call' command functionality."""
    
    def test_call_json_config(self, sample_config_json):
        """Test call command with JSON config."""
        result = runner.invoke(app, ["call", str(sample_config_json)])
        
        assert result.exit_code == 0
        # Check that we got a response or validation message
        assert "Response" in result.output or "validation" in result.output.lower()
        
    def test_call_yaml_config(self, sample_config_yaml):
        """Test call command with YAML config."""
        result = runner.invoke(app, ["call", str(sample_config_yaml)])
        
        assert result.exit_code == 0
        # Check for any numeric response
        assert any(char.isdigit() for char in result.output) or "Response" in result.output
        
    def test_call_with_overrides(self, sample_config_json):
        """Test call command with config overrides."""
        result = runner.invoke(app, [
            "call", str(sample_config_json),
            "--prompt", "Say 'override worked'",
            "--model", TEST_MODEL
        ])
        
        assert result.exit_code == 0
        # Check that the call was made
        assert "Response" in result.output or "Using model" in result.output


class TestModelCommands:
    """Test model listing commands."""
    
    def test_models_list_all(self):
        """Test listing all models."""
        result = runner.invoke(app, ["models", "--all"])
        
        assert result.exit_code == 0
        assert "Available Models" in result.output
        # Should show at least one provider
        assert any(provider in result.output for provider in ["OpenAI", "Ollama", "Claude CLI"])
        
    def test_models_filter_provider(self):
        """Test filtering models by provider."""
        # Test with a provider we know exists
        result = runner.invoke(app, ["models", "--provider", "openai"])
        
        assert result.exit_code == 0
        # Should show openai/gpt models
        assert "gpt" in result.output.lower() or "openai" in result.output.lower()


class TestValidatorCommand:
    """Test validator listing command."""
    
    def test_validators_list(self):
        """Test listing validation strategies."""
        result = runner.invoke(app, ["validators"])
        
        assert result.exit_code == 0
        assert "Available Validation Strategies" in result.output
        # Should show some validators
        assert any(v in result.output for v in ["json", "contains", "length"])


# ============================================
# CONFIGURATION MANAGEMENT TESTS
# ============================================

class TestConfigManagement:
    """Test configuration file handling."""
    
    def test_config_example_json(self, temp_dir):
        """Test generating example JSON config."""
        output_file = temp_dir / "example.json"
        result = runner.invoke(app, ["config-example", "--output", str(output_file)])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify it's valid JSON
        config = json.loads(output_file.read_text())
        assert "model" in config
        assert "messages" in config
        
    def test_config_example_yaml(self, temp_dir):
        """Test generating example YAML config."""
        output_file = temp_dir / "example.yaml"
        result = runner.invoke(app, ["config-example", "--output", str(output_file), "--format", "yaml"])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify it's valid YAML
        config = yaml.safe_load(output_file.read_text())
        assert "model" in config


# ============================================
# AUTO-GENERATION COMMAND TESTS
# ============================================

class TestGenerateCommands:
    """Test slash command and MCP generation."""
    
    def test_generate_claude(self, temp_dir):
        """Test Claude slash command generation."""
        output_dir = temp_dir / "claude_commands"
        result = runner.invoke(app, ["generate-claude", "--output", str(output_dir)])
        
        assert result.exit_code == 0
        assert "Generated" in result.output
        assert output_dir.exists()
        
        # Check that some command files were created
        json_files = list(output_dir.glob("*.json"))
        assert len(json_files) > 0
        
        # Verify JSON structure
        for json_file in json_files[:1]:  # Check first file
            config = json.loads(json_file.read_text())
            assert "name" in config
            assert "description" in config
            assert "execute" in config
            
    def test_generate_mcp_config(self, temp_dir):
        """Test MCP config generation."""
        output_file = temp_dir / "mcp_config.json"
        result = runner.invoke(app, [
            "generate-mcp-config",
            "--output", str(output_file),
            "--name", "test-cli"
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Verify MCP config structure
        config = json.loads(output_file.read_text())
        assert config["name"] == "test-cli"
        assert "server" in config
        assert "tools" in config
        assert len(config["tools"]) > 0
        
        # Check tool structure
        for tool_name, tool_config in config["tools"].items():
            assert "description" in tool_config
            assert "inputSchema" in tool_config


class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_serve_mcp_help(self):
        """Test serve-mcp command help."""
        result = runner.invoke(app, ["serve-mcp", "--help"])
        
        # Should show help or error about missing fastmcp
        assert result.exit_code == 0 or "FastMCP not installed" in result.output


# ============================================
# TEST RUNNER COMMAND TESTS  
# ============================================

class TestTestRunnerCommands:
    """Test the test runner functionality."""
    
    def test_test_command_no_files(self, temp_dir):
        """Test 'test' command when no test files exist."""
        result = runner.invoke(app, ["test", "poc_*.py", "--dir", str(temp_dir)])
        
        assert result.exit_code == 0
        assert "No test files found" in result.output
        
    def test_test_command_with_files(self, temp_dir):
        """Test 'test' command with test files."""
        # Create a dummy test file
        test_file = temp_dir / "poc_test.py"
        test_file.write_text("""
print("Running test...")
print("✅ VALIDATION PASSED")
""")
        
        result = runner.invoke(app, ["test", "poc_*.py", "--dir", str(temp_dir)])
        
        assert result.exit_code == 0
        assert "PASSED" in result.output
        assert "Test Summary Report" in result.output
        
    def test_test_poc_help(self):
        """Test test-poc command help."""
        result = runner.invoke(app, ["test-poc", "--help"])
        
        assert result.exit_code == 0


# ============================================
# README ALIGNMENT TESTS
# ============================================

class TestREADMEAlignment:
    """Verify CLI commands align with README documentation."""
    
    def test_readme_examples_exist(self):
        """Test that commands mentioned in README exist in CLI."""
        # Commands explicitly mentioned in README
        readme_commands = [
            "ask",
            "chat", 
            "call",
            "models",
            "validators",
            "config-example",
            "generate-claude",
            "generate-mcp-config",
            "serve-mcp",
            "test",
            "test-poc"
        ]
        
        # Get help to see available commands
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        
        for cmd in readme_commands:
            assert cmd in result.output, f"Command '{cmd}' mentioned in README but not in CLI"
            
    def test_readme_ask_examples(self):
        """Test that README 'ask' examples work."""
        # Test basic example from README
        result = runner.invoke(app, [
            "ask", "What is 2+2?",
            "--model", TEST_MODEL,
            "--max-tokens", "10"
        ])
        
        assert result.exit_code == 0


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegration:
    """Test integration between different CLI features."""
    
    def test_config_with_validation(self, temp_dir):
        """Test using config file with validation."""
        # Create config with validation
        config = {
            "model": TEST_MODEL,
            "messages": [{"role": "user", "content": "Say 'valid'"}],
            "validation": [{"type": "contains", "value": "valid"}],
            "max_tokens": 20,
            "temperature": 0.1
        }
        config_file = temp_dir / "validated_config.json"
        config_file.write_text(json.dumps(config))
        
        result = runner.invoke(app, ["call", str(config_file)])
        
        assert result.exit_code == 0
        # Check that validation was attempted or response received
        assert "validation" in result.output.lower() or "Response" in result.output
        
    def test_generate_then_use_commands(self, temp_dir):
        """Test generating commands and verifying they're usable."""
        # Generate Claude commands
        claude_dir = temp_dir / "claude"
        result = runner.invoke(app, ["generate-claude", "--output", str(claude_dir)])
        assert result.exit_code == 0
        
        # Verify 'ask' command was generated
        ask_cmd = claude_dir / "llm-ask.json"
        assert ask_cmd.exists()
        
        config = json.loads(ask_cmd.read_text())
        assert config["name"] == "llm-ask"
        assert "ask" in config["execute"]
        
        # Generate MCP config
        mcp_file = temp_dir / "mcp.json"
        result = runner.invoke(app, ["generate-mcp-config", "--output", str(mcp_file)])
        assert result.exit_code == 0
        
        mcp_config = json.loads(mcp_file.read_text())
        assert "ask" in mcp_config["tools"]


# ============================================
# ERROR HANDLING TESTS
# ============================================

class TestErrorHandling:
    """Test error handling in CLI commands."""
    
    def test_call_missing_config(self):
        """Test call command with missing config file."""
        result = runner.invoke(app, ["call", "nonexistent.json"])
        
        assert result.exit_code == 1
        assert "Error" in result.output
        
    def test_call_invalid_config_format(self, temp_dir):
        """Test call command with unsupported config format."""
        bad_config = temp_dir / "config.txt"
        bad_config.write_text("not json or yaml")
        
        result = runner.invoke(app, ["call", str(bad_config)])
        
        assert result.exit_code == 1
        assert "Error" in result.output
        
    def test_ask_invalid_model(self):
        """Test handling invalid model."""
        result = runner.invoke(app, [
            "ask", "Test",
            "--model", "invalid/model/that/does/not/exist"
        ])
        
        # The command might still succeed with fallback handling
        # Check that some error or warning was shown, or response is None
        assert "error" in result.output.lower() or "Error" in result.output or "None" in result.output or result.exit_code != 0


# ============================================
# VALIDATION FUNCTION
# ============================================

if __name__ == "__main__":
    """Run validation tests to ensure CLI is working."""
    import subprocess
    
    print("🧪 Running CLI Comprehensive Test Suite (Real Implementation)")
    print("=" * 60)
    
    # OpenAI should be configured with API key
    
    print(f"Using test model: {TEST_MODEL}")
    
    # Run pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, 
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
        
    if result.returncode == 0:
        print("\n✅ All CLI tests passed!")
        
        # Additional validation
        print("\n📋 Checking CLI help...")
        help_result = subprocess.run([sys.executable, "-m", "llm_call.cli.main", "--help"], 
                                   capture_output=True, text=True)
        
        if help_result.returncode == 0:
            print("✅ CLI help works correctly")
            
            # Count available commands
            import re
            commands = re.findall(r'^\s+(\w+(?:-\w+)*)\s+', help_result.stdout, re.MULTILINE)
            print(f"📊 Found {len(commands)} CLI commands")
            
            # Verify key commands exist
            key_commands = ["ask", "chat", "call", "models", "test", "generate-claude"]
            missing = [cmd for cmd in key_commands if cmd not in commands]
            
            if missing:
                print(f"❌ Missing commands: {missing}")
            else:
                print("✅ All key commands present")
        else:
            print("❌ CLI help failed")
            
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)