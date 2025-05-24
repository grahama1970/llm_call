# Task 011: Comprehensive CLI and Core Testing ⏳ Not Started

**Objective**: Thoroughly test every CLI command, parameter, and core functionality to ensure the project is free from bugs. Validate that src/llm_call/cli/ and src/llm_call/core/ work as expected with proper validation, error handling, and integration.

**Requirements**:
1. Test all CLI commands with every parameter combination
2. Validate validation strategies work correctly post-LLM response
3. Test max/claude models with Claude CLI proxy integration
4. Verify config file loading (JSON/YAML) with overrides
5. Test slash command generation with full parameter preservation
6. Validate core module integration (caller.py, router.py, providers)
7. Test error handling for invalid inputs and edge cases
8. Ensure all tests use real data and produce expected results
9. Create verification reports with actual command outputs
10. Fix any bugs discovered during testing

## Overview

This task provides comprehensive testing of the LLM CLI system after fixing the validation implementation. The CLI now properly handles validation by extracting it from the config before passing to LiteLLM and applying validation strategies after receiving responses.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 7 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

The validation system has been fixed to properly:
- Extract validation from CLI config before LLM calls
- Apply validation strategies after LLM responses  
- Support built-in validators (response_not_empty, json_string, code, etc.)
- Integrate with retry mechanisms when validation fails

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use external research tools** when functionality fails 3+ times
2. **Document all findings** in task reports with links and examples
3. **Base implementations on real working code** not theoretical patterns
4. **Verify current best practices** for CLI testing and validation

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: CLI Command Basic Functionality ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Implementation Steps**:
- [ ] 1.1 Test basic ask command
  - Test: `llm-cli ask "What is 2+2?"`
  - Expected: Mathematical answer (e.g., "4" or "2+2 equals 4")
  - Verify: Response is non-empty and mathematically correct
  - Document: Exact command, response time, response content

- [ ] 1.2 Test ask with model selection
  - Test: `llm-cli ask "Hello" --model gpt-4`
  - Test: `llm-cli ask "Hello" --model gpt-3.5-turbo`
  - Expected: Different model responses, both non-empty
  - Verify: Model selection actually affects the call
  - Document: Response differences between models

- [ ] 1.3 Test ask with temperature control
  - Test: `llm-cli ask "Tell me a creative story" --temp 0.1`
  - Test: `llm-cli ask "Tell me a creative story" --temp 1.5`
  - Expected: Lower temp = more focused, higher temp = more creative
  - Verify: Responses show expected temperature behavior
  - Document: Response creativity differences

- [ ] 1.4 Test ask with token limits
  - Test: `llm-cli ask "Explain quantum physics" --max-tokens 10`
  - Test: `llm-cli ask "Explain quantum physics" --max-tokens 100`
  - Expected: Shorter response with lower token limit
  - Verify: Token limits are respected
  - Document: Response lengths and adherence to limits

- [ ] 1.5 Test ask with system prompts
  - Test: `llm-cli ask "What is Python?" --system "You are a expert programmer"`
  - Expected: More technical, detailed programming-focused response
  - Verify: System prompt influences response style
  - Document: Response quality and technical accuracy

- [ ] 1.6 Test ask with JSON mode
  - Test: `llm-cli ask "List 3 colors" --json`
  - Expected: Valid JSON array/object response
  - Verify: Response is valid JSON format
  - Document: JSON validity and structure

- [ ] 1.7 Create verification report
  - Create `/docs/reports/011_task_1_basic_cli_commands.md`
  - Include all command outputs and response times
  - Document any failures or unexpected behaviors
  - Include performance metrics for each test

**Technical Specifications**:
- Response time target: <10 seconds per command
- Success rate requirement: 100% for basic commands
- Response quality: Accurate and relevant to prompts
- Error rate: 0% for valid inputs

**Verification Method**:
- Run each command with actual CLI
- Capture exact output and timing
- Compare responses against expected behavior
- Document any deviations or errors

**Acceptance Criteria**:
- All basic commands execute successfully
- Responses are accurate and appropriate
- Model selection works correctly
- Parameter effects are observable
- No CLI crashes or errors

### Task 2: Validation System Comprehensive Testing ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: HIGH | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 2.1 Test response_not_empty validation
  - Test: `llm-cli ask "What is 2+2?" --validate response_not_empty`
  - Expected: Successful response with validation passing
  - Verify: Response contains actual content
  - Document: Validation logs and success confirmation

- [ ] 2.2 Test JSON validation
  - Test: `llm-cli ask "List 3 colors as JSON" --validate json_string --json`
  - Expected: Valid JSON response that passes validation
  - Verify: Response is properly formatted JSON
  - Document: JSON structure and validation success

