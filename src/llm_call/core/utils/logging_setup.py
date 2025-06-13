"""
Logging setup module for llm_call package.
Module: logging_setup.py
Description: Functions for logging setup operations

This module provides centralized logging configuration using loguru.
It configures console and optional file logging with customizable levels.

Links:
- Loguru documentation: https://loguru.readthedocs.io/

Sample usage:
    from llm_call.core.utils.logging_setup import setup_logging
    setup_logging(level="DEBUG", log_file="app.log")

Expected output:
    Configured logger with console and file sinks
"""

import os
import sys
from typing import Optional
from loguru import logger


def get_logger(name: str = None):
    """Get a logger instance."""
    return logger.bind(name=name) if name else logger


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
    colorize: bool = True
) -> None:
    """
    Configure loguru logger for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for log output
        rotation: Log rotation policy (e.g., "10 MB", "1 day")
        retention: Log retention policy (e.g., "1 week", "10 files")
        colorize: Whether to colorize console output
    """
    # Remove default handler
    logger.remove()
    
    # Get level from environment if not specified
    env_level = os.getenv("LOG_LEVEL", level).upper()
    
    # Console sink configuration - matching POC format
    console_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # Add console sink
    logger.add(
        sys.stderr,
        format=console_format,
        level=env_level,
        colorize=colorize
    )
    
    # Add file sink if specified
    if log_file:
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} - "
            "{message}"
        )
        logger.add(
            log_file,
            format=file_format,
            level=env_level,
            rotation=rotation,
            retention=retention,
            encoding="utf-8"
        )
    
    # Configure for FastAPI/Uvicorn compatibility (from POC)
    if colorize and "uvicorn" in sys.modules:
        # Special handling for Uvicorn to ensure colors work
        import uvicorn.config
        uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(levelprefix)s %(message)s"
        uvicorn.config.LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
    
    logger.info(f"Logging configured at {env_level} level")
    if log_file:
        logger.info(f"File logging enabled: {log_file}")


# Test function
if __name__ == "__main__":
    import sys
    
    # Test basic logging setup
    setup_logging(level="DEBUG")
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test with file output
    setup_logging(level="INFO", log_file="test_log.log")
    logger.info("Testing file logging")
    
    # Verify file was created
    if os.path.exists("test_log.log"):
        logger.success(" File logging verified")
        # Clean up
        os.remove("test_log.log")
    else:
        logger.error(" File logging failed")
        sys.exit(1)
    
    logger.success(" All logging tests passed")
    sys.exit(0)