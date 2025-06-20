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
from loguru import logger

from llm_call.core.caller import make_llm_request
from llm_call.core.config.loader import load_configuration
from llm_call.core.strategies import registry
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache

# Initialize cache on module import if enabled
_cache_initialized = False
_settings = load_configuration()

if _settings.retry.enable_cache and not _cache_initialized:
    try:
        initialize_litellm_cache()
        _cache_initialized = True
    except Exception as e:
        # Log but don't fail if cache can't be initialized
        import warnings
        warnings.warn(f"Could not initialize cache: {e}")


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
    timeout: Optional[float] = None,
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
    if timeout is not None:
        config["timeout"] = timeout
    
    if retry_max is not None:
        config["retry_config"] = {"max_attempts": retry_max}
    
    # Make the request
    response = await make_llm_request(config)
    
    # Extract content from response
    if isinstance(response, dict):
        # Handle OpenAI-style response
        if "choices" in response and response["choices"]:
            return response["choices"][0]["message"]["content"]
        # Handle simple content response
        elif "content" in response:
            return response["content"]
        else:
            return response
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


class ChatSessionSync:
    """
    Synchronous wrapper for ChatSession.
    
    Provides the same interface as ChatSession but with synchronous methods.
    """
    
    def __init__(self, chat_session: Optional[ChatSession] = None, **kwargs):
        if chat_session:
            self._session = chat_session
        else:
            # Create a new ChatSession with provided kwargs
            self._session = ChatSession(**kwargs)
    
    def send(self, message: str) -> str:
        """
        Send a message and get a response synchronously.
        
        Args:
            message: The message to send
            
        Returns:
            The assistant's response
        """
        return asyncio.run(self._session.send(message))
    
    def clear_history(self):
        """Clear the conversation history, keeping only system prompt if present."""
        self._session.clear_history()
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history."""
        return self._session.get_history()
    
    @property
    def model(self):
        """Get the model being used."""
        return self._session.model
    
    @property
    def temperature(self):
        """Get the temperature setting."""
        return self._session.temperature
    
    @property
    def history(self):
        """Get the conversation history."""
        return self._session.history


# Synchronous wrappers for convenience
def ask_sync(*args, **kwargs) -> Union[str, Dict[str, Any]]:
    """Synchronous version of ask()."""
    return asyncio.run(ask(*args, **kwargs))


def chat_sync(*args, **kwargs) -> ChatSessionSync:
    """Synchronous version of chat()."""
    session = asyncio.run(chat(*args, **kwargs))
    return ChatSessionSync(session)


def call_sync(*args, **kwargs) -> Union[str, Dict[str, Any]]:
    """Synchronous version of call()."""
    return asyncio.run(call(*args, **kwargs))


# Custom validator registration helper
def register_validator(name: str, validator_func=None):
    """
    Register a custom validation function or decorator.
    
    Can be used as a decorator or direct function:
    
    As decorator:
        >>> @register_validator("sql_safe")
        >>> def validate_sql_safety(response: str, context: dict) -> bool:
        ...     dangerous_keywords = ["DROP", "DELETE", "TRUNCATE"]
        ...     return not any(keyword in response.upper() for keyword in dangerous_keywords)
    
    Direct registration:
        >>> def my_validator(response: str, context: dict) -> bool:
        ...     return True
        >>> register_validator("my_validator", my_validator)
    """
    from llm_call.core.strategies import validator as strategy_validator
    from llm_call.core.base import BaseValidator
    
    from llm_call.core.base import ValidationResult
    
    if validator_func is None:
        # Used as decorator
        def decorator(func):
            # Create a validator class that wraps the function
            class FunctionValidator(BaseValidator):
                @property
                def name(self) -> str:
                    return name
                
                def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
                    try:
                        result = func(response, context or {})
                        return ValidationResult(
                            valid=bool(result),
                            error=None if result else f"Validation '{name}' failed"
                        )
                    except Exception as e:
                        return ValidationResult(
                            valid=False,
                            error=f"Validation '{name}' error: {str(e)}"
                        )
            
            # Set the validator name
            FunctionValidator._validator_name = name
            # Register it
            return strategy_validator(name)(FunctionValidator)
        return decorator
    else:
        # Direct registration
        class FunctionValidator(BaseValidator):
            @property
            def name(self) -> str:
                return name
            
            def validate(self, response: str, context: Optional[dict] = None) -> ValidationResult:
                try:
                    result = validator_func(response, context or {})
                    return ValidationResult(
                        valid=bool(result),
                        error=None if result else f"Validation '{name}' failed"
                    )
                except Exception as e:
                    return ValidationResult(
                        valid=False,
                        error=f"Validation '{name}' error: {str(e)}"
                    )
        
        FunctionValidator._validator_name = name
        return strategy_validator(name)(FunctionValidator)


# Validation helper function
async def validate_llm_response(
    response: str,
    validators: Union[str, List[str]],
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Validate an LLM response using one or more validators.
    
    Args:
        response: The LLM response to validate
        validators: Single validator name or list of validator names
        context: Optional context for validation
        
    Returns:
        True if all validators pass, False otherwise
        
    Example:
        >>> is_valid = await validate_llm_response(
        ...     "SELECT * FROM users",
        ...     ["sql", "no_injection"],
        ...     {"database": "mysql"}
        ... )
    """
    from llm_call.core.strategies import get_validator
    from llm_call.core.retry import validate_response as validate_with_strategy
    
    if isinstance(validators, str):
        validators = [validators]
    
    if context is None:
        context = {}
    
    try:
        # Validate with each validator
        for validator_name in validators:
            try:
                # Get validator instance
                validator = get_validator(validator_name)
                
                # Create a simple strategy wrapper
                class SimpleStrategy:
                    def __init__(self, validator):
                        self.validator = validator
                        self.name = validator_name
                    
                    async def validate(self, response, context):
                        # Check if validator has async validate method
                        if hasattr(self.validator, 'validate'):
                            result = self.validator.validate(response, context)
                            # If it's a coroutine, await it
                            if asyncio.iscoroutine(result):
                                return await result
                            return result
                        return None
                
                strategy = SimpleStrategy(validator)
                
                # Validate
                result = await validate_with_strategy(strategy, response, context)
                if not result.valid:
                    return False
                    
            except ValueError as e:
                # Validator not found
                logger.warning(f"Validator '{validator_name}' not found: {e}")
                return False
            except Exception as e:
                logger.error(f"Validation error with '{validator_name}': {e}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        return False


def validate_llm_response_sync(
    response: str,
    validators: Union[str, List[str]],
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Synchronous version of validate_llm_response."""
    return asyncio.run(validate_llm_response(response, validators, context))


# Provider helper function  
def get_available_providers() -> List[str]:
    """
    Get a list of available LLM providers.
    
    Returns:
        List of provider names that can be used with model specifications
        
    Example:
        >>> providers = get_available_providers()
        >>> print(providers)
        ['openai', 'anthropic', 'google', 'max', 'groq', 'together']
    """
    # Common providers supported by litellm
    providers = [
        'openai',
        'anthropic', 
        'google',
        'max',
        'groq',
        'together',
        'cohere',
        'replicate',
        'huggingface',
        'azure',
        'bedrock',
        'vertex_ai',
        'palm',
        'ai21',
        'baseten',
        'openrouter',
        'aleph_alpha',
        'nlp_cloud',
        'petals',
        'vllm',
        'ollama',
        'deepinfra',
        'perplexity',
        'anyscale',
        'mistral',
        'groq',
        'deepseek',
        'codestral',
        'text-completion-openai',
        'text-completion-cohere',
        'custom'
    ]
    
    # Remove duplicates and sort
    return sorted(list(set(providers)))