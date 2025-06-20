"""LLM Call - Unified interface for language model access"""

from typing import Optional, Dict, Any, List

# Import core functionality with absolute imports
from llm_call.core.caller import make_llm_request
from llm_call.core.validation.retry_manager import ValidationError
from llm_call.core import config as get_config
from llm_call.core.strategies import VALIDATION_STRATEGIES, registry as STRATEGIES
from llm_call.core.router import resolve_route as route_request

# Import API functions
from llm_call.api import (
    ask, chat, call, ask_sync, chat_sync, call_sync, 
    ChatSession, ChatSessionSync, register_validator,
    get_available_providers, validate_llm_response_sync
)

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
# Import new modules with absolute imports
from llm_call.multimodal import process_multimodal, process_multimodal_sync
from llm_call.conversation import ConversationManager, ConversationManagerSync
from llm_call.slash_commands import SlashCommandRegistry

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
    "ChatSessionSync",
    "register_validator",
    "get_available_providers",
    "validate_llm_response_sync",
    "get_config",
    "VALIDATION_STRATEGIES",
    "STRATEGIES",
    "route_request",
    "process_multimodal",
    "process_multimodal_sync",
    "ConversationManager",
    "ConversationManagerSync",
    "SlashCommandRegistry"
]
