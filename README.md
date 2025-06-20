# LLM Call - Universal LLM Interface with Multi-Model Collaboration

A flexible command-line tool and library that enables **fluid conversational collaboration between different LLM models**. Claude can delegate to Gemini for large documents, GPT-4 for specific tasks, or any other model - all while maintaining conversation context.

**This is a SPOKE module** - it makes LLM calls and is orchestrated by the HUB ([claude-module-communicator](https://github.com/grahamwetzler/claude-module-communicator)).

## 🐳 Quick Start with Docker

The easiest way to run llm_call is using Docker:

```bash
# Clone the repository
git clone https://github.com/grahama1970/llm_call.git
cd llm_call

# Copy environment template
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# For Claude Max users: Authenticate Claude CLI
./docker/claude-proxy/authenticate.sh
# Test authentication
./docker/claude-proxy/test_claude.sh

# Optional: Install convenient aliases
./scripts/install_claude_aliases.sh
# Then use: claude-auth, claude-test, claude-status
# See docker/claude-proxy/AUTHENTICATION.md for details
```

### Accessing Services

- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Claude Proxy**: http://localhost:3010 (for max/opus models)

### Testing the API

```bash
# Health check
curl http://localhost:8001/health

# Test request with OpenAI
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Using Claude Max

If you have a Claude Max subscription, you can use max/opus models in two ways:

#### Option 1: Docker Proxy Mode (Default)

1. **First-time setup** - Authenticate Claude CLI:
```bash
# Option 1: Use the helper script (recommended)
./docker/claude-proxy/authenticate.sh

# Option 2: Manual authentication
docker exec -it llm-call-claude-proxy /bin/bash
claude  # Launch Claude Code and authenticate
```

2. Use the max/opus models:
```python
from llm_call import make_llm_request
```

#### Option 2: Local Mode (Direct CLI)

For lower latency, you can run Claude CLI directly without the proxy:

```bash
# Set environment variables
export CLAUDE_PROXY_EXECUTION_MODE=local
export CLAUDE_PROXY_LOCAL_CLI_PATH=/path/to/claude  # e.g., ~/.nvm/versions/node/v22.15.0/bin/claude
unset ANTHROPIC_API_KEY  # Required for OAuth

# Use the same API
from llm_call import make_llm_request

response = await make_llm_request({
    "model": "max/opus",  # or "max/claude-3-opus-20240229"
    "messages": [{"role": "user", "content": "Hello!"}]
})
```

### Docker Profiles

```bash
# Run with GPU support (for local Ollama)
docker compose --profile gpu up -d

# Run with development tools
docker compose --profile dev up -d
```

## 🎯 Core Capabilities

### 1. Multi-Model Collaboration with Conversation State
- **Persistent Conversations**: SQLite-based conversation tracking across model calls
- **Context Preservation**: Models can build on each other's responses
- **Fluid Delegation**: Claude can delegate to Gemini (1M context), GPT-4, or any model
- **Iterative Refinement**: Models can refine and improve each other's outputs

### 2. Intelligent Routing
- **Automatic Model Selection**: Routes to appropriate provider based on task
- **Context-Aware Delegation**: Automatically delegates when context limits are exceeded
- **Provider Support**: OpenAI, Anthropic, Google Vertex AI, Ollama, Runpod, and more

### 3. Response Validation
- **16 Built-in Validators**: JSON, code, schema, length, regex, and more
- **Retry with Feedback**: Automatically retries with validation feedback
- **Custom Validators**: Easy to add domain-specific validation

## 🚀 Quick Start for LLM Agents

### For Module Communicator Integration

```python
# Import the conversational delegator
from llm_call.tools.conversational_delegator import conversational_delegate

# Start a new collaboration
result = await conversational_delegate(
    model="vertex_ai/gemini-1.5-pro",
    prompt="Analyze this 500k character document...",
    conversation_name="large-doc-analysis",
    temperature=0.0
)
conversation_id = result["conversation_id"]

# Continue the conversation with a different model
result = await conversational_delegate(
    model="gpt-4",
    prompt="What patterns did you identify?",
    conversation_id=conversation_id
)
```

### Environment Setup

#### Local Development

```bash
# Required: Set PYTHONPATH and load environment
export PYTHONPATH=./src
source .venv/bin/activate

# The system loads API keys from .env file
# Required keys:
# - OPENAI_API_KEY (for GPT models)
# - GOOGLE_APPLICATION_CREDENTIALS (for Vertex AI/Gemini)
# - ANTHROPIC_API_KEY (for Claude API calls - currently empty)
```

#### Docker Environment

Create a `.env` file with your API keys:

```bash
# LLM Provider Keys
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here  # For Gemini
ANTHROPIC_API_KEY=your_key_here  # For Claude API (optional)

# Service Configuration
REDIS_URL=redis://redis:6379
CLAUDE_PROXY_URL=http://claude-proxy:3010
ENABLE_RL_ROUTING=true
ENABLE_LLM_VALIDATION=false

# Optional Tool Keys
PERPLEXITY_API_KEY=your_key_here
BRAVE_API_KEY=your_key_here
GITHUB_TOKEN=your_token_here
```

For Vertex AI in Docker, mount your service account:
```yaml
volumes:
  - ./vertex_ai_service_account.json:/app/vertex_ai_service_account.json:ro
environment:
  - GOOGLE_APPLICATION_CREDENTIALS=/app/vertex_ai_service_account.json
```

## 📚 Key Features for Orchestration

### 1. Conversation Management

```python
from llm_call.core.conversation_manager import ConversationManager

# Initialize manager (uses SQLite by default)
manager = ConversationManager()

# Create a conversation
conv_id = await manager.create_conversation(
    "Research Task",
    metadata={"models": ["claude", "gemini", "gpt-4"]}
)

# Add messages
await manager.add_message(conv_id, "user", "Research quantum computing")
await manager.add_message(conv_id, "assistant", "I'll search for recent papers...", model="claude")

# Retrieve conversation for next model
messages = await manager.get_conversation_for_llm(conv_id)
```

### 2. Model Routing Examples

```python
from llm_call.core.caller import make_llm_request

# Route to specific models
config = {
    "model": "vertex_ai/gemini-1.5-pro",  # For 1M context
    "messages": messages,
    "temperature": 0.0
}
response = await make_llm_request(config)

# Available routes:
# - "max/opus" -> Claude CLI (supports multimodal)
# - "vertex_ai/gemini-1.5-pro" -> Gemini with 1M context
# - "gpt-4", "gpt-3.5-turbo" -> OpenAI
# - "ollama/llama3.2" -> Local models
# - "runpod/pod-id/llama-3-70b" -> Runpod hosted models (30-70B)

# Multimodal example (images)
multimodal_config = {
    "model": "max/opus",  # or gpt-4-vision-preview, gemini-pro-vision
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "/path/to/image.png"}}
        ]
    }]
}
response = await make_llm_request(multimodal_config)
```

### 3. Validation Integration

```python
from llm_call.core.strategies import get_validator

