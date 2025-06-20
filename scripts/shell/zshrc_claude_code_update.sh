#!/bin/bash
# claude-skip function using ~/.claude/claude_code/.mcp.json

cat << 'EOF'
# Update your ~/.zshrc with this version:

claude-skip() {
    local mcp_config="$HOME/.claude/claude_code/.mcp.json"
    if [ -f "$mcp_config" ]; then
        echo "🚀 Loading MCP servers from ~/.claude/claude_code/.mcp.json"
        claude --dangerously-skip-permissions --mcp-config "$mcp_config" "$@"
    else
        claude --dangerously-skip-permissions "$@"
    fi
}

# After updating ~/.zshrc:
# source ~/.zshrc
EOF