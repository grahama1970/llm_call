# Runpod Integration Guide

## Overview

LLM Call now supports Runpod inference endpoints, allowing you to deploy and use 30-70B parameter models through OpenAI-compatible APIs. Runpod provides cost-effective GPU infrastructure for running large language models.

## How It Works

Runpod support is implemented through LiteLLM's OpenAI-compatible endpoint feature. When you specify a model with the `runpod/` prefix, llm_call automatically:

1. Routes the request through LiteLLM
2. Converts the model name to OpenAI format
3. Sets the appropriate Runpod endpoint URL
4. Handles authentication (Runpod uses empty API keys)

## Model Name Formats

### Format 1: With Pod ID
```python
"model": "runpod/{pod_id}/{model_name}"
```
Example: `"runpod/abc123xyz/llama-3-70b"`

This format automatically constructs the endpoint URL from the pod ID.

### Format 2: With Custom API Base
```python
"model": "runpod/{model_name}",
"api_base": "https://your-endpoint-8000.proxy.runpod.net/v1"
```
Example: `"runpod/llama-3-70b"` with explicit `api_base`

Use this when you want to specify the endpoint URL directly.

## Usage Examples

### Basic Usage with Pod ID
```python
import asyncio
from llm_call import make_llm_request

async def main():
    config = {
        "model": "runpod/your-pod-id/llama-3-70b",
        "messages": [
            {"role": "user", "content": "Explain quantum computing"}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    response = await make_llm_request(**config)
    print(response)

asyncio.run(main())
```

### Using Custom Endpoint
```python
config = {
    "model": "runpod/mixtral-8x7b",
    "api_base": "https://custom-pod-8000.proxy.runpod.net/v1",
    "messages": [
        {"role": "user", "content": "Write a haiku"}
    ]
}
```

### With Custom Fine-tuned Models
```python
config = {
    "model": "runpod/pod-123/meta-llama/Llama-3-70b-instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Generate Python code"}
    ],
    "temperature": 0.2  # Lower for code generation
}
```

## Runpod Setup

1. **Create a Runpod Account**: Sign up at [runpod.io](https://runpod.io)

2. **Deploy a Model**: 
   - Choose a GPU (A6000 48GB for smaller models, A100 80GB for 70B models)
   - Use a one-click template or custom Docker image
   - Deploy with vLLM or TGI for OpenAI compatibility

3. **Get Your Pod ID**:
   - Find it in the Runpod dashboard
   - It appears in your endpoint URL: `https://{pod_id}-8000.proxy.runpod.net`

4. **Test the Endpoint**:
   ```bash
   curl https://your-pod-id-8000.proxy.runpod.net/v1/models
   ```

## Supported Features

- ✅ Chat completions
- ✅ Streaming responses
- ✅ Custom temperature and max_tokens
- ✅ System messages
- ✅ Multi-turn conversations
- ✅ JSON mode (if supported by model)

## Common Models

- `llama-3-70b` - Meta's Llama 3 70B
- `mixtral-8x7b` - Mistral's Mixture of Experts model
- `deepseek-coder-33b` - Code generation model
- `qwen-72b` - Alibaba's Qwen model
- Custom fine-tuned models

## Troubleshooting

### Error: "Runpod model requires either pod_id..."
**Solution**: Either include the pod ID in the model name or provide an `api_base` parameter.

### Connection Timeout
**Solution**: Ensure your pod is running. Check the Runpod dashboard for pod status.

### Model Not Found
**Solution**: Verify the model name matches what's deployed on your pod. Check with:
```bash
curl https://your-pod-id-8000.proxy.runpod.net/v1/models
```

### Authentication Errors
**Solution**: Runpod uses empty API keys by default. Don't provide an API key unless you've configured custom authentication.

## Cost Optimization

1. **Use Spot Instances**: Cheaper but may be interrupted
2. **Stop Pods When Not in Use**: Runpod charges by the hour
3. **Choose Appropriate GPU**: Don't use A100 for models that fit on A6000
4. **Enable Quantization**: Use AWQ or GPTQ models to reduce memory usage

## Advanced Configuration

### Using Environment Variables
```bash
export RUNPOD_POD_ID="your-pod-id"
```

Then in your code:
```python
import os

config = {
    "model": f"runpod/{os.getenv('RUNPOD_POD_ID')}/llama-3-70b",
    ...
}
```

### Custom Headers
If you need custom headers for your Runpod endpoint:
```python
config = {
    "model": "runpod/model-name",
    "api_base": "https://your-endpoint/v1",
    "extra_headers": {
        "X-Custom-Header": "value"
    }
}
```

## Performance Tips

1. **Warm Up the Model**: Make a test request after pod startup
2. **Batch Requests**: Use appropriate batch sizes for throughput
3. **Monitor GPU Memory**: Check Runpod metrics dashboard
4. **Use Streaming**: For long responses, enable streaming

## See Also

- [Runpod Documentation](https://docs.runpod.io/)
- [LiteLLM OpenAI Compatible Endpoints](https://docs.litellm.ai/docs/providers/openai_compatible)
- [Example Script](../../examples/runpod_example.py)