# TASK POLLING VERIFICATION TEST (WITH CLAUDE-VERIFY SLASH COMMAND)

## IMPORTANT: SLASH COMMANDS ALREADY EXIST
**DO NOT IMPLEMENT the `/claude-verify` and `/claude-poll` slash commands!**  
These commands already exist in:
- `~/.claude/commands/claude-verify.md`
- `~/.claude/commands/claude-poll.md`

They are automatically loaded by Claude Code and can be used directly.

## PURPOSE
Test sequential task execution with background Claude Code verification and polling.
Verify that polling prevents race conditions and ensures proper task completion before proceeding.

**VERIFICATION GOAL:**  
Prove that the `/claude-verify` and `/claude-poll` slash commands can orchestrate sequential tasks, waiting for background Claude Code instances to complete verification before proceeding.

## CRITICAL LIMITATIONS
- No extra Python files/modules beyond those explicitly required.
- All code and logging setup is included inline in generated scripts via prompts.
- All logs go to `task_execution.log`.
- All file paths and parameters are passed via slash commands or prompt variables (no hardcoded values).

---

## TASKS (SEQUENTIAL - MUST WAIT FOR EACH TO COMPLETE)

### Task -0: READ GLOBAL CLAUDE.MD
- Use the Read tool to read `/home/graham/.claude/CLAUDE.md`
- This file contains CRITICAL LIMITATIONS and rules that MUST be followed
- Pay special attention to:
  - "BEFORE ANY TASK: source .venv/bin/activate"
  - "Check for slash commands first: /help"
  - "FORBIDDEN" section
  - All other directives

### Task 0: READ PROJECT CLAUDE.MD
- Use the Read tool to read `/home/graham/workspace/experiments/llm_call/CLAUDE.md`
- This file contains project-specific overrides
- Pay special attention to:
  - Current Tasks Plan
  - Project-specific dependencies
  - Special considerations

### Task 1: VERIFY ENVIRONMENT
- Run `which python` to verify virtual environment is activated
- If the path does NOT contain `.venv`, STOP and run `source .venv/bin/activate` first
- This is MANDATORY per CLAUDE.md rules

### Task 2: Setup Loguru Logging (Prompt-Only Instruction)
- For all Python code generated in the following tasks, prepend this code to the top of the script:
  ```
  from loguru import logger
  import datetime
  
  # Configure logger with clear, parseable format
  logger.add('task_execution.log', 
             rotation='1 MB', 
             enqueue=True, 
             backtrace=True, 
             diagnose=True,
             format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
  ```
- All log messages in every task should use this logger and append to `task_execution.log`.
- Log: `"🚀 SEQUENTIAL TASK EXECUTION STARTED"`
- Log: `"="*80` (separator line for clarity)

---

### Task 3: Create Simple Function with Output
- Log: `"📝 TASK 1 STARTED: Create simple function"`
- Log: `"-"*80` (sub-separator)
- Write `simple_add.py` containing:
  - The Loguru setup (as above).
  - A function that adds two numbers, logs the calculation, writes the result to `add_results.txt`, and logs completion.
  - A main block that calls the function.
