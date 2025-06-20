"""
Core module for llm_call package.
Module: __init__.py
Description: Package initialization and exports

This module initializes the core functionality including logging,
configuration, and exposes key components.
"""

from llm_call.core.base import ValidationResult, ValidationStrategy
from llm_call.core.retry import retry_with_validation, RetryConfig
from llm_call.core.strategies import registry, validator
from llm_call.core.utils.logging_setup import setup_logging
from llm_call.core.config.loader import load_configuration
from llm_call.core.caller import make_llm_request

# Initialize logging on import
setup_logging()

# Load global configuration
config = load_configuration()
settings = config  # Alias for compatibility
get_config = config  # Function-like access

__all__ = [
    "ValidationResult",
    "ValidationStrategy", 
    "retry_with_validation",
    "RetryConfig",
    "registry",
    "validator",
    "config",
    "settings",
    "get_config",
    "make_llm_request",
]