- [ ] 2.3 Test multiple validators
  - Test: `llm-cli ask "Generate JSON data" --validate response_not_empty --validate json_string --json`
  - Expected: Response passes both validations
  - Verify: Multiple validation strategies execute in sequence
  - Document: Each validation step and overall result

- [ ] 2.4 Test validation failure and retry
  - Create scenario that triggers validation failure
  - Test validation retry mechanism
  - Expected: System retries until validation passes or max attempts reached
  - Verify: Retry logs show validation attempts
  - Document: Retry behavior and final outcome

- [ ] 2.5 Test all available validators
  - Test each validator from `llm-cli validators` output
  - Test: code, schema, length, contains, regex validators
  - Expected: Each validator works according to its purpose
  - Verify: Validators correctly accept/reject appropriate content
  - Document: Each validator's behavior and test results

- [ ] 2.6 Test validation with config files
  - Create config file with validation settings
  - Test: `llm-cli call validation_config.json`
  - Expected: File-based validation configuration works
  - Verify: Config file validation is applied correctly
  - Document: Config file structure and validation results

- [ ] 2.7 Create validation verification report
  - Create `/docs/reports/011_task_2_validation_testing.md`
  - Document all validation tests and outcomes
  - Include retry logs and performance metrics
  - Report any validation failures or issues

**Technical Specifications**:
- Validation accuracy: 100% correct accept/reject decisions
- Retry mechanism: Functional with backoff delays
- Performance target: Validation adds <2 seconds overhead
- Error handling: Graceful failure with clear messages

**Verification Method**:
- Test each validator with appropriate content
- Verify validation occurs AFTER LLM response
- Confirm validation parameters not sent to LLM
- Document validation timing and effectiveness

**Acceptance Criteria**:
- All validators work correctly
- Validation happens post-response  
- Retry mechanism functions properly
- No validation parameters sent to LLM
- Clear validation success/failure reporting

### Task 3: Claude CLI Proxy Model Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Implementation Steps**:
- [ ] 3.1 Test max model routing
  - Test: `llm-cli ask "Hello" --model max/claude-3-haiku`
  - Expected: Routes to PROXY instead of LITELLM
  - Verify: Router correctly identifies max/ prefix
  - Document: Routing decision and logs

- [ ] 3.2 Test Claude CLI proxy integration (if available)
  - Start Claude CLI proxy server if available
  - Test: `llm-cli ask "What is the capital of France?" --model max/claude-3-opus`
  - Expected: Response from Claude via CLI proxy
  - Verify: Successful proxy communication
  - Document: Proxy response and performance

- [ ] 3.3 Test proxy error handling
  - Test max model without proxy server running
  - Expected: Clear error message about proxy unavailability
  - Verify: Graceful failure with helpful error message
  - Document: Error handling behavior

- [ ] 3.4 Test proxy with validation
  - Test: `llm-cli ask "Generate code" --model max/claude-3-sonnet --validate code`
  - Expected: Proxy response with validation applied
  - Verify: Validation works with proxy responses
  - Document: Proxy + validation integration

- [ ] 3.5 Create proxy testing report
  - Create `/docs/reports/011_task_3_claude_proxy_testing.md`
  - Document routing behavior and proxy communication
  - Include error handling and validation integration
  - Report proxy availability and functionality

**Technical Specifications**:
- Routing accuracy: 100% correct provider selection
- Proxy communication: Functional when server available
- Error handling: Clear messages for proxy issues
- Validation integration: Works with proxy responses

**Verification Method**:
- Test routing with model names
- Verify proxy communication logs
- Test error scenarios
- Confirm validation applies to proxy responses

**Acceptance Criteria**:
- Correct routing for max/ models
- Functional proxy communication when available
- Clear error messages for proxy issues
- Validation works with all provider types

### Task 4: Configuration System Testing ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Implementation Steps**:
- [ ] 4.1 Test JSON config files
  - Create comprehensive JSON config file
  - Test: `llm-cli call test_config.json`
  - Expected: Config loaded and applied correctly
  - Verify: All config parameters take effect
  - Document: Config structure and application

- [ ] 4.2 Test YAML config files
  - Create equivalent YAML config file
  - Test: `llm-cli call test_config.yaml`
  - Expected: YAML config works identically to JSON
  - Verify: YAML parsing and parameter application
  - Document: YAML format support and functionality

