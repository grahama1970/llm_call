"""
API request handlers for Claude CLI proxy.
Module: handlers.py

This module contains the request handlers that process incoming API requests
and delegate them to the Claude CLI executor.

Links:
- FastAPI documentation: https://fastapi.tiangolo.com/

Sample usage:
    Called automatically by FastAPI when requests are received

Expected output:
    OpenAI-compatible API responses
"""

import json
import time
import os
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from llm_call.core.config.loader import load_configuration

# Load settings at module level  
settings = load_configuration()
from llm_call.core.api.claude_cli_executor import execute_claude_cli

# Create router for API endpoints
router = APIRouter()


@router.post("/v1/chat/completions")
async def chat_completions_endpoint(request: Request):
    """
    Handle chat completion requests in OpenAI format.
    
    This endpoint receives messages in OpenAI's chat format and proxies'
    them to the Claude CLI, returning responses in the same format.
    """
    logger.info("[API Handler] Received chat completion request")
    
    try:
        data = await request.json()
        logger.debug(f"[API Handler] Request data: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        logger.error("[API Handler] Invalid JSON received")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Extract messages and model from request
    messages = data.get("messages", [])
    model_requested_by_client = data.get("model", settings.claude_proxy.default_model_label)
    mcp_config = data.get("mcp_config")  # Extract MCP configuration
    
    # Extract user and system messages
    user_message_content = ""
    system_message_content = "You are a helpful assistant."  # Default from POC
    
    for msg in messages:
        if msg.get("role") == "user":
            user_message_content = msg.get("content", "")
        elif msg.get("role") == "system":
            system_message_content = msg.get("content", system_message_content)
    
    if not user_message_content:
        logger.warning("[API Handler] No user message found")
        raise HTTPException(status_code=400, detail="No user message provided")
    
    # Execute Claude CLI
    claude_response_text = execute_claude_cli(
        prompt=user_message_content,
        system_prompt_content=system_message_content,
        target_dir=settings.claude_proxy.workspace_dir,
        claude_exe_path=Path(settings.claude_proxy.cli_path),
        mcp_config=mcp_config,
        model_name=model_requested_by_client
    )
    
    # Handle error responses
    if claude_response_text is None:
        logger.error("[API Handler] Failed to get response from Claude CLI (returned None)")
        raise HTTPException(status_code=500, detail="Error processing request with Claude CLI: No response")
    
    error_indicators = [
        "Claude CLI exited with code",
        "Claude CLI not found",
        "Claude process timed out",
        "Unexpected server error"
    ]
    
    for indicator in error_indicators:
        if indicator in claude_response_text:
            logger.error(f"[API Handler] Error from Claude CLI: {claude_response_text}")
            raise HTTPException(status_code=500, detail=claude_response_text)
    
    # Log successful response (preview)
    preview_length = 200
    stripped_response_preview = claude_response_text.strip()[:preview_length]
    ellipsis = "..." if len(claude_response_text.strip()) > preview_length else ""
    logger.info(f"[API Handler] Claude response preview:  {stripped_response_preview}{ellipsis}")
    
    # Construct OpenAI-compatible response
    response_payload = {
        "id": f"claude-{os.urandom(8).hex()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model_requested_by_client,  # Use the model name client sent
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": claude_response_text
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }  # Dummy usage for now, matching POC
    }
    
    logger.success("[API Handler] Sending response back to client")
    return JSONResponse(content=response_payload)


# Test function
if __name__ == "__main__":
    import sys
    
    logger.info("Testing API handlers...")
    
    # Test the handler components
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Router is properly configured
    total_tests += 1
    try:
        assert len(router.routes) > 0
        assert any(route.path == "/v1/chat/completions" for route in router.routes)
        logger.success(" Router configured with chat completions endpoint")
    except Exception as e:
        all_validation_failures.append(f"Router configuration failed: {e}")
    
    # Test 2: Configuration is accessible
    total_tests += 1
    try:
        assert settings.claude_proxy.cli_path
        assert settings.claude_proxy.workspace_dir
        logger.success(" Configuration accessible in handlers")
    except Exception as e:
        all_validation_failures.append(f"Configuration access failed: {e}")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f" VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f" VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)