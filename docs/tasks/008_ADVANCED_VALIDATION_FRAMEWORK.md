# Task 008: Advanced Validation Framework 🔄 In Progress

**Objective**: Implement the sophisticated validation patterns from the POC into the core structure, including AI-assisted validation, staged retry escalation, and research-enabled contradiction checking.

**Requirements**:
1. Port POC retry manager with staged escalation (basic → tool-assisted → human review)
2. Implement AI-assisted validators that can make recursive LLM calls
3. Create research-enabled validators using MCP tools (perplexity-ask, web-search)
4. Support dynamic validator configuration with dependency injection
5. Enable validator-specific MCP tool configuration
6. Implement validation result accumulation for retry context
7. Create production-ready contradiction detection validators

## Overview

The POC demonstrates advanced validation patterns that go beyond simple response checking. This task implements AI-assisted validation where validators can:
- Make recursive LLM calls to verify responses
- Use external tools (perplexity-ask) for fact-checking
- Perform domain-specific validation (contradiction detection)
- Escalate through retry stages with increasing assistance

This creates a self-improving system where AI validates AI output using real-time research.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

The POC shows that effective AI validation requires:
- Recursive LLM calling capabilities for validators
- Tool integration for external fact-checking
- Staged retry escalation for difficult validations
- Context preservation across retry attempts
- Structured validation result formats

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - AI validation patterns 2025
   - LLM fact-checking techniques
   - Retry escalation strategies
   - Tool-assisted validation approaches

2. **Use `WebSearch`** to find:
   - GitHub repos with AI validation implementations
   - Production retry managers with escalation
   - LLM validation frameworks
   - Research-enabled validators

3. **Document all findings** in task reports:
   - Working validation patterns
   - Retry escalation examples
   - Tool integration approaches
   - Performance characteristics

4. **DO NOT proceed without research**:
   - Must find real AI validation examples
   - Must understand retry escalation patterns
   - Must locate tool-assisted validation code
   - Must verify best practices

