# Serve this CLI as an MCP server using FastMCP.

Serve this CLI as an MCP server using FastMCP.
    
    Allows Claude and other MCP-compatible tools to use CLI commands.

## Usage

Execute this command via the CLI:

```bash
python -m llm_call.cli.main serve_mcp $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:serve_mcp "your prompt here"

# With options:
/project:serve_mcp "prompt" --model gpt-4 --stream
```

---
*Auto-generated from LLM CLI command: serve_mcp*
