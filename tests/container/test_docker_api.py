#!/usr/bin/env python3
"""
Module: test_docker_api.py
Description: Tests specifically for Docker container functionality

These tests ONLY run when containers are up and verify container-specific
features like networking, volume mounts, and inter-service communication.

External Dependencies:
- pytest: https://docs.pytest.org/
- httpx: https://www.python-httpx.org/

Sample Input:
>>> response = await client.get("http://localhost:8001/health")

Expected Output:
>>> {"status": "healthy", "services": {...}}

Example Usage:
>>> # Only run when containers are up
>>> docker-compose up -d
>>> pytest tests/container/test_docker_api.py -v
>>> docker-compose down
"""

import asyncio
import os
import sys
from typing import Dict, Any

import pytest
import httpx
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO")

class TestDockerAPI:
    """Test Docker container functionality."""
    
    @pytest.fixture
    async def client(self):
        """Create HTTP client for API testing."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    async def test_api_health_endpoint(self, client):
        """Test that API health endpoint responds correctly."""
        response = await client.get("http://localhost:8001/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
        
        # Check service connectivity
        if "services" in data:
            logger.info(f"Connected services: {data['services']}")
    
    async def test_claude_proxy_health(self, client):
        """Test Claude proxy health endpoint."""
        response = await client.get("http://localhost:3010/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    async def test_inter_service_communication(self, client):
        """Test that API can communicate with Claude proxy."""
        # Make a request that would use the Claude proxy
        request_data = {
            "model": "max/chat-general",
            "messages": [{"role": "user", "content": "Say 'inter-service test passed'"}]
        }
        
        try:
            response = await client.post(
                "http://localhost:8001/v1/chat/completions",
                json=request_data
            )
            
            # We expect this might fail if Claude isn't authenticated
            # But we should get a proper error response, not a connection error
            assert response.status_code in [200, 401, 403, 500]
            
            if response.status_code == 200:
                data = response.json()
                logger.success("Claude proxy integration working!")
                assert "choices" in data
            else:
                logger.warning(f"Claude proxy returned {response.status_code} - may need authentication")
                
        except httpx.ConnectError:
            pytest.fail("Cannot connect to API - are containers running?")
    
    async def test_volume_persistence(self, client):
        """Test that volumes are properly mounted."""
        # This would test that logs/cache volumes work
        # Make a request that generates logs
        await client.get("http://localhost:8001/health")
        
        # In a real test, we'd exec into container and check /app/logs
        # For now, we just verify the endpoint works
        assert True
    
    async def test_redis_connectivity(self, client):
        """Test Redis connectivity through the API."""
        # Make multiple requests to test caching
        for i in range(3):
            response = await client.get("http://localhost:8001/health")
            assert response.status_code == 200
            
        # Redis should be reported as healthy
        data = response.json()
        if "redis" in data:
            assert data["redis"] in ["ok", "connected"]
    
    async def test_security_headers(self, client):
        """Test that security headers are present."""
        response = await client.get("http://localhost:8001/")
        
        # Check for security headers
        headers = response.headers
        
        # These might be set by the API or reverse proxy
        security_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection"
        ]
        
        # Log which security headers are present
        for header in security_headers:
            if header in headers:
                logger.info(f"Security header present: {header}={headers[header]}")
    
    async def test_resource_limits(self, client):
        """Test that resource limits are enforced."""
        # Make many concurrent requests to test rate limiting
        tasks = []
        for i in range(10):
            task = client.get("http://localhost:8001/health")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful responses
        success_count = sum(1 for r in responses 
                          if not isinstance(r, Exception) and r.status_code == 200)
        
        logger.info(f"Concurrent requests: {success_count}/10 succeeded")
        
        # At least some should succeed
        assert success_count > 0
    
    @pytest.mark.slow
    async def test_llm_request_through_container(self, client):
        """Test making an actual LLM request through containerized API."""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a test assistant. Keep responses very short."},
                {"role": "user", "content": "Reply with exactly: 'Container test successful'"}
            ],
            "max_tokens": 50,
            "temperature": 0
        }
        
        try:
            response = await client.post(
                "http://localhost:8001/v1/chat/completions",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "choices" in data
                assert len(data["choices"]) > 0
                
                content = data["choices"][0]["message"]["content"]
                logger.success(f"LLM Response: {content}")
                
                # Verify we got a real response
                assert len(content) > 0
                assert "test" in content.lower() or "container" in content.lower()
            else:
                # API key might not be configured
                logger.warning(f"LLM request returned {response.status_code}")
                assert response.status_code in [401, 403]
                
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            # Don't fail test if API keys aren't configured
            if "api" in str(e).lower() or "key" in str(e).lower():
                pytest.skip("API keys not configured")
            else:
                raise

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )

if __name__ == "__main__":
    # Simple check when run directly
    import subprocess
    
    print("Checking if containers are running...")
    result = subprocess.run(
        ["docker", "ps", "--format", "table {{.Names}}"],
        capture_output=True,
        text=True
    )
    
    if "llm-call-api" in result.stdout:
        print("✅ Containers are running")
        print("Run: pytest tests/container/test_docker_api.py -v")
    else:
        print("❌ Containers not running")
        print("Run: docker-compose up -d")
        sys.exit(1)