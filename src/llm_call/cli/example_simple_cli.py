"""
Module: example_simple_cli.py
Description: Functions for example simple cli operations

External Dependencies:
- typer: [Documentation URL]
- llm_call: [Documentation URL]

Sample Input:
>>> # Add specific examples based on module functionality

Expected Output:
>>> # Add expected output examples

Example Usage:
>>> # Add usage examples
"""

#!/usr/bin/env python3
"""
Example: Simple CLI with one-line slash/MCP integration

This demonstrates how ANY Typer CLI can get slash commands and MCP support
with a single line of code.
"""

import typer
from pathlib import Path
from llm_call.cli.slash_mcp_mixin import add_slash_mcp_commands

# Create your CLI as normal
app = typer.Typer(name="example-cli", help="Example CLI with auto slash/MCP")

# YOUR NORMAL CLI COMMANDS
@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to analyze"),
    recursive: bool = typer.Option(True, "--recursive", "-r")
):
    """Analyze files in the given path."""
    typer.echo(f" Analyzing: {path}")
    if recursive:
        typer.echo("   Including subdirectories")
    # Your analysis logic here
    typer.echo(" Analysis complete!")

@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input file"),
    output_format: str = typer.Option("json", "--format", "-f")
):
    """Convert file to different format."""
    typer.echo(f" Converting {input_file} to {output_format}")
    # Your conversion logic here
    typer.echo(f" Converted to {output_format}")

# THIS IS THE MAGIC LINE - adds slash commands and MCP support!
add_slash_mcp_commands(app)

if __name__ == "__main__":
    app()