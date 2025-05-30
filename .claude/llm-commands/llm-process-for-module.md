# Process Data for Specific Module

Process data using LLM for a specific target module.

## Usage

```bash
llm-cli process-for-module <source_module> <data> [--target <module>] [--model <model>]
```

## Arguments

- `source_module`: Module that sent the data
- `data`: Data to process (file or inline)
- `--target`: Target module for output format
- `--model`: Specific model to use

## Examples

```bash
# Process SPARTA data for Unsloth
/llm-process-for-module sparta qa_data.json --target unsloth

# Enhance marker extraction for ArangoDB
/llm-process-for-module marker extracted.json --target arangodb --model claude-3-5-sonnet

# Process with specific formatting
/llm-process-for-module arangodb entities.json --target unsloth --model gpt-4
```

## Processing Types

- **Enhancement**: Improve Q&A quality
- **Formatting**: Adapt to target schema
- **Generation**: Create additional training data
- **Validation**: Verify data quality

---
*Claude Max Proxy Module*
