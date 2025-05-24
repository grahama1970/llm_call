# Task 015: Comprehensive LLM Call Testing ⏳ Not Started

**Objective**: Systematically test every reasonable variation of user configurations for the llm_call package to ensure robustness, flexibility, and proper error handling across all supported models and features.

**Requirements**:
1. Test all LiteLLM supported models with various configurations
2. Test Claude Max proxy option thoroughly
3. Validate all verification strategies work correctly
4. Test JSON and non-JSON response formats
5. Verify error handling and edge cases
6. Ensure retry mechanisms function properly
7. Test multimodal capabilities where applicable
8. Validate CLI and programmatic interfaces

## Overview

This comprehensive testing suite will validate that the llm_call package handles all reasonable user configurations correctly. We will execute all 30 test cases from `tests/fixtures/user_prompts.jsonl`, covering everything from simple calls to complex AI-assisted validation with MCP tools.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.
3. All 30 test cases from user_prompts.jsonl MUST pass before marking complete.

## Research Summary

The llm_call package is a sophisticated LLM routing and validation system that acts as a proxy layer for Claude and other LLM providers. It provides intelligent routing, validation strategies, retry mechanisms, and specialized Claude CLI integration.

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - LiteLLM configuration best practices 2025
   - Common LLM API error patterns and solutions
   - JSON mode implementation patterns
   - Validation strategy design patterns

2. **Use `WebSearch`** to find:
   - GitHub repositories using LiteLLM in production
   - Real-world LLM proxy implementations
   - Retry mechanism examples
   - Validation framework patterns

3. **Document all findings** in task reports:
   - Links to source repositories
   - Code snippets that work
   - Performance characteristics
   - Integration patterns

4. **DO NOT proceed without research**:
   - No theoretical implementations
   - No guessing at patterns
   - Must have real code examples
   - Must verify current best practices

