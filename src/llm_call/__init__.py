"""LLM Call - Unified interface for language model access"""

from typing import Optional, Dict, Any, List

# Import core functionality
try:
    from .core.caller import make_llm_request
    from .core.base import ValidationError
except ImportError:
    make_llm_request = None
    ValidationError = Exception

# Import API functions
try:
    from .api import ask, chat, call, ask_sync, chat_sync, call_sync, ChatSession, register_validator
except ImportError as e:
    # If imports fail, provide None fallbacks
    ask = None
    chat = None
    call = None
    ask_sync = None
    chat_sync = None
    call_sync = None
    ChatSession = None
    register_validator = None

# Convenience wrapper
async def llm_call(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    **kwargs
) -> Any:
    """Make a call to an LLM with simple interface."""
    if make_llm_request is None:
        raise ImportError("LLM Call core not properly installed")
    
    config = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        **kwargs
    }
    
    return await make_llm_request(config)

# Export main interfaces
__version__ = "1.0.0"
__all__ = [
    "llm_call", 
    "make_llm_request", 
    "ValidationError",
    "ask",
    "chat",
    "call",
    "ask_sync",
    "chat_sync",
    "call_sync",
    "ChatSession",
    "register_validator"
]
