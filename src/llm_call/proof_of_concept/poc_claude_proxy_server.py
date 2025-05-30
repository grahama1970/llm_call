"""
POC Claude Proxy Server with MCP (Model Context Protocol) Support.

This server enhances the existing claude_cli_via_api_poc_v1_working.py with:
1. Dynamic MCP configuration per request
2. .mcp.json file management in Claude's working directory
3. Default "all tools" configuration when no MCP specified
4. Cleanup of MCP files after each request

Documentation:
- MCP Spec: https://modelcontextprotocol.io/specification/
- Claude CLI MCP: https://docs.anthropic.com/en/docs/claude-code
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

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import time

from loguru import logger
from dotenv import load_dotenv
load_dotenv()

# --- PoC Configuration ---
POC_SERVER_HOST = "127.0.0.1"
POC_SERVER_PORT = 3010  # As requested
FASTAPI_POC_ENDPOINT_URL = f"http://{POC_SERVER_HOST}:{POC_SERVER_PORT}/v1/chat/completions"

# Claude CLI Configuration
CLAUDE_CLI_PATH = os.getenv("CLAUDE_CLI_PATH", "/home/graham/.nvm/versions/node/v22.15.0/bin/claude")
POC_TARGET_DIR = Path(__file__).parent.resolve() / "claude_poc_workspace"
POC_TARGET_DIR.mkdir(exist_ok=True)

# Configure logger
logger.remove()
logger.add(
    lambda msg: print(msg, end=""), 
    colorize=True, 
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>", 
    level="INFO"
)

# --- Default MCP Configuration ---
# Based on the .mcp.json file in the project root
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
    """
    Write MCP configuration to .mcp.json in the target directory.
    
    Args:
        mcp_config: The MCP configuration dict
        target_dir: Directory where Claude CLI will run
        
    Returns:
        Path to the written .mcp.json file
    """
    mcp_file_path = target_dir / ".mcp.json"
    
    try:
        # Ensure we have a valid config
        if not mcp_config:
            mcp_config = DEFAULT_ALL_TOOLS_MCP_CONFIG
            logger.info("Using default MCP config (all tools)")
        
        # Write the config
        with open(mcp_file_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        
        logger.info(f"Wrote MCP config to: {mcp_file_path}")
        logger.debug(f"MCP Config contents: {json.dumps(mcp_config, indent=2)}")
        
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

# --- Claude CLI Execution ---
def execute_claude_cli_for_poc(
    prompt: str,
    system_prompt_content: str,
    target_dir: Path,
    claude_exe_path: Path,
    temperature: float = 0.0,
    max_tokens: int = 4096
) -> Optional[str]:
    """
    Execute Claude CLI with the given parameters.
    
    The .mcp.json file should already be written to target_dir before calling this.
    """
    logger.info(f"[MCP-Enhanced PoC] Executing Claude CLI")
    
    if not claude_exe_path.is_file():
        logger.error(f"Claude executable not found at: {claude_exe_path}")
        return None
    
    if not target_dir.is_dir():
        logger.error(f"Target directory not found: {target_dir}")
        return None
    
    # Build command
    cmd_list = [
        str(claude_exe_path),
        "--system-prompt", system_prompt_content,
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose"
    ]
    
    # Note: Claude CLI doesn't support --temperature or --max-tokens flags
    # These would need to be part of the prompt or system prompt if needed
    
    logger.info(f"Executing in '{target_dir}': {' '.join(shlex.quote(c) for c in cmd_list)}")
    
    # Check if .mcp.json exists in target directory
    mcp_file = target_dir / ".mcp.json"
    if mcp_file.exists():
        logger.info(f"MCP config found at: {mcp_file}")
    else:
        logger.warning("No .mcp.json found in target directory - Claude will run without tools")
    
    process = None
    final_result_content: Optional[str] = None
    
    try:
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_dir),
            bufsize=1
        )
        logger.info(f"Claude subprocess started (PID: {process.pid})")
        
        full_response_text = ""
        
        # Parse streaming JSON output
        for line in iter(process.stdout.readline, ''):
            stripped_line = line.strip()
            if not stripped_line:
                continue
            
            logger.debug(f"Stream line: {stripped_line}")
            
            try:
                data = json.loads(stripped_line)
                
                # Handle assistant messages
                if data.get("type") == "assistant" and isinstance(data.get("message"), dict):
                    content_list = data["message"].get("content", [])
                    for item in content_list:
                        if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                            full_response_text += item["text"]
                
                # Handle final result
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"]
                        logger.info("Successfully extracted final result")
                        break
                        
            except json.JSONDecodeError:
                logger.warning(f"Non-JSON line: {stripped_line}")
            except Exception as e:
                logger.error(f"Error processing stream: {e}")
        
        # Fallback to accumulated text if no final result
        if final_result_content is None and full_response_text:
            logger.info("Using accumulated text as final result")
            final_result_content = full_response_text.strip()
        
        # Wait for process completion
        stdout_remaining, stderr_output = process.communicate(timeout=120)
        
        if stderr_output:
            logger.error(f"STDERR from Claude:\n{stderr_output.strip()}")
        
        if process.returncode != 0:
            logger.error(f"Claude exited with code {process.returncode}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("Claude process timed out")
        if process:
            process.kill()
            process.communicate()
        return None
        
    except Exception as e:
        logger.exception(f"Error running Claude: {e}")
        return None
        
    finally:
        if process and process.poll() is None:
            logger.warning("Terminating Claude process")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
    
    return final_result_content

# --- FastAPI Application ---
app = FastAPI(title="PoC Claude CLI Proxy with MCP Support")

@app.post("/v1/chat/completions")
async def poc_chat_completions_endpoint(request: Request):
    """
    Handle chat completion requests with MCP support.
    
    Expected payload includes standard OpenAI format plus optional:
    - mcp_config: Dict with MCP server definitions
    - temperature: Float (0.0-2.0)
    - max_tokens: Int
    """
    logger.info("[MCP Proxy] Received chat completion request")
    
    mcp_file_written_path: Optional[Path] = None
    
    try:
        # Parse request
        data = await request.json()
        logger.debug(f"Request data: {json.dumps(data, indent=2)}")
        
        # Extract messages
        messages = data.get("messages", [])
        user_message_content = ""
        system_message_content = "You are a helpful assistant."
        
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # Handle multimodal content
                if isinstance(content, list):
                    # Extract text from multimodal content
                    text_parts = [item.get("text", "") for item in content if item.get("type") == "text"]
                    user_message_content = " ".join(text_parts)
                else:
                    user_message_content = content
            elif msg.get("role") == "system":
                system_message_content = msg.get("content", "")
        
        if not user_message_content:
            raise HTTPException(status_code=400, detail="No user message provided")
        
        # Extract optional parameters
        temperature = data.get("temperature", 0.0)
        max_tokens = data.get("max_tokens", 4096)
        response_format = data.get("response_format")
        
        # Handle MCP configuration
        mcp_config = data.get("mcp_config")
        if mcp_config:
            logger.info("Using custom MCP config from request")
            mcp_file_written_path = write_dynamic_mcp_json(mcp_config, POC_TARGET_DIR)
        else:
            logger.info("No MCP config in request, using default all tools")
            mcp_file_written_path = write_dynamic_mcp_json(DEFAULT_ALL_TOOLS_MCP_CONFIG, POC_TARGET_DIR)
        
        # Execute Claude CLI
        claude_response = execute_claude_cli_for_poc(
            prompt=user_message_content,
            system_prompt_content=system_message_content,
            target_dir=POC_TARGET_DIR,
            claude_exe_path=Path(CLAUDE_CLI_PATH),
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if claude_response is None:
            raise HTTPException(status_code=500, detail="Failed to get response from Claude CLI")
        
        # Extract JSON if response_format specifies it
        if response_format and response_format.get("type") == "json_object":
            # Try to extract JSON from Claude's response
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',  # Markdown JSON block
                r'```\s*([\s\S]*?)\s*```',       # Generic code block  
                r'\{[\s\S]*\}'                   # Raw JSON object
            ]
            
            extracted_json = None
            for pattern in json_patterns:
                matches = re.findall(pattern, claude_response)
                if matches:
                    # Try to parse the first match
                    try:
                        json_str = matches[0] if pattern != r'\{[\s\S]*\}' else claude_response
                        # Find the JSON object in the string
                        if pattern == r'\{[\s\S]*\}':
                            # Extract just the JSON part
                            start = json_str.find('{')
                            end = json_str.rfind('}') + 1
                            if start >= 0 and end > start:
                                json_str = json_str[start:end]
                        extracted_json = json.loads(json_str)
                        # Successfully parsed - use the JSON string as response
                        claude_response = json.dumps(extracted_json)
                        logger.info(f"Extracted JSON from Claude response: {claude_response[:100]}...")
                        break
                    except json.JSONDecodeError:
                        continue
            
            if not extracted_json:
                logger.warning("Failed to extract valid JSON from Claude response despite response_format")
        
        # Build OpenAI-compatible response
        response_payload = {
            "id": f"poc-claude-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": data.get("model", "poc/claude-mcp"),
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
        
        logger.success("Sending response back to client")
        return JSONResponse(content=response_payload)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Always clean up MCP file
        if mcp_file_written_path:
            remove_dynamic_mcp_json(mcp_file_written_path)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "claude_cli_path": CLAUDE_CLI_PATH,
        "working_directory": str(POC_TARGET_DIR),
        "mcp_support": True
    }

# --- Test Client ---
async def test_mcp_proxy():
    """Test the MCP proxy with various configurations."""
    await asyncio.sleep(2)  # Give server time to start
    
    logger.info("🚀 Testing MCP Proxy Server")
    
    # Test 1: Basic call with default MCP
    test_cases = [
        {
            "name": "Default MCP (all tools)",
            "payload": {
                "model": "max/test-default-mcp",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What tools do you have available?"}
                ]
            }
        },
        {
            "name": "Custom MCP (only perplexity)",
            "payload": {
                "model": "max/test-custom-mcp",
                "messages": [
                    {"role": "user", "content": "Can you use perplexity to search for 'Model Context Protocol'?"}
                ],
                "mcp_config": {
                    "mcpServers": {
                        "perplexity-ask": {
                            "command": "npx",
                            "args": ["-y", "server-perplexity-ask"],
                            "env": {"PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY", "")}
                        }
                    }
                }
            }
        },
        {
            "name": "No tools (empty MCP)",
            "payload": {
                "model": "max/test-no-tools",
                "messages": [
                    {"role": "user", "content": "Hello! Can you see any tools?"}
                ],
                "mcp_config": {"mcpServers": {}}
            }
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for test in test_cases:
            logger.info(f"\n📋 Test: {test['name']}")
            logger.debug(f"Payload: {json.dumps(test['payload'], indent=2)}")
            
            try:
                response = await client.post(
                    FASTAPI_POC_ENDPOINT_URL,
                    json=test["payload"],
                    timeout=120.0
                )
                
                logger.info(f"Status: {response.status_code}")
                response.raise_for_status()
                
                data = response.json()
                if data.get("choices"):
                    content = data["choices"][0]["message"]["content"]
                    logger.success(f"Response: {content[:200]}...")
                    
            except Exception as e:
                logger.error(f"Test failed: {e}")

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
    logger.info(f"Server will run on: {POC_SERVER_HOST}:{POC_SERVER_PORT}")
    
    # Check for command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run test client
        logger.info("Running in test mode")
        asyncio.run(test_mcp_proxy())
    else:
        # Run server
        logger.info("Starting MCP-enhanced Claude proxy server...")
        logger.info("Run with --test in another terminal to test")
        uvicorn.run(
            app,
            host=POC_SERVER_HOST,
            port=POC_SERVER_PORT,
            log_level="info"
        )