# Configure Model Routing

Configure automatic model routing for different module requests.

## Usage

```bash
llm-cli model-router <config> [--set-default <model>]
```

## Arguments

- `config`: Routing configuration file
- `--set-default`: Default model for unmatched requests

## Examples

```bash
# Configure routing
/llm-model-router routing_config.json

# Set default model
/llm-model-router routing.json --set-default claude-3-5-sonnet
```

## Routing Configuration

```json
{
  "routes": [
    {
      "source": "sparta",
      "task": "qa_enhancement",
      "model": "max/claude-3-5-sonnet"
    },
    {
      "source": "marker",
      "task": "summarization",
      "model": "gpt-4"
    }
  ]
}
```

---
*Claude Max Proxy Module*