Example Research Queries:
```
perplexity_ask: "AI assisted validation LLM fact checking 2025 best practices"
WebSearch: "site:github.com LLM validation framework retry escalation"
perplexity_ask: "contradiction detection AI validators research tools"
WebSearch: "site:github.com recursive LLM validation tool integration"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Staged Retry Manager with Escalation ✅ Complete

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "retry escalation patterns 2025 best practices"
- [ ] Use `WebSearch` for "site:github.com retry manager staged escalation"
- [ ] Search for "tenacity retry library advanced patterns"
- [ ] Find production retry managers with tool assistance
- [ ] Research human-in-the-loop validation patterns

**Implementation Steps**:
- [ ] 1.1 Create retry manager module
  - Create `/src/llm_call/core/validation/retry_manager.py`
  - Define `RetryConfig` with escalation thresholds
  - Implement `HumanReviewNeededError` exception
  - Add retry stage tracking

- [ ] 1.2 Implement staged retry logic
  - Basic retry attempts (configurable max_attempts)
  - Tool-assisted retry stage (after N failures)
  - Human review escalation (final stage)
  - Context accumulation between attempts
  - Validation error aggregation

- [ ] 1.3 Add retry context management
  - Preserve original request context
  - Accumulate validation errors
  - Track retry stage transitions
  - Build retry feedback messages
  - Pass context to validators

- [ ] 1.4 Create verification tests
  - Test basic retry flow
  - Test tool escalation trigger
  - Test human review escalation
  - Verify context preservation
  - Test with real LLM calls (NO MOCKING)

- [ ] 1.5 Create verification report
  - Document actual retry flows
  - Show stage transitions
  - Include real validation errors
  - Demonstrate context accumulation
  - Performance metrics

**Technical Specifications**:
- Support 3 retry stages minimum
- Configurable thresholds per stage
- Context preserved across retries
- Real validation errors (no mocking)
- Async/await compatible

**Verification Method**:
```python
# Test with actual failing validation
config = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Generate invalid JSON"}],
    "response_format": {"type": "json_object"},
    "retry_config": {
        "max_attempts": 5,
        "max_attempts_before_tool_use": 2,
        "max_attempts_before_human": 4
    }
}
# Should show retry progression through stages
```

**Acceptance Criteria**:
- Retry manager handles all 3 stages
- Context preserved across attempts
- Real validation failures trigger escalation
- No mocked responses
- Performance within limits

### Task 2: AI-Assisted Validator Base Class ✅ Complete

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "recursive LLM validation patterns"
- [ ] Use `WebSearch` for "site:github.com AI validator dependency injection"
- [ ] Find examples of validators calling LLMs
- [ ] Research async validation patterns
- [ ] Look for production AI validation frameworks

**Implementation Steps**:
- [ ] 2.1 Create AI validator base class
  - Create `/src/llm_call/core/validation/ai_validator_base.py`
  - Define `AIAssistedValidator` base class
  - Implement `set_llm_caller` method
  - Add recursive call protection
  - Handle async validation

- [ ] 2.2 Implement LLM caller injection
  - Support callable injection
  - Validate caller signature
  - Handle call failures gracefully
  - Add timeout protection
  - Log recursive calls

- [ ] 2.3 Add structured response handling
  - Parse JSON responses
  - Extract validation results
  - Handle parse errors
  - Support custom response formats
  - Aggregate sub-validation results

- [ ] 2.4 Test with real LLM calls
  - Create test validator
  - Make actual recursive calls
  - Verify response parsing
  - Test error handling
  - NO MOCKED LLM RESPONSES

- [ ] 2.5 Create verification report
  - Show actual recursive calls
  - Document response formats
  - Include performance data
  - Demonstrate error handling
  - Real validation examples

**Technical Specifications**:
- Async validation support
- Configurable timeout (30s default)
- Structured error reporting
- Real LLM calls only
- Type-safe implementation

**Verification Method**:
```python
# Test with actual recursive validation
validator = TestAIValidator()
validator.set_llm_caller(make_llm_request)
result = await validator.validate(response, context)
# Should show real LLM call to validate
```

**Acceptance Criteria**:
- Base class supports dependency injection
- Real recursive LLM calls work
- Structured responses parsed correctly
- Error handling tested with real failures
- No mocking of LLM calls

### Task 3: Research-Enabled Contradiction Validator ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "contradiction detection algorithms 2025"
- [ ] Use `WebSearch` for "site:github.com fact checking AI validator"
- [ ] Find scientific misinformation detection patterns
- [ ] Research tool-assisted validation examples
- [ ] Look for production fact-checking systems

**Implementation Steps**:
- [ ] 3.1 Implement contradiction validator
  - Create `/src/llm_call/core/validation/builtin_strategies/contradiction_validator.py`
  - Port `PoCAIContradictionValidator` logic
  - Add MCP tool configuration
  - Implement research prompts
  - Structure validation results

- [ ] 3.2 Add research tool integration
  - Configure perplexity-ask tool
  - Build research queries dynamically
  - Parse research results
  - Integrate findings into validation
  - Handle tool failures gracefully

- [ ] 3.3 Implement contradiction detection
  - Analyze text for logical inconsistencies
  - Check against research findings
  - Calculate confidence scores
  - Generate detailed reports
  - Return structured results

- [ ] 3.4 Test with real contradictions
  - Test with flat earth text
  - Test with cold fusion claims
  - Test with scientific facts
  - Verify research tool usage
  - NO MOCKED RESEARCH RESULTS

- [ ] 3.5 Create verification report
  - Show actual perplexity queries
  - Document contradiction findings
  - Include confidence scores
  - Demonstrate research integration
  - Real validation results

**Technical Specifications**:
- Uses perplexity-ask for research
- Confidence score 0.0-1.0
- Structured JSON responses
- Real tool calls only
- Domain-configurable

**Verification Method**:
```python
# Test with actual contradictory text
validator = ContradictionValidator(
    text_to_check="The Earth is flat and spherical",
    topic_context="Earth shape",
    required_mcp_tools=["perplexity-ask"]
)
result = await validator.validate(response, context)
# Should show real perplexity research
```

**Acceptance Criteria**:
- Validator uses real perplexity-ask
- Contradictions detected accurately
- Research queries logged
- Confidence scores meaningful
- No mocked tool responses

### Task 4: Generic Agent Task Validator ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "LLM task validation patterns"
- [ ] Use `WebSearch` for "site:github.com agent task validator"
- [ ] Find code validation examples
- [ ] Research success criteria patterns
- [ ] Look for production task validators

**Implementation Steps**:
- [ ] 4.1 Implement agent task validator
  - Create `/src/llm_call/core/validation/builtin_strategies/agent_task_validator.py`
  - Port `PoCAgentTaskValidator` logic
  - Support custom task prompts
  - Add success criteria evaluation
  - Handle placeholder substitution

- [ ] 4.2 Add flexible task configuration
  - Support task prompt templates
  - Implement placeholder system
  - Add MCP tool configuration
  - Support custom success criteria
  - Enable context passing

- [ ] 4.3 Implement success evaluation
  - Check basic pass/fail
  - Evaluate custom criteria
  - Support dict/list criteria
  - Calculate final result
  - Generate detailed reports

- [ ] 4.4 Test with real tasks
  - Test code validation
  - Test text analysis
  - Test with MCP tools
  - Verify criteria evaluation
  - NO MOCKED AGENT RESPONSES

- [ ] 4.5 Create verification report
  - Show actual agent tasks
  - Document success criteria
  - Include agent responses
  - Demonstrate tool usage
  - Real validation examples

**Technical Specifications**:
- Flexible task prompts
- Custom success criteria
- MCP tool support
- Real agent calls only
- Template substitution

**Verification Method**:
```python
# Test with actual code validation
validator = AgentTaskValidator(
    task_prompt="Validate this Python code works",
    mcp_config={"mcpServers": {"python_executor": {...}}},
    success_criteria={"all_true_in_details_keys": ["syntax_ok"]}
)
result = await validator.validate(code_response, context)
# Should show real agent execution
```

**Acceptance Criteria**:
- Validator executes real agent tasks
- Success criteria evaluated correctly
- MCP tools used when configured
- Template substitution works
- No mocked agent responses

### Task 5: Integration with Core Caller ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "validation framework integration patterns"
- [ ] Use `WebSearch` for "site:github.com LLM validation integration"
- [ ] Find caller integration examples
- [ ] Research validation pipelines
- [ ] Look for production integrations

**Implementation Steps**:
- [ ] 5.1 Update core caller
  - Modify `/src/llm_call/core/caller.py`
  - Add retry manager import
  - Replace basic retry logic
  - Add staged retry support
  - Preserve backward compatibility

- [ ] 5.2 Add validation config handling
  - Support POC validation format
  - Handle retry stage config
  - Pass MCP configs through
  - Enable tool escalation
  - Support human review

- [ ] 5.3 Implement error aggregation
  - Collect validation errors
  - Build retry context
  - Format error messages
  - Add to message history
  - Track retry stages

- [ ] 5.4 Test full integration
  - Test basic validation
  - Test retry escalation
  - Test tool assistance
  - Test human review
  - NO MOCKED COMPONENTS

- [ ] 5.5 Create verification report
  - Show integrated flow
  - Document retry stages
  - Include real errors
  - Demonstrate escalation
  - Performance metrics

**Technical Specifications**:
- Backward compatible
- Supports all retry stages
- Real validation flow
- Integrated error handling
- Production ready

**Verification Method**:
```python
# Test integrated validation flow
config = {
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Test"}],
    "validation": [{
        "type": "ai_contradiction_check",
        "params": {...}
    }],
    "retry_config": {
        "max_attempts_before_tool_use": 2
    }
}
response = await make_llm_request(config)
# Should show full integrated flow
```

**Acceptance Criteria**:
- Full integration works end-to-end
- All retry stages functional
- Validation errors aggregated
- Real LLM calls throughout
- No mocked integrations

### Task 6: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 6.1 Review all task reports
  - Read all `/docs/reports/008_task_*.md` files
  - Create checklist of incomplete features
  - Identify failed tests
  - Document blocking issues
  - Prioritize fixes

- [ ] 6.2 Create completion matrix
  - Build status table
  - Mark COMPLETE/INCOMPLETE
  - List specific failures
  - Identify dependencies
  - Calculate completion %

- [ ] 6.3 Iterate on incomplete tasks
  - Fix identified issues
  - Re-run validation tests
  - Update reports
  - Continue until passing
  - NO PARTIAL COMPLETION

- [ ] 6.4 End-to-end validation
  - Run full validation scenarios
  - Test all validator types
  - Verify retry escalation
  - Check tool integration
  - Confirm human review

- [ ] 6.5 Performance validation
  - Measure validation overhead
  - Check retry delays
  - Verify timeout handling
  - Test at scale
  - Document limits

- [ ] 6.6 Create final report
  - Complete feature matrix
  - Working examples
  - Performance data
  - Known limitations
  - Usage guide

**Technical Specifications**:
- 100% completion required
- All tests must pass
- Real validation only
- No theoretical completion
- Production ready

**Verification Method**:
- Run all test scenarios
- Verify all reports show COMPLETE
- Check performance metrics
- Confirm no mocking used

**Acceptance Criteria**:
- ALL tasks COMPLETE
- ALL tests passing
- Real validation throughout
- Performance acceptable
- Ready for production

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| `make_llm_request` | Request with validation | See config examples | Validated response |
| `ContradictionValidator` | Check for contradictions | `validator.validate()` | Research-based result |
| `AgentTaskValidator` | Run custom validation | With task prompt | Task execution result |
| Retry Manager | Handle staged retries | Automatic on failure | Escalated validation |

## Version Control Plan

- **Initial Commit**: Create task-008-start tag
- **Feature Commits**: After each validator implementation
- **Integration Commit**: After core integration
- **Test Commits**: After verification reports
- **Final Tag**: Create task-008-complete after 100% complete

## Resources

**Python Packages**:
- tenacity: Retry management
- httpx: Async HTTP client
- pydantic: Validation models
- loguru: Logging

**Documentation**:
- [Tenacity Docs](https://tenacity.readthedocs.io/)
- [AsyncIO Patterns](https://docs.python.org/3/library/asyncio.html)
- [Pydantic V2](https://docs.pydantic.dev/latest/)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All validators working with real validation

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.