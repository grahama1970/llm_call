"""
Enhanced MCP Handler for better integration with the MCP server
Extends the existing MCPHandler with additional functionality
"""
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

from .mcp_handler import MCPHandler


class MCPHandlerEnhanced(MCPHandler):
    """Enhanced MCP handler with additional features for the MCP server"""
    
    def __init__(self):
        super().__init__()
        self.temp_configs = {}  # Track temporary configs for cleanup
        
    def get_available_servers(self) -> List[Dict[str, Any]]:
        """Get list of available MCP servers with their configurations"""
        servers = []
        
        # Perplexity
        servers.append({
            "name": "perplexity",
            "description": "Web search and information retrieval",
            "enabled": True,
            "command": "npx",
            "args": ["-y", "@perplexity/mcp-server-perplexity"],
            "requires_env": ["PERPLEXITY_API_KEY"]
        })
        
        # GitHub
        servers.append({
            "name": "github", 
            "description": "GitHub repository access and analysis",
            "enabled": True,
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "requires_env": ["GITHUB_PERSONAL_ACCESS_TOKEN"]
        })
        
        # Brave Search
        servers.append({
            "name": "brave_search",
            "description": "Brave search engine integration", 
            "enabled": True,
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "requires_env": ["BRAVE_API_KEY"]
        })
        
        # Filesystem
        servers.append({
            "name": "filesystem",
            "description": "Local filesystem access",
            "enabled": True,
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"],
            "config": {"rootPath": os.getcwd()}
        })
        
        # Memory
        servers.append({
            "name": "memory",
            "description": "Persistent memory/knowledge base",
            "enabled": True,
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"]
        })
        
        # Postgres (if configured)
        if os.getenv("DATABASE_URL"):
            servers.append({
                "name": "postgres",
                "description": "PostgreSQL database access",
                "enabled": True,
                "command": "npx", 
                "args": ["-y", "@modelcontextprotocol/server-postgres"],
                "requires_env": ["DATABASE_URL"]
            })
        
        return servers
    
    def get_mcp_config(
        self, 
        mcp_servers: List[str], 
        working_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build MCP configuration for specified servers"""
        config = {"mcpServers": {}}
        
        available = {s["name"]: s for s in self.get_available_servers()}
        
        for server_name in mcp_servers:
            if server_name not in available:
                continue
                
            server = available[server_name]
            
            # Build server config
            server_config = {
                "command": server["command"],
                "args": server["args"]
            }
            
            # Add environment variables if needed
            if "requires_env" in server:
                env = {}
                for env_var in server["requires_env"]:
                    value = os.getenv(env_var, "")
                    if value:
                        env[env_var] = value
                if env:
                    server_config["env"] = env
            
            # Add specific configurations
            if server_name == "filesystem" and working_directory:
                server_config["args"].extend(["--root-path", working_directory])
            
            # Add any additional config
            if "config" in server:
                server_config.update(server["config"])
            
            config["mcpServers"][server_name] = server_config
        
        return config
    
    def write_temp_config(
        self, 
        mcp_config: Dict[str, Any], 
        working_directory: str
    ) -> str:
        """Write temporary MCP config file and return path"""
        # Create temp directory if it doesn't exist
        temp_dir = Path(working_directory) / ".mcp_temp"
        temp_dir.mkdir(exist_ok=True)
        
        # Create unique temp file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.mcp.json',
            dir=str(temp_dir),
            delete=False
        )
        
        # Write config
        json.dump(mcp_config, temp_file, indent=2)
        temp_file.close()
        
        # Track for cleanup
        self.temp_configs[temp_file.name] = True
        
        return temp_file.name
    
    def cleanup_temp_config(self, config_path: str):
        """Clean up temporary MCP config file"""
        try:
            if config_path in self.temp_configs:
                os.unlink(config_path)
                del self.temp_configs[config_path]
        except Exception:
            pass  # Ignore cleanup errors
    
    def cleanup_all_temp_configs(self):
        """Clean up all temporary configs"""
        for config_path in list(self.temp_configs.keys()):
            self.cleanup_temp_config(config_path)
    
    def update_server_config(
        self, 
        server_name: str, 
        config_updates: Dict[str, Any]
    ) -> bool:
        """Update configuration for a specific MCP server"""
        # This would update persistent configuration
        # For now, just validate the server exists
        available = {s["name"]: s for s in self.get_available_servers()}
        return server_name in available
    
    async def test_server(self, server_name: str) -> Dict[str, Any]:
        """Test if an MCP server is accessible"""
        available = {s["name"]: s for s in self.get_available_servers()}
        
        if server_name not in available:
            return {
                "success": False,
                "error": f"Unknown server: {server_name}"
            }
        
        server = available[server_name]
        
        # Check required environment variables
        missing_env = []
        if "requires_env" in server:
            for env_var in server["requires_env"]:
                if not os.getenv(env_var):
                    missing_env.append(env_var)
        
        if missing_env:
            return {
                "success": False,
                "error": f"Missing environment variables: {', '.join(missing_env)}"
            }
        
        # Basic connectivity test would go here
        # For now, just return success if config is valid
        return {
            "success": True,
            "server": server_name,
            "config": server
        }
    
    def get_tool_suggestions(self, prompt: str) -> List[str]:
        """Suggest MCP tools based on the prompt content"""
        suggestions = []
        prompt_lower = prompt.lower()
        
        # Search-related keywords
        if any(word in prompt_lower for word in [
            "search", "find", "look up", "what is", "who is", 
            "latest", "news", "information about"
        ]):
            suggestions.append("perplexity")
            suggestions.append("brave_search")
        
        # GitHub-related keywords  
        if any(word in prompt_lower for word in [
            "github", "repository", "repo", "pull request", "pr",
            "issue", "commit", "branch", "code review"
        ]):
            suggestions.append("github")
        
        # File system keywords
        if any(word in prompt_lower for word in [
            "file", "directory", "folder", "read", "write",
            "create", "delete", "list files", "save"
        ]):
            suggestions.append("filesystem")
        
        # Memory/knowledge keywords
        if any(word in prompt_lower for word in [
            "remember", "recall", "previous", "earlier",
            "save this", "store", "knowledge"
        ]):
            suggestions.append("memory")
        
        # Database keywords
        if any(word in prompt_lower for word in [
            "database", "sql", "query", "table", "postgres"
        ]) and os.getenv("DATABASE_URL"):
            suggestions.append("postgres")
        
        return list(set(suggestions))  # Remove duplicates