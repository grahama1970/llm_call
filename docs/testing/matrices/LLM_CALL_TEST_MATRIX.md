# LLM Call Feature Test Matrix

**Generated**: 2025-01-14  
**Purpose**: Comprehensive testing of all llm_call features with real LLM calls and external verification

## Test Categories

1. **Basic Model Calls** - Different models with simple queries
2. **Multimodal** - Image analysis with various models  
3. **Validation** - Response validation strategies
4. **Conversation Management** - Multi-turn conversations
5. **Configuration** - Using config files
6. **Document Processing** - Corpus analysis
7. **Advanced Features** - Streaming, system prompts, etc.

## Test Commands

| ID | Category | Feature | CLI Command | Slash Command | Expected Response | Verification Method |
|----|----------|---------|-------------|---------------|-------------------|-------------------|
| 1 | Basic Model | GPT-3.5-turbo | `python -m llm_call.cli.main ask "What is the capital of France?" --model gpt-3.5-turbo` | `/llm "What is the capital of France?" --model gpt-3.5-turbo` | "Paris" with explanation | Simple verification |
| 2 | Basic Model | GPT-4o-mini | `python -m llm_call.cli.main ask "Explain quantum computing in one sentence" --model gpt-4o-mini` | `/llm "Explain quantum computing in one sentence" --model gpt-4o-mini` | One-sentence explanation | Length check |
| 3 | Basic Model | Claude Max/Opus | `python -m llm_call.cli.main ask "Write a haiku about programming" --model max/opus` | `/llm "Write a haiku about programming" --model max/opus` | 3-line haiku format | Format verification |
| 4 | Basic Model | Vertex AI Gemini | `python -m llm_call.cli.main ask "List 3 benefits of exercise" --model vertex_ai/gemini-1.5-pro` | `/llm "List 3 benefits of exercise" --model vertex_ai/gemini-1.5-pro` | Numbered list of 3 items | Count verification |
| 5 | Multimodal | Claude Vision | `python -m llm_call.cli.main ask "Describe this image: /home/graham/workspace/experiments/llm_call/images/test2.png" --model max/opus` | `/llm "Describe this image" --image /home/graham/workspace/experiments/llm_call/images/test2.png --model max/opus` | Description of coconuts/tropical scene | Content match |
| 6 | Multimodal | GPT-4 Vision | `python -m llm_call.cli.main ask "What objects are in this image?" --model gpt-4-vision-preview --image /home/graham/workspace/experiments/llm_call/images/test2.png` | `/llm "What objects are in this image?" --image /home/graham/workspace/experiments/llm_call/images/test2.png --model gpt-4-vision-preview` | List of objects (coconuts, etc.) | Object detection |
| 7 | Validation | JSON Output | `python -m llm_call.cli.main ask "Generate a JSON object with name and age fields" --model gpt-3.5-turbo --validate json --validate field_present:name,age` | `/llm "Generate a JSON object with name and age fields" --validate json --validate field_present:name,age` | Valid JSON with required fields | JSON parse & field check |
| 8 | Validation | Length Check | `python -m llm_call.cli.main ask "Write a story" --model gpt-3.5-turbo --validate length:min_length=200` | `/llm "Write a story" --validate length:min_length=200` | Story with 200+ characters | Length verification |
| 9 | Validation | Code Validation | `python -m llm_call.cli.main ask "Write a Python function to calculate factorial" --model gpt-4 --validate python` | `/llm "Write a Python function to calculate factorial" --validate python` | Valid Python code | Syntax check |
| 10 | Conversation | Multi-turn | `python src/llm_call/tools/conversational_delegator.py --model gpt-3.5-turbo --prompt "Let's discuss AI" --conversation-name "ai-discussion"` | N/A | Conversation ID returned | ID format check |
| 11 | Conversation | Continue | `python src/llm_call/tools/conversational_delegator.py --model gpt-4 --prompt "What are the risks?" --conversation-id <previous-id>` | N/A | Contextual response about AI risks | Context verification |
| 12 | Config File | JSON Config | `echo '{"model": "gpt-3.5-turbo", "messages": [{"role": "system", "content": "You are a pirate"}, {"role": "user", "content": "Hello"}], "temperature": 0.9}' > pirate.json && python -m llm_call.cli.main ask --config pirate.json` | `/llm --config pirate.json` | Pirate-themed response | Style verification |
| 13 | Config File | Override | `python -m llm_call.cli.main ask "Tell me about cats" --config pirate.json --model gpt-4 --temperature 0.1` | `/llm "Tell me about cats" --config pirate.json --model gpt-4` | Cat info in pirate style with GPT-4 | Model & style check |
| 14 | Document | Corpus Analysis | `python -m llm_call.cli.main ask "Summarize the code" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core --model vertex_ai/gemini-1.5-pro` | `/llm "Summarize the code structure" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core` | Summary of core module structure | Content relevance |
| 15 | Document | File Filtering | `python -m llm_call.cli.main ask "What validation strategies are available?" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core/validation --include "*.py" --model gpt-4` | `/llm "List validation strategies" --corpus /home/graham/workspace/experiments/llm_call/src/llm_call/core/validation` | List of 16 validators | Count verification |
| 16 | Advanced | System Prompt | `python -m llm_call.cli.main ask "Hello" --model gpt-3.5-turbo --system "You are a medieval knight"` | `/llm "Hello" --system "You are a medieval knight"` | Medieval-style greeting | Style verification |
| 17 | Advanced | Temperature | `python -m llm_call.cli.main ask "Write a creative story opening" --model gpt-3.5-turbo --temperature 0.9` | `/llm "Write a creative story opening" --temperature 0.9` | Creative, varied response | Creativity check |
| 18 | Advanced | Max Tokens | `python -m llm_call.cli.main ask "Explain machine learning" --model gpt-3.5-turbo --max-tokens 50` | `/llm "Explain machine learning" --max-tokens 50` | Truncated explanation (~50 tokens) | Length limit |
| 19 | Advanced | Streaming | `python -c "import asyncio; from llm_call import make_llm_request; asyncio.run(make_llm_request({'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': 'Count to 10'}], 'stream': True}))"` | N/A | Streaming response chunks | Stream verification |
| 20 | Error Handling | Invalid Model | `python -m llm_call.cli.main ask "Hello" --model invalid-model-xyz` | `/llm "Hello" --model invalid-model-xyz` | Error message about invalid model | Error format |
| 21 | Text-Only | Simple String | `python -c "from llm_call import ask; import asyncio; print(asyncio.run(ask('What is 2+2?', model='gpt-3.5-turbo')))"` | N/A | "4" or "2+2 equals 4" | Calculation check |
| 22 | Caching | Cache Test | `python -m llm_call.cli.main ask "What is the weather?" --model gpt-3.5-turbo --cache` | `/llm "What is the weather?" --cache` | Weather-related response (cached on 2nd call) | Cache hit verification |

