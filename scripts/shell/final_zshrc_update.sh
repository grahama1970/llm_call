#!/bin/bash
# Final claude-skip function using ~/.mcp.json

cat << 'EOF'
# Update your ~/.zshrc with this simpler version:

claude-skip() {
    if [ -f "$HOME/.mcp.json" ]; then
        echo "🚀 Loading MCP servers from ~/.mcp.json"
        claude --dangerously-skip-permissions --mcp-config ~/.mcp.json "$@"
    else
        claude --dangerously-skip-permissions "$@"
    fi
}

# After updating ~/.zshrc:
# source ~/.zshrc
EOF