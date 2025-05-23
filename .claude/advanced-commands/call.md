# Make an LLM call with full configuration support.

Make an LLM call with full configuration support.
    
    You can either:
    1. Use a config file (JSON/YAML) for complete control
    2. Use command-line options for common settings
    3. Mix both (CLI options override config file)
    
    Examples:
    - Config file: call --config request.json
    - CLI options: call --model gpt-4 --prompt "Hello"
    - Mixed: call --config base.yaml --model claude-3-opus
    - With validation: call -p "List 3 colors" --json --validation json_string

## Usage

```bash
python main_advanced.py call $ARGUMENTS
```

## Examples

```bash
# In Claude Code:
/project:call [arguments]
```

---
*Auto-generated slash command*
