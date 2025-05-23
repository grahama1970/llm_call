#!/usr/bin/env python3
"""
Typer CLI with Auto-Generation for Claude Code and FastMCP
This is a complete, working example that you can use as a template.
"""

import typer
from pathlib import Path
from typing import Optional, List
import json
import sys
from datetime import datetime

# Initialize your Typer app
app = typer.Typer(
    name="my-cli",
    help="Example CLI that auto-generates Claude Code commands and MCP wrapper"
)

# ============================================
# YOUR ACTUAL CLI COMMANDS GO HERE
# ============================================

@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Analyze recursively"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Analyze code quality, patterns, and potential issues in the specified path.
    
    This command performs static analysis including:
    - Code complexity metrics
    - Common anti-patterns
    - Security vulnerabilities
    - Performance bottlenecks
    """
    typer.echo(f"🔍 Analyzing: {path}")
    if recursive:
        typer.echo("   Including subdirectories...")
    
    # Your actual analysis implementation would go here
    results = {
        "path": str(path),
        "timestamp": datetime.now().isoformat(),
        "files_analyzed": 42,
        "issues_found": 3,
        "recursive": recursive
    }
    
    if output:
        output.write_text(json.dumps(results, indent=2))
        typer.echo(f"✅ Results saved to: {output}")
    else:
        typer.echo(f"📊 Results: {json.dumps(results, indent=2)}")

@app.command()
def format(
    files: List[Path] = typer.Argument(..., help="Files or directories to format"),
    check: bool = typer.Option(False, "--check", help="Check only, don't modify files"),
    style: str = typer.Option("black", "--style", help="Formatting style: black, prettier, etc.")
):
    """
    Format code files using the specified style guide.
    
    Supports multiple formatters:
    - Python: black, autopep8, yapf
    - JavaScript/TypeScript: prettier
    - Go: gofmt
    - Rust: rustfmt
    """
    for file_path in files:
        if check:
            typer.echo(f"🔍 Checking: {file_path}")
            # In real implementation, check if formatting is needed
            typer.echo(f"   Would reformat: {file_path}")
        else:
            typer.echo(f"✨ Formatting: {file_path} with {style}")
            # Your actual formatting implementation would go here

@app.command()
def test(
    pattern: str = typer.Argument("test_*.py", help="Test file pattern"),
    coverage: bool = typer.Option(False, "--coverage", help="Generate coverage report"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Run tests in parallel"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose test output")
):
    """
    Run tests matching the specified pattern with optional coverage analysis.
    
    Features:
    - Automatic test discovery
    - Parallel execution support
    - Coverage reporting with HTML output
    - JUnit XML report generation
    """
    typer.echo(f"🧪 Running tests: {pattern}")
    
    if parallel:
        typer.echo("   Running in parallel mode...")
    
    # Your actual test runner implementation would go here
    typer.echo("   ✅ 42 tests passed")
    typer.echo("   ⏭️  2 tests skipped")
    typer.echo("   ❌ 0 tests failed")
    
    if coverage:
        typer.echo("\n📊 Coverage Report:")
        typer.echo("   Overall: 87%")
        typer.echo("   src/main.py: 92%")
        typer.echo("   src/utils.py: 78%")

@app.command()
def lint(
    path: Path = typer.Argument(".", help="Path to lint"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix issues where possible"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Custom lint config file")
):
    """
    Run linting checks on your code using multiple linters.
    
    Includes:
    - Style violations (PEP8, ESLint)
    - Type checking (mypy, TypeScript)
    - Security issues (bandit, semgrep)
    - Complexity analysis
    """
    typer.echo(f"🔍 Linting: {path}")
    
    if config:
        typer.echo(f"   Using config: {config}")
    
    # Your actual linting implementation would go here
    issues = [
        "line 42: Missing type annotation",
        "line 78: Function too complex (12 > 10)",
        "line 125: Possible SQL injection"
    ]
    
    if issues and fix:
        typer.echo("🔧 Auto-fixing issues...")
        typer.echo("   Fixed 2 of 3 issues")
    
    for issue in issues[:1] if fix else issues:
        typer.echo(f"   ⚠️  {issue}")

@app.command()
def deploy(
    environment: str = typer.Argument(..., help="Target environment: dev, staging, prod"),
    version: Optional[str] = typer.Option(None, "--version", "-v", help="Specific version to deploy"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate deployment without changes"),
    force: bool = typer.Option(False, "--force", "-f", help="Force deployment without confirmations")
):
    """
    Deploy application to the specified environment.
    
    Deployment process:
    1. Run pre-deployment tests
    2. Build and package application
    3. Deploy to target environment
    4. Run post-deployment health checks
    5. Update deployment manifest
    """
    if not force and environment == "prod" and not dry_run:
        confirm = typer.confirm("⚠️  Deploy to PRODUCTION?")
        if not confirm:
            typer.echo("Deployment cancelled")
            raise typer.Exit(0)
    
    typer.echo(f"🚀 Deploying to: {environment}")
    
    if version:
        typer.echo(f"   Version: {version}")
    else:
        typer.echo("   Version: latest")
    
    if dry_run:
        typer.echo("\n🔍 DRY RUN - No changes will be made")
    
    # Deployment steps
    steps = [
        "Running tests...",
        "Building application...",
        "Uploading artifacts...",
        "Updating configuration...",
        "Starting deployment...",
        "Running health checks..."
    ]
    
    for step in steps:
        typer.echo(f"   → {step}")
        if not dry_run:
            # Your actual deployment logic here
            pass
    
    typer.echo(f"\n✅ {'Would deploy' if dry_run else 'Deployed'} successfully!")

# ============================================
# AUTO-GENERATION COMMANDS
# ============================================

@app.command()
def generate_claude(
    output_dir: Optional[Path] = typer.Option(None, "--output", "-o", help="Output directory for commands"),
    prefix: Optional[str] = typer.Option(None, "--prefix", "-p", help="Prefix for command names"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """
    Generate Claude Code slash commands for all CLI commands.
    
    This creates markdown files in .claude/commands/ that allow you to use
    your CLI commands directly from Claude Code interface.
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
        
        # Add prefix if specified
        slash_cmd_name = f"{prefix}-{cmd_name}" if prefix else cmd_name
        
        # Generate command content
        content = f"""# {short_description}

{docstring.strip()}

## Usage

Execute this command via the CLI:

```bash
python {Path(sys.argv[0]).name} {cmd_name} $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:{slash_cmd_name} --help

# With arguments:
/project:{slash_cmd_name} path/to/files --verbose
```

---
*Auto-generated from Typer CLI command: {cmd_name}*
"""
        
        # Write command file
        cmd_file = output_path / f"{slash_cmd_name}.md"
        cmd_file.write_text(content)
        
        if verbose:
            typer.echo(f"✅ Created: {cmd_file}")
        else:
            typer.echo(f"✅ /project:{slash_cmd_name}")
        
        generated += 1
    
    typer.echo(f"\n🎉 Generated {generated} Claude Code commands in {output_path}")