- [ ] 4.3 Test config file overrides
  - Test: `llm-cli call config.json --model gpt-4 --temp 0.5`
  - Expected: CLI parameters override config file values
  - Verify: Override precedence is correct
  - Document: Override behavior and final config

- [ ] 4.4 Test complex config scenarios
  - Config with validation, retry, and response format
  - Test: `llm-cli call complex_config.json --show-config`
  - Expected: All complex settings applied correctly
  - Verify: Config display shows final merged settings
  - Document: Complex configuration handling

- [ ] 4.5 Test config generation
  - Test: `llm-cli config-example --format json`
  - Test: `llm-cli config-example --format yaml --output sample.yaml`
  - Expected: Valid example configs generated
  - Verify: Generated configs are usable
  - Document: Config generation functionality

- [ ] 4.6 Create configuration testing report
  - Create `/docs/reports/011_task_4_configuration_testing.md`
  - Document all config tests and file formats
  - Include override behavior and complex scenarios
  - Report config generation and validation

**Technical Specifications**:
- Config loading: 100% success rate for valid files
- Override behavior: CLI parameters take precedence
- Format support: Both JSON and YAML work identically
- Error handling: Clear messages for invalid configs

**Verification Method**:
- Test config loading with various file formats
- Verify parameter precedence in override scenarios
- Test config generation and usability
- Document config merging behavior

**Acceptance Criteria**:
- JSON and YAML configs work correctly
- Override precedence is properly implemented
- Complex configurations are handled correctly
- Config generation produces usable files
- Clear error messages for config issues

### Task 5: Slash Command Generation Testing ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: MEDIUM

**Implementation Steps**:
- [ ] 5.1 Test basic slash command generation
  - Test: `llm-cli generate-claude --output .claude/test_commands --verbose`
  - Expected: JSON files created for each CLI command
  - Verify: Generated files have correct structure
  - Document: Generation process and file contents

- [ ] 5.2 Test generated command structure
  - Examine generated JSON files
  - Verify: Commands include all parameter definitions
  - Verify: Parameter types are correctly identified
  - Document: Command structure and parameter accuracy

- [ ] 5.3 Test command parameter preservation
  - Check that complex commands preserve all options
  - Verify: ask command includes all CLI parameters
  - Verify: Optional parameters marked correctly
  - Document: Parameter preservation and type detection

- [ ] 5.4 Test slash command usability
  - Load generated commands into Claude Code (if available)
  - Test: Execute generated slash commands
  - Expected: Commands work as CLI equivalents
  - Verify: Parameter passing works correctly
  - Document: Usability and functionality

- [ ] 5.5 Test command filtering
  - Verify: Generation skips meta-commands appropriately
  - Check: generate-claude not included in output
  - Expected: Only user-facing commands generated
  - Document: Command filtering logic

- [ ] 5.6 Create slash command testing report
  - Create `/docs/reports/011_task_5_slash_command_testing.md`
  - Document generation process and file structure
  - Include parameter preservation analysis
  - Report usability and filtering behavior

**Technical Specifications**:
- Generation success: 100% for all eligible commands
- Parameter accuracy: All CLI options preserved
- File format: Valid JSON structure
- Command filtering: Appropriate exclusions

**Verification Method**:
- Generate slash commands and inspect output
- Verify JSON file validity and structure
- Test parameter preservation for complex commands
- Document generation behavior and results

**Acceptance Criteria**:
- All CLI commands generate valid slash configurations
- Parameter types and options are preserved correctly
- Generated commands are usable in Claude Code
- Appropriate command filtering is applied
- Generated files have consistent structure

### Task 6: Error Handling and Edge Cases ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Implementation Steps**:
- [ ] 6.1 Test invalid command syntax
  - Test: `llm-cli ask` (missing required argument)
  - Test: `llm-cli ask "test" --invalid-option`
  - Expected: Clear error messages for syntax errors
  - Verify: CLI shows helpful usage information
  - Document: Error message quality and helpfulness

- [ ] 6.2 Test invalid model names
  - Test: `llm-cli ask "test" --model nonexistent-model`
  - Expected: Clear error about invalid model
  - Verify: Model validation works correctly
  - Document: Model error handling

- [ ] 6.3 Test invalid config files
  - Test with malformed JSON config
  - Test with missing config file
  - Expected: Clear error messages for config issues
  - Verify: Config validation prevents crashes
  - Document: Config error handling

- [ ] 6.4 Test network and API errors
  - Test with invalid API keys (if possible)
  - Test with network connectivity issues
  - Expected: Graceful error handling with retry
  - Verify: Retry mechanism functions correctly
  - Document: Network error resilience

