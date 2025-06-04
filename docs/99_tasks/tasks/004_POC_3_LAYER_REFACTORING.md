# Task 004: POC 3-Layer Architecture Refactoring ⏳ Not Started

**Objective**: Refactor the working POC `orchestrator_cli.py` into a clean 3-layer architecture following established project standards and patterns, enabling better maintainability, testability, and extensibility.

**Requirements**:
1. Extract core business logic into independently testable functions
2. Create a clean CLI layer using Typer with rich formatting
3. Implement MCP integration layer for Claude tools
4. Maintain all existing functionality while improving structure
5. Add comprehensive validation and error handling
6. Follow CLAUDE.md coding standards throughout
7. Ensure all code is under 500 lines per file
8. Provide real data validation for all functions

## Overview

The current POC (`src/claude_comms/poc/orchestrator_cli.py`) is a working 450-line monolithic script that successfully handles:
- Claude CLI subprocess execution with streaming output
- Real-time SQLite progress tracking
- JSON stream parsing from Claude's `--output-format stream-json`
- Live progress display with status updates
- Comprehensive logging with loguru
- Error handling and subprocess management
- Simulation mode for testing

This refactoring will preserve all functionality while creating a maintainable, extensible architecture.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

Analysis of the POC reveals:
- Single-command CLI using `@app.callback()` with `invoke_without_command=True`
- Comprehensive subprocess management with proper error handling
- Real-time database updates with SQLite thread safety
- Stream processing of JSON output from Claude CLI
- Dual logging (console INFO, file DEBUG) with loguru
- Simulation mode for testing without actual Claude calls

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Current Python subprocess best practices (2025-current)
   - SQLite thread safety patterns for real-time updates
   - JSON streaming processing optimization techniques
   - Typer CLI architecture patterns for complex applications

2. **Use `WebSearch`** to find:
   - GitHub repositories with working subprocess management
   - Real production examples of CLI refactoring
   - Popular patterns for database progress tracking
   - Stream processing implementations

3. **Document all findings** in task reports:
   - Links to source repositories with working code
   - Performance characteristics of different approaches
   - Integration patterns that work in production
   - Best practices for error handling

4. **DO NOT proceed without research**:
   - No theoretical refactoring approaches
   - Must have real code examples to follow
   - Must verify current best practices
   - Must understand performance implications

Example Research Queries:
```
perplexity_ask: "python subprocess streaming json processing best practices 2025"
WebSearch: "site:github.com python cli typer architecture patterns production"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Create Core Layer - Database and Progress Management ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to find SQLite real-time update patterns
- [ ] Use `WebSearch` to find production database progress tracking
- [ ] Search GitHub for "python sqlite progress tracking" examples
- [ ] Find real-world task status management strategies
- [ ] Locate performance benchmarking code for database operations

**Working Starting Code** (from POC analysis):
```python
# Core functionality to extract from orchestrator_cli.py:
def create_database(db_path_str: str, progress_id_for_log: str):
    # Lines 32-56 from POC
def insert_progress_record(conn, progress_id, prompt, requester, responder_module, target_dir_str, system_prompt_file_str):
    # Lines 58-71 from POC
def update_progress_in_db(conn, progress_id, status, content_to_set=None, increment_chunk=False):
    # Lines 73-102 from POC
```

**Implementation Steps**:
- [ ] 1.1 Create core infrastructure
  - Create `/src/claude_comms/core/` directory structure
  - Create `database_manager.py` for all DB operations
  - Create `progress_tracker.py` for progress state management
  - Create `task_manager.py` for task lifecycle
  - Add dependencies to pyproject.toml if needed

- [ ] 1.2 Implement database management functions
  - Extract and refactor `create_database()` function
  - Extract and refactor `insert_progress_record()` function
  - Extract and refactor `update_progress_in_db()` function
  - Add connection pooling and thread safety
  - Include comprehensive error handling
  - Add logging throughout

- [ ] 1.3 Implement progress tracking functions
  - Create `ProgressTracker` class for state management
  - Add methods for status updates and chunk counting
  - Implement thread-safe operations
  - Add validation for status transitions
  - Include progress calculation utilities

- [ ] 1.4 Implement task management functions
  - Create `TaskManager` class for task lifecycle
  - Add task creation, execution, and completion methods
  - Implement task ID generation and management
  - Add task metadata handling
  - Include cleanup and resource management

- [ ] 1.5 Add validation methods for all functions
  - Create test fixtures with real SQLite databases
  - Test concurrent access scenarios
  - Validate performance with multiple tasks
  - Test error recovery and rollback
  - Measure database operation timings

- [ ] 1.6 Create verification report
  - Create `/docs/reports/004_task_1_core_database.md`
  - Document actual database operations and timing
  - Include real performance benchmarks
  - Show working code examples with output
  - Add evidence of thread safety

- [ ] 1.7 Test with real database operations
  - Test with concurrent task creation
  - Validate progress updates in real-time
  - Check database integrity under load
  - Verify error handling and recovery
  - Test with various data types and sizes

- [ ] 1.8 Git commit core database layer

**Technical Specifications**:
- Performance target: <10ms for database operations
- Concurrency: Support 10+ concurrent tasks
- Reliability: >99.9% operation success rate
- Error recovery: Automatic retry with exponential backoff
- Database file size: Efficient storage with regular cleanup

**Verification Method**:
- Run concurrent database operations
- Measure operation timing and success rates
- Check database integrity after stress testing
- Verify thread safety with multiple processes
- CLI testing with actual database file creation

**CLI Testing Requirements** (MANDATORY FOR ALL TASKS):
- [ ] Execute actual database operations, not mocked tests
  - Create real SQLite databases with multiple tasks
  - Test concurrent access from multiple processes
  - Verify data integrity after operations
  - Document exact operations performed
  - Capture and verify actual performance metrics
- [ ] Test end-to-end database functionality
  - Start with empty database creation
  - Verify task insertion and updates
  - Confirm progress tracking accuracy
  - Test error scenarios and recovery
- [ ] Document all database tests in report
  - Include exact operations executed
  - Show actual data stored and retrieved
  - Note any performance issues
  - Verify against expected database schema

**Acceptance Criteria**:
- All database functions work with real SQLite files
- Performance meets timing targets
- Thread safety verified with concurrent access
- Error handling tested with actual failures
- Documentation complete with examples

### Task 2: Create Core Layer - Subprocess Management ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to find Python subprocess streaming best practices
- [ ] Use `WebSearch` to find production subprocess management examples  
- [ ] Search GitHub for "python subprocess json streaming" implementations
- [ ] Find real-world Claude CLI integration patterns
- [ ] Locate subprocess error handling and recovery code

**Working Starting Code** (from POC analysis):
```python
# Core subprocess functionality to extract:
# Lines 262-380 from orchestrator_cli.py - subprocess execution and streaming
process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, cwd=subprocess_cwd)
for line in iter(process.stdout.readline, ''):
    # JSON parsing and content extraction
    data = json.loads(stripped_line)
    # Process different message types
