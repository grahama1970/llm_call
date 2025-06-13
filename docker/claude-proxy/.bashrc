#!/bin/bash
# Claude Docker Container Shell Configuration

# Add some helpful aliases
alias auth='claude auth login'
alias test-auth='claude api "Say hello" --output json 2>&1 | grep -q "hello" && echo "✅ Authenticated" || echo "❌ Not authenticated"'

# Claude-skip function from host ~/.zshrc
claude-skip() {
  claude --dangerously-skip-permissions "$@"
}

# Show authentication status on login
echo "================================================"
echo "🤖 Claude CLI Proxy Container"
echo "================================================"
echo ""

# Check authentication
if [ -f "/root/.claude/.credentials.json" ]; then
    echo "✅ Credentials file found"
    # Quick test to see if actually authenticated
    if claude api "test" --output json 2>&1 | grep -q "not authenticated"; then
        echo "⚠️  Credentials expired or invalid"
        echo ""
        echo "To authenticate, run: auth"
    else
        echo "✅ Claude is authenticated and ready!"
    fi
else
    echo "❌ Not authenticated"
    echo ""
    echo "To authenticate, run one of:"
    echo "  • auth          (shortcut for claude auth login)"
    echo "  • claude auth login"
    echo "  • claude        (launch Claude Code)"
fi

echo ""
echo "Helpful commands:"
echo "  • auth         - Authenticate with Claude"
echo "  • test-auth    - Test authentication status"
echo "  • claude       - Launch Claude Code"
echo "  • claude-skip  - Run Claude with --dangerously-skip-permissions"
echo "  • exit         - Leave container"
echo ""
echo "================================================"
echo ""

# Keep default bash prompt
PS1='claude-proxy:\w\$ '