#!/bin/bash
set -e

# Ensure PYTHONPATH is set correctly
export PYTHONPATH=/app/src:/app

echo "Starting LLM Call API Server..."

# Function to check service availability
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1
    
    echo "Waiting for $service_name at $host:$port..."
    
    while ! python -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('$host', $port)); s.close()" 2>/dev/null; do
        if [ $attempt -eq $max_attempts ]; then
            echo "❌ $service_name failed to start after $max_attempts attempts"
            exit 1
        fi
        echo "Attempt $attempt/$max_attempts: $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "✅ $service_name is ready!"
}

# Check environment
echo "Environment Configuration:"
echo "- LOG_LEVEL: ${LOG_LEVEL}"
echo "- REDIS_URL: ${REDIS_URL}"
echo "- CLAUDE_PROXY_URL: ${CLAUDE_PROXY_URL}"
echo "- ENABLE_RL_ROUTING: ${ENABLE_RL_ROUTING}"
echo "- ENABLE_LLM_VALIDATION: ${ENABLE_LLM_VALIDATION}"

# Check API keys (don't print them)
if [ -n "$OPENAI_API_KEY" ]; then echo "✅ OpenAI API key configured"; else echo "⚠️  No OpenAI API key"; fi
if [ -n "$GOOGLE_API_KEY" ]; then echo "✅ Google API key configured"; else echo "⚠️  No Google API key"; fi
if [ -n "$ANTHROPIC_API_KEY" ]; then echo "✅ Anthropic API key configured"; else echo "⚠️  No Anthropic API key"; fi

# Parse REDIS_URL and set environment variables for litellm
if [[ "$REDIS_URL" == *"redis"* ]]; then
    # Extract host and port from REDIS_URL
    # Handle redis://host:port/db format
    REDIS_HOST=$(echo $REDIS_URL | sed -E 's|redis://([^:/]+)(:[0-9]+)?(/.*)?|\1|')
    REDIS_PORT=$(echo $REDIS_URL | sed -E 's|redis://[^:]+:([0-9]+)(/.*)?|\1|' | grep -E '^[0-9]+$' || echo "6379")
    export REDIS_HOST=$REDIS_HOST
    export REDIS_PORT=$REDIS_PORT
    echo "Redis configuration: REDIS_HOST=$REDIS_HOST, REDIS_PORT=$REDIS_PORT"
    echo "Note: Redis connection will be attempted but is not required (fallback to in-memory cache)"
fi

if [[ "$CLAUDE_PROXY_URL" == *"claude-proxy"* ]]; then
    # Extract host and port from CLAUDE_PROXY_URL
    PROXY_HOST=$(echo $CLAUDE_PROXY_URL | sed -E 's|.*://([^:]+):.*|\1|')
    PROXY_PORT=$(echo $CLAUDE_PROXY_URL | sed -E 's|.*:([0-9]+).*|\1|')
    wait_for_service "$PROXY_HOST" "$PROXY_PORT" "Claude Proxy"
fi

# Create required directories if they don't exist
mkdir -p /app/logs /app/cache

# Check if running API server or another command
if [ $# -eq 0 ]; then
    # Default: run the API server
    echo "Starting API server on port 8001..."
    # Use env to ensure all environment variables are passed to the child process
    exec env REDIS_HOST="$REDIS_HOST" REDIS_PORT="$REDIS_PORT" python -m uvicorn llm_call.api_server:app --host 0.0.0.0 --port 8001
else
    # Run whatever command was passed
    exec env REDIS_HOST="$REDIS_HOST" REDIS_PORT="$REDIS_PORT" "$@"
fi