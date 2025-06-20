# Test Priority Guide for LLM Call

## Priority Levels

### **CRITICAL** - Core Functionality Tests
Tests that MUST pass for the system to be considered operational. Failure indicates complete system breakdown.

**Criteria:**
- Basic LLM calls to each provider (OpenAI, Anthropic, Vertex AI)
- Essential validation (JSON, code syntax)
- API health endpoints
- Redis connection for caching
- Conversation state persistence
- Docker container startup

**Examples:**
- Basic model queries (GPT-3.5, GPT-4, max/opus, Gemini)
- JSON validation for structured outputs
- Health check endpoints
- Redis cache initialization
- Conversational delegator basic flow

### MODERATE - Important Feature Tests
Tests for features that enhance functionality but system can operate without them temporarily.

**Criteria:**
- Advanced validation strategies
- Multimodal capabilities
- Corpus analysis
- Text chunking for large documents
- Cost tracking
- Export/import features

**Examples:**
- Image analysis with vision models
- Schema validation
- Corpus directory analysis
- Document summarization
- Conversation export/import

### EDGE - Edge Cases and Resilience Tests
Tests for unusual scenarios, error conditions, and system limits.

**Criteria:**
- Error handling scenarios
- Rate limiting behavior
- Malformed inputs
- Security/injection tests
- Performance under load
- Failure recovery

**Examples:**
- Prompt injection attempts
- Invalid API keys
- Network timeouts
- Circular reasoning detection
- Memory exhaustion handling

## Test Execution Strategy

### Phase 1: Critical Tests Only (Smoke Test)
Run time: ~5 minutes
- Verify all providers respond
- Check basic validation works
- Ensure API is healthy
- Confirm Redis caching

### Phase 2: Critical + Moderate (Standard Test)
Run time: ~20 minutes
- All Phase 1 tests
- Multimodal functionality
- Advanced features
- Integration scenarios

### Phase 3: Full Test Suite (Comprehensive)
Run time: ~60 minutes
- All tests including edge cases
- Performance benchmarks
- Security validation
- Failure mode testing

## Priority by Feature Area

### Multi-Provider Support
- **CRITICAL**: Basic calls to each provider
- MODERATE: Provider-specific features
- EDGE: Provider failover scenarios

### Validation Framework
- **CRITICAL**: JSON, Python syntax validation
- MODERATE: Schema, regex, length validation
- EDGE: Complex validation chains, AI-based validation

### Conversation Management
- **CRITICAL**: Create/continue conversations
- MODERATE: Multi-model conversations
- EDGE: Export/import, merge conversations

### Docker/Deployment
- **CRITICAL**: Container startup, health checks
- MODERATE: Multi-container coordination
- EDGE: Resource limits, security constraints

### Caching
- **CRITICAL**: Basic Redis caching with --cache
- MODERATE: Cache TTL behavior
- EDGE: Cache fallback scenarios

### Agent Collaboration
- **CRITICAL**: Basic model-to-model delegation
- MODERATE: Tool augmentation workflows
- EDGE: Infinite loop prevention, failure recovery