# Use validators to ensure quality
validators = [
    get_validator("json"),           # Ensure valid JSON
    get_validator("length", min_length=100),  # Minimum length
    get_validator("field_present", required_fields=["summary", "key_points"])
]

# Apply validation in requests
config["validation_strategies"] = validators
```

## 🔧 Command Line Tools

### Conversational Delegator

```bash
# Start a new conversation
python src/llm_call/tools/conversational_delegator.py \
  --model "vertex_ai/gemini-1.5-pro" \
  --prompt "Analyze this large document" \
  --conversation-name "doc-analysis"

# Continue existing conversation
python src/llm_call/tools/conversational_delegator.py \
  --model "gpt-4" \
  --prompt "Summarize the key findings" \
  --conversation-id "uuid-from-previous"

# View conversation history
python src/llm_call/tools/conversational_delegator.py \
  --show-history \
  --conversation-id "uuid"
```

### Basic LLM Calls

```bash
# Quick question
python -m llm_call.cli.main ask "What is Python?"

# Interactive chat
python -m llm_call.cli.main chat --model gpt-4

# With validation
python -m llm_call.cli.main ask "Generate a SQL query" --validate sql --validate sql_safe
```

## 🔌 Integration Points

### For Claude Module Communicator (HUB)

This module exposes:
1. **Conversational Delegation**: Multi-model conversations with state
2. **Model Routing**: Access to all configured LLM providers
3. **Validation Services**: Ensure response quality
4. **MCP Tools**: For Claude Desktop integration

### API Endpoints

```python
# Main entry points for orchestration
from llm_call.core.caller import make_llm_request
from llm_call.tools.conversational_delegator import conversational_delegate
from llm_call.core.conversation_manager import ConversationManager
from llm_call.core.strategies import get_validator
```

### Database Integration

- **SQLite**: `logs/conversations.db` for conversation state
- **ArangoDB**: Optional integration at `/home/graham/workspace/experiments/arangodb`

## 📊 Current Configuration Status

### Working Models (with API keys in .env):
- ✅ **Vertex AI/Gemini 1.5 Pro**: 1M context window
- ✅ **OpenAI GPT-4/GPT-3.5**: General purpose
- ✅ **Claude CLI**: Via `max/` prefix
- ✅ **Runpod**: Host 30-70B models via `runpod/` prefix
- ✅ **Perplexity**: For web search (via MCP)
- ❌ **Anthropic API**: Key missing in .env (line 15)

### Validation Strategies Available:
- Basic: `response_not_empty`, `json_string`, `not_empty`
- Advanced: `length`, `regex`, `contains`, `code`, `field_present`
- Specialized: `python`, `json`, `sql`, `openapi_spec`, `sql_safe`
- AI-based: `ai_contradiction_check`, `agent_task` (require LLM)

## 🎯 Typical Workflows

### Large Document Analysis (Claude → Gemini)
```python
# 1. Claude receives 500k char document (exceeds 200k limit)
# 2. Delegate to Gemini
result = await conversational_delegate(
    model="vertex_ai/gemini-1.5-pro",
    prompt=f"Analyze this document: {large_document}",
    conversation_name="large-doc-analysis"
)

