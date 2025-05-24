# V4 Completion Action Plan

## Immediate Actions (Today)

### 1. Test the Async Implementation
Run the async test suite to verify all essential cases work:

    cd /home/graham/workspace/experiments/claude_max_proxy/
    source .venv/bin/activate
    python test_v4_essential_async.py

Expected: All 8 test cases should pass without timeouts.

### 2. Fix Any Test Failures

#### Agent Validation Issues
If agent validation fails, check:
- {CODE_TO_VALIDATE} placeholder is properly replaced
- Validation prompts are correctly formatted
- Success criteria matches expected format

#### MCP File Operations
If MCP tests fail:
- Ensure /tmp directory is writable
- Check npx and @modelcontextprotocol/server-filesystem are available
- Verify .mcp.json configuration

### 3. Integration Checkpoints

#### Check 1: Direct Calls Work
    python -c "import asyncio; from src.llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc import llm_call; print(asyncio.run(llm_call({'model': 'gpt-3.5-turbo', 'messages': [{'role': 'user', 'content': 'Say test'}]})))"

#### Check 2: Async Polling Works
    python -c "import asyncio; from src.llm_call.proof_of_concept.async_polling_manager import AsyncPollingManager; print('Async polling ready')"

#### Check 3: Claude Proxy Works
Test with actual Claude proxy (if running on port 3010):
    python -c "import asyncio; from src.llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import llm_call; print(asyncio.run(llm_call({'model': 'max/text-general', 'messages': [{'role': 'user', 'content': 'Hello'}]})))"

## Core Integration Steps

### Step 1: Update Core Retry Manager
Location: src/llm_call/core/retry.py

Add async polling support:
1. Import AsyncPollingManager
2. Add is_long_running_call() detection
3. Implement async execution path
4. Add progress callbacks

### Step 2: Update Validation Framework
Location: src/llm_call/core/validation/

Ensure all validators:
1. Support async execution
2. Can report progress
3. Handle long-running operations

### Step 3: Update Router
Location: src/llm_call/core/router.py

Add routing hints for:
1. Long-running models
2. Polling preferences
3. Timeout configurations

## Testing Plan

### Unit Tests
1. Test async polling manager independently
2. Test timeout handling
3. Test concurrent task execution
4. Test task cancellation

### Integration Tests
1. Test v4 client with all validation strategies
2. Test retry logic with polling
3. Test MCP operations
4. Test error handling

### Performance Tests
1. Measure latency improvement
2. Test concurrent request handling
3. Verify resource usage
4. Test scalability limits

## Documentation Updates

### 1. Update README.md
Add sections for:
- Async polling usage
- Timeout handling
- Long-running operations

### 2. Update CHANGELOG.md
Document:
- Async improvements
- Breaking changes (if any)
- Migration notes

### 3. Create Migration Guide
docs/MIGRATION_V3_TO_V4.md:
- API differences
- Configuration changes
- Best practices

## Success Criteria

1. All 8 essential test cases pass
2. No timeout errors during testing
3. Claude proxy calls complete successfully
4. MCP operations work as expected
5. Validation strategies function correctly
6. Retry logic handles all edge cases
7. Documentation is complete

## Timeline

- **Day 1** (Today): Complete async implementation and testing
- **Day 2**: Core integration and unit tests
- **Day 3**: Integration tests and documentation
- **Day 4**: Performance testing and optimization
- **Day 5**: Final review and release preparation

## Notes

- The async approach solves the fundamental timeout issue
- All v4 functionality is preserved
- The solution scales better than the thread-based approach
- Backward compatibility is maintained

## Commands Reference

### Run specific test
    python -m pytest tests/llm_call/proof_of_concept/test_v4_async.py -v

### Check proxy health
    curl http://localhost:3010/health

### Monitor active tasks
    python -c "import asyncio; from src.llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc_async import list_active_tasks; print(asyncio.run(list_active_tasks()))"

### Clean up database
    rm llm_polling_tasks.db

This action plan provides a clear path to completing the v4 integration with the async improvements.
