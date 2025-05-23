# Claude Code MCP Integration

This document explains how this project integrates directly with Claude Code's built-in MCP (Model Context Protocol) capabilities without requiring a separate MCP server.

## Overview

Claude Code already has built-in MCP capabilities that we can leverage directly. Instead of implementing our own MCP server or using a third-party MCP server, we can communicate directly with Claude Code through its native capabilities.

Key benefits of this approach:

1. **Simplicity**: No need to manage a separate MCP server
2. **Reliability**: Direct integration with Claude Code's supported features
3. **Compatibility**: Works with any Claude Code installation without additional dependencies
4. **Future-proof**: Automatically benefits from Claude Code updates and improvements

## Implementation Details

The direct Claude Code MCP integration is implemented in the `/src/claude_comms/background/mcp_client_updated.py` file, which contains:

1. `ClaudeMCPClient`: A client that communicates directly with Claude Code's native capabilities
2. `MCPInstancePool`: A pool manager for multiple Claude instances

### How It Works

Unlike previous approaches that required a separate Node.js MCP server, this implementation:

1. Uses the Claude Code CLI directly with appropriate flags
2. Manages Claude instances directly through the CLI
3. Handles conversation states and metadata
4. Supports both synchronous and asynchronous usage patterns

#### Key Features

- **Direct Claude Execution**: Uses the Claude executable directly rather than going through a separate server
- **Conversation Persistence**: Maintains conversation IDs for continued interactions
- **Instance Pooling**: Manages multiple Claude instances efficiently
- **Background Processing**: Enables non-blocking operation for long-running queries
- **Error Handling**: Robust handling of errors and timeouts

## Usage Examples

### Basic Query

```python
from claude_comms.background.mcp_client_updated import ClaudeMCPClient

# Create a client
client = ClaudeMCPClient()

# Query Claude
response = client.query_claude(
    prompt="What is the capital of France?",
    system_prompt="You are a helpful assistant.",
    model="claude-3-opus-20240229"
)

print(response)
```

### Using Instance Pool

```python
from claude_comms.background.mcp_client_updated import MCPInstancePool

# Create a pool of Claude instances
pool = MCPInstancePool(pool_size=3)

# Send multiple queries using the pool
responses = []
for prompt in ["Query 1", "Query 2", "Query 3"]:
    response = pool.query(
        prompt=prompt,
        system_prompt="You are a helpful assistant."
    )
    responses.append(response)
```

### Continuing a Conversation

```python
# Send initial query
result = pool.query(
    prompt="Tell me about Python programming.",
    system_prompt="You are a programming expert."
)

conversation_id = result["conversation_id"]

# Continue the conversation
follow_up = pool.query(
    prompt="What about Python's async features?",
    conversation_id=conversation_id
)
```

## Integration with SQLite for Inter-Instance Communication

While the direct MCP integration handles communication with Claude Code, we still use the SQLite database for:

1. **Progress Tracking**: Monitoring task progress across multiple instances
2. **Inter-Instance Messaging**: Allowing different Claude instances to exchange messages
3. **Centralized Task Management**: Coordinating work between instances
4. **Persistent Storage**: Storing conversation history and results

This combination provides the best of both worlds:
- Direct access to Claude Code's capabilities without middleware
- Shared state and communication between instances through SQLite

## Implementation Notes

1. The implementation uses the `--dangerously-skip-permissions` flag to enable background/automated operation
2. Each Claude instance is managed independently and maintains its own conversation state
3. The instance pool uses a simple least-recently-used (LRU) strategy by default
4. Temporary files are used for passing prompts and system prompts to Claude

## Testing

The integration includes comprehensive tests in `/tests/test_claude_mcp_direct.py` to verify:

1. Client initialization and health checks
2. Query functionality with various parameters
3. Instance pool management and routing
4. Conversation continuity

To run the tests:

```bash
python -m unittest tests/test_claude_mcp_direct.py
```