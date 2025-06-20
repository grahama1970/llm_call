# LLM Call Test Commands - Real Feature Testing

**Date**: January 14, 2025  
**Purpose**: Test all documented llm_call features with actual commands

## 1. Basic Model Tests

### GPT Models
```bash
# Test 1.1: GPT-3.5-turbo basic query
llm ask "What is 2+2?" --model gpt-3.5-turbo

# Test 1.2: GPT-4 with specific task
llm ask "Write a Python function to reverse a string" --model gpt-4

# Test 1.3: GPT-4o-mini for quick response
llm ask "Define machine learning in one sentence" --model gpt-4o-mini
```

### Claude Max/Opus
```bash
# Test 1.4: Claude Max basic query
llm ask "Write a haiku about coding" --model max/opus

# Test 1.5: Claude with system prompt
llm ask "Hello" --model max/opus --system "You are a helpful assistant who speaks like Shakespeare"
```

### Vertex AI/Gemini
```bash
# Test 1.6: Gemini Pro
llm ask "List 5 programming languages and their main uses" --model vertex_ai/gemini-1.5-pro

# Test 1.7: Gemini with temperature control
llm ask "Write a creative story opening" --model vertex_ai/gemini-1.5-pro --temperature 0.9
```

## 2. Multimodal Tests

```bash
# Test 2.1: Claude Max image analysis
llm ask "Describe this image in detail" --model max/opus --image /home/graham/workspace/experiments/llm_call/images/test2.png

# Test 2.2: GPT-4 Vision
llm ask "What objects are in this image?" --model gpt-4-vision-preview --image /home/graham/workspace/experiments/llm_call/images/test2.png

# Test 2.3: Gemini Vision
llm ask "Analyze the composition of this image" --model vertex_ai/gemini-pro-vision --image /home/graham/workspace/experiments/llm_call/images/test2.png
```

## 3. Validation Tests

```bash
# Test 3.1: JSON validation
llm ask "Create a JSON object with fields: name (string), age (number), active (boolean)" --model gpt-3.5-turbo --validate json

# Test 3.2: Field presence validation
llm ask "Generate user data as JSON" --model gpt-3.5-turbo --validate json --validate field_present:name,email,id

# Test 3.3: Length validation
llm ask "Write a product description" --model gpt-4 --validate length:min_length=100,max_length=200

# Test 3.4: Code validation (Python)
llm ask "Write a function to calculate fibonacci numbers" --model gpt-4 --validate python

# Test 3.5: Multiple validators
llm ask "Generate a SQL CREATE TABLE statement for users" --model gpt-3.5-turbo --validate sql --validate sql_safe
```

## 4. Conversation Management

```bash
# Test 4.1: Start conversation
python src/llm_call/tools/conversational_delegator.py --model gpt-3.5-turbo --prompt "Let's plan a web application" --conversation-name "webapp-planning"

# Test 4.2: Continue conversation (use ID from 4.1)
python src/llm_call/tools/conversational_delegator.py --model vertex_ai/gemini-1.5-pro --prompt "What database should we use?" --conversation-id [ID-FROM-4.1]

# Test 4.3: Switch models in conversation
python src/llm_call/tools/conversational_delegator.py --model max/opus --prompt "Can you summarize our discussion so far?" --conversation-id [ID-FROM-4.1]
```

## 5. Document/Corpus Analysis

```bash
# Test 5.1: Analyze code directory
llm ask "What are the main components in this codebase?" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core --model vertex_ai/gemini-1.5-pro

# Test 5.2: Specific file type analysis
llm ask "List all validation strategies" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core/validation --include "*.py" --model gpt-4

# Test 5.3: Documentation analysis
llm ask "Summarize the main features" --corpus /home/graham/workspace/experiments/llm_call/docs --include "*.md" --model vertex_ai/gemini-1.5-pro
```

## 6. Configuration File Tests