- After writing the file, log:
  ```
  "[CODE_WRITTEN] simple_add.py:"
  logger.info("```python")
  # Log the entire content of the file
  logger.info("```")
  ```
- Execute the script and log:
  ```
  "[EXECUTION_OUTPUT]"
  logger.info(f"stdout: {stdout}")
  logger.info(f"stderr: {stderr}")
  ```
- After writing `add_results.txt`, log:
  ```
  "[FILE_CREATED] add_results.txt:"
  logger.info("```")
  # Log the content
  logger.info("```")
  ```
- Log: `"✅ TASK 1 COMPLETED: Function created and executed"`
- Log: `"="*80` (separator)

---

### Task 4: Launch Background Verification via `/claude-verify` Slash Command
- Log: `"🔬 TASK 2 STARTED: Launch background verification"`
- Log: `"-"*80` (sub-separator)
- Immediately create `verification_status.json` with status `"in-progress"`.
- Log the command being executed:
  ```
  "[COMMAND] /claude-verify code_file=simple_add.py result_file=add_results.txt status_file=verification_status.json log_file=task_execution.log"
  ```
- Log the initial JSON status:
  ```
  "[JSON_WRITTEN] verification_status.json:"
  logger.info("```json")
  # Log the JSON content with proper formatting
  logger.info("```")
  ```
- **IMPORTANT**: Use the EXISTING `/claude-verify` slash command that is already available in `~/.claude/commands/claude-verify.md`. DO NOT implement this command - it already exists and will be auto-loaded by Claude Code.
- The `/claude-verify` slash command will launch a background Claude Code instance that:
  - Imports and configures Loguru as in Task 0.
  - Logs start and all actions.
  - Analyzes `simple_add.py` and `add_results.txt`.
  - Runs `python simple_add.py`, captures output and errors.
  - Updates `verification_status.json` with:
    - `datetime`
    - `critique`
    - `status` ("pass" or "fail")
    - `stdout`
    - `stderr`
  - Logs completion with status.
- Log: `"="*80` (separator)

#### `/claude-verify` Slash Command Specification (FOR REFERENCE ONLY - DO NOT IMPLEMENT)

**NOTE**: This section describes what the EXISTING `/claude-verify` command in `~/.claude/commands/claude-verify.md` does. DO NOT implement this - just use the existing command.

**Command:**
```
/claude-verify code_file=simple_add.py result_file=add_results.txt status_file=verification_status.json log_file=task_execution.log
```

**Behavior:**  
The existing command generates and executes the following Python code (parameters substituted from the command):

```
from loguru import logger
import subprocess, json, datetime, sys

code_file = "simple_add.py"
result_file = "add_results.txt"
status_file = "verification_status.json"
log_file = "task_execution.log"

