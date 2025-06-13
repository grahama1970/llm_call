"""
Convenience API for llm_call package.
Module: api.py

Provides simple, user-friendly functions that match the README examples.
"""
# Security middleware - try to import if available
try:
    from granger_security_middleware_simple import GrangerSecurity, SecurityConfig
    # Initialize security
    _security = GrangerSecurity()
except ImportError:
    # If security middleware is not available, continue without it
    _security = None


import asyncio
from typing import Optional, List, Union, Dict, Any
from pathlib import Path

from llm_call.core.caller import make_llm_request
from llm_call.core.config.loader import load_configuration
from llm_call.core.strategies import registry


async def ask(
    prompt: str,
    model: Optional[str] = None,
    validate: Optional[Union[str, List[str]]] = None,
    system: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, str]] = None,
    retry_max: Optional[int] = None,
    stream: bool = False,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    Ask a single question to an LLM with optional validation.
    
    Args:
        prompt: The question or prompt to send
        model: Model to use (e.g., 'gpt-4', 'claude-3-opus', 'max/claude-3-5-sonnet')
        validate: Validation strategy or list of strategies
        system: System prompt to set context
        temperature: Sampling temperature (0.0 to 2.0)
        max_tokens: Maximum tokens in response
        response_format: Format specification (e.g., {"type": "json_object"})
        retry_max: Maximum retry attempts
        stream: Whether to stream the response
        **kwargs: Additional parameters passed to the LLM
        
    Returns:
        The LLM response as a string, or full response dict if streaming
        
    Examples:
        >>> response = await ask("What is Python?")
        >>> 
        >>> response = await ask(
        ...     "Generate a Python function to calculate fibonacci",
        ...     model="gpt-4",
        ...     validate=["code", "python"]
        ... )
    """
    # Build configuration
    config = {
        "messages": [{"role": "user", "content": prompt}],
        **kwargs
    }
    
    # Add system prompt if provided
    if system:
        config["messages"].insert(0, {"role": "system", "content": system})
    
    # Set model
    if model:
        config["model"] = model
    
    # Set parameters
    if temperature is not None:
        config["temperature"] = temperature
    if max_tokens is not None:
        config["max_tokens"] = max_tokens
    if response_format:
        config["response_format"] = response_format
    if stream:
        config["stream"] = stream
    
    # Configure validation
    if validate:
        if isinstance(validate, str):
            validate = [validate]
        config["validation"] = [{"type": v} for v in validate]
    
    # Configure retry
    if retry_max is not None:
        config["retry_config"] = {"max_attempts": retry_max}
    
    # Make the request
    response = await make_llm_request(config)
    
    # Extract content from response
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    elif hasattr(response, 'choices') and response.choices:
        return response.choices[0].message.content
    else:
        return response


async def chat(
    model: Optional[str] = None,
    system: Optional[str] = None,
    temperature: Optional[float] = None,
    history: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> "ChatSession":
    """
    Start an interactive chat session with an LLM.
    
    Args:
        model: Model to use for the chat
        system: System prompt to set assistant behavior
        temperature: Sampling temperature
        history: Previous conversation history
        **kwargs: Additional parameters
        
    Returns:
        A ChatSession object for managing the conversation
        
    Example:
        >>> session = await chat(model="gpt-4", system="You are a helpful assistant")
        >>> response = await session.send("Hello!")
        >>> print(response)
    """
    return ChatSession(
        model=model,
        system=system,
        temperature=temperature,
        history=history,
        **kwargs
    )


async def call(
    config: Union[str, Path, Dict[str, Any]],
    prompt: Optional[str] = None,
    model: Optional[str] = None,
    **overrides
) -> Union[str, Dict[str, Any]]:
    """
    Execute an LLM call using a configuration file or dict.
    
    Args:
        config: Path to config file (JSON/YAML) or config dict
        prompt: Override the prompt in the config
        model: Override the model in the config
        **overrides: Additional overrides for the config
        
    Returns:
        The LLM response
        
    Example:
        >>> response = await call("config.json", prompt="Override prompt")
        >>> 
        >>> response = await call({
        ...     "model": "gpt-4",
        ...     "messages": [{"role": "user", "content": "Hello"}]
        ... })
    """
    # Load config if it's a path
    if isinstance(config, (str, Path)):
        config_path = Path(config)
        if config_path.suffix == '.json':
            import json
            with open(config_path) as f:
                config_dict = json.load(f)
        elif config_path.suffix in ['.yaml', '.yml']:
            import yaml
            with open(config_path) as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    else:
        config_dict = config.copy()
    
    # Apply overrides
    if prompt:
        config_dict["messages"] = [{"role": "user", "content": prompt}]
    if model:
        config_dict["model"] = model
    
    config_dict.update(overrides)
    
    # Make the request
    response = await make_llm_request(config_dict)
    
    # Extract content
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    elif hasattr(response, 'choices') and response.choices:
        return response.choices[0].message.content
    else:
        return response


class ChatSession:
    """
    Manages an interactive chat session with an LLM.
    
    Maintains conversation history and context across multiple exchanges.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ):
        self.model = model or "gpt-3.5-turbo"
        self.temperature = temperature
        self.history = history or []
        self.kwargs = kwargs
        
        # Add system prompt if provided
        if system and not any(msg.get("role") == "system" for msg in self.history):
            self.history.insert(0, {"role": "system", "content": system})
    
    async def send(self, message: str) -> str:
        """
        Send a message and get a response.
        
        Args:
            message: The message to send
            
        Returns:
            The assistant's response'
        """
        # Add user message
        self.history.append({"role": "user", "content": message})
        
        # Build config
        config = {
            "model": self.model,
            "messages": self.history,
            **self.kwargs
        }
        
        if self.temperature is not None:
            config["temperature"] = self.temperature
        
        # Make request
        response = await make_llm_request(config)
        
        # Extract content
        if isinstance(response, dict) and "content" in response:
            content = response["content"]
        elif hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
        else:
            content = str(response)
        
        # Add to history
        self.history.append({"role": "assistant", "content": content})
        
        return content
    
    def clear_history(self):
        """Clear the conversation history, keeping only system prompt if present."""
        self.history = [msg for msg in self.history if msg.get("role") == "system"]
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self.history.copy()


# Synchronous wrappers for convenience
def ask_sync(*args, **kwargs) -> Union[str, Dict[str, Any]]:
    """Synchronous version of ask()."""
    return asyncio.run(ask(*args, **kwargs))


def chat_sync(*args, **kwargs) -> ChatSession:
    """Synchronous version of chat()."""
    return asyncio.run(chat(*args, **kwargs))


def call_sync(*args, **kwargs) -> Union[str, Dict[str, Any]]:
    """Synchronous version of call()."""
    return asyncio.run(call(*args, **kwargs))


# Custom validator registration helper
def register_validator(name: str):
    """
    Decorator to register a custom validation strategy.
    
    This is an alias for the @validator decorator to match README examples.
    
    Example:
        >>> @register_validator("sql_safe")
        >>> def validate_sql_safety(response: str, context: dict) -> bool:
        ...     dangerous_keywords = ["DROP", "DELETE", "TRUNCATE"]
        ...     return not any(keyword in response.upper() for keyword in dangerous_keywords)
    """
    from llm_call.core.strategies import validator
    return validator(name)