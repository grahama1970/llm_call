# Claude CLI Docker Setup Guide

This guide explains how to properly configure the Claude CLI to work within the llm_call Docker container while maintaining security.

## Problem Overview

The Claude CLI requires writable directories for:
- Project files (`~/.claude/projects/`)
- Cache data (`~/.claude/cache/`)
- Log files (`~/.claude/logs/`)
- Session management (`~/.claude/session.json`)

The original Docker setup had security restrictions that prevented Claude CLI from creating these directories.

## Solution

We've implemented a solution that:
1. Uses Docker named volumes for persistent storage
2. Properly handles file permissions
3. Maintains security while allowing necessary operations
4. Provides convenient wrapper scripts

## Setup Instructions

### 1. Apply the Fixed Configuration

```bash
# Backup current files
cp docker-compose.yml docker-compose.yml.backup
cp docker/claude-proxy/Dockerfile docker/claude-proxy/Dockerfile.backup
cp docker/claude-proxy/entrypoint.sh docker/claude-proxy/entrypoint.sh.backup

# Apply fixes
mv docker-compose.fixed.yml docker-compose.yml
mv docker/claude-proxy/Dockerfile.fixed docker/claude-proxy/Dockerfile
mv docker/claude-proxy/entrypoint.fixed.sh docker/claude-proxy/entrypoint.sh
chmod +x docker/claude-proxy/entrypoint.sh
```

### 2. Rebuild and Start the Container

```bash
# Stop existing containers
docker-compose down

# Rebuild with new configuration
docker-compose build claude-proxy

# Start the services
docker-compose up -d
```

### 3. Fix Permissions (First Time Only)

```bash
# Use the wrapper script to fix permissions
./scripts/claude-cli-wrapper.sh fix
```

### 4. Authenticate Claude CLI

If you haven't already authenticated:

```bash
# Enter the container shell
./scripts/claude-cli-wrapper.sh shell

# Inside the container, run Claude
claude

# Follow the authentication prompts
# Exit the container when done (Ctrl+D or exit)
```

## Using Claude CLI

### With the Wrapper Script (Recommended)

```bash
# Run Claude CLI commands
./scripts/claude-cli-wrapper.sh

# Show help
./scripts/claude-cli-wrapper.sh --help

# Enter interactive shell
./scripts/claude-cli-wrapper.sh shell

# View container logs
./scripts/claude-cli-wrapper.sh logs

# Fix permission issues
./scripts/claude-cli-wrapper.sh fix
```

### Direct Docker Commands

```bash
# Run Claude CLI
docker exec -it -u claude llm-call-claude-proxy claude

# Enter shell as claude user
docker exec -it -u claude llm-call-claude-proxy /bin/zsh

# Fix permissions (as root)
docker exec -u root llm-call-claude-proxy chown -R claude:claude /home/claude/.claude
```

## Key Changes Made

### 1. Docker Compose Changes
- Added named volumes for Claude's working directories
- Mounted only necessary files (credentials, session) instead of entire directory
- Added `DAC_OVERRIDE` capability for file operations
- Removed `read_only` constraint from claude-proxy service

### 2. Dockerfile Changes
- Created all necessary directories during build
- Set proper ownership and permissions
- Added workspace directories

### 3. Entrypoint Script Changes
- Creates missing directories on startup
- Fixes permissions automatically
- Handles session file creation
- Sets proper environment variables

## Security Considerations

While we've relaxed some security constraints for the Claude CLI to work:
- The container still runs as non-root user (claude)
- Only necessary capabilities are added
- Credentials are mounted read-only
- The main API service maintains strict security

## Troubleshooting

### Permission Denied Errors
```bash
# Fix permissions
./scripts/claude-cli-wrapper.sh fix
```

### Cannot Create Directory
```bash
# Ensure volumes exist
docker volume ls | grep claude

# Recreate if needed
docker-compose down -v
docker-compose up -d
```

### Authentication Issues
```bash
# Check credentials
docker exec llm-call-claude-proxy ls -la /home/claude/.claude/.credentials.json

# Re-authenticate if needed
./scripts/claude-cli-wrapper.sh shell
# Then run: claude
```

## Persistent Data

The following data persists between container restarts:
- Claude projects in `claude-projects` volume
- Cache data in `claude-cache` volume
- Logs in `claude-logs` volume
- Workspace in `claude-workspace` volume

To completely reset:
```bash
docker-compose down -v
docker-compose up -d
```

## Integration with llm_call API

The Claude proxy is available at:
- Internal: `http://claude-proxy:3010`
- External: `http://localhost:3010`

The main API service can make requests to Claude models through this proxy.