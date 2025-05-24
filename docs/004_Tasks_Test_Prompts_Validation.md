# Task 004: Test Prompts Validation Implementation 🚧 In Progress

**Objective**: Implement and validate all test cases defined in `test_prompts.json` to ensure the v4 Claude validator system handles diverse LLM call scenarios including text, JSON, multimodal, and agent-based validation.

**Requirements**:
1. All 30+ test cases in test_prompts.json must pass validation
2. Support for Claude proxy (max/*) model routing
3. Support for LiteLLM (OpenAI, Vertex AI) model routing
4. JSON response validation with field checking
5. Multimodal image handling (local and HTTP)
6. AI-assisted validation through agent tasks
7. String pattern validation (contains, regex, etc.)
8. Iterative retry with staged escalation
9. MCP configuration support for Claude agents
10. Performance targets: <2s for simple calls, <10s for agent validation

## Overview

The test_prompts.json file contains comprehensive test scenarios covering the full range of capabilities needed for the v4 Claude validator system. This task ensures all validation strategies, routing mechanisms, and integration points work correctly across diverse use cases.

**IMPORTANT**: 
1. Each sub-task MUST include creation of POC scripts in `/src/llm_call/proof_of_concept/code/task_004_test_prompts/`
2. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
3. Task 8 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks until 100% completion is achieved.

## Research Summary

Based on the test_prompts.json analysis:
- 5 basic text call scenarios
- 4 JSON validation scenarios  
- 6 multimodal image scenarios
- 5 agent-based validation scenarios
- 6 string/field validation scenarios
- 4 additional edge cases
- Total: ~30 distinct test cases requiring implementation

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - LiteLLM best practices for model routing
   - Claude CLI integration patterns
   - JSON schema validation techniques
   - Multimodal image handling strategies

2. **Use `WebSearch`** to find:
   - GitHub examples of validation frameworks
   - Production retry/escalation patterns
   - MCP server configuration examples
   - Agent-based validation architectures

3. **Document all findings** in task reports:
   - Working code snippets
   - Performance benchmarks
   - Integration patterns
   - Error handling strategies

4. **DO NOT proceed without research**:
   - Must find real implementation examples
   - Must verify current best practices
   - Must test with actual API calls
   - Must validate against real responses

Example Research Queries:
```
perplexity_ask: "LiteLLM model routing best practices 2025"
WebSearch: "site:github.com validation framework retry escalation pattern"
perplexity_ask: "Claude MCP server configuration examples"
WebSearch: "site:github.com multimodal image validation LLM"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Basic Model Routing Infrastructure ✅ Complete

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [x] POC-1: Test Claude proxy routing with simple text
- [x] POC-2: Test LiteLLM routing (OpenAI/Vertex AI)
- [x] POC-3: Test message format conversion
- [x] POC-4: Test error handling for invalid models
- [x] POC-5: Performance benchmark for routing overhead

**Research Requirements**:
- [x] Use `perplexity_ask` for LiteLLM routing patterns
- [x] Use `WebSearch` for production routing examples
- [x] Find model aliasing best practices
- [x] Research error handling strategies
- [x] Locate performance optimization techniques

**Implementation Steps**:
- [x] 1.0 Create POC scripts (MANDATORY FIRST STEP)
  - Created directory `/src/llm_call/proof_of_concept/code/task_004_test_prompts/`
  - Wrote POC-1: `poc_01_claude_proxy_routing.py` ✅
  - Wrote POC-2: `poc_02_litellm_routing.py` ✅
  - Wrote POC-3: `poc_03_message_conversion.py` ✅
  - Wrote POC-4: `poc_04_routing_errors.py` ✅
  - Wrote POC-5: `poc_05_routing_performance.py` ✅
  - Verified ALL POCs pass ✅

- [x] 1.1 Implement routing logic
  - Update `determine_llm_route_and_params()` function
  - Support max/* model prefixes for Claude proxy
  - Support standard LiteLLM model names
  - Add route validation and error handling
  - Include comprehensive logging

- [x] 1.2 Test basic text scenarios
  - Test cases: max_text_001, max_text_002, max_text_003
  - Test cases: vertex_text_001, openai_text_001
  - Verify message format conversions
  - Confirm routing decisions
  - Measure routing performance

- [x] 1.3 Create verification report
  - Document all test results
  - Include actual API responses
  - Show routing decisions made
  - Performance metrics
  - Any discovered limitations

**Technical Specifications**:
- Routing decision time: <50ms
- Support for 10+ model providers
- Clear error messages for invalid models
- Extensible routing configuration

**Verification Method**:
- All POC scripts pass
- All basic text test cases pass
- Routing performance meets targets
- Error handling works correctly

**Acceptance Criteria**:
- 100% of basic text scenarios pass
- Routing overhead <50ms
- Clear logs showing routing decisions
- No hardcoded model assumptions

### Task 2: JSON Validation Implementation ✅ Complete

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [x] POC-1: JSON parsing and validation
- [x] POC-2: Field presence checking
- [x] POC-3: Nested field validation
- [x] POC-4: JSON schema validation
- [x] POC-5: Error handling for malformed JSON

**Research Requirements**:
- [x] Use `perplexity_ask` for JSON validation best practices
- [x] Use `WebSearch` for schema validation libraries
- [x] Find field checking patterns
- [x] Research performance considerations
- [x] Locate error recovery strategies

**Implementation Steps**:
- [x] 2.0 Create POC scripts
  - Write POC-1: `poc_06_json_parsing.py`
  - Write POC-2: `poc_07_field_presence.py`
  - Write POC-3: `poc_08_nested_fields.py`
  - Write POC-4: `poc_09_schema_validation.py`
  - Write POC-5: `poc_10_json_errors.py`
  - Verify ALL POCs pass

- [x] 2.1 Implement JSON validators
  - Create `PoCJSONValidator` class
  - Create `PoCFieldPresentValidator` class
  - Support nested field paths
  - Add schema validation option
  - Include detailed error messages

- [ ] 2.2 Test JSON scenarios
  - Test cases: openai_json_001, max_json_002
  - Test cases: max_json_003, field_present_001
  - Verify all field checks work
  - Test malformed JSON handling
  - Measure validation performance

- [ ] 2.3 Create verification report
  - Document JSON test results
  - Show actual JSON responses
  - Include validation decisions
  - Performance benchmarks
  - Error handling examples

**Technical Specifications**:
- JSON parsing time: <10ms
- Support nested field paths (e.g., "user.address.city")
- Clear validation error messages
- Schema validation support

**Verification Method**:
- All JSON POCs pass
- All JSON test cases pass
- Performance targets met
- Error messages are helpful

**Acceptance Criteria**:
- 100% of JSON scenarios pass
- Field validation works for nested paths
- Schema validation functional
- Clear error reporting

### Task 3: Multimodal Image Handling ✅ Complete

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: MEDIUM

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [x] POC-1: Image encoding and format support (poc_11)
- [x] POC-2: Size and resolution optimization (poc_12)
- [x] POC-3: Multimodal message formatting (poc_13)
- [x] POC-4: Provider-specific formatting
- [x] POC-5: Format conversion between providers

**Research Requirements**:
- [x] Use `perplexity_ask` for multimodal LLM best practices
- [x] Use `WebSearch` for image handling examples
- [x] Find base64 encoding patterns
- [x] Research supported image formats
- [x] Locate size/resolution limits

**Implementation Steps**:
- [x] 3.0 Create POC scripts
  - Write POC-1: `poc_11_image_encoding.py`
  - Write POC-2: `poc_12_size_optimization.py`
  - Write POC-3: `poc_13_multimodal_messages.py`
  - Provider-specific formatting implemented
  - Format conversion implemented
  - Verify ALL POCs pass

- [x] 3.1 Implement image handling
  - Update message preprocessing
  - Support local file paths
  - Support HTTP URLs
  - Add image validation
  - Include size limits

- [ ] 3.2 Test multimodal scenarios
  - Test cases: openai_multimodal_001, max_multimodal_001
  - Test cases: max_multimodal_002, openai_multimodal_003
  - Test cases: max_multimodal_003
  - Verify both local and HTTP images
  - Test various image formats

- [ ] 3.3 Create test images
  - Create `/test_images_poc/` directory
  - Add dummy_image.png
  - Add six_animals.png
  - Include various formats
  - Document image contents

- [ ] 3.4 Create verification report
  - Document multimodal results
  - Show image handling process
  - Include API responses
  - Performance metrics
  - Size/format limitations

**Technical Specifications**:
- Image loading time: <500ms
- Support PNG, JPEG, GIF, WebP
- Max image size: 20MB
- Automatic format detection

**Verification Method**:
- All image POCs pass
- All multimodal test cases pass
- Various formats supported
- Performance acceptable

**Acceptance Criteria**:
- 100% of multimodal scenarios pass
- Local and HTTP images work
- Format detection automatic
- Clear error messages

### Task 4: Agent-Based Validation System ⏳ Not Started

**Priority**: HIGH | **Complexity**: VERY HIGH | **Impact**: HIGH

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [ ] POC-1: Basic agent task validation
- [ ] POC-2: MCP configuration handling
- [ ] POC-3: Tool delegation testing
- [ ] POC-4: Success criteria evaluation
- [ ] POC-5: Claude proxy integration

**Research Requirements**:
- [ ] Use `perplexity_ask` for agent validation patterns
- [ ] Use `WebSearch` for MCP server examples
- [ ] Find tool delegation strategies
- [ ] Research Claude CLI integration
- [ ] Locate production agent architectures

**Implementation Steps**:
- [ ] 4.0 Create POC scripts
  - Write POC-1: `poc_16_agent_basic.py`
  - Write POC-2: `poc_17_mcp_config.py`
  - Write POC-3: `poc_18_tool_delegation.py`
  - Write POC-4: `poc_19_success_criteria.py`
  - Write POC-5: `poc_20_claude_integration.py`
  - Verify ALL POCs pass

- [ ] 4.1 Implement PoCAgentTaskValidator
  - Create validator class
  - Support task prompt templates
  - Handle MCP configuration
  - Parse agent responses
  - Evaluate success criteria

- [ ] 4.2 Test agent scenarios
  - Test case: agent_validation_001 (contradiction check)
  - Test case: agent_validation_002 (code syntax)
  - Test case: agent_validation_003 (large text)
  - Test case: agent_validation_004 (keyword check)
  - Test case: agent_task_002 (default MCP)

- [ ] 4.3 Configure MCP servers
  - Set up perplexity-ask server
  - Configure llm_call_tool
  - Test python_linter_tool
  - Document server setup
  - Handle environment variables

- [ ] 4.4 Create verification report
  - Document agent validations
  - Show MCP configurations used
  - Include tool outputs
  - Success criteria results
  - Performance metrics

**Technical Specifications**:
- Agent response time: <10s
- Support multiple MCP tools
- Clear success/failure reporting
- Robust JSON response parsing

**Verification Method**:
- All agent POCs pass
- All agent test cases pass
- MCP tools functional
- Success criteria work

**Acceptance Criteria**:
- 100% of agent scenarios pass
- Tool delegation works
- MCP configuration flexible
- Clear validation results

### Task 5: String and Pattern Validation ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: MEDIUM

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [ ] POC-1: String contains validation
- [ ] POC-2: Regex pattern matching
- [ ] POC-3: Length validation
- [ ] POC-4: Corpus keyword checking
- [ ] POC-5: Combined validations

**Research Requirements**:
- [ ] Use `perplexity_ask` for text validation patterns
- [ ] Use `WebSearch` for regex best practices
- [ ] Find efficient string searching
- [ ] Research corpus validation
- [ ] Locate validation frameworks

**Implementation Steps**:
- [ ] 5.0 Create POC scripts
  - Write POC-1: `poc_21_string_contains.py`
  - Write POC-2: `poc_22_regex_match.py`
  - Write POC-3: `poc_23_length_check.py`
  - Write POC-4: `poc_24_corpus_check.py`
  - Write POC-5: `poc_25_combined_string.py`
  - Verify ALL POCs pass

- [ ] 5.1 Implement string validators
  - Create `PoCStringCheckValidator`
  - Support contains/not_contains
  - Add regex matching
  - Include length limits
  - Create corpus validator

- [ ] 5.2 Test string scenarios
  - Test cases: string_check_001 through string_check_004
  - Test case: corpus_check_001
  - Test case: combo_val_004
  - Verify all patterns work
  - Test edge cases

- [ ] 5.3 Create verification report
  - Document string validations
  - Show pattern matches
  - Include performance data
  - Edge case results
  - Validation combinations

**Technical Specifications**:
- String validation: <1ms
- Regex compilation cached
- Unicode support
- Clear match reporting

**Verification Method**:
- All string POCs pass
- All string test cases pass
- Performance optimal
- Edge cases handled

**Acceptance Criteria**:
- 100% of string scenarios pass
- Regex patterns work correctly
- Performance <1ms per check
- Unicode text supported

### Task 6: Retry and Escalation Logic ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: HIGH | **Impact**: HIGH

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [ ] POC-1: Basic retry mechanism
- [ ] POC-2: Exponential backoff
- [ ] POC-3: Tool escalation trigger
- [ ] POC-4: Human escalation flow
- [ ] POC-5: Debug mode integration

**Research Requirements**:
- [ ] Use `perplexity_ask` for retry best practices
- [ ] Use `WebSearch` for escalation patterns
- [ ] Find backoff algorithms
- [ ] Research tool integration
- [ ] Locate human-in-loop examples

**Implementation Steps**:
- [ ] 6.0 Create POC scripts
  - Write POC-1: `poc_26_basic_retry.py`
  - Write POC-2: `poc_27_exponential_backoff.py`
  - Write POC-3: `poc_28_tool_escalation.py`
  - Write POC-4: `poc_29_human_escalation.py`
  - Write POC-5: `poc_30_debug_mode.py`
  - Verify ALL POCs pass

- [ ] 6.1 Enhance retry manager
  - Update `PoCRetryManager`
  - Add staged escalation
  - Support tool triggers
  - Include human escalation
  - Add debug logging

- [ ] 6.2 Test retry scenarios
  - Test case: code_gen_001_staged_retry
  - Test validation failures
  - Test tool escalation
  - Test human escalation
  - Verify debug mode

- [ ] 6.3 Create verification report
  - Document retry behavior
  - Show escalation paths
  - Include timing data
  - Tool usage examples
  - Human escalation cases

**Technical Specifications**:
- Initial retry delay: 1s
- Max retry attempts: 5
- Exponential factor: 2.0
- Clear escalation logs

**Verification Method**:
- All retry POCs pass
- Escalation paths work
- Timing appropriate
- Debug mode helpful

**Acceptance Criteria**:
- Retry logic prevents failures
- Tool escalation automatic
- Human escalation clear
- Debug information useful

### Task 7: Integration Testing Suite ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: CRITICAL

**POC Requirements** (MANDATORY - Complete BEFORE implementation):
- [ ] POC-1: Test runner framework
- [ ] POC-2: Result aggregation
- [ ] POC-3: Performance tracking
- [ ] POC-4: Failure reporting
- [ ] POC-5: Parallel execution

**Research Requirements**:
- [ ] Use `perplexity_ask` for test framework patterns
- [ ] Use `WebSearch` for integration testing
- [ ] Find result reporting tools
- [ ] Research parallel execution
- [ ] Locate CI/CD patterns

**Implementation Steps**:
- [ ] 7.0 Create POC scripts
  - Write POC-1: `poc_31_test_runner.py`
  - Write POC-2: `poc_32_result_aggregation.py`
  - Write POC-3: `poc_33_performance_track.py`
  - Write POC-4: `poc_34_failure_report.py`
  - Write POC-5: `poc_35_parallel_tests.py`
  - Verify ALL POCs pass

- [ ] 7.1 Create test runner
  - Load test_prompts.json
  - Execute each test case
  - Track results
  - Measure performance
  - Generate reports

- [ ] 7.2 Run all test cases
  - Execute all 30+ scenarios
  - Record successes/failures
  - Capture error details
  - Track timing data
  - Identify patterns

- [ ] 7.3 Create master report
  - Summary statistics
  - Individual test results
  - Performance analysis
  - Failure patterns
  - Improvement suggestions

**Technical Specifications**:
- Test execution: <5min total
- Parallel execution: 5 workers
- Detailed error capture
- Markdown report output

**Verification Method**:
- Test runner executes all cases
- Results accurately tracked
- Reports generated correctly
- Performance acceptable

**Acceptance Criteria**:
- All test cases executed
- Clear pass/fail reporting
- Performance data captured
- Actionable failure info

### Task 8: Final Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 8.1 Review all task reports
  - Read all reports in `/docs/reports/004_task_*`
  - Create checklist of incomplete features
  - Identify failed tests or missing functionality
  - Document specific issues preventing completion
  - Prioritize fixes by impact

- [ ] 8.2 Create task completion matrix
  - Build comprehensive status table
  - Mark each sub-task as COMPLETE/INCOMPLETE
  - List specific failures for incomplete tasks
  - Identify blocking dependencies
  - Calculate overall completion percentage

- [ ] 8.3 Review POC results
  - Check all POCs in `/src/llm_call/proof_of_concept/code/task_004_test_prompts/`
  - Verify all POCs still pass
  - Identify any that need updates
  - Document learnings from POCs

- [ ] 8.4 Iterate on incomplete tasks
  - Return to first incomplete task
  - Create new POCs if needed
  - Fix identified issues
  - Re-run validation tests
  - Update verification reports
  - Continue until task passes

- [ ] 8.5 Run complete test suite
  - Execute all 30+ test cases
  - Verify 100% pass rate
  - Check performance targets
  - Validate error handling
  - Confirm all features integrated

- [ ] 8.6 Final comprehensive validation
  - Run performance benchmarks
  - Test error scenarios
  - Verify all integrations
  - Check documentation accuracy
  - Confirm production readiness

- [ ] 8.7 Create final summary report
  - Create `/docs/reports/004_final_summary.md`
  - Include test results matrix
  - Document all working features
  - Performance benchmarks
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 8.8 Mark task complete only if ALL sub-tasks pass
  - Verify 100% task completion
  - Confirm all test cases pass
  - Ensure no critical issues remain
  - Get final approval
  - Update task status to ✅ Complete

**Technical Specifications**:
- Zero tolerance for incomplete features
- All 30+ test cases must pass
- Performance targets must be met
- No known critical bugs

**Verification Method**:
- Task completion matrix showing 100%
- All test cases passing
- Performance benchmarks met
- Rich table with final status

**Acceptance Criteria**:
- ALL tasks marked COMPLETE
- ALL test cases pass (30/30)
- ALL performance targets met
- ALL features work in production
- NO incomplete functionality

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL previous tasks are verified as COMPLETE with passing tests and working functionality. The agent MUST continue iterating on incomplete tasks until 100% completion is achieved.

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| `llm_call()` | Basic text call | `llm_call({"model": "max/text-general", "question": "Hello"})` | Text response |
| `llm_call()` | JSON validation | `llm_call({"model": "openai/gpt-4", "validation": [{"type": "json_string"}]})` | Validated JSON |
| `llm_call()` | Multimodal call | `llm_call({"model": "max/claude", "messages": [...images...]})` | Image description |
| `llm_call()` | Agent validation | `llm_call({"validation": [{"type": "agent_task", "params": {...}}]})` | Agent-validated response |
| Test Runner | Run all tests | `python run_test_prompts.py` | 30/30 tests passed |
| POC Scripts | Validate concept | `python poc_01_claude_proxy_routing.py` | ✅ POC PASSED |

## Version Control Plan

- **Initial Commit**: Create task-004-start tag before implementation
- **POC Commits**: After each POC script completion
- **Feature Commits**: After each major feature implementation
- **Integration Commits**: After component integration
- **Test Commits**: After test suite completion
- **Final Tag**: Create task-004-complete after all tests pass

## Resources

**Python Packages**:
- litellm: Multi-provider LLM client
- pydantic: Data validation
- pytest: Testing framework
- httpx: HTTP client for images
- Pillow: Image processing

**Documentation**:
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Claude MCP Specification](https://github.com/anthropics/mcp)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Retry Best Practices](https://github.com/topics/retry-pattern)

**Example Implementations**:
- [LiteLLM Examples](https://github.com/BerriAI/litellm/tree/main/examples)
- [Validation Frameworks](https://github.com/topics/validation-framework)
- [Agent Architectures](https://github.com/topics/agent-based-validation)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All 30+ test cases passing, performance targets met

## Report Documentation Requirements

Each sub-task MUST have a corresponding verification report in `/docs/reports/` following these requirements:

### Report Structure:
Each report must include:
1. **Task Summary**: Brief description of what was implemented
2. **POC Scripts Created**: List of all POC scripts with results
3. **Research Findings**: Links to repos, code examples found, best practices discovered
4. **Non-Mocked Results**: Real API outputs and performance metrics
5. **Performance Metrics**: Actual benchmarks with real data
6. **Code Examples**: Working code with verified output
7. **Verification Evidence**: Logs or metrics proving functionality
8. **Limitations Found**: Any discovered issues or constraints
9. **External Resources Used**: All GitHub repos, articles, and examples referenced
10. **Test Results Table**: MANDATORY well-formatted markdown table

### MANDATORY Test Results Table Format

| Test | Description | Code Link | Input | Expected Output | Actual Output | Status |
|------|-------------|-----------|-------|-----------------|---------------|--------|

Example for this task:
| Test Case ID | Description | Test Type | Input Config | Expected Result | Actual Result | Status |
|--------------|-------------|-----------|--------------|-----------------|---------------|--------|
| max_text_001 | Simple Claude proxy call | Text | `{"model": "max/text-general", "question": "..."}` | Text response | "The primary function..." | ✅ PASS |
| openai_json_001 | JSON with field validation | JSON | `{"model": "openai/gpt-4", "validation": [...]}` | Valid JSON with fields | `{"title": "...", "author": "..."}` | ✅ PASS |
| agent_validation_001 | Contradiction check | Agent | `{"validation": [{"type": "agent_task"}]}` | Agent detects contradictions | `{"validation_passed": false, ...}` | ✅ PASS |

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.
