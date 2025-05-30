# Serve Commands

Start various servers for the LLM Call project.

## Claude Proxy Server

/serve-claude-proxy
Description: Start Claude proxy server with polling support
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python src/llm_call/proof_of_concept/poc_claude_proxy_with_polling.py
```

/serve-claude-proxy-background
Description: Start Claude proxy in background
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
nohup python src/llm_call/proof_of_concept/poc_claude_proxy_with_polling.py > claude_proxy.log 2>&1 &
echo "Claude proxy started. Check logs: tail -f claude_proxy.log"
```

/serve-claude-proxy-stop
Description: Stop Claude proxy server
```bash
pkill -f "poc_claude_proxy_with_polling.py" || echo "No Claude proxy process found"
```

/serve-claude-proxy-status
Description: Check Claude proxy status
```bash
# Check if running
ps aux | grep -E "claude.*proxy.*polling" | grep -v grep || echo "Not running"

# Check health endpoint
curl -s http://127.0.0.1:3010/health | jq . || echo "Server not responding"

# Check active tasks
curl -s http://127.0.0.1:3010/v1/polling/active | jq . || echo "Cannot reach polling endpoint"
```

## MCP Server

/serve-mcp
Description: Start Model Context Protocol server
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
llm-cli serve-mcp --port 5000
```

/serve-mcp-debug
Description: Start MCP server with debug logging
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
llm-cli serve-mcp --port 5000 --debug
```

/serve-mcp-config
Description: Generate and start MCP server with config
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
# Generate config
llm-cli generate-mcp-config --output mcp_config.json

# Start server
llm-cli serve-mcp --config mcp_config.json
```

## API Server

/serve-api
Description: Start FastAPI server for LLM Call
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python src/llm_call/core/api/main.py
```

/serve-api-dev
Description: Start API server in development mode with auto-reload
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
uvicorn src.llm_call.core.api.main:app --reload --host 0.0.0.0 --port 8000
```

/serve-api-production
Description: Start API server with production settings
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
uvicorn src.llm_call.core.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker Services

/serve-docker
Description: Start all services with Docker Compose
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
docker-compose up -d
```

/serve-docker-logs
Description: View Docker service logs
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
docker-compose logs -f
```

/serve-docker-stop
Description: Stop Docker services
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
docker-compose down
```

/serve-docker-status
Description: Check Docker service status
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
docker-compose ps
```

## Redis Cache Server

/serve-redis
Description: Start Redis for LiteLLM caching
```bash
docker run -d \
  --name llm-redis \
  -p 6379:6379 \
  redis:alpine
```

/serve-redis-stop
Description: Stop Redis server
```bash
docker stop llm-redis
docker rm llm-redis
```

/serve-redis-status
Description: Check Redis status
```bash
redis-cli ping || echo "Redis not running"
```

## Development Servers

/serve-docs
Description: Serve documentation locally
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python -m http.server 8080 --directory docs/
```

/serve-jupyter
Description: Start Jupyter notebook server
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
jupyter notebook --no-browser --port=8888
```

## Service Management

/serve-all
Description: Start all required services
```bash
cd /home/graham/workspace/experiments/claude_max_proxy

# Start Redis
docker run -d --name llm-redis -p 6379:6379 redis:alpine || echo "Redis already running"

# Start Claude proxy
nohup python src/llm_call/proof_of_concept/poc_claude_proxy_with_polling.py > claude_proxy.log 2>&1 &

# Start API server
nohup uvicorn src.llm_call.core.api.main:app --host 0.0.0.0 --port 8000 > api_server.log 2>&1 &

echo "All services started. Check logs:"
echo "  Claude proxy: tail -f claude_proxy.log"
echo "  API server: tail -f api_server.log"
```

/serve-stop-all
Description: Stop all services
```bash
# Stop processes
pkill -f "poc_claude_proxy_with_polling.py"
pkill -f "uvicorn.*llm_call"

# Stop Docker services
docker stop llm-redis 2>/dev/null

echo "All services stopped"
```

/serve-status-all
Description: Check status of all services
```bash
echo "=== Service Status ==="
echo ""

echo "Claude Proxy (port 3010):"
curl -s http://127.0.0.1:3010/health | jq -r .status || echo "  Not running"

echo ""
echo "API Server (port 8000):"
curl -s http://127.0.0.1:8000/health | jq -r .status || echo "  Not running"

echo ""
echo "Redis (port 6379):"
redis-cli ping 2>/dev/null || echo "  Not running"

echo ""
echo "Running processes:"
ps aux | grep -E "(claude_proxy|uvicorn.*llm_call)" | grep -v grep || echo "  None found"
```

## Port Management

/serve-ports
Description: Show all service ports
```bash
echo "Service Ports:"
echo "  Claude Proxy: 3010"
echo "  API Server: 8000"
echo "  MCP Server: 5000"
echo "  Redis: 6379"
echo "  Documentation: 8080"
echo "  Jupyter: 8888"
echo ""
echo "Active listeners:"
netstat -tlnp 2>/dev/null | grep -E "(3010|8000|5000|6379|8080|8888)" || \
  lsof -iTCP -sTCP:LISTEN | grep -E "(3010|8000|5000|6379|8080|8888)"
```

/serve-check-port [port]
Description: Check if a port is in use
Arguments:
  - port: Port number to check
```bash
lsof -i :[port] || echo "Port [port] is available"
```

## Monitoring

/serve-monitor
Description: Monitor all services with live updates
```bash
watch -n 2 '
echo "=== LLM Call Services Monitor ==="
echo ""
echo "Claude Proxy Health:"
curl -s http://127.0.0.1:3010/health 2>/dev/null | jq . || echo "Not running"
echo ""
echo "Active Polling Tasks:"
curl -s http://127.0.0.1:3010/v1/polling/active 2>/dev/null | jq . || echo "N/A"
echo ""
echo "Process Status:"
ps aux | grep -E "(claude_proxy|uvicorn)" | grep -v grep | awk "{print \$11, \$12}" || echo "No processes"
'
```

## Common Workflows

### 1. Development Setup
```bash
# Start Redis for caching
/serve-redis

# Start Claude proxy
/serve-claude-proxy

# Start API server in dev mode
/serve-api-dev
```

### 2. Production Setup
```bash
# Use Docker Compose for all services
/serve-docker

# Monitor logs
/serve-docker-logs
```

### 3. Quick Testing
```bash
# Start only Claude proxy
/serve-claude-proxy-background

# Check it's working
/serve-claude-proxy-status

# Run tests
/test-claude-proxy

# Stop when done
/serve-claude-proxy-stop
```