## Verification Script

To verify these tests, use Gemini or Perplexity to judge the responses:

```python
import asyncio
from llm_call import ask

async def verify_response(test_id, command, expected, actual_response):
    prompt = f"""
    Test ID: {test_id}
    Command: {command}
    Expected: {expected}
    Actual Response: {actual_response}
    
    Does the actual response match the expected criteria? Answer YES or NO with brief explanation.
    """
    
    verification = await ask(prompt, model="vertex_ai/gemini-1.5-pro")
    return verification

# Run verification for each test
```

## Python Import Examples

```python
# Basic ask
from llm_call import ask
response = await ask("What is Python?", model="gpt-3.5-turbo")

# With validation
response = await ask(
    "Generate a JSON object", 
    model="gpt-4",
    validation_strategies=["json", "field_present:id,name"]
)

# Multimodal
from llm_call.core.caller import make_llm_request
response = await make_llm_request({
    "model": "max/opus",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {"type": "image_url", "image_url": {"url": "/path/to/image.png"}}
        ]
    }]
})

# Conversation management
from llm_call.tools.conversational_delegator import conversational_delegate
result = await conversational_delegate(
    model="vertex_ai/gemini-1.5-pro",
    prompt="Analyze this large document...",
    conversation_name="doc-analysis"
)
```

## Notes

1. **API Keys Required**: Ensure all API keys are set in `.env` file
2. **Claude Max**: Requires authentication via `claude` CLI
3. **Images**: Test images are at `/home/graham/workspace/experiments/llm_call/images/`
4. **Caching**: Use `--cache` flag to reduce API costs during testing
5. **Verification**: Each test should be verified by an independent LLM (Gemini/Perplexity)

## Success Criteria

- ✅ All basic model calls return appropriate responses
- ✅ Multimodal commands correctly analyze images
- ✅ Validation strategies properly enforce constraints
- ✅ Conversations maintain context across calls
- ✅ Config files override defaults correctly
- ✅ Corpus analysis summarizes code accurately
- ✅ Advanced features work as documented
- ✅ Error handling provides clear feedback