@app.command()
def generate_mcp_config(
    output: Path = typer.Option("mcp_config.json", "--output", "-o", help="Output file path"),
    name: Optional[str] = typer.Option(None, "--name", help="MCP server name"),
    host: str = typer.Option("localhost", "--host", help="MCP server host"),
    port: int = typer.Option(5000, "--port", help="MCP server port")
):
    """
    Generate MCP (Model Context Protocol) configuration for FastMCP integration.
    
    This creates a configuration file that allows your CLI to be used
    as an MCP server with Claude or other MCP-compatible tools.
    """
    # Determine server name
    server_name = name or Path(sys.argv[0]).stem.replace("_", "-")
    
    # Build tool definitions
    tools = {}
    
    skip_commands = {"generate-claude", "serve-mcp", "generate-mcp-config"}
    
    for command in app.registered_commands:
        cmd_name = command.name or command.callback.__name__
        
        if cmd_name in skip_commands:
            continue
        
        func = command.callback
        docstring = func.__doc__ or f"Execute {cmd_name}"
        
        # Extract parameter information
        import inspect
        sig = inspect.signature(func)
        
        parameters = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ['self', 'ctx']:
                continue
            
            # Determine parameter type
            param_type = "string"  # default
            if param.annotation != param.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == float:
                    param_type = "number"
                elif hasattr(param.annotation, "__origin__"):
                    # Handle List, Optional, etc.
                    if param.annotation.__origin__ == list:
                        param_type = "array"
            
            # Build parameter schema
            param_schema = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            parameters[param_name] = param_schema
            
            # Check if required
            if param.default == param.empty:
                required.append(param_name)
        
        # Build tool definition
        tools[cmd_name] = {
            "description": docstring.strip().split('\n')[0],
            "inputSchema": {
                "type": "object",
                "properties": parameters,
                "required": required
            }
        }
    
    # Build complete configuration
    config = {
        "name": server_name,
        "version": "1.0.0",
        "description": f"MCP server for {server_name} CLI",
        "server": {
            "command": sys.executable,
            "args": [Path(sys.argv[0]).name, "serve-mcp", "--host", host, "--port", str(port)]
        },
        "tools": tools,
        "capabilities": {
            "tools": True,
            "prompts": False,
            "resources": False
        }
    }
    
    # Write configuration
    output.write_text(json.dumps(config, indent=2))
    typer.echo(f"✅ Generated MCP config: {output}")
    typer.echo(f"\n📋 Configuration includes {len(tools)} tools")
    typer.echo(f"🚀 Start server with: python {Path(sys.argv[0]).name} serve-mcp")

