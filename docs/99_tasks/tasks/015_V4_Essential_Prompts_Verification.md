# Task 015: V4 Essential Prompts Verification ⏳ Not Started

**Objective**: Ensure all 8 test cases in test_prompts_essential.json return expected results without timeouts using the async polling implementation.

**Requirements**:
1. All 8 test cases must pass with actual LLM responses
2. Claude proxy calls (max/*) must complete without timeouts
3. Validation strategies must correctly validate responses
4. MCP file operations must work as expected
5. Retry mechanisms must function properly
6. All results must be from real executions (no mocking)

## Overview

The v4 POC implementation has been enhanced with async polling to handle long-running Claude agent calls. This task systematically verifies each test case works as expected and documents actual results.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in  with actual command outputs and performance results.
2. Task 9 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

Initial research showed Claude proxy calls take 7-15 seconds, causing timeouts. The async polling solution addresses this by running long operations in background tasks.

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH test case, the agent MUST:

1. **Use ** to research:
   - Best practices for LLM response validation 2025
   - Production patterns for handling slow API calls
   - Agent-based validation techniques
   - MCP server configuration patterns

2. **Use ** to find:
   - GitHub examples of litellm with validation
   - Claude proxy integration patterns
   - Async polling implementations
   - MCP file operation examples

3. **Document all findings** in task reports:
   - Working validation strategies
   - Timeout handling patterns
   - Performance characteristics
   - Integration approaches

4. **DO NOT proceed without research**:
   - Must understand validation patterns
   - Must find timeout solutions
   - Must have real MCP examples
   - Must verify async best practices

Example Research Queries:


## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Basic Claude Proxy Text Calls ⏳ Not Started

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Test Cases Covered**:
- max_text_001_simple_question
- max_text_002_messages_format
- max_text_003_with_system

**Research Requirements**:
- [ ] Use  to find Claude proxy integration patterns
- [ ] Use  to find timeout handling examples
- [ ] Search GitHub for "claude proxy async" patterns
- [ ] Find real-world response validation strategies
- [ ] Locate performance benchmarking approaches

**Implementation Steps**:
- [ ] 1.1 Set up test environment
  - Verify Claude proxy is running on port 3010
  - Test proxy health endpoint
  - Initialize async polling manager
  - Configure logging for debugging
  - Set appropriate timeouts

- [ ] 1.2 Test max_text_001_simple_question
  - Execute test with actual proxy call
  - Measure response time
  - Validate response contains CPU explanation
  - Check response_not_empty validation
  - Verify field_present validation for "content"

- [ ] 1.3 Test max_text_002_messages_format
  - Execute with messages array format
  - Verify recursion explanation returned
  - Check response validation
  - Measure performance
  - Document actual response

- [ ] 1.4 Test max_text_003_with_system
  - Include system message in call
  - Verify concise ML explanation
  - Validate both strategies pass
  - Check response structure
  - Record timing metrics

- [ ] 1.5 Create verification report
  - Create 
  - Include actual responses
  - Add performance metrics
  - Show validation results
  - Document any issues found

**Technical Specifications**:
- Timeout: 30 seconds per call
- Expected response time: 7-15 seconds
- Validation must pass on first attempt
- Content field must be present
- Responses must be non-empty

**Verification Method**:


**CLI Testing Requirements**:
- [ ] Execute test script:  
- [ ] Verify all 3 basic tests pass
- [ ] Check logs for timing information
- [ ] Confirm no timeout errors
- [ ] Document exact commands used

**Acceptance Criteria**:
- All 3 basic text tests pass
- Response times under 30 seconds
- Validation strategies work correctly
- No timeout errors occur
- Actual responses match expected behavior

### Task 2: Code Generation and Agent Validation ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Test Cases Covered**:
- max_code_001_simple_code

**Research Requirements**:
- [ ] Use  for "agent-based code validation patterns 2025"
- [ ] Use  for "recursive LLM validation examples"
- [ ] Find GitHub examples of code validation with LLMs
- [ ] Research placeholder replacement strategies
- [ ] Find success criteria patterns

**Implementation Steps**:
- [ ] 2.1 Fix agent validation prompt
  - Ensure {CODE_TO_VALIDATE} placeholder exists
  - Verify prompt formatting
  - Test placeholder replacement
  - Check success_criteria structure
  - Validate JSON response format

- [ ] 2.2 Test factorial code generation
  - Request Python factorial function
  - Capture generated code
  - Pass to agent validator
  - Verify validation response
  - Check success criteria match

- [ ] 2.3 Debug validation flow
  - Log validation prompt sent
  - Capture agent response
  - Parse JSON validation result
  - Check "VALID" in details
  - Handle validation errors

- [ ] 2.4 Performance optimization
  - Measure total validation time
  - Check for double timeout issues
  - Optimize prompt length
  - Test concurrent validations
  - Document bottlenecks

- [ ] 2.5 Create verification report
  - Create 
  - Include generated code samples
  - Show validation prompts
  - Document agent responses
  - Add performance metrics

**Technical Specifications**:
- Primary call timeout: 30 seconds
- Validation call timeout: 30 seconds
- Total time budget: 60 seconds
- Must handle recursive LLM calls
- JSON response required from validator

**Verification Method**:


**Acceptance Criteria**:
- Code generation works correctly
- Agent validation completes
- Success criteria properly evaluated
- No recursive timeout issues
- Validation results are accurate

### Task 3: MCP File Operations ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Test Cases Covered**:
- max_mcp_001_file_operations

**Research Requirements**:
- [ ] Use  for "MCP modelcontextprotocol server setup 2025"
- [ ] Use  for "npx @modelcontextprotocol/server-filesystem examples"
- [ ] Find GitHub MCP integration examples
- [ ] Research file operation validation
- [ ] Find MCP configuration patterns

**Implementation Steps**:
- [ ] 3.1 Set up MCP server
  - Install @modelcontextprotocol/server-filesystem
  - Configure filesystem access to /tmp
  - Create .mcp.json configuration
  - Test MCP server startup
  - Verify permissions

- [ ] 3.2 Test file creation
  - Execute MCP file write command
  - Verify file created in /tmp
  - Check file contents
  - Test file read operation
  - Validate response confirms both operations

- [ ] 3.3 Handle MCP timeouts
  - MCP operations can be slow
  - Use extended timeout (60s)
  - Implement retry logic
  - Check for partial completion
  - Handle server errors

- [ ] 3.4 Validation strategy
  - Check response mentions file creation
  - Verify content confirmation
  - Use agent validator for complex check
  - Ensure "SUCCESS" in validation
  - Handle edge cases

- [ ] 3.5 Create verification report
  - Create 
  - Show MCP configuration
  - Include server logs
  - Document file operations
  - Add timing information

**Technical Specifications**:
- MCP server timeout: 60 seconds
- File operations in /tmp only
- Retry up to 4 times
- Must create and read file
- Agent must confirm success

**Verification Method**:


**Acceptance Criteria**:
- MCP server starts correctly
- File creation succeeds
- File content verified
- Agent confirms operations
- No permission errors

### Task 4: JSON Output Validation ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: MEDIUM

**Test Cases Covered**:
- max_json_001_structured_output

**Research Requirements**:
- [ ] Use  for "JSON schema validation LLM outputs 2025"
- [ ] Use  for "structured output validation patterns"
- [ ] Find multi-field validation examples
- [ ] Research JSON parsing strategies
- [ ] Find field presence validation patterns

**Implementation Steps**:
- [ ] 4.1 Test JSON generation
  - Request specific JSON structure
  - Parse response as JSON
  - Validate against schema
  - Check all required fields
  - Handle malformed JSON

- [ ] 4.2 Multi-validator testing
  - Apply json_string validator
  - Check field_present for "name"
  - Check field_present for "age"
  - Check field_present for "city"
  - Ensure all pass

- [ ] 4.3 Error handling
  - Test with invalid JSON
  - Handle missing fields
  - Check type mismatches
  - Validate error messages
  - Test recovery behavior

- [ ] 4.4 Performance testing
  - Measure JSON parsing time
  - Check validation overhead
  - Test with large JSON
  - Optimize validators
  - Document performance

- [ ] 4.5 Create verification report
  - Create 
  - Show generated JSON examples
  - Include validation results
  - Document field checks
  - Add performance data

**Technical Specifications**:
- JSON must be valid
- All 3 fields required
- Correct data types
- Validation < 100ms
- No parsing errors

**Verification Method**:


**Acceptance Criteria**:
- Valid JSON generated
- All fields present
- Correct values returned
- All validators pass
- No parsing errors

### Task 5: LiteLLM OpenAI Compatibility ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: MEDIUM

**Test Cases Covered**:
- litellm_001_openai_compatible

**Research Requirements**:
- [ ] Use  for "LiteLLM OpenAI compatibility 2025"
- [ ] Use  for "gpt-3.5-turbo response patterns"
- [ ] Find quick response examples
- [ ] Research response validation
- [ ] Find performance benchmarks

**Implementation Steps**:
- [ ] 5.1 Test basic math question
  - Send "What is 2 + 2?"
  - Verify response contains "4"
  - Check response time < 2s
  - Validate response structure
  - Test response_not_empty

- [ ] 5.2 Compare with direct OpenAI
  - Test same prompt via OpenAI
  - Compare response format
  - Check compatibility
  - Verify no modifications
  - Document differences

- [ ] 5.3 Cache verification
  - Make same call twice
  - Check cache hit
  - Verify faster response
  - Test cache invalidation
  - Document cache behavior

- [ ] 5.4 Error scenarios
  - Test with invalid model
  - Check rate limit handling
  - Test network errors
  - Verify error format
  - Document error patterns

- [ ] 5.5 Create verification report
  - Create 
  - Show response examples
  - Include timing data
  - Document cache behavior
  - Add compatibility notes

**Technical Specifications**:
- Response time < 2 seconds
- Must mention "4" or "four"
- OpenAI compatible format
- Cache should work
- No modifications to response

**Verification Method**:


**Acceptance Criteria**:
- Response contains correct answer
- Fast response time
- Cache functioning
- OpenAI compatibility maintained
- Validation passes

### Task 6: Retry Mechanism Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Test Cases Covered**:
- validation_retry_001

**Research Requirements**:
- [ ] Use  for "LLM retry strategies validation 2025"
- [ ] Use  for "exponential backoff patterns"
- [ ] Find retry with feedback examples
- [ ] Research validation failure handling
- [ ] Find retry configuration patterns

**Implementation Steps**:
- [ ] 6.1 Test word count validation
  - Request exactly 3 words
  - Count words in response
  - Trigger retry if not 3
  - Verify retry feedback
  - Check retry attempts

- [ ] 6.2 Retry flow testing
  - Log all retry attempts
  - Verify exponential backoff
  - Check feedback messages
  - Test max attempts
  - Document retry behavior

- [ ] 6.3 Tool suggestion phase
  - After 3 attempts test tool suggestion
  - Verify MCP config injection
  - Check tool availability
  - Test tool usage
  - Document tool behavior

- [ ] 6.4 Human escalation
  - After 5 attempts test escalation
  - Verify error structure
  - Check last response included
  - Test validation errors list
  - Document escalation format

- [ ] 6.5 Create verification report
  - Create 
  - Show retry sequence
  - Include timing between retries
  - Document feedback evolution
  - Add success/failure cases

**Technical Specifications**:
- Max 3 attempts before tools
- Max 5 attempts before human
- Exponential backoff delays
- Feedback must improve
- Must eventually succeed or escalate

**Verification Method**:


**Acceptance Criteria**:
- Retry logic triggers correctly
- Feedback helps convergence
- Tool suggestion works
- Human escalation works
- No infinite loops

### Task 7: Async Polling Integration ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use  for "async polling patterns Python 2025"
- [ ] Use  for "asyncio task management examples"
- [ ] Find SQLite async patterns
- [ ] Research task cancellation
- [ ] Find progress tracking examples

**Implementation Steps**:
- [ ] 7.1 Test automatic polling detection
  - Verify max/* models use polling
  - Check agent validation uses polling
  - Test MCP operations use polling
  - Verify quick calls don't poll
  - Document detection logic

- [ ] 7.2 Task management testing
  - Submit multiple concurrent tasks
  - Check task status tracking
  - Test task cancellation
  - Verify cleanup
  - Monitor resource usage

- [ ] 7.3 Database persistence
  - Verify tasks persist to SQLite
  - Test recovery after restart
  - Check old task cleanup
  - Verify status updates
  - Test concurrent access

- [ ] 7.4 Performance validation
  - Measure overhead vs direct calls
  - Test with 10 concurrent tasks
  - Check memory usage
  - Verify no thread creation
  - Document scalability

- [ ] 7.5 Create verification report
  - Create 
  - Show task lifecycle
  - Include performance metrics
  - Document resource usage
  - Add scalability analysis

**Technical Specifications**:
- < 1ms task creation
- Support 100+ concurrent tasks
- SQLite for persistence
- Automatic cleanup after 24h
- No thread creation

**Verification Method**:


**Acceptance Criteria**:
- Polling works automatically
- Concurrent execution smooth
- Database operations reliable
- Performance targets met
- No resource leaks

### Task 8: End-to-End Integration Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use  for "end-to-end testing LLM applications 2025"
- [ ] Use  for "integration testing async Python"
- [ ] Find test orchestration patterns
- [ ] Research timing verification
- [ ] Find report generation examples

**Implementation Steps**:
- [ ] 8.1 Run complete test suite
  - Execute test_v4_essential_async.py
  - Run all 8 test cases
  - Monitor execution flow
  - Check no timeouts
  - Verify all pass

- [ ] 8.2 Mixed execution testing
  - Quick tests run directly
  - Long tests use polling
  - Verify correct routing
  - Check performance
  - Document behavior

- [ ] 8.3 Error recovery testing
  - Simulate proxy failures
  - Test network errors
  - Check timeout handling
  - Verify graceful degradation
  - Document recovery

- [ ] 8.4 Performance analysis
  - Total suite execution time
  - Individual test times
  - Resource usage peaks
  - Concurrent execution benefits
  - Create timing chart

- [ ] 8.5 Create verification report
  - Create 
  - Full test results table
  - Timing analysis
  - Resource usage graphs
  - Success/failure summary

**Technical Specifications**:
- All 8 tests must pass
- Total time < 2 minutes
- No timeout errors
- Proper error handling
- Complete logging

**Verification Method**:
       0
       0

**Acceptance Criteria**:
- 100% test pass rate
- No timeout errors
- Performance acceptable
- Logs comprehensive
- Results reproducible

### Task 9: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 9.1 Review all task reports
  - Read all 8 verification reports
  - Create pass/fail checklist
  - Identify any failures
  - Document specific issues
  - Prioritize fixes

- [ ] 9.2 Create task completion matrix
  - Build comprehensive status table
  - List all 8 test cases
  - Show COMPLETE/INCOMPLETE status
  - Include failure reasons
  - Calculate success percentage

- [ ] 9.3 Iterate on incomplete tasks
  - Return to first failure
  - Debug root cause
  - Implement fix
  - Re-run verification
  - Update report

- [ ] 9.4 Re-validate all tests
  - Run complete suite again
  - Ensure no regressions
  - Verify all fixes work
  - Check performance
  - Update all reports

- [ ] 9.5 Final comprehensive validation
  - Execute all tests sequentially
  - Run concurrent test batch
  - Verify database cleanup
  - Check resource usage
  - Confirm production ready

- [ ] 9.6 Create final summary report
  - Create 
  - Include completion matrix
  - Document all test results
  - List any limitations
  - Provide recommendations

- [ ] 9.7 Mark task complete only if ALL tests pass
  - Verify 100% success rate
  - Confirm no timeouts
  - Check all validations work
  - Ensure MCP operations succeed
  - Update task status

**Technical Specifications**:
- Zero tolerance for failures
- All 8 tests must pass
- No partial completion
- Full documentation required
- Production ready state

**Verification Method**:
- Task completion matrix showing 100%
- All test reports showing PASS
- No timeout errors in any test
- All features working correctly

**Acceptance Criteria**:
- ALL tests marked COMPLETE
- ALL validations passing
- ALL timeouts eliminated
- ALL features functional
- NO incomplete items

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL 8 test cases pass with actual LLM responses, proper validation, and no timeout errors. The agent MUST continue iterating until 100% success is achieved.

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
|  | Make LLM call with auto-polling |  | Response or task_id |
|  | Call with timeout fallback |  | Response (polling if needed) |
|  | Check polling task status |  | Task info dict |
|  | Wait for task completion |  | Final result |
|  | Run all essential tests |  | All 8 tests pass |

## Version Control Plan

- **Initial Tag**: Create task-015-start before implementation
- **Test Commits**: After each test case verification
- **Fix Commits**: After resolving any failures
- **Integration Commit**: After full suite passes
- **Final Tag**: Create task-015-complete after 100% success

## Resources

**Python Packages**:
- litellm: LLM abstraction layer
- httpx: Async HTTP client
- loguru: Logging framework
- asyncio: Async programming

**Documentation**:
- [LiteLLM Docs](https://docs.litellm.ai/)
- [AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)
- [MCP Protocol](https://github.com/modelcontextprotocol/servers)
- [Claude Proxy Setup](internal-docs)

**Example Implementations**:
- [Async Polling Examples](https://github.com/search?q=async+polling+python)
- [LLM Validation Patterns](https://github.com/search?q=llm+response+validation)
- [MCP Integration](https://github.com/modelcontextprotocol/servers/tree/main/filesystem)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: 1 day
- Completion criteria: All 8 tests passing, no timeouts, documented

## Report Documentation Requirements

Each sub-task MUST have a corresponding verification report in  following these requirements:

### Report Structure:
1. **Task Summary**: What was tested and results
2. **Research Findings**: Validation patterns and timeout solutions found
3. **Real Command Outputs**: Actual test execution logs
4. **Performance Metrics**: Response times and resource usage
5. **Test Results Table**: MANDATORY comprehensive results (see below)
6. **Validation Evidence**: Actual LLM responses and validation results
7. **Issues Found**: Any problems or limitations discovered
8. **External Resources**: All references used

### Report Naming Convention:


### MANDATORY Test Results Table Format

**CRITICAL REQUIREMENT**: Every report MUST include a comprehensive test results table:

| Test Case | Description | Code Link | Input | Expected Output | Actual Output | Response Time | Status |
|-----------|-------------|-----------|-------|-----------------|---------------|---------------|--------|
| max_text_001 | Simple question | litellm_client_poc.py:125 | CPU function question | CPU explanation | "The CPU processes instructions..." | 12.3s | ✅ PASS |

**Requirements**:
1. **NO HALLUCINATED OUTPUTS**: Actual output MUST be from real execution
2. **Include timing**: Response time column is mandatory
3. **Exact test case IDs**: Use IDs from test_prompts_essential.json
4. **Real responses**: Show actual LLM output (truncated if needed)
5. **All tests documented**: Both passing and failing

---

This task document serves as the comprehensive guide for verifying all v4 essential prompts work correctly with the async polling implementation. Update status emojis and checkboxes as tasks are completed.
