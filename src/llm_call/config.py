"""Configuration constants for LLM Call module."""

import os

# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSION", 1024))

# Default LLM configuration
DEFAULT_CONFIG = {
    "llm_config": {
        "model": "anthropic/max",  # <-- triggers the routing logic
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello from Claude Code Max!"}
        ],
        "response_format": "json",
        "stream": False,
        "max_tokens": 1000,
    }
}

# Legacy config for backwards compatibility
config = DEFAULT_CONFIG
updates = DEFAULT_CONFIG