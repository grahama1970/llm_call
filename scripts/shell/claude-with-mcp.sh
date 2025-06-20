#!/bin/bash
# Script to start Claude Code with MCP servers loaded from .mcp.json

MCP_CONFIG_FILE="./.mcp.json"

if [ ! -f "$MCP_CONFIG_FILE" ]; then
    echo "❌ Error: $MCP_CONFIG_FILE not found"
    exit 1
fi

echo "🚀 Starting Claude Code with MCP servers from $MCP_CONFIG_FILE"
echo "📋 Available servers:"
cat "$MCP_CONFIG_FILE" | jq -r '.mcpServers | keys[]' 2>/dev/null || echo "Could not parse servers"

echo ""
echo "⚠️  Use this command to start Claude Code with MCP servers:"
echo ""
echo "claude --mcp-config $MCP_CONFIG_FILE"
echo ""
echo "Or for a specific task:"
echo "claude --mcp-config $MCP_CONFIG_FILE \"your prompt here\""