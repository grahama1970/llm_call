# Enhance Q&A Tuples

Enhance question-answer tuples using LLM capabilities.

## Usage

```bash
llm-cli enhance-qa <qa_file> [--model <model>] [--enhancement <type>]
```

## Arguments

- `qa_file`: Q&A tuples file
- `--model`: Model to use for enhancement
- `--enhancement`: Enhancement type (rephrase, expand, validate)

## Examples

```bash
# Basic enhancement
/llm-enhance-qa sparta_qa.json

# Expand answers with Claude
/llm-enhance-qa cyber_qa.json --model max/claude-3-5-sonnet --enhancement expand

# Validate and improve
/llm-enhance-qa training_qa.json --enhancement validate
```

## Enhancement Types

- **rephrase**: Improve clarity and variety
- **expand**: Add context and detail
- **validate**: Check accuracy and consistency
- **augment**: Generate variations

---
*Claude Max Proxy Module*
