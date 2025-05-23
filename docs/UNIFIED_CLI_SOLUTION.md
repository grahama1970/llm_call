# Unified LLM CLI Solution

## Overview

This document describes the unified CLI solution that addresses the requirement to "figure out the best way to include litellm config dict (model, settings, validation, etc.) with the CLI and automate slash command and MCP integration."

## Solution Architecture

### 1. **Unified CLI (`main_unified.py`)**

The unified CLI combines:
- **Simple Interface**: Basic commands (ask, chat, models) for quick tasks
- **Full Configuration**: Complete litellm config dict support
- **Auto-generation**: Slash commands generated automatically
- **Flexibility**: Config files, CLI options, or mixed mode

### 2. **Configuration Flow**

```
User Input → CLI Arguments → Config File → Build Config → LiteLLM Call
                    ↓             ↓            ↓
                Override      Load JSON/    Merge & 
                Options       YAML File     Validate
```

### 3. **Key Features**

#### Simple Commands
```bash
# Quick question
uv run python -m llm_call.cli.main_unified ask "What is Python?"

# With model selection
uv run python -m llm_call.cli.main_unified ask "Explain decorators" --model gpt-4

# With validation
uv run python -m llm_call.cli.main_unified ask "Write a function" --validate code
```

#### Advanced Configuration
```bash
# Using config file
uv run python -m llm_call.cli.main_unified call config.json

# Override config file settings
uv run python -m llm_call.cli.main_unified call config.json --model claude-3 --validate json

# Complex inline configuration
uv run python -m llm_call.cli.main_unified ask "Create API" \
  --model gpt-4 \
  --validate code \
  --validate imports \
  --temp 0.3 \
  --max-tokens 2000 \
  --system "You are an expert developer"
```

#### Auto-generated Slash Commands
```bash
# Generate slash commands for all CLI features
uv run python -m llm_call.cli.main_unified generate-claude

# Generates commands like:
# /llm-ask - Ask with full config options
# /llm-chat - Start chat session
# /llm-call - Use config file
# /llm-models - List models
# /llm-validators - List validation strategies
```

## Implementation Details

### 1. **Configuration Building**

The `build_llm_config()` function handles:
- Loading base config from files (JSON/YAML)
- Applying CLI overrides
- Building message arrays
- Setting up validation chains
- Configuring retry strategies

```python
def build_llm_config(
    prompt: str,
    model: Optional[str] = None,
    validation: Optional[List[str]] = None,
    retry_max: Optional[int] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    response_format: Optional[str] = None,
    config_file: Optional[Path] = None
) -> Dict[str, Any]:
```

### 2. **Integration with LiteLLM**

The unified CLI directly uses the existing `make_llm_request()` function:

```python
from ..core.caller import make_llm_request

# Build config from various sources
config = build_llm_config(...)

# Make the request with full config
response = make_llm_request(config)
```

### 3. **Slash Command Generation**

Using the universal mixin:

```python
from .slash_mcp_mixin import add_slash_mcp_commands

# One line adds all capabilities
add_slash_mcp_commands(app)
```

This automatically:
- Introspects all CLI commands
- Generates appropriate slash command configs
- Handles complex parameter types
- Preserves all options

## Benefits

### 1. **Simplicity**
- One CLI for all use cases
- Auto-generation means zero maintenance
- Works with any Typer app

### 2. **Power**
- Full litellm configuration exposed
- Complex validation chains
- Retry strategies
- Response formatting

### 3. **Integration**
- Slash commands work with all features
- MCP server ready
- Config files for CI/CD

## Usage Patterns

### Development
```bash
# Quick testing
llm ask "Debug this: ${CODE}"

# Code generation with validation
llm ask "Write tests for ${FILE}" --validate code --model gpt-4
```

### Production
```yaml
# config/api-generator.yaml
model: gpt-4
temperature: 0.2
validation:
  - strategy: code
    language: python
  - strategy: imports
    required: ["fastapi", "pydantic"]
retry_config:
  max_attempts: 3
  backoff_factor: 2.0
```

```bash
# Use in CI/CD
llm call config/api-generator.yaml --prompt "Generate user endpoint"
```

### Claude Code Integration
```json
// .claude/commands/llm-ask.json
{
  "name": "llm-ask",
  "description": "Ask LLM with full configuration options",
  "args": [
    {"name": "prompt", "type": "string"},
    {"name": "model", "type": "string", "optional": true},
    {"name": "validate", "type": "array", "optional": true},
    {"name": "temperature", "type": "number", "optional": true}
  ],
  "execute": "uv run python -m llm_call.cli.main_unified ask \"${prompt}\" ${model} ${validate} ${temperature}"
}
```

## Future Enhancements

1. **Streaming Support**: Add `--stream` flag for real-time responses
2. **Tool Use**: Expose function calling capabilities
3. **Batch Processing**: Process multiple prompts from file
4. **Output Formats**: Support markdown, code blocks, etc.
5. **Profiles**: Named configuration profiles for common tasks

## Conclusion

The unified CLI successfully integrates:
- Simple commands for ease of use
- Full litellm configuration support
- Automatic slash command generation
- Flexible configuration options

This provides the "best way to include litellm config dict with the CLI and automate slash command and MCP integration" as requested.