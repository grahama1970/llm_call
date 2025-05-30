"""
Enhanced POC Claude Proxy Server with Async SQLite Polling Support.

This server extends the existing Claude proxy with:
1. Async SQLite-based polling for long-running Claude CLI calls
2. Real-time status updates visible to agents via polling API
3. Background task execution with progress tracking
4. Integration with the existing AsyncPollingManager

Documentation:
- MCP Spec: https://modelcontextprotocol.io/specification/
- Claude CLI MCP: https://docs.anthropic.com/en/docs/claude-code
- AsyncIO: https://docs.python.org/3/library/asyncio-task.html
"""

import asyncio
import httpx
import json
import os
import re
import subprocess
import shlex
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import tempfile
import uuid
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from loguru import logger
from dotenv import load_dotenv

# Import the async polling manager
from llm_call.proof_of_concept.async_polling_manager import AsyncPollingManager, TaskStatus

load_dotenv()

# --- PoC Configuration ---
POC_SERVER_HOST = "127.0.0.1"
POC_SERVER_PORT = 3010
FASTAPI_POC_ENDPOINT_URL = f"http://{POC_SERVER_HOST}:{POC_SERVER_PORT}/v1/chat/completions"

# Claude CLI Configuration
CLAUDE_CLI_PATH = os.getenv("CLAUDE_CLI_PATH", "/home/graham/.nvm/versions/node/v22.15.0/bin/claude")
POC_TARGET_DIR = Path(__file__).parent.resolve() / "claude_poc_workspace"
POC_TARGET_DIR.mkdir(exist_ok=True)

# SQLite database for polling
POLLING_DB_PATH = Path(__file__).parent.parent.parent.parent / "logs" / "llm_polling_tasks.db"
POLLING_DB_PATH.parent.mkdir(exist_ok=True)

# Configure logger
logger.remove()
logger.add(
    lambda msg: print(msg, end=""), 
    colorize=True, 
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>", 
    level="INFO"
)

# --- Default MCP Configuration ---
DEFAULT_ALL_TOOLS_MCP_CONFIG = {
    "mcpServers": {
        "perplexity-ask": {
            "command": "npx",
            "args": ["-y", "server-perplexity-ask"],
            "env": {
                "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", "")
            }
        },
        "desktop-commander": {
            "command": "npx",
            "args": ["-y", "@wonderwhy-er/desktop-commander"],
            "env": {}
        },
        "brave-search": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": os.getenv("BRAVE_API_KEY", "")
            }
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN", "")
            }
        },
        "context7": {
            "command": "npx",
            "args": ["-y", "@upstash/context7-mcp@latest"],
            "env": {}
        }
    }
}

