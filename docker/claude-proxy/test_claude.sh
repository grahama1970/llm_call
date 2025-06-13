#!/bin/bash
set -e

echo "==================================="
echo "Claude Proxy Test Script"
echo "==================================="
echo ""

# Check if proxy is healthy
echo "1. Checking Claude proxy health..."
HEALTH_RESPONSE=$(curl -s http://localhost:3010/health)

if [ $? -ne 0 ]; then
    echo "❌ Error: Could not connect to Claude proxy on port 3010"
    echo "   Make sure the container is running: docker compose ps"
    exit 1
fi

# Extract authentication status
AUTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.claude_authenticated')
AUTH_MESSAGE=$(echo "$HEALTH_RESPONSE" | jq -r '.auth_status')

echo "✅ Claude proxy is running"
echo ""

if [ "$AUTH_STATUS" != "true" ]; then
    echo "❌ Claude is not authenticated"
    echo "   Status: $AUTH_MESSAGE"
    echo ""
    echo "Please run: ./docker/claude-proxy/authenticate.sh"
    exit 1
fi

echo "✅ Claude is authenticated"
echo ""

# Test Claude with a simple request
echo "2. Testing Claude API..."
echo ""

RESPONSE=$(curl -s -X POST http://localhost:3010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "max/opus",
    "messages": [{"role": "user", "content": "Say hello and tell me you are working properly in exactly 10 words."}]
  }')

if [ $? -ne 0 ]; then
    echo "❌ Error: Request failed"
    exit 1
fi

# Check for error in response
ERROR=$(echo "$RESPONSE" | jq -r '.error // .detail // empty')
if [ -n "$ERROR" ]; then
    echo "❌ Error from Claude proxy: $ERROR"
    exit 1
fi

# Extract the message content
MESSAGE=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [ -z "$MESSAGE" ]; then
    echo "❌ Error: No message in response"
    echo "Full response:"
    echo "$RESPONSE" | jq .
    exit 1
fi

echo "✅ Claude responded successfully!"
echo ""
echo "Claude says: $MESSAGE"
echo ""
echo "==================================="
echo "✅ All tests passed! Claude is working properly."
echo "==================================="