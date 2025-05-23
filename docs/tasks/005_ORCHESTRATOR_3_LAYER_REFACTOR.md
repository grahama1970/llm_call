# Task 005: Orchestrator CLI 3-Layer Architecture Refactor ⏳ Not Started

**Objective**: Refactor the working POC `orchestrator_cli.py` into a clean 3-layer architecture following the specific breakdown provided, preserving ALL functionality while improving maintainability and extensibility.

**Requirements**:
1. Extract core business logic into `core/` layer with pure functions
2. Create CLI layer in `cli/` with Typer and Rich formatting
3. Implement optional MCP layer for Claude tools integration
4. Preserve POC directory completely untouched as reference
5. Maintain all existing functionality (database tracking, streaming, logging)
6. Follow CLAUDE.md coding standards (500 lines max, validation functions)
7. Create new entry points while preserving existing POC entry point

## Overview

The current POC (`src/claude_comms/poc/orchestrator_cli.py`) is a working 450-line script that will be refactored using the specific layer breakdown provided. The POC will remain completely untouched as a working reference.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.
3. **NEVER MODIFY POC FILES** - Only create new files in new directories

## Research Summary

Specific refactoring approach based on analysis:
- Extract Claude execution and streaming into `core/claude_executor.py`
- Extract database operations into `core/db_manager.py` 
- Move CLI logic to `cli/app.py` with formatters in `cli/formatters.py`
- Preserve all POC functionality while improving structure

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Python generator patterns for streaming data (2025-current)
   - SQLite connection management best practices
   - Typer CLI refactoring patterns
   - JSON stream processing optimization

2. **Use `WebSearch`** to find:
   - GitHub repositories with subprocess streaming generators
   - Real production examples of CLI layer separation
   - Database manager patterns in Python applications
   - Stream processing with yield patterns

3. **Document all findings** in task reports:
   - Links to source repositories with working generator code
   - Performance characteristics of streaming approaches
   - Best practices for subprocess management
   - Error handling patterns in production code

4. **DO NOT proceed without research**:
   - Must have real examples of generator-based streaming
   - Must verify subprocess management patterns
   - Must understand error handling approaches
   - Must see production CLI refactoring examples

Example Research Queries:
```
perplexity_ask: "python subprocess streaming generator yield patterns best practices 2025"
WebSearch: "site:github.com python cli typer layer separation production"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Create Core Layer - Claude Executor ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to find Python generator streaming patterns
- [ ] Use `WebSearch` to find subprocess streaming implementations
- [ ] Search GitHub for "python subprocess json generator" examples
- [ ] Find real-world Claude CLI integration patterns
- [ ] Locate streaming error handling and recovery code

**Working Starting Code** (to extract from POC):
```python
# From orchestrator_cli.py lines 229-233, 262-380
cmd_list = [str(claude_exe_path_obj), "-p", prompt, "--output-format", "stream-json"]
process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, cwd=subprocess_cwd)
for line in iter(process.stdout.readline, ''):
    data = json.loads(stripped_line)
    # Process different message types
