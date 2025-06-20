#!/bin/bash
# Updated claude-skip function for ~/.zshrc that auto-includes MCP config

cat << 'EOF'
# Add this updated function to your ~/.zshrc file:

claude-skip() {
  if [ -f "./.mcp.json" ]; then
    echo "🚀 Loading MCP servers from ./.mcp.json"
    claude --dangerously-skip-permissions --mcp-config ./.mcp.json "$@"
  else
    claude --dangerously-skip-permissions "$@"
  fi
}

# Alternative version that always checks for .mcp.json in current and parent directories:
claude-skip-smart() {
  local mcp_file=""
  
  # Check current directory
  if [ -f "./.mcp.json" ]; then
    mcp_file="./.mcp.json"
  # Check parent directory
  elif [ -f "../.mcp.json" ]; then
    mcp_file="../.mcp.json"
  # Check two levels up
  elif [ -f "../../.mcp.json" ]; then
    mcp_file="../../.mcp.json"
  fi
  
  if [ -n "$mcp_file" ]; then
    echo "🚀 Loading MCP servers from $mcp_file"
    claude --dangerously-skip-permissions --mcp-config "$mcp_file" "$@"
  else
    claude --dangerously-skip-permissions "$@"
  fi
}

# After adding to ~/.zshrc, run:
# source ~/.zshrc
EOF