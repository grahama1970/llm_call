# PURPOSE: llm_call

## 🎯 Core Mission

**llm_call provides a unified interface to multiple LLM providers (OpenAI, Anthropic, Google, Ollama) with automatic failover, rate limiting, and consistent API across all providers.**

## 🚫 What This Tool PREVENTS

1. **Vendor Lock-in** - No dependency on a single LLM provider
2. **API Failures** - Automatic failover to alternative providers
3. **Rate Limit Errors** - Built-in rate limiting and retry logic
4. **Inconsistent APIs** - Unified interface regardless of provider
5. **Cost Overruns** - Model selection based on cost/performance

## ✅ What This Tool ENSURES

1. **Provider Flexibility** - Switch between providers without code changes
2. **High Availability** - Falls back to alternative providers on failure
3. **Consistent Interface** - Same API for all LLM providers
4. **Cost Optimization** - Uses cheaper models when appropriate
5. **Error Handling** - Graceful degradation and clear error messages

## 📊 How It Works

```
1. Request comes in with prompt/config
           ↓
2. Select best provider based on:
   - Availability
   - Cost
   - Performance requirements
           ↓
3. Apply rate limiting
           ↓
4. Make API call
           ↓
5. If fails: Try next provider
           ↓
6. Return unified response format
```

## 🔧 Key Features

1. **Multi-Provider Support**
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude)
   - Google (Gemini)
   - Ollama (local models)

2. **Smart Routing**
   - Cost-based selection
   - Performance-based selection
   - Availability-based failover

3. **Rate Limiting**
   - Per-provider limits
   - Automatic backoff
   - Queue management

4. **Unified API**
   ```python
   from llm_call import make_llm_request
   
   response = await make_llm_request({
       "model": "auto",  # Auto-selects best model
       "messages": [...],
       "temperature": 0.7
   })
   ```

## 💡 Key Principles

1. **Provider Agnostic** - Code shouldn't care which LLM is used
2. **Fail Gracefully** - Always try alternatives before giving up
3. **Cost Conscious** - Use expensive models only when needed
4. **Transparent** - Clear logging of provider selection
5. **Async First** - Built for high-performance async operations

## 🚀 Common Use Cases

1. **SPARTA Alternative Finding** - When documents are paywalled
2. **Test Verification** - Multi-AI consensus (Gemini + Perplexity)
3. **Code Generation** - Flexible model selection
4. **Document Analysis** - Cost-effective processing
5. **Real-time Chat** - Low-latency responses

## 🔗 Integration Points

- Used by SPARTA for alternative finding
- Used by claude-test-reporter for multi-AI verification
- Used by granger_hub for LLM operations
- Available to all Granger modules

---

*"One API to rule them all, one interface to bind them."*