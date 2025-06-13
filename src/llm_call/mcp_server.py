"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, AsyncGenerator
import json
import asyncio
import os
from pathlib import Path
Module: mcp_server.py
Description: Implementation of mcp server functionality
Description: Implementation of mcp server functionality

from llm_call.api import call as llm_call
from llm_call.core.api.mcp_handler_wrapper import MCPHandler
from llm_call.core.config_manager import ConfigManager

app = FastAPI(title="Claude Max Proxy MCP Server", version="1.0.0")

# Initialize components
mcp_handler = MCPHandler()
config_manager = ConfigManager()

class MCPRequest(BaseModel):
    command: str
    params: Dict[str, Any]

class ChatRequest(BaseModel):
    prompt: str
    context: Optional[List[Dict[str, str]]] = []
    model: str = "max/claude-3-opus-20240229"
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7
    stream: bool = False
    mcp_servers: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    working_directory: Optional[str] = None

@app.post("/mcp/execute")
async def execute_mcp_command(request: MCPRequest):
    """Main MCP endpoint that routes commands"""
"""
MCP Server implementation for llm_call
Exposes LLM routing and validation capabilities as an MCP service
    
    command = request.command
    params = request.params
    
    try:
        if command == "chat":
            return await handle_chat(ChatRequest(**params))
        
        elif command == "validate":
            return await handle_validation(params)
        
        elif command == "analyze_code":
            return await handle_code_analysis(params)
        
        elif command == "configure_mcp":
            return await handle_mcp_configuration(params)
        
        else:
            raise HTTPException(400, f"Unknown command: {command}")
    except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "command": command
        }

async def handle_chat(request: ChatRequest):
    """Handle chat requests with optional MCP tool configuration"""
    
    # Set working directory if specified
    working_dir = request.working_directory or os.getcwd()
    
    # Configure MCP servers if specified
    mcp_config = None
    if request.mcp_servers:
        mcp_config = mcp_handler.get_mcp_config(
            mcp_servers=request.mcp_servers,
            working_directory=working_dir
        )
    
    # Build messages
    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})
    
    # Add context messages
    for msg in request.context:
        messages.append(msg)
    
    # Add current prompt
    messages.append({"role": "user", "content": request.prompt})
    
    # Handle streaming
    if request.stream:
        return StreamingResponse(
            stream_chat_response(request.model, messages, mcp_config, working_dir),
            media_type="text/event-stream"
        )
    
    # Non-streaming response
    try:
        # Create temporary MCP config if needed
        temp_config_path = None
        if mcp_config and request.model.startswith("max/"):
            temp_config_path = mcp_handler.write_temp_config(mcp_config, working_dir)
        
        try:
            response = await llm_call(
                prompt=messages[-1]["content"],
                model=request.model,
                messages=messages[:-1] if len(messages) > 1 else None,
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )
            
            # response is a string when using the simplified API
            return {
                "type": "chat_response",
                "content": response if isinstance(response, str) else response.get("content", ""),
                "model": request.model,
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "metadata": {
                    "mcp_servers": request.mcp_servers or [],
                    "working_directory": working_dir
                }
            }
        finally:
            # Clean up temporary config
            if temp_config_path:
                mcp_handler.cleanup_temp_config(temp_config_path)
                
    except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "model": request.model
        }

async def stream_chat_response(
    model: str, 
    messages: List[Dict], 
    mcp_config: Optional[Dict],
    working_dir: str
) -> AsyncGenerator[str, None]:
    """Stream chat responses"""
    temp_config_path = None
    
    try:
        # Create temporary MCP config if needed
        if mcp_config and model.startswith("max/"):
            temp_config_path = mcp_handler.write_temp_config(mcp_config, working_dir)
        
        # Streaming not supported in simplified API, return full response
        response = await llm_call(
            prompt=messages[-1]["content"],
            model=model,
            messages=messages[:-1] if len(messages) > 1 else None
        )
        content = response if isinstance(response, str) else response.get("content", "")
        yield f"data: {json.dumps({'content': content})}\n\n"
        
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
    finally:
        # Clean up temporary config
        if temp_config_path:
            mcp_handler.cleanup_temp_config(temp_config_path)

async def handle_validation(params: Dict[str, Any]):
    """Handle validation requests using llm_call's validators"""
    
    validator_type = params.get("validator_type", "json")
    content = params.get("content", "")
    schema = params.get("schema", None)
    
    # Map validator types to actual validator functions
    validator_map = {
        "json": "json_validator",
        "code": "code_validator", 
        "python": "python_validator",
        "yaml": "yaml_validator"
    }
    
    validator_name = validator_map.get(validator_type)
    if not validator_name:
        return {"type": "error", "error": f"Unknown validator: {validator_type}"}
    
    try:
        # Build validation prompt
        prompt = f"Validate and fix the following {validator_type}:\n\n{content}"
        
        # Use llm_call with validation
        response = await llm_call(
            prompt=prompt,
            model="claude-3-haiku-20240307",  # Use faster model for validation
            validate=validator_name,
            max_retries=3
        )
        
        return {
            "type": "validation_response",
            "valid": True,
            "content": response if isinstance(response, str) else response.get("content", ""),
            "validator": validator_type
        }
    except Exception as e:
        return {
            "type": "validation_response",
            "valid": False,
            "error": str(e),
            "original_content": content,
            "validator": validator_type
        }

