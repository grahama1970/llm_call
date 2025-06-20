#!/bin/bash
set -e

echo "Starting Claude Proxy Server..."
echo ""
echo "================================================"
echo "Claude CLI Proxy Server v1.0"
echo "================================================"

# Ensure Claude working directories exist with correct permissions
echo "Setting up Claude CLI directories..."
for dir in /home/claude/.claude/projects /home/claude/.claude/cache /home/claude/.claude/logs /home/claude/.claude/tmp; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
    fi
    chown -R claude:claude "$dir" 2>/dev/null || true
    chmod 755 "$dir" 2>/dev/null || true
done

# Fix permissions for the entire .claude directory
chown -R claude:claude /home/claude/.claude 2>/dev/null || true
chmod -R 755 /home/claude/.claude 2>/dev/null || true

# Ensure the workspace directory exists and has correct permissions
if [ ! -d "/home/claude/.claude_workspace" ]; then
    mkdir -p /home/claude/.claude_workspace
fi
chown -R claude:claude /home/claude/.claude_workspace 2>/dev/null || true

# Check if Claude credentials exist
if [ -f "/home/claude/.claude/.credentials.json" ]; then
    echo "✅ Claude credentials found"
    # Ensure credentials are readable by claude user
    chmod 644 /home/claude/.claude/.credentials.json 2>/dev/null || true
    chown claude:claude /home/claude/.claude/.credentials.json 2>/dev/null || true
    
    # Handle session file
    if [ -f "/home/claude/.claude/session.json" ]; then
        chmod 644 /home/claude/.claude/session.json 2>/dev/null || true
        chown claude:claude /home/claude/.claude/session.json 2>/dev/null || true
    else
        # Create empty session file if it doesn't exist
        touch /home/claude/.claude/session.json
        chown claude:claude /home/claude/.claude/session.json
        chmod 644 /home/claude/.claude/session.json
    fi
    
    echo ""
    echo "Authentication status available at:"
    echo "  http://localhost:3010/health"
else
    echo "⚠️  No Claude credentials found"
    echo ""
    echo "IMPORTANT: To use Claude Max/Opus models, authenticate first:"
    echo ""
    echo "  Option 1 (Recommended):"
    echo "    From your host machine, run: ./docker/claude-proxy/authenticate.sh"
    echo ""
    echo "  Option 2 (Manual):"
    echo "    docker exec -it llm-call-claude-proxy /bin/zsh"
    echo "    claude  # Launch Claude Code and authenticate"
    echo ""
    echo "Starting proxy server anyway (requests will fail until authenticated)..."
fi

echo "================================================"
echo ""

# Create a symlink for easier access to projects
ln -sf /home/claude/.claude/projects /home/claude/projects 2>/dev/null || true

# Unset ANTHROPIC_API_KEY to force OAuth usage
unset ANTHROPIC_API_KEY

# Set HOME explicitly for claude user
export HOME=/home/claude

echo "Starting proxy server on port 3010..."
# Switch to claude user and run the server using uvicorn
exec su -s /bin/bash claude -c "cd /home/claude && uvicorn llm_call.core.api.main:app --host 0.0.0.0 --port 3010"