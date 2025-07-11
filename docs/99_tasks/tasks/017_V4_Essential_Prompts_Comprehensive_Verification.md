# Task 017: V4 Essential Prompts Comprehensive Verification ⏳ Not Started

**Objective**: Systematically verify that all 8 essential test prompts in `/src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json` return expected results with the new async polling implementation.

**Requirements**:
1. All 8 test cases must pass without timeouts
2. Long-running Claude proxy calls must use automatic polling
3. Each test must produce verifiable output matching expectations
4. Performance must meet specified targets (no >30s timeouts)
5. All validation strategies must be properly tested

## Overview

The V4 POC implementation has been enhanced with async polling to handle long-running Claude agent calls. This task ensures all essential test prompts work correctly with the new async infrastructure, addressing the timeout issues identified by Claude Code.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 10 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

Initial research indicates:
- Claude proxy calls take 7-15 seconds, causing test timeouts
- Async polling solution uses ~50KB per task vs ~2MB per thread
- Python's asyncio.create_task() provides true concurrency
- Test framework needs both unit tests and CLI verification

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Async testing best practices in Python 2025
   - LiteLLM timeout handling patterns
   - Claude API polling implementation strategies
   - JSON validation testing approaches

2. **Use `WebSearch`** to find:
   - GitHub repos with async LLM client implementations
   - Production examples of polling managers
   - Test suites for LLM proxy services
   - Performance benchmarking for async Python

3. **Document all findings** in task reports:
   - Links to working async implementations
   - Performance characteristics discovered
   - Error handling patterns from production code
   - Integration test examples

4. **DO NOT proceed without research**:
   - Must understand async/await patterns
   - Must find real polling implementations
   - Must verify timeout handling approaches
   - Must locate validation testing examples

