"""
claude_max_proxy FastMCP Server

Granger standard MCP server implementation for claude_max_proxy.
"""

from fastmcp import FastMCP
from .claude_max_proxy_prompts import register_all_prompts
from .prompts import get_prompt_registry

# Initialize server
mcp = FastMCP("claude_max_proxy")
mcp.description = "claude_max_proxy - Granger spoke module"

# Register prompts
register_all_prompts()
prompt_registry = get_prompt_registry()


# =============================================================================
# PROMPTS - Required for Granger standard
# =============================================================================

@mcp.prompt()
async def capabilities() -> str:
    """List all MCP server capabilities"""
    return await prompt_registry.execute("claude_max_proxy:capabilities")


@mcp.prompt()
async def help(context: str = None) -> str:
    """Get context-aware help"""
    return await prompt_registry.execute("claude_max_proxy:help", context=context)


@mcp.prompt()
async def quick_start() -> str:
    """Quick start guide for new users"""
    return await prompt_registry.execute("claude_max_proxy:quick-start")


# =============================================================================
# TOOLS - Add your existing tools here
# =============================================================================

# TODO: Migrate existing tools from your current implementation
# Example:
# @mcp.tool()
# async def your_tool(param: str) -> dict:
#     """Tool description"""
#     return {"success": True, "result": param}


# =============================================================================
# SERVER
# =============================================================================

def serve():
    """Start the MCP server"""
    mcp.run(transport="stdio")  # Use stdio for Claude Code


if __name__ == "__main__":
    # Quick validation
    import asyncio
    
    async def validate():
        result = await capabilities()
        assert "claude_max_proxy" in result.lower()
        print("✅ Server validation passed")
    
    asyncio.run(validate())
    
    # Start server
    serve()
