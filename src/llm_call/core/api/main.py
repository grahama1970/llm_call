"""
FastAPI application for Claude CLI proxy server.

This module creates the main FastAPI application that proxies requests
to the Claude CLI, maintaining compatibility with OpenAI's API format.

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
    logger.info(f"⚙️ Starting {config.api.title} v{config.api.version}")
    logger.info(f"📍 Server configured on {config.claude_proxy.host}:{config.claude_proxy.port}")
    logger.info(f"🔧 Claude CLI path: {config.claude_proxy.cli_path}")
    logger.info(f"📂 Claude workspace: {config.claude_proxy.workspace_dir}")
    
    # Check if Claude CLI exists
    from pathlib import Path
    cli_path = Path(config.claude_proxy.cli_path)
    if not cli_path.is_file():
        logger.critical(f"❌ CRITICAL: Claude CLI not found at '{config.claude_proxy.cli_path}'")
        logger.critical("Please ensure CLAUDE_CLI_PATH is correct or update configuration")
    else:
        logger.success(f"✅ Claude CLI found at '{config.claude_proxy.cli_path}'")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": config.api.title,
        "version": config.api.version
    }


# Test function
if __name__ == "__main__":
    import uvicorn
    
    # Run the server for testing
    logger.info("Running API server in test mode...")
    uvicorn.run(
        app,
        host=config.claude_proxy.host,
        port=config.claude_proxy.port,
        log_level="info"
    )