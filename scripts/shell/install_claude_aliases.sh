#!/bin/bash
set -e

echo "================================================"
echo "Installing Claude Docker Aliases"
echo "================================================"
echo ""

# Function to add aliases to a shell config file
add_aliases() {
    local config_file="$1"
    local shell_name="$2"
    
    if [ -f "$config_file" ]; then
        echo "Adding Claude aliases to $config_file..."
        
        # Check if aliases already exist
        if grep -q "Claude Docker Aliases" "$config_file"; then
            echo "✅ Aliases already installed in $config_file"
        else
            # Add aliases
            cat >> "$config_file" << 'EOF'

# Claude Docker Aliases
alias claude-auth='docker exec -it llm-call-claude-proxy /bin/bash -c "source /root/.bashrc && auth"'
alias claude-test='docker exec llm-call-claude-proxy /bin/bash -c "source /root/.bashrc && test-auth"'
alias claude-shell='docker exec -it llm-call-claude-proxy /bin/bash'
alias claude-status='curl -s http://localhost:3010/health | jq ".claude_authenticated, .auth_status"'

EOF
            echo "✅ Added aliases to $config_file"
            echo ""
            echo "To use the aliases in your current session, run:"
            echo "  source $config_file"
        fi
    fi
}

# Add to bash config
if [ -f "$HOME/.bashrc" ]; then
    add_aliases "$HOME/.bashrc" "bash"
fi

# Add to zsh config
if [ -f "$HOME/.zshrc" ]; then
    add_aliases "$HOME/.zshrc" "zsh"
fi

echo ""
echo "Available aliases:"
echo "  • claude-auth   - Authenticate Claude in Docker"
echo "  • claude-test   - Test Claude authentication"
echo "  • claude-shell  - Open shell in Claude container"
echo "  • claude-status - Check authentication status"
echo ""
echo "================================================"
echo ""

# Detect current shell and suggest reload
if [ -n "$ZSH_VERSION" ]; then
    echo "To use the aliases now, run: source ~/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    echo "To use the aliases now, run: source ~/.bashrc"
fi