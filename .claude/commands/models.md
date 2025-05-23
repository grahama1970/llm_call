# List and manage LLM models.

List and manage LLM models.
    
    Examples:
    - List all: models --available
    - Show current: models --current

## Usage

Execute this command via the CLI:

```bash
python -m llm_call.cli.main models $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:models "your prompt here"

# With options:
/project:models "prompt" --model gpt-4 --stream
```

---
*Auto-generated from LLM CLI command: models*
