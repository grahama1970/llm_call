"""
FastAPI application for Claude CLI proxy server.
Module: main.py
Description: Functions for main operations

This module creates the main FastAPI application that proxies requests
to the Claude CLI, maintaining compatibility with OpenAI's API format.'

Links:
- FastAPI documentation: https://fastapi.tiangolo.com/

Sample usage:
    uvicorn llm_call.core.api.main:app --port 8001

Expected output:
    FastAPI server running on specified port
"""

from fastapi import FastAPI
from loguru import logger

from llm_call.core.config.loader import load_configuration

# Load settings at module level
settings = load_configuration()
from llm_call.core.api.handlers import router

# Create FastAPI app instance
app = FastAPI(
    title=settings.api.title,
    version=settings.api.version,
    description=settings.api.description,
    docs_url=settings.api.docs_url,
    redoc_url=settings.api.redoc_url
)

# Include the API routes
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Log server startup information."""
    logger.info(f"⚙️ Starting {settings.api.title} v{settings.api.version}")
    logger.info(f"📍 API endpoint: http://0.0.0.0:8001")
    logger.info(f"📚 Documentation: http://0.0.0.0:8001/docs")
    
    # Log enabled features from environment
    import os
    if os.getenv('ENABLE_LLM_VALIDATION', 'true').lower() == 'true':
        logger.info("✅ LLM validation enabled")
    if os.getenv('ENABLE_RL_ROUTING', 'true').lower() == 'true':
        logger.info("✅ RL-based routing enabled")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import os
    return {
        "status": "healthy",
        "service": settings.api.title,
        "version": settings.api.version,
        "features": {
            "validation": os.getenv('ENABLE_LLM_VALIDATION', 'true').lower() == 'true',
            "rl_routing": os.getenv('ENABLE_RL_ROUTING', 'true').lower() == 'true'
        }
    }


# Test function
if __name__ == "__main__":
    import uvicorn
    
    # Run the server for testing
    logger.info("Running API server in test mode...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )