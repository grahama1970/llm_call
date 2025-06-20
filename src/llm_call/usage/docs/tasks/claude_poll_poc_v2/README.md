# Claude Poll POC v2 - Flexible Task Automation Framework

This is version 2 of the Claude Poll POC, featuring a declarative YAML-based task orchestration system with self-correction capabilities.

## Overview

This framework moves from a rigid, proof-of-concept script to a flexible, self-correcting automation system. Key improvements include:

- **Declarative Task Definition**: Tasks are defined in `tasks.yaml` instead of verbose markdown files
- **Self-Correction**: Command templates include `[SELF_CORRECTION]` blocks for automatic error recovery
- **Flexible Execution**: Support for inline and background task execution
- **Better Organization**: Clear separation between configuration, templates, and runtime artifacts

## Architectural Design: Why YAML + Markdown?

This system uses two distinct formats for a specific architectural reason:

### YAML for Orchestration (`tasks.yaml`)
- **Machine-readable structure** that Claude Code can parse and execute systematically
- **Declarative configuration** defining WHAT should happen, not HOW
- Acts as the "program" that Claude Code runs step-by-step
- Similar to how CI/CD systems use YAML for workflow definition

### Markdown for Code Generation (`commands/*.md`)
- **Natural language prompts** that Claude Code reads when generating code
- **Self-prompting system** where Claude talks to itself in human-readable format
- Contains instructions, examples, and error recovery guidance
- Enables recursive self-improvement through `[SELF_CORRECTION]` blocks

This separation creates clear boundaries between Claude Code's different roles:
1. **Orchestrator**: Reading and executing the YAML task list
2. **Code Generator**: Reading markdown templates and creating Python scripts
3. **Executor**: Running the generated code and handling results

The result is a self-improving system where Claude Code can modify its own prompts based on execution failures, creating a feedback loop for continuous improvement.

## Directory Structure

```
claude_poll_poc_v2/
├── tasks.yaml                   # Declarative task definitions
├── README.md                    # This file
├── commands/                    # Command templates with self-correction
│   ├── archive-setup.md         # Environment setup template
│   ├── ask-gemini-flash.md      # Gemini Flash query template
│   ├── ask-gemini-pro.md        # Gemini Pro query template
│   ├── ask-ollama.md            # Ollama query template
│   ├── ask-perplexity.md        # Perplexity query template
│   ├── claude-poll.md           # Claude polling template
│   ├── claude-verify.md         # Claude verification template
│   └── logging-setup.md         # Logging configuration template
├── docs/                        # Documentation
│   ├── gemini_instructions.md   # Original design document
│   ├── 002_gemini_response.md   # Improvement suggestions
│   ├── 003_implementation_summary.md # Implementation changes
│   ├── orchestrator_design.md  # Orchestrator architecture
│   ├── tasks_template_rules.md  # Template writing guidelines
│   └── critiques/              # Critique rounds and analysis
├── examples/                    # Example runs and outputs
├── generated_scripts/           # Auto-generated scripts (runtime)
├── logs/                        # Execution logs (runtime)
└── outputs/                     # Task outputs (runtime)
```

## Task Definition Format

Tasks are defined in `tasks.yaml` with the following structure:

```yaml
working_directory: "/absolute/path/to/execution/directory"

settings:
  log_file: "task_execution.log"

tasks:
  - task_id: UNIQUE_ID
    description: "Human-readable description"
    action:
      type: llm_generate_and_run | execute_command | write_file
      mode: inline | background  # Optional, default: inline
      prompt_template: "path/to/template.md"  # For llm_generate_and_run
      output_path: "path/to/output.py"        # For llm_generate_and_run
      command: "command to execute"           # For execute_command
      content: "content to write"             # For write_file
      params:                                 # Template parameters
        key: value
    execute_after_generate:      # Optional, for generated scripts
      type: execute_command
      command: "python path/to/script.py"
    verify:                      # Optional verification steps
      - type: file_exists | file_contains | log_contains
        path: "file/to/check"
        content: "expected content"  # For file_contains
        pattern: "log pattern"       # For log_contains
    skip_if:                     # Optional skip conditions
      - type: file_exists
        path: "path/to/check"
```

## Key Features

### 1. Declarative Tasks
- High-level task definitions separate "what" from "how"
- Human-readable YAML format
- Support for dependencies and conditional execution

### 2. Self-Correction
- Command templates include `[SELF_CORRECTION]` blocks
- Automatic template revision on failures
- Root cause analysis and permanent fixes

### 3. Flexible Execution Modes
- **Inline**: Synchronous execution (default)
- **Background**: Asynchronous execution with polling
- **Verification**: Optional post-execution checks

### 4. Idempotency
- `skip_if` conditions prevent redundant work
- Generated scripts are saved for reuse
- Support for resuming failed workflows

## Template Standards

All command templates follow these standards:
- **Parameters Section**: Every template includes a `## Parameters:` section documenting required inputs
- **Variable Syntax**: All templates use `{{ params.variable }}` syntax consistently
- **Self-Correction**: Each template includes a `[SELF_CORRECTION]` block for error recovery
- **No Hardcoded Values**: Templates use parameters for all configurable values

## Usage

1. Define your tasks in `tasks.yaml`
   - Set `working_directory` to the root of your execution environment
   - All paths in tasks are relative to this working directory
2. Create or customize command templates in `commands/`
   - Use `{{ params.variable }}` syntax for all parameters
   - Include a `## Parameters:` section documenting inputs
3. Run the orchestrator (implementation-specific)
4. Monitor logs and outputs in respective directories

## Example Task Flow

The included `tasks.yaml` demonstrates:
1. Environment setup and archiving
2. Code generation and execution
3. Background verification with Claude
4. Status polling and synchronization
5. Final audit with Gemini

## Self-Correction Workflow

When a task fails:
1. Orchestrator analyzes the failure
2. Consults the `[SELF_CORRECTION]` section of the failed template
3. Generates a revised template if the issue is fixable
4. Retries the task with the improved template
5. Reports external errors for human intervention

This creates a system that learns from mistakes and becomes more reliable over time.