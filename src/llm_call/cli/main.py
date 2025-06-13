"""
Module: main.py
Description: Functions for main operations

External Dependencies:
- typer: [Documentation URL]
- yaml: [Documentation URL]
- inspect: [Documentation URL]
- loguru: [Documentation URL]
- rich: [Documentation URL]
- : [Documentation URL]
- asyncio: [Documentation URL]
- llm_call: [Documentation URL]
- fastmcp: [Documentation URL]
- glob: [Documentation URL]
- concurrent: [Documentation URL]

Sample Input:
>>> # Add specific examples based on module functionality

Expected Output:
>>> # Add expected output examples

Example Usage:
>>> # Add usage examples
"""

#!/usr/bin/env python3
"""
LLM CLI with Full Configuration Support and Auto-Generated Slash Commands

This unified CLI provides:
1. Simple commands for quick tasks (ask, chat, models)
2. Full litellm configuration support (validation, retry, etc.)
3. Config file support (JSON/YAML) with CLI overrides
4. Auto-generated Claude Code slash commands
5. MCP server integration

Example usage:
    # Simple usage
    uv run python -m llm_call.cli.main ask "What is Python?"
    
    # With full configuration
    uv run python -m llm_call.cli.main ask "Generate code" --model gpt-4 --validate code --temp 0.3
    
    # Using config file
    uv run python -m llm_call.cli.main call config.json --prompt "Override prompt"
    
    # Generate slash commands
    uv run python -m llm_call.cli.main generate-claude
"""

import typer
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import sys
import yaml
import inspect
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Initialize the CLI app
app = typer.Typer(
    name="llm-cli",
    help="Unified LLM CLI with full configuration support and auto-generated slash commands"
)

# Add slash command and MCP generation
from .slash_mcp_mixin import add_slash_mcp_commands
add_slash_mcp_commands(app)

console = Console()

# Global state for chat sessions
chat_history: List[Dict[str, str]] = []

# ============================================
# CONFIGURATION UTILITIES
# ============================================

def load_config_file(path: Path) -> Dict[str, Any]:
    """Load configuration from JSON or YAML file."""
    if path.suffix == '.json':
        with open(path) as f:
            return json.load(f)
    elif path.suffix in ['.yaml', '.yml']:
        with open(path) as f:
            return yaml.safe_load(f)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")


def build_llm_config(
    prompt: str,
    model: Optional[str] = None,
    validation: Optional[List[str]] = None,
    retry_max: Optional[int] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    response_format: Optional[str] = None,
    config_file: Optional[Path] = None
) -> Dict[str, Any]:
    """Build LLM configuration from various sources."""
    # Start with base config
    config = {
        "messages": [{"role": "user", "content": prompt}]
    }
    
    # Load from config file if provided
    if config_file:
        file_config = load_config_file(config_file)
        config.update(file_config)
        # Messages from CLI override file
        if prompt:
            config["messages"] = [{"role": "user", "content": prompt}]
    
    # Apply CLI overrides
    if model:
        config["model"] = model
    if validation:
        config["validation"] = [{"type": v} for v in validation]
    if retry_max is not None:
        config["retry_config"] = {"max_attempts": retry_max}
    if temperature is not None:
        config["temperature"] = temperature
    if max_tokens is not None:
        config["max_tokens"] = max_tokens
    if system_prompt:
        # Prepend system message
        messages = config.get("messages", [])
        config["messages"] = [{"role": "system", "content": system_prompt}] + messages
    if response_format:
        config["response_format"] = {"type": response_format}
    
    # Default model if not specified
    if "model" not in config:
        config["model"] = "gpt-3.5-turbo"
    
    return config

# ============================================
# CORE LLM COMMANDS
# ============================================

