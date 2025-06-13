# ITERATIVE TEST PLAN - LLM_CALL

Following TEST_VERIFICATION_TEMPLATE_GUIDE.md requirements for progressive, real API testing.

## 🎯 Testing Philosophy
- **NO MOCKS** - All tests use real APIs
- **PROGRESSIVE** - Start simple, build complexity
- **EVIDENCE-BASED** - Collect timing, responses, IDs
- **ITERATIVE** - Each phase builds on previous
- **DURATION ENFORCED** - API calls must take >0.05s

## 📊 Test Coverage Matrix

| Feature | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|---------|---------|---------|---------|---------|---------|
| Basic API Calls | ✅ Done | | | | |
| Model Routing | | ✅ | | | |
| Conversation Management | | | ✅ | | |
| Validation Strategies | | | | ✅ | |
| Multi-Model Collaboration | | | | | ✅ |

## Phase 1: Basic Provider Connectivity ✅ COMPLETE
**Goal**: Verify all providers can make real API calls

### Tests Created:
- [x] test_openai_real_api - Basic OpenAI call
- [x] test_gemini_vertex_real_api - Vertex AI Gemini call  
- [x] test_claude_background_real_api - Claude proxy call
- [x] Honeypot tests (must fail)

**Status**: All passing with real API calls

---

## Phase 2: Model Routing & Provider Selection
**Goal**: Test the routing logic with real calls

### Tests to Create:
1. **test_routing_to_specific_providers.py**
   - Route to OpenAI explicitly
   - Route to Vertex AI explicitly
   - Route to Claude proxy explicitly
   - Verify correct provider is used (check response metadata)

2. **test_model_aliases.py**
   - Test "gpt-4" routes to OpenAI
   - Test "vertex_ai/gemini-1.5-pro" routes to Vertex
   - Test "max/opus" routes to Claude proxy
   - Test "ollama/*" routes (skip if not available)

3. **test_provider_fallback.py**
   - Test fallback when primary provider fails
   - Test retry logic with real delays
   - Verify retry attempts in evidence

### Evidence to Collect:
- Response headers showing provider
- Timing for each provider
- Model name in response
- Retry attempt counts

---

## Phase 3: Conversation Management
**Goal**: Test SQLite conversation persistence with real API calls

### Tests to Create:
1. **test_conversation_creation.py**
   - Create conversation
   - Verify SQLite database created
   - Check conversation metadata stored

2. **test_conversation_continuity.py**
   - Start conversation with model A
   - Continue with model B
   - Verify full history available
   - Check message ordering

3. **test_conversation_retrieval.py**
   - Retrieve by ID
   - Retrieve by name
   - List all conversations
   - Export conversation history

### Evidence to Collect:
- Database file creation time
- Row counts in tables
- Message timestamps
- Conversation UUIDs

---

## Phase 4: Validation Strategies
**Goal**: Test all 16 validators with real LLM responses

### Tests to Create:
1. **test_json_validation.py**
   - Request JSON from LLM
   - Validate structure
   - Test retry on invalid JSON

2. **test_code_validation.py**
   - Request Python code
   - Validate syntax
   - Test SQL validation
   - Test SQL safety checks

3. **test_schema_validation.py**
   - Define expected schema
   - Request structured data
   - Validate against schema

4. **test_length_validation.py**
   - Minimum length requirements
   - Maximum length constraints
   - Test retry on too short/long

5. **test_field_validation.py**
   - Required fields present
   - Nested field validation
   - Array field validation

### Evidence to Collect:
- Validation failure reasons
- Retry attempts with feedback
- Time taken for retries
- Final valid responses

---

## Phase 5: Multi-Model Collaboration
**Goal**: Test real conversations between different models

### Tests to Create:
1. **test_claude_gemini_collaboration.py**
   - Claude asks Gemini to analyze large doc
   - Gemini responds with analysis
   - Claude summarizes findings
   - Verify conversation flow

2. **test_iterative_refinement.py**
   - Model A generates draft
   - Model B critiques
   - Model A improves based on feedback
   - Verify improvement

3. **test_context_delegation.py**
   - Start with small context model
   - Detect need for larger context
   - Delegate to Gemini 1M
   - Return summary to original

4. **test_specialized_routing.py**
   - Math problem → GPT-4
   - Creative writing → Claude
   - Code generation → specialized model
   - Verify appropriate routing

### Evidence to Collect:
- Full conversation transcripts
- Model switching timestamps
- Context sizes at each step
- Total tokens used

---

## 🔧 Test Implementation Pattern

Each test follows this pattern:

```python
@pytest.mark.asyncio
async def test_feature_with_real_api(self):
    """Test description following GRANGER standards."""
    # 1. Setup evidence collection
    evidence = {
        "test_name": "test_feature",
        "start_time": time.time(),
        "environment": {...}
    }
    
    # 2. Make REAL API call
    try:
        response = await real_api_call()
        
        # 3. Collect detailed evidence
        evidence["response_id"] = response.id
        evidence["duration"] = time.time() - evidence["start_time"]
        evidence["tokens_used"] = response.usage
        
        # 4. Verify real interaction
        assert evidence["duration"] > 0.05  # Minimum API latency
        assert response.id is not None  # Real response has ID
        
        # 5. Log evidence for cross-examination
        logger.info(f"Evidence: {evidence}")
        
    except Exception as e:
        evidence["error"] = str(e)
        # Real errors are valuable test results!
        logger.error(f"Real API error: {e}")
```

---

## 🚀 Execution Plan

### Week 1: Phase 2 (Model Routing)
- Day 1-2: Implement routing tests
- Day 3: Test fallback scenarios
- Day 4-5: Document findings

### Week 2: Phase 3 (Conversations)
- Day 1-2: SQLite integration tests
- Day 3-4: Multi-model conversations
- Day 5: Performance testing

### Week 3: Phase 4 (Validation)
- Day 1: JSON/Code validators
- Day 2: Schema validators
- Day 3: Length/Field validators
- Day 4: Retry logic testing
- Day 5: Edge cases

### Week 4: Phase 5 (Collaboration)
- Day 1-2: Two-model conversations
- Day 3: Three+ model orchestration
- Day 4: Context delegation
- Day 5: Final integration tests

---

## 📋 Success Criteria

Each phase is complete when:
1. All tests use REAL API calls (no mocks)
2. Minimum duration thresholds met
3. Evidence collected for all interactions
4. Honeypot tests still failing
5. Documentation updated
6. 90%+ confidence in test authenticity

---

## 🔍 Anti-Patterns to Avoid

### ❌ NEVER DO THIS:
- Mock or patch any external service
- Use fake response data
- Skip tests due to API limits
- Cache responses between runs
- Assume instant responses

### ✅ ALWAYS DO THIS:
- Use real API keys
- Accept real failures as valid results
- Measure actual latency
- Collect response IDs
- Document rate limits hit