# 3. Claude continues with summary
result = await conversational_delegate(
    model="max/opus",
    prompt="Based on the analysis, what are the key actionable insights?",
    conversation_id=result["conversation_id"]
)
```

### Multi-Model Research (Claude → Perplexity → GPT-4)
```python
# 1. Start research task
conv_id = await manager.create_conversation("Research: Quantum Computing 2024")

# 2. Web search via Perplexity
# 3. Paper analysis via Gemini
# 4. Synthesis via GPT-4
# All maintaining conversation context
```

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/llm_call.git
cd llm_call

# Setup environment
python -m venv .venv
source .venv/bin/activate
uv add -e .

# Configure API keys in .env
cp .env.example .env
# Edit .env with your API keys
```

## 💻 Claude Desktop Slash Commands

For Claude Desktop users, llm_call includes powerful slash commands with flexible configuration:

```bash
# Installation
cp ~/.claude/commands/llm_call ~/.claude/commands/
cp ~/.claude/commands/llm_call_multimodal ~/.claude/commands/
cp ~/.claude/commands/llm ~/.claude/commands/  # Short alias

# Basic usage
/llm_call "What is Python?" --model gpt-4
/llm "Describe image" --image photo.jpg --model max/opus

# Advanced features
/llm --query "Find issues" --corpus /path/to/code --model vertex_ai/gemini-2.0-flash-exp
/llm --config analysis.json --model gpt-4
```

### Slash Command Features

- **Multimodal support**: Analyze images with `--image`
- **Corpus analysis**: Analyze entire directories with `--corpus`
- **Config files**: Use JSON/YAML configs with `--config`
- **Flexible models**: Any model llm_call supports
- **Parameter control**: Temperature, max tokens, validation

### Configuration Locations

The slash commands look for .env files in this order:
1. Path in `LLM_CALL_ENV_FILE` environment variable
2. `/home/graham/workspace/experiments/llm_call/.env`
3. `~/.llm_call/.env`
4. Same directory as the slash command

See [docs/SLASH_COMMAND_SETUP.md](docs/SLASH_COMMAND_SETUP.md) for detailed setup options.

## 📋 File Structure

```
llm_call/
├── src/llm_call/
│   ├── core/
│   │   ├── caller.py              # Main LLM request handler
│   │   ├── conversation_manager.py # Conversation state persistence
│   │   ├── router.py              # Model routing logic
│   │   └── validation/            # Validation strategies
│   ├── tools/
│   │   ├── llm_call_delegator.py  # Basic delegation tool
│   │   └── conversational_delegator.py # Stateful conversations
│   └── cli/
│       └── main.py                # CLI interface
├── logs/
│   └── conversations.db           # SQLite conversation storage
└── .env                          # API keys and configuration
```

## 🔒 Security Notes

- API keys are loaded from `.env` via `load_dotenv()`
- Never commit `.env` file
- Use environment-specific configurations
- Validate all LLM responses before use

## 🤝 Integration with Claude Module Communicator

As a SPOKE module, this integrates with the HUB by:
1. Accepting orchestration commands via the conversational delegator
2. Maintaining conversation state across multiple model calls
3. Providing validation feedback to the orchestrator
4. Exposing all LLM capabilities through a unified interface

The HUB can use this module to:
- Delegate tasks to appropriate models based on requirements
- Maintain complex multi-model conversations
- Ensure response quality through validation
- Handle model-specific limitations (context windows, capabilities)

---

*LLM Call - Enabling fluid collaboration between AI models*