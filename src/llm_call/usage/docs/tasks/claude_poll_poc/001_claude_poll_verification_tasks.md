# Background Verification with Polling POC

## Objective
Prove that we can use a background Claude Code process to verify results and block task progression until verification completes, using explicit shell commands for conditional logic.

## Important
This is a self-contained POC. All required command files are in the `commands/` subdirectory.

**CRITICAL FOR CLAUDE**: 
- When implementing slash commands (e.g., `/user:claude-verify`), use the templates in THIS POC's `commands/` directory.
- DO NOT use templates from `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/`
- ALL generated files go in THIS POC directory, not elsewhere.

## Working Directory
All tasks should be executed with the current working directory as:
`/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc/`

All file paths are relative to this directory unless otherwise specified.

## Generated Files
All generated files should be organized as follows:
- `generated_scripts/` - Directory for all generated Python scripts
 - `archive_and_setup.py` - Archives previous run and sets up logging
 - `simple_add.py` - Generated Python script
 - `verify_script.py` - Generated verification script
 - `poll_script.py` - Generated polling script
 - `answer_question.py` - Script for Task 4
 - `gemini_critique.py` - Generated Gemini validation script
- `add_results.txt` - Output from simple_add.py
- `verification_status.json` - Status file from verification
- `final_answer.txt` - Final output file, proving conditional execution
- `execution_summary.txt` - Summary for Gemini
- `gemini_validation_response.md` - Gemini's critique
- `task_execution.log` - All logging output
- `generated_scripts_archive_[timestamp]/` - Archived scripts from previous runs
- `task_execution_archive_[timestamp].log` - Archived logs from previous runs

## Tasks

### Task 1: Setup Environment
- Read `/home/graham/.claude/CLAUDE.md` and `/home/graham/workspace/experiments/llm_call/CLAUDE.md`
- Verify virtual environment is active (`which python` contains `.venv`)
- **Create `archive_and_setup.py` in the current directory first** (not in generated_scripts/ yet).
- **The script should:**
 - Archive existing `generated_scripts/` directory if it exists (rename with timestamp).
 - Archive existing `task_execution.log` if it exists (rename with timestamp).
 - Create a fresh `generated_scripts/` directory.
 - Initialize new logging to `task_execution.log`.
 - Use the code snippets in `commands/logging-setup.md` as a starting point.
- **Execute:** `python archive_and_setup.py`
- **After successful execution, move the script:** `mv archive_and_setup.py generated_scripts/`
- Log: "[TASK1] Environment setup complete."

### Task 2: Create and Run Simple Function
- Write a Python script named `generated_scripts/simple_add.py` that contains a function to add 2 and 3, and writes the result to a file named `add_results.txt`. The output should be the string "The sum of 2 and 3 is 5".
- The script should NOT log its own source code (prevents recursive logging).
- **Execute:** `python generated_scripts/simple_add.py`
- Log: "[TASK2] Script executed. Verifying output."
- **Execute a command to verify the content. This command will fail if the text is not found, halting execution if the orchestrator is run with `bash -e`:** `grep -q "The sum of 2 and 3 is 5" add_results.txt`
- Log: "[TASK2] Output in add_results.txt verified successfully."

### Task 3: Launch Background Verification and Wait for Completion
- Create `verification_status.json` with initial content: `{"status": "in-progress"}`
- Log: "[TASK3] Initial status file created."
- **Launch background verification:**
 - Generate a new script named `generated_scripts/verify_script.py` by following the instructions in `commands/claude-verify.md` with these parameters:
 - code_file=generated_scripts/simple_add.py, result_file=add_results.txt, status_file=verification_status.json, log_file=task_execution.log, expected_result=5
 - **Execute as a non-blocking background process:** `python generated_scripts/verify_script.py &`
 - Log: "[TASK3] Background verification process launched."
- **Wait for verification and log success atomically:**
 - Create a new script named `generated_scripts/poll_script.py`. Use the full Python code provided in `commands/claude-poll.md` as its content, replacing the placeholder variables with these parameters:
 - status_file=verification_status.json, expected_status=pass, timeout=600, log_file=task_execution.log
 - **Execute the polling script and chain its success log using `&&`. The next command only runs if `poll_script.py` exits with code 0. This removes the ambiguity of checking the exit code.**
 - **Execute:** `python generated_scripts/poll_script.py && python -c "from loguru import logger; logger.add('task_execution.log', format='{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}'); logger.info('[TASK3] Verification confirmed successfully.')"`
 - **Note:** If the polling script fails (e.g., timeout returns exit code 1), the `&&` chain will be broken, the success message will not be logged, and a properly configured orchestrator (`bash -e`) will halt all further tasks.

### Task 4: Answer Geography Question (Conditionally Executed)
- **This task will only be reached by the orchestrator if the `Execute` command in Task 3 completed successfully.**
- Create a Python script `generated_scripts/answer_question.py` to perform the following:
  - Import `loguru`.
  - Add the `task_execution.log` file handler (with the standard format).
  - Write the answer "Paris" to `final_answer.txt`.
  - Log: "[TASK4] Question answered and written to final_answer.txt"
- **Execute:** `python generated_scripts/answer_question.py`

### Task 5: Validate with Gemini
- Create `execution_summary.txt` by reading the generated files and populating the following template:
 ```
 POC Execution Summary:
 - generated_scripts/simple_add.py created: [yes/no]
 - add_results.txt contains: [file content]
 - verification_status.json status: [final status value from file]
 - final_answer.txt contains: [file content, or "not created" if Task 4 did not run]
 - All files were created sequentially: [Answer 'yes' only if Task 4 was successfully executed, otherwise answer 'no']
 ```
- Create `generated_scripts/gemini_critique.py` using the template from THIS POC's `commands/ask-gemini-flash.md`
- Make a REAL API call to Gemini (do NOT simulate)
- Include the full execution log and context about the task sequence
- **Ask Gemini to provide a detailed CRITIQUE of:**
 - Code quality and implementation
 - Task execution flow and sequencing
 - Logging clarity and completeness
 - Any potential issues or improvements
 - Whether the POC achieves its stated goals
- **IMPORTANT: Save Gemini's FULL CRITIQUE to `gemini_validation_response.md` including:**
 - Timestamp
 - Model used
 - Full critique text (not just YES/NO)
 - Specific observations and recommendations
 - Any concerns or improvements suggested
- **READ AND UNDERSTAND the critique** - use it to improve future implementations
- Log: "[TASK5] Gemini critique complete, saved to gemini_validation_response.md"

## Success Criteria
- All tasks execute in sequence.
- Task 4 only runs after Task 3's polling confirms verification passed with an exit code of 0.
- Gemini confirms all results are real and sequential execution was successful (or correctly halted).