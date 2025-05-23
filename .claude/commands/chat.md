# Send a message in a chat conversation with the LLM.

Send a message in a chat conversation with the LLM.
    
    Examples:
    - Basic: chat "Hello, how are you?"
    - With model: chat "Tell me a joke" --model claude-3-haiku
    - With system: chat "Explain quantum physics" --system "You are a teacher"

## Usage

Execute this command via the CLI:

```bash
python -m llm_call.cli.main chat $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:chat "your prompt here"

# With options:
/project:chat "prompt" --model gpt-4 --stream
```

---
*Auto-generated from LLM CLI command: chat*
