# Task 3: Module Communication Refactor ⏳ Not Started

**Objective**: Refactor the claude_comms project to use the verified shell-based Claude CLI execution method for robust module-to-module communication.

**Requirements**:
1. Replace all instances of Claude CLI execution using the command list approach with the shell=True cd approach
2. Implement proper JSON parsing for all Claude CLI output formats across the codebase
3. Add timeout management to prevent hanging processes
4. Enhance error handling and reporting
5. Ensure cross-directory module communication works reliably
6. Update documentation with verified working approaches

## Overview

The claude_comms project enables modules to communicate with each other through Claude CLI. Critical to this functionality is the ability to execute Claude CLI in the specific directory context of each module. This task refactors the codebase to use the verified working approach of shell=True with cd command, ensuring proper directory context for Claude CLI execution.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 8 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

Research has shown that when executing Claude CLI in different directory contexts, using the subprocess.Popen with the cwd parameter does not correctly set the context for Claude CLI. Instead, a shell command with cd must be used with shell=True. This approach has been verified to work correctly while the command list approach with cwd fails.

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Current best practices (2025-current) for subprocess execution with directory context
   - Production implementation patterns for module-to-module communication
   - Common pitfalls and solutions in subprocess execution with shell=True
   - Performance optimization techniques for streaming processing

2. **Use `WebSearch`** to find:
   - GitHub repositories with working code for Python subprocess with shell commands
   - Real production examples of module communication architectures
   - Popular library implementations of streaming output processing
   - Security considerations for shell=True execution

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
perplexity_ask: "python subprocess shell=True cd command security best practices 2025"
WebSearch: "site:github.com python subprocess popen shell cd directory context"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Core Shell Command Execution Function ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research subprocess execution patterns
- [ ] Use `WebSearch` to find production Python subprocess examples
- [ ] Search GitHub for "subprocess shell cd directory context" examples
- [ ] Find real-world subprocess security strategies
- [ ] Locate performance benchmarking code for subprocess execution

**Example Starting Code** (to be found via research):
```python
# Agent MUST use perplexity_ask and WebSearch to find:
# 1. Best practices for subprocess.Popen with shell=True
# 2. Security patterns for string escaping in shell commands
# 3. Error handling approaches for subprocess
# 4. Timeout management strategies
# Example search queries:
# - "site:github.com python subprocess popen shell security" 
# - "subprocess shell=True security best practices 2025"
# - "python execute command in directory context"
```

**Working Starting Code** (verified working):
```python
def execute_claude_in_directory(
    working_dir: str,
    prompt: str,
    system_prompt: str,
    timeout: int = 60
) -> subprocess.Popen:
    # Escape quotes for shell safety
    escaped_system_prompt = system_prompt.replace('"', '\\"')
    escaped_prompt = prompt.replace('"', '\\"')
    
    # Build the shell command using the approach that works in terminal
    cmd_str = f'cd {working_dir} && timeout {timeout}s claude --system-prompt "{escaped_system_prompt}" -p "{escaped_prompt}" --output-format stream-json --verbose'
    
    # Use shell=True to execute the cd command and Claude in sequence
    proc = subprocess.Popen(
        cmd_str,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True  # This is critical for the cd command to work
    )
    
    return proc
```

**Implementation Steps**:
- [ ] 1.1 Create core function
  - Implement execute_claude_in_directory in claude_comms/core/execution.py
  - Add comprehensive docstrings
  - Include security considerations
  - Add proper error handling
  - Implement logging

- [ ] 1.2 Add timeout management
  - Implement timeout parameter
  - Add default timeout configuration
  - Handle timeout exceptions
  - Document timeout behaviors

- [ ] 1.3 Enhance security
  - Add proper string escaping
  - Validate inputs for injection risks
  - Document security considerations
  - Add safeguards against common vulnerabilities

- [ ] 1.4 Add output processing
  - Implement streaming output handling
  - Parse different JSON formats
  - Handle non-JSON lines
  - Implement content deduplication

- [ ] 1.5 Add error processing
  - Capture stderr output
  - Parse error messages
  - Categorize common errors
  - Provide helpful error reporting

- [ ] 1.6 Create verification report
  - Create `/docs/reports/003_task_1_core_execution.md`
  - Document actual commands and results
  - Include real execution examples
  - Show working code examples
  - Add evidence of functionality

- [ ] 1.7 Write unit tests
  - Test with mock subprocess
  - Test directory validation
  - Test error conditions
  - Test timeout behavior

- [ ] 1.8 Git commit feature

**Technical Specifications**:
- Performance target: <100ms for command setup
- Security requirement: All input properly escaped
- Reliability: Proper process termination on timeout
- Error handling: All errors properly captured and reported
- Compatibility: Works with all Claude CLI versions

**Verification Method**:
- Run with different directories
- Test with various prompts
- Check error handling
- Verify timeout behavior
- Test with malformed inputs

**Acceptance Criteria**:
- Function works in all target directories
- All security concerns addressed
- Proper timeout handling implemented
- Comprehensive error reporting
- Documentation complete

### Task 2: JSON Streaming Parser ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research JSON streaming patterns
- [ ] Use `WebSearch` to find production JSON stream processing examples
- [ ] Search GitHub for "claude cli json streaming parse" examples
- [ ] Find real-world streaming processor implementations
- [ ] Locate performance benchmarking code for streaming JSON

**Example Starting Code** (to be found via research):
```python
# Agent MUST use perplexity_ask and WebSearch to find:
# 1. JSON streaming processing patterns
# 2. Claude CLI output format parsing
# 3. Content extraction approaches
# 4. Efficient streaming implementation
# Example search queries:
# - "site:github.com python json streaming parser" 
# - "claude cli output format json schema 2025"
# - "python streaming json processing best practices"
```

**Working Starting Code** (verified working):
```python
def parse_claude_json_stream(proc: subprocess.Popen) -> Tuple[bool, List[str], str]:
    content_chunks: List[str] = []
    error_output: str = ""
    
    try:
        for line in proc.stdout:  # type: ignore
            line = line.strip()
            if not line or not line.startswith("{"):
                continue
                
            try:
                obj = json.loads(line)
                
                # Handle different JSON formats
                if "content" in obj:
                    # Handle direct content field (older format)
                    content_chunks.append(obj["content"])
                elif "type" in obj and obj.get("type") == "assistant" and "message" in obj:
                    # Handle Claude CLI message format
                    message = obj.get("message", {})
                    if "content" in message and isinstance(message["content"], list):
                        for content_item in message["content"]:
                            if content_item.get("type") == "text" and "text" in content_item:
                                content_chunks.append(content_item["text"])
                elif "type" in obj and obj.get("type") == "result" and "result" in obj:
                    # Handle the result field in the final summary
                    result_content = obj.get("result")
                    if result_content and isinstance(result_content, str):
                        # Avoid duplicates
                        if not any(chunk == result_content for chunk in content_chunks):
                            content_chunks.append(result_content)
            except json.JSONDecodeError:
                continue
        
        proc.wait()
        stderr_output = proc.stderr.read().strip()  # type: ignore
        
        success = proc.returncode == 0
        if not success:
            error_output = stderr_output
        
        return success, content_chunks, error_output
    except Exception as e:
        return False, content_chunks, str(e)
```

**Implementation Steps**:
- [ ] 2.1 Create streaming parser
  - Implement JSON streaming parser in claude_comms/core/parsing.py
  - Support all Claude CLI output formats
  - Add content deduplication
  - Handle error conditions
  - Include logging

- [ ] 2.2 Add format detection and handling
  - Detect and parse content format
  - Handle message format
  - Process result format
  - Support future format changes

- [ ] 2.3 Implement progress tracking
  - Track progress during streaming
  - Report percentage complete
  - Calculate tokens processed
  - Estimate remaining time

- [ ] 2.4 Add error recovery
  - Handle partial JSON
  - Recover from parse errors
  - Continue after non-JSON lines
  - Gracefully handle interruptions

- [ ] 2.5 Optimize performance
  - Reduce memory usage
  - Minimize string concatenation
  - Optimize JSON parsing
  - Improve error handling efficiency

- [ ] 2.6 Create verification report
  - Create `/docs/reports/003_task_2_json_parser.md`
  - Document actual parsing examples
  - Include real JSON outputs
  - Show parsing of different formats
  - Add evidence of functionality

- [ ] 2.7 Write unit tests
  - Test with sample outputs
  - Test error conditions
  - Test different formats
  - Test content deduplication

