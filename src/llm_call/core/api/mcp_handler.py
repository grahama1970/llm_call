"""
MCP (Multi-Claude Protocol) configuration handler.

This module manages dynamic MCP configuration for Claude CLI tools.

Links:
- MCP documentation: (internal/proprietary)

Sample usage:
    mcp_path = write_mcp_config(workspace_dir, mcp_config)
    # ... run Claude CLI ...
    remove_mcp_config(mcp_path)

Expected output:
    Temporary .mcp.json file created and cleaned up
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger


# Default MCP configuration with all available tools
DEFAULT_ALL_TOOLS_MCP_CONFIG = {
    "mcpServers": {
        "perplexity-ask": {
            "command": "npm",
            "args": ["run", "dev"],
            "env": {"PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY_FOR_MCP", "")},
            "description": "Perplexity search tool for research queries",
            "version": "1.0.0"
        },
        "web-search": {
            "command": "npm",
            "args": ["run", "dev"],
            "description": "General web search capabilities",
            "version": "1.0.0"
        },
        "brave-search": {
            "command": "npm",
            "args": ["run", "dev"],
            "env": {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY_FOR_MCP", "")},
            "description": "Brave search engine integration",
            "version": "1.0.0"
        },
        "github": {
            "command": "npm",
            "args": ["run", "dev"],
            "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN_FOR_MCP", None)},
            "description": "GitHub repository access and operations",
            "version": "1.0.0"
        },
        "desktop-commander": {
            "command": "npm",
            "args": ["run", "dev"],
            "env": {
                "MCP_CLAUDE_DEBUG": "true",
                "MCP_HEARTBEAT_INTERVAL_MS": "15000",
                "MCP_EXECUTION_TIMEOUT_MS": "1800000",
                "MCP_USE_ROOMODES": "true",
                "MCP_WATCH_ROOMODES": "true",
                "MCP_MAX_RETRIES": "3",
                "MCP_RETRY_DELAY_MS": "1000",
                "MCP_DEFAULT_TASK_EXECUTION_MODE": "sequential"
            },
            "description": "Enhanced desktop automation and file operations",
            "version": "1.0.0"
        },
        "context7": {
            "command": "npm",
            "args": ["run", "dev"],
            "description": "Context7 documentation integration",
            "version": "1.0.0"
        }
    }
}


def write_mcp_config(target_dir: Path, mcp_config: Optional[Dict[str, Any]] = None) -> Path:
    """
    Write MCP configuration to .mcp.json in target directory.
    
    Args:
        target_dir: Directory to write .mcp.json to
        mcp_config: MCP configuration dict. If None, uses DEFAULT_ALL_TOOLS_MCP_CONFIG
        
    Returns:
        Path to written .mcp.json file
        
    Raises:
        IOError: If unable to write file
    """
    config_to_write = mcp_config or DEFAULT_ALL_TOOLS_MCP_CONFIG
    mcp_json_path = target_dir / ".mcp.json"
    
    try:
        with open(mcp_json_path, 'w', encoding='utf-8') as f:
            json.dump(config_to_write, f, indent=2)
        
        tools_list = list(config_to_write.get('mcpServers', {}).keys())
        logger.info(f"Wrote MCP config to '{mcp_json_path}' with tools: {tools_list}")
        return mcp_json_path
        
    except Exception as e:
        logger.error(f"Failed to write MCP config to '{mcp_json_path}': {e}")
        raise IOError(f"Could not write MCP configuration: {e}")


def remove_mcp_config(mcp_json_path: Path) -> None:
    """
    Remove MCP configuration file.
    
    Args:
        mcp_json_path: Path to .mcp.json file to remove
    """
    try:
        if mcp_json_path.exists():
            mcp_json_path.unlink()
            logger.info(f"Removed MCP config from '{mcp_json_path}'")
    except Exception as e:
        logger.warning(f"Failed to remove MCP config '{mcp_json_path}': {e}")


def get_tool_config(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get configuration for a specific MCP tool.
    
    Args:
        tool_name: Name of the tool (e.g., "perplexity-ask")
        
    Returns:
        Tool configuration dict or None if not found
    """
    return DEFAULT_ALL_TOOLS_MCP_CONFIG.get("mcpServers", {}).get(tool_name)


def build_selective_mcp_config(tool_names: List[str]) -> Dict[str, Any]:
    """
    Build MCP configuration with only selected tools.
    
    Args:
        tool_names: List of tool names to include
        
    Returns:
        MCP configuration dict with only requested tools
    """
    selective_config = {"mcpServers": {}}
    
    for tool_name in tool_names:
        tool_config = get_tool_config(tool_name)
        if tool_config:
            selective_config["mcpServers"][tool_name] = tool_config
        else:
            logger.warning(f"Tool '{tool_name}' not found in default MCP configuration")
    
    return selective_config


if __name__ == "__main__":
    # Test MCP handler
    import tempfile
    
    print("Testing MCP configuration handler...")
    
    # Test writing default config
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Write default config
        mcp_path = write_mcp_config(tmppath)
        print(f"✅ Wrote default MCP config to: {mcp_path}")
        
        # Check it exists
        assert mcp_path.exists()
        with open(mcp_path) as f:
            config = json.load(f)
        print(f"✅ Config has {len(config.get('mcpServers', {}))} tools")
        
        # Remove it
        remove_mcp_config(mcp_path)
        assert not mcp_path.exists()
        print("✅ Successfully removed MCP config")
    
    # Test selective config
    selective = build_selective_mcp_config(["perplexity-ask", "github"])
    print(f"✅ Built selective config with tools: {list(selective['mcpServers'].keys())}")
    
    print("\n✅ All MCP handler tests passed!")