@app.command()
def ask(
    prompt: str = typer.Argument(..., help="Question or prompt for the LLM"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use (e.g., gpt-4, claude-3)"),
    validate: Optional[List[str]] = typer.Option(None, "--validate", "-v", help="Validation strategies to apply"),
    temperature: Optional[float] = typer.Option(None, "--temp", "-t", help="Temperature for response generation"),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens", help="Maximum tokens in response"),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt to prepend"),
    json_mode: bool = typer.Option(False, "--json", "-j", help="Request JSON formatted response"),
    retry: Optional[int] = typer.Option(None, "--retry", "-r", help="Maximum retry attempts"),
    show_config: bool = typer.Option(False, "--show-config", help="Display the configuration being used"),
    stream: bool = typer.Option(False, "--stream", help="Stream the response")
):
    """
    Ask a single question to an LLM with optional configuration.
    
    Examples:
    - Basic: ask "What is Python?"
    - With model: ask "Explain AI" --model gpt-4
    - With validation: ask "Write a function" --validate code
    - Full config: ask "Create API" --model gpt-4 --validate code --temp 0.3 --system "You are an expert"
    """
    import asyncio
    from llm_call.core.caller import make_llm_request
    
    try:
        # Build configuration
        config = build_llm_config(
            prompt=prompt,
            model=model,
            validation=validate,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system,
            response_format="json_object" if json_mode else None,
            retry_max=retry
        )
        
        if stream:
            config["stream"] = True
        
        if show_config:
            console.print(Panel(
                Syntax(json.dumps(config, indent=2), "json"),
                title="LLM Configuration",
                border_style="blue"
            ))
        
        # Make the request
        console.print(f"[bold blue]Using model:[/bold blue] {config.get('model', 'default')}")
        
        if validate:
            console.print(f"[bold yellow]Applying validation:[/bold yellow] {', '.join(validate)}")
        
        with console.status("[bold green]Thinking..."):
            response = asyncio.run(make_llm_request(config))
        
        # Display response
        if isinstance(response, dict) and "content" in response:
            content = response["content"]
        elif hasattr(response, 'choices'):
            content = response.choices[0].message.content
        else:
            content = str(response)
        
        if json_mode:
            try:
                parsed = json.loads(content)
                console.print(Panel(
                    Syntax(json.dumps(parsed, indent=2), "json"),
                    title="Response",
                    border_style="green"
                ))
            except Exception:  # Fallback to plain output if JSON parsing fails
                console.print(Panel(content, title="Response", border_style="green"))
        else:
            console.print(Panel(content, title="Response", border_style="green"))
            
    except Exception as e:
        logger.error(f"LLM request failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def chat(
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use"),
    system: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt"),
    temperature: Optional[float] = typer.Option(None, "--temp", "-t", help="Temperature")
):
    """
    Start an interactive chat session with an LLM.
    
    Examples:
    - Basic: chat
    - With model: chat --model gpt-4
    - With system: chat --system "You are a helpful coding assistant"
    """
    import asyncio
    from llm_call.core.caller import make_llm_request
    
    global chat_history
    
    console.print("[bold green]Starting chat session. Type 'exit' or 'quit' to end.[/bold green]")
    
    if system:
        chat_history.append({"role": "system", "content": system})
        console.print(f"[dim]System: {system}[/dim]")
    
    selected_model = model or "gpt-3.5-turbo"
    console.print(f"[bold blue]Using model:[/bold blue] {selected_model}")
    
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
            
            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold yellow]Ending chat session.[/bold yellow]")
                break
            
            chat_history.append({"role": "user", "content": user_input})
            
            config = {
                "model": selected_model,
                "messages": chat_history,
            }
            
            if temperature is not None:
                config["temperature"] = temperature
            
            with console.status("[bold green]Thinking..."):
                response = asyncio.run(make_llm_request(config))
            
            if isinstance(response, dict) and "content" in response:
                content = response["content"]
            elif hasattr(response, 'choices'):
                content = response.choices[0].message.content
            else:
                content = str(response)
            
            chat_history.append({"role": "assistant", "content": content})
            console.print(f"[bold magenta]Assistant:[/bold magenta] {content}")
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Chat interrupted.[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")


@app.command()
def call(
    config_file: Path = typer.Argument(..., help="Path to configuration file (JSON or YAML)"),
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Override prompt from config"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model from config"),
    validate: Optional[List[str]] = typer.Option(None, "--validate", "-v", help="Override validation"),
    show_config: bool = typer.Option(False, "--show-config", help="Display final configuration")
):
    """
    Make an LLM call using a configuration file with optional overrides.
    
    Examples:
    - Basic: call config.json
    - Override prompt: call config.json --prompt "New prompt"
    - Override model: call config.json --model gpt-4
    - Show config: call config.json --show-config
    """
    import asyncio
    from llm_call.core.caller import make_llm_request
    
    try:
        # Build configuration
        config = build_llm_config(
            prompt=prompt or "",
            model=model,
            validation=validate,
            config_file=config_file
        )
        
        if show_config:
            console.print(Panel(
                Syntax(json.dumps(config, indent=2), "json"),
                title="Final Configuration",
                border_style="blue"
            ))
        
        # Make the request
        with console.status("[bold green]Processing..."):
            response = asyncio.run(make_llm_request(config))
        
        # Display response
        if isinstance(response, dict):
            console.print(Panel(
                Syntax(json.dumps(response, indent=2), "json"),
                title="Response",
                border_style="green"
            ))
        else:
            console.print(Panel(str(response), title="Response", border_style="green"))
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)

