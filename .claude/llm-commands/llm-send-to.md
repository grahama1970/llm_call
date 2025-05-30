# Send Enhanced Data to Modules

Send LLM-processed data to other modules.

## Usage

```bash
llm-cli send-to <target_module> <data> [--type <data_type>]
```

## Arguments

- `target_module`: Target module name
- `data`: Enhanced data file or content
- `--type`: Data type (enhanced_qa, generated_text, analysis)

## Examples

```bash
# Send enhanced Q&A to Unsloth
/llm-send-to unsloth enhanced_qa.json --type enhanced_qa

# Send to ArangoDB
/llm-send-to arangodb processed_entities.json

# Send analysis results
/llm-send-to sparta analysis_results.json --type analysis
```

---
*Claude Max Proxy Module*