```

**Implementation Steps**:
- [ ] 2.1 Create subprocess management infrastructure
  - Create `subprocess_manager.py` for all subprocess operations
  - Create `stream_processor.py` for JSON stream handling
  - Create `command_builder.py` for Claude CLI command construction
  - Add error handling and recovery mechanisms
  - Include comprehensive logging

- [ ] 2.2 Implement subprocess execution functions
  - Extract subprocess creation and management logic
  - Add proper process lifecycle management
  - Implement stream reading with error handling
  - Add timeout and resource cleanup
  - Include process monitoring and health checks

- [ ] 2.3 Implement JSON stream processing
  - Create stream parser for Claude's JSON output format
  - Handle different message types (assistant, system, result)
  - Extract text chunks and assemble content
  - Add validation for JSON structure
  - Include error recovery for malformed JSON

- [ ] 2.4 Implement command building utilities
  - Create Claude CLI command construction functions
  - Handle different execution modes (actual vs simulation)
  - Add system prompt integration
  - Include parameter validation and escaping
  - Add command logging and debugging support

- [ ] 2.5 Add validation methods for subprocess functions
  - Test with actual Claude CLI execution
  - Validate stream processing with real JSON output
  - Test error scenarios and recovery
  - Measure performance and resource usage
  - Verify process cleanup and resource management

- [ ] 2.6 Create verification report
  - Create `/docs/reports/004_task_2_subprocess_management.md`
  - Document actual subprocess operations and performance
  - Include real Claude CLI execution examples
  - Show working stream processing with output
  - Add evidence of proper resource management

- [ ] 2.7 Test with real Claude CLI integration
  - Test with actual Claude executable
  - Validate JSON stream processing
  - Check error handling with various failure modes
  - Verify resource cleanup after completion
  - Test simulation mode compatibility

- [ ] 2.8 Git commit subprocess management layer

**Technical Specifications**:
- Performance target: <100ms subprocess startup time
- Streaming: Process JSON chunks in real-time with <50ms latency
- Resource management: 100% process cleanup success rate
- Error handling: Graceful recovery from subprocess failures
- Memory usage: <50MB for stream processing

**Verification Method**:
- Execute actual Claude CLI commands
- Process real JSON streams from Claude output
- Measure subprocess startup and execution time
- Verify resource cleanup with process monitoring
- Test error scenarios with actual failures

**Acceptance Criteria**:
- Subprocess management works with actual Claude CLI
- JSON stream processing handles all message types
- Error handling tested with real failure scenarios
- Resource cleanup verified with process monitoring
- Performance meets timing and memory targets

### Task 3: Create CLI Layer - Typer Application and Formatters ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: MEDIUM

**Research Requirements**:
- [ ] Use `perplexity_ask` to find Typer CLI architecture patterns
- [ ] Use `WebSearch` to find production Typer applications
- [ ] Search GitHub for "typer rich formatting" examples
- [ ] Find real-world CLI validation patterns
- [ ] Locate Typer callback vs command best practices

**Working Starting Code** (from POC analysis):
```python
# CLI structure to refactor from orchestrator_cli.py:
app = typer.Typer(help="CLI for inter-module communication using Claude", invoke_without_command=True)
@app.callback()
def run_claude_communication(ctx: typer.Context, prompt: str = typer.Option(...), ...):
    # Lines 122-445 - main CLI logic
```

**Implementation Steps**:
- [ ] 3.1 Create CLI layer infrastructure
  - Create `/src/claude_comms/cli/` directory structure  
  - Create `app.py` for main Typer application
  - Create `formatters.py` for Rich-based output formatting
  - Create `validators.py` for input validation functions
  - Create `schemas.py` for Pydantic models

- [ ] 3.2 Implement main Typer application
  - Extract CLI parameter definitions from POC
  - Implement clean command structure using callback pattern
  - Add comprehensive help text and documentation
  - Integrate with core layer functions
  - Include proper error handling and user feedback

- [ ] 3.3 Implement Rich-based formatters
  - Create progress display formatters
  - Add status update formatting with colors and icons
  - Implement table formatters for task summaries
  - Create error message formatting
  - Add JSON pretty-printing utilities

- [ ] 3.4 Implement input validators
  - Create path validation functions
  - Add system prompt file validation
  - Implement database path validation
  - Create Claude executable validation
  - Add parameter combination validation

- [ ] 3.5 Implement Pydantic schemas
  - Create data models for task configuration
  - Add progress state models
  - Implement validation rules for all inputs
  - Create response models for CLI outputs
  - Add serialization/deserialization support

- [ ] 3.6 Add validation methods for CLI functions
  - Test CLI with actual command execution
  - Validate all parameter combinations
  - Test error handling with invalid inputs
  - Verify Rich formatting output
  - Test help system and documentation

- [ ] 3.7 Create verification report
  - Create `/docs/reports/004_task_3_cli_layer.md`
  - Document actual CLI command executions
  - Include screenshots of Rich formatting
  - Show working validation examples
  - Add evidence of proper help system

- [ ] 3.8 Test CLI integration with core layer
  - Test complete CLI workflow
  - Validate parameter passing to core functions
  - Check error propagation and display
  - Verify output formatting and user experience
  - Test all CLI options and combinations

- [ ] 3.9 Git commit CLI layer

**Technical Specifications**:
- CLI startup time: <200ms
- Help system: Complete documentation for all options
- Validation: 100% input validation coverage
- User experience: Clear error messages and progress feedback
- Rich formatting: Consistent visual design throughout

**Verification Method**:
- Execute CLI commands with all parameter combinations
- Test help system completeness
- Validate error message clarity and usefulness
- Verify Rich formatting visual consistency
- Test CLI responsiveness and performance

**Acceptance Criteria**:
- CLI application works with all POC functionality
- Rich formatting provides clear user feedback
- Input validation prevents all common errors
- Help system is comprehensive and useful
- Performance meets responsiveness targets

### Task 4: Create MCP Layer - FastMCP Integration ⏳ Not Started

**Priority**: LOW | **Complexity**: HIGH | **Impact**: MEDIUM

**Research Requirements**:
- [ ] Use `perplexity_ask` to find FastMCP integration patterns
- [ ] Use `WebSearch` to find production MCP implementations
- [ ] Search GitHub for "fastmcp python tools" examples
- [ ] Find real-world Claude tools integration
- [ ] Locate MCP schema definition best practices

**Implementation Steps**:
- [ ] 4.1 Create MCP layer infrastructure
  - Create `/src/claude_comms/mcp/` directory structure
  - Create `schema.py` for JSON schema definitions
  - Create `wrapper.py` for FastMCP integration
  - Create `handlers.py` for MCP request handlers
  - Add MCP dependencies to pyproject.toml

- [ ] 4.2 Implement JSON schemas for MCP
  - Define input schemas for all CLI parameters
  - Create output schemas for task results
  - Add error response schemas
  - Implement progress update schemas
  - Include validation rules and descriptions

- [ ] 4.3 Implement FastMCP wrapper
  - Create MCP server configuration
  - Add tool registration for Claude communication
  - Implement request/response handling
  - Add error handling and validation
  - Include logging and debugging support

- [ ] 4.4 Implement MCP request handlers
  - Create handlers for each CLI command
  - Add parameter mapping between MCP and core
  - Implement response formatting
  - Add progress streaming support
  - Include error transformation

- [ ] 4.5 Add validation methods for MCP functions
  - Test MCP server startup and registration
  - Validate schema definitions with real data
  - Test handler functions with actual requests
  - Verify error handling and responses
  - Test integration with Claude tools

- [ ] 4.6 Create verification report
  - Create `/docs/reports/004_task_4_mcp_layer.md`
  - Document actual MCP server operations
  - Include real tool registration examples
  - Show working handler responses
  - Add evidence of Claude tools integration

- [ ] 4.7 Test MCP integration end-to-end
  - Test MCP server with actual Claude tools
  - Validate schema compliance
  - Check handler function correctness
  - Verify error handling and recovery
  - Test performance under load

- [ ] 4.8 Git commit MCP layer

**Technical Specifications**:
- MCP startup time: <500ms
- Schema validation: 100% request validation
- Handler performance: <100ms response time
- Error handling: Comprehensive error responses
- Claude integration: Full tool compatibility

**Verification Method**:
- Start MCP server and register tools
- Execute requests through Claude tools interface
- Validate schema compliance with real data
- Test error scenarios and responses
- Measure performance and reliability

**Acceptance Criteria**:
- MCP server integrates with Claude tools
- All schemas validate correctly
- Handler functions work with real requests
- Error handling provides useful feedback
- Performance meets responsiveness targets

### Task 5: Integration and Module Exports ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: HIGH

**Implementation Steps**:
- [ ] 5.1 Update main module `__init__.py`
  - Import and export core functionality
  - Add version information and metadata
  - Create high-level usage examples
  - Include backwards compatibility
  - Add module documentation

- [ ] 5.2 Create unified entry points
  - Update pyproject.toml with new CLI entry point
  - Ensure backwards compatibility with POC entry point
  - Add MCP server entry point
  - Test all entry points work correctly
  - Update installation documentation

- [ ] 5.3 Add integration testing
  - Create end-to-end tests with real Claude CLI
  - Test database integration with actual files
  - Validate MCP integration if implemented
  - Test error scenarios and recovery
  - Verify performance under realistic conditions

- [ ] 5.4 Update documentation
  - Update README with new architecture
  - Create usage examples for each layer
  - Document migration from POC
  - Add troubleshooting guide
  - Include performance characteristics

- [ ] 5.5 Create verification report
  - Create `/docs/reports/004_task_5_integration.md`
  - Document actual integration testing results
  - Include performance benchmarks
  - Show working examples of all layers
  - Add evidence of backwards compatibility

- [ ] 5.6 Test complete system integration
  - Run full workflow with all layers
  - Test backwards compatibility with POC usage
  - Validate performance matches POC
  - Check error handling throughout system
  - Verify all functionality preserved

- [ ] 5.7 Git commit integration updates

**Acceptance Criteria**:
- All layers integrate seamlessly
- POC functionality fully preserved
- Performance equals or exceeds POC
- Entry points work correctly
- Documentation is complete and accurate

### Task 6: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 6.1 Review all task reports
  - Read all reports in `/docs/reports/004_task_*`
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
  - Verify cross-layer compatibility
  - Update affected reports
  - Document any new limitations

- [ ] 6.5 Final comprehensive validation
  - Run all CLI commands with actual data
  - Execute performance benchmarks
  - Test all integrations
  - Verify documentation accuracy
  - Confirm all POC features work

- [ ] 6.6 Create final summary report
  - Create `/docs/reports/004_final_summary.md`
  - Include completion matrix
  - Document all working features
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 6.7 Mark task complete only if ALL sub-tasks pass
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
| `claude-comms-refactored` | Execute refactored CLI | `claude-comms-refactored --prompt "test" --target-dir "."` | Task execution with progress |
| `Database.create()` | Create task database | `db = Database.create("test.db")` | SQLite database created |
| `ProgressTracker.update()` | Update task progress | `tracker.update("running", content="...")` | Progress updated in DB |
| `SubprocessManager.execute()` | Execute Claude CLI | `manager.execute(cmd_list, cwd=target_dir)` | Subprocess executed |
| `StreamProcessor.parse()` | Parse JSON stream | `processor.parse(json_line)` | Structured data extracted |

## Version Control Plan

- **Initial Commit**: Create task-004-start tag before implementation
- **Core Commits**: After each layer implementation
- **Integration Commits**: After layer integration
- **Test Commits**: After comprehensive testing
- **Final Tag**: Create task-004-complete after all tests pass

## Resources

**Python Packages**:
- typer: CLI framework
- rich: Console formatting
- loguru: Logging
- sqlite3: Database operations
- subprocess: Process management
- pydantic: Data validation
- fastmcp: MCP integration (optional)

**Documentation**:
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

**Example Implementations**:
- Current POC: `src/claude_comms/poc/orchestrator_cli.py`
- CLI Entry Point: `claude-comms-poc-cli` in pyproject.toml
- Working Command: See `cli_terminal_command.md`

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All POC features working in 3-layer architecture

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
`/docs/reports/004_task_[SUBTASK]_[feature_name].md`

Example content for a report:
```markdown
# Task 004.1: Core Database Layer Verification Report

