# Task 1: Refactor PoC `orchestrator_cli.py` to 3-Layer Architecture ⏳ Not Started

**Objective**: To refactor the existing single-file proof-of-concept `orchestrator_cli.py` (which handles inter-module communication with Claude, including subprocess management, output streaming, database progress tracking, and live CLI updates) into a clean 3-layer architecture (`core`, `cli`, `mcp`) as defined in `docs/3_LAYER_ARCHITECTURE.md`. This will improve modularity, testability, maintainability, and prepare the functionality for potential integration into the larger `claude-comms` project.

**Requirements**:
1. The refactored application MUST replicate all existing functionality of the `consolidated_orchestrator_v1` script.
2. The refactored code MUST strictly adhere to the 3-layer architecture (core, cli, mcp) outlined in `docs/3_LAYER_ARCHITECTURE.md`.
3. The `core` layer MUST be pure Python with no Typer, Rich, or other CLI/UI dependencies and must be independently testable.
4. The `cli` layer MUST use Typer for command-line argument parsing and should be responsible for all user-facing output and interaction.
5. Database interactions (SQLite) MUST be managed within the `core` layer.
6. Subprocess management for the Claude CLI MUST be handled within the `core` layer.
7. Logging (Loguru) should be configurable and used appropriately in each layer, with context (like `progress_id`) passed down.
8. All existing CLI options from `orchestrator_cli.py` (prompt, requester, responder, target-dir, system-prompt, db-path, claude-exe-path, simulation mode, verbose) MUST be supported by the new CLI layer.
9. The final output (Claude's response or error) MUST be handled as in the original script (pretty-printed JSON to stdout for success, error details to stderr).
10. Each refactoring sub-task MUST produce a verification report as specified in `docs/TASK_LIST_TEMPLATE_GUIDE.md`.

## Overview

The current `orchestrator_cli.py` is a proof-of-concept demonstrating end-to-end inter-module communication via the Claude CLI. While functional, its single-file structure is not ideal for a larger, maintainable project. Refactoring this into a 3-layer architecture will separate concerns, making the codebase cleaner, easier to test, and more extensible. This refactoring is a foundational step for potentially integrating this capability more formally into the `claude-comms` application. The `mcp` layer will be minimally stubbed for now, as the primary focus is on the `core` and `cli` separation of the existing functionality.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` (e.g., `/docs/reports/task1_refactor_orchestrator/`) with actual command outputs and performance results (where applicable).
2. Task 5 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

The primary research for this task involves understanding best practices for structuring Python applications, specifically regarding separation of concerns (business logic, UI, data access), and how to effectively use Typer for CLI applications. The existing `orchestrator_cli.py` serves as the primary source for current functionality. The `3_LAYER_ARCHITECTURE.md` and `TASK_LIST_TEMPLATE_GUIDE.md` provide the structural and procedural guidelines.

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH implementation sub-task (especially for core logic and CLI structure), the agent MUST:

1. **Use `perplexity_ask`** to research:
    - Current best practices (2025-current) for Python application layering.
    - Design patterns for separating CLI logic from core business logic.
    - Effective error handling and propagation across layers in Python.
    - Best practices for managing subprocesses in Python robustly.
    - SQLite usage patterns in Python applications (connection management, transaction handling).
    - Typer best practices for structuring commands and options.

2. **Use `WebSearch`** to find:
    - GitHub repositories with well-structured Python CLI tools using Typer.
    - Examples of Python projects with clear separation between core logic and interface layers.
    - Real production examples of Python applications managing external processes and database interactions.
    - Popular Python libraries that follow a similar layered approach.

3. **Document all findings** in task reports:
    - Links to source repositories that served as inspiration or provided patterns.
    - Code snippets illustrating effective layering or specific techniques (e.g., subprocess management, error handling).
    - Rationale for design choices based on research.

4. **DO NOT proceed without research**:
    - No theoretical implementations without grounding in existing patterns.
    - Must have real code examples or established best practices to guide the refactoring.

Example Research Queries:
perplexity_ask: "python 3-layer architecture cli typer best practices 2025"perplexity_ask: "python subprocess management robust error handling patterns"perplexity_ask: "sqlite3 connection management python application layers"WebSearch: "site:github.com python typer cli layered architecture example"WebSearch: "site:github.com python core logic separate from cli"
## Implementation Tasks (Ordered by Priority/Complexity)

Let the new refactored module be named `inter_module_communicator` located under `src/claude_comms/`.

### Task 1.1: Setup Project Structure and Core Infrastructure ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for Python project structuring with `src` layout.
- [ ] Use `WebSearch` for examples of `pyproject.toml` with Typer and Loguru.

**Working Starting Code** (Conceptual, based on `orchestrator_cli.py`):
* Current `DEFAULT_CLAUDE_PATH`.
* Initial Loguru setup.
* Basic Typer app definition.

**Implementation Steps**:
- [ ] 1.1.1 Create base directory structure for the new refactored module:
    - `src/claude_comms/inter_module_communicator/`
    - `src/claude_comms/inter_module_communicator/core/`
    - `src/claude_comms/inter_module_communicator/cli/`
    - `src/claude_comms/inter_module_communicator/mcp/` (stubbed for now)
    - `tests/inter_module_communicator/core/`
    - `tests/inter_module_communicator/cli/`
- [ ] 1.1.2 Add `__init__.py` files to all new directories to make them packages.
- [ ] 1.1.3 Update `pyproject.toml` (if necessary) to include dependencies used by the PoC if they are not already present (e.g., `typer[all]`, `loguru`, `pathlib` (though standard), `shlex`). `sqlite3` is standard. `typing_extensions` is often a Typer sub-dependency.
- [ ] 1.1.4 Define basic configuration management (e.g., for `DEFAULT_CLAUDE_PATH`, default DB path) – can be constants in a `core/config.py` or use `python-dotenv` if preferred.
- [ ] 1.1.5 Set up initial Loguru configuration in a shared utility or within the CLI app module, ensuring it can be controlled by a `--verbose` flag.

**Technical Specifications**:
- Standard Python package structure.
- Dependencies correctly listed.

**Verification Method**:
- Directory structure matches the plan.
- `__init__.py` files are present.
- `pyproject.toml` reflects necessary dependencies.
- Basic import of new modules works.

**CLI Testing Requirements**: N/A for this infrastructure task.

**Acceptance Criteria**:
- Directory structure created.
- `__init__.py` files in place.
- Dependencies updated in `pyproject.toml`.
- Basic configuration approach decided and implemented.
- Initial Loguru setup is functional.

- [ ] 1.1.6 Create verification report: `/docs/reports/task1_refactor_orchestrator/task_1_1_infrastructure_setup.md`

### Task 1.2: Refactor Database Logic into Core Layer ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for SQLite best practices in Python (connection handling, context managers, error handling).
- [ ] Use `WebSearch` for examples of data access layers in Python applications.

**Working Starting Code** (from `orchestrator_cli.py`):
* `create_database` function.
* `insert_progress_record` function.
* `update_progress_in_db` function.

**Implementation Steps**:
- [ ] 1.2.1 Create `src/claude_comms/inter_module_communicator/core/db_manager.py`.
- [ ] 1.2.2 Move and adapt `create_database`, `insert_progress_record`, and `update_progress_in_db` functions from `orchestrator_cli.py` into `db_manager.py`.
    - Ensure functions take a database connection or path as an argument.
    - Ensure they handle SQLite errors gracefully (e.g., `sqlite3.Error`).
    - Ensure all necessary parameters (progress\_id, prompt, requester, responder, target\_dir, system\_prompt\_file\_path, status, content, etc.) are passed and stored. The schema should match the one in `orchestrator_cli.py`.
- [ ] 1.2.3 Add a function `get_task_status(conn, progress_id)` to fetch the current status and relevant details of a task (this will be used by the CLI for polling/display).
- [ ] 1.2.4 Ensure all database functions use contextualized Loguru logging (passing `progress_id`).
- [ ] 1.2.5 Implement basic validation for `db_manager.py` in its `if __name__ == "__main__":` block, demonstrating creation, insertion, update, and retrieval.

**Technical Specifications**:
- All DB operations are transactional where appropriate (e.g., using `conn.commit()`).
- Handles `sqlite3.Error` exceptions.

**Verification Method**:
- Run the `db_manager.py` standalone validation.
- Manually inspect the SQLite database created by the validation to confirm data integrity.
- Logs should show correct DB operations.

**CLI Testing Requirements**: N/A for this core task.

**Acceptance Criteria**:
- Database functions are moved to `core/db_manager.py`.
- Functions are testable and handle SQLite errors.
- Standalone validation in `db_manager.py` passes.
- Database schema correctly stores all required task information.

- [ ] 1.2.6 Create verification report: `/docs/reports/task1_refactor_orchestrator/task_1_2_core_db_logic.md`

### Task 1.3: Refactor Claude Execution Logic into Core Layer ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for robust Python `subprocess.Popen` usage (handling stdout/stderr, `communicate`, `poll`, termination, error codes, CWD management).
- [ ] Use `WebSearch` for examples of Python wrappers around CLI tools that stream JSON output.

**Working Starting Code** (from `orchestrator_cli.py`):
* Logic for constructing `cmd_list` (for both actual Claude and simulation).
* `subprocess.Popen` call with `cwd`.
* Loop for `iter(process.stdout.readline, '')`.
* JSON parsing of streamed lines (`json.loads(stripped_line)`).
* Extraction of content from `assistant` messages and handling of `system` and `result` messages.
* `process.communicate()` and exit code handling.

**Implementation Steps**:
- [ ] 1.3.1 Create `src/claude_comms/inter_module_communicator/core/claude_executor.py`.
- [ ] 1.3.2 Create a function, e.g., `execute_claude_task(progress_id, prompt_text, system_prompt_content, target_dir_path, claude_exe_path, use_simulation, pass_verbose_to_claude_cli)`.
    - This function will encapsulate the logic of:
        - Constructing the `cmd_list` (actual or simulation).
        - Launching the subprocess with `subprocess.Popen`, setting the `cwd` to `target_dir_path`.
        - Iterating through `process.stdout.readline()`.
        - Parsing each JSON line.
    - Instead of directly updating the DB or printing, this function should be a **generator** that `yield`s structured event objects or data dictionaries as they are processed from the stream. Examples of yielded objects:
        - `{"type": "status_update", "status": "claude_init", "details": {"session_id": "..."}}`
        - `{"type": "text_chunk", "chunk": "some text from Claude"}`
        - `{"type": "final_result", "subtype": "success", "content": "full assembled content"}`
        - `{"type": "final_result", "subtype": "error", "details": "error info", "stderr": "..."}`
        - `{"type": "subprocess_exit", "code": 0, "stderr": "..."}`
    - This makes the core executor testable independently of the DB or CLI.
- [ ] 1.3.3 Ensure robust error handling for subprocess failures (e.g., executable not found, non-zero exit codes, timeouts). These should also be yielded as structured error events.
- [ ] 1.3.4 Log subprocess activities (command executed, PID, CWD) using contextualized Loguru. Raw stdout lines from Claude should be logged at DEBUG level.
- [ ] 1.3.5 Implement basic validation for `claude_executor.py` in its `if __name__ == "__main__":` block, demonstrating calling `execute_claude_task` (likely with simulation mode) and iterating through/printing the yielded events.

**Technical Specifications**:
- Handles subprocess lifecycle correctly (launch, stream, communicate, terminate/kill).
- Parses expected JSON stream from Claude.
- Gracefully handles non-JSON lines or JSON parsing errors in the stream.

**Verification Method**:
- Run the `claude_executor.py` standalone validation.
- Verify that the validation script correctly iterates through yielded events from the simulation.
- Check logs for correct command execution and CWD.

**CLI Testing Requirements**: N/A for this core task.

**Acceptance Criteria**:
- Claude execution logic is moved to `core/claude_executor.py`.
- `execute_claude_task` function is a generator yielding structured events/data.
- Handles subprocess errors and stream parsing issues robustly.
- Standalone validation passes.

- [ ] 1.3.6 Create verification report: `/docs/reports/task1_refactor_orchestrator/task_1_3_core_claude_executor.md`

### Task 1.4: Implement CLI Layer using Typer ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for Typer best practices (structuring commands, options, type hints, help text, callbacks).
- [ ] Use `WebSearch` for examples of Typer CLIs that interact with a core logic layer.

**Working Starting Code** (from `orchestrator_cli.py`):
* Typer app definition (`app = typer.Typer(...)`).
* `@app.callback()` or `@app.command("launch-claude")` decorator and `run_claude_communication` function signature with `typer.Option` definitions.
* Loguru setup logic based on `--verbose`.
* `display_cli_progress` function.
* Final result printing logic (including pretty-printing JSON).

**Implementation Steps**:
- [ ] 1.4.1 Create `src/claude_comms/inter_module_communicator/cli/app.py`.
- [ ] 1.4.2 Define the Typer application `app = typer.Typer(...)`.
- [ ] 1.4.3 Re-implement the `launch-claude` command (e.g., as `def launch_claude_command(...)` decorated with `@app.command("launch-claude")`).
    - This function will take all the CLI options defined in the original `orchestrator_cli.py` (`prompt`, `target_dir`, `requester`, `responder`, `system_prompt_file`, `db_path`, `claude_exe_path`, `use_simulation`, `verbose`). Use basic types (str, bool) for Typer options for simplicity first, and convert to `Path` objects inside the function.
    - **Orchestration Logic**:
        1. Configure Loguru based on `verbose` flag (console INFO, file DEBUG).
        2. Generate `progress_id`.
        3. Call `core.db_manager.create_database`.
        4. Call `core.db_manager.insert_initial_task_record`.
        5. Call `cli.formatters.display_cli_progress` (initially).
        6. Read system prompt file content.
        7. Iterate through events yielded by `core.claude_executor.execute_claude_task(...)`:
            - If `event["type"] == "text_chunk"`, append to local `content_chunks`. Call `core.db_manager.update_task_progress` with status `receiving_chunk`, full content, and `increment_chunk=True`.
            - If `event["type"] == "status_update"`, call `core.db_manager.update_task_progress` with the new status.
            - If `event["type"] == "final_result"` and `subtype == "success"`, call `core.db_manager.update_task_progress` with status `complete` and final content.
            - If `event["type"] == "final_result"` and `subtype == "error"`, call `core.db_manager.update_task_progress` with status `error` and error details.
            - After each DB update, call `cli.formatters.display_cli_progress`.
        8. Log final task summary.
        9. Print final result to `stdout` (pretty-print JSON) or error to `stderr`.
- [ ] 1.4.4 Create `src/claude_comms/inter_module_communicator/cli/formatters.py`.
    - Move and adapt the `display_cli_progress` function here. It should accept structured data and use Loguru to print.
- [ ] 1.4.5 Ensure the `if __name__ == "__main__": app()` block is in `cli/app.py` to make it runnable.
- [ ] 1.4.6 Add an entry point to `pyproject.toml` for this new CLI app, e.g., `imc-cli = "claude_comms.inter_module_communicator.cli.app:app"`.

**Technical Specifications**:
- All CLI options from original script are present and functional.
- Output matches the original script's live progress and final result format.
- Logging behavior (console INFO, file DEBUG, controlled by `--verbose` for Claude CLI itself) is replicated.

**Verification Method**:
- Run the new CLI (`python src/claude_comms/inter_module_communicator/cli/app.py launch-claude ...` or via installed entry point `imc-cli launch-claude ...`).
- Test with both simulation and actual Claude mode.
- Test with and without `--verbose`.
- Verify console output, file log content, and database records.
- Use the exact terminal command from `src/claude_comms/poc/cli_terminal_command.md` as a primary test case.

**CLI Testing Requirements**:
- [ ] Execute `imc-cli launch-claude` with all parameter combinations from the original PoC test command.
- [ ] Verify correct CWD is used for the Claude subprocess.
- [ ] Verify correct system prompt content is passed to Claude.
- [ ] Verify live progress updates on the console are accurate and timely.
- [ ] Verify final output (JSON pretty-printed or text) to `stdout` for success.
- [ ] Verify error messages to `stderr` for failures.
- [ ] Verify database entries are correct.
- [ ] Verify file logs contain DEBUG level details, including raw Claude stream.

**Acceptance Criteria**:
- New CLI is runnable and replicates all functionality of the original `orchestrator_cli.py`.
- Code is cleanly separated into `cli/app.py` and `cli/formatters.py`, calling functions from the `core` layer.
- All CLI tests pass.

- [ ] 1.4.7 Create verification report: `/docs/reports/task1_refactor_orchestrator/task_1_4_cli_layer_implementation.md`

### Task 1.5: Stub MCP Layer and Final Integration ⏳ Not Started

**Priority**: LOW | **Complexity**: LOW | **Impact**: MEDIUM (for future extensibility)

**Research Requirements**: N/A for stubbing.

**Implementation Steps**:
- [ ] 1.5.1 Create `src/claude_comms/inter_module_communicator/mcp/schema.py` and `src/claude_comms/inter_module_communicator/mcp/wrapper.py` with basic placeholder content or comments indicating their future purpose, as per `docs/3_LAYER_ARCHITECTURE.md`.
- [ ] 1.5.2 Ensure all layers (`core`, `cli`) can be imported correctly from the main `src/claude_comms/inter_module_communicator/__init__.py`.
- [ ] 1.5.3 Perform a full end-to-end test using the new CLI entry point (`imc-cli`) with a complex scenario (e.g., the Marker/ArangoDB example).

**Technical Specifications**:
- MCP layer files exist as placeholders.
- The refactored application is fully runnable as a package.

**Verification Method**:
- Run the CLI end-to-end.
- Check that imports work and no structural errors exist.

**CLI Testing Requirements**:
- [ ] Re-run key end-to-end tests using the installed CLI entry point.

**Acceptance Criteria**:
- MCP layer stubs are in place.
- Full application is integrated and runs end-to-end correctly via its new CLI entry point.

- [ ] 1.5.4 Create verification report: `/docs/reports/task1_refactor_orchestrator/task_1_5_mcp_stub_integration.md`

### Task 1.6: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 1.6.1 Review all task reports from 1.1 to 1.5:
    - Read all reports in `/docs/reports/task1_refactor_orchestrator/`
    - Create a checklist of any incomplete features or deviations from requirements.
    - Identify any failed tests or missing functionality noted in reports.
- [ ] 1.6.2 Create task completion matrix for tasks 1.1-1.5.
    - Mark each sub-task as COMPLETE/INCOMPLETE.
    - List specific failures or pending items for any INCOMPLETE tasks.
- [ ] 1.6.3 Iterate on any incomplete tasks from 1.1-1.5:
    - Address identified issues.
    - Re-run relevant validation tests.
    - Update verification reports to reflect fixes and successful completion.
    - Continue until all preceding tasks (1.1-1.5) are marked COMPLETE.
- [ ] 1.6.4 Final comprehensive validation of the refactored application:
    - Run all CLI commands with various valid and invalid inputs.
    - Execute performance benchmarks (if defined, though less critical for this refactoring PoC).
    - Test actual Claude and simulation modes thoroughly.
    - Verify logging behavior (console vs. file, verbosity).
    - Confirm database integrity and content.
- [ ] 1.6.5 Create final summary report: `/docs/reports/task1_refactor_orchestrator/task_1_6_final_summary.md`
    - Include the completion matrix.
    - Document all working features of the refactored application.
    - List any remaining limitations or areas for future improvement.
- [ ] 1.6.6 Mark this main Task 1 complete only if ALL sub-tasks (1.1-1.5) pass and are verified.

**Technical Specifications**:
- 100% completion of all preceding sub-tasks.
- All verification reports for sub-tasks must show success.

**Verification Method**:
- Task completion matrix showing 100% for tasks 1.1-1.5.
- All individual sub-task reports confirming success.
- Successful execution of all final comprehensive validation tests.

**Acceptance Criteria**:
- ALL sub-tasks (1.1-1.5) marked COMPLETE.
- ALL verification reports for sub-tasks show success and are accurate.
- The refactored application fully replicates the functionality of the original PoC and meets all specified requirements.

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL previous tasks (1.1-1.5) are verified as COMPLETE with passing tests and working functionality. The agent MUST continue iterating on incomplete tasks until 100% completion is achieved.

## Usage Table (for the new refactored CLI)

| Command / Function          | Description                                                                 | Example Usage                                                                                                                                                                                                                                                                                       | Expected Output                                                                                                                                                              |
| --------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `imc-cli launch-claude`     | Initiates inter-module communication with Claude, tracks progress to DB.    | `imc-cli launch-claude --prompt "What is X?" --requester "ModA" --responder "ModB" --target-dir "/path/to/ModB" --system-prompt "/path/to/ModA/sys_prompt.md" --db-path "./tasks.db" --no-simulation`                                                                                             | Live progress updates to console, DEBUG logs to file, final Claude response to stdout (pretty-printed if JSON), task record in `tasks.db`.                                |
| `imc-cli launch-claude ... --simulation` | Runs the above in simulation mode.                                        | `imc-cli launch-claude --prompt "Simulate schema" --requester "TestR" --responder "TestS" --target-dir "/tmp" --simulation`                                                                                                                                                                   | Similar to above, but uses simulated Claude output. Useful for testing flow without actual Claude calls.                                                                     |
| `imc-cli launch-claude --help`| Displays help for the `launch-claude` command and its options.            | `imc-cli launch-claude --help`                                                                                                                                                                                                                                                                      | Detailed help message listing all available options, their descriptions, and defaults.                                                                                       |

## Version Control Plan

- **Initial Commit**: Create tag `task-1-refactor-start` before beginning implementation.
- **Core Layer Commit**: After Task 1.2 (DB) and Task 1.3 (Executor) are complete and verified. Tag: `task-1-core-complete`.
- **CLI Layer Commit**: After Task 1.4 (CLI App) is complete and verified. Tag: `task-1-cli-complete`.
- **Integration Commit**: After Task 1.5 (MCP Stub & Final Integration) is complete. Tag: `task-1-integration-complete`.
- **Final Tag**: Create tag `task-1-refactor-complete` after Task 1.6 (Completion Verification) confirms all sub-tasks pass.

## Resources

**Python Packages**:
- `typer`: For building the CLI layer.
- `loguru`: For structured logging.
- `sqlite3`: (Standard library) For database interaction.
- `pathlib`: (Standard library) For path manipulation.
- `shlex`: (Standard library) For quoting command arguments for logging.
- `json`: (Standard library) For parsing Claude's output.

**Project Documentation**:
- `docs/3_LAYER_ARCHITECTURE.md`: The architectural guide for this refactoring.
- `docs/TASK_LIST_TEMPLATE_GUIDE.md`: This template guide itself.
- `src/claude_comms/poc/orchestrator_cli.py` (Canvas artifact `consolidated_orchestrator_v1`): The source script being refactored.

**External Documentation**:
- [Typer Documentation](https://typer.tiangolo.com/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Python `subprocess` Module](https://docs.python.org/3/library/subprocess.html)
- [Python `sqlite3` Module](https://docs.python.org/3/library/sqlite3.html)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All features of the original PoC are replicated in the new 3-layer architecture, all tasks in this list are marked ✅ Complete, and all verification reports confirm success.

## Report Documentation Requirements

(This section is a reminder and matches the main guide)

Each sub-task (1.1 through 1.5) MUST have a corresponding verification report in `/docs/reports/task1_refactor_orchestrator/` following these requirements:

### Report Structure:
Each report must include:
1. **Task Summary**: Brief description of what was implemented for that specific sub-task.
2. **Research Findings**: Links to repos, code examples found, best practices discovered relevant to the sub-task.
3. **Non-Mocked Results**: Real command outputs (e.g., from running `python core/db_manager.py` for its validation) and performance metrics where applicable.
4. **Performance Metrics**: Actual benchmarks with real data (less critical for this refactoring, but note if any performance implications were observed).
5. **Code Examples**: Key working code snippets from the implemented sub-task with verified output.
6. **Verification Evidence**: Logs (snippets from the file log), database query results, or console output snippets proving functionality of the sub-task.
7. **Limitations Found**: Any discovered issues or constraints specific to the sub-task.
8. **External Resources Used**: All GitHub repos, articles, and examples referenced for the sub-task.

### Report Naming Convention:
`/docs/reports/task1_refactor_orchestrator/task_1_X_[short_feature_name].md`
Example: `/docs/reports/task1_refactor_orchestrator/task_1_2_core_db_logic.md`

## Context Management

When context length is running low during implementation, use the following approach to compact and resume work:

1. Issue the `/compact` command to create a concise summary of current progress.
2. The summary will include:
    - Completed tasks and key functionality.
    - Current task in progress with specific subtask.
    - Known issues or blockers.
    - Next steps to resume work.
    - Key decisions made or patterns established.

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.
