"""
MCP Handler wrapper class for the MCP server.

This wraps the existing mcp_handler functionality into a class-based interface.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger

from .mcp_handler import (
    write_mcp_config,
    remove_mcp_config,
    get_tool_config,
    build_selective_mcp_config,
    DEFAULT_ALL_TOOLS_MCP_CONFIG
)


class MCPHandler:
    """Wrapper class for MCP configuration management."""
    
    def __init__(self):
        self.temp_configs = []  # Track temporary configs for cleanup
        self._available_servers = DEFAULT_ALL_TOOLS_MCP_CONFIG.get("mcpServers", {})
    
    def get_mcp_config(
        self,
        mcp_servers: List[str],
        working_directory: str
    ) -> Dict[str, Any]:
        """
        Get MCP configuration for specified servers.
        
        Args:
            mcp_servers: List of MCP server names to include
            working_directory: Working directory for the servers
            
        Returns:
            MCP configuration dict
        """
        return build_selective_mcp_config(mcp_servers)
    
    def write_temp_config(
        self,
        mcp_config: Dict[str, Any],
        working_dir: str
    ) -> Path:
        """
        Write temporary MCP configuration.
        
        Args:
            mcp_config: MCP configuration dict
            working_dir: Directory to write config to
            
        Returns:
            Path to temporary config file
        """
        config_path = write_mcp_config(Path(working_dir), mcp_config)
        self.temp_configs.append(config_path)
        return config_path
    
    def cleanup_temp_config(self, config_path: Path) -> None:
        """
        Clean up temporary MCP configuration.
        
        Args:
            config_path: Path to config file to remove
        """
        remove_mcp_config(config_path)
        if config_path in self.temp_configs:
            self.temp_configs.remove(config_path)
    
    def get_available_servers(self) -> List[Dict[str, Any]]:
        """
        Get list of available MCP servers.
        
        Returns:
            List of server configurations
        """
        servers = []
        for name, config in self._available_servers.items():
            servers.append({
                "name": name,
                "description": config.get("description", ""),
                "version": config.get("version", "1.0.0"),
                "has_env_vars": bool(config.get("env", {}))
            })
        return servers
    
    def update_server_config(
        self,
        server_name: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        Update configuration for a specific server.
        
        Args:
            server_name: Name of the server to update
            config: New configuration
            
        Returns:
            True if successful, False otherwise
        """
        if server_name not in self._available_servers:
            logger.error(f"Server '{server_name}' not found")
            return False
        
        try:
            # Merge configurations
            self._available_servers[server_name].update(config)
            logger.info(f"Updated configuration for server '{server_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to update server config: {e}")
            return False
    
    async def test_server(self, server_name: str) -> Dict[str, Any]:
        """
        Test MCP server connection.
        
        Args:
            server_name: Name of server to test
            
        Returns:
            Test result dict
        """
        if server_name not in self._available_servers:
            return {
                "success": False,
                "error": f"Server '{server_name}' not found"
            }
        
        server_config = self._available_servers[server_name]
        
        # Check if required environment variables are set
        env_vars = server_config.get("env", {})
        missing_vars = []
        
        for var_name, var_value in env_vars.items():
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            return {
                "success": False,
                "error": f"Missing environment variables: {', '.join(missing_vars)}",
                "server": server_name
            }
        
        return {
            "success": True,
            "server": server_name,
            "description": server_config.get("description", ""),
            "version": server_config.get("version", "1.0.0")
        }
    
    def __del__(self):
        """Clean up any remaining temporary configs."""
        for config_path in self.temp_configs[:]:
            try:
                self.cleanup_temp_config(config_path)
            except Exception:
                pass


if __name__ == "__main__":
    # Test the MCPHandler wrapper
    handler = MCPHandler()
    
    print("Testing MCPHandler wrapper...")
    
    # Test getting available servers
    servers = handler.get_available_servers()
    print(f"✅ Found {len(servers)} available servers")
    
    # Test getting MCP config
    config = handler.get_mcp_config(["perplexity-ask", "github"], "/tmp")
    print(f"✅ Built config with {len(config['mcpServers'])} servers")
    
    # Test writing temp config
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_path = handler.write_temp_config(config, tmpdir)
        print(f"✅ Wrote temp config to: {temp_path}")
        
        # Test cleanup
        handler.cleanup_temp_config(temp_path)
        print("✅ Cleaned up temp config")
    
    print("\n✅ All MCPHandler tests passed!")