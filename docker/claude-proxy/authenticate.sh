#!/bin/bash
set -e

echo "==================================="
echo "Claude CLI Authentication Helper"
echo "==================================="
echo ""
echo "This script will help you authenticate Claude CLI in the Docker container."
echo ""

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q '^llm-call-claude-proxy$'; then
    echo "❌ Error: Claude proxy container is not running!"
    echo ""
    echo "Please start the container first:"
    echo "  docker compose up -d claude-proxy"
    exit 1
fi

echo "✅ Claude proxy container is running"
echo ""
echo "You will now be connected to the container's terminal."
echo ""
echo "To authenticate, you need to:"
echo "  1. Launch Claude Code by typing: claude"
echo "  2. In Claude Code, authenticate with your account"
echo "  3. After authentication, exit Claude Code (Ctrl+C or Cmd+C)"
echo "  4. Type 'exit' to leave the container"
echo ""
echo "Press Enter to continue..."
read -r

# Connect to container with interactive terminal (using zsh)
docker exec -it llm-call-claude-proxy /bin/zsh