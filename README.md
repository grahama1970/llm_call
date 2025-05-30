# LLM Call - Universal LLM Interface with Smart Validation

A flexible command-line tool and library that lets you interact with any LLM through a unified interface. Whether you prefer typing commands, using it within Claude Desktop/Code as an MCP tool, or integrating it into your Python scripts - llm_call handles it all with built-in response validation.

## 🎯 Why LLM Call?

**The Problem**: Different LLMs have different APIs, different strengths, and different failure modes. You want to use the best model for each task without rewriting code or manually validating responses.

**The Solution**: LLM Call provides a single interface that:
- Works with any LLM provider (OpenAI, Anthropic, Ollama, etc.)
- Validates responses to ensure quality and format compliance  
- Retries intelligently when responses don't meet your requirements
- Integrates seamlessly into your workflow (CLI, MCP, or Python)

## 🚀 Quick Start

### Installation
```bash
pip install llm-call
# or
uv add llm-call
```

### Create a Convenient Alias (Optional)
Since `python -m llm_call.cli.main` is verbose, you can create an alias:
```bash
# Add to your ~/.bashrc or ~/.zshrc
alias llm='python -m llm_call.cli.main'

# Then you can use:
llm ask "What is Python?"
```

### Three Ways to Use LLM Call

#### 1. Command Line Interface
```bash
# Quick question
python -m llm_call.cli.main ask "What are the main differences between Python and JavaScript?"

# Interactive chat
python -m llm_call.cli.main chat --model gpt-4

# Using configuration files
python -m llm_call.cli.main call config.json --prompt "Analyze this data"
```

#### 2. MCP Tool in Claude Desktop/Code
```bash
# Generate MCP configuration
python -m llm_call.cli.main generate-mcp-config

# Add to Claude's MCP settings
# Now you can use any model directly from Claude!
```

#### 3. Python Library
```python
from llm_call import ask

response = await ask(
    "Generate a Python function to calculate fibonacci numbers",
    model="gpt-4",
    validate=["code", "python"]
)
```

## 📚 Use Case Scenarios

### Scenario 1: Code Generation with Validation
**Goal**: Generate Python code that actually works

**CLI Command**:
```bash
python -m llm_call.cli.main ask "Write a Python function to merge two sorted lists" \
  --model gpt-4 \
  --validate code \
  --validate python
```

**In Claude Desktop** (via MCP):
```
Please write a Python function to merge two sorted lists. 
Make sure it handles edge cases and includes type hints.
```
*Behind the scenes: Claude uses llm_call to validate the response is proper Python code*

### Scenario 2: Structured Data Extraction
**Goal**: Extract structured information from text and ensure it's valid JSON

**CLI Command**:
```bash
python -m llm_call.cli.main ask "Extract the key points from this article as JSON" \
  --model claude-3-opus \
  --json \
  --validate json \
  --system "You are a precise data extractor"
```

**Configuration File** (`extract_config.json`):
```json
{
  "model": "claude-3-opus",
  "system": "You are a precise data extractor",
  "response_format": {"type": "json_object"},
  "validation": [
    {"type": "json"},
    {"type": "schema", "schema": {
      "type": "object",
      "properties": {
        "key_points": {"type": "array"},
        "summary": {"type": "string"}
      }
    }}
  ]
}
```

### Scenario 3: Multi-Model Comparison
**Goal**: Get responses from different models for comparison

**Shell Script**:
```bash
#!/bin/bash
PROMPT="Explain quantum computing to a 10-year-old"

echo "=== GPT-4 ==="
python -m llm_call.cli.main ask "$PROMPT" --model gpt-4

echo -e "\n=== Claude ==="
python -m llm_call.cli.main ask "$PROMPT" --model claude-3-opus

echo -e "\n=== Local Llama ==="
python -m llm_call.cli.main ask "$PROMPT" --model ollama/llama3.2
```

### Scenario 4: Validated API Documentation
**Goal**: Generate OpenAPI documentation that's guaranteed to be valid

**Python Integration**:
```python
from llm_call import call_llm

config = {
    "model": "gpt-4",
    "messages": [{
        "role": "system", 
        "content": "You are an API documentation expert. Generate valid OpenAPI 3.0 specs."
    }, {
        "role": "user",
        "content": "Create OpenAPI spec for a user authentication API"
    }],
    "response_format": {"type": "json_object"},
    "validation": [
        {"type": "json"},
        {"type": "openapi_spec"}
    ],
    "retry_config": {
        "max_attempts": 3,
        "validation_feedback": True
    }
}

result = await call_llm(config)
```

### Scenario 5: Research Assistant with Web Access
**Goal**: Research a topic using multiple sources

**Interactive Chat Session**:
```bash
python -m llm_call.cli.main chat --model gpt-4 --system "You are a research assistant with web access"

You: What are the latest developments in quantum computing in 2024?
Assistant: I'll research the latest developments in quantum computing for 2024...
You: Focus on practical applications
Assistant: Let me narrow down to practical applications...
```

### Scenario 6: Advanced Code Analysis with Conversational Validation
**Goal**: Analyze complex codebases with a specialized model that validates its own reasoning