Example Research Queries:
```
perplexity_ask: "async LLM client polling implementation Python 2025"
WebSearch: "site:github.com litellm async timeout polling"
WebSearch: "site:github.com claude proxy async client implementation"
perplexity_ask: "testing async Python code with timeouts best practices"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 0: Read CLAUDE.md and Setup Environment ✅ COMPLETE

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Documentation Links**:
- Claude Code Overview: https://docs.anthropic.com/en/docs/claude-code/overview
- Claude Code Best Practices: https://docs.anthropic.com/en/docs/claude-code/best-practices
- Internal Standards: /home/graham/workspace/experiments/llm_call/CLAUDE.md

**Implementation Steps**:
- [ ] 0.1 Read and understand CLAUDE.md
  - Study all coding standards
  - Understand project structure requirements
  - Note validation requirements
  - Review async code guidelines
  - Understand documentation standards

- [ ] 0.2 Setup test environment
  - SSH to graham@192.168.86.49
  - Navigate to /home/graham/workspace/experiments/llm_call/
  - Read .env file for environment variables
  - Activate .venv virtual environment
  - Verify Python version and dependencies

- [ ] 0.3 Verify async implementation files
  - Check `async_polling_manager.py` exists
  - Check `litellm_client_poc_async.py` exists
  - Check `test_v4_essential_async.py` exists
  - Verify all imports work correctly
  - Test basic async functionality

### Task 1: Verify max_text_001_simple_question ❌ BLOCKED - Critical fixes needed

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Documentation Links**:
- LiteLLM Basic Usage: https://docs.litellm.ai/docs/
- LiteLLM Completion: https://docs.litellm.ai/docs/completion/input
- Async Testing Guide: https://docs.litellm.ai/docs/completion/async
- Test Prompts Validation: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- Relevant Code: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/main.py

**Test Case Details**:
- Model: max/text-general
- Input: "What is the primary function of a CPU in a computer?"
- Expected: Brief explanation about CPU functions
- Validation: response_not_empty, field_present(content)

**Research Requirements**:
- [ ] Use `perplexity_ask` to find Claude proxy testing patterns
- [ ] Use `WebSearch` for async test implementation examples
- [ ] Find timeout handling for simple LLM calls
- [ ] Research response validation strategies

**Implementation Steps**:
- [ ] 1.1 Create test execution script
  - Import test_v4_essential_async module
  - Create test runner for this specific case
  - Add performance timing
  - Include error handling
  - Add logging for debugging

- [ ] 1.2 Execute test with timing
  - Run the test case
  - Measure response time
  - Verify no timeout occurs
  - Check response structure
  - Validate content field exists

- [ ] 1.3 Verify validation strategies
  - Test response_not_empty validation
  - Test field_present validation
  - Document actual response content
  - Compare against expectations
  - Note any discrepancies

- [ ] 1.4 Create verification report
  - Create `/docs/reports/017_task_1_simple_question.md`
  - Include actual command output
  - Document response time
  - Show response content
  - Add validation results

**CLI Testing Requirements**:
- [ ] Execute via command line
  - Run: `python test_v4_essential_async.py -k max_text_001`
  - Capture full output
  - Document any errors
  - Verify async polling if needed

**Acceptance Criteria**:
- Response received within 30 seconds
- Content field present in response
- Response contains CPU explanation
- No timeout errors
- All validations pass

### Task 2: Verify max_text_002_messages_format ⏳ Not Started

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Documentation Links**:
- LiteLLM Messages Format: https://docs.litellm.ai/docs/completion/input#messages
- OpenAI Messages Format: https://docs.litellm.ai/docs/providers/openai#openai-chat-completion
- Test Format Examples: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- Message Conversion Code: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/utils.py

**Test Case Details**:
- Model: max/text-general
- Input: Messages format with user role
- Content: "Explain the concept of recursion in programming."
- Expected: Explanation of recursion
- Validation: response_not_empty

**Research Requirements**:
- [ ] Research messages format vs question format
- [ ] Find LiteLLM messages handling examples
- [ ] Search for format conversion patterns
- [ ] Understand role-based messaging

**Implementation Steps**:
- [ ] 2.1 Test messages format handling
- [ ] 2.2 Execute with timing measurement
- [ ] 2.3 Verify response structure
- [ ] 2.4 Create verification report
- [ ] 2.5 Document any format issues

### Task 3: Verify max_text_003_with_system ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Documentation Links**:
- LiteLLM System Messages: https://docs.litellm.ai/docs/completion/input#messages
- Claude System Prompts: https://docs.anthropic.com/en/docs/claude-code/system-prompts
- Multi-Message Handling: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/llms/anthropic.py
- Internal Validation Guide: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md

**Test Case Details**:
- Model: max/text-general
- System message: "You are a helpful assistant that explains concepts clearly and concisely."
- User message: "What is machine learning?"
- Expected: Clear, concise ML explanation
- Validation: response_not_empty, field_present(content)

**Research Requirements**:
- [ ] Research system message handling in Claude
- [ ] Find system prompt best practices
- [ ] Search for multi-message examples
- [ ] Understand message ordering

**Implementation Steps**:
- [ ] 3.1 Test system message integration
- [ ] 3.2 Verify message ordering
- [ ] 3.3 Check response adheres to system prompt
- [ ] 3.4 Measure performance impact
- [ ] 3.5 Create detailed report

### Task 4: Verify max_code_001_simple_code ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Documentation Links**:
- Claude Code Agent Tasks: https://docs.anthropic.com/en/docs/claude-code/agent-tasks
- LiteLLM Response Validation: https://docs.litellm.ai/docs/completion/reliable_completions
- Code Generation Patterns: https://docs.litellm.ai/docs/completion/function_call
- Agent Validation Implementation: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- Validation Code: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/integrations/

**Test Case Details**:
- Model: max/code-expert
- Question: "Write a Python function to calculate the factorial of a number."
- Expected: Python code for factorial
- Validation: response_not_empty, agent_task validation

**Research Requirements**:
- [ ] Research code generation validation
- [ ] Find agent task validation patterns
- [ ] Search for code quality checking
- [ ] Understand JSON validation responses

**Implementation Steps**:
- [ ] 4.1 Test code generation
- [ ] 4.2 Execute agent validation task
- [ ] 4.3 Verify JSON validation response
- [ ] 4.4 Check code quality
- [ ] 4.5 Document validation process

### Task 5: Verify max_mcp_001_file_operations ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: HIGH | **Impact**: CRITICAL

**Documentation Links**:
- Claude MCP Integration: https://docs.anthropic.com/en/docs/claude-code/mcp
- LiteLLM Tools Support: https://docs.litellm.ai/docs/completion/function_call
- MCP Server Config: https://docs.anthropic.com/en/docs/claude-code/mcp-servers
- File Operations Guide: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- Retry Implementation: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/router.py

**Test Case Details**:
- Model: max/claude-mcp-agent
- Task: Create and read file via MCP
- MCP Config: filesystem server at /tmp
- Expected: File creation and verification
- Validation: response_not_empty, agent_task
- Retry config: 2 attempts before tool use, 4 before human

**Research Requirements**:
- [ ] Research MCP filesystem integration
- [ ] Find MCP server setup examples
- [ ] Search for file operation validation
- [ ] Understand retry mechanisms

**Implementation Steps**:
- [ ] 5.1 Verify MCP server configuration
- [ ] 5.2 Test file creation
- [ ] 5.3 Test file reading
- [ ] 5.4 Verify retry mechanism
- [ ] 5.5 Test async polling for long operations
- [ ] 5.6 Create comprehensive report

### Task 6: Verify max_json_001_structured_output ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Documentation Links**:
- LiteLLM JSON Mode: https://docs.litellm.ai/docs/completion/json_mode
- Response Format Enforcement: https://docs.litellm.ai/docs/completion/response_format
- JSON Validation Patterns: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- JSON Parsing Code: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/utils.py

**Test Case Details**:
- Model: max/json-expert
- Task: Generate JSON with name, age, city
- Expected: Valid JSON object
- Validation: json_string, field_present (name, age, city)

**Research Requirements**:
- [ ] Research JSON generation validation
- [ ] Find structured output examples
- [ ] Search for JSON schema validation
- [ ] Understand field validation patterns

**Implementation Steps**:
- [ ] 6.1 Test JSON generation
- [ ] 6.2 Validate JSON structure
- [ ] 6.3 Check all required fields
- [ ] 6.4 Test edge cases
- [ ] 6.5 Document JSON output

### Task 7: Verify litellm_001_openai_compatible ✅ COMPLETE

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: MEDIUM

**Documentation Links**:
- LiteLLM OpenAI Compatibility: https://docs.litellm.ai/docs/providers/openai
- OpenAI Provider Setup: https://docs.litellm.ai/docs/providers/openai#api-keys
- Model Routing: https://docs.litellm.ai/docs/routing
- OpenAI Implementation: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/llms/openai.py

**Test Case Details**:
- Model: gpt-3.5-turbo
- Question: "What is 2 + 2?"
- Expected: "4" or equivalent
- Validation: response_not_empty

**Research Requirements**:
- [ ] Research LiteLLM OpenAI compatibility
- [ ] Find standard LiteLLM examples
- [ ] Understand model routing
- [ ] Check timeout differences

**Implementation Steps**:
- [ ] 7.1 Test OpenAI-compatible call
- [ ] 7.2 Verify quick response (no polling)
- [ ] 7.3 Check response format
- [ ] 7.4 Compare with Claude calls
- [ ] 7.5 Document differences

### Task 8: Verify validation_retry_001 ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: HIGH | **Impact**: CRITICAL

**Documentation Links**:
- LiteLLM Retry Logic: https://docs.litellm.ai/docs/completion/reliable_completions
- Fallback Strategies: https://docs.litellm.ai/docs/routing#fallbacks
- Validation Retry Patterns: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- Retry Implementation: /home/graham/workspace/experiments/llm_call/repos/litellm/litellm/router.py

**Test Case Details**:
- Model: max/text-general
- Task: Generate exactly 3 random words
- Validation: agent_task counting words
- Retry config: 3 attempts before tool, 5 before human

**Research Requirements**:
- [ ] Research retry mechanism implementation
- [ ] Find validation failure handling
- [ ] Search for iterative improvement patterns
- [ ] Understand retry escalation

**Implementation Steps**:
- [ ] 8.1 Test initial generation
- [ ] 8.2 Test validation failure handling
- [ ] 8.3 Verify retry attempts
- [ ] 8.4 Check retry escalation
- [ ] 8.5 Document retry behavior

### Task 9: Performance and Integration Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Documentation Links**:
- LiteLLM Performance: https://docs.litellm.ai/docs/observability/
- Load Testing Guide: https://docs.litellm.ai/docs/load_test
- Async Performance: https://docs.litellm.ai/docs/completion/async
- Benchmark Examples: /home/graham/workspace/experiments/llm_call/repos/litellm/tests/

**Implementation Steps**:
- [ ] 9.1 Run all tests sequentially
  - Measure total execution time
  - Check for memory leaks
  - Monitor async task creation
  - Verify no hanging processes

- [ ] 9.2 Run tests concurrently
  - Test parallel execution
  - Check resource usage
  - Verify no race conditions
  - Monitor polling manager

- [ ] 9.3 Stress test polling manager
  - Simulate multiple long calls
  - Check task cleanup
  - Verify memory efficiency
  - Test error recovery

- [ ] 9.4 Create performance report
  - Document all metrics
  - Compare with thread-based approach
  - Show resource improvements
  - Include graphs if helpful

### Task 10: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Documentation Links**:
- Claude Code Testing: https://docs.anthropic.com/en/docs/claude-code/testing
- LiteLLM Testing: https://docs.litellm.ai/docs/testing
- Comprehensive Validation: /home/graham/workspace/experiments/llm_call/docs/004_Tasks_Test_Prompts_Validation.md
- Test Suite Examples: /home/graham/workspace/experiments/llm_call/repos/litellm/tests/

**Implementation Steps**:
- [ ] 10.1 Review all task reports
  - Read all reports in `/docs/reports/017_task_*`
  - Create checklist of incomplete tests
  - Identify failed validations
  - Document specific issues
  - Prioritize fixes by impact

- [ ] 10.2 Create test completion matrix
  - Build comprehensive status table
  - Mark each test as PASS/FAIL
  - List specific failures
  - Calculate pass percentage
  - Identify patterns in failures

- [ ] 10.3 Iterate on failed tests
  - Return to first failed test
  - Debug specific issues
  - Fix and re-run
  - Update verification report
  - Continue until test passes

- [ ] 10.4 Re-validate all tests
  - Run complete test suite
  - Ensure no regressions
  - Verify all async features work
  - Check performance targets met
  - Document final results

- [ ] 10.5 Create final summary report
  - Create `/docs/reports/017_final_summary.md`
  - Include test results matrix
  - Document all timings
  - List any remaining issues
  - Provide recommendations

**Test Results Matrix Template**:
| Test Case | Description | Execution Time | Polling Used | Validation | Status |
|-----------|-------------|----------------|--------------|------------|--------|
| max_text_001 | Simple question | X.Xs | No | ✅ PASS | ✅ PASS |
| max_text_002 | Messages format | X.Xs | No | ✅ PASS | ✅ PASS |
| max_text_003 | With system | X.Xs | No | ✅ PASS | ✅ PASS |
| max_code_001 | Code generation | X.Xs | Yes | ✅ PASS | ✅ PASS |
| max_mcp_001 | File operations | X.Xs | Yes | ✅ PASS | ✅ PASS |
| max_json_001 | JSON output | X.Xs | No | ✅ PASS | ✅ PASS |
| litellm_001 | OpenAI compatible | X.Xs | No | ✅ PASS | ✅ PASS |
| validation_retry_001 | Retry mechanism | X.Xs | Yes | ✅ PASS | ✅ PASS |

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL 8 test cases pass with:
- No timeout errors
- All validations successful
- Performance within targets
- Proper async polling for long calls
- Complete documentation

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| `python test_v4_essential_async.py` | Run all essential tests | `python test_v4_essential_async.py` | All 8 tests pass |
| `python test_v4_essential_async.py -k max_text` | Run specific test pattern | `python test_v4_essential_async.py -k max_text_001` | Single test result |
| `AsyncPollingManager` | Manage async polling | `manager.submit_task(request)` | Task ID returned |
| Test Matrix | Verify all tests pass | Review final report | 100% pass rate required |

## Version Control Plan

- **Initial Tag**: Create task-017-start before beginning
- **Test Commits**: After each test verification
- **Fix Commits**: After resolving any issues
- **Final Tag**: Create task-017-complete after 100% pass

## Resources

**Python Packages**:
- litellm: LLM client library
- asyncio: Async/await support
- pytest: Test framework
- pytest-asyncio: Async test support

**Documentation**:
- [LiteLLM Async Docs](https://docs.litellm.ai/docs/completion/async)
- [Python asyncio Guide](https://docs.python.org/3/library/asyncio.html)
- [Pytest Async Testing](https://pytest-asyncio.readthedocs.io/)

**Internal Documentation**:
- `/docs/ASYNC_IMPROVEMENTS.md`
- `/docs/V4_COMPLETION_ACTION_PLAN.md`
- `/docs/POLLING_SOLUTION.md`

## Progress Tracking

- Start date: TBD
- Current phase: Not Started
- Expected completion: All tests passing
- Completion criteria: 100% test pass rate, no timeouts

## Report Documentation Requirements

Each sub-task MUST have a verification report in `/docs/reports/` with:

### MANDATORY Test Results Table Format

| Test | Description | Code Link | Input | Expected Output | Actual Output | Status |
|------|-------------|-----------|-------|-----------------|---------------|--------|

**Requirements**:
1. **NO HALLUCINATED OUTPUTS**: Actual output from real execution
2. **Include execution times**: Add timing for each test
3. **Show polling status**: Indicate if async polling was used
4. **Real error messages**: Include actual errors if any
5. **Complete commands**: Show exact commands executed

### Report Naming Convention:
`/docs/reports/017_task_[N]_[test_name].md`

---

This task document serves as the comprehensive verification guide for all V4 essential prompts. Update status emojis and checkboxes as tasks are completed.