```bash
# Test 6.1: Create and use JSON config
cat > test_config.json << EOF
{
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 150,
  "messages": [
    {"role": "system", "content": "You are a friendly pirate"},
    {"role": "user", "content": "Tell me about treasure"}
  ]
}
EOF

llm ask --config test_config.json

# Test 6.2: Override config parameters
llm ask "Tell me about ships instead" --config test_config.json --model gpt-4 --temperature 0.3
```

## 7. Advanced Features

```bash
# Test 7.1: System prompts
llm ask "Explain gravity" --model gpt-3.5-turbo --system "You are a physics teacher explaining to a 10-year-old"

# Test 7.2: Temperature control
llm ask "Write a poem about the ocean" --model gpt-4 --temperature 0.1  # Low creativity
llm ask "Write a poem about the ocean" --model gpt-4 --temperature 0.9  # High creativity

# Test 7.3: Max tokens limit
llm ask "Explain the history of computers" --model gpt-3.5-turbo --max-tokens 50

# Test 7.4: Caching
llm ask "What is the capital of France?" --model gpt-3.5-turbo --cache
# Run again - should be faster
llm ask "What is the capital of France?" --model gpt-3.5-turbo --cache
```

## 8. Error Handling Tests

```bash
# Test 8.1: Invalid model
llm ask "Hello" --model non-existent-model

# Test 8.2: Missing API key (unset OPENAI_API_KEY)
unset OPENAI_API_KEY && llm ask "Hello" --model gpt-3.5-turbo

# Test 8.3: Invalid image path
llm ask "Describe this image" --model max/opus --image /non/existent/image.png

# Test 8.4: Invalid validation strategy
llm ask "Generate text" --model gpt-3.5-turbo --validate invalid_validator
```

## 9. Python API Tests

```python
# Test 9.1: Basic ask function
from llm_call import ask
import asyncio

async def test_basic():
    response = await ask("What is Python?", model="gpt-3.5-turbo")
    print(response)

asyncio.run(test_basic())

# Test 9.2: With validation
async def test_validation():
    response = await ask(
        "Generate a user profile as JSON",
        model="gpt-4",
        validation_strategies=["json", "field_present:name,email"]
    )
    print(response)

asyncio.run(test_validation())

# Test 9.3: Multimodal with make_llm_request
from llm_call.core.caller import make_llm_request

async def test_multimodal():
    response = await make_llm_request({
        "model": "max/opus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "/home/graham/workspace/experiments/llm_call/images/test2.png"}}
            ]
        }]
    })
    print(response['choices'][0]['message']['content'])

asyncio.run(test_multimodal())
```

## 10. Slash Command Tests (Claude Desktop)

```bash
# Test 10.1: Basic slash command
/llm "What is the meaning of life?" --model gpt-3.5-turbo

# Test 10.2: With image
/llm "Describe this image" --image /home/graham/workspace/experiments/llm_call/images/test2.png --model max/opus

# Test 10.3: With corpus
/llm "Summarize the validation strategies" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core/validation

# Test 10.4: With config file
/llm --config /path/to/config.json

# Test 10.5: Short alias
/llm_call "Quick test" --model gpt-3.5-turbo
```

## Expected Results Summary

| Test Category | Expected Behavior |
|--------------|-------------------|
| Basic Models | Each model responds with appropriate content |
| Multimodal | Image descriptions match actual image content (coconuts, tropical scene) |
| Validation | Responses pass validation criteria, failures show clear error messages |
| Conversations | Context maintained across calls, conversation IDs generated |
| Corpus Analysis | Accurate summaries of code/documentation structure |
| Config Files | Settings applied correctly, overrides work |
| Advanced | Parameters affect output appropriately |
| Error Handling | Clear, helpful error messages |
| Python API | Functions return expected response formats |
| Slash Commands | Work identically to CLI commands |

## Verification Process

1. Run each command and capture output
2. Check output matches expected behavior
3. For subjective outputs (creativity, style), verify with Gemini:
   ```bash
   llm ask "Does this response match the expected criteria? [paste test details and output]" --model vertex_ai/gemini-1.5-pro
   ```