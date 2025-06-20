# Usage Function Test Summary

**Generated**: January 16, 2025  
**Purpose**: Verify llm_call produces same results as direct API calls

## Test Results Overview

### ✅ F1.1 - GPT-4o-mini Basic Math
- **Status**: Working
- **Model**: gpt-4o-mini  
- **Test**: "What is 2+2?"
- **Result**: All methods returned "4"

### ✅ F1.2 - Vertex AI Python Generation  
- **Status**: Working (after cache fix)
- **Model**: vertex_ai/gemini-1.5-flash
- **Test**: "Write a Python function to reverse a string"
- **Result**: All methods returned valid Python code

### ✅ F1.3 - Ollama ML Definition
- **Status**: Working (after cache fix)
- **Model**: ollama/phi3:mini
- **Test**: "Define ML in one sentence"  
- **Result**: All methods returned ML definitions

### ✅ F1.4 - Claude Haiku Test
- **Status**: Working (with local execution mode)
- **Model**: max/opus (Claude CLI subprocess)
- **Test**: "Write a haiku about coding"
- **Result**: All methods returned haikus about coding
- **Fix**: Set CLAUDE_PROXY_EXECUTION_MODE=local and CLAUDE_CLI_PATH

### ✅ F1.5 - Ollama List Languages
- **Status**: Working
- **Model**: ollama/codellama:latest (qwen2.5:32b not available)
- **Test**: "List 5 programming languages"
- **Result**: All methods returned 5 languages

### ✅ F1.6 - Perplexity Weather
- **Status**: Working  
- **Model**: perplexity/llama-3.1-sonar-small-128k-online
- **Test**: "What is the weather today?"
- **Result**: All methods returned weather data with sources

## Key Findings

### 1. Caching Issues
- Redis caching causes identical prompts to return same result
- Solution: Add unique timestamps to each prompt
- Affects all tests until fixed

### 2. Model Availability
- max/opus requires OAuth, uses subprocess call to `claude -p`
- Direct baseline = subprocess call, not litellm API
- Set CLAUDE_PROXY_EXECUTION_MODE=local for local execution
- Claude API models need ANTHROPIC_API_KEY
- Ollama models vary by environment
- Always check available models before testing

### 3. Response Extraction
- Different providers return data differently
- Need flexible extraction logic for:
  - `response.choices[0].message.content`
  - `response['choices'][0]['message']['content']`
  - Dict vs object responses

### 4. llm_call Functionality
- ✅ Successfully passes through responses without corruption
- ✅ Works with multiple providers (OpenAI, Vertex AI, Ollama, Perplexity)
- ✅ Handles different response formats correctly
- ✅ Online/search models (Perplexity) work properly

## Lessons for Future Testing

1. **Always add unique identifiers to prompts** to avoid cache collisions
2. **Check model availability first** - don't assume models exist
3. **Understand provider limitations** - some models can't be called directly
4. **Keep tests simple** - focus on comparing outputs, not validating quality
5. **Document environment requirements** clearly (API keys, models, etc.)

## Next Steps

1. Fix F1.4 by either:
   - Using a different Claude model that works with API keys
   - Skipping direct comparison for OAuth-only models
   
2. Create multi-AI judge functions as outlined in FUTURE_IMPLEMENTATION.md

3. Test remaining functionality:
   - Validation strategies
   - Conversation persistence
   - Multimodal capabilities
   - Document processing