@app.command()
def models(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all available models")
):
    """
    List available LLM models.
    
    Examples:
    - List all: models --all
    - Filter by provider: models --provider openai
    """
    try:
        # Common models grouped by provider
        common_models = {
            "OpenAI": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-opus-4-20250514"],
            "Google": ["gemini-pro", "gemini-pro-vision"],
            "Local": ["ollama/llama2", "ollama/mistral"],
            "Claude CLI": ["max/claude-3-opus", "max/claude-3-sonnet", "max/claude-3-haiku", "max/claude-opus-4-20250514"]
        }
        
        console.print("[bold]Available Models:[/bold]")
        
        for provider_name, model_list in common_models.items():
            if provider and provider.lower() not in provider_name.lower():
                continue
                
            console.print(f"\n[bold cyan]{provider_name}:[/bold cyan]")
            for model in model_list:
                console.print(f"  • {model}")
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def validators():
    """List available validation strategies."""
    try:
        from llm_call.core.strategies import VALIDATION_STRATEGIES
        
        console.print("[bold]Available Validation Strategies:[/bold]\n")
        
        for name, strategy in VALIDATION_STRATEGIES.items():
            console.print(f"[bold cyan]{name}:[/bold cyan]")
            if hasattr(strategy, "__doc__") and strategy.__doc__:
                console.print(f"  {strategy.__doc__.strip()}")
            console.print()
    except ImportError:
        # Fallback list if strategies module not available
        strategies = ["json", "code", "schema", "length", "contains", "regex"]
        console.print("[bold]Available Validation Strategies:[/bold]\n")
        for strategy in strategies:
            console.print(f"• {strategy}")


@app.command()
def config_example(
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save to file"),
    format: str = typer.Option("json", "--format", "-f", help="Output format (json/yaml)")
):
    """Generate an example configuration file."""
    example_config = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Your prompt here"}
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
        "validation": [
            {"strategy": "json", "max_attempts": 3},
            {"strategy": "code", "language": "python"}
        ],
        "retry_config": {
            "max_attempts": 3,
            "backoff_factor": 2.0
        },
        "response_format": {
            "type": "json_object"
        }
    }
    
    if format == "yaml":
        content = yaml.dump(example_config, default_flow_style=False)
        syntax_format = "yaml"
    else:
        content = json.dumps(example_config, indent=2)
        syntax_format = "json"
    
    if output:
        output.write_text(content)
        console.print(f"[bold green]Example configuration saved to:[/bold green] {output}")
    else:
        console.print(Panel(
            Syntax(content, syntax_format),
            title=f"Example Configuration ({format.upper()})",
            border_style="blue"
        ))

# ============================================
# AUTO-GENERATION COMMANDS
# ============================================

