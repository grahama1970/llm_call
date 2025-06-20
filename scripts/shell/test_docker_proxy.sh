#!/bin/bash
# Test script to verify Docker proxy mode works correctly

set -e

echo "=========================================="
echo "Docker Proxy Mode Test"
echo "=========================================="
echo ""

# Check if services are running
echo "1. Checking Docker services..."
if ! docker compose ps | grep -q "llm-call-api.*running"; then
    echo "❌ API service not running. Starting services..."
    docker compose up -d
    echo "Waiting for services to start..."
    sleep 10
else
    echo "✅ API service is running"
fi

if ! docker compose ps | grep -q "llm-call-claude-proxy.*running"; then
    echo "❌ Claude proxy not running"
    exit 1
else
    echo "✅ Claude proxy is running"
fi

echo ""
echo "2. Checking health endpoints..."

# Check API health
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed"
    curl -s http://localhost:8001/health
    exit 1
fi

# Check proxy health
if curl -s http://localhost:3010/health | grep -q "healthy"; then
    echo "✅ Proxy health check passed"
else
    echo "❌ Proxy health check failed"
    curl -s http://localhost:3010/health
    exit 1
fi

echo ""
echo "3. Testing Claude Max/Opus via API..."

# Create a test Python script
cat > /tmp/test_proxy_mode.py << 'EOF'
import asyncio
import httpx
import json

async def test_proxy():
    async with httpx.AsyncClient() as client:
        # Test via API endpoint
        response = await client.post(
            "http://localhost:8001/v1/chat/completions",
            json={
                "model": "max/opus",
                "messages": [
                    {"role": "user", "content": "What is 2+2? Answer with just the number."}
                ],
                "temperature": 0.0,
                "max_tokens": 10
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"Response: {content}")
            
            if "4" in content:
                print("✅ Proxy mode test PASSED")
                return True
            else:
                print(f"❌ Unexpected response: {content}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(response.text)
            return False

if __name__ == "__main__":
    success = asyncio.run(test_proxy())
    exit(0 if success else 1)
EOF

# Run the test
echo "Sending test request..."
python /tmp/test_proxy_mode.py

echo ""
echo "4. Checking container logs for routing..."
echo ""
echo "API logs (last 10 lines):"
docker logs llm-call-api --tail 10 | grep -E "(Determined route|ERROR)" || true

echo ""
echo "Proxy logs (last 10 lines):"
docker logs llm-call-claude-proxy --tail 10 | grep -E "(Claude CLI|ERROR)" || true

echo ""
echo "=========================================="
echo "Docker Proxy Mode Test Complete"
echo "=========================================="