logger.add(log_file, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
logger.info("🔬 BACKGROUND CLAUDE VERIFICATION STARTED")
logger.info("-" * 80)

critique = ""
status = "fail"
stdout = ""
stderr = ""

# Analyze code quality
try:
    with open(code_file) as f:
        code = f.read()
    logger.info("[CODE_ANALYSIS] Reading simple_add.py")
    logger.info("```python")
    logger.info(code)
    logger.info("```")
    if "def" in code and "add" in code:
        critique += "Function appears to be defined correctly. "
    else:
        critique += "Function definition may be missing or incorrect. "
except Exception as e:
    critique += f"Error reading code file: {e} "
    logger.error(f"[ERROR] Failed to read code file: {e}")

# Run the code and capture output
try:
    logger.info("[EXECUTION] Running python simple_add.py")
    proc = subprocess.run(
        [sys.executable, code_file],
        capture_output=True, text=True, timeout=10
    )
    stdout = proc.stdout
    stderr = proc.stderr
    logger.info(f"[EXECUTION_OUTPUT]")
    logger.info(f"stdout: {stdout.strip()}")
    logger.info(f"stderr: {stderr.strip()}")
    logger.info(f"return_code: {proc.returncode}")
    if proc.returncode == 0:
        critique += "Code executed successfully. "
    else:
        critique += f"Code execution failed with return code {proc.returncode}. "
except Exception as e:
    stderr += f"Exception running code: {e}\n"
    critique += "Exception during code execution. "
    logger.error(f"[ERROR] Exception during execution: {e}")

# Verify output file
try:
    with open(result_file) as f:
        result = f.read().strip()
    logger.info("[FILE_VERIFICATION] Reading add_results.txt")
    logger.info("```")
    logger.info(result)
    logger.info("```")
    if result.isdigit() and int(result) == 5:
        critique += "Output result is correct. "
        status = "pass"
    else:
        critique += f"Output result is incorrect: {result}. "
except Exception as e:
    critique += f"Error reading result file: {e} "
    logger.error(f"[ERROR] Failed to read result file: {e}")

# Write verification status JSON
verification = {
    "datetime": datetime.datetime.utcnow().isoformat() + "Z",
    "critique": critique.strip(),
    "status": status,
    "stdout": stdout.strip(),
    "stderr": stderr.strip()
}
logger.info("[JSON_UPDATE] Writing final verification status")
logger.info("```json")
logger.info(json.dumps(verification, indent=2))
logger.info("```")

with open(status_file, "w") as f:
    json.dump(verification, f, indent=2)

logger.info(f"🔬 BACKGROUND VERIFICATION COMPLETE: {status.upper()}")
logger.info("=" * 80)
```

---

### Task 5: Poll for Verification Completion via `/claude-poll`
- Log: `"🔄 TASK 3 STARTED: Polling for verification completion"`
- Log: `"-"*80` (sub-separator)
- **IMPORTANT**: Use the EXISTING `/claude-poll` slash command that is already available in `~/.claude/commands/claude-poll.md`. DO NOT implement this command - it already exists and will be auto-loaded by Claude Code.
- Use `/claude-poll` slash command to poll `verification_status.json` until `"status": "pass"`.
- All polling actions and results must be logged to `task_execution.log`.
- The polling script should log each attempt in this format:
  ```
  "[POLL_ATTEMPT] #{attempt_number} at {timestamp}"
  "[FILE_READ] verification_status.json:"
  logger.info("```json")
  # Log the JSON content
  logger.info("```")
  "[POLL_RESULT] Status: {status} ({message})"
  ```
- When status is "pass", log: `"✅ TASK 3 COMPLETED: Verification passed"`
- Log: `"="*80` (separator)

**Command:**
```
/claude-poll status_file=verification_status.json expected_status=pass timeout=600 log_file=task_execution.log
```

**Behavior (FOR REFERENCE - DO NOT IMPLEMENT):**  
The existing command generates and executes a polling script that:
- Waits for the status file to exist.
- Checks the status field for the expected value.
- Logs all polling actions and results to `task_execution.log`.
- Exits only when the expected status is reached or timeout occurs.

---

### Task 6: Answer Simple Question (Only After Verification Passes)
- Log: `"❓ TASK 4 STARTED: Answer question (verification passed)"`
- Log: `"-"*80` (sub-separator)
- Write the answer to "What is the capital of France?" in `final_answer.txt`.
- Log the file creation:
  ```
  "[FILE_WRITTEN] final_answer.txt:"
  logger.info("```")
  logger.info("Paris")
  logger.info("```")
  ```
- Log: `"🎉 TASK 4 COMPLETED: Sequential execution finished"`
- Log: `"="*80` (separator)

---

## VERIFICATION CRITERIA
- All tasks execute in sequence (no parallel execution).
- `/claude-verify` runs in background without blocking.
- `/claude-poll` prevents Task 4 from starting prematurely.
- All output files contain expected content:
  - `add_results.txt`: Contains addition results.
  - `verification_status.json`: Contains "pass" status with critique.
  - `final_answer.txt`: Contains "Paris".
  - `task_execution.log`: Contains logs from all steps.

---

## SUCCESS INDICATORS
- Sequential execution maintained.
- Background verification completes without manual intervention.
- Polling mechanism works correctly.
- JSON status file updates properly.
- All output files created with correct content.

---

## NOTES
- No extra Python modules or files beyond those explicitly required.
- All code and logging setup is included inline in generated scripts via prompts.
- All logs go to `task_execution.log`.
- All file paths and parameters are passed via slash commands or prompt variables (no hardcoded values).
- **CRITICAL**: The `/claude-verify` and `/claude-poll` commands already exist in `~/.claude/commands/` and should NOT be re-implemented. They will be automatically available when you use them.