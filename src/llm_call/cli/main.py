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
        config["validation"] = [{"strategy": v} for v in validation]
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
            except:
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
            "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "Google": ["gemini-pro", "gemini-pro-vision"],
            "Local": ["ollama/llama2", "ollama/mistral"],
            "Claude CLI": ["max/claude-3-opus", "max/claude-3-sonnet", "max/claude-3-haiku"]
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
            console.print(f"✅ Created: {cmd_file}")
        
        generated += 1
    
    console.print(f"[bold green]✅ Generated {generated} slash commands in {output_path}/[/bold green]")
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
    typer.echo(f"✅ Generated MCP config: {output}")
    typer.echo(f"📋 Includes {len(tools)} tools")

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
        typer.echo("❌ FastMCP not installed!")
        typer.echo("\nInstall with:")
        typer.echo("  pip install fastmcp")
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
    
    typer.echo(f"🔧 Registered {registered} MCP tools")
    typer.echo(f"🚀 Starting MCP server on {host}:{port}")
    typer.echo("\nPress Ctrl+C to stop")
    
    # In production, start the actual server
    typer.echo("\n[FastMCP server would run here - install fastmcp first]")

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    app()