**Interactive Session**:
```bash
python -m llm_call.cli.main chat --model anthropic/max

You: I need help understanding this legacy codebase. It has a complex 
     authentication system spread across multiple files.

Assistant: I'll analyze your codebase systematically. Let me start by examining 
          the authentication flow. Can you show me the main entry point?

You: The auth starts in src/auth/manager.py but it calls into 
     src/security/validators.py and src/database/user_store.py

Assistant: I'll trace through this authentication flow for you. Let me analyze 
          each component:
          
          1. First, examining the manager.py to understand the orchestration...
          2. Now checking how validators.py handles credential validation...
          3. Looking at user_store.py for the persistence layer...
          
          [Detailed analysis with code snippets and explanations]
          
          I notice a potential security issue in the password hashing - 
          would you like me to explain and suggest a fix?

You: Yes, and make sure the fix is compatible with the existing database

Assistant: Let me design a backwards-compatible security improvement. I'll:
          1. Create a migration strategy for existing password hashes
          2. Implement stronger hashing while maintaining compatibility
          3. Validate that the solution won't break existing user logins
          
          [Provides validated, tested code with migration plan]
```

**What Makes This Special**: 
- The model (`anthropic/max`) has access to sophisticated code analysis capabilities
- It validates its own suggestions through conversational reasoning
- Complex multi-file understanding with context retention
- Proactive security analysis and backwards-compatible solutions

## 🛠️ Key Features

### Model Flexibility
- **Any Provider**: OpenAI, Anthropic, Google, Ollama, Groq, etc.
- **Smart Routing**: Automatically routes to the right provider
- **Local Models**: Full support for Ollama and local LLMs
- **Custom Endpoints**: Configure your own API endpoints

### Validation Power
- **Built-in Validators**: JSON, code, length, regex, custom
- **Retry Logic**: Automatic retry with validation feedback
- **Schema Validation**: Ensure responses match your data structure
- **Language-Specific**: Validate Python, JavaScript, SQL, etc.

### Integration Options
- **CLI**: Full-featured command-line interface
- **MCP**: Use any model seamlessly within Claude
- **Python API**: Async/sync support for applications
- **Config Files**: JSON/YAML configuration for complex setups

## 🎯 Advanced Usage

### Custom Validation
```python
from llm_call import register_validator

@register_validator("sql_safe")
def validate_sql_safety(response: str, context: dict) -> bool:
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE"]
    return not any(keyword in response.upper() for keyword in dangerous_keywords)

# Use it
response = await ask(
    "Generate a SQL query to find top customers",
    model="gpt-4",
    validate=["sql", "sql_safe"]
)
```

### Model Routing Patterns
```bash
# Local models for sensitive data
python -m llm_call.cli.main ask "Summarize this confidential document" --model ollama/llama3.2

# Powerful models for complex tasks  
python -m llm_call.cli.main ask "Solve this differential equation" --model gpt-4

# Fast models for simple tasks
python -m llm_call.cli.main ask "Format this date" --model gpt-3.5-turbo

# Specialized models (wink wink 😉)
python -m llm_call.cli.main ask "Debug this complex codebase" --model anthropic/max
```

### Conversation Context in Claude
When using llm_call as an MCP tool in Claude, you get the best of both worlds:
- Claude's excellent conversational interface
- Access to any LLM model for specialized tasks
- Automatic validation of all responses
- Seamless integration that feels native

**Example Claude Conversation**:
```
You: Can you help me create a data pipeline that processes CSV files?

Claude: I'll help you create a data pipeline for CSV processing. Let me design
this using the best model for code generation.

[Behind the scenes: Uses llm_call with gpt-4 + code validation]

Here's a complete data pipeline implementation:
[Validated, working code appears here]

You: Can you make it handle large files more efficiently?

Claude: I'll optimize it for large file processing using streaming:
[Updated, validated code with streaming support]
```

## 📋 Command Reference

### Core Commands
- `ask` - Single question/prompt
- `chat` - Interactive conversation  
- `call` - Use configuration file
- `models` - List available models
- `validators` - Show validation strategies
- `config-example` - Generate example config

### Generation Commands
- `generate-claude` - Create Claude slash commands
- `generate-mcp-config` - Generate MCP configuration
- `serve-mcp` - Run as MCP server

### Testing Commands
- `test` - Run validation tests
- `test-poc` - Test proof of concepts

## 🔧 Configuration

### Environment Variables
```bash
# Optional API keys for different providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# Default model selection
LLM_DEFAULT_MODEL=gpt-4
LLM_FALLBACK_MODEL=gpt-3.5-turbo
```

### Example Configuration File
```yaml
model: gpt-4
temperature: 0.7
max_tokens: 2000
messages:
  - role: system
    content: You are a helpful coding assistant
  - role: user  
    content: "{{ prompt }}"  # Filled from CLI
validation:
  - type: code
    language: python
  - type: length
    min: 100
retry_config:
  max_attempts: 3
  backoff_factor: 2.0
```

## 🚀 Getting Started

1. **Install**: `pip install llm-call`
2. **Set API Keys**: Add your LLM provider API keys
3. **Test It**: `python -m llm_call.cli.main ask "Hello, which model are you?"`
4. **Explore**: Try different models and validation strategies

## 🤝 Contributing

We welcome contributions! Key areas:
- Additional validation strategies
- New LLM provider integrations  
- MCP feature enhancements
- Documentation improvements

## 📄 License

GPL-3.0-or-later

---

*LLM Call - Because every LLM has its strengths, and you should be able to use them all.*