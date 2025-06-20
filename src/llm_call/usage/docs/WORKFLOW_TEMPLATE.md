# LLM_CALL Testing Workflow Template

## Purpose
This workflow ensures transparent, verifiable testing by comparing direct litellm API calls with llm_call functionality. Each test follows the same pattern, making it impossible to fake results.

## Standard Workflow Pattern

### 1. Setup Phase
```python
# Import both libraries
import litellm
from llm_call import ask, make_llm_request

# Configure
litellm.drop_params = True
litellm.set_verbose = False
```

### 2. Direct LiteLLM Call (Control)
```python
# This is our baseline - what we know works
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Your prompt here"}],
    temperature=0.1,  # Low for consistency
    max_tokens=100
)
litellm_result = response.choices[0].message.content
print(f"LiteLLM Result: {litellm_result}")
```

### 3. LLM_CALL Equivalent (Test)
```python
# This is what we're testing
llm_call_result = await ask(
    prompt="Your prompt here",
    model="gpt-3.5-turbo", 
    temperature=0.1,
    max_tokens=100
)
print(f"LLM_CALL Result: {llm_call_result}")
```

### 4. Comparison & Verification
```python
# Both should produce similar results
# Key things to check:
# 1. Both calls succeed/fail together
# 2. Both return substantive responses
# 3. Both contain expected keywords/patterns
```

## Test Categories & Workflows

### Basic Model Calls (Tests 1-4)
**Workflow**: Simple prompt → response comparison
```python
# LiteLLM
messages = [{"role": "user", "content": prompt}]
litellm_response = litellm.completion(model=model, messages=messages)

# LLM_CALL
llm_call_response = await ask(prompt=prompt, model=model)
```

### Multimodal (Tests 5-6)
**Workflow**: Image + prompt → description comparison
```python
# LiteLLM (with base64 encoding)
base64_image = base64.b64encode(open(image_path, 'rb').read()).decode()
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
    ]
}]

# LLM_CALL (handles encoding internally)
config = {
    "model": model,
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_path}}
        ]
    }]
}
response = await make_llm_request(config)
```

### Validation (Tests 7-9)
**Workflow**: Request with constraints → validated response
```python
# LiteLLM (no built-in validation)
response = litellm.completion(model=model, messages=messages)
# Manual validation of response

# LLM_CALL (automatic validation & retry)
config = {
    "model": model,
    "messages": messages,
    "validation": [
        {"type": "json"},
        {"type": "field_present", "params": {"required_fields": ["name", "age"]}}
    ]
}
response = await make_llm_request(config)
```

### Conversation Management (Tests 10-11)
**Workflow**: Multi-turn conversation with context
```python
# LiteLLM (manual conversation tracking)
messages = []
messages.append({"role": "user", "content": "First message"})
response1 = litellm.completion(model=model, messages=messages)
messages.append({"role": "assistant", "content": response1.choices[0].message.content})
messages.append({"role": "user", "content": "Second message"})
response2 = litellm.completion(model=model, messages=messages)

# LLM_CALL (automatic conversation management)
from llm_call.tools.conversational_delegator import conversational_delegate
result1 = await conversational_delegate(
    model=model,
    prompt="First message",
    conversation_name="test-conv"
)
result2 = await conversational_delegate(
    model=model,
    prompt="Second message", 
    conversation_id=result1["conversation_id"]
)
```

### Configuration (Tests 12-13)
**Workflow**: JSON/YAML config → configured behavior
```python
# Both use same config structure
config = {
    "model": "gpt-3.5-turbo",
    "messages": messages,
    "temperature": 0.9,
    "system": "You are a pirate"
}

# LiteLLM
response = litellm.completion(**config)

# LLM_CALL  
response = await make_llm_request(config)
```

### Document/Corpus Analysis (Tests 14-15)
**Workflow**: Multiple files → consolidated analysis
```python
# LiteLLM (manual file reading)
file_contents = []
for file in Path(directory).glob("*.py"):
    file_contents.append(file.read_text())
combined = "\n---\n".join(file_contents)
messages = [{"role": "user", "content": f"Analyze this code:\n{combined}"}]

# LLM_CALL CLI (automatic corpus handling)
# python -m llm_call.cli.main ask "Analyze the code" --corpus /path/to/dir
```

## Output Format

Each test should produce:

```
========================================
TEST: [Name]
========================================

1. DIRECT LITELLM:
   Response: [actual response]
   Tokens: [count]
   Success: ✅/❌

2. LLM_CALL:
   Response: [actual response]  
   Success: ✅/❌

3. COMPARISON:
   Match: ✅/❌
   Reason: [why they match/differ]

4. VERIFICATION:
   Expected: [what we expected]
   Found: [what we found]
   Valid: ✅/❌
========================================
```

## Key Principles

1. **Always show actual responses** - No hiding behind "response received"
2. **Always run both methods** - Direct comparison is the only truth
3. **Save results to file** - JSON output for external verification
4. **Exit codes matter** - 0 for success, 1 for any failure
5. **Timestamps everything** - Know when each test ran
6. **Check environment** - Show which API keys are set

## Verification Checklist

- [ ] Both methods called with identical parameters
- [ ] Actual responses printed (not just success/fail)
- [ ] Responses contain expected content
- [ ] Error messages are specific and actionable
- [ ] Results saved to timestamped file
- [ ] Exit code reflects true pass/fail status