- [ ] 6.5 Test validation edge cases
  - Test with empty responses
  - Test with malformed JSON when JSON expected
  - Expected: Validation catches issues appropriately
  - Verify: Validation error messages are clear
  - Document: Validation edge case handling

- [ ] 6.6 Create error handling report
  - Create `/docs/reports/011_task_6_error_handling.md`
  - Document all error scenarios tested
  - Include error message quality assessment
  - Report system resilience and recovery

**Technical Specifications**:
- Error coverage: Test all major error categories
- Error messages: Clear and actionable
- System stability: No crashes on invalid input
- Recovery: Graceful handling of temporary failures

**Verification Method**:
- Test various invalid input scenarios
- Verify error message clarity and usefulness
- Test system recovery from error conditions
- Document error handling effectiveness

**Acceptance Criteria**:
- System handles all invalid inputs gracefully
- Error messages are clear and helpful
- No crashes or undefined behavior
- Retry mechanisms work for recoverable errors
- Validation errors are properly reported

### Task 7: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 7.1 Review all task reports
  - Read all reports in `/docs/reports/011_task_*`
  - Create checklist of incomplete features
  - Identify failed tests or missing functionality
  - Document specific issues preventing completion
  - Prioritize fixes by impact

- [ ] 7.2 Create task completion matrix
  - Build comprehensive status table
  - Mark each sub-task as COMPLETE/INCOMPLETE
  - List specific failures for incomplete tasks
  - Identify blocking dependencies
  - Calculate overall completion percentage

- [ ] 7.3 Iterate on incomplete tasks
  - Return to first incomplete task
  - Fix identified issues
  - Re-run validation tests
  - Update verification report
  - Continue until task passes

- [ ] 7.4 Re-validate completed tasks
  - Ensure no regressions from fixes
  - Run integration tests
  - Verify cross-task compatibility
  - Update affected reports
  - Document any new limitations

- [ ] 7.5 Final comprehensive validation
  - Run all CLI commands
  - Execute performance benchmarks
  - Test all integrations
  - Verify documentation accuracy
  - Confirm all features work together

- [ ] 7.6 Create final summary report
  - Create `/docs/reports/011_final_summary.md`
  - Include completion matrix
  - Document all working features
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 7.7 Mark task complete only if ALL sub-tasks pass
  - Verify 100% task completion
  - Confirm all reports show success
  - Ensure no critical issues remain
  - Get final approval
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
- Rich table with final status

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
| `llm-cli ask` | Basic LLM query | `llm-cli ask "What is 2+2?"` | Mathematical answer (e.g., "4") |
| `llm-cli ask --validate` | Query with validation | `llm-cli ask "Hello" --validate response_not_empty` | Validated non-empty response |
| `llm-cli ask --model` | Model selection | `llm-cli ask "Hello" --model gpt-4` | Response from specified model |
| `llm-cli ask --json` | JSON mode | `llm-cli ask "List colors" --json` | Valid JSON response |
| `llm-cli call` | Config file usage | `llm-cli call config.json` | Response using file config |
| `llm-cli models` | List models | `llm-cli models --all` | Available model list |
| `llm-cli validators` | List validators | `llm-cli validators` | Available validation strategies |
| `llm-cli generate-claude` | Generate slash commands | `llm-cli generate-claude` | Claude Code command files |
| Task Matrix | Verify completion | Review `/docs/reports/011_task_*` | 100% completion required |

## Version Control Plan

- **Initial Commit**: Create task-011-start tag before implementation
- **Feature Commits**: After each major test category  
- **Integration Commits**: After component integration testing
- **Test Commits**: After test suite completion
- **Final Tag**: Create task-011-complete after all tests pass

## Resources

**Python Packages**:
- llm_call: Main CLI package
- litellm: LLM integration
- typer: CLI framework
- rich: Output formatting

**Documentation**:
- [Typer Documentation](https://typer.tiangolo.com/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Rich Documentation](https://rich.readthedocs.io/)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All CLI commands tested, validation working, no bugs

## Report Documentation Requirements

Each sub-task MUST have a corresponding verification report in `/docs/reports/` following these requirements:

### Report Structure:
Each report must include:
1. **Task Summary**: Commands tested and results achieved
2. **Command Outputs**: Actual CLI executions with exact outputs
3. **Performance Metrics**: Response times and success rates
4. **Validation Results**: Validation behavior and effectiveness
5. **Error Cases**: Error handling and edge case testing
6. **Limitations Found**: Any discovered issues or constraints

### Report Naming Convention:
`/docs/reports/011_task_[N]_[description].md`

---

This task document serves as the comprehensive testing guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.