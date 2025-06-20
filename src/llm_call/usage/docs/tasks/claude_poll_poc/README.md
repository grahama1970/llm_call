# Claude Poll POC - Background Verification with Polling

This POC demonstrates how to use background Claude Code processes for verification with polling-based synchronization, ensuring sequential task execution without race conditions.

## Key Learnings

1. **Declarative Task Structure**: The main task file describes WHAT to do, while helper prompts contain HOW to do it.
2. **Self-Contained Execution**: All files (inputs, outputs, logs) stay within the POC directory.
3. **Hybrid Template Strategy**: Intentionally uses both dynamic code generation (from prompts) and parameterized scripts to balance flexibility with reliability.
4. **Synchronization Pattern**: Background process + polling ensures proper sequencing without race conditions.
5. **Clear Logging**: Structured logging enables debugging and verification by humans, agents, and models.
6. **Selective Verification**: A two-tiered approach (inline verification for key steps, holistic audit for all) balances rigor with efficiency.

## Directory Structure
The project maintains a clean structure by separating source instructions, generated code, and final artifacts.

```
claude_poll_poc/
├── 001_claude_poll_verification_tasks.md # Main task list (declarative)
├── README.md               # This file
├── .gitignore              # Git ignore for generated files
├── commands/               # Helper instruction templates (the "source")
│ ├── archive-setup.md         # Helper for archiving and setup
│ ├── claude-verify.md         # Prompt for background Claude verification process
│ ├── claude-poll.md          # Template for generating polling scripts
│ └── ... (other command helpers)
├── docs/                 # Documentation and templates
│ └── tasks_template_rules.md      # Rules for creating robust task lists
└── [Generated during execution - not tracked in git]
 ├── generated_scripts/         # All generated Python scripts are placed here
 │ ├── setup.py            # Archives previous runs and sets up
 │ ├── simple_add.py          # Generated Python script
 │ ├── poll_script.py         # Generated polling script
 │ └── gemini_critique.py       # Gemini validation script
 ├── generated_scripts_archive_*/    # Archived scripts from previous runs
 ├── add_results.txt           # Output from simple_add.py
 ├── verification_status.json      # Status file (in-progress → pass/fail)
 ├── final_answer.txt          # Proof of sequential execution
 ├── execution_summary.txt        # Summary for validation
 ├── gemini_validation_response.md    # Gemini's critique
 ├── task_execution.log         # Complete execution log for the current run
 └── task_execution_archive_*.log    # Archived logs from previous runs
```

## Execution Flow

```mermaid
graph TD
 Start([Start]) --> Setup[Task 1: Setup Environment]
 Setup --> |Archives old logs & scripts| Create[Task 2: Create simple_add.py]
 Create --> |Executes script| Verify[Task 3a: Launch Background Verification]
  
 Verify --> |Non-blocking| Poll[Task 3b: Poll for Completion]
 Poll --> |Blocks until complete| Check{Verification<br/>Passed?}
  
 Check -->|Yes (exit code 0)| Final[Task 4: Answer Question]
 Check -->|No (exit code 1)| End([End - Failed])
  
 Final --> Validate[Task 5: Holistic Validation]
 Validate --> End2([End - Success])

 %% Styling for light/dark mode compatibility
 classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px,color:#000
 classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
 classDef decision fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
 classDef endpoint fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
  
 class Setup,Create,Verify,Poll,Final,Validate process
 class Check decision
 class Start,End,End2 endpoint
```

## How It Works

### 1. **Setup Environment** (Task 1)
- Archives any logs and scripts from previous runs to a timestamped directory.
- Creates a clean `generated_scripts/` directory for the current execution.
- Initializes fresh loguru logging for the current run.

### 2. **Create and Run Function** (Task 2)
- Creates `generated_scripts/simple_add.py` to perform a basic calculation.
- Executes the script and verifies its output. This is a foundational, high-stakes task.

### 3. **Background Verification with Polling** (Task 3)
- **Launch Phase**: Launches a background Claude process with the `claude-verify.md` prompt to verify the correctness and quality of `simple_add.py`. This is our **transactional verification**.
- **Poll Phase**: The main process blocks and waits for the verification to complete by running a polling script. The shell's `&&` operator ensures the workflow only proceeds if the verification result is "pass" (and the poll script exits with code 0).

### 4. **Answer Question & Prove Sequence** (Task 4)
- Only executes if the verification in Task 3 passed (thanks to the `&&` operator).
- Answers a simple knowledge-based question ("What is the capital of France?").
- Writing the answer to `final_answer.txt` proves that this step ran sequentially after the verification was complete. This is a low-complexity task that does not require its own inline verification.

