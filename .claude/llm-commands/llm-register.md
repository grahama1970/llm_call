# Register LLM Proxy Module

Register Claude Max Proxy/LLM module with the Module Communicator.

## Usage

```bash
llm-cli register [--name <n>] [--capabilities <list>]
```

## Arguments

- `--name`: Module name (default: llm_proxy)
- `--capabilities`: Override default capabilities

## Examples

```bash
# Basic registration
/llm-register

# Custom registration
/llm-register --name claude_enhancer --capabilities "qa_enhancement,text_generation,analysis"
```

## Default Capabilities

- text_enhancement
- qa_pair_generation
- prompt_engineering
- model_routing
- response_validation
- multi_model_support

---
*Claude Max Proxy Module*