```

**Implementation Steps**:
- [ ] 1.1 Create core infrastructure
  - Create `/src/claude_comms/core/` directory
  - Create `claude_executor.py` file
  - Create `__init__.py` with proper exports
  - Add comprehensive docstring header with purpose, links, sample I/O

- [ ] 1.2 Implement `construct_claude_command()` function
  - Extract command building logic from POC lines 222-254
  - Input: prompt, system_prompt_content, claude_exe_path, verbose_claude_flag
  - Output: List of command arguments for subprocess.Popen
  - Add validation for all parameters
  - Include simulation mode support
  - Add logging and error handling

- [ ] 1.3 Implement `run_claude_and_stream_output()` generator function
  - Extract streaming logic from POC lines 262-380
  - Input: command list, target_cwd
  - Output: Generator yielding structured events:
    - `{"type": "chunk", "data": "text_chunk"}`
    - `{"type": "event", "event_type": "init", "details": {...}}`
    - `{"type": "final_result", "data": "..."}`
    - `{"type": "error", "details": "..."}`
  - Handle subprocess.Popen and line-by-line reading
  - Parse JSON and structure events
  - Include proper error handling and cleanup

- [ ] 1.4 Add comprehensive validation in main block
  - Test with actual Claude CLI executable
  - Validate command construction with various parameters
  - Test streaming generator with real Claude output
  - Test error scenarios and recovery
  - Test simulation mode functionality
  - Verify resource cleanup after subprocess completion

- [ ] 1.5 Create verification report
  - Create `/docs/reports/005_task_1_claude_executor.md`
  - Document actual Claude CLI executions
  - Include real streaming output examples
  - Show generator event structures
  - Add performance metrics for streaming

- [ ] 1.6 Test integration with actual Claude CLI
  - Test command construction with real parameters
  - Execute streaming with actual Claude processes
  - Validate JSON parsing of real Claude output
  - Test error handling with process failures
  - Verify memory usage during streaming

- [ ] 1.7 Git commit claude executor core

**Technical Specifications**:
- Generator latency: <50ms per yielded event
- Memory usage: <10MB for streaming buffer
- Error recovery: Handle malformed JSON gracefully
- Process cleanup: 100% subprocess resource cleanup
- Command validation: Prevent injection attacks

**Verification Method**:
- Execute actual Claude CLI commands
- Process real JSON streams from Claude
- Measure generator performance and memory usage
- Test error scenarios with actual failures
- Verify subprocess cleanup with process monitoring

**CLI Testing Requirements** (MANDATORY):
- [ ] Execute actual Claude CLI subprocess calls
  - Test command construction with real parameters
  - Validate streaming output parsing
  - Test error handling with actual process failures
  - Document exact commands executed
  - Capture and verify streaming performance
- [ ] Test generator functionality end-to-end
  - Validate all event types are properly yielded
  - Test with various Claude CLI output formats
  - Verify proper error propagation
  - Test resource cleanup after completion

**Acceptance Criteria**:
- Command construction works with all POC parameters
- Generator streams real Claude CLI output correctly
- All event types properly structured and yielded
- Error handling tested with actual subprocess failures
- Performance meets latency and memory targets

### Task 2: Create Core Layer - Database Manager ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to find SQLite connection pooling patterns
- [ ] Use `WebSearch` to find production database manager examples
- [ ] Search GitHub for "python sqlite progress tracking" implementations
- [ ] Find real-world database abstraction patterns
- [ ] Locate thread-safe database operation examples

**Working Starting Code** (to extract from POC):
```python
# From orchestrator_cli.py lines 32-102
def create_database(db_path_str: str, progress_id_for_log: str):
def insert_progress_record(conn, progress_id, prompt, requester, responder_module, target_dir_str, system_prompt_file_str):
def update_progress_in_db(conn, progress_id, status, content_to_set=None, increment_chunk=False):
```

**Implementation Steps**:
- [ ] 2.1 Create database manager infrastructure
  - Create `db_manager.py` in `/src/claude_comms/core/`
  - Add comprehensive docstring with purpose, SQLite links, sample I/O
  - Include database schema documentation
  - Add connection management utilities

- [ ] 2.2 Implement `create_database(db_path)` function
  - Extract and refactor from POC lines 32-56
  - Input: database file path
  - Output: database connection object
  - Add table creation with proper schema
  - Include error handling for file/permission issues
  - Add logging for database operations

- [ ] 2.3 Implement `insert_initial_task_record()` function
  - Extract and refactor from POC lines 58-71
  - Input: conn, progress_id, prompt, requester, responder, target_dir, system_prompt_file
  - Output: success/failure indicator
  - Add parameter validation
  - Include comprehensive error handling
  - Add transaction support

- [ ] 2.4 Implement `update_task_progress()` function
  - Refine from POC lines 73-102
  - Input: conn, progress_id, status, content=None, new_chunk_received=False
  - Output: success indicator
  - Handle chunk count increment logic
  - Add validation for status transitions
  - Include atomic updates with transactions

- [ ] 2.5 Implement `get_task_details()` function
  - New function for retrieving task state
  - Input: conn, progress_id
  - Output: task details dictionary
  - Include error handling for missing records
  - Add caching for performance
  - Support partial record retrieval

- [ ] 2.6 Add comprehensive validation in main block
  - Test database creation with real files
  - Test record insertion with various data
  - Test progress updates with concurrent access
  - Test task detail retrieval
  - Test error scenarios and recovery
  - Measure database operation performance

- [ ] 2.7 Create verification report
  - Create `/docs/reports/005_task_2_db_manager.md`
  - Document actual database operations
  - Include performance benchmarks
  - Show working examples with real data
  - Add thread safety verification

- [ ] 2.8 Test database operations thoroughly
  - Test with concurrent database access
  - Validate data integrity after operations
  - Test error recovery and rollback
  - Verify performance under load
  - Test with various data sizes

- [ ] 2.9 Git commit database manager core

**Technical Specifications**:
- Operation latency: <10ms for standard operations
- Concurrency: Support 20+ concurrent connections
- Data integrity: ACID compliance for all operations
- Error recovery: Automatic retry with exponential backoff
- Connection pooling: Efficient resource management

**Verification Method**:
- Execute real database operations
- Test concurrent access scenarios
- Measure performance under various loads
- Validate data consistency after operations
- Test error handling with actual database failures

**Acceptance Criteria**:
- All database functions work with real SQLite files
- Performance meets timing requirements
- Concurrent access handled safely
- Error recovery tested with actual failures
- Data integrity maintained under all conditions

### Task 3: Create CLI Layer - Application and Formatters ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to find Typer command refactoring patterns
- [ ] Use `WebSearch` to find production CLI layer separation examples
- [ ] Search GitHub for "typer rich formatting production" implementations
- [ ] Find real-world CLI application architecture patterns
- [ ] Locate progress display and formatting best practices

**Working Starting Code** (to extract from POC):
```python
# From orchestrator_cli.py lines 26-29, 122-445
app = typer.Typer(help="CLI for inter-module communication using Claude", invoke_without_command=True)
@app.callback()
def run_claude_communication(ctx: typer.Context, ...):
def display_cli_progress(progress_id, status, chunk_count, elapsed_time, requester, responder):
```

**Implementation Steps**:
- [ ] 3.1 Create CLI layer infrastructure
  - Create `/src/claude_comms/cli/` directory
  - Create `app.py` for main Typer application
  - Create `formatters.py` for Rich-based formatting
  - Create `__init__.py` with proper exports
  - Add comprehensive docstrings for all modules

- [ ] 3.2 Implement main Typer application in `app.py`
  - Extract CLI structure from POC lines 26-29, 122-445
  - Create `@app.command("launch-claude")` function
  - Parse CLI arguments using Typer (preserve all POC options)
  - Initialize Loguru logging (extract from POC lines 140-166)
  - Generate progress_id and handle task lifecycle
  - Integrate with core layer functions (db_manager, claude_executor)

- [ ] 3.3 Implement main execution flow in `run_claude_communication()`
  - Call `core.db_manager.create_database` and `insert_initial_task_record`
  - Read system prompt file content (POC lines 208-220)
  - Call `core.claude_executor.construct_claude_command`
  - Iterate through `core.claude_executor.run_claude_and_stream_output`
  - Handle event types from generator:
    - Update content_chunks locally
    - Call `core.db_manager.update_task_progress`
    - Call `cli.formatters.display_cli_progress`
  - Handle finalization and final status updates
  - Log task summary and print final results

- [ ] 3.4 Implement Rich formatters in `formatters.py`
  - Extract `display_cli_progress` from POC lines 104-119
  - Input: structured data (progress_id, status, chunk_count, elapsed_time, requester, responder)
  - Output: formatted console display using loguru
  - Add Rich-based progress bars and status indicators
  - Include error formatting and success indicators
  - Add JSON pretty-printing utilities

- [ ] 3.5 Add comprehensive validation in main blocks
  - Test CLI with all parameter combinations
  - Validate integration with core layer functions
  - Test error handling and user feedback
  - Test Rich formatting output
  - Verify logging configuration and output

- [ ] 3.6 Create verification report
  - Create `/docs/reports/005_task_3_cli_layer.md`
  - Document actual CLI command executions
  - Include screenshots/examples of Rich formatting
  - Show integration with core layer
  - Add performance metrics for CLI responsiveness

- [ ] 3.7 Test CLI application thoroughly
  - Test all CLI options and combinations
  - Validate integration with core functions
  - Test error scenarios and user feedback
  - Verify Rich formatting consistency
  - Test help system and documentation

- [ ] 3.8 Git commit CLI layer

**Technical Specifications**:
- CLI startup time: <200ms
- Rich formatting: Consistent visual design
- Error handling: Clear user feedback for all errors
- Integration: Seamless communication with core layer
- Logging: Proper dual-layer configuration

**Verification Method**:
- Execute CLI with all parameter combinations
- Test integration with core layer functions
- Validate Rich formatting visual output
- Test error handling and user experience
- Measure CLI responsiveness and performance

**Acceptance Criteria**:
- CLI preserves all POC functionality
- Rich formatting provides clear progress feedback
- Integration with core layer works seamlessly
- Error handling gives clear user guidance
- Performance meets responsiveness targets

### Task 4: Create Optional Search Functionality ⏳ Not Started

**Priority**: LOW | **Complexity**: LOW | **Impact**: MEDIUM

**Research Requirements**:
- [ ] Use `perplexity_ask` to find SQLite query patterns for search
- [ ] Use `WebSearch` to find CLI search command implementations
- [ ] Search GitHub for "typer table display rich" examples
- [ ] Find database search and filtering patterns
- [ ] Locate CLI table formatting best practices

**Implementation Steps**:
- [ ] 4.1 Add search functionality to database manager
  - Add `search_tasks()` function to `core/db_manager.py`
  - Input: search criteria (status, requester, keywords, date range)
  - Output: list of matching task records
  - Support SQL-based filtering and sorting
  - Add pagination for large result sets
  - Include performance optimization for searches

- [ ] 4.2 Add search command to CLI
  - Add `@app.command("search-tasks")` to `cli/app.py`
  - Support filtering by status, requester, responder, keywords
  - Add date range filtering and sorting options
  - Include result limiting and pagination
  - Add export options for search results

- [ ] 4.3 Add search result formatting
  - Add search result formatters to `cli/formatters.py`
  - Create Rich table display for search results
  - Add summary statistics for searches
  - Include export formatting (JSON, CSV)
  - Add color coding for different statuses

- [ ] 4.4 Add comprehensive validation
  - Test search with various criteria combinations
  - Validate table formatting with different result sizes
  - Test performance with large databases
  - Test export functionality
  - Verify search accuracy and completeness

- [ ] 4.5 Create verification report
  - Create `/docs/reports/005_task_4_search_functionality.md`
  - Document search command usage examples
  - Include table formatting screenshots
  - Show performance metrics for large searches
  - Add examples of all search criteria

- [ ] 4.6 Git commit search functionality

**Technical Specifications**:
- Search performance: <100ms for databases with 1000+ records
- Table formatting: Support 50+ results with pagination
- Export functionality: JSON and CSV formats
- Query flexibility: Multiple filter combinations
- User experience: Clear search syntax and help

**Acceptance Criteria**:
- Search command works with all filter combinations
- Table formatting handles various result sizes
- Export functionality produces correct formats
- Performance meets requirements for large databases
- Help system clearly documents search syntax

### Task 5: Create MCP Layer (Optional) ⏳ Not Started

**Priority**: LOW | **Complexity**: HIGH | **Impact**: LOW

**Research Requirements**:
- [ ] Use `perplexity_ask` to find FastMCP integration patterns
- [ ] Use `WebSearch` to find MCP schema definition examples
- [ ] Search GitHub for "fastmcp claude tools" implementations
- [ ] Find real-world MCP server patterns
- [ ] Locate JSON schema best practices for tools

**Implementation Steps**:
- [ ] 5.1 Create MCP layer infrastructure (if needed)
  - Create `/src/claude_comms/mcp/` directory
  - Create `schema.py` for JSON schema definitions
  - Create `wrapper.py` for FastMCP server
  - Define schemas for Claude tools integration
  - Add MCP server configuration

- [ ] 5.2 Implement JSON schemas
  - Define input schemas for CLI parameters
  - Create output schemas for task results
  - Add progress update schemas
  - Include error response schemas
  - Add validation rules and descriptions

- [ ] 5.3 Implement FastMCP wrapper
  - Create MCP server for Claude tools
  - Add tool registration and handlers
  - Implement request/response mapping
  - Add error handling and validation
  - Include logging and debugging

- [ ] 5.4 Add validation and testing
  - Test MCP server startup and registration
  - Validate schema compliance
  - Test with Claude tools integration
  - Verify error handling and responses
  - Test performance and reliability

- [ ] 5.5 Create verification report
  - Create `/docs/reports/005_task_5_mcp_layer.md`
  - Document MCP server operations
  - Include Claude tools integration examples
  - Show schema validation results
  - Add performance metrics

- [ ] 5.6 Git commit MCP layer

**Acceptance Criteria**:
- MCP server integrates with Claude tools (if implemented)
- Schemas validate correctly with real data
- Error handling provides useful feedback
- Performance meets Claude tools requirements

### Task 6: Integration and Entry Points ⏳ Not Started

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Implementation Steps**:
- [ ] 6.1 Update pyproject.toml entry points
  - Add new CLI entry point: `claude-comms-refactored = "claude_comms.cli.app:app"`
  - Preserve existing POC entry point: `claude-comms-poc-cli` (unchanged)
  - Add search command entry point if implemented
  - Add MCP server entry point if implemented
  - Test all entry points work correctly

- [ ] 6.2 Update module exports
  - Update `/src/claude_comms/__init__.py` with new exports
  - Export core layer functions for programmatic use
  - Include version information and metadata
  - Add backwards compatibility imports
  - Document API usage examples

- [ ] 6.3 Create integration tests
  - Test complete workflow from CLI to database
  - Validate all layers work together
  - Test error propagation through layers
  - Verify performance matches POC
  - Test with actual Claude CLI integration

- [ ] 6.4 Update documentation
  - Update main README with new architecture
  - Create migration guide from POC
  - Document API for programmatic usage
  - Add troubleshooting guide
  - Include performance comparisons

- [ ] 6.5 Create verification report
  - Create `/docs/reports/005_task_6_integration.md`
  - Document complete workflow testing
  - Include performance comparisons with POC
  - Show all entry points working
  - Add integration test results

- [ ] 6.6 Test backwards compatibility
  - Ensure POC entry point still works
  - Test new entry point matches POC functionality
  - Validate all CLI options preserved
  - Check performance parity
  - Verify database compatibility

- [ ] 6.7 Git commit integration updates

**Acceptance Criteria**:
- All entry points work correctly
- New CLI matches POC functionality exactly
- Performance equals or exceeds POC
- Documentation is complete and accurate
- Backwards compatibility maintained

### Task 7: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 7.1 Review all task reports
  - Read all reports in `/docs/reports/005_task_*`
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
  - Verify cross-layer compatibility
  - Update affected reports
  - Document any new limitations

- [ ] 7.5 Final comprehensive validation
  - Run complete workflow with all layers
  - Execute performance benchmarks
  - Test all CLI commands and options
  - Verify POC functionality preserved
  - Confirm all features work together

- [ ] 7.6 Create final summary report
  - Create `/docs/reports/005_final_summary.md`
  - Include completion matrix
  - Document all working features
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 7.7 Mark task complete only if ALL sub-tasks pass
  - Verify 100% task completion
  - Confirm all reports show success
  - Ensure no critical issues remain
  - Verify POC functionality preserved
  - Update task status to ✅ Complete

**Technical Specifications**:
- Zero tolerance for incomplete features
- Mandatory iteration until completion
- All tests must pass
- All reports must verify success
- POC functionality must be preserved

**Verification Method**:
- Task completion matrix showing 100%
- All reports confirming success
- Side-by-side comparison with POC functionality

**Acceptance Criteria**:
- ALL tasks marked COMPLETE
- ALL verification reports show success
- ALL tests pass without issues
- ALL POC features work in refactored version
- NO functionality regressions

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL previous tasks are verified as COMPLETE with passing tests and working functionality. The agent MUST continue iterating on incomplete tasks until 100% completion is achieved.

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| `claude-comms-refactored launch-claude` | Execute refactored CLI | `claude-comms-refactored launch-claude --prompt "test" --target-dir "." --requester "Marker" --responder "ArangoDB"` | Task execution with progress |
| `core.claude_executor.construct_claude_command()` | Build Claude command | `cmd = construct_claude_command(prompt, system_prompt, claude_path, verbose)` | Command list for subprocess |
| `core.claude_executor.run_claude_and_stream_output()` | Stream Claude output | `for event in run_claude_and_stream_output(cmd, cwd): ...` | Generator yielding structured events |
| `core.db_manager.create_database()` | Create task database | `conn = create_database("tasks.db")` | SQLite connection |
| `core.db_manager.update_task_progress()` | Update progress | `update_task_progress(conn, task_id, "running", content="...")` | Progress updated in DB |
| `claude-comms-refactored search-tasks` | Search task history | `claude-comms-refactored search-tasks --status complete --requester Marker` | Formatted table of results |

## Version Control Plan

- **Initial Commit**: Create task-005-start tag before implementation
- **Core Commits**: After each core layer implementation
- **CLI Commits**: After CLI layer completion
- **Integration Commits**: After layer integration
- **Test Commits**: After comprehensive testing
- **Final Tag**: Create task-005-complete after all tests pass

## Resources

**Python Packages**:
- typer: CLI framework (existing)
- rich: Console formatting (existing)
- loguru: Logging (existing)
- sqlite3: Database operations (existing)
- subprocess: Process management (existing)
- json: JSON processing (existing)
- pathlib: Path handling (existing)

**Documentation**:
- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Python Subprocess Guide](https://docs.python.org/3/library/subprocess.html)
- [SQLite Python Tutorial](https://docs.python.org/3/library/sqlite3.html)

**Reference Implementation**:
- POC: `src/claude_comms/poc/orchestrator_cli.py` (NEVER MODIFY)
- Working Entry Point: `claude-comms-poc-cli`
- Test Command: See `src/claude_comms/poc/reference/cli_terminal_command.md`

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All POC features working in 3-layer architecture, POC preserved

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
`/docs/reports/005_task_[SUBTASK]_[feature_name].md`

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.

**CRITICAL PRESERVATION REQUIREMENT**: The POC directory (`src/claude_comms/poc/`) MUST remain completely untouched. All refactoring creates NEW files in NEW directories while preserving the working POC as reference.