async def handle_code_analysis(params: Dict[str, Any]):
    """Handle code analysis requests"""
    
    code = params.get("code", "")
    language = params.get("language", "python")
    analysis_type = params.get("analysis_type", "review")
    
    prompts = {
        "review": f"Review this {language} code and provide detailed feedback on code quality, potential bugs, and improvements:\n```{language}\n{code}\n```",
        "optimize": f"Optimize this {language} code for better performance. Explain the optimizations:\n```{language}\n{code}\n```",
        "refactor": f"Refactor this {language} code for better readability and maintainability:\n```{language}\n{code}\n```",
        "security": f"Analyze this {language} code for security vulnerabilities and provide fixes:\n```{language}\n{code}\n```",
        "document": f"Add comprehensive documentation to this {language} code:\n```{language}\n{code}\n```"
    }
    
    prompt = prompts.get(analysis_type, prompts["review"])
    
    try:
        response = await llm_call(
            prompt=prompt,
            model="max/claude-3-opus-20240229",
            temperature=0.3  # Lower temperature for code analysis
        )
        
        return {
            "type": "code_analysis_response",
            "analysis_type": analysis_type,
            "language": language,
            "result": response if isinstance(response, str) else response.get("content", ""),
            "model": "max/claude-3-opus-20240229"
        }
    except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "analysis_type": analysis_type
        }

async def handle_mcp_configuration(params: Dict[str, Any]):
    """Handle MCP server configuration"""
    
    action = params.get("action", "list")
    
    if action == "list":
        # List available MCP servers with their configs
        available_servers = mcp_handler.get_available_servers()
        
        return {
            "type": "mcp_config_response",
            "action": "list",
            "servers": available_servers
        }
    
    elif action == "configure":
        # Configure specific MCP server
        server_name = params.get("server_name")
        config = params.get("config", {})
        
        success = mcp_handler.update_server_config(server_name, config)
        
        return {
            "type": "mcp_config_response",
            "action": "configured",
            "server": server_name,
            "success": success,
            "config": config
        }
    
    elif action == "test":
        # Test MCP server connection
        server_name = params.get("server_name")
        
        test_result = await mcp_handler.test_server(server_name)
        
        return {
            "type": "mcp_config_response",
            "action": "test",
            "server": server_name,
            "result": test_result
        }

@app.get("/mcp/info")
async def get_mcp_info():
    """Return MCP server information"""
    
    # Get available MCP servers
    mcp_servers = mcp_handler.get_available_servers()
    
    return {
        "name": "llm_call",
        "version": "1.0.0",
        "description": "Advanced LLM routing with Claude Code integration and MCP tool support",
        "capabilities": {
            "models": [
                "max/claude-3-opus-20240229",
                "max/claude-3-sonnet-20240229",
                "max/claude-3-haiku-20240307",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307",
                "gpt-4",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            "features": [
                "streaming",
                "validation",
                "retry_logic",
                "mcp_tools",
                "code_analysis",
                "multi_model_routing",
                "context_management"
            ],
            "validators": [
                "json",
                "code",
                "python",
                "yaml"
            ],
            "mcp_servers": [s["name"] for s in mcp_servers]
        },
        "commands": [
            {
                "name": "chat",
                "description": "Chat with LLMs using advanced routing and optional MCP tools",
                "params": {
                    "prompt": "User message",
                    "context": "Conversation history (array of role/content objects)",
                    "model": "Model to use (default: max/claude-3-opus-20240229)",
                    "mcp_servers": "List of MCP servers to enable",
                    "stream": "Enable streaming responses",
                    "working_directory": "Working directory for MCP tools"
                }
            },
            {
                "name": "validate",
                "description": "Validate and fix content using LLM-powered validators",
                "params": {
                    "content": "Content to validate",
                    "validator_type": "json|code|python|yaml",
                    "schema": "Optional schema for validation"
                }
            },
            {
                "name": "analyze_code",
                "description": "Analyze code with various strategies",
                "params": {
                    "code": "Code to analyze",
                    "language": "Programming language",
                    "analysis_type": "review|optimize|refactor|security|document"
                }
            },
            {
                "name": "configure_mcp",
                "description": "Configure MCP servers",
                "params": {
                    "action": "list|configure|test",
                    "server_name": "Name of MCP server (for configure/test)",
                    "config": "Configuration object (for configure)"
                }
            }
        ]
    }

@app.get("/mcp/health")
async def health_check():
    """Health check endpoint"""
    
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check MCP handler
    try:
        mcp_servers = mcp_handler.get_available_servers()
        health_status["components"]["mcp_handler"] = {
            "status": "healthy",
            "servers_available": len(mcp_servers)
        }
    except Exception as e:
        health_status["components"]["mcp_handler"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check if we can make LLM calls
    try:
        # Quick test with a simple prompt
        test_response = await llm_call(
            prompt="Hello",
            model="claude-3-haiku-20240307",
            max_tokens=10
        )
        health_status["components"]["llm_routing"] = {
            "status": "healthy",
            "test_model": "claude-3-haiku-20240307"
        }
    except Exception as e:
        health_status["components"]["llm_routing"] = {
            "status": "unhealthy", 
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)