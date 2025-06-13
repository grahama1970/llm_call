# Claude Proxy Docker Container

This Docker container runs the Claude CLI proxy server that enables `max/opus` model access through the llm_call module.

## Prerequisites

1. **Claude Max Subscription**: You need an active Claude Max subscription
2. **Docker and Docker Compose**: Installed and running

## Setup Instructions

### 1. Build and Run the Container

From the llm_call root directory:

```bash
# Build the container
docker-compose build claude-proxy

# Run the container
docker-compose up -d claude-proxy

# Check logs
docker-compose logs -f claude-proxy
```

### 2. Authenticate Claude CLI Inside Container

If this is your first time running the container, you need to authenticate:

```bash
# Enter the container
docker exec -it llm-call-claude-proxy /bin/bash

# Inside the container, run:
claude /login

# Follow the prompts - you can paste your API key directly
```

The authentication will be persisted in the mounted volume.

### 3. Verify It's Working

Test the proxy:
```bash
curl http://localhost:3010/health
```

Test with llm_call:
```python
from llm_call.core.caller import make_llm_request

response = await make_llm_request({
    "model": "max/claude-3-opus-20240229",
    "messages": [{"role": "user", "content": "Hello!"}]
})
```

## Troubleshooting

### "No Claude credentials found"
- Run `claude /login` on the host machine
- Ensure ~/.claude/.credentials.json exists

### "Invalid API key"
- The container automatically unsets ANTHROPIC_API_KEY
- This forces Claude CLI to use OAuth credentials
- Check the entrypoint.sh script is running

### Container won't start
- Check docker logs: `docker-compose logs claude-proxy`
- Verify credentials: `cat ~/.claude/.credentials.json | jq .claudeAiOauth.accessToken`

## Architecture

1. **Entrypoint Script**: Validates credentials before starting
2. **No API Key**: ANTHROPIC_API_KEY is explicitly unset to force OAuth
3. **Volume Mount**: Host credentials are mounted read-only
4. **Health Check**: Available at /health endpoint

## Security Notes

- Credentials are mounted read-only
- The container runs isolated from the host
- No API keys are stored in the image