# LLM CLI Configuration Schema

## Overview

The unified LLM CLI supports configuration through:
1. **CLI Arguments** - Direct command-line options
2. **Configuration Files** - JSON or YAML files with full settings
3. **Mixed Mode** - Config files with CLI overrides

## Configuration Schema

### Full Configuration Object

```json
{
  "model": "string",              // Required: Model identifier (e.g., "gpt-4", "claude-3")
  "messages": [                   // Required: Conversation messages
    {
      "role": "system|user|assistant",
      "content": "string"
    }
  ],
  "temperature": 0.0-2.0,         // Optional: Creativity level (default: 1.0)
  "max_tokens": "integer",        // Optional: Maximum response length
  "top_p": 0.0-1.0,              // Optional: Nucleus sampling
  "frequency_penalty": -2.0-2.0,  // Optional: Reduce repetition
  "presence_penalty": -2.0-2.0,   // Optional: Encourage new topics
  
  "validation": [                 // Optional: Validation strategies
    {
      "strategy": "string",       // Strategy name (json, code, schema, etc.)
      "max_attempts": "integer",  // Max validation attempts
      "language": "string",       // For code validation
      "schema": "object"          // For schema validation
    }
  ],
  
  "retry_config": {               // Optional: Retry configuration
    "max_attempts": "integer",    // Maximum retry attempts (default: 3)
    "backoff_factor": "float",    // Exponential backoff multiplier
    "initial_delay": "float",     // Initial retry delay in seconds
    "max_delay": "float"          // Maximum retry delay
  },
  
  "response_format": {            // Optional: Response format constraints
    "type": "json_object|text"    // Force JSON responses
  },
  
  "tools": [                      // Optional: Function calling tools
    {
      "type": "function",
      "function": {
        "name": "string",
        "description": "string",
        "parameters": "object"
      }
    }
  ],
  
  "stream": "boolean",            // Optional: Stream responses
  "logprobs": "boolean",          // Optional: Include log probabilities
  "stop": ["string"],             // Optional: Stop sequences
  "user": "string"                // Optional: User identifier for tracking
}
```

## CLI Command Mapping

### `ask` Command Options

| CLI Option | Config Field | Description |
|------------|--------------|-------------|
| `--model, -m` | `model` | Override model selection |
| `--validate, -v` | `validation` | Add validation strategies |
| `--temp, -t` | `temperature` | Set temperature |
| `--max-tokens` | `max_tokens` | Limit response length |
| `--system, -s` | Prepends to `messages` | Add system prompt |
| `--json, -j` | `response_format` | Request JSON output |

### `call` Command Options

| CLI Option | Config Field | Description |
|------------|--------------|-------------|
| `--prompt, -p` | `messages` | Override prompt |
| `--model, -m` | `model` | Override model |
| `--validate, -v` | `validation` | Override validation |

## Validation Strategies

Available validation strategies:

- **`json`** - Validates JSON structure
- **`code`** - Validates code syntax (specify language)
- **`schema`** - Validates against JSON Schema
- **`length`** - Validates response length
- **`contains`** - Validates required content
- **`regex`** - Validates with regex patterns
- **`custom`** - Custom validation function

## Example Configurations

### Basic Chat Configuration

```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
}
```

### Code Generation with Validation

```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are an expert Python developer."},
    {"role": "user", "content": "Write a binary search function"}
  ],
  "temperature": 0.2,
  "validation": [
    {
      "strategy": "code",
      "language": "python",
      "max_attempts": 3
    }
  ],
  "retry_config": {
    "max_attempts": 3,
    "backoff_factor": 2.0
  }
}
```

### JSON Response with Schema Validation

```yaml
model: gpt-4
messages:
  - role: system
    content: You are a data formatter.
  - role: user
    content: Generate user profile data
response_format:
  type: json_object
validation:
  - strategy: json
  - strategy: schema
    schema:
      type: object
      required: [name, email, age]
      properties:
        name:
          type: string
        email:
          type: string
          format: email
        age:
          type: integer
          minimum: 0
```

### Multi-Step Validation

```json
{
  "model": "claude-3-opus",
  "messages": [
    {"role": "user", "content": "Create a REST API endpoint"}
  ],
  "validation": [
    {
      "strategy": "code",
      "language": "python"
    },
    {
      "strategy": "contains",
      "patterns": ["@app.route", "return jsonify"]
    },
    {
      "strategy": "length",
      "min_length": 100,
      "max_length": 1000
    }
  ]
}
```

## Environment Variables

The CLI respects these environment variables:

- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key
- `LLM_DEFAULT_MODEL` - Default model if not specified
- `LLM_CONFIG_PATH` - Default config file location

## Best Practices

1. **Start Simple**: Use CLI arguments for quick tasks
2. **Use Config Files**: For complex, repeatable configurations
3. **Version Control**: Store config files in version control
4. **Validation Chains**: Order validators from simple to complex
5. **Retry Strategy**: Configure retries for production use

## Integration with Slash Commands

When slash commands are generated, they preserve all configuration options:

```json
{
  "name": "llm-ask-validated",
  "description": "Ask LLM with code validation",
  "args": [
    {"name": "prompt", "type": "string"},
    {"name": "model", "type": "string", "optional": true},
    {"name": "validate", "type": "array", "optional": true}
  ],
  "execute": "uv run python -m llm_call.cli.main_unified ask \"${prompt}\" ${model} ${validate}"
}
```

This ensures that complex configurations work seamlessly with Claude Code's slash command system.