### 5. **Holistic Validation** (Task 5)
- Creates a summary of the entire execution.
- Makes a real API call to an external model like Gemini for a final validation.
- This acts as a **holistic audit**, confirming the overall success and consistency of the entire task sequence by reviewing the final logs and artifacts.

## Key Design Decisions

1. **A Hybrid Template Strategy ("Declarative Prompts" vs. "Declarative Code")**: This POC intentionally uses two different types of instruction "templates" to balance flexibility with reliability.
  -  **Declarative Prompts (e.g., `claude-verify.md`):** These are detailed *specifications* that instruct the AI to *generate* a script from scratch. This approach offers maximum flexibility, adaptability, and the potential for self-correction, making it ideal for complex, one-off, or evolving tasks.
  -  **Declarative Code (e.g., `claude-poll.md`):** These helpers provide complete Python code that the AI uses directly with parameter substitution. This approach is faster, more reliable, and deterministic for common utility tasks.

2. **Why Background + Polling?**: Mimics real-world async operations (like API calls or long-running jobs) while maintaining strict sequential control in the main task flow.

3. **Why Self-Contained?**: Makes the POC portable, debuggable, and easy to understand by keeping all inputs, outputs, and logs in a single directory.

4. **Why Structured Logging?**: Enables reliable parsing by different systems (humans, agents, verification models) for debugging and auditing.

5. **Why Selective Verification?**: This POC demonstrates a two-tiered verification strategy to balance rigor with efficiency.
  -  **Transactional Verification (Task 3):** High-stakes, complex tasks (like generating a script) are verified immediately using the background/poll pattern. This acts as a critical quality gate.
  -  **Holistic Validation (Task 5):** Lower-complexity tasks (like Task 4's question-answering) do not require immediate verification. Their success is confirmed at the very end by the final audit, which reviews all evidence.

## The "Contain, Don't Destroy" Principle for Generated Code
A critical design choice in this framework is how to handle the scripts generated by the AI.

-  **Containment:** All generated executable code is placed within the `generated_scripts/` directory. This keeps the project root clean and separates human-authored "source" from machine-authored "code."
-  **Persistence:** These scripts are **never deleted** automatically after execution. They are treated as essential output artifacts, just like the `task_execution.log`.
-  **Why?** This provides a complete, auditable trail of the AI's work. If a task fails, the exact script that caused the error is available for inspection and debugging. This is crucial for improving the source `commands/` templates over time.
-  **Lifecycle Management:** Before a new run begins, the `setup.py` script archives the entire `generated_scripts/` directory, preserving the full context of every execution run for historical analysis.

## A Note on Debugging Scripts
This project may contain standalone scripts like `debug_gemini.py`. These files serve a specific, limited purpose:
-  **Role**: They are one-time, manual tools for troubleshooting fundamental environmental issues, such as API authentication, network connectivity, or library installation problems.
-  **Intended Use**: Run them manually from your terminal *before* starting a full execution to ensure your environment is configured correctly.
-  **Primary Improvement Loop**: They are **not** part of the main automated workflow. The primary method for resolving task-related errors is to improve the **Error Recovery Instructions** within the `commands/` helper templates themselves, creating a self-healing system.

## Success Criteria

- ✅ All tasks execute in sequence.
- ✅ All generated scripts are created in the `generated_scripts/` directory.
- ✅ Task 4 only runs after the verification in Task 3 passes.
- ✅ No race conditions between the verification and polling scripts.
- ✅ Clear, parseable logs are created for debugging and auditing.
- ✅ The final Gemini critique is successfully generated and saved to `gemini_validation_response.md`.

## Usage

1. Navigate to the POC directory:
  ```bash
  cd /home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc/
  ```

2. Execute the tasks in `001_claude_poll_verification_tasks.md` sequentially.

3. Review generated files and `task_execution.log` for results.

## Extension Points

This pattern can be extended for:
- Multiple background workers with centralized status tracking.
- Complex verification chains with dependencies.
- Integration with real external validators (Gemini, GPT-4, etc.).
- Distributed task execution with proper synchronization.

## Task List Conversion

The `docs/tasks_template_rules.md` file provides a template that AI models can use to convert traditional, informal task lists into the structured format demonstrated in this POC. This enables:

-  **Consistent Structure**: All task lists follow the same declarative pattern.
-  **Reusable Components**: Common operations can reference helper templates.
-  **Clear Dependencies**: Sequential requirements and exit conditions are explicit.
-  **Verification Integration**: Tasks can include inline verification steps where needed.

To convert a traditional task list:
1. Provide the original task list to Claude or Gemini.
2. Reference the rules in `docs/tasks_template_rules.md`.
3. The AI will restructure it into the declarative format with proper helper references.