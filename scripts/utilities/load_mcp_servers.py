#!/usr/bin/env python3
"""
Module: load_mcp_servers.py
Description: Automatically loads all MCP servers from .mcp.json into Claude Code

External Dependencies:
- None (uses only standard library)

Sample Input:
>>> .mcp.json file with mcpServers object

Expected Output:
>>> All servers registered with Claude Code via 'claude mcp add-json' commands

Example Usage:
>>> python scripts/load_mcp_servers.py
>>> # Or to remove all first:
>>> python scripts/load_mcp_servers.py --clean
"""

import json
import subprocess
import sys
import argparse
from pathlib import Path
from typing import Dict, Any


def load_mcp_config(config_path: Path = Path(".mcp.json")) -> Dict[str, Any]:
    """Load and parse the .mcp.json configuration file."""
    if not config_path.exists():
        print(f"❌ Error: {config_path} not found")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config.get("mcpServers", {})
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        sys.exit(1)


def remove_existing_servers(servers: Dict[str, Any]) -> None:
    """Remove all existing MCP servers to avoid conflicts."""
    print("🧹 Removing existing MCP servers...")
    
    for server_name in servers.keys():
        try:
            result = subprocess.run(
                ["claude", "mcp", "remove", server_name],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✅ Removed: {server_name}")
            else:
                # Server might not exist, that's OK
                print(f"  ⏭️  Skipped: {server_name} (not found)")
        except Exception as e:
            print(f"  ⚠️  Warning: Could not remove {server_name}: {e}")


def add_mcp_server(name: str, config: Dict[str, Any]) -> bool:
    """Add a single MCP server to Claude Code."""
    # Prepare the JSON config for claude mcp add-json
    server_json = json.dumps(config)
    
    try:
        result = subprocess.run(
            ["claude", "mcp", "add-json", name, server_json, "-s", "project"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Added: {name}")
            return True
        else:
            print(f"❌ Failed to add {name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error adding {name}: {e}")
        return False


def list_current_servers() -> None:
    """List currently registered MCP servers."""
    print("\n📋 Currently registered MCP servers:")
    try:
        result = subprocess.run(
            ["claude", "mcp", "list"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            print(result.stdout)
        else:
            print("  (none)")
    except Exception as e:
        print(f"  ⚠️  Could not list servers: {e}")


def main():
    """Main function to load all MCP servers from .mcp.json."""
    parser = argparse.ArgumentParser(
        description="Load MCP servers from .mcp.json into Claude Code"
    )
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="Remove existing servers before adding new ones"
    )
    parser.add_argument(
        "--config", 
        type=Path, 
        default=Path(".mcp.json"),
        help="Path to .mcp.json file (default: ./.mcp.json)"
    )
    args = parser.parse_args()
    
    print("🚀 Loading MCP servers from .mcp.json into Claude Code")
    print("=" * 60)
    
    # Load configuration
    servers = load_mcp_config(args.config)
    
    if not servers:
        print("❌ No servers found in configuration")
        sys.exit(1)
    
    print(f"📦 Found {len(servers)} servers to register:")
    for name in servers:
        print(f"  - {name}")
    
    # Remove existing if requested
    if args.clean:
        print()
        remove_existing_servers(servers)
    
    # Add each server
    print("\n🔧 Adding MCP servers...")
    success_count = 0
    
    for name, config in servers.items():
        if add_mcp_server(name, config):
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Successfully added {success_count}/{len(servers)} servers")
    
    if success_count < len(servers):
        print(f"⚠️  {len(servers) - success_count} servers failed to add")
    
    # List current servers
    list_current_servers()
    
    if success_count == len(servers):
        print("\n🎉 All servers loaded successfully!")
        print("⚠️  Remember to restart Claude Code for the changes to take effect")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())