# Orchestrator Design Document

## Overview

The Claude Code Orchestrator is the master AI agent responsible for executing tasks defined in `tasks.yaml`. It provides a flexible, self-correcting automation framework that can adapt to failures and improve over time.

## Core Components

### 1. Task Parser
- Reads and validates `tasks.yaml`
- Expands template variables (e.g., `{{settings.log_file}}`)
- Builds execution graph respecting dependencies

### 2. Task Executor
Handles different action types:
- `llm_generate_and_run`: Generate code from templates and execute
- `execute_command`: Run shell commands directly
- `write_file`: Create files with specified content
- `poll_file_status`: Wait for async operations to complete

### 3. Verification Engine
- Executes post-task verification steps
- Supports multiple verification types:
  - `file_exists`: Check file/directory existence
  - `file_contains`: Verify file content
  - `log_contains`: Check log entries

### 4. Self-Correction Module
- Activates on task failures
- Analyzes errors using `[SELF_CORRECTION]` blocks
- Generates template revisions
- Retries failed tasks with improvements

## Execution Flow

### Main Loop
```
1. Parse tasks.yaml
2. For each task:
   a. Log task start
   b. Check skip_if conditions
   c. Execute action (inline or background)
   d. Handle results and run verification
   e. On failure, trigger self-correction
3. Complete workflow or report errors
```

### Self-Correction Flow
```
1. Capture failure context:
   - Task definition
   - Template used
   - Generated code
   - Error output
2. Analyze using [SELF_CORRECTION] section
3. Receive correction response:
   - template_revision: Update template and retry
   - external_error: Report for human intervention
4. Apply fixes and continue
```

## Key Design Principles

### 1. Separation of Concerns
- Task definitions (what) vs. implementation templates (how)
- Configuration vs. runtime artifacts
- Human-readable plans vs. machine execution

### 2. Idempotency
- Skip conditions prevent redundant work
- Generated scripts saved for reuse
- Stateless task execution

### 3. Observability
- Comprehensive logging at each step
- Status files for async coordination
- Clear error reporting

### 4. Resilience
- Self-correction for recoverable failures
- Graceful handling of external errors
- Support for workflow resumption

## Implementation Considerations

### Template Processing
- Use template engine (e.g., Jinja2) for variable substitution
- Pass parameters explicitly via `params` block
- Maintain template context throughout execution

### Background Execution
- Fork processes for `mode: background` tasks
- Use status files for inter-process communication
- Implement timeout mechanisms for polling

### Error Handling
- Capture stdout/stderr for all executions
- Preserve error context for self-correction
- Distinguish between template and external errors

### State Management
- Maintain minimal state between tasks
- Use filesystem as source of truth
- Enable stateless restart from any point

## Extension Points

### Custom Action Types
New action types can be added by:
1. Defining handler in executor
2. Specifying required parameters
3. Implementing verification logic

### Verification Types
Additional verification methods:
- API endpoint checks
- Database state validation
- Performance benchmarks

### Self-Correction Strategies
Enhanced correction capabilities:
- Multi-attempt refinement
- Cross-template learning
- Historical error patterns

## Security Considerations

- Sanitize template parameters
- Restrict file system access
- Validate generated code before execution
- Log all template modifications

## Future Enhancements

1. **Parallel Execution**: Run independent tasks concurrently
2. **Conditional Branching**: Dynamic task selection based on results
3. **Template Versioning**: Track and rollback template changes
4. **Distributed Execution**: Run tasks across multiple machines
5. **Visual Workflow Editor**: GUI for task definition and monitoring