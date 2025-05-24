"""
LLM Config Structure Documentation

This file documents the complete structure of the llm_config dictionary
that users pass to make_llm_request().
"""

# Example 1: Basic LLM request
basic_config = {
    "model": "gpt-3.5-turbo",  # Required: model name
    "messages": [  # Required: conversation messages
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ],
    "temperature": 0.7,  # Optional: sampling temperature
    "max_tokens": 150,   # Optional: max response tokens
}

# Example 2: Request with validation
validated_config = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "List 5 programming languages"}
    ],
    "validation": [  # Optional: list of validation strategies
        {"type": "response_not_empty"},  # Basic validator
        {"type": "field_present", "params": {"field_name": "languages"}},  # Validator with params
    ],
    "retry_config": {  # Optional: retry configuration
        "max_attempts": 5,
        "backoff_factor": 2.0,
        "initial_delay": 1.0,
        "debug_mode": True
    }
}

# Example 3: JSON response with validation
json_config = {
    "model": "vertex_ai/gemini-1.5-flash",
    "messages": [
        {"role": "user", "content": "Return user info for John Doe as JSON"}
    ],
    "response_format": {"type": "json_object"},  # Request JSON response
    "validation": [
        {"type": "response_not_empty"},
        {"type": "json_string"},  # Validates JSON format
        {"type": "field_present", "params": {"field_name": "name"}},
        {"type": "field_present", "params": {"field_name": "age"}}
    ],
    "temperature": 0.1,
    "max_tokens": 250
}

# Example 4: Multimodal request
multimodal_config = {
    "model": "openai/gpt-4-vision",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "path/to/image.jpg"}}
            ]
        }
    ],
    "image_directory": "/path/to/images",  # For relative image paths
    "max_image_size_kb": 500,  # Optional: resize large images
    "validation": [{"type": "response_not_empty"}]
}

# Example 5: Claude proxy request (max/ prefix)
claude_config = {
    "model": "max/claude-3-opus",  # Routes to Claude proxy
    "messages": [
        {"role": "system", "content": "You are Claude."},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.5,
    "max_tokens": 500,
    "validation": [{"type": "response_not_empty"}]
}

# Example 6: Advanced validation with AI validator
ai_validated_config = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "Write a Python function to sort a list"}
    ],
    "validation": [
        {"type": "response_not_empty"},
        {
            "type": "ai_code_validator",  # Custom AI validator
            "params": {
                "validation_model": "gpt-3.5-turbo",
                "check_syntax": True,
                "check_logic": True
            }
        }
    ],
    "retry_config": {
        "max_attempts": 3,
        "debug_mode": True
    }
}

# Example 7: Complete config with all options
complete_config = {
    # Required fields
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are an expert programmer."},
        {"role": "user", "content": "Create a web scraper in Python"}
    ],
    
    # Optional LLM parameters
    "temperature": 0.3,
    "max_tokens": 1000,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stop": ["\n\n", "```"],
    
    # Response format
    "response_format": {"type": "json_object"},  # or None for text
    
    # Validation configuration
    "validation": [
        {"type": "response_not_empty"},
        {"type": "json_string"},
        {
            "type": "custom_validator",
            "params": {
                "min_length": 100,
                "max_length": 5000,
                "custom_param": "value"
            }
        }
    ],
    
    # Retry configuration
    "retry_config": {
        "max_attempts": 5,          # Max retry attempts (default: 3)
        "backoff_factor": 2.0,      # Exponential backoff factor (default: 2.0)
        "initial_delay": 1.0,       # Initial retry delay in seconds (default: 1.0)
        "max_delay": 60.0,          # Maximum retry delay (default: 60.0)
        "debug_mode": True,         # Enable debug logging (default: False)
        "enable_cache": True        # Enable response caching (default: True)
    },
    
    # Additional options (these are typically removed before API calls)
    "default_validate": True,  # Add default validator if none specified
    
    # For multimodal requests
    "image_directory": "/path/to/images",
    "max_image_size_kb": 1000,
}

"""
Key Points:

1. REQUIRED fields:
   - model: The LLM model identifier
   - messages: List of message dicts with 'role' and 'content'

2. OPTIONAL fields:
   - Standard LLM params: temperature, max_tokens, top_p, etc.
   - response_format: For JSON responses
   - validation: List of validation configurations
   - retry_config: Retry behavior configuration
   - Multimodal: image_directory, max_image_size_kb

3. Validation structure:
   - Each validator is a dict with 'type' and optional 'params'
   - Validators are applied in order
   - Failed validations trigger retries with feedback

4. Retry behavior:
   - On validation failure, the LLM's response is added to conversation
   - Clear error feedback is provided to the LLM
   - Conversation continues with extended history
   - Process repeats until validation passes or max attempts reached

5. Response handling:
   - Dict responses (Claude proxy): response["choices"][0]["message"]["content"]
   - ModelResponse objects (LiteLLM): response.choices[0].message.content
"""