- [ ] 2.8 Git commit feature

**Technical Specifications**:
- Handle all Claude CLI output formats
- Support streaming with minimal buffering
- Properly deduplicate content
- Handle errors gracefully
- Maintain order of content

**Verification Method**:
- Test with sample Claude CLI outputs
- Verify handling of all formats
- Check error recovery
- Confirm content deduplication
- Validate formatting preservation

**Acceptance Criteria**:
- Correctly parses all Claude CLI formats
- Handles errors gracefully
- Deduplicates content appropriately
- Preserves content formatting
- Documentation complete

### Task 3: Module-to-Module Communication Function ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research module communication patterns
- [ ] Use `WebSearch` to find production module communication examples
- [ ] Search GitHub for "inter-module communication python" examples
- [ ] Find real-world communication implementations
- [ ] Locate conversation tracking approaches

**Example Starting Code** (to be found via research):
```python
# Agent MUST use perplexity_ask and WebSearch to find:
# 1. Module communication patterns
# 2. Conversation tracking approaches
# 3. Message status management
# 4. Streaming response handling
# Example search queries:
# - "site:github.com python inter-module communication" 
# - "microservice communication patterns python 2025"
# - "conversation tracking state management"
```

**Working Starting Code** (verified working):
```python
def module_ask_module(
    questioner_dir: Path,
    responder_dir: Path,
    question: str,
    system_prompt: str = None,
    timeout: int = 60
) -> Dict[str, Any]:
    # Create conversation thread
    thread_id = conversation_store.create_thread(
        title=f"{questioner_dir.name}-{responder_dir.name} Communication",
        modules=[questioner_dir.name, responder_dir.name],
        metadata={"source": "module_communication"}
    )
    
    # Store question
    question_msg_id = conversation_store.add_message(
        thread_id=thread_id,
        module_name=questioner_dir.name,
        content=question,
        message_type="question",
        status="complete"
    )
    
    # Use default system prompt if none provided
    if system_prompt is None:
        system_prompt = f"""
        You are the {responder_dir.name} module, responsible for providing information
        and services to other modules. Answer the question from {questioner_dir.name}
        module clearly and precisely.
        """
    
    # Execute Claude in responder directory
    proc = execute_claude_in_directory(
        working_dir=str(responder_dir),
        prompt=question,
        system_prompt=system_prompt,
        timeout=timeout
    )
    
    # Process streaming output
    response_msg_id = conversation_store.add_message(
        thread_id=thread_id,
        module_name=responder_dir.name,
        content="",
        message_type="response",
        status="processing"
    )
    
    success, content_chunks, error = parse_claude_json_stream(proc)
    final_content = "".join(content_chunks)
    
    # Update message status
    conversation_store.update_message(
        response_msg_id,
        content=final_content,
        status="complete" if success else "failed",
        metadata={"error": error} if not success else {}
    )
    
    return {
        "success": success,
        "thread_id": thread_id,
        "question_msg_id": question_msg_id,
        "response_msg_id": response_msg_id,
        "content": final_content,
        "error": error if not success else None,
        "conversation": conversation_store.get_thread(thread_id)
    }
```

**Implementation Steps**:
- [ ] 3.1 Create communication function
  - Implement module_ask_module in claude_comms/core/communication.py
  - Support conversation threads
  - Add message tracking
  - Handle errors gracefully
  - Include logging

- [ ] 3.2 Add system prompt management
  - Generate appropriate system prompts
  - Load custom prompts if available
  - Fall back to default prompts
  - Support prompt templating

- [ ] 3.3 Implement conversation store integration
  - Update message status during processing
  - Store streamed content incrementally
  - Add metadata for tracking
  - Support conversation retrieval

- [ ] 3.4 Add error handling and recovery
  - Handle Claude CLI failures
  - Capture and store error information
  - Support retry mechanisms
  - Provide error diagnostics

- [ ] 3.5 Implement status tracking
  - Track message status
  - Report progress
  - Support polling for updates
  - Add completion callbacks

- [ ] 3.6 Create verification report
  - Create `/docs/reports/003_task_3_module_communication.md`
  - Document actual module communication
  - Include real conversation examples
  - Show error handling
  - Add evidence of functionality

- [ ] 3.7 Write unit tests
  - Test with mock modules
  - Test conversation flow
  - Test error conditions
  - Test with real modules

- [ ] 3.8 Git commit feature

**Technical Specifications**:
- Support all module types
- Handle arbitrary directory structures
- Support streaming responses
- Track conversation state
- Provide comprehensive error information

**Verification Method**:
- Test with real module directories
- Verify conversation storage
- Check error handling
- Confirm message tracking
- Test with various questions

**Acceptance Criteria**:
- Successfully communicates between modules
- Stores conversations properly
- Handles errors gracefully
- Provides accurate status tracking
- Documentation complete

### Task 4: Conversation Polling and Status Tracking ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research async status tracking
- [ ] Use `WebSearch` to find production polling implementations
- [ ] Search GitHub for "message status polling" examples
- [ ] Find real-world status tracking systems
- [ ] Locate conversation monitoring approaches

**Implementation Steps**:
- [ ] 4.1 Create polling function
  - Implement message_status_poller in claude_comms/core/polling.py
  - Support configurable polling intervals
  - Add timeout functionality
  - Handle various message statuses
  - Include logging

- [ ] 4.2 Add real-time status updates
  - Report streaming progress
  - Calculate completion percentage
  - Estimate remaining time
  - Provide content previews

- [ ] 4.3 Implement callback mechanism
  - Support status change callbacks
  - Add completion notifications
  - Handle error callbacks
  - Support custom handlers

- [ ] 4.4 Add monitoring dashboard
  - Create simple status display
  - Show active conversations
  - Display message statuses
  - Provide error information

- [ ] 4.5 Add CLI commands
  - Implement status check commands
  - Add conversation listing
  - Support message retrieval
  - Include formatting options

- [ ] 4.6 Create verification report
  - Create `/docs/reports/003_task_4_status_polling.md`
  - Document actual polling examples
  - Include real status updates
  - Show status transition handling
  - Add evidence of functionality

- [ ] 4.7 Write unit tests
  - Test polling functionality
  - Test status transitions
  - Test timeout handling
  - Test with various message states

- [ ] 4.8 Git commit feature

**Acceptance Criteria**:
- Correctly polls for status updates
- Reports progress accurately
- Handles timeouts properly
- Provides useful status information
- Documentation complete

### Task 5: Multi-Module Conversation Orchestration ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research conversation orchestration
- [ ] Use `WebSearch` to find production orchestration examples
- [ ] Search GitHub for "multi-party conversation management" examples
- [ ] Find real-world orchestration implementations
- [ ] Locate conversation routing approaches

**Implementation Steps**:
- [ ] 5.1 Create orchestration service
  - Implement ConversationOrchestrator in claude_comms/orchestration/orchestrator.py
  - Support multiple modules
  - Add conversation routing
  - Handle conversation flow
  - Include logging

- [ ] 5.2 Add module discovery
  - Implement module detection
  - Add capability discovery
  - Support dynamic registration
  - Handle module dependencies

- [ ] 5.3 Implement conversation routing
  - Route questions to appropriate modules
  - Handle multi-module conversations
  - Support conversation branching
  - Manage conversation context

- [ ] 5.4 Add conversation management
  - Track conversation threads
  - Maintain conversation history
  - Support context preservation
  - Implement memory management

- [ ] 5.5 Implement error handling
  - Handle module unavailability
  - Support fallback mechanisms
  - Provide error diagnostics
  - Implement recovery strategies

- [ ] 5.6 Create verification report
  - Create `/docs/reports/003_task_5_orchestration.md`
  - Document actual orchestration examples
  - Include real multi-module conversations
  - Show routing decisions
  - Add evidence of functionality

- [ ] 5.7 Write unit tests
  - Test with mock modules
  - Test routing logic
  - Test error conditions
  - Test with real modules

- [ ] 5.8 Git commit feature

**Acceptance Criteria**:
- Successfully orchestrates multi-module conversations
- Routes messages appropriately
- Maintains conversation context
- Handles errors gracefully
- Documentation complete

### Task 6: CLI Interface Refactoring ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: MEDIUM

**Research Requirements**:
- [ ] Use `perplexity_ask` to research CLI design patterns
- [ ] Use `WebSearch` to find production CLI implementations
- [ ] Search GitHub for "typer python cli" examples
- [ ] Find real-world CLI interface implementations
- [ ] Locate command structuring approaches

