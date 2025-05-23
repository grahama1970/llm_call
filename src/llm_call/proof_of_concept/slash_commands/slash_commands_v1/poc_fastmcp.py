#!/usr/bin/env python3
"""
FastMCP Integration Example for Claude Code Slash Commands
This shows how to create Claude Code commands that leverage MCP tools
"""

import typer
from pathlib import Path
import json
from typing import Optional

app = typer.Typer(help="FastMCP-Claude Code Integration")

# Example MCP tool command templates
MCP_TEMPLATES = {
    "search-code": {
        "description": "Search code using MCP tools",
        "content": """Search for code pattern: $ARGUMENTS

Use the following MCP tools in order:
1. search_code - Search in current project
2. search_repositories - Search in GitHub
3. web_search - Search documentation and examples

Provide a comprehensive summary of findings with code examples.
"""
    },
    
    "analyze-project": {
        "description": "Comprehensive project analysis using MCP",
        "content": """Analyze project: $ARGUMENTS

Perform comprehensive analysis using MCP tools:
1. list_directory - Explore project structure
2. read_file - Read key files (README, package.json, etc.)
3. search_code - Find patterns and dependencies
4. get_file_info - Gather statistics

Generate a report including:
- Project structure overview
- Technology stack
- Code patterns and conventions
- Potential improvements
"""
    },
    
    "mcp-workflow": {
        "description": "Execute MCP-based workflow",
        "content": """Execute MCP workflow: $ARGUMENTS

Available MCP tools to use:
- File operations: read_file, write_file, create_directory
- Code search: search_code, search_files
- Git operations: via execute_command
- Web tools: web_search, web_fetch

Parse the workflow request and execute appropriate MCP tools in sequence.
"""
    },
    
    "fetch-docs": {
        "description": "Fetch and summarize documentation",
        "content": """Fetch documentation for: $ARGUMENTS

Steps:
1. Use web_search to find official documentation
2. Use web_fetch to retrieve documentation pages
3. Extract and summarize key information
4. Save summary to project documentation folder

Focus on:
- Installation instructions
- Key features
- API reference
- Code examples
"""
    }
}


@app.command()
def create_mcp_commands():
    """Create all MCP-integrated Claude Code commands"""
    
    commands_dir = Path(".claude/commands")
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    for name, template in MCP_TEMPLATES.items():
        command_file = commands_dir / f"mcp-{name}.md"
        
        content = f"""# MCP Integration: {template['description']}
# This command leverages MCP tools within Claude Code

{template['content']}

---
*This is an MCP-integrated command. Claude will use available MCP tools to complete this task.*
"""
        
        command_file.write_text(content)
        typer.echo(f"✅ Created /project:mcp-{name}")
    
    typer.echo(f"\n🎉 Created {len(MCP_TEMPLATES)} MCP-integrated commands")


@app.command()
def create_fastmcp_wrapper(
    mcp_server: str = typer.Argument(..., help="FastMCP server name"),
    command_name: str = typer.Option(None, help="Custom command name"),
    description: str = typer.Option("FastMCP tool wrapper", help="Command description")
):
    """Create a Claude Code command that wraps a FastMCP server"""
    
    if not command_name:
        command_name = f"mcp-{mcp_server}"
    
    commands_dir = Path(".claude/commands")
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    command_content = f"""# FastMCP Server: {mcp_server}
# {description}

Execute FastMCP tool from {mcp_server} server with arguments: $ARGUMENTS

This command interfaces with the {mcp_server} MCP server.
Available tools depend on the server implementation.

Usage examples:
- /project:{command_name} list available tools
- /project:{command_name} execute tool_name param1 param2
- /project:{command_name} help tool_name

Note: Ensure the {mcp_server} MCP server is running and accessible.
"""
    
    command_file = commands_dir / f"{command_name}.md"
    command_file.write_text(command_content)
    
    typer.echo(f"✅ Created /project:{command_name} for FastMCP server: {mcp_server}")


