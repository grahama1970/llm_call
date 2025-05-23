# Typer CLI → Claude Code + FastMCP Bridge 🌉

A simple, elegant approach to automatically generate Claude Code slash commands and MCP server capabilities from your existing Typer CLI applications.

## 📋 Table of Contents

- [Overview](#overview)
- [Why This Approach](#why-this-approach)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Features](#features)
- [Usage Guide](#usage-guide)
- [Code Structure](#code-structure)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## 🎯 Overview

This solution provides a minimal, elegant way to:
1. **Build your Typer CLI** (which you're doing anyway)
2. **Auto-generate Claude Code slash commands** from your CLI commands
3. **Create an MCP server** from the same codebase using FastMCP

### The Architecture

```
Your Typer CLI (single source of truth)
         │
         ├─── Auto-generates ──→ Claude Code Commands (.md files)
         │                        └── /project:command → executes CLI
         │
         └─── Serves as ──────→ MCP Server (via FastMCP)
                                  └── Tools accessible to Claude
```

## 💡 Why This Approach

### The Problem

When building CLI tools, you often want to:
- Use them in terminal (traditional CLI)
- Access them from Claude Code (slash commands)
- Expose them via MCP for AI agents

Maintaining three separate implementations leads to:
- ❌ Code duplication
- ❌ Synchronization issues
- ❌ Documentation drift
- ❌ Triple the maintenance work

### The Solution

**Write once, use everywhere:**
- ✅ Single codebase (your Typer CLI)
- ✅ Auto-generate everything else
- ✅ Always in sync
- ✅ Zero manual maintenance

### Comparison with Alternatives

| Approach | Pros | Cons |
|----------|------|------|
| **This Solution** | Single source of truth, auto-sync, minimal code | Requires initial setup |
| Manual .md files | Simple for 1-2 commands | Maintenance nightmare at scale |
| Separate implementations | Full control | 3x the work, sync issues |
| Complex frameworks | Feature-rich | Over-engineered for most use cases |

## 📦 Installation

### Prerequisites

```bash
# Python 3.8+
python --version

# Install Typer
pip install typer

# Optional: Install FastMCP for MCP server functionality
pip install fastmcp
```

### Getting Started

1. **Clone or copy the example:**
   ```bash
   wget https://raw.githubusercontent.com/your-repo/typer_claude_bridge.py
   # Or copy the code from the artifact
   ```

2. **Make it executable:**
   ```bash
   chmod +x typer_claude_bridge.py
   ```

3. **Install dependencies:**
   ```bash
   pip install typer fastmcp  # fastmcp is optional
   ```

## 🚀 Quick Start

### 1. Create Your Typer CLI

```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str = "World"):
    """Say hello to someone"""
    typer.echo(f"Hello, {name}!")

# Add the auto-generation command
@app.command()
def generate_claude():
    """Generate Claude Code commands"""
    from pathlib import Path
    
    Path(".claude/commands").mkdir(parents=True, exist_ok=True)
    
    for cmd in app.registered_commands:
        if cmd.name != "generate-claude":
            Path(f".claude/commands/{cmd.name}.md").write_text(
                f"{cmd.callback.__doc__}\n\n"
                f"```bash\npython {__file__} {cmd.name} $ARGUMENTS\n```"
            )
            print(f"✅ /project:{cmd.name}")

if __name__ == "__main__":
    app()
```

### 2. Generate Claude Commands

```bash
python your_cli.py generate-claude
```

### 3. Use in Claude Code

```
/project:hello Alice
```

That's it! 🎉

## ✨ Features

### Core Features

- **🔄 Auto-generation**: Automatically create Claude Code commands from Typer CLI
- **📝 Smart Documentation**: Extracts docstrings and parameter info
- **🎯 Zero Configuration**: Works out of the box with any Typer CLI
- **🔧 MCP Integration**: Optional FastMCP server generation
- **📦 Batch Operations**: Generate all commands with one command

### Command Generation Features

- **Preserves Documentation**: Full docstrings become command help
- **Parameter Handling**: `$ARGUMENTS` placeholder for all CLI args
- **Custom Prefixes**: Optional prefixing for command namespacing
- **Selective Generation**: Skip certain commands from generation
- **Output Control**: Specify custom output directories

### MCP Server Features

- **Automatic Tool Registration**: All CLI commands become MCP tools
- **Type Inference**: Automatically detects parameter types
- **Configuration Export**: Generate MCP config files
- **Debug Mode**: Verbose output for troubleshooting

## 📖 Usage Guide

### Basic Usage

#### Step 1: Add Generation to Your CLI

Add these two commands to your existing Typer CLI:

```python
@app.command()
def generate_claude():
    """Generate Claude Code slash commands"""
    from pathlib import Path
    
    Path(".claude/commands").mkdir(parents=True, exist_ok=True)
    
    for cmd in app.registered_commands:
        if cmd.name == "generate-claude":
            continue
            
        name = cmd.name or cmd.callback.__name__
        doc = (cmd.callback.__doc__ or f"Run {name}").strip()
        
        Path(f".claude/commands/{name}.md").write_text(
            f"{doc}\n\n```bash\npython {__file__} {name} $ARGUMENTS\n```"
        )
        print(f"✅ /project:{name}")

@app.command()
def serve_mcp():
    """Serve as MCP server"""
    from fastmcp import FastMCP
    
    mcp = FastMCP("my-cli")
    
    for cmd in app.registered_commands:
        if cmd.name not in ["generate-claude", "serve-mcp"]:
            mcp.tool(name=cmd.name)(cmd.callback)
    
    mcp.run()
```

#### Step 2: Generate Commands

```bash
# Generate Claude Code commands
python my_cli.py generate-claude

# Generate with options
python my_cli.py generate-claude --output custom/path --prefix myapp --verbose
```

#### Step 3: Use Your Commands

**In Claude Code:**
```
/project:analyze ./src --recursive
/project:format *.py --check
/project:test --coverage
```

**As MCP Server:**
```bash
# Start server
python my_cli.py serve-mcp

# Or generate config for external MCP runner
python my_cli.py generate-mcp-config
```

### Advanced Usage

#### Custom Output Directory

```bash
python my_cli.py generate-claude --output ~/global-commands/
```

#### Namespaced Commands

```bash
python my_cli.py generate-claude --prefix myapp
# Creates: /project:myapp-analyze, /project:myapp-format, etc.
```

#### MCP Configuration

```bash
# Generate MCP config file
python my_cli.py generate-mcp-config --name my-cli-server --port 6000

# Start MCP server
python my_cli.py serve-mcp --host 0.0.0.0 --port 6000 --debug
```

## 🏗️ Code Structure

### Minimal Implementation

```python
# Minimum viable implementation (15 lines)
@app.command()
def generate_claude():
    from pathlib import Path
    Path(".claude/commands").mkdir(parents=True, exist_ok=True)
    
    for cmd in app.registered_commands:
        if cmd.name != "generate-claude":
            Path(f".claude/commands/{cmd.name}.md").write_text(
                f"{cmd.callback.__doc__}\n\n"
                f"```bash\npython {__file__} {cmd.name} $ARGUMENTS\n```"
            )
```

### Full Implementation Structure

```
typer_claude_bridge.py
├── CLI Commands (your actual functionality)
│   ├── analyze()
│   ├── format()
│   ├── test()
│   └── deploy()
│
├── Generation Commands
│   ├── generate_claude()      # Creates .md files
│   ├── generate_mcp_config()  # Creates MCP config
│   └── serve_mcp()           # Runs MCP server
│
└── Main Entry Point
    └── if __name__ == "__main__"
```

### Generated File Structure

```
your-project/
├── .claude/
│   └── commands/
│       ├── analyze.md
│       ├── format.md
│       ├── test.md
│       └── deploy.md
├── mcp_config.json
└── your_cli.py
```

## 📚 Examples

### Example 1: Simple CLI Tool

```python
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def count_lines(file: Path):
    """Count lines in a file"""
    lines = file.read_text().count('\n')
    typer.echo(f"{file} has {lines} lines")

# Add generation
@app.command()
def generate_claude():
    # ... (15 line implementation from above)
```

Generated `count-lines.md`:
```markdown
Count lines in a file

```bash
python simple_cli.py count-lines $ARGUMENTS
```
```

### Example 2: Complex CLI with Multiple Commands

See the complete `typer_claude_bridge.py` example which includes:
- Multiple commands with rich parameters
- Comprehensive docstrings
- Type hints
- Optional parameters
- Boolean flags

### Example 3: MCP Integration

```python
# After adding serve_mcp command
$ python my_cli.py serve-mcp --debug

🔧 Registered 5 MCP tools
🚀 Starting MCP server: my-cli
📡 Listening on: localhost:5000

🐛 Debug mode enabled
  Registered tool: analyze
  Registered tool: format
  Registered tool: test
  Registered tool: lint
  Registered tool: deploy
```

## 🎯 Best Practices

### 1. Documentation

Always include comprehensive docstrings:

```python
@app.command()
def deploy(env: str):
    """
    Deploy application to the specified environment.
    
    Deployment process:
    1. Run pre-deployment tests
    2. Build and package application
    3. Deploy to target environment
    4. Run post-deployment health checks
    """
```

### 2. Command Naming

Use clear, action-oriented names:
- ✅ `analyze`, `format`, `test`, `deploy`
- ❌ `do_thing`, `proc`, `x`

### 3. Parameter Design

Design parameters for both CLI and Claude usage:

```python
@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive")
):
    """Analyze code in path"""
```

### 4. Error Handling

Provide clear error messages:

```python
if not path.exists():
    typer.echo(f"❌ Error: {path} not found", err=True)
    raise typer.Exit(1)
```

### 5. Version Control

```bash
# Add to .gitignore
mcp_config.json  # If generated dynamically

# Track these
.claude/commands/  # Version control for team sharing
```

## 🔧 Advanced Usage

### Integration with CI/CD

```yaml
# .github/workflows/generate-commands.yml
name: Generate Claude Commands

on:
  push:
    paths:
      - 'cli.py'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: python cli.py generate-claude
      - uses: actions/upload-artifact@v2
        with:
          name: claude-commands
          path: .claude/commands/
```

### Custom Generation Logic

```python
@app.command()
def generate_claude_custom():
    """Custom generation with filtering"""
    
    # Only generate for public commands
    public_commands = [
        cmd for cmd in app.registered_commands
        if not cmd.name.startswith("_")
    ]
    
    # Add custom metadata
    for cmd in public_commands:
        metadata = {
            "generated": datetime.now().isoformat(),
            "version": "1.0.0",
            "author": "Your Name"
        }
        # ... generate with metadata
```

### FastMCP Advanced Configuration

```python
@app.command()
def serve_mcp_advanced():
    """Advanced MCP server with middleware"""
    from fastmcp import FastMCP
    
    mcp = FastMCP("my-cli")
    
    # Add middleware
    @mcp.middleware
    async def logging_middleware(request, call_next):
        print(f"Tool called: {request.tool_name}")
        response = await call_next(request)
        print(f"Response: {response.status}")
        return response
    
    # Register tools with custom logic
    for cmd in app.registered_commands:
        # ... custom registration
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Commands not appearing in Claude Code

**Problem**: Created .md files but commands don't show up
**Solution**: 
- Ensure files are in `.claude/commands/` (project-specific) or `~/.claude/commands/` (global)
- Check file has `.md` extension
- Restart Claude Code if needed

#### 2. FastMCP import error

**Problem**: `ImportError: No module named 'fastmcp'`
**Solution**:
```bash
pip install fastmcp
```

#### 3. Arguments not passing correctly

**Problem**: `$ARGUMENTS` not being replaced
**Solution**: 
- Ensure you're using `$ARGUMENTS` (all caps)
- Check for typos in the markdown files

### Debug Mode

Run with verbose output:
```bash
python my_cli.py generate-claude --verbose
python my_cli.py serve-mcp --debug
```

## ❓ FAQ

### Q: Do I need to modify my existing Typer CLI?

**A:** Minimally. Just add the `generate_claude` command (15 lines).

### Q: Can I use this with Click instead of Typer?

**A:** The concept works, but you'd need to adapt the command introspection code for Click's API.

### Q: How do I handle complex argument types?

**A:** Claude Code passes everything as strings via `$ARGUMENTS`. Your CLI's argument parsing handles the conversion.

### Q: Can I exclude certain commands?

**A:** Yes, add them to the skip list:
```python
skip_commands = {"generate-claude", "serve-mcp", "internal-command"}
```

### Q: What about async commands?

**A:** The CLI commands can be sync. The MCP wrapper handles async conversion when needed.

### Q: How do I update commands after changes?

**A:** Just run `generate-claude` again. It overwrites existing files.

### Q: Can I customize the generated markdown?

**A:** Yes, modify the template in the `generate_claude` function:
```python
content = f"""# Custom template
{doc}

Your custom content here...
```

### Q: Is this production-ready?

**A:** The approach is production-ready. Add error handling and tests as needed for your specific use case.

## 🤝 Contributing

This is a proof-of-concept demonstrating the approach. Feel free to:
- Adapt it for your needs
- Add features like command versioning
- Create Click/Fire/Argparse variants
- Build a proper package/library

## 📄 License

This proof-of-concept is provided as-is for educational purposes. Use and modify freely for your projects.

---

## 🎯 Quick Reference

```bash
# Generate Claude commands
python my_cli.py generate-claude

# Generate with options
python my_cli.py generate-claude --output path --prefix app --verbose

# Generate MCP config
python my_cli.py generate-mcp-config --name server --port 6000

# Start MCP server  
python my_cli.py serve-mcp --host 0.0.0.0 --port 6000 --debug

# Use in Claude Code
/project:command-name arguments
```

**Remember**: The goal is simplicity. Don't over-engineer. Your Typer CLI is the single source of truth, everything else is auto-generated. 🚀