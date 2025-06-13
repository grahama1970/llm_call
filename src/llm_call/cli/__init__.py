"""
LLM CLI Package
Module: __init__.py
Description: Package initialization and exports

This package provides a unified command-line interface for the LLM call system:

- main.py - Unified CLI with all functionality
- slash_mcp_mixin.py - Universal mixin for slash command generation

The CLI provides:
- Simple commands for quick tasks (ask, chat, models)
- Full litellm configuration support (validation, retry, etc.)
- Config file support (JSON/YAML) with CLI overrides
- Auto-generated Claude Code slash commands
- MCP server integration
"""

from .main import app
from .slash_mcp_mixin import add_slash_mcp_commands

__all__ = ["app", "add_slash_mcp_commands"]