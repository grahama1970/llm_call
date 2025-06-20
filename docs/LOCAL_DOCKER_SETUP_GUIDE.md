# Local and Docker Setup Guide for LLM Call

This guide provides instructions for running llm_call in both local development mode and production Docker mode.

## Overview

LLM Call supports three execution modes:
1. **Local Development** - Direct Python execution for rapid development
2. **Docker Production** - Full containerized stack for security and isolation
3. **Hybrid Mode** - Mix of local and containerized components

## Prerequisites

### For All Modes
- Python 3.9+ 
- API Keys in `.env` file:
  ```bash
  OPENAI_API_KEY=your_key
  GOOGLE_API_KEY=your_key  # or GOOGLE_APPLICATION_CREDENTIALS
  PERPLEXITY_API_KEY=your_key
  BRAVE_API_KEY=your_key
  ```

### For Docker Mode
- Docker Engine 20.10+
- Docker Compose 2.0+
- (Optional) NVIDIA Docker for GPU support

## Mode 1: Local Development

### Setup
```bash
# 1. Clone repository
git clone https://github.com/grahama1970/llm_call.git
cd llm_call

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install uv
uv sync

# 4. Set environment
export PYTHONPATH=./src
cp .env.example .env
# Edit .env with your API keys

# 5. Start Redis locally
redis-server --port 6379

# 6. Initialize cache
python src/llm_call/core/utils/initialize_litellm_cache.py
```

### Running Locally
```bash
# CLI Interface
python -m llm_call.cli.main ask "What is Python?" --model gpt-4

# API Server
python src/llm_call/api_server.py
# Access at http://localhost:8001

# Conversational Delegator
python src/llm_call/tools/conversational_delegator.py \
  --model vertex_ai/gemini-1.5-pro \
  --prompt "Analyze this document" \
  --conversation-name "doc-analysis"
```

### Claude Max/Opus in Local Mode
```bash
# Requires Claude CLI installed locally
export CLAUDE_PROXY_EXECUTION_MODE=local
export CLAUDE_PROXY_LOCAL_CLI_PATH=$(which claude)
unset ANTHROPIC_API_KEY  # Required for OAuth

# Now use max/opus models
python -m llm_call.cli.main ask "Hello" --model max/opus
```

## Mode 2: Docker Production

### Setup
```bash
# 1. Clone and setup
git clone https://github.com/grahama1970/llm_call.git
cd llm_call

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Build and start all services
docker compose up -d

# 4. Verify services
docker compose ps
# Should show: api, claude-proxy, redis as "healthy"

# 5. For Claude Max users - authenticate
./docker/claude-proxy/authenticate.sh
# Follow prompts to login to Claude

# 6. Test the setup
./docker/claude-proxy/test_claude.sh
curl http://localhost:8001/health
```

### Using Docker Services
```bash
# API Endpoints
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'

# With GPU support (Ollama)
docker compose --profile gpu up -d

# Development tools
docker compose --profile dev up -d
# Redis Commander at http://localhost:8081
```

### Docker Environment Variables
```yaml
# In docker-compose.yml or .env
ENABLE_RL_ROUTING=true      # Enable reinforcement learning routing
ENABLE_LLM_VALIDATION=true  # Enable response validation
LOG_LEVEL=INFO              # Logging level
REDIS_URL=redis://redis:6379
CLAUDE_PROXY_URL=http://claude-proxy:3010
```

## Mode 3: Hybrid Development

Best of both worlds - local code with containerized dependencies.

### Setup
```bash
# 1. Start only infrastructure services
docker compose up -d redis claude-proxy

# 2. Set environment for local development
export PYTHONPATH=./src
export REDIS_URL=redis://localhost:6379
export CLAUDE_PROXY_URL=http://localhost:3010
source .venv/bin/activate

# 3. Run API locally
python src/llm_call/api_server.py
```

### Benefits
- Fast code iteration (no rebuild needed)
- Secure Claude proxy (containerized)
- Persistent Redis cache
- Easy debugging with local code

## Configuration Options

### Local Configuration
```python
# config/local.yaml
model_preferences:
  default: gpt-3.5-turbo
  fallback: 
    - gpt-4
    - vertex_ai/gemini-1.5-pro
    
validation:
  retry_count: 3
  retry_delay: 1.0
  
cache:
  ttl: 172800  # 48 hours
  redis_url: redis://localhost:6379
```

### Docker Configuration
```yaml
# docker-compose.override.yml for custom settings
services:
  api:
    environment:
      - CUSTOM_CONFIG=/app/config/production.yaml
    volumes:
      - ./config/production.yaml:/app/config/production.yaml:ro
```

## Switching Between Modes

### Local to Docker
```bash
# Stop local services
pkill -f "python.*llm_call"
redis-cli shutdown

# Start Docker stack
docker compose up -d
```

### Docker to Local
```bash
# Stop Docker services
docker compose down

# Start local Redis
redis-server --port 6379 &

# Run locally
export PYTHONPATH=./src
python src/llm_call/api_server.py
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using ports
   lsof -i :8001  # API
   lsof -i :3010  # Claude proxy
   lsof -i :6379  # Redis
   ```

2. **Claude authentication**
   ```bash
   # Re-authenticate
   docker exec -it llm-call-claude-proxy /bin/bash
   claude  # Follow login prompts
   ```

3. **Redis connection**
   ```bash
   # Test Redis
   redis-cli ping
   # Should return "PONG"
   ```

4. **API key issues**
   ```bash
   # Verify environment
   docker compose exec api env | grep API_KEY
   ```

## Performance Optimization

### Local Mode
- Use `--cache` flag for repeated queries
- Run Redis with persistence: `redis-server --appendonly yes`
- Set `PYTHONUNBUFFERED=1` for real-time logs

### Docker Mode
- Adjust resource limits in docker-compose.yml
- Use volume mounts for model caches
- Enable only needed services (skip Ollama if not using)

## Security Considerations

### Local Mode
- Keep API keys in `.env` (never commit)
- Use virtual environment isolation
- Run Redis with password in production

### Docker Mode
- Read-only root filesystem for API container
- Dropped capabilities for security
- Network isolation between services
- Volume permissions restricted

## Next Steps

1. Choose your preferred mode based on use case
2. Run the critical tests first (see TEST_PRIORITY_GUIDE.md)
3. Configure for your specific needs
4. Monitor logs for any issues:
   - Local: Check terminal output
   - Docker: `docker compose logs -f`