# Generate Claude Code slash commands for all CLI commands.

Generate Claude Code slash commands for all CLI commands.
    
    This creates markdown files in .claude/commands/ that enable using
    CLI commands directly from the Claude Code interface.
    
    Examples:
    - Basic: generate-claude
    - Custom output: generate-claude --output ~/my-commands
    - With prefix: generate-claude --prefix llm

## Usage

Execute this command via the CLI:

```bash
python -m llm_call.cli.main generate_claude $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:generate_claude "your prompt here"

# With options:
/project:generate_claude "prompt" --model gpt-4 --stream
```

---
*Auto-generated from LLM CLI command: generate_claude*
