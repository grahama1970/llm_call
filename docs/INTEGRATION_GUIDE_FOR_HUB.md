# Integration Guide for Claude Module Communicator (HUB)

This guide is specifically for the HUB orchestrator to understand how to use llm_call as a SPOKE module.

## Quick Integration

```python
# In your HUB orchestrator
from llm_call.llm_call.tools.conversational_delegator import conversational_delegate
from llm_call.llm_call.core.conversation_manager import ConversationManager

# Initialize conversation manager
manager = ConversationManager()

# Start a multi-model task
result = await conversational_delegate(
    model="vertex_ai/gemini-1.5-pro",  # Use Gemini for large context
    prompt="Analyze this 500k character document about quantum computing",
    conversation_name="quantum-analysis-2024"
)

# Get the conversation ID for further iterations
conv_id = result["conversation_id"]

# Claude can continue the conversation
result = await conversational_delegate(
    model="max/opus",  # Switch back to Claude
    prompt="Based on the analysis, what are the practical applications?",
    conversation_id=conv_id
)
```

## Key Capabilities This SPOKE Provides

### 1. Model Routing
- `"max/opus"` → Claude CLI (your local Claude)
- `"vertex_ai/gemini-1.5-pro"` → Google Gemini (1M context!)
- `"gpt-4"`, `"gpt-3.5-turbo"` → OpenAI
- `"ollama/llama3.2"` → Local models

### 2. Conversation State
- All conversations tracked in `logs/conversations.db`
- Full context preserved across model switches
- Can retrieve any conversation for analysis

### 3. Validation
- 16 built-in validators
- Ensures response quality
- Automatic retry with feedback

## Environment Requirements

The SPOKE expects these environment variables (loaded from `.env`):
```bash
PYTHONPATH=./src
OPENAI_API_KEY=sk-...
GOOGLE_APPLICATION_CREDENTIALS=vertex_ai_service_account.json
# ANTHROPIC_API_KEY is currently empty (line 15)
```

## API Reference

### Main Functions

```python
# For single LLM calls
from llm_call.core.caller import make_llm_request

# For conversational delegation
from llm_call.tools.conversational_delegator import conversational_delegate

# For conversation management
from llm_call.core.conversation_manager import ConversationManager
```

### Response Format

```python
{
    "success": True,
    "conversation_id": "uuid-here",
    "model": "vertex_ai/gemini-1.5-pro",
    "content": "The analysis shows...",
    "message_count": 3
}
```

## Typical Orchestration Patterns

### Pattern 1: Large Document Processing
```python
# HUB receives document > 200k chars
if len(document) > 200000:
    # Delegate to Gemini
    result = await conversational_delegate(
        model="vertex_ai/gemini-1.5-pro",
        prompt=f"Analyze: {document}",
        conversation_name="large-doc"
    )
```

### Pattern 2: Multi-Stage Research
```python
# Stage 1: Web search (if Perplexity MCP configured)
# Stage 2: Paper analysis (Gemini for large PDFs)
# Stage 3: Synthesis (GPT-4 or Claude)
# All maintaining conversation context
```

### Pattern 3: Code Generation with Validation
```python
result = await make_llm_request({
    "model": "gpt-4",
    "messages": messages,
    "validation_strategies": [
        get_validator("python"),
        get_validator("length", min_length=50)
    ]
})
```

## Database Schema

### Conversations Table
- `id`: UUID
- `name`: Descriptive name
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `metadata`: JSON (models used, purpose, etc.)

### Messages Table
- `id`: UUID
- `conversation_id`: Foreign key
- `role`: user/assistant/system
- `content`: Message text
- `model`: Which model generated it
- `timestamp`: When created
- `metadata`: JSON (tokens, latency, etc.)

## Error Handling

The SPOKE handles errors gracefully:
```python
{
    "success": False,
    "conversation_id": "uuid",
    "error": "Error message",
    "error_type": "ExceptionType",
    "model": "attempted-model"
}
```

## Performance Notes

- Gemini 1.5 Pro: Best for documents > 200k chars
- GPT-4: Best for complex reasoning
- Claude: Best for nuanced understanding
- Local models: Best for privacy-sensitive data

## Contact

This SPOKE is maintained as part of the llm_call project.
For issues, check the logs in `logs/` directory.