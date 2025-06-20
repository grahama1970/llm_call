#!/bin/bash
# Better claude-skip function that works from any directory

cat << 'EOF'
# Replace your claude-skip function in ~/.zshrc with this:

claude-skip() {
    # Check for .mcp.json in current directory
    if [ -f "./.mcp.json" ]; then
        local mcp_path="$(pwd)/.mcp.json"
        echo "🚀 Loading MCP servers from ${mcp_path}"
        claude --dangerously-skip-permissions --mcp-config "$mcp_path" "$@"
    # Check for .mcp.json in llm_call project
    elif [ -f "/home/graham/workspace/experiments/llm_call/.mcp.json" ]; then
        echo "🚀 Loading MCP servers from llm_call project"
        claude --dangerously-skip-permissions --mcp-config /home/graham/workspace/experiments/llm_call/.mcp.json "$@"
    else
        claude --dangerously-skip-permissions "$@"
    fi
}

# Alternative: Always use llm_call's MCP servers
claude-skip-llm() {
    echo "🚀 Loading MCP servers from llm_call project"
    claude --dangerously-skip-permissions --mcp-config /home/graham/workspace/experiments/llm_call/.mcp.json "$@"
}

# After updating ~/.zshrc:
# source ~/.zshrc
EOF