Example Research Queries:
```
perplexity_ask: "litellm json mode configuration best practices 2025"
WebSearch: "site:github.com litellm retry validation production"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Basic Text Call Testing (Claude Proxy & LiteLLM) ⏳ Not Started

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to find LiteLLM basic usage patterns
- [ ] Use `WebSearch` to find production LiteLLM configurations
- [ ] Search GitHub for "litellm gpt-4 claude" examples
- [ ] Find real-world error handling strategies
- [ ] Locate performance benchmarking code

**Test Cases from user_prompts.jsonl**:
- max_text_001_simple_question_string
- max_text_002_user_message_only
- max_text_003_with_system_prompt
- max_text_004_no_validation_explicit
- max_text_005_custom_retry
- vertex_text_001_simple_question_string
- vertex_text_002_user_message_only
- vertex_text_003_with_system_prompt
- misc_001_openai_no_validation
- max_text_006_only_system_prompt_error
- openai_text_001_no_validation

**Implementation Steps**:
- [ ] 1.1 Test Claude proxy (max/) basic calls
  - Test simple question string format
  - Test with messages array format
  - Test with system + user messages
  - Test with default_validate: false
  - Test custom retry configurations

- [ ] 1.2 Test LiteLLM provider calls
  - Test Vertex AI/Gemini models
  - Test OpenAI models
  - Test with various message formats
  - Verify consistent response handling
  - Test question vs messages format

- [ ] 1.3 Test parameter variations
  - Temperature settings (0.5, 0.7)
  - Max tokens limits (100, 150, 200)
  - Custom retry configs
  - default_validate flag
  - Model aliases

- [ ] 1.4 Test edge cases
  - System-only messages (should error)
  - Empty responses
  - Missing user messages
  - Invalid model names
  - Malformed configurations

- [ ] 1.5 Create verification report
  - Create `/docs/reports/015_task_1_basic_text_calls.md`
  - Include test results table
  - Document all 11 test cases
  - Show actual API responses
  - Note any failures or issues

- [ ] 1.6 Git commit feature

**Technical Specifications**:
- Response time: <5s for basic calls
- Error handling: Graceful failures with clear messages
- Success rate: >95% for valid configurations

**Verification Method**:
- Execute all test scenarios
- Capture actual responses
- Measure response times
- Document error messages

**CLI Testing Requirements**:
- [ ] Test via llm-cli ask command
- [ ] Test via Python API
- [ ] Compare CLI vs API results
- [ ] Verify consistent behavior

**Acceptance Criteria**:
- All valid model calls succeed
- Error messages are clear
- Response times acceptable
- No unexpected failures

### Task 2: JSON Mode and Field Validation Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "openai json mode system prompt requirements 2025"
- [ ] Use `WebSearch` for "site:github.com litellm response_format json_object"
- [ ] Find JSON validation patterns
- [ ] Research structured output best practices

**Test Cases from user_prompts.jsonl**:
- openai_json_001_basic_json_request
- max_json_002_proxy_json_request
- combo_val_001_json_and_fields_openai
- combo_val_003_multiple_simple_validators
- vertex_json_002_malformed_request

**Implementation Steps**:
- [ ] 2.1 Test JSON mode with OpenAI
  - Test response_format={"type": "json_object"}
  - Verify JSON validation chain
  - Test field_present validators
  - Validate user details JSON
  - Check multiple field validation

- [ ] 2.2 Test JSON mode with Claude proxy
  - Test max/json_formatter_agent
  - Verify system prompt handling
  - Test status and data array format
  - Validate JSON structure
  - Test field validation

- [ ] 2.3 Test complex validation chains
  - response_not_empty + json_string
  - Multiple field_present validators
  - Product catalog JSON structure
  - Name/city extraction
  - Nested field validation

- [ ] 2.4 Test malformed JSON retry
  - Vertex AI with buggy JSON prompt
  - Test trailing comma scenario
  - Verify retry mechanism fixes JSON
  - Test debug_mode logging
  - Validate final correct output

- [ ] 2.5 Create verification report
  - Create `/docs/reports/015_task_2_json_field_validation.md`
  - Include test results table
  - Document all 5 test cases
  - Show JSON outputs and validation
  - Note retry behaviors

- [ ] 2.6 Git commit feature

**Technical Specifications**:
- JSON validation: 100% for JSON mode
- Error recovery: Graceful handling of malformed JSON
- Performance: <10% overhead for JSON mode

**Verification Method**:
- Parse all JSON responses
- Validate against schemas
- Test edge cases
- Measure overhead

**Acceptance Criteria**:
- JSON mode produces valid JSON
- Non-JSON modes work correctly
- Validation catches errors
- Clear error messages

### Task 3: AI-Assisted Validation Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "llm response validation patterns 2025"
- [ ] Use `WebSearch` for "site:github.com ai response validation strategies"
- [ ] Find validation framework examples
- [ ] Research retry patterns with validation

**Test Cases from user_prompts.jsonl**:
- ai_validation_001_contradiction_flat_earth
- ai_validation_002_contradiction_cold_fusion
- agent_task_001_simple_command
- combo_val_002_agent_task_specific_mcp
- ai_complex_001_code_refactor_validation
- ai_complex_002_contradiction_with_large_text_delegation
- max_text_007_tool_use_without_explicit_mcp_in_config

**Implementation Steps**:
- [ ] 3.1 Test AI contradiction checking
  - Flat Earth contradiction validation
  - Cold Fusion contradiction validation
  - Test with Perplexity MCP tool
  - Verify Claude agent validation
  - Check validation reasoning

- [ ] 3.2 Test agent task validation
  - Simple command validation
  - Task verification with MCP tools
  - Python research validation
  - Tool usage validation
  - Success criteria checking

- [ ] 3.3 Test complex AI validation
  - Code refactor validation
  - Python syntax checking
  - Function testing validation
  - Docstring verification
  - Multi-criteria validation

- [ ] 3.4 Test MCP configurations
  - Specific MCP tool configs
  - Default MCP fallback
  - Multiple tool availability
  - Large text delegation
  - Tool chaining scenarios

- [ ] 3.5 Create verification report
  - Create `/docs/reports/015_task_3_ai_validation.md`
  - Include test results table
  - Document all 7 test cases
  - Show validation outputs
  - Include MCP tool usage

- [ ] 3.6 Git commit feature

**Technical Specifications**:
- Validation accuracy: >95%
- Retry success rate: >80% within 3 attempts
- Performance overhead: <20%

**Verification Method**:
- Test each validator type
- Measure success rates
- Track retry patterns
- Document failures

**Acceptance Criteria**:
- All validators function correctly
- Retry mechanism works
- Clear validation feedback
- Acceptable performance

### Task 4: Multimodal Testing (Images with LLM calls) ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "gpt-4-vision image handling best practices 2025"
- [ ] Use `WebSearch` for "site:github.com litellm multimodal examples"
- [ ] Find image processing patterns
- [ ] Research base64 encoding strategies

**Test Cases from user_prompts.jsonl**:
- openai_multimodal_001_image_description_local
- openai_multimodal_002_http_image
- max_multimodal_001_image_description_local
- max_multimodal_002_http_image

**Implementation Steps**:
- [ ] 4.1 Test OpenAI multimodal calls
  - Local image with GPT-4o-mini
  - Test image_directory parameter
  - HTTP image URL handling
  - Color/content description
  - Logo recognition test

- [ ] 4.2 Test Claude proxy multimodal
  - Local image via max/image_analyzer_agent
  - Test image path resolution
  - HTTP URL passthrough
  - Image description quality
  - Error handling for missing images

- [ ] 4.3 Test image processing
  - Base64 encoding verification
  - Image size handling
  - Format compatibility (PNG, JPEG)
  - Multiple images in one request
  - Large image handling

- [ ] 4.4 Test edge cases
  - Missing image files
  - Invalid image formats
  - Corrupted images
  - Very large images
  - Network image timeouts

- [ ] 4.5 Create verification report
  - Create `/docs/reports/015_task_4_multimodal.md`
  - Include test results table
  - Document all 4 test cases
  - Show image analysis outputs
  - Include performance metrics

- [ ] 4.6 Git commit feature

**Technical Specifications**:
- Response time: <10s for Claude calls
- Streaming latency: <500ms
- Error recovery: 100% graceful

**Verification Method**:
- Test all Claude models
- Measure streaming performance
- Test error scenarios
- Verify output format

**Acceptance Criteria**:
- Claude proxy works reliably
- Streaming functions properly
- Errors handled gracefully
- Performance acceptable

### Task 5: Staged Retry and Escalation Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "llm retry strategies with tool escalation 2025"
- [ ] Use `WebSearch` for "site:github.com retry backoff patterns"
- [ ] Find staged escalation examples
- [ ] Research human-in-the-loop patterns

**Test Cases from user_prompts.jsonl**:
- code_gen_001_force_tool_retry
- code_gen_002_force_human_escalation
- misc_002_max_empty_response_test
- misc_003_short_max_tokens_vertex

**Implementation Steps**:
- [ ] 5.1 Test tool use escalation
  - Force initial failure with bad syntax
  - Verify tool suggestion after N attempts
  - Test perplexity-ask tool injection
  - Verify MCP config handling
  - Check successful retry after tool use

- [ ] 5.2 Test human escalation
  - Force persistent validation failures
  - Test max_attempts_before_human threshold
  - Verify human review error raised
  - Check error context preservation
  - Test escalation messaging

- [ ] 5.3 Test retry configurations
  - Custom retry counts
  - Debug mode logging
  - Initial delay settings
  - Backoff strategies
  - Retry feedback incorporation

- [ ] 5.4 Test edge cases
  - Empty response handling
  - Max tokens exhaustion
  - Finish reason 'length'
  - Network failures
  - Timeout scenarios

- [ ] 5.5 Create verification report
  - Create `/docs/reports/015_task_5_retry_escalation.md`
  - Include test results table
  - Document all 4 test cases
  - Show retry sequences
  - Include escalation outputs

- [ ] 5.6 Git commit feature

**Technical Specifications**:
- Image processing: <2s overhead
- Feature detection: 100% accurate
- Error messages: Clear and actionable

**Verification Method**:
- Test all multimodal scenarios
- Verify feature compatibility
- Document limitations
- Measure performance

**Acceptance Criteria**:
- Multimodal inputs work
- Complex configs handled
- Clear compatibility rules
- Good performance

### Task 6: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 6.1 Review all task reports
  - Read all reports in `/docs/reports/015_task_*`
  - Create checklist of incomplete features
  - Identify failed tests or missing functionality
  - Document specific issues preventing completion
  - Prioritize fixes by impact

- [ ] 6.2 Create task completion matrix
  - Build comprehensive status table
  - Mark each sub-task as COMPLETE/INCOMPLETE
  - List specific failures for incomplete tasks
  - Identify blocking dependencies
  - Calculate overall completion percentage

- [ ] 6.3 Iterate on incomplete tasks
  - Return to first incomplete task
  - Fix identified issues
  - Re-run validation tests
  - Update verification report
  - Continue until task passes

- [ ] 6.4 Re-validate completed tasks
  - Ensure no regressions from fixes
  - Run integration tests
  - Verify cross-task compatibility
  - Update affected reports
  - Document any new limitations

- [ ] 6.5 Final comprehensive validation
  - Run all 30 test cases from user_prompts.jsonl
  - Verify all validations work
  - Test all retry scenarios
  - Confirm MCP integrations
  - Validate multimodal handling

- [ ] 6.6 Create final summary report
  - Create `/docs/reports/015_final_summary.md`
  - Include completion matrix
  - Document all 30 test cases
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 6.7 Mark task complete only if ALL sub-tasks pass
  - Verify 100% task completion
  - All 30 test cases must pass
  - Ensure no critical issues remain
  - Document any workarounds needed
  - Update task status to ✅ Complete

**Technical Specifications**:
- Zero tolerance for incomplete features
- Mandatory iteration until completion
- All tests must pass
- All reports must verify success
- No theoretical completions allowed

**Verification Method**:
- Task completion matrix showing 100%
- All reports confirming success
- Comprehensive test results table

**Acceptance Criteria**:
- ALL tasks marked COMPLETE
- ALL verification reports show success
- ALL tests pass without issues
- ALL features work in production
- NO incomplete functionality

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL previous tasks are verified as COMPLETE with passing tests and working functionality. The agent MUST continue iterating on incomplete tasks until 100% completion is achieved.

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| Basic call | Simple question | `{"model": "max/text-generation", "question": "Hello Claude"}` | Text response |
| JSON mode | Get JSON response | `{"response_format": {"type": "json_object"}}` | Valid JSON output |
| Field validation | Validate JSON fields | `{"validation": [{"type": "field_present", "params": {"field_name": "status"}}]}` | Validated JSON |
| AI validation | Contradiction check | `{"validation": [{"type": "ai_contradiction_check", "params": {...}}]}` | Validation result |
| Multimodal | Image analysis | `{"messages": [{"content": [{"type": "text"}, {"type": "image_url"}]}]}` | Image description |
| Retry escalation | Tool suggestion | `{"max_attempts_before_tool_use": 1}` | Tool use after failure |
| Human escalation | Human review | `{"max_attempts_before_human": 2}` | Human review needed |
| MCP tools | Tool configuration | `{"mcp_config": {"mcpServers": {...}}}` | Tool execution |
| Test Matrix | All 30 test cases | Review `/docs/reports/015_final_summary.md` | 100% pass required |

## Version Control Plan

- **Initial Commit**: Create task-015-start tag before implementation
- **Feature Commits**: After each test category
- **Report Commits**: After each verification report
- **Fix Commits**: After addressing failures
- **Final Tag**: Create task-015-complete after all tests pass

## Resources

**Python Packages**:
- litellm: Core LLM integration
- httpx: Async HTTP client
- loguru: Logging framework
- redis: Caching backend

**Documentation**:
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Redis Documentation](https://redis.io/docs/)

**Example Implementations**:
- [LiteLLM Examples](https://github.com/BerriAI/litellm/tree/main/examples)
- [LLM Proxy Patterns](https://github.com/topics/llm-proxy)
- [Validation Frameworks](https://github.com/topics/validation-framework)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All tests passing, no failures, comprehensive documentation

---

This task document serves as the comprehensive testing guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.