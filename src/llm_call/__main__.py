#!/usr/bin/env python3
"""
Entry point for running llm_call as a module with python -m llm_call

This enables commands like:
- python -m llm_call ask "What is Python?"
- python -m llm_call models
- python -m llm_call chat
"""

import sys
from llm_call.cli.main import app

if __name__ == "__main__":
    # Remove the module name from sys.argv since typer expects
    # the script name to be argv[0]
    if len(sys.argv) > 0 and sys.argv[0].endswith("__main__.py"):
        sys.argv[0] = "llm_call"
    
    app()