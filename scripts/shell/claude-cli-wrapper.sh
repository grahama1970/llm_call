#!/bin/bash
# Claude CLI Wrapper for Docker Container
# This script provides a convenient way to use Claude CLI within the Docker container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Container name
CONTAINER="llm-call-claude-proxy"

# Function to check if container is running
check_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
        echo -e "${RED}Error: Container '${CONTAINER}' is not running.${NC}"
        echo -e "${YELLOW}Start it with: docker-compose up -d claude-proxy${NC}"
        exit 1
    fi
}

# Function to run Claude CLI command
run_claude_command() {
    docker exec -it -u claude -w /home/claude ${CONTAINER} claude "$@"
}

# Function to fix permissions inside container
fix_permissions() {
    echo -e "${YELLOW}Fixing permissions in container...${NC}"
    docker exec -u root ${CONTAINER} bash -c '
        chown -R claude:claude /home/claude/.claude
        chmod -R 755 /home/claude/.claude
        mkdir -p /home/claude/.claude/projects /home/claude/.claude/cache /home/claude/.claude/logs
        chown -R claude:claude /home/claude/.claude/projects
    '
    echo -e "${GREEN}Permissions fixed!${NC}"
}

# Function to show container logs
show_logs() {
    docker logs -f ${CONTAINER}
}

# Function to enter interactive shell
enter_shell() {
    docker exec -it -u claude -w /home/claude ${CONTAINER} /bin/zsh
}

# Main script logic
case "${1:-help}" in
    fix|fix-permissions)
        check_container
        fix_permissions
        ;;
    logs)
        show_logs
        ;;
    shell|sh)
        check_container
        enter_shell
        ;;
    help|--help|-h)
        echo "Claude CLI Docker Wrapper"
        echo ""
        echo "Usage: $0 [command] [args...]"
        echo ""
        echo "Commands:"
        echo "  fix, fix-permissions    Fix file permissions in the container"
        echo "  logs                    Show container logs"
        echo "  shell, sh              Enter interactive shell in container"
        echo "  help                   Show this help message"
        echo "  [claude args...]       Pass arguments directly to Claude CLI"
        echo ""
        echo "Examples:"
        echo "  $0                     Run Claude CLI interactively"
        echo "  $0 fix                 Fix permissions issues"
        echo "  $0 shell               Enter container shell"
        echo "  $0 --help              Show Claude CLI help"
        ;;
    *)
        check_container
        run_claude_command "$@"
        ;;
esac