@app.command()
def serve_mcp(
    host: str = typer.Option("localhost", "--host", help="Server host"),
    port: int = typer.Option(5000, "--port", help="Server port"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode")
):
    """
    Serve this CLI as an MCP (Model Context Protocol) server using FastMCP.
    
    This allows Claude and other MCP-compatible tools to use your CLI
    commands as tools/functions.
    """
    try:
        from fastmcp import FastMCP
    except ImportError:
        typer.echo("❌ FastMCP not installed!")
        typer.echo("\nInstall with:")
        typer.echo("  pip install fastmcp")
        raise typer.Exit(1)
    
    # Create FastMCP server
    server_name = Path(sys.argv[0]).stem.replace("_", "-")
    mcp = FastMCP(server_name)
    
    # Skip these commands in MCP
    skip_commands = {"generate-claude", "serve-mcp", "generate-mcp-config"}
    
    # Register all CLI commands as MCP tools
    registered = 0
    
    for command in app.registered_commands:
        cmd_name = command.name or command.callback.__name__
        
        if cmd_name in skip_commands:
            continue
        
        func = command.callback
        docstring = func.__doc__ or f"Execute {cmd_name}"
        
        # Create async wrapper for the command
        @mcp.tool(name=cmd_name, description=docstring.strip().split('\n')[0])
        async def mcp_tool_wrapper(**kwargs):
            """Wrapper that calls the original Typer command"""
            # Get the original function from the closure
            original_func = func
            
            try:
                # Call the original function
                # In production, you'd handle async/sync conversion properly
                result = original_func(**kwargs)
                return {"status": "success", "result": result}
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        registered += 1
        
        if debug:
            typer.echo(f"  Registered tool: {cmd_name}")
    
    typer.echo(f"\n🔧 Registered {registered} MCP tools")
    typer.echo(f"🚀 Starting MCP server: {server_name}")
    typer.echo(f"📡 Listening on: {host}:{port}")
    
    if debug:
        typer.echo("\n🐛 Debug mode enabled")
    
    typer.echo("\nPress Ctrl+C to stop the server")
    
    # Start the server
    try:
        # In real implementation, you'd properly start the FastMCP server
        # mcp.run(host=host, port=port)
        typer.echo("\n[FastMCP server would run here]")
        typer.echo("Note: Install fastmcp and implement the actual server.run() method")
    except KeyboardInterrupt:
        typer.echo("\n\n👋 Server stopped")

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    # Check if running in MCP mode
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp-server":
        # Direct MCP server mode
        serve_mcp()
    else:
        # Normal CLI mode
        app()