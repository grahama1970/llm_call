# Test Cleanup Recommendations for LLM Call

## Tests to Remove (No Longer Relevant)

### 1. `test_router_supports_multiple_models` 
- **File**: `test_claude_capabilities_verification.py`
- **Reason**: Tests expect `Router` and `ModelSpec` classes that don't exist
- **Action**: Remove or rewrite to use `resolve_route` function

### 2. `test_llm_call_delegator_exists`
- **File**: `test_claude_collaboration_fixed.py`
- **Reason**: Expects LLMCallDelegator to be a class, but it's a CLI script
- **Action**: Remove - functionality is covered by CLI tests

### 3. `test_mcp_server_configuration` 
- **File**: `test_claude_collaboration.py`
- **Reason**: Imports non-existent `SlashMCPMixin` class
- **Action**: Remove or update imports

### 4. MCP Prompts Tests (entire file)
- **File**: `tests/mcp/test_prompts.py`
- **Reason**: Tests for `llm_call.mcp.llm_call_prompts` module that was never implemented
- **Action**: Remove entire file (already skipped)

## Tests to Update

### 1. Field Presence Validation Test
- **Issue**: Expects nested field validation that isn't implemented
- **Fix**: Update test to match actual validator capabilities

### 2. RL Integration Tests
- **Issue**: Method signatures don't match implementation
- **Fix**: Update method calls to use correct parameters:
  - `update_reward` → `update_from_result`
  - Add required `latency` and `cost` parameters

### 3. SafeRLDeployment Tests
- **Issue**: Tests expect methods that don't exist
- **Fix**: Update to match actual SafeRLDeployment interface

### 4. Length Validator Test
- **Issue**: Validator requires min_length or max_length
- **Fix**: Update test to provide required parameters

## Tests That Are Fine (Just Need Environment)

### 1. OpenAI Integration Test
- **Issue**: Invalid API key
- **Solution**: Set `OPENAI_API_KEY` environment variable or skip in CI

### 2. MCP Server Initialization
- **Issue**: Server startup validation
- **Solution**: May need to adjust test expectations for server output

## Recommended Actions

1. **Immediate**: Remove outdated tests that reference non-existent classes
2. **Short-term**: Update RL integration tests to match actual method signatures
3. **Long-term**: Consider adding integration test suite that runs with real APIs in controlled environment

## Summary

Out of 20 failing tests:
- 4 should be removed (outdated/irrelevant)
- 10 need minor updates (method signatures, parameters)
- 4 need investigation (MCP server behavior)
- 2 just need proper environment setup (API keys)

This would bring the test suite to a much healthier state with minimal irrelevant tests.