# Receive Data for LLM Processing

Receive data from other modules for LLM processing.

## Usage

```bash
llm-cli receive-from <source_module> [--auto-process] [--model <model>]
```

## Arguments

- `source_module`: Source module name
- `--auto-process`: Automatically process received data
- `--model`: Default model for processing

## Examples

```bash
# Receive from SPARTA
/llm-receive-from sparta

# Auto-process with Claude
/llm-receive-from marker --auto-process --model max/claude-3-5-sonnet

# Receive for enhancement
/llm-receive-from arangodb --auto-process
```

---
*Claude Max Proxy Module*