**Implementation Steps**:
- [ ] 6.1 Update CLI application
  - Refactor app.py to use new execution approach
  - Update command structure
  - Add new functionality
  - Improve error handling
  - Enhance user feedback

- [ ] 6.2 Add module communication commands
  - Implement ask command
  - Add conversation management
  - Support status tracking
  - Include formatting options

- [ ] 6.3 Implement conversation viewing
  - Add list-conversations command
  - Implement get-conversation
  - Support filtering and sorting
  - Add export functionality

- [ ] 6.4 Add status monitoring
  - Implement status command
  - Add progress tracking
  - Support continuous monitoring
  - Include notification options

- [ ] 6.5 Improve documentation
  - Update command help
  - Add usage examples
  - Include tutorials
  - Provide troubleshooting information

- [ ] 6.6 Create verification report
  - Create `/docs/reports/003_task_6_cli_interface.md`
  - Document actual CLI commands
  - Include real command outputs
  - Show error handling
  - Add evidence of functionality

- [ ] 6.7 Write unit tests
  - Test CLI commands
  - Test parameter handling
  - Test error conditions
  - Test with real scenarios

- [ ] 6.8 Git commit feature

**Acceptance Criteria**:
- All CLI commands function correctly
- Error handling is comprehensive
- Help documentation is clear
- Command structure is intuitive
- Documentation complete

### Task 7: Documentation and Examples ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research documentation best practices
- [ ] Use `WebSearch` to find production documentation examples
- [ ] Search GitHub for "python module documentation" examples
- [ ] Find real-world example implementations
- [ ] Locate tutorial structuring approaches

**Implementation Steps**:
- [ ] 7.1 Update main documentation
  - Update README.md
  - Revise architecture documentation
  - Add implementation details
  - Include security considerations
  - Enhance troubleshooting section

- [ ] 7.2 Create usage guides
  - Write module communication guide
  - Create conversation management tutorial
  - Add CLI usage examples
  - Include configuration guide

- [ ] 7.3 Implement example scripts
  - Create basic module communication example
  - Add multi-module conversation example
  - Implement orchestration example
  - Include error handling example

- [ ] 7.4 Add API documentation
  - Document core functions
  - Add class references
  - Include method documentation
  - Provide type information

- [ ] 7.5 Create diagrams
  - Add architecture diagram
  - Include flow charts
  - Create sequence diagrams
  - Add component diagrams

- [ ] 7.6 Create verification report
  - Create `/docs/reports/003_task_7_documentation.md`
  - Document actual documentation created
  - Include real example outputs
  - Show usage scenarios
  - Add evidence of functionality

- [ ] 7.7 Add tutorials
  - Create getting started tutorial
  - Add advanced usage tutorial
  - Include troubleshooting guide
  - Provide best practices

- [ ] 7.8 Git commit feature

**Acceptance Criteria**:
- Documentation is comprehensive
- Examples are functional
- Diagrams are clear
- API references are complete
- Tutorials are easy to follow

### Task 8: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 8.1 Review all task reports
  - Read all reports in `/docs/reports/003_task_*`
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

- [ ] 8.3 Iterate on incomplete tasks
  - Return to first incomplete task
  - Fix identified issues
  - Re-run validation tests
  - Update verification report
  - Continue until task passes

- [ ] 8.4 Re-validate completed tasks
  - Ensure no regressions from fixes
  - Run integration tests
  - Verify cross-task compatibility
  - Update affected reports
  - Document any new limitations

- [ ] 8.5 Final comprehensive validation
  - Run all CLI commands
  - Execute performance benchmarks
  - Test all integrations
  - Verify documentation accuracy
  - Confirm all features work together

- [ ] 8.6 Create final summary report
  - Create `/docs/reports/003_final_summary.md`
  - Include completion matrix
  - Document all working features
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 8.7 Mark task complete only if ALL sub-tasks pass
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
|-------------------|-------------|---------------|--------------------|
| `module_ask_module` | Have one module ask another module a question | `result = module_ask_module(marker_dir, arangodb_dir, "What schema do you use?")` | Question and response stored in conversation store |
| `execute_claude_in_directory` | Run Claude CLI in a specific directory | `proc = execute_claude_in_directory("/path/to/dir", "prompt", "system prompt")` | Subprocess with Claude running in target directory |
| `parse_claude_json_stream` | Parse streaming JSON from Claude CLI | `success, chunks, error = parse_claude_json_stream(proc)` | Parsed content chunks and status |
| `claude-comms ask` | CLI command to ask a module a question | `claude-comms ask marker arangodb "What schema do you use?"` | Question and response displayed |