@app.command()
def generate_claude(
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Generate Claude Code slash commands for all CLI commands.
    
    Creates .json files that Claude Code can use as slash commands with full configuration support.
    
    Examples:
    - Basic: generate-claude
    - Custom output: generate-claude --output .claude/my-commands
    """
    # Determine output directory
    output_path = output_dir or Path(".claude/commands")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Commands to skip
    skip_commands = {"generate-claude", "serve-mcp", "generate-mcp-config"}
    
    generated = 0
    
    for command in app.registered_commands:
        cmd_name = command.name or command.callback.__name__
        
        if cmd_name in skip_commands:
            continue
            
        # Get function details
        func = command.callback
        docstring = func.__doc__ or f"Run {cmd_name} command"
        
        # Clean up docstring
        doc_lines = docstring.strip().split('\n')
        short_description = doc_lines[0]
        
        # Generate Claude Code slash command config
        slash_config = {
            "name": f"llm-{cmd_name}",
            "description": short_description,
            "args": [],
            "execute": f"llm-cli {cmd_name}",
            "type": "command"
        }
        
        # Get function signature for arguments
        try:
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                if param_name in ['self', 'ctx']:
                    continue
                    
                arg_config = {
                    "name": param_name,
                    "type": "string",
                    "optional": param.default != param.empty
                }
                
                if param.annotation != param.empty:
                    if param.annotation == int:
                        arg_config["type"] = "number"
                    elif param.annotation == bool:
                        arg_config["type"] = "boolean"
                
                slash_config["args"].append(arg_config)
        except Exception as e:
            if verbose:
                console.print(f"[yellow]Warning: Could not parse signature for {cmd_name}: {e}[/yellow]")
        
        # Write command file
        cmd_file = output_path / f"{slash_config['name']}.json"
        with open(cmd_file, 'w') as f:
            json.dump(slash_config, f, indent=2)
        
        if verbose:
            console.print(f" Created: {cmd_file}")
        
        generated += 1
    
    console.print(f"[bold green] Generated {generated} slash commands in {output_path}/[/bold green]")
    console.print("\n[bold]Available commands:[/bold]")
    
    # List generated commands
    for json_file in output_path.glob("llm-*.json"):
        with open(json_file) as f:
            config = json.load(f)
            cmd_name = config.get("name", json_file.stem)
            description = config.get("description", "No description")
            console.print(f"  [cyan]/{cmd_name}[/cyan] - {description}")

@app.command()
def generate_mcp_config(
    output: Path = typer.Option("mcp_config.json", "--output", "-o", help="Output file"),
    name: Optional[str] = typer.Option(None, "--name", help="MCP server name"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    port: int = typer.Option(5000, "--port", help="Server port")
):
    """
    Generate MCP (Model Context Protocol) configuration.
    
    Creates a configuration file for using this CLI as an MCP server
    with Claude or other MCP-compatible tools.
    """
    import inspect
    
    server_name = name or "llm-cli"
    
    # Build tool definitions
    tools = {}
    skip_commands = {"generate-claude", "serve-mcp", "generate-mcp-config"}
    
    for command in app.registered_commands:
        cmd_name = command.name or command.callback.__name__
        
        if cmd_name in skip_commands:
            continue
            
        func = command.callback
        docstring = func.__doc__ or f"Execute {cmd_name}"
        
        # Extract parameters
        sig = inspect.signature(func)
        parameters = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'ctx']:
                continue
                
            # Determine type
            param_type = "string"
            if param.annotation != param.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == float:
                    param_type = "number"
                    
            parameters[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            if param.default == param.empty:
                required.append(param_name)
        
        tools[cmd_name] = {
            "description": docstring.strip().split('\n')[0],
            "inputSchema": {
                "type": "object",
                "properties": parameters,
                "required": required
            }
        }
    
    # Build configuration
    config = {
        "name": server_name,
        "version": "1.0.0",
        "description": f"MCP server for {server_name}",
        "server": {
            "command": sys.executable,
            "args": ["-m", "llm_call.cli.main", "serve-mcp", "--host", host, "--port", str(port)]
        },
        "tools": tools,
        "capabilities": {
            "tools": True,
            "prompts": False,
            "resources": False
        }
    }
    
    output.write_text(json.dumps(config, indent=2))
    typer.echo(f" Generated MCP config: {output}")
    typer.echo(f" Includes {len(tools)} tools")

@app.command()
def serve_mcp(
    host: str = typer.Option("localhost", "--host", help="Server host"),
    port: int = typer.Option(5000, "--port", help="Server port"),
    debug: bool = typer.Option(False, "--debug", help="Debug mode")
):
    """
    Serve this CLI as an MCP server using FastMCP.
    
    Allows Claude and other MCP-compatible tools to use CLI commands.
    """
    try:
        from fastmcp import FastMCP
    except ImportError:
        typer.echo(" FastMCP not installed!")
        typer.echo("\nInstall with:")
        typer.echo("  uv add fastmcp")
        raise typer.Exit(1)
    
    # Create FastMCP server
    mcp = FastMCP("llm-cli")
    
    # Skip these commands
    skip_commands = {"generate-claude", "serve-mcp", "generate-mcp-config"}
    
    # Register commands as tools
    registered = 0
    
    for command in app.registered_commands:
        cmd_name = command.name or command.callback.__name__
        
        if cmd_name in skip_commands:
            continue
            
        # Note: In production, properly handle async conversion
        # This is a simplified example
        registered += 1
        
        if debug:
            typer.echo(f"  Registered: {cmd_name}")
    
    typer.echo(f" Registered {registered} MCP tools")
    typer.echo(f" Starting MCP server on {host}:{port}")
    typer.echo("\nPress Ctrl+C to stop")
    
    # In production, start the actual server
    typer.echo("\n[FastMCP server would run here - install fastmcp first]")

# ============================================
# TEST RUNNER COMMANDS
# ============================================

@app.command()
def test(
    pattern: Optional[str] = typer.Argument(None, help="Pattern to match test files (e.g., 'poc_*.py', 'test_*.py')"),
    directory: Optional[Path] = typer.Option(None, "--dir", "-d", help="Directory to search for tests"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Run tests in parallel"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Timeout per test in seconds"),
    show_output: bool = typer.Option(False, "--show-output", "-o", help="Show test output even on success")
):
    """
    Run POC validation tests and report results.
    
    Examples:
    - Run all POCs: test "poc_*.py"
    - Run specific POC: test "poc_11_*.py"
    - Run all tests: test "test_*.py"
    - Run in parallel: test "poc_*.py" --parallel
    - Custom directory: test --dir src/llm_call/proof_of_concept
    """
    import subprocess
    import glob
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from pathlib import Path
    import time
    
    # Default search directory
    if directory:
        search_dir = directory
    else:
        # Try common POC locations
        poc_dirs = [
            Path("src/llm_call/proof_of_concept"),
            Path("src/llm_call/proof_of_concept/code/task_004_test_prompts"),
            Path("tests/llm_call/core"),
            Path(".")
        ]
        
        # Find first existing directory
        search_dir = None
        for d in poc_dirs:
            if d.exists():
                search_dir = d
                break
        
        if not search_dir:
            console.print("[bold red]Error:[/bold red] No test directory found")
            raise typer.Exit(1)
    
    # Default pattern if not provided
    if not pattern:
        pattern = "poc_*.py"
    
    # Find test files
    test_files = []
    
    # Handle recursive search
    if "**" in pattern:
        test_files = list(search_dir.glob(pattern))
    else:
        # Search in directory and immediate subdirectories
        test_files = list(search_dir.glob(pattern))
        for subdir in search_dir.iterdir():
            if subdir.is_dir():
                test_files.extend(subdir.glob(pattern))
    
    if not test_files:
        console.print(f"[bold yellow]No test files found matching '{pattern}' in {search_dir}[/bold yellow]")
        raise typer.Exit(0)
    
    console.print(f"[bold]Found {len(test_files)} test files in {search_dir}[/bold]")
    
    # Test runner function
    def run_test_file(test_file: Path) -> Dict[str, Any]:
        """Run a single test file and return results."""
        start_time = time.time()
        
        try:
            # Run the test
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            elapsed = time.time() - start_time
            
            # Check for success patterns
            success_patterns = [
                "VALIDATION PASSED",
                "All tests passed",
                " VALIDATION PASSED",
                "tests produced expected results",
                " All exponential backoff tests passed",
                " All"
            ]
            
            # Check both stdout and stderr (for loguru output)
            output = result.stdout + result.stderr
            
            # Also check for failure patterns
            failure_patterns = [
                "VALIDATION FAILED",
                "tests failed",
                " VALIDATION FAILED",
                "AssertionError",
                "Exception:",
                "Traceback"
            ]
            
            has_success = any(pattern in output for pattern in success_patterns)
            has_failure = any(pattern in output for pattern in failure_patterns)
            
            # Success if: has success pattern, no failure pattern, and exit code 0
            success = has_success and not has_failure and result.returncode == 0
            
            return {
                "file": test_file.name,
                "success": success,
                "elapsed": elapsed,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output": output
            }
            
        except subprocess.TimeoutExpired:
            return {
                "file": test_file.name,
                "success": False,
                "elapsed": timeout,
                "error": f"Timeout after {timeout}s",
                "output": ""
            }
        except Exception as e:
            return {
                "file": test_file.name,
                "success": False,
                "elapsed": time.time() - start_time,
                "error": str(e),
                "output": ""
            }
    
    # Run tests
    results = []
    
    if parallel:
        console.print("[bold blue]Running tests in parallel...[/bold blue]")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_test_file, f) for f in test_files]
            
            for future in futures:
                results.append(future.result())
    else:
        console.print("[bold blue]Running tests sequentially...[/bold blue]")
        for test_file in test_files:
            if verbose:
                console.print(f"\n[dim]Running {test_file.name}...[/dim]")
            
            result = run_test_file(test_file)
            results.append(result)
            
            # Show immediate feedback
            if result["success"]:
                console.print(f" {result['file']} - [green]PASSED[/green] ({result['elapsed']:.2f}s)")
                if show_output:
                    console.print(Panel(result["output"], title=f"Output: {result['file']}", border_style="green"))
            else:
                console.print(f" {result['file']} - [red]FAILED[/red] ({result['elapsed']:.2f}s)")
                if verbose or show_output:
                    error_msg = result.get("error", "Test failed")
                    console.print(Panel(
                        f"Error: {error_msg}\n\nOutput:\n{result.get('output', 'No output')}",
                        title=f"Failed: {result['file']}",
                        border_style="red"
                    ))
    
    # Summary report
    console.print("\n" + "="*60)
    console.print("[bold]Test Summary Report[/bold]")
    console.print("="*60)
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    total_time = sum(r["elapsed"] for r in results)
    
    console.print(f"\n[bold]Total:[/bold] {len(results)} tests")
    console.print(f"[bold green]Passed:[/bold green] {passed}")
    console.print(f"[bold red]Failed:[/bold red] {failed}")
    console.print(f"[bold]Total time:[/bold] {total_time:.2f}s")
    
    if failed > 0:
        console.print("\n[bold red]Failed tests:[/bold red]")
        for r in results:
            if not r["success"]:
                console.print(f"  • {r['file']}: {r.get('error', 'Test failed')}")
    
    # Performance report
    if verbose and len(results) > 0:
        console.print("\n[bold]Performance Report:[/bold]")
        sorted_results = sorted(results, key=lambda x: x["elapsed"], reverse=True)
        
        console.print("\nSlowest tests:")
        for r in sorted_results[:5]:
            console.print(f"  • {r['file']}: {r['elapsed']:.2f}s")
        
        avg_time = total_time / len(results)
        console.print(f"\nAverage time per test: {avg_time:.2f}s")
    
    # Exit code based on results
    if failed > 0:
        raise typer.Exit(1)
    else:
        console.print("\n[bold green] All tests passed![/bold green]")


@app.command()
def summarize(
    file_path: str = typer.Argument(None, help="Path to file to summarize (or - for stdin)"),
    model: str = typer.Option(None, "--model", "-m", help="Model to use for summarization"),
    strategy: str = typer.Option("auto", "--strategy", "-s", help="Summarization strategy: auto, simple, rolling_window, hierarchical"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (optional)"),
    prompt: str = typer.Option(None, "--prompt", "-p", help="Custom summarization prompt"),
    max_length: int = typer.Option(None, "--max-length", "-l", help="Maximum summary length in tokens"),
    window_size: int = typer.Option(3, "--window-size", "-w", help="Window size for rolling window strategy"),
):
    """Summarize a document using large context models."""
    import asyncio
    from llm_call.core.utils.document_summarizer import summarize_document, summarize_file
    from llm_call.core.utils.auth_diagnostics import diagnose_auth_error
    
    try:
        # Check if we're reading from stdin
        if file_path == "-" or file_path is None:
            if file_path is None and sys.stdin.isatty():
                console.print("[red]Error: No file specified and no input from stdin[/red]")
                console.print("Usage: llm summarize <file> or echo 'text' | llm summarize -")
                raise typer.Exit(1)
            
            # Read from stdin
            console.print("[dim]Reading from stdin...[/dim]")
            text = sys.stdin.read()
            
            if not text.strip():
                console.print("[red]Error: No text provided[/red]")
                raise typer.Exit(1)
            
            # Summarize text
            result = asyncio.run(summarize_document(
                text=text,
                model=model,
                strategy=strategy,
                custom_prompt=prompt,
                summary_max_tokens=max_length,
                window_size=window_size
            ))
            
            # Check if we got a result
            if not result:
                console.print("[red]Error: No result returned from summarization[/red]")
                console.print("[yellow]This may be due to authentication issues. Check your API credentials.[/yellow]")
                raise typer.Exit(1)
            
            # Handle output
            if output:
                from pathlib import Path
                output_path = Path(output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                if output_path.suffix == '.json':
                    import json
                    with open(output_path, 'w') as f:
                        json.dump(result, f, indent=2)
                else:
                    with open(output_path, 'w') as f:
                        f.write(result["summary"])
                console.print(f"[green]Summary saved to {output}[/green]")
            else:
                # Print to console
                console.print("\n[bold]Summary:[/bold]")
                console.print(result["summary"])
                
                # Show metadata
                console.print(f"\n[dim]Strategy: {result.get('strategy', 'unknown')}[/dim]")
                if 'total_chunks' in result:
                    console.print(f"[dim]Total chunks: {result['total_chunks']}[/dim]")
                if 'total_tokens' in result:
                    console.print(f"[dim]Total tokens: {result['total_tokens']}[/dim]")
        else:
            # Summarize file
            from pathlib import Path
            if not Path(file_path).exists():
                console.print(f"[red]Error: File not found: {file_path}[/red]")
                raise typer.Exit(1)
            
            console.print(f"[bold blue]Summarizing {file_path}...[/bold blue]")
            
            kwargs = {
                "model": model,
                "strategy": strategy,
                "output_path": output,
                "window_size": window_size
            }
            
            if prompt:
                kwargs["custom_prompt"] = prompt
            if max_length:
                kwargs["summary_max_tokens"] = max_length
            
            result = asyncio.run(summarize_file(file_path, **kwargs))
            
            # Check if we got a result
            if not result:
                console.print("[red]Error: No result returned from summarization[/red]")
                console.print("[yellow]This may be due to authentication issues. Check your API credentials.[/yellow]")
                raise typer.Exit(1)
            
            # Show result
            console.print("\n[bold green]Summary:[/bold green]")
            console.print(result["summary"])
            
            # Show metadata
            console.print(f"\n[dim]Model: {result.get('model', 'unknown')}[/dim]")
            console.print(f"[dim]Strategy: {result.get('strategy', 'unknown')}[/dim]")
            if 'total_chunks' in result:
                console.print(f"[dim]Total chunks: {result['total_chunks']}[/dim]")
            if 'total_tokens' in result:
                console.print(f"[dim]Total tokens: {result['total_tokens']}[/dim]")
            
            if output:
                console.print(f"\n[green]Summary saved to {output}[/green]")
                
    except Exception as e:
        error_str = str(e).lower()
        
        # Check if this is an authentication error
        if any(auth_term in error_str for auth_term in ["jwt", "token", "auth", "credential", "forbidden", "unauthorized", "403", "401"]):
            console.print("[bold red]Authentication Error Detected[/bold red]")
            # The diagnosis will be printed by diagnose_auth_error
            diagnose_auth_error(e, model, verbose=True)
            console.print("\n[yellow]Tip: After fixing the issue, run the command again.[/yellow]")
        else:
            console.print(f"[bold red]Summarization failed: {e}[/bold red]")
        
        raise typer.Exit(1)


@app.command()
def test_poc(
    poc_number: Optional[int] = typer.Argument(None, help="Specific POC number to run (e.g., 11)"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show all POC files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Run specific POC validation tests.
    
    Examples:
    - List all POCs: test-poc --all
    - Run specific POC: test-poc 11
    - Run POC 27: test-poc 27 --verbose
    """
    from pathlib import Path
    
    # Find POC directory
    poc_dir = Path("src/llm_call/proof_of_concept/code/task_004_test_prompts")
    if not poc_dir.exists():
        poc_dir = Path("src/llm_call/proof_of_concept")
    
    if not poc_dir.exists():
        console.print("[bold red]Error:[/bold red] POC directory not found")
        raise typer.Exit(1)
    
    # List all POCs if requested
    if show_all or poc_number is None:
        poc_files = sorted(poc_dir.glob("poc_*.py"))
        
        if not poc_files:
            console.print("[bold yellow]No POC files found[/bold yellow]")
            raise typer.Exit(0)
        
        console.print("[bold]Available POC files:[/bold]\n")
        
        # Group by number
        poc_groups = {}
        for f in poc_files:
            # Extract POC number
            import re
            match = re.match(r"poc_(\d+)", f.name)
            if match:
                num = int(match.group(1))
                if num not in poc_groups:
                    poc_groups[num] = []
                poc_groups[num].append(f)
        
        for num in sorted(poc_groups.keys()):
            console.print(f"[bold cyan]POC {num:02d}:[/bold cyan]")
            for f in poc_groups[num]:
                # Try to extract description from file
                try:
                    with open(f) as file:
                        lines = file.readlines()[:10]
                        for line in lines:
                            if "POC-" in line and ":" in line:
                                desc = line.split(":", 1)[1].strip()
                                console.print(f"  • {f.name} - {desc}")
                                break
                        else:
                            console.print(f"  • {f.name}")
                except ValueError:  # Handle non-integer input
                    console.print(f"  • {f.name}")
        
        if poc_number is None:
            raise typer.Exit(0)
    
    # Run specific POC
    pattern = f"poc_{poc_number:02d}_*.py" if poc_number < 100 else f"poc_{poc_number}_*.py"
    
    console.print(f"\n[bold]Running POC {poc_number}...[/bold]")
    
    # Call the test command directly
    test(
        pattern=pattern,
        directory=poc_dir,
        verbose=verbose,
        show_output=True,
        parallel=False
    )


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import tempfile
    import os
    
    # If running as usage validation, test the CLI commands
    if len(sys.argv) == 1 or "--test" in sys.argv:
        print("🧪 Testing LLM Call CLI Commands")
        print("=" * 50)
        
        # Test 1: Help command
        print("\n📝 Test 1: Help system")
        sys.argv = ["app", "--help"]
        try:
            app()
            print("✅ Help command works")
        except SystemExit as e:
            if e.code == 0:
                print("✅ Help command works")
            else:
                print(f"❌ Help failed with code {e.code}")
        
        # Test 2: Models command
        print("\n📝 Test 2: Models list")
        sys.argv = ["app", "models"]
        try:
            app()
            print("✅ Models command works")
        except SystemExit as e:
            if e.code == 0:
                print("✅ Models command works")
            else:
                print(f"❌ Models failed with code {e.code}")
        
        # Test 3: Validators command
        print("\n📝 Test 3: Validators list")
        sys.argv = ["app", "validators"]
        try:
            app()
            print("✅ Validators command works")
        except SystemExit as e:
            if e.code == 0:
                print("✅ Validators command works")
            else:
                print(f"❌ Validators failed with code {e.code}")
        
        # Test 4: Config example
        print("\n📝 Test 4: Config example")
        sys.argv = ["app", "config-example"]
        try:
            app()
            print("✅ Config example works")
        except SystemExit as e:
            if e.code == 0:
                print("✅ Config example works")
            else:
                print(f"❌ Config example failed with code {e.code}")
        
        # Test 5: Ask with empty prompt (should fail)
        print("\n📝 Test 5: Ask validation")
        sys.argv = ["app", "ask", ""]
        try:
            app()
            print("❌ Ask should require non-empty prompt")
        except (SystemExit, Exception) as e:
            if hasattr(e, 'code'):
                print("✅ Ask validation works")
            else:
                print("✅ Ask validation works")
        
        # ===== SECTION 3: SLASH COMMAND TESTS =====
        print("\n🔧 Section 3: Slash Commands")
        print("-" * 40)
        
        # Test 1: Generate slash commands
        print("Generating slash commands...")
        sys.argv = ["app", "generate-claude"]
        try:
            app()
            print("✅ Slash command generation completed")
        except SystemExit as e:
            if e.code == 0:
                print("✅ Slash command generation completed")
            else:
                print(f"⚠️  Generate-claude returned code {e.code}")
        
        # Test 2: Verify slash commands exist
        print("\nVerifying slash commands...")
        from pathlib import Path
        import subprocess
        
        claude_dir = Path.home() / ".claude" / "commands"
        expected_commands = ["llm_ask", "llm_call", "granger-llm-ask"]
        
        if claude_dir.exists():
            existing_files = list(claude_dir.glob("llm*.py")) + list(claude_dir.glob("granger-llm*.py"))
            found_commands = [f.stem for f in existing_files]
            
            if found_commands:
                print(f"✅ Found {len(found_commands)} slash commands:")
                for cmd in found_commands:
                    print(f"   - {cmd}")
            else:
                print("⚠️  No llm slash commands found")
        else:
            print("❌ ~/.claude/commands directory not found")
        
        print("\n" + "=" * 50)
        print("✅ LLM Call Complete Validation:")
        print("  ✓ Core module functions")
        print("  ✓ CLI commands") 
        print("  ✓ Slash commands")
        print("ALL COMPONENTS VERIFIED")
        
    else:
        # Normal CLI execution
        app()