# --- MCP File Management ---
def write_dynamic_mcp_json(mcp_config: Dict[str, Any], target_dir: Path) -> Path:
    """Write MCP configuration to .mcp.json in the target directory."""
    mcp_file_path = target_dir / ".mcp.json"
    
    try:
        if not mcp_config:
            mcp_config = DEFAULT_ALL_TOOLS_MCP_CONFIG
            logger.info("Using default MCP config (all tools)")
        
        with open(mcp_file_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        logger.info(f"Wrote MCP config to: {mcp_file_path}")
        return mcp_file_path
        
    except Exception as e:
        logger.error(f"Failed to write MCP config: {e}")
        raise

def remove_dynamic_mcp_json(mcp_file_path: Path) -> None:
    """Remove the dynamically created MCP config file."""
    try:
        if mcp_file_path.exists():
            mcp_file_path.unlink()
            logger.info(f"Removed MCP config file: {mcp_file_path}")
    except Exception as e:
        logger.warning(f"Failed to remove MCP config file: {e}")

# --- Claude CLI Execution with Progress Updates ---
async def execute_claude_cli_with_progress(
    prompt: str,
    system_prompt_content: str,
    target_dir: Path,
    claude_exe_path: Path,
    task_id: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4096
) -> Optional[str]:
    """
    Execute Claude CLI with progress updates to the polling database.
    
    This function runs Claude CLI and provides real-time updates via SQLite
    that agents can poll to see the current status.
    """
    logger.info(f"[Polling-Enhanced] Executing Claude CLI for task: {task_id}")
    
    if not claude_exe_path.is_file():
        raise ValueError(f"Claude executable not found at: {claude_exe_path}")
    
    if not target_dir.is_dir():
        raise ValueError(f"Target directory not found: {target_dir}")
    
    # Build command
    cmd_list = [
        str(claude_exe_path),
        "--system-prompt", system_prompt_content,
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose"
    ]
    
    logger.info(f"Executing in '{target_dir}': {' '.join(shlex.quote(c) for c in cmd_list)}")
    
    # Check if .mcp.json exists
    mcp_file = target_dir / ".mcp.json"
    if mcp_file.exists():
        logger.info(f"MCP config found at: {mcp_file}")
    else:
        logger.warning("No .mcp.json found - Claude will run without tools")
    
    # Update progress: Starting Claude
    if task_id and polling_manager:
        await polling_manager._update_status(
            task_id, 
            TaskStatus.RUNNING,
            progress={"stage": "starting_claude", "message": "Starting Claude CLI process"}
        )
    
    process = None
    final_result_content: Optional[str] = None
    
    try:
        # Start Claude process
        process = await asyncio.create_subprocess_exec(
            *cmd_list,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(target_dir)
        )
        
        logger.info(f"Claude subprocess started (PID: {process.pid})")
        
        # Update progress: Claude running
        if task_id and polling_manager:
            await polling_manager._update_status(
                task_id,
                TaskStatus.RUNNING,
                progress={"stage": "claude_running", "message": f"Claude process running (PID: {process.pid})"}
            )
        
        full_response_text = ""
        tool_calls_count = 0
        
        # Read stdout line by line
        async for line in process.stdout:
            stripped_line = line.decode().strip()
            if not stripped_line:
                continue
            
            try:
                data = json.loads(stripped_line)
                
                # Track tool usage for progress updates
                if data.get("type") == "tool_use":
                    tool_calls_count += 1
                    tool_name = data.get("tool", {}).get("name", "unknown")
                    if task_id and polling_manager:
                        await polling_manager._update_status(
                            task_id,
                            TaskStatus.RUNNING,
                            progress={
                                "stage": "tool_execution",
                                "message": f"Executing tool: {tool_name}",
                                "tool_calls": tool_calls_count
                            }
                        )
                
                # Handle assistant messages
                elif data.get("type") == "assistant" and isinstance(data.get("message"), dict):
                    content_list = data["message"].get("content", [])
                    for item in content_list:
                        if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                            full_response_text += item["text"]
                            
                            # Update progress with partial response
                            if task_id and polling_manager and len(full_response_text) % 100 == 0:
                                await polling_manager._update_status(
                                    task_id,
                                    TaskStatus.RUNNING,
                                    progress={
                                        "stage": "generating_response",
                                        "message": f"Generated {len(full_response_text)} characters",
                                        "partial_response": full_response_text[:200] + "..."
                                    }
                                )
                
                # Handle final result
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"]
                        logger.info("Successfully extracted final result")
                        break
                        
            except json.JSONDecodeError:
                logger.debug(f"Non-JSON line: {stripped_line}")
            except Exception as e:
                logger.error(f"Error processing stream: {e}")
        
        # Fallback to accumulated text
        if final_result_content is None and full_response_text:
            logger.info("Using accumulated text as final result")
            final_result_content = full_response_text.strip()
        
        # Wait for process completion
        try:
            await asyncio.wait_for(process.wait(), timeout=120)
        except asyncio.TimeoutError:
            logger.error("Claude process timed out")
            process.kill()
            await process.wait()
            raise
        
        # Read any remaining stderr
        stderr_data = await process.stderr.read()
        if stderr_data:
            stderr_output = stderr_data.decode()
            logger.error(f"STDERR from Claude:\n{stderr_output.strip()}")
        
        if process.returncode != 0:
            raise RuntimeError(f"Claude exited with code {process.returncode}")
            
    except Exception as e:
        logger.exception(f"Error running Claude: {e}")
        raise
        
    finally:
        if process and process.returncode is None:
            logger.warning("Terminating Claude process")
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=5)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
    
    return final_result_content

# --- Async Polling Manager Instance ---
# Will be initialized in startup event
polling_manager: Optional[AsyncPollingManager] = None

# --- FastAPI Application ---
app = FastAPI(title="Claude Proxy with Async Polling Support")

