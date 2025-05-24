"""
Polling Server for LLM Calls

Provides REST API endpoints for submitting and polling long-running LLM tasks.

Endpoints:
    POST /v1/tasks/submit - Submit a new LLM task
    GET  /v1/tasks/{task_id}/status - Get task status
    GET  /v1/tasks/{task_id}/wait - Wait for task completion
    POST /v1/tasks/{task_id}/cancel - Cancel a task
    GET  /health - Health check
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

from llm_call.proof_of_concept.litellm_client_poc_polling import (
    llm_call, get_task_status, wait_for_task, cancel_task,
    polling_manager
)


# Pydantic models for API
class LLMConfig(BaseModel):
    """LLM configuration for task submission."""
    model: str = Field(..., description="Model name (e.g., 'gpt-3.5-turbo', 'max/text-general')")
    messages: list = Field(..., description="Chat messages")
    temperature: Optional[float] = Field(None, description="Temperature for sampling")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    validation: Optional[list] = Field(None, description="Validation strategies")
    retry_config: Optional[dict] = Field(None, description="Retry configuration")
    mcp_config: Optional[dict] = Field(None, description="MCP configuration for Claude")


class TaskSubmitRequest(BaseModel):
    """Request for task submission."""
    llm_config: LLMConfig
    polling_mode: bool = Field(True, description="If True, returns immediately with task_id")
    timeout: Optional[float] = Field(None, description="Timeout in seconds (for non-polling mode)")


class TaskSubmitResponse(BaseModel):
    """Response for task submission."""
    task_id: str
    status: str
    message: Optional[str] = None


class TaskStatusResponse(BaseModel):
    """Response for task status."""
    task_id: str
    status: str
    progress: int = 0
    start_time: str
    end_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting polling server...")
    await polling_manager.start_cleanup_job(interval=1800)  # 30 min cleanup
    
    yield
    
    # Shutdown
    logger.info("Shutting down polling server...")
    await polling_manager.shutdown()


# Create FastAPI app
app = FastAPI(
    title="LLM Polling Server",
    description="REST API for long-running LLM calls with polling support",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/v1/tasks/submit", response_model=TaskSubmitResponse)
async def submit_task(request: TaskSubmitRequest) -> TaskSubmitResponse:
    """Submit a new LLM task."""
    try:
        # Convert Pydantic model to dict
        llm_config = request.llm_config.model_dump(exclude_none=True)
        
        # Submit task
        result = await llm_call(
            llm_config,
            polling_mode=request.polling_mode,
            timeout=request.timeout
        )
        
        if request.polling_mode and isinstance(result, dict) and "task_id" in result:
            # Polling mode - return task ID
            return TaskSubmitResponse(
                task_id=result["task_id"],
                status=result["status"],
                message=result.get("message")
            )
        elif result:
            # Immediate mode - create a completed task entry
            task_id = f"immediate_{hash(str(llm_config)) & 0xffffff:06x}"
            return TaskSubmitResponse(
                task_id=task_id,
                status="completed",
                message="Task completed immediately"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to submit task")
            
    except Exception as e:
        logger.error(f"Task submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_status(task_id: str) -> TaskStatusResponse:
    """Get task status."""
    status = await get_task_status(task_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskStatusResponse(**status)


@app.get("/v1/tasks/{task_id}/wait")
async def wait_for_completion(
    task_id: str,
    timeout: float = 300.0,
    poll_interval: float = 2.0
) -> Dict[str, Any]:
    """
    Wait for task completion (long polling).
    
    This endpoint will block until the task completes or times out.
    """
    try:
        result = await wait_for_task(task_id, timeout=timeout)
        return {
            "task_id": task_id,
            "status": "completed",
            "result": result
        }
    except TimeoutError:
        return {
            "task_id": task_id,
            "status": "timeout",
            "error": f"Task timed out after {timeout}s"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        return {
            "task_id": task_id,
            "status": "failed",
            "error": str(e)
        }


@app.post("/v1/tasks/{task_id}/cancel")
async def cancel_task_endpoint(task_id: str) -> Dict[str, Any]:
    """Cancel a running task."""
    cancelled = await cancel_task(task_id)
    
    if cancelled:
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled successfully"
        }
    else:
        status = await get_task_status(task_id)
        if not status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        else:
            return {
                "task_id": task_id,
                "status": status["status"],
                "message": f"Task cannot be cancelled (current status: {status['status']})"
            }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Check database
    try:
        active_tasks = polling_manager.db.get_active_tasks()
        db_healthy = True
    except Exception as e:
        db_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # Check proxy if needed
    proxy_healthy = True
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3010/health", timeout=2.0)
            proxy_healthy = response.status_code == 200
    except:
        proxy_healthy = False
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "ok" if db_healthy else "error",
        "proxy": "ok" if proxy_healthy else "error",
        "active_tasks": len(active_tasks) if db_healthy else "unknown"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "LLM Polling Server",
        "version": "1.0.0",
        "endpoints": {
            "submit_task": "POST /v1/tasks/submit",
            "get_status": "GET /v1/tasks/{task_id}/status",
            "wait_for_task": "GET /v1/tasks/{task_id}/wait",
            "cancel_task": "POST /v1/tasks/{task_id}/cancel",
            "health": "GET /health"
        }
    }


# Error handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting LLM Polling Server on http://localhost:8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )