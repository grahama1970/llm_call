# Ask a question to the LLM and get a response.

Ask a question to the LLM and get a response.
    
    Examples:
    - Basic: ask "What is Python?"
    - With model: ask "Explain AI" --model gpt-4
    - Streaming: ask "Tell a story" --stream
    - JSON mode: ask "List 3 colors" --json

## Usage

Execute this command via the CLI:

```bash
python -m llm_call.cli.main ask $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:ask "your prompt here"

# With options:
/project:ask "prompt" --model gpt-4 --stream
```

---
*Auto-generated from LLM CLI command: ask*
