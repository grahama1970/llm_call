# LLM Call MCP Server

This project can now be run as an MCP (Model Context Protocol) server, exposing its LLM routing and validation capabilities through a standardized API.

## Quick Start

### 1. Run the MCP Server

```bash
# From the llm_call directory
python run_mcp_server.py

# Or using module
python -m llm_call.mcp_server
```

The server will start on `http://localhost:8001`

### 2. Environment Variables

Set these environment variables for full functionality:

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"  # For GPT models
export GITHUB_PERSONAL_ACCESS_TOKEN="your-token"  # For GitHub MCP tool
export BRAVE_API_KEY="your-key"  # For Brave search
export PERPLEXITY_API_KEY="your-key"  # For Perplexity search
```

## MCP Endpoints

### Execute Command
```
POST /mcp/execute
```

Execute various commands through the MCP interface.

#### Chat Command
```json
{
  "command": "chat",
  "params": {
    "prompt": "What is quantum computing?",
    "model": "max/claude-3-opus-20240229",
    "mcp_servers": ["perplexity", "brave_search"],
    "stream": false
  }
}
```

#### Validate Command
```json
{
  "command": "validate",
  "params": {
    "content": "{\"name\": \"test\", \"value\": 123",
    "validator_type": "json"
  }
}
```

#### Analyze Code Command
```json
{
  "command": "analyze_code",
  "params": {
    "code": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)",
    "language": "python",
    "analysis_type": "optimize"
  }
}
```

### Server Information
```
GET /mcp/info
```

Returns server capabilities, available models, and supported commands.

### Health Check
```
GET /mcp/health
```

Returns health status of the MCP server and its components.

## Available MCP Tools

When using the `chat` command, you can enable these MCP tools:

- **perplexity**: Web search and information retrieval
- **github**: GitHub repository access and analysis
- **brave_search**: Brave search engine integration
- **filesystem**: Local filesystem access
- **memory**: Persistent memory/knowledge base
- **postgres**: PostgreSQL database access (if DATABASE_URL is set)

## Integration with Chat Interface

### Update Backend Configuration

In your chat backend's `mcp_client.py`:

```python
self.available_servers = {
    "llm_call": {
        "url": "http://localhost:8001",
        "description": "Claude Code with enhanced capabilities and MCP tools"
    },
    # ... other servers
}
```

### Docker Compose

Add to your `docker-compose.yml`:

```yaml
services:
  llm-call:
    build: ../llm_call
    ports:
      - "8001:8001"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GITHUB_PERSONAL_ACCESS_TOKEN=${GITHUB_TOKEN}
      - BRAVE_API_KEY=${BRAVE_API_KEY}
    volumes:
      - ../llm_call:/app
    command: python run_mcp_server.py
```

## Features

### 1. **Multi-Model Support**
- Routes to Claude CLI for "max/" prefixed models
- Falls back to LiteLLM for other models (GPT-4, standard Claude, etc.)

### 2. **Validation Framework**
- JSON validation and auto-fixing
- Code validation for multiple languages
- Schema-based validation

### 3. **Smart Retry Logic**
- Automatic retries with exponential backoff
- Validation-based retry improvements

### 4. **MCP Tool Integration**
- Dynamic tool loading based on query
- Seamless integration with Claude CLI

### 5. **Streaming Support**
- Real-time streaming responses
- Progress indicators

## Example Usage from Chat Frontend

```javascript
// In your React chat component
const response = await fetch('http://localhost:8000/api/mcp/llm_call/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: "Search for the latest AI developments",
    mcp_servers: ['perplexity'],
    stream: false
  })
});

const data = await response.json();
console.log(data.content);
```

## Development

### Running Tests

```bash
pytest tests/test_mcp_server.py
```

### Adding New MCP Tools

Edit `mcp_handler_enhanced.py` to add new tools:

```python
servers.append({
    "name": "your_tool",
    "description": "Your tool description",
    "enabled": True,
    "command": "npx",
    "args": ["-y", "@your/mcp-server"],
    "requires_env": ["YOUR_API_KEY"]
})
```

## Troubleshooting

### MCP Tools Not Working
- Check environment variables are set
- Ensure npm/npx is available in the container
- Check logs for specific error messages

### Claude CLI Not Found
- Ensure Claude CLI is installed and in PATH
- Check Docker volume mounts if using containers

### Connection Refused
- Verify the server is running on port 8001
- Check firewall/network settings
- Ensure Docker port mapping is correct