# LLM Caller

A sophisticated LLM routing and validation system that acts as a proxy layer for Claude and other LLM providers. This experimental project enables seamless switching between different LLM providers while providing robust validation, retry mechanisms, and specialized Claude CLI integration.

## 🎯 Purpose

The Claude Max Proxy creates a **smart LLM proxy** that can:
- Route requests intelligently between different LLM providers
- Validate LLM responses rigorously with configurable strategies
- Provide a consistent OpenAI-compatible API interface across providers
- Integrate Claude CLI tool into standard LLM workflows

## 🏗️ Architecture

### Core Components

#### **Model Router** (`src/llm_call/core/router.py`)
Maps model names to appropriate providers and API endpoints:
```python
# Routes "anthropic/max" to local Claude proxy
if model in ["anthropic/max", "claude/max", "claude-code/max"]:
    llm_config["api_base"] = "http://localhost:3010/v1"
    llm_config["model"] = "claude-3-5-haiku-20241022"
```

#### **Validation Framework** (`src/llm_call/core/`)
- **`base.py`**: Validation protocols and result structures
- **`strategies.py`**: Registry system for pluggable validation strategies
- **`retry.py`**: Retry mechanism with exponential backoff and validation feedback

#### **API Server** (`src/llm_call/core/api.py`)
FastAPI server providing OpenAI-compatible `/v1/chat/completions` endpoint

### Provider Support

#### **Claude Provider** (`src/llm_call/core/providers/claude/`)
- **Claude CLI Executor**: Sophisticated subprocess execution with streaming JSON parsing
- **Database Manager**: Handles Claude CLI data persistence
- **Focused Extractor**: Specialized response processing
- **Logging Utils**: Comprehensive logging and debugging

#### **Other Providers**
- **Ollama**: Local Ollama instance integration
- **RunPod**: Framework ready for cloud GPU providers

## 🚀 Features

### **Unified LLM Access**
- Single API interface for multiple LLM providers
- Automatic provider routing based on model names
- OpenAI-compatible endpoints for easy integration

### **Claude CLI Integration**
- Executes Claude CLI as subprocess with real-time parsing
- Handles different message types (system, assistant, result)
- Context-aware execution in specific directories
- Comprehensive error handling and logging

### **Response Quality Assurance**
- Protocol-based validation strategies
- Automatic retry with feedback on validation failure
- Debug tracing and detailed reporting
- Both sync and async validation support

### **Development Workflow**
- Docker containerization for easy deployment
- Volume mounts for live code updates
- Redis integration for LiteLLM caching
- Comprehensive logging and debugging

## 🛠️ Setup

### Prerequisites
- Python 3.10+
- Docker and Docker Compose
- Claude CLI installed and configured
- Virtual environment activated

### Environment Setup

1. **Clone and setup**:
   ```bash
   cd /home/graham/workspace/experiments/claude_max_proxy
   source .venv/bin/activate
   export PYTHONPATH=/home/graham/workspace/experiments/claude_max_proxy/src
   ```

2. **Environment Variables** (`.env`):
   ```bash
   PYTHONPATH=/home/graham/workspace/experiments/claude_max_proxy/src
   REDIS_HOST=localhost
   ARANGO_HOST=localhost
   EMBEDDING_DIMENSION=1024
   EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
   
   # API Keys
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   DEEPSEEK_API=your_deepseek_key
   PERPLEXITY_API_KEY=your_perplexity_key
   
   # LLM Validation Configuration
   LITELLM_DEFAULT_MODEL=vertex_ai/gemini-2.5-flash-preview-04-17
   LITELLM_JUDGE_MODEL=vertex_ai/gemini-2.5-flash-preview-04-17
   ENABLE_LLM_VALIDATION=false
   ```

### Docker Deployment

```bash
# Start services
docker-compose up -d

# Claude Proxy runs on port 3010
# Redis runs on port 6379
```

## 📖 Usage

### Basic API Usage

```python
import openai

# Configure client to use Claude Max Proxy
client = openai.OpenAI(
    api_key="your-key",
    base_url="http://localhost:3010/v1"
)

# Route to Claude CLI
response = client.chat.completions.create(
    model="anthropic/max",
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)

# Route to Ollama
response = client.chat.completions.create(
    model="ollama/llama3.2",
    messages=[{"role": "user", "content": "Hello, Ollama!"}]
)
```

### Validation Strategies

```python
from llm_call.core.strategies import ValidationStrategy
from llm_call.core.base import ValidationResult

class CustomValidator(ValidationStrategy):
    def validate(self, response: str, context: dict) -> ValidationResult:
        # Custom validation logic
        is_valid = len(response) > 10
        return ValidationResult(
            is_valid=is_valid,
            feedback="Response too short" if not is_valid else None
        )
```

### Model Routing Configuration

The system automatically routes models based on naming patterns:
- `anthropic/max`, `claude/max`, `claude-code/max` → Local Claude CLI
- `ollama/*` → Local Ollama instance
- Other models → LiteLLM with standard providers

## 🧪 Proof of Concept

The `src/llm_call/proof_of_concept/` directory demonstrates:
- Core LiteLLM integration with routing logic
- Structured response handling with Pydantic models
- Multi-provider fallback strategies

## 🏛️ Project Structure

```
claude_max_proxy/
├── src/llm_call/
│   ├── core/
│   │   ├── api.py              # FastAPI server
│   │   ├── router.py           # Model routing logic
│   │   ├── strategies.py       # Validation strategies
│   │   ├── retry.py           # Retry mechanisms
│   │   └── providers/
│   │       ├── claude/         # Claude CLI integration
│   │       ├── ollama.py      # Ollama provider
│   │       └── runpod.py      # RunPod framework
│   ├── proof_of_concept/      # Demonstration code
│   └── config.py              # Configuration management
├── docker-compose.yml         # Container orchestration
├── Dockerfile                 # Container definition
└── pyproject.toml            # Python project configuration
```

## 🤝 Contributing

This is an experimental project exploring advanced LLM proxy patterns. Key areas for development:

1. **Provider Expansion**: Add support for more LLM providers
2. **Validation Strategies**: Develop domain-specific validation logic
3. **Performance Optimization**: Improve routing and caching strategies
4. **Monitoring**: Add comprehensive metrics and observability

## 📄 License

GPL-3.0-or-later

## 👨‍💻 Author

Graham Anderson - graham@grahama.co

---

*This project demonstrates cutting-edge approaches to LLM integration, validation, and routing for production-ready AI applications.*