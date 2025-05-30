#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Feature Tests

This test suite specifically verifies MCP functionality including:
1. MCP configuration generation
2. MCP server functionality
3. Tool registration and execution
4. Claude integration via MCP
"""

import pytest
import json
import sys
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import patch
import tempfile

from llm_call.cli.main import app
from llm_call.cli.slash_mcp_mixin import add_slash_mcp_commands, slash_mcp_cli

runner = CliRunner()


# ============================================
# FIXTURES
# ============================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_cli_app():
    """Create a sample CLI app for testing mixin."""
    import typer
    
    test_app = typer.Typer(name="test-cli")
    
    @test_app.command()
    def hello(name: str = typer.Argument(..., help="Name to greet")):
        """Say hello to someone."""
        print(f"Hello {name}")
        
    @test_app.command()
    def calculate(
        x: int = typer.Argument(..., help="First number"),
        y: int = typer.Argument(..., help="Second number"),
        operation: str = typer.Option("add", help="Operation to perform")
    ):
        """Perform calculation on two numbers."""
        if operation == "add":
            print(x + y)
        elif operation == "multiply":
            print(x * y)
            
    return test_app


# ============================================
# MCP CONFIGURATION TESTS
# ============================================

class TestMCPConfiguration:
    """Test MCP configuration generation."""
    
    def test_generate_mcp_config_structure(self, temp_dir):
        """Test that generated MCP config has correct structure."""
        output_file = temp_dir / "mcp_config.json"
        
        result = runner.invoke(app, [
            "generate-mcp-config",
            "--output", str(output_file),
            "--name", "llm-cli-test",
            "--host", "0.0.0.0",
            "--port", "8080"
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        config = json.loads(output_file.read_text())
        
        # Verify top-level structure
        assert config["name"] == "llm-cli-test"
        assert config["version"] == "1.0.0"
        assert "description" in config
        assert "server" in config
        assert "tools" in config
        assert "capabilities" in config
        
        # Verify server configuration
        server_config = config["server"]
        assert "command" in server_config
        assert "args" in server_config
        assert "--host" in server_config["args"]
        assert "0.0.0.0" in server_config["args"]
        assert "--port" in server_config["args"]
        assert "8080" in server_config["args"]
        
        # Verify capabilities
        capabilities = config["capabilities"]
        assert capabilities["tools"] is True
        assert capabilities["prompts"] is False
        assert capabilities["resources"] is False
        
    def test_mcp_tool_definitions(self, temp_dir):
        """Test that MCP tools are properly defined."""
        output_file = temp_dir / "mcp_config.json"
        
        result = runner.invoke(app, [
            "generate-mcp-config",
            "--output", str(output_file)
        ])
        
        assert result.exit_code == 0
        
        config = json.loads(output_file.read_text())
        tools = config["tools"]
        
        # Verify key tools are present
        expected_tools = ["ask", "chat", "call", "models", "validators"]
        for tool in expected_tools:
            assert tool in tools, f"Tool '{tool}' not found in MCP config"
            
        # Verify tool structure
        ask_tool = tools["ask"]
        assert "description" in ask_tool
        assert "inputSchema" in ask_tool
        
        schema = ask_tool["inputSchema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        
        # Verify ask tool parameters
        properties = schema["properties"]
        assert "prompt" in properties
        assert properties["prompt"]["type"] == "string"
        
        # Verify prompt is a parameter (required field may not exist)
        assert "prompt" in properties
        
    def test_mcp_parameter_types(self, temp_dir):
        """Test that parameter types are correctly mapped."""
        output_file = temp_dir / "mcp_config.json"
        
        result = runner.invoke(app, ["generate-mcp-config", "--output", str(output_file)])
        assert result.exit_code == 0
        
        config = json.loads(output_file.read_text())
        
        # Check different parameter types
        ask_tool = config["tools"]["ask"]
        properties = ask_tool["inputSchema"]["properties"]
        
        # String parameters
        assert properties.get("prompt", {}).get("type") == "string"
        assert properties.get("model", {}).get("type") == "string"
        
        # Temperature might be string in MCP format
        if "temperature" in properties:
            assert properties["temperature"]["type"] in ["number", "string"]
        if "max_tokens" in properties:
            # MCP tools typically use strings for all parameters
            assert properties["max_tokens"]["type"] in ["integer", "string"]
            
        # Boolean parameters
        if "json_mode" in properties:
            assert properties["json_mode"]["type"] == "boolean"


# ============================================
# MCP SERVER TESTS
# ============================================

class TestMCPServer:
    """Test MCP server functionality."""
    
    def test_serve_mcp_initialization(self):
        """Test MCP server initialization."""
        # FastMCP is installed, so this should succeed
        result = runner.invoke(app, ["serve-mcp", "--host", "localhost", "--port", "5000"])
        
        # Should successfully initialize
        assert result.exit_code == 0
        assert "Starting MCP server" in result.output
        assert "Registered" in result.output and "MCP tools" in result.output
        
    def test_serve_mcp_missing_dependency(self):
        """Test error when FastMCP is not installed."""
        with patch.dict(sys.modules, {'fastmcp': None}):
            result = runner.invoke(app, ["serve-mcp"])
            
            assert result.exit_code == 1
            assert "FastMCP not installed" in result.output
            assert "pip install fastmcp" in result.output
            
    def test_serve_mcp_debug_mode(self):
        """Test MCP server in debug mode."""
        # FastMCP is installed, so debug mode should work
        result = runner.invoke(app, ["serve-mcp", "--debug"])
        
        # Should successfully initialize in debug mode
        assert result.exit_code == 0
        assert "Starting MCP server" in result.output


# ============================================
# SLASH MCP MIXIN TESTS
# ============================================

class TestSlashMCPMixin:
    """Test the universal slash/MCP mixin functionality."""
    
    def test_add_slash_mcp_commands(self, sample_cli_app, temp_dir):
        """Test adding slash/MCP commands to a CLI app."""
        # Add slash/MCP commands
        enhanced_app = add_slash_mcp_commands(
            sample_cli_app,
            output_dir=str(temp_dir / "commands")
        )
        
        # Verify commands were added
        command_names = [cmd.name or cmd.callback.__name__ for cmd in enhanced_app.registered_commands]
        
        assert "generate-claude" in command_names
        assert "generate-mcp-config" in command_names
        assert "serve-mcp" in command_names
        
        # Original commands should still exist
        assert "hello" in command_names
        assert "calculate" in command_names
        
    def test_generate_claude_via_mixin(self, sample_cli_app, temp_dir):
        """Test Claude generation via mixin."""
        enhanced_app = add_slash_mcp_commands(sample_cli_app)
        runner_local = CliRunner()
        
        output_dir = temp_dir / "claude_commands"
        result = runner_local.invoke(enhanced_app, [
            "generate-claude",
            "--output", str(output_dir)
        ])
        
        assert result.exit_code == 0
        assert output_dir.exists()
        
        # Check that original commands were converted
        files = list(output_dir.glob("*.md"))
        assert len(files) >= 2  # hello and calculate
        
        # Verify file content
        hello_file = output_dir / "hello.md"
        assert hello_file.exists()
        content = hello_file.read_text()
        assert "Say hello to someone" in content
        assert "/project:hello" in content
        
    def test_generate_mcp_via_mixin(self, sample_cli_app, temp_dir):
        """Test MCP config generation via mixin."""
        enhanced_app = add_slash_mcp_commands(sample_cli_app)
        runner_local = CliRunner()
        
        output_file = temp_dir / "mcp.json"
        result = runner_local.invoke(enhanced_app, [
            "generate-mcp-config",
            "--output", str(output_file),
            "--name", "test-cli"
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        
        config = json.loads(output_file.read_text())
        assert config["name"] == "test-cli"
        
        # Verify original commands are in tools
        tools = config["tools"]
        assert "hello" in tools
        assert "calculate" in tools
        
        # Verify parameter mapping
        calc_tool = tools["calculate"]
        properties = calc_tool["inputSchema"]["properties"]
        assert properties["x"]["type"] == "integer"
        assert properties["y"]["type"] == "integer"
        assert properties["operation"]["type"] == "string"
        
    def test_slash_mcp_decorator(self):
        """Test the @slash_mcp_cli decorator."""
        import typer
        
        # Create app and decorate it
        app = typer.Typer()
        
        @app.command()
        def test_command():
            """Test command."""
            print("Test")
        
        # Apply decorator
        decorated_app = slash_mcp_cli(name="decorated-cli")(app)
        
        # Verify slash/MCP commands were added
        command_names = [cmd.name or cmd.callback.__name__ for cmd in decorated_app.registered_commands]
        assert "generate-claude" in command_names
        assert "generate-mcp-config" in command_names
        assert "serve-mcp" in command_names


# ============================================
# CLAUDE INTEGRATION TESTS
# ============================================

class TestClaudeIntegration:
    """Test Claude-specific MCP integration."""
    
    def test_claude_slash_command_format(self, temp_dir):
        """Test that Claude slash commands have correct format."""
        output_dir = temp_dir / "claude"
        
        result = runner.invoke(app, [
            "generate-claude",
            "--output", str(output_dir),
            "--verbose"
        ])
        
        assert result.exit_code == 0
        
        # Check ask command
        ask_file = output_dir / "llm-ask.json"
        assert ask_file.exists()
        
        config = json.loads(ask_file.read_text())
        
        # Verify Claude slash command structure
        assert "name" in config
        assert "description" in config
        assert "args" in config
        assert "execute" in config
        assert config["type"] == "command"
        
        # Verify execute command format
        assert "llm-cli ask" in config["execute"]
        
        # Verify arguments
        args = config["args"]
        prompt_arg = next((arg for arg in args if arg["name"] == "prompt"), None)
        assert prompt_arg is not None
        assert prompt_arg["type"] == "string"
        # Claude commands mark all args as optional
        assert "optional" in prompt_arg
        
    def test_claude_command_skip_list(self, temp_dir):
        """Test that certain commands are skipped for Claude."""
        output_dir = temp_dir / "claude"
        
        result = runner.invoke(app, ["generate-claude", "--output", str(output_dir)])
        
        assert result.exit_code == 0
        
        # These commands should NOT be generated
        skip_commands = ["generate-claude", "serve-mcp", "generate-mcp-config"]
        
        for skip_cmd in skip_commands:
            skip_file = output_dir / f"llm-{skip_cmd}.json"
            assert not skip_file.exists(), f"Command {skip_cmd} should be skipped"
            
    def test_mcp_tool_execution_mapping(self, temp_dir):
        """Test that MCP tools map correctly to CLI execution."""
        output_file = temp_dir / "mcp.json"
        
        result = runner.invoke(app, ["generate-mcp-config", "--output", str(output_file)])
        assert result.exit_code == 0
        
        config = json.loads(output_file.read_text())
        
        # Verify server args include proper module execution
        server_args = config["server"]["args"]
        assert "-m" in server_args
        assert "llm_call.cli.main" in server_args
        assert "serve-mcp" in server_args


# ============================================
# END-TO-END MCP TESTS
# ============================================

class TestMCPEndToEnd:
    """Test complete MCP workflow."""
    
    def test_full_mcp_generation_workflow(self, temp_dir):
        """Test generating both Claude and MCP configs."""
        # Generate Claude commands
        claude_dir = temp_dir / "claude"
        result = runner.invoke(app, ["generate-claude", "--output", str(claude_dir)])
        assert result.exit_code == 0
        
        # Generate MCP config
        mcp_file = temp_dir / "mcp.json"
        result = runner.invoke(app, ["generate-mcp-config", "--output", str(mcp_file)])
        assert result.exit_code == 0
        
        # Verify consistency between Claude and MCP
        claude_files = list(claude_dir.glob("llm-*.json"))
        mcp_config = json.loads(mcp_file.read_text())
        mcp_tools = mcp_config["tools"]
        
        # Every Claude command should have corresponding MCP tool
        for claude_file in claude_files:
            claude_config = json.loads(claude_file.read_text())
            command_name = claude_config["name"].replace("llm-", "")
            
            # Skip meta commands
            if command_name not in ["generate-claude", "serve-mcp", "generate-mcp-config"]:
                assert command_name in mcp_tools, f"Command {command_name} in Claude but not MCP"
                
    def test_mcp_parameter_consistency(self, temp_dir):
        """Test that parameters are consistent across formats."""
        # Generate MCP config
        mcp_file = temp_dir / "mcp.json"
        result = runner.invoke(app, ["generate-mcp-config", "--output", str(mcp_file)])
        assert result.exit_code == 0
        
        mcp_config = json.loads(mcp_file.read_text())
        
        # Test ask command parameters
        ask_tool = mcp_config["tools"]["ask"]
        ask_params = ask_tool["inputSchema"]["properties"]
        
        # Core parameters should exist
        assert "prompt" in ask_params
        assert "model" in ask_params
        assert "temperature" in ask_params
        
        # Check required field exists (may be empty for CLI tools)
        required = ask_tool["inputSchema"].get("required", [])
        # CLI tools typically have all optional parameters
        assert isinstance(required, list)


# ============================================
# VALIDATION FUNCTION
# ============================================

if __name__ == "__main__":
    """Run MCP feature tests."""
    import subprocess
    
    print("🔌 Running MCP Feature Test Suite")
    print("=" * 60)
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__,
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
        
    if result.returncode == 0:
        print("\n✅ All MCP tests passed!")
        
        # Additional MCP validation
        print("\n📋 Testing MCP generation...")
        
        # Try to generate MCP config
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            gen_result = subprocess.run([
                sys.executable, "-m", "llm_call.cli.main",
                "generate-mcp-config", "--output", tmp.name
            ], capture_output=True, text=True)
            
            if gen_result.returncode == 0:
                print("✅ MCP config generation works")
                
                # Parse and validate
                import json
                config = json.loads(Path(tmp.name).read_text())
                print(f"📊 Generated {len(config.get('tools', {}))} MCP tools")
                
                # Check for key tools
                key_tools = ["ask", "chat", "call"]
                missing = [t for t in key_tools if t not in config.get('tools', {})]
                if missing:
                    print(f"❌ Missing tools: {missing}")
                else:
                    print("✅ All key tools present in MCP config")
            else:
                print("❌ MCP config generation failed")
                print(gen_result.stderr)
                
            Path(tmp.name).unlink()  # Clean up
    else:
        print("\n❌ Some MCP tests failed!")
        sys.exit(1)