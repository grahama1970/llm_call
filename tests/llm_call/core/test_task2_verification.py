"""
Task 2 Verification: Test Core API Server (Claude Proxy)

This script verifies that all Task 2 components work correctly together.
"""

import sys
import asyncio
import json
from pathlib import Path
from loguru import logger
import httpx

from llm_call.core import config


async def test_api_server():
    """Test the API server by making actual requests."""
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Health check endpoint
    total_tests += 1
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{config.claude_proxy.host}:{config.claude_proxy.port}/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == config.api.title
            logger.success("✅ Health check endpoint works")
    except Exception as e:
        all_validation_failures.append(f"Health check test failed: {e}")
        logger.warning("Note: This might fail if another server is running on the same port")
    
    # Test 2: Chat completions endpoint structure
    total_tests += 1
    try:
        # Test with invalid JSON
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{config.claude_proxy.host}:{config.claude_proxy.port}/v1/chat/completions",
                content="invalid json"
            )
            assert response.status_code == 400
            assert "Invalid JSON" in response.json()["detail"]
            logger.success("✅ Invalid JSON handling works")
    except Exception as e:
        all_validation_failures.append(f"Invalid JSON test failed: {e}")
    
    # Test 3: Missing user message
    total_tests += 1
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{config.claude_proxy.host}:{config.claude_proxy.port}/v1/chat/completions",
                json={"messages": [{"role": "system", "content": "Be helpful"}]}
            )
            assert response.status_code == 400
            assert "No user message" in response.json()["detail"]
            logger.success("✅ Missing user message handling works")
    except Exception as e:
        all_validation_failures.append(f"Missing message test failed: {e}")
    
    # Test 4: Full chat completion (if Claude CLI exists)
    total_tests += 1
    cli_path = Path(config.claude_proxy.cli_path)
    if cli_path.exists():
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://{config.claude_proxy.host}:{config.claude_proxy.port}/v1/chat/completions",
                    json={
                        "model": "max/test-model",
                        "messages": [
                            {"role": "system", "content": "You are a test assistant. Be very brief."},
                            {"role": "user", "content": "Say 'API test successful!' and nothing else."}
                        ]
                    },
                    timeout=30.0
                )
                assert response.status_code == 200
                data = response.json()
                
                # Verify response structure matches OpenAI format
                assert "id" in data
                assert data["object"] == "chat.completion"
                assert "created" in data
                assert data["model"] == "max/test-model"  # Should match request
                assert len(data["choices"]) == 1
                assert data["choices"][0]["message"]["role"] == "assistant"
                assert "content" in data["choices"][0]["message"]
                assert "usage" in data
                
                content = data["choices"][0]["message"]["content"]
                logger.success(f"✅ Full chat completion works: {content[:100]}...")
        except Exception as e:
            all_validation_failures.append(f"Chat completion test failed: {e}")
    else:
        logger.warning("⚠️ Skipping full chat test - Claude CLI not found")
    
    return all_validation_failures, total_tests


def test_task2_components():
    """Test all Task 2 components."""
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Import API components
    total_tests += 1
    try:
        from llm_call.core.api.main import app
        from llm_call.core.api.handlers import router, chat_completions_endpoint
        from llm_call.core.api.claude_cli_executor import execute_claude_cli
        logger.success("✅ All API components import successfully")
    except Exception as e:
        all_validation_failures.append(f"Import test failed: {e}")
    
    # Test 2: FastAPI app configuration
    total_tests += 1
    try:
        from llm_call.core.api.main import app
        assert app.title == config.api.title
        assert app.version == config.api.version
        # Check routes
        routes = [route.path for route in app.routes]
        assert "/health" in routes
        assert "/v1/chat/completions" in routes
        logger.success("✅ FastAPI app properly configured")
    except Exception as e:
        all_validation_failures.append(f"App configuration test failed: {e}")
    
    # Test 3: POC compatibility check
    total_tests += 1
    try:
        # Verify key POC constants are preserved
        assert config.claude_proxy.host == "127.0.0.1"
        assert config.claude_proxy.port == 8001
        assert config.claude_proxy.proxy_url == "http://127.0.0.1:8001/v1/chat/completions"
        logger.success("✅ POC compatibility maintained")
    except Exception as e:
        all_validation_failures.append(f"POC compatibility test failed: {e}")
    
    return all_validation_failures, total_tests


async def run_server_tests():
    """Run tests that require the server to be running."""
    # Import here to avoid circular imports
    from llm_call.core.api.main import app
    import uvicorn
    from threading import Thread
    import time
    
    # Start server in background thread
    def run_server():
        uvicorn.run(app, host=config.claude_proxy.host, port=config.claude_proxy.port, log_level="error")
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    logger.info("Waiting for server to start...")
    time.sleep(2)
    
    # Run API tests
    failures, tests = await test_api_server()
    
    return failures, tests


if __name__ == "__main__":
    # Run component tests
    failures1, tests1 = test_task2_components()
    
    # Run server tests
    failures2, tests2 = asyncio.run(run_server_tests())
    
    # Combine results
    all_validation_failures = failures1 + failures2
    total_tests = tests1 + tests2
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("\n" + "="*60)
        logger.success("TASK 2 COMPLETE: Core API Server (Claude Proxy)")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info("  ✅ core/api/main.py created with FastAPI app")
        logger.info("  ✅ core/api/handlers.py created with request handlers")
        logger.info("  ✅ core/api/claude_cli_executor.py created with CLI execution")
        logger.info("  ✅ Server endpoints tested and working")
        logger.info("  ✅ POC functionality preserved")
        sys.exit(0)