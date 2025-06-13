#!/bin/bash
set -e

echo "Starting Claude Proxy Server..."
echo ""
echo "================================================"
echo "Claude CLI Proxy Server v1.0"
echo "================================================"

# Fix permissions for mounted volume (if we can)
if [ -d "/home/claude/.claude" ]; then
    # Try to fix permissions - this will only work if we have the capability
    find /home/claude/.claude -type d -exec chmod 755 {} \; 2>/dev/null || true
    find /home/claude/.claude -type f -exec chmod 644 {} \; 2>/dev/null || true
    # Try to fix ownership for new files
    find /home/claude/.claude -user root -exec chown claude:claude {} \; 2>/dev/null || true
fi

# Check if Claude credentials exist
if [ -f "/home/claude/.claude/.credentials.json" ]; then
    echo "✅ Claude credentials found"
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

# Unset ANTHROPIC_API_KEY to force OAuth usage
unset ANTHROPIC_API_KEY

echo "Starting proxy server on port 3010..."
# Switch to claude user and run the server
exec su -c "python -m llm_call.proof_of_concept.poc_claude_proxy_server" claude