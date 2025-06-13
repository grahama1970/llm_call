# Claude CLI Authentication Guide

## Quick Start

After starting the Docker containers, you need to authenticate Claude CLI inside the container.

### Step 1: Check Authentication Status

```bash
curl http://localhost:3010/health | jq .claude_authenticated
```

If it returns `false`, proceed to Step 2.

### Step 2: Authenticate Claude CLI

Run the authentication helper script:

```bash
./docker/claude-proxy/authenticate.sh
```

This will:
1. Connect you to the Claude proxy container
2. Show instructions to launch Claude Code
3. Allow you to authenticate with your Claude account

Inside the container:
- Type `claude` to launch Claude Code
- Authenticate with your account when prompted
- Exit Claude Code with Ctrl+C (or Cmd+C on Mac)
- Type `exit` to leave the container

### Step 3: Verify Authentication

After authentication, verify it worked:

```bash
curl http://localhost:3010/health | jq .auth_status
```

It should show "Authenticated".

### Step 4: Test Claude

Run the test script to verify everything is working:

```bash
./docker/claude-proxy/test_claude.sh
```

Or test manually:

```bash
curl -X POST http://localhost:3010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "max/opus",
    "messages": [{"role": "user", "content": "Hello Claude!"}]
  }'
```

## Troubleshooting

- **"Not authenticated" error**: Run `./docker/claude-proxy/authenticate.sh`
- **Container not running**: Check with `docker compose ps`
- **Port 3010 in use**: Stop other services or change the port in docker-compose.yml

## Notes

- Authentication persists across container restarts (credentials are mounted)
- You only need to authenticate once per Claude account
- The authentication uses OAuth, not API keys