## Summary
Implemented core database management layer with SQLite operations, progress tracking, and thread-safe concurrent access.

## Research Findings
- Found SQLite thread safety pattern in repo: [link]
- Best practice for progress tracking from: [link]
- Performance optimization techniques from: [article]

## Real Command Outputs
```bash
$ python -c "from claude_comms.core.database_manager import DatabaseManager; db = DatabaseManager.create('test.db'); print('Database created successfully')"
Database created successfully
$ sqlite3 test.db ".tables"
progress
$ python -c "import time; from claude_comms.core.database_manager import DatabaseManager; db = DatabaseManager.create('test.db'); start=time.time(); db.insert_progress_record('test-id', 'test prompt', 'Marker', 'ArangoDB', '/tmp', None); print(f'Insert time: {time.time()-start:.3f}s')"
Insert time: 0.008s
```

## Actual Performance Results
| Operation | Metric | Result | Target | Status |
|-----------|--------|--------|--------|--------|
| Database creation | Time | 5.2ms | <10ms | PASS |
| Record insertion | Time | 8.1ms | <10ms | PASS |
| Progress update | Time | 6.8ms | <10ms | PASS |
| Concurrent access | Success rate | 100% | >99.9% | PASS |

## Working Code Example
```python
# Actual tested code
from claude_comms.core.database_manager import DatabaseManager
import time

# Test database creation and operations
db = DatabaseManager.create("test.db")
start_time = time.time()
db.insert_progress_record("task-123", "test prompt", "Marker", "ArangoDB", "/tmp", None)
insert_time = time.time() - start_time
print(f"Insert completed in {insert_time:.3f}s")
# Output:
# Insert completed in 0.008s
```

## Verification Evidence
- Database file created successfully
- All operations completed within timing targets
- Thread safety verified with concurrent testing
- Error handling tested with invalid inputs

## Limitations Discovered
- Large content updates (>1MB) show slower performance
- Concurrent access limited to 50 simultaneous connections

## External Resources Used
- [SQLite Python Threading](https://github.com/example/sqlite-threading) - Thread safety patterns
- [Progress Tracking Examples](https://github.com/example/progress) - Real-time updates
- [Performance Optimization](https://article.example.com) - Database tuning techniques
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