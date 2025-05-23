#!/usr/bin/env python3
"""
Claude Code Slash Command Bridge - Proof of Concept
This demonstrates how to create and manage Claude Code slash commands from a Typer CLI
"""

import typer
from pathlib import Path
import subprocess
import json
import sys
from typing import Optional, List
from datetime import datetime

app = typer.Typer(help="Claude Code Slash Command Manager")

# Configuration
CLAUDE_COMMANDS_DIR = Path(".claude/commands")
GLOBAL_COMMANDS_DIR = Path.home() / ".claude/commands"
COMMAND_TEMPLATE = """# Auto-generated Claude Code command: {name}
# Generated at: {timestamp}
# Description: {description}

{content}
"""

# Store command metadata
METADATA_FILE = Path(".claude_command_metadata.json")


def load_metadata():
    """Load command metadata from JSON file"""
    if METADATA_FILE.exists():
        return json.loads(METADATA_FILE.read_text())
    return {}


def save_metadata(metadata):
    """Save command metadata to JSON file"""
    METADATA_FILE.write_text(json.dumps(metadata, indent=2))


@app.command()
def create(
    name: str = typer.Argument(..., help="Command name (without /project: prefix)"),
    description: str = typer.Option("Custom command", help="Command description"),
    content: str = typer.Option(None, help="Command content (or use stdin)"),
    global_command: bool = typer.Option(False, "--global", "-g", help="Create as global command"),
    typer_command: str = typer.Option(None, "--from-typer", help="Generate from existing Typer command")
):
    """Create a new Claude Code slash command"""
    
    # Determine target directory
    target_dir = GLOBAL_COMMANDS_DIR if global_command else CLAUDE_COMMANDS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate command content
    if typer_command:
        # Convert Typer command to Claude Code command
        content = f"""Execute Python Typer command with arguments: $ARGUMENTS

```bash
python {typer_command} $ARGUMENTS
```

This command wraps the Typer CLI command '{typer_command}'.
"""
    elif content is None:
        # Read from stdin if no content provided
        typer.echo("Enter command content (Ctrl+D when done):")
        content = sys.stdin.read()
    
    # Ensure $ARGUMENTS placeholder is included
    if "$ARGUMENTS" not in content:
        content += "\n\nArguments: $ARGUMENTS"
    
    # Create command file
    command_file = target_dir / f"{name}.md"
    command_content = COMMAND_TEMPLATE.format(
        name=name,
        timestamp=datetime.now().isoformat(),
        description=description,
        content=content
    )
    
    command_file.write_text(command_content)
    
    # Update metadata
    metadata = load_metadata()
    metadata[name] = {
        "description": description,
        "created": datetime.now().isoformat(),
        "global": global_command,
        "typer_command": typer_command
    }
    save_metadata(metadata)
    
    scope = "global" if global_command else "project"
    typer.echo(f"✅ Created {scope} command: /{'project:' if not global_command else ''}{name}")
    typer.echo(f"   File: {command_file}")


@app.command()
def list(
    global_only: bool = typer.Option(False, "--global", "-g", help="List only global commands"),
    local_only: bool = typer.Option(False, "--local", "-l", help="List only local commands")
):
    """List all available Claude Code commands"""
    
    metadata = load_metadata()
    commands_found = False
    
    # List local commands
    if not global_only and CLAUDE_COMMANDS_DIR.exists():
        typer.echo("📁 Project Commands:")
        for cmd_file in CLAUDE_COMMANDS_DIR.glob("*.md"):
            name = cmd_file.stem
            info = metadata.get(name, {})
            desc = info.get("description", "No description")
            typer.echo(f"  /project:{name} - {desc}")
            commands_found = True
    
    # List global commands
    if not local_only and GLOBAL_COMMANDS_DIR.exists():
        typer.echo("\n🌍 Global Commands:")
        for cmd_file in GLOBAL_COMMANDS_DIR.glob("*.md"):
            name = cmd_file.stem
            info = metadata.get(name, {})
            desc = info.get("description", "No description")
            typer.echo(f"  /{name} - {desc}")
            commands_found = True
    
    if not commands_found:
        typer.echo("No commands found. Create one with 'python slashcli.py create'")


