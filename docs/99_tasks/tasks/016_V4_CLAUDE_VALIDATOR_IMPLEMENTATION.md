# Task List: V4 Claude Validator Implementation

## Overview
Implement the v4_claude_validator system that adds AI-assisted validation using Claude agents with MCP (Model Context Protocol) tools, dynamic tool configuration, recursive LLM calls, and multi-stage retry logic.

## Key Architecture Changes

### 1. MCP (Model Context Protocol) Integration
- **What**: Open standard by Anthropic for AI models to integrate with external tools and systems
- **Why**: Enables Claude agents to access tools dynamically during validation
- **How**: Server writes `.mcp.json` files in Claude CLI working directory per validation call

### 2. AI-Assisted Validation via Agent Tasks
- **PoCAgentTaskValidator**: New validator that delegates complex validation to Claude agents
- **Dynamic prompts**: Constructs natural language prompts with placeholders for content/context
- **Tool instructions**: Explicitly tells Claude which tools to use for validation
- **JSON response format**: Claude must respond with structured validation results

### 3. Multi-Stage Retry with Tool Escalation
- **Stage 1**: Self-correction with validation feedback (attempts 1-N)
- **Stage 2**: Tool-assisted retry with MCP config injection (attempts N+1-M)
- **Stage 3**: Human escalation if all attempts fail (attempt M+1)

### 4. Recursive LLM Capabilities
- **llm_call_tool**: Claude agents can make recursive LLM calls to other models
- **Use case**: Delegate large context analysis to models with bigger windows (e.g., Gemini)

## Implementation Tasks

### Task 1: Create MCP Infrastructure
**Objective**: Build foundation for Model Context Protocol support

**Files to create/modify**:
1. `src/llm_call/core/mcp/` directory structure
2. `src/llm_call/core/mcp/config.py` - MCP configuration handling
3. `src/llm_call/core/mcp/server.py` - MCP server definitions
4. `src/llm_call/core/mcp/tools.py` - Tool definitions

**Implementation steps**:
1. Define MCP config schema using Pydantic
2. Create tool definition format compatible with Claude CLI
3. Implement config writer that generates `.mcp.json` files
4. Add default tool configurations (perplexity-ask, python executor, etc.)

**Verification**:
- [ ] MCP config can be serialized to valid JSON
- [ ] Tool definitions include command, args, and env variables
- [ ] Default tools configuration loads correctly

### Task 2: Implement Claude Proxy Server
**Objective**: Create proxy server that handles MCP config injection

**Files to create**:
1. `src/llm_call/proof_of_concept/poc_claude_proxy_server.py`
2. `src/llm_call/core/providers/claude/mcp_handler.py`

**Implementation steps**:
1. Create FastAPI server that proxies to Claude CLI
2. Intercept requests to inject MCP config
3. Write `.mcp.json` to Claude's working directory
4. Handle default "all tools" config when none provided
5. Proxy responses back to client

**Verification**:
- [ ] Server starts and accepts POST requests
- [ ] MCP config is written before Claude CLI execution
- [ ] Responses are properly proxied back
- [ ] Default tools work when no config provided

### Task 3: Integrate PoCAgentTaskValidator
**Objective**: Add AI-assisted validation to existing framework

**Files to modify**:
1. `src/llm_call/proof_of_concept/poc_validation_strategies.py` - Copy v4 implementation
2. `src/llm_call/core/validation/ai_validator_base.py` - Update base classes
3. `src/llm_call/proof_of_concept/litellm_client_poc.py` - Update to use new validators

**Implementation steps**:
1. Copy PoCAgentTaskValidator from v4 implementation
2. Update validator registry to include agent_task type
3. Implement set_llm_caller for recursive calls
4. Add prompt template handling with placeholders
5. Parse Claude's JSON responses for validation results

**Verification**:
- [ ] Agent task validator instantiates correctly
- [ ] Prompts are built with proper placeholders
- [ ] Claude responses are parsed for validation results
- [ ] Success criteria evaluation works

### Task 4: Update Retry Manager for Staged Escalation
**Objective**: Enhance retry logic with tool suggestion and MCP injection

**Files to modify**:
1. `src/llm_call/proof_of_concept/poc_retry_manager.py`
2. `src/llm_call/core/retry.py` - Port changes to core

**Implementation steps**:
1. Add max_attempts_before_tool_use parameter handling
2. Add max_attempts_before_human parameter handling
3. Implement MCP config injection at tool threshold
4. Update feedback messages to suggest tool usage
5. Add PoCHumanReviewNeededError handling

**Verification**:
- [ ] Tool suggestion appears after N attempts
- [ ] MCP config is injected for tool-assisted retries
- [ ] Human escalation triggers at correct threshold
- [ ] Feedback messages include tool instructions

### Task 5: Implement Recursive LLM Call Tool
**Objective**: Enable Claude agents to delegate to other LLMs

