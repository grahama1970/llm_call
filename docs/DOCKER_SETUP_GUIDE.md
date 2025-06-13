# Docker Setup Guide for llm_call

## Quick Start

### 1. Basic Setup (Claude Proxy Only)

This is the current setup - just the Claude proxy containerized:

```bash
# Start Claude proxy and Redis
docker-compose up -d claude-proxy redis

# Check status
docker-compose ps

# View logs
docker-compose logs -f claude-proxy
```

### 2. Full Container Setup

To run the entire llm_call stack in containers:

```bash
# Create GRANGER network (one time)
docker network create granger-network

# Start all services
docker-compose -f docker-compose.full.yml up -d

# With GPU support for Ollama
docker-compose -f docker-compose.full.yml --profile gpu up -d

# Development mode with Redis Commander
docker-compose -f docker-compose.full.yml --profile dev up -d
```

## Authentication

### Claude CLI Authentication

If using Claude Max (OAuth):

```bash
# Enter the Claude proxy container
docker exec -it llm-call-claude-proxy /bin/bash

# Inside container, authenticate
claude /login

# Follow prompts to complete OAuth
```

## Environment Variables

Create a `.env` file with your API keys:

```bash
# LLM Provider Keys
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  # If using API instead of Claude Max

# Tool Keys
PERPLEXITY_API_KEY=your_key_here
BRAVE_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here

# Service Configuration
REDIS_URL=redis://redis:6379
CLAUDE_PROXY_URL=http://claude-proxy:3010
```

## Development Workflow

### Hot Reload Setup

For development with hot code reload:

1. Edit `docker-compose.full.yml`
2. Uncomment the development volume mount
3. Restart the API container

```yaml
volumes:
  # For development - uncomment to enable hot reload
  - ./src:/app/src  # <-- Uncomment this line
```

### Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f api

# Enter container for debugging
docker exec -it llm-call-api /bin/bash

# Check service health
curl http://localhost:8001/health
curl http://localhost:3010/health
```

## Integration with GRANGER

### For Other GRANGER Projects

Projects can connect to llm_call via:

```python
# If on same Docker network
llm_call_url = "http://llm-call-api:8001"

# If on host
llm_call_url = "http://localhost:8001"
```

### Network Configuration

Ensure your project is on the GRANGER network:

```yaml
# In your project's docker-compose.yml
networks:
  granger-network:
    external: true
```

## Security Considerations

### Production Deployment

1. **Use secrets management** for API keys
2. **Enable TLS** for external connections
3. **Set resource limits** to prevent runaway containers
4. **Use read-only mounts** where possible
5. **Implement proper logging** and monitoring

### Container Hardening

The Claude proxy already includes:
- Dropped capabilities
- No new privileges
- tmpfs for temporary files
- Limited file system access

## Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using ports
sudo lsof -i :8001
sudo lsof -i :3010

# Stop conflicting services
docker-compose down
```

**Authentication errors:**
```bash
# Re-authenticate Claude
docker exec -it llm-call-claude-proxy claude /login

# Check credentials
docker exec -it llm-call-claude-proxy ls -la /root/.claude/
```

**Container won't start:**
```bash
# Check logs
docker-compose logs claude-proxy

# Rebuild if needed
docker-compose build --no-cache claude-proxy
```

## Monitoring

### Health Checks

All services include health endpoints:

```bash
# Check all health endpoints
curl http://localhost:8001/health  # API
curl http://localhost:3010/health  # Claude proxy
docker exec llm-call-redis redis-cli ping  # Redis
```

### Resource Usage

```bash
# View resource usage
docker stats

# View detailed info
docker-compose ps
docker-compose top
```

## Backup and Restore

### Backup Volumes

```bash
# Backup Redis data
docker run --rm -v llm-call_redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz -C /data .

# Backup Claude workspace
docker run --rm -v llm-call_claude-workspace:/data -v $(pwd):/backup alpine tar czf /backup/claude-backup.tar.gz -C /data .
```

### Restore Volumes

```bash
# Restore Redis data
docker run --rm -v llm-call_redis-data:/data -v $(pwd):/backup alpine tar xzf /backup/redis-backup.tar.gz -C /data

# Restore Claude workspace
docker run --rm -v llm-call_claude-workspace:/data -v $(pwd):/backup alpine tar xzf /backup/claude-backup.tar.gz -C /data
```

## Next Steps

1. Test the current Claude proxy setup ✅
2. Evaluate full containerization needs
3. Implement based on chosen architecture
4. Update GRANGER hub integration
5. Document deployment procedures