@app.command()
def execute(
    command: str = typer.Argument(..., help="Command name to execute"),
    arguments: str = typer.Argument("", help="Arguments to pass to the command"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="Show command without executing")
):
    """Execute a Claude Code slash command"""
    
    # Check if command exists
    local_cmd = CLAUDE_COMMANDS_DIR / f"{command}.md"
    global_cmd = GLOBAL_COMMANDS_DIR / f"{command}.md"
    
    if local_cmd.exists():
        full_command = f"/project:{command} {arguments}".strip()
    elif global_cmd.exists():
        full_command = f"/{command} {arguments}".strip()
    else:
        typer.echo(f"❌ Command '{command}' not found", err=True)
        raise typer.Exit(1)
    
    if dry_run:
        typer.echo(f"Would execute: claude-code -x \"{full_command}\"")
        return
    
    # Execute via Claude Code CLI
    try:
        typer.echo(f"🚀 Executing: {full_command}")
        subprocess.run(["claude-code", "-x", full_command], check=True)
    except subprocess.CalledProcessError as e:
        typer.echo(f"❌ Command failed: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo("❌ claude-code CLI not found. Please install Claude Code first.", err=True)
        raise typer.Exit(1)


@app.command()
def delete(
    name: str = typer.Argument(..., help="Command name to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Delete without confirmation")
):
    """Delete a Claude Code command"""
    
    # Find command file
    local_cmd = CLAUDE_COMMANDS_DIR / f"{name}.md"
    global_cmd = GLOBAL_COMMANDS_DIR / f"{name}.md"
    
    cmd_file = None
    if local_cmd.exists():
        cmd_file = local_cmd
        scope = "project"
    elif global_cmd.exists():
        cmd_file = global_cmd
        scope = "global"
    else:
        typer.echo(f"❌ Command '{name}' not found", err=True)
        raise typer.Exit(1)
    
    # Confirm deletion
    if not force:
        confirm = typer.confirm(f"Delete {scope} command '{name}'?")
        if not confirm:
            typer.echo("Cancelled")
            raise typer.Exit(0)
    
    # Delete file
    cmd_file.unlink()
    
    # Update metadata
    metadata = load_metadata()
    if name in metadata:
        del metadata[name]
        save_metadata(metadata)
    
    typer.echo(f"✅ Deleted {scope} command: {name}")


@app.command()
def template(
    name: str = typer.Argument(..., help="Template name"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path")
):
    """Generate common command templates"""
    
    templates = {
        "git-commit": {
            "description": "Create a git commit with conventional commit format",
            "content": """Generate a git commit message for the following changes: $ARGUMENTS

Use conventional commit format (feat:, fix:, docs:, etc.)
Include a descriptive subject line and body if needed.
Then execute the commit with:
```bash
git add -A && git commit -m "<generated message>"
```"""
        },
        "test-runner": {
            "description": "Run tests with coverage",
            "content": """Run tests for: $ARGUMENTS

1. Identify the test framework (pytest, unittest, etc.)
2. Run tests with coverage enabled
3. Show coverage report
4. Highlight any failing tests

```bash
pytest $ARGUMENTS -v --cov --cov-report=term-missing
```"""
        },
        "code-review": {
            "description": "Perform code review on files",
            "content": """Please review the following code: $ARGUMENTS

Check for:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Security vulnerabilities
5. Suggestions for improvement

Provide specific, actionable feedback."""
        },
        "typer-wrapper": {
            "description": "Wrapper for Typer CLI commands",
            "content": """Execute Typer CLI command: $ARGUMENTS

This is a generic wrapper for Typer-based commands.
Replace 'your_script.py' with your actual script name.

```bash
python your_script.py $ARGUMENTS
```"""
        }
    }
    
    if name not in templates:
        typer.echo(f"Available templates: {', '.join(templates.keys())}")
        raise typer.Exit(1)
    
    template_data = templates[name]
    
    if output:
        # Save to file
        output.write_text(template_data["content"])
        typer.echo(f"✅ Template saved to: {output}")
    else:
        # Print to stdout
        typer.echo(f"\n--- Template: {name} ---")
        typer.echo(f"Description: {template_data['description']}\n")
        typer.echo(template_data["content"])


@app.command()
def sync(
    typer_script: Path = typer.Argument(..., help="Path to your Typer CLI script"),
    prefix: str = typer.Option("cli", help="Prefix for generated commands")
):
    """Auto-generate Claude Code commands from a Typer CLI script"""
    
    import ast
    import inspect
    
    try:
        # Parse the Python file
        with open(typer_script) as f:
            tree = ast.parse(f.read())
        
        # Find Typer commands
        commands_created = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's decorated with @app.command()
                for decorator in node.decorator_list:
                    if (isinstance(decorator, ast.Call) and 
                        isinstance(decorator.func, ast.Attribute) and
                        decorator.func.attr == "command"):
                        
                        # Create Claude Code command
                        cmd_name = f"{prefix}-{node.name}"
                        cmd_content = f"""Execute Typer command: {node.name} with arguments: $ARGUMENTS

```bash
python {typer_script} {node.name} $ARGUMENTS
```

Auto-generated from Typer CLI command."""
                        
                        # Get docstring if available
                        docstring = ast.get_docstring(node)
                        if docstring:
                            cmd_content = f"{docstring}\n\n{cmd_content}"
                        
                        create(
                            name=cmd_name,
                            description=f"Wrapper for {node.name} command",
                            content=cmd_content,
                            typer_command=f"{typer_script} {node.name}"
                        )
                        commands_created += 1
        
        typer.echo(f"\n✅ Created {commands_created} commands from {typer_script}")
        
    except Exception as e:
        typer.echo(f"❌ Error parsing Typer script: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()