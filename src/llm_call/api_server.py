"""
Module: api_server.py
Description: FastAPI server for LLM Call

External Dependencies:
- fastapi: https://fastapi.tiangolo.com/
- uvicorn: https://www.uvicorn.org/

Sample Input:
>>> GET /health

Expected Output:
>>> {"status": "healthy"}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="LLM Call API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    status = "healthy"
    services = {}
    
    # Check Redis
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        # Parse Redis URL
        if redis_url.startswith("redis://"):
            host_port = redis_url.replace("redis://", "").split("/")[0]
            host = host_port.split(":")[0]
            port = int(host_port.split(":")[1]) if ":" in host_port else 6379
        else:
            host, port = 'localhost', 6379
            
        r = redis.Redis(host=host, port=port, decode_responses=True, socket_timeout=1)
        r.ping()
        services["redis"] = "ok"
    except Exception as e:
        services["redis"] = f"unavailable: {str(e)}"
        status = "degraded"
    
    return {
        "status": status,
        "services": services
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: Dict[str, Any]):
    """OpenAI-compatible chat completions endpoint."""
    try:
        # Use make_llm_request
        from llm_call.core.caller import make_llm_request
        
        response = await make_llm_request(request)
        
        # Format response as OpenAI style if needed
        if hasattr(response, 'model_dump'):
            return response.model_dump()
        elif isinstance(response, dict):
            return response
        else:
            return {
                "choices": [{
                    "message": {"content": str(response)},
                    "finish_reason": "stop"
                }],
                "model": request.get("model", "gpt-3.5-turbo")
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
