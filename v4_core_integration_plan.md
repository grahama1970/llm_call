# V4 Core Integration Plan

## Overview

With the v4 POC validated and working, we can now integrate the proven features into the core modules.

## Integration Tasks

### 1. Update `src/llm_call/core/retry.py`

**Current State**: Basic retry logic without staged escalation

**Changes Needed**:
- Add `PoCRetryConfig` features as `RetryConfig`
- Implement staged retry thresholds (`max_attempts_before_tool_use`, `max_attempts_before_human`)
- Add conversation context tracking
- Implement feedback message building with tool suggestions
- Add `HumanReviewNeededError` exception

**Key Functions to Port**:
- `extract_content_from_response()`
- `build_retry_feedback_message()`
- Enhanced `retry_with_validation()` with staged logic

### 2. Create `src/llm_call/core/validation/ai_validator_base.py`

**New Module**: AI-powered validation strategies

**Implementation**:
- Port `PoCAgentTaskValidator` as `AgentTaskValidator`
- Add proper base class inheritance from `AsyncValidationStrategy`
- Implement recursive LLM call support
- Add MCP config injection support
- Support complex success criteria evaluation

**Key Features**:
- Placeholder substitution (`{CODE_TO_VALIDATE}`, `{TEXT_TO_VALIDATE}`, `{ORIGINAL_USER_PROMPT}`)
- JSON response parsing from validation agents
- Success criteria: `must_contain_in_details`, `all_true_in_details_keys`

### 3. Update `src/llm_call/core/caller.py`

**Current State**: Basic LLM call orchestration

**Changes Needed**:
- Add support for Claude proxy routes (`max/` prefix)
- Implement dynamic MCP config injection
- Add retry configuration pass-through
- Support question-to-messages format conversion
- Add original prompt tracking for validators

**Key Additions**:
```python
# Handle "question" format
if "question" in llm_config and "messages" not in llm_config:
    llm_config["messages"] = [{"role": "user", "content": llm_config.pop("question")}]

# Track original prompt for validators
original_user_prompt = extract_original_prompt(messages)
```

### 4. Update `src/llm_call/core/router.py`

**Current State**: Routes to different providers

**Changes Needed**:
- Add Claude proxy route handling
- Support `max/` model prefix routing
- Add proxy URL configuration
- Implement proper error handling for proxy timeouts

### 5. Update `src/llm_call/core/strategies.py`

**Current State**: Basic validation strategies

**Changes Needed**:
- Register new AI validator types
- Add `agent_task` to strategy registry
- Support dynamic validator configuration
- Add validator chaining support

### 6. Create `src/llm_call/core/providers/claude_cli_proxy.py`

**New Provider**: Claude CLI proxy provider

**Implementation**:
- Port proxy communication logic
- Add timeout configuration
- Implement health checks
- Support MCP config passing

### 7. Update `src/llm_call/cli/main.py`

**Current State**: Basic CLI interface

**Changes Needed**:
- Add commands for v4 features
- Support validation configuration in CLI
- Add retry configuration options
- Implement human review workflow

## Testing Strategy

### 1. Unit Tests
- Mock Claude proxy responses
- Test validation logic independently
- Test retry state machine
- Verify error handling

### 2. Integration Tests
- Use real Claude proxy for key scenarios
- Test end-to-end validation flows
- Verify retry escalation
- Test MCP integration

### 3. Performance Tests
- Measure validation overhead
- Test timeout handling
- Benchmark with/without caching
- Profile memory usage

## Migration Path

1. **Phase 1**: Core retry.py updates
   - Implement staged retry
   - Add conversation tracking
   - Test with existing validators

2. **Phase 2**: AI validator implementation
   - Create ai_validator_base.py
   - Test with simple prompts
   - Validate JSON parsing

3. **Phase 3**: Router and caller updates
   - Add proxy routing
   - Test with POC server
   - Verify timeout handling

4. **Phase 4**: CLI integration
   - Add new commands
   - Update documentation
   - Create usage examples

## Configuration Schema

```python
{
    "model": "max/claude-agent",
    "messages": [...],
    "validation": [
        {
            "type": "agent_task",
            "params": {
                "task_prompt_to_claude": "...",
                "validation_model_alias": "max/validator",
                "mcp_config": {...},
                "success_criteria": {...}
            }
        }
    ],
    "retry_config": {
        "max_attempts": 5,
        "max_attempts_before_tool_use": 2,
        "max_attempts_before_human": 4,
        "debug_mode": true
    },
    "mcp_config": {...}
}
```

## Success Metrics

1. All POC tests pass with core implementation
2. No performance regression for existing calls
3. Clean API maintains backward compatibility
4. Documentation covers all new features
5. CLI provides intuitive access to v4 features

## Next Steps

1. Start with retry.py enhancements
2. Create comprehensive unit tests
3. Implement AI validator
4. Update router and caller
5. Integrate with CLI
6. Update documentation

This plan ensures a systematic integration of v4 features while maintaining code quality and backward compatibility.