## Version Control Plan

- **Initial Commit**: Create task-003-start tag before implementation
- **Feature Commits**: After each major feature
- **Integration Commits**: After component integration  
- **Test Commits**: After test suite completion
- **Final Tag**: Create task-003-complete after all tests pass

## Resources

**Python Packages**:
- subprocess: Process management
- typer: CLI interface
- loguru: Logging
- sqlalchemy: Database storage

**Documentation**:
- [Claude CLI Documentation](https://docs.anthropic.com/claude/docs/claude-cli)
- [Python Subprocess Documentation](https://docs.python.org/3/library/subprocess.html)
- [Typer Documentation](https://typer.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

**Example Implementations**:
- [claude_cli_module_test.py](https://github.com/USERNAME/claude_comms/blob/master/claude_cli_module_test.py)
- [MODULE_COMMUNICATION_SHELL_EXECUTION.md](https://github.com/USERNAME/claude_comms/blob/master/docs/MODULE_COMMUNICATION_SHELL_EXECUTION.md)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All features working, tests passing, documented

## Report Documentation Requirements

Each sub-task MUST have a corresponding verification report in `/docs/reports/` following these requirements:

### Report Structure:
Each report must include:
1. **Task Summary**: Brief description of what was implemented
2. **Research Findings**: Links to repos, code examples found, best practices discovered
3. **Non-Mocked Results**: Real command outputs and performance metrics
4. **Performance Metrics**: Actual benchmarks with real data
5. **Code Examples**: Working code with verified output
6. **Verification Evidence**: Logs or metrics proving functionality
7. **Limitations Found**: Any discovered issues or constraints
8. **External Resources Used**: All GitHub repos, articles, and examples referenced

### Report Naming Convention:
`/docs/reports/003_task_[SUBTASK]_[feature_name].md`

Example content for a report:
```markdown
# Task 3.1: Core Shell Command Execution Verification Report

## Summary
Implemented a robust shell command execution function that correctly sets the directory context for Claude CLI execution.

## Research Findings
- Found pattern X in repo: [link]
- Best practice Y from: [link]
- Security considerations Z from: [article]

## Real Command Outputs
```bash
$ python -c "import claude_comms.core.execution as ex; ex.execute_claude_in_directory('/home/user/module', 'Test prompt', 'Test system prompt')"
Running command: cd /home/user/module && timeout 60s claude --system-prompt "Test system prompt" -p "Test prompt" --output-format stream-json --verbose
Process started with PID: 12345
```

## Actual Performance Results
| Operation | Metric | Result | Target | Status |
|-----------|--------|--------|--------|--------|
| Command setup | Time | 3.2ms | <100ms | PASS |
| Process start | Time | 12.5ms | <50ms | PASS |

## Working Code Example
```python
# Actual tested code
from claude_comms.core.execution import execute_claude_in_directory

proc = execute_claude_in_directory(
    working_dir="/home/user/module",
    prompt="What is your purpose?",
    system_prompt="You are a helpful assistant",
    timeout=30
)
# Successfully started process in /home/user/module
```

## Verification Evidence
- Command executed successfully
- Process started in correct directory
- Timeout properly applied
- Quotes correctly escaped

## Limitations Discovered
- Directory must exist and be readable
- System prompt has 4000 token limit
- Shell command must be properly escaped

## External Resources Used
- [Python Subprocess Docs](https://docs.python.org/3/library/subprocess.html)
- [Claude CLI GitHub](https://github.com/anthropics/claude-cli)
- [Shell Command Security Best Practices](https://link-to-article)
```

## Context Management

When context length is running low during implementation, use the following approach to compact and resume work:

1. Issue the `/compact` command to create a concise summary of current progress
2. The summary will include:
   - Completed tasks and key functionality
   - Current task in progress with specific subtask
   - Known issues or blockers
   - Next steps to resume work
   - Key decisions made or patterns established

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.