@app.command()
def create_mcp_chain(
    name: str = typer.Argument(..., help="Chain command name"),
    tools: str = typer.Argument(..., help="Comma-separated list of MCP tools")
):
    """Create a command that chains multiple MCP tools"""
    
    tool_list = [t.strip() for t in tools.split(",")]
    
    commands_dir = Path(".claude/commands")
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate tool chain content
    tool_steps = "\n".join([f"{i+1}. {tool}" for i, tool in enumerate(tool_list)])
    
    command_content = f"""# MCP Tool Chain: {name}
# Executes multiple MCP tools in sequence

Process request: $ARGUMENTS

Execute the following MCP tools in order:
{tool_steps}

Each tool's output should inform the next tool's input.
Provide a consolidated summary at the end.

Example workflow:
- First tool gathers information
- Middle tools process/transform data  
- Final tool produces the result
"""
    
    command_file = commands_dir / f"chain-{name}.md"
    command_file.write_text(command_content)
    
    typer.echo(f"✅ Created /project:chain-{name} with {len(tool_list)} tools")


@app.command()
def demo():
    """Run a complete demo of MCP integration"""
    
    typer.echo("🚀 FastMCP-Claude Code Integration Demo")
    typer.echo("=" * 50)
    
    # Create all MCP commands
    typer.echo("\n1️⃣ Creating MCP-integrated commands...")
    create_mcp_commands()
    
    # Create a FastMCP wrapper
    typer.echo("\n2️⃣ Creating FastMCP server wrapper...")
    create_fastmcp_wrapper("github", "gh-tools", "GitHub operations via FastMCP")
    
    # Create a tool chain
    typer.echo("\n3️⃣ Creating MCP tool chain...")
    create_mcp_chain("analyze-and-fix", "search_code,read_file,write_file")
    
    # Create a custom workflow
    typer.echo("\n4️⃣ Creating custom MCP workflow...")
    commands_dir = Path(".claude/commands")
    custom_workflow = commands_dir / "mcp-custom-workflow.md"
    custom_workflow.write_text("""# Custom MCP Workflow
# This demonstrates a complex MCP tool integration

Objective: $ARGUMENTS

This workflow combines multiple MCP capabilities:

## Phase 1: Discovery
- Use search_code to find relevant files
- Use read_file to examine content
- Use web_search for documentation if needed

## Phase 2: Analysis  
- Parse and understand the code structure
- Identify patterns and dependencies
- Check for potential issues

## Phase 3: Action
- Create or modify files as needed
- Execute commands for testing
- Generate summary report

The workflow adapts based on the specific request in $ARGUMENTS.
""")
    typer.echo("✅ Created /project:mcp-custom-workflow")
    
    # List all created commands
    typer.echo("\n📋 Created MCP Commands:")
    typer.echo("-" * 30)
    
    for cmd_file in sorted(commands_dir.glob("mcp-*.md")):
        typer.echo(f"  /project:{cmd_file.stem}")
    
    for cmd_file in sorted(commands_dir.glob("chain-*.md")):
        typer.echo(f"  /project:{cmd_file.stem}")
    
    typer.echo("\n✨ Demo complete!")
    typer.echo("\nUsage in Claude Code:")
    typer.echo("  /project:mcp-search-code find all TODO comments")
    typer.echo("  /project:mcp-analyze-project ./src")
    typer.echo("  /project:mcp-fetch-docs FastMCP documentation")
    typer.echo("  /project:gh-tools list repositories")
    typer.echo("  /project:chain-analyze-and-fix bug in authentication")


# Example of how to integrate with actual FastMCP server
@app.command()
def fastmcp_config(
    output: Optional[Path] = typer.Option("mcp_config.json", help="Output config file")
):
    """Generate FastMCP configuration for Claude Code integration"""
    
    config = {
        "servers": {
            "claude-code-bridge": {
                "command": "python",
                "args": ["slashcli.py", "mcp-server"],
                "env": {
                    "CLAUDE_CODE_COMMANDS": ".claude/commands"
                }
            }
        },
        "tools": {
            "create_command": {
                "description": "Create a new Claude Code slash command",
                "parameters": {
                    "name": "string",
                    "content": "string",
                    "description": "string"
                }
            },
            "execute_command": {
                "description": "Execute a Claude Code command",
                "parameters": {
                    "command": "string",
                    "arguments": "string"
                }
            },
            "list_commands": {
                "description": "List all available Claude Code commands",
                "parameters": {}
            }
        }
    }
    
    output.write_text(json.dumps(config, indent=2))
    typer.echo(f"✅ Generated FastMCP config: {output}")
    typer.echo("\nTo use with Claude Code:")
    typer.echo(f"  1. Add this config to your MCP settings")
    typer.echo(f"  2. The bridge will be available as MCP tools")
    typer.echo(f"  3. Claude can create/manage slash commands via MCP")


if __name__ == "__main__":
    app()