@app.on_event("startup")
async def startup_event():
    """Initialize polling manager on startup."""
    global polling_manager
    polling_manager = AsyncPollingManager(
        db_path=str(POLLING_DB_PATH),
        cleanup_after_hours=24,
        max_concurrent_tasks=5
    )
    logger.info("Polling manager initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    if polling_manager:
        # Cancel any active tasks
        active_tasks = await polling_manager.get_active_tasks()
        for task in active_tasks:
            await polling_manager.cancel_task(task.task_id)
        logger.info("Shutdown complete")

@app.post("/v1/chat/completions")
async def chat_completions_with_polling(request: Request):
    """
    Handle chat completion requests with async polling support.
    
    Additional parameters:
    - polling_mode: If true, returns immediately with task_id for polling
    - timeout: Maximum time to wait (default: 300s for Claude calls)
    """
    logger.info("[Polling Proxy] Received chat completion request")
    
    mcp_file_written_path: Optional[Path] = None
    
    try:
        # Parse request
        data = await request.json()
        
        # Extract polling parameters
        polling_mode = data.get("polling_mode", False)
        timeout = data.get("timeout", 300.0)
        
        # Check if this is a Claude proxy call
        model = data.get("model", "")
        is_claude_proxy = model.startswith("max/")
        
        # For non-Claude models, use the original sync behavior
        if not is_claude_proxy:
            return await _handle_sync_request(data)
        
        # Extract messages
        messages = data.get("messages", [])
        user_message_content = ""
        system_message_content = "You are a helpful assistant."
        
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, list):
                    text_parts = [item.get("text", "") for item in content if item.get("type") == "text"]
                    user_message_content = " ".join(text_parts)
                else:
                    user_message_content = content
            elif msg.get("role") == "system":
                system_message_content = msg.get("content", "")
        
        if not user_message_content:
            raise HTTPException(status_code=400, detail="No user message provided")
        
        # Handle MCP configuration
        mcp_config = data.get("mcp_config")
        if mcp_config:
            logger.info("Using custom MCP config from request")
            mcp_file_written_path = write_dynamic_mcp_json(mcp_config, POC_TARGET_DIR)
        else:
            logger.info("No MCP config in request, using default all tools")
            mcp_file_written_path = write_dynamic_mcp_json(DEFAULT_ALL_TOOLS_MCP_CONFIG, POC_TARGET_DIR)
        
        # Define the async executor for Claude CLI
        async def claude_executor(config: Dict[str, Any]) -> Dict[str, Any]:
            """Execute Claude CLI and return OpenAI-compatible response."""
            task_id = config.get('_task_id')
            
            claude_response = await execute_claude_cli_with_progress(
                prompt=user_message_content,
                system_prompt_content=system_message_content,
                target_dir=POC_TARGET_DIR,
                claude_exe_path=Path(CLAUDE_CLI_PATH),
                task_id=task_id,
                temperature=data.get("temperature", 0.0),
                max_tokens=data.get("max_tokens", 4096)
            )
            
            if claude_response is None:
                raise RuntimeError("Failed to get response from Claude CLI")
            
            # Extract JSON if needed
            response_format = config.get("response_format") or data.get("response_format")
            if response_format and response_format.get("type") == "json_object":
                claude_response = _extract_json_from_response(claude_response)
            
            # Build OpenAI-compatible response
            return {
                "id": f"claude-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": claude_response
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
        
        # Submit task to polling manager
        polling_manager.set_executor(claude_executor)
        
        # Prepare task config
        task_config = {
            "model": model,
            "messages": messages,
            "temperature": data.get("temperature", 0.0),
            "max_tokens": data.get("max_tokens", 4096),
            "response_format": data.get("response_format"),
            "_original_request": data
        }
        
        task_id = await polling_manager.submit_task(task_config)
        logger.info(f"Submitted Claude task: {task_id}")
        
        if polling_mode:
            # Return immediately with task ID
            return JSONResponse(content={
                "task_id": task_id,
                "status": "pending",
                "message": "Task submitted for background execution",
                "polling_url": f"/v1/polling/status/{task_id}"
            })
        else:
            # Wait for completion
            try:
                result = await polling_manager.wait_for_task(task_id, timeout=timeout)
                return JSONResponse(content=result)
            except TimeoutError:
                # Return timeout error but keep task running
                return JSONResponse(
                    status_code=408,
                    content={
                        "error": "Request timeout",
                        "task_id": task_id,
                        "message": f"Task is still running. Check status at /v1/polling/status/{task_id}",
                        "timeout": timeout
                    }
                )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Clean up MCP file
        if mcp_file_written_path:
            remove_dynamic_mcp_json(mcp_file_written_path)

@app.get("/v1/polling/status/{task_id}")
async def get_polling_status(task_id: str):
    """Get the status of a polling task."""
    task_info = await polling_manager.get_status(task_id)
    
    if not task_info:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    response = {
        "task_id": task_info.task_id,
        "status": task_info.status.value,
        "created_at": task_info.created_at,
        "started_at": task_info.started_at,
        "completed_at": task_info.completed_at,
        "progress": task_info.progress
    }
    
    if task_info.status == TaskStatus.COMPLETED:
        response["result"] = task_info.result
    elif task_info.status in [TaskStatus.FAILED, TaskStatus.TIMEOUT]:
        response["error"] = task_info.error
    
    return JSONResponse(content=response)

@app.post("/v1/polling/cancel/{task_id}")
async def cancel_polling_task(task_id: str):
    """Cancel a running task."""
    success = await polling_manager.cancel_task(task_id)
    
    if success:
        return JSONResponse(content={"message": f"Task {task_id} cancelled"})
    else:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found or already completed")

@app.get("/v1/polling/active")
async def get_active_tasks():
    """Get all active polling tasks."""
    active_tasks = await polling_manager.get_active_tasks()
    
    return JSONResponse(content={
        "active_tasks": [
            {
                "task_id": task.task_id,
                "status": task.status.value,
                "model": task.llm_config.get("model", "unknown"),
                "created_at": task.created_at,
                "started_at": task.started_at,
                "progress": task.progress
            }
            for task in active_tasks
        ],
        "count": len(active_tasks)
    })

@app.get("/health")
async def health_check():
    """Health check endpoint with polling status."""
    active_tasks = await polling_manager.get_active_tasks()
    
    return {
        "status": "healthy",
        "claude_cli_path": CLAUDE_CLI_PATH,
        "working_directory": str(POC_TARGET_DIR),
        "mcp_support": True,
        "polling_support": True,
        "active_tasks": len(active_tasks),
        "database_path": str(POLLING_DB_PATH)
    }

async def _handle_sync_request(data: Dict[str, Any]) -> JSONResponse:
    """Handle non-Claude requests synchronously (original behavior)."""
    # This would forward to LiteLLM or other providers
    # For now, return a mock response
    return JSONResponse(content={
        "id": f"sync-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": data.get("model", "unknown"),
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This would be handled by the original sync proxy logic"
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    })

def _extract_json_from_response(response: str) -> str:
    """Extract JSON from Claude's response."""
    json_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
        r'\{[\s\S]*\}'
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response)
        if matches:
            try:
                json_str = matches[0] if pattern != r'\{[\s\S]*\}' else response
                if pattern == r'\{[\s\S]*\}':
                    start = json_str.find('{')
                    end = json_str.rfind('}') + 1
                    if start >= 0 and end > start:
                        json_str = json_str[start:end]
                json.loads(json_str)  # Validate
                return json_str
            except json.JSONDecodeError:
                continue
    
    return response

# --- Main ---
if __name__ == "__main__":
    import sys
    
    # Verify Claude CLI exists
    if not Path(CLAUDE_CLI_PATH).is_file():
        logger.error(f"Claude CLI not found at: {CLAUDE_CLI_PATH}")
        logger.error("Set CLAUDE_CLI_PATH environment variable or update the default path")
        sys.exit(1)
    
    logger.info(f"Claude CLI: {CLAUDE_CLI_PATH}")
    logger.info(f"Working directory: {POC_TARGET_DIR}")
    logger.info(f"Polling database: {POLLING_DB_PATH}")
    logger.info(f"Server will run on: {POC_SERVER_HOST}:{POC_SERVER_PORT}")
    logger.info("\n📊 Polling endpoints:")
    logger.info("  - GET  /v1/polling/status/{task_id}")
    logger.info("  - POST /v1/polling/cancel/{task_id}")
    logger.info("  - GET  /v1/polling/active")
    
    # Run server
    logger.info("\n🚀 Starting Claude proxy with async polling support...")
    uvicorn.run(
        app,
        host=POC_SERVER_HOST,
        port=POC_SERVER_PORT,
        log_level="info"
    )