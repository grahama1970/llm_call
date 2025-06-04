# Task 019: Remove All Test Mocking

## Status: IN PROGRESS

## Objective
Replace all mocking in test files with real implementations, as per CLAUDE.md requirement: "MagicMock is strictly forbidden for testing core functionality."

## Files Requiring Updates

### 1. `/tests/llm_call/cli/test_llm_integration.py`
**Current Mocking:**
- Router (`determine_llm_route_and_params`)
- LiteLLM completion calls
- Claude CLI executor
- Ollama requests

**Replacement Strategy:**
- Use real router with test configurations
- Make actual LLM calls to test models (e.g., ollama/tinyllama)
- Use real validation strategies from the registry
- Test with actual HTTP endpoints

### 2. `/tests/llm_call/cli/test_mcp_features.py`
**Current Mocking:**
- MCP server interactions
- Tool execution results

**Replacement Strategy:**
- Start a real MCP test server
- Execute real tools with test data
- Validate actual MCP protocol responses

### 3. `/tests/llm_call/cli/test_cli_comprehensive.py`
**Current Mocking:**
- `make_llm_request` function
- CLI command handlers

**Replacement Strategy:**
- Use CliRunner with real command execution
- Make actual LLM requests with small, fast models
- Test with real file I/O operations

### 4. `/tests/llm_call/core/test_retry_exponential.py`
**Current Mocking:**
- Async LLM call functions
- Time/sleep functions

**Replacement Strategy:**
- Create a test endpoint that fails predictably
- Use real delays (with shorter times for testing)
- Test with actual retry scenarios

### 5. `/tests/llm_call/core/test_router.py`
**Current Mocking:**
- Minimal mocking, mostly real

**Replacement Strategy:**
- Remove any remaining patches
- Use real configuration loading
- Test with actual model routing

### 6. `/tests/llm_call/core/validation/test_ai_validator_realistic.py`
**Current Mocking:**
- Remove unused mock imports

**Replacement Strategy:**
- Already uses real validators, just clean up imports

### 7. `/tests/llm_call/core/test_core_integration.py`
**Current Mocking:**
- Various integration points

**Replacement Strategy:**
- Use real end-to-end integration tests
- Set up test environment with real services

## Implementation Plan

### Phase 1: Set Up Test Infrastructure
1. Create test configuration with fast, local models
2. Set up test MCP server
3. Create test data fixtures
4. Configure test environment variables

### Phase 2: Replace Mocking (File by File)
1. Start with simpler files (test_router.py, test_ai_validator_realistic.py)
2. Move to CLI tests (test_cli_comprehensive.py)
3. Handle complex integration tests (test_llm_integration.py)
4. Update retry and MCP tests

### Phase 3: Validation
1. Run all tests with real implementations
2. Ensure no performance degradation
3. Verify test coverage remains high
4. Generate test report

## Test Environment Requirements

### Local Models for Testing
```bash
# Install ollama for local testing
curl -fsSL https://ollama.ai/install.sh | sh

# Pull small test models
ollama pull tinyllama
ollama pull all-minilm  # For embeddings
```

### Environment Variables
```bash
# Test configuration
export LLM_TEST_MODEL="ollama/tinyllama"
export LLM_TEST_TIMEOUT=30
export LLM_TEST_MAX_RETRIES=2
```

### Test MCP Server
```python
# Simple test MCP server for testing
from llm_call.mcp_server import create_test_server

test_server = create_test_server(
    tools=["test_tool_1", "test_tool_2"],
    port=8080
)
```

## Success Criteria
- [ ] All 7 files have mocking removed
- [ ] All tests pass with real implementations
- [ ] Test execution time remains reasonable (<5 minutes)
- [ ] No MagicMock, patch, or Mock imports in test files
- [ ] Test coverage maintained at 80%+
- [ ] Generated test report shows all tests passing

## Notes
- Some tests may need to be marked as `@pytest.mark.slow` if they make real API calls
- Consider using `pytest-xdist` for parallel test execution
- May need to create test-specific models or endpoints
- Ensure CI/CD pipeline can handle real service dependencies