**Files to create**:
1. `src/llm_call/tools/llm_call_delegator.py`
2. `src/llm_call/core/mcp/tools/llm_call_tool.json`

**Implementation steps**:
1. Create Python script that imports llm_call function
2. Accept parameters: model, messages, task description
3. Make recursive call using llm_call framework
4. Return results to stdout for Claude CLI
5. Create MCP tool definition for the script

**Verification**:
- [ ] Script can be executed standalone
- [ ] Recursive llm_call works correctly
- [ ] Output is captured by Claude CLI
- [ ] Tool definition is valid MCP format

### Task 6: Update Core Caller Integration
**Objective**: Integrate v4 changes into main llm_call function

**Files to modify**:
1. `src/llm_call/core/caller.py`
2. `src/llm_call/core/config/settings.py`

**Implementation steps**:
1. Add validation config parsing from llm_config
2. Support dynamic validator instantiation
3. Pass original_user_prompt to validators
4. Handle mcp_config in request payload
5. Update response handling for agent validators

**Verification**:
- [ ] Validation config is parsed correctly
- [ ] Agent validators receive proper context
- [ ] MCP config flows through the system
- [ ] Recursive calls work end-to-end

### Task 7: Create Comprehensive Test Suite
**Objective**: Test all v4 functionality with realistic scenarios

**Test cases from v4**:
1. Basic text calls with/without validation
2. JSON mode with field validation
3. Multimodal calls with image analysis
4. AI-assisted validation (contradiction check)
5. Code syntax validation with tools
6. Large text delegation to Gemini
7. Iterative code generation with staged retry

**Files to create**:
1. `tests/llm_call/core/test_v4_integration.py`
2. `tests/fixtures/v4_test_prompts.json`

**Verification**:
- [ ] All 30+ test cases from v4 pass
- [ ] MCP tools are called correctly
- [ ] Staged retry works as expected
- [ ] Human escalation triggers properly

## Success Criteria

1. **MCP Integration Working**:
   - Claude agents can use dynamically configured tools
   - `.mcp.json` files are created per validation call
   - Default tools work when no config provided

2. **AI-Assisted Validation Functional**:
   - PoCAgentTaskValidator makes successful calls to Claude
   - Claude uses specified tools during validation
   - JSON responses are parsed correctly
   - Validation pass/fail decisions are accurate

3. **Staged Retry Operational**:
   - Self-correction works for first N attempts
   - Tool usage is suggested after threshold
   - MCP config is injected for tool attempts
   - Human escalation triggers at final threshold

4. **Recursive Calls Successful**:
   - Claude agents can call other LLMs via llm_call_tool
   - Large context delegation to Gemini works
   - Results flow back through the validation chain

5. **All Test Cases Pass**:
   - 30+ test scenarios execute successfully
   - No regressions in existing functionality
   - Performance remains acceptable

## Test Results Table

| Test Case | Description | Implementation | Expected Result | Actual Result | Status |
|-----------|-------------|----------------|-----------------|---------------|---------|
| MCP Config Write | Server writes .mcp.json | poc_claude_proxy_server.py:45 | File created with tools | - | PENDING |
| Agent Task Validator | Claude validates with tools | poc_validation_strategies.py:125 | Validation result JSON | - | PENDING |
| Tool Suggestion | Retry suggests tool after N | poc_retry_manager.py:290 | Feedback includes tool | - | PENDING |
| MCP Injection | Config injected at threshold | poc_retry_manager.py:212 | Tool available to LLM | - | PENDING |
| Human Escalation | Escalate after M attempts | poc_retry_manager.py:191 | PoCHumanReviewNeededError | - | PENDING |
| Recursive LLM Call | Claude calls Gemini | llm_call_delegator.py:25 | Delegation successful | - | PENDING |
| JSON Validation | Validate response structure | test_prompts.json:case_3 | All fields present | - | PENDING |
| Contradiction Check | Perplexity validates text | test_prompts.json:case_5 | Contradictions found | - | PENDING |
| Code Syntax Check | Python linter validation | test_prompts.json:case_6 | Syntax errors detected | - | PENDING |
| Staged Retry Flow | Complete retry sequence | test_prompts.json:case_9 | Success after tool use | - | PENDING |

## Notes

1. **MCP Security**: Ensure tool definitions don't expose sensitive paths or commands
2. **Performance**: Monitor latency added by proxy server and MCP config writes
3. **Error Handling**: Gracefully handle missing tools or MCP config errors
4. **Backwards Compatibility**: Ensure existing validation strategies still work
5. **Documentation**: Update user guides with v4 features and examples

---

**Status**: PENDING
**Priority**: HIGH
**Estimated Effort**: 16-24 hours
**Dependencies**: 
- Model Context Protocol specification understanding
- Claude CLI MCP integration knowledge
- Access to test Claude proxy endpoint