# Multimodal Usage Guide for llm_call

This guide shows how to use llm_call to describe images using max/opus or other multimodal models.

## Prerequisites

For max/opus (Claude Max) models, set environment variables:
```bash
export CLAUDE_PROXY_EXECUTION_MODE=local
export CLAUDE_PROXY_LOCAL_CLI_PATH=/home/graham/.nvm/versions/node/v22.15.0/bin/claude
unset ANTHROPIC_API_KEY  # Required for OAuth
```

## Method 1: Using Python API (Recommended for Multimodal)

```python
#!/usr/bin/env python3
import asyncio
from llm_call.core.caller import make_llm_request

async def describe_image():
    response = await make_llm_request({
        "model": "max/opus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Please describe this image:"},
                {"type": "image_url", "image_url": {"url": "/path/to/image.png"}}
            ]
        }]
    })
    
    print(response['choices'][0]['message']['content'])

asyncio.run(describe_image())
```

## Method 2: Using the Simple API

```python
from llm_call import ask

# Claude CLI can parse image paths in the prompt
response = await ask(
    prompt="Please describe the image: /path/to/image.png",
    model="max/opus"
)
print(response)
```

## Method 3: Using the Slash Command

The slash command works with simple text prompts that include image paths:

```bash
/llm_call "Please describe the image: /path/to/image.png" --model max/opus
```

Note: The slash command is configured to use local mode by default for max/opus models.

## Method 4: Command Line

From the llm_call directory:

```bash
python -m llm_call.cli.main ask "Describe the image: /path/to/image.png" --model max/opus
```

## Supported Models

Models that support multimodal (image) inputs:
- `max/opus` - Claude Max (local or proxy mode)
- `gpt-4-vision-preview` - OpenAI GPT-4 Vision
- `vertex_ai/gemini-pro-vision` - Google Gemini Pro Vision
- `claude-3-opus-20240229` - Claude 3 Opus (API key required)

## Example Output

When describing `/home/graham/workspace/experiments/llm_call/images/test2.png`:

```
This image shows a beautiful tropical scene featuring coconuts. The main subjects are several brown, fibrous coconuts - some whole and some split open to reveal the white coconut meat inside. The coconuts are arranged on what appears to be a light-colored, sandy surface. The composition includes decorative palm frond shadows cast across the scene, adding an artistic tropical element with warm, natural lighting.
```

## Troubleshooting

1. **"Cannot view images" error**: 
   - Ensure the image path is absolute, not relative
   - Check file permissions
   - For Claude CLI, make sure ANTHROPIC_API_KEY is unset

2. **Proxy mode issues**:
   - Check if Docker container is running
   - Verify proxy is accessible at http://localhost:3010

3. **Local mode issues**:
   - Verify Claude CLI path is correct
   - Ensure Claude CLI is authenticated (`claude` command works)

## Performance Tips

- **Local mode**: Faster response times, direct CLI execution
- **Proxy mode**: Better for production, isolated execution
- **Image size**: Claude CLI handles full-size images; other providers may have limits
- **Base64 conversion**: Automatic for providers that need it, bypassed for Claude CLI