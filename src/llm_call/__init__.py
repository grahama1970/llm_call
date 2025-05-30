"""
LLM Call - Universal LLM Interface with Smart Validation

A flexible library that lets you interact with any LLM through a unified interface.
"""

# Core functionality
from llm_call.core.caller import make_llm_request
from llm_call.core.base import ValidationResult, ValidationStrategy
from llm_call.core.retry import retry_with_validation, RetryConfig
from llm_call.core.strategies import registry, validator
from llm_call.core.config.loader import load_configuration

# Convenience API
from llm_call.api import (
    ask,
    chat,
    call,
    ask_sync,
    chat_sync,
    call_sync,
    register_validator,
    ChatSession
)

# Version
__version__ = "1.0.0"

# Public API
__all__ = [
    # Convenience functions (matches README)
    "ask",
    "chat",
    "call",
    "ask_sync",
    "chat_sync", 
    "call_sync",
    "ChatSession",
    "register_validator",
    
    # Core functionality
    "make_llm_request",
    "ValidationResult",
    "ValidationStrategy",
    "retry_with_validation",
    "RetryConfig",
    "registry",
    "validator",
    "load_configuration",
]