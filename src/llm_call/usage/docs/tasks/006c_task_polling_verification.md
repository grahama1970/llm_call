# TASK POLLING VERIFICATION TEST (WITH PROMPT TEMPLATES)

## IMPORTANT: USE EXISTING PROMPT TEMPLATES
**DO NOT RE-IMPLEMENT the logic for verification or polling!**  
Always use the existing prompt templates:
- `~/.claude/commands/claude-verify.md`
- `~/.claude/commands/claude-poll.md`

These prompt files are automatically loaded by Claude Code and contain all necessary instructions.  
**When verification or polling is required, thoroughly read and implement the instructions from the respective markdown prompt file.**

## PURPOSE
Test sequential task execution with background Claude Code verification and polling using prompt templates.
Verify that polling prevents race conditions and ensures proper task completion before proceeding.

**VERIFICATION GOAL:**  
Prove that the prompt templates in `~/.claude/commands/claude-verify.md` and `~/.claude/commands/claude-poll.md` can orchestrate sequential tasks, with Claude Code thoroughly reading and implementing these markdown files to manage background verification and polling, ensuring each step completes before proceeding.

## CRITICAL LIMITATIONS
- No extra Python files/modules beyond those explicitly required.
- All code and logging setup is included inline in generated scripts via prompts.
- All logs go to `task_execution.log`.
- All file paths and parameters are passed via prompt variables (no hardcoded values).

---

## GLOBAL INSTRUCTION: LOGURU LOGGING SETUP

**Before starting Task 3 and beyond, ensure all generated Python scripts include the following Loguru setup at the top. All log messages must use this logger and append to `task_execution.log`.**

```
from loguru import logger
import datetime
logger.add('task_execution.log', 
           rotation='1 MB', 
           enqueue=True, 
           backtrace=True, 
           diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
```

---

## TASKS (SEQUENTIAL - MUST WAIT FOR EACH TO COMPLETE)

### Task 1: Read Global CLAUDE.md
- Use the Read tool to read `/home/graham/.claude/CLAUDE.md`
- This file contains CRITICAL LIMITATIONS and rules that MUST be followed
- Pay special attention to:
  - "BEFORE ANY TASK: source .venv/bin/activate"
  - "Check for slash commands first: /help"
  - "FORBIDDEN" section
  - All other directives

### Task 2: Read Project CLAUDE.md
- Use the Read tool to read `/home/graham/workspace/experiments/llm_call/CLAUDE.md`
- This file contains project-specific overrides
- Pay special attention to:
  - Current Tasks Plan
  - Project-specific dependencies
  - Special considerations

### Task 3: Verify Environment
- Run `which python` to verify virtual environment is activated
- If the path does NOT contain `.venv`, STOP and run `source .venv/bin/activate` first
- This is MANDATORY per CLAUDE.md rules

### Task 4: Create Simple Function with Output
- Log: `"📝 TASK 4 STARTED: Create simple function"`
- Log: `"-"*80` (sub-separator)
- Write `simple_add.py` containing:
  - The Loguru setup (as above).
  - A function that adds two numbers, logs the calculation, writes the result to `add_results.txt`, and logs completion.
  - A main block that calls the function.
- After writing the file, log:
  ```
  logger.info("[CODE_WRITTEN] simple_add.py:")
  logger.info("```python")
  logger.info(open("simple_add.py").read())
  logger.info("```")
  ```
- Execute the script and log:
  ```
  logger.info("[EXECUTION_OUTPUT]")
  logger.info(f"stdout: {stdout}")
  logger.info(f"stderr: {stderr}")
  ```
- After writing `add_results.txt`, log:
  ```
  logger.info("[FILE_CREATED] add_results.txt:")
  logger.info("```")
  logger.info(open("add_results.txt").read())
  logger.info("```")
  ```
- Log: `"✅ TASK 4 COMPLETED: Function created and executed"`
- Log: `"="*80"` (separator)

---

### Task 5: Launch Verification Script in Background (Prompt Template)
- Log: `"🔬 TASK 5 STARTED: Launch background verification"`
- Log: `"-"*80` (sub-separator)
- Before launching, create `verification_status.json` with status `"in-progress"`:
  ```
  import json
  with open("verification_status.json", "w") as f:
      json.dump({"status": "in-progress"}, f, indent=2)
  logger.info("[JSON_WRITTEN] verification_status.json:")
  logger.info("```json")
  logger.info(open("verification_status.json").read())
  logger.info("```")
  ```
- Use the prompt template at `~/.claude/commands/claude-verify.md`, substituting parameters as specified:
  - code_file=simple_add.py
  - result_file=add_results.txt
  - status_file=verification_status.json
  - log_file=task_execution.log
  - expected_result=5
- Execute the verification script in a background subprocess (e.g., using `subprocess.Popen` in Python), so the main workflow can proceed to polling without blocking.
- The verification script should:
  - Import and configure Loguru as in the global instruction.
  - Log start and all actions.
  - Analyze `simple_add.py` and `add_results.txt`.
  - Run `python simple_add.py`, capturing output and errors.
  - Update `verification_status.json` with:
    - `datetime`
    - `critique`
    - `status` ("pass" or "fail")
    - `stdout`
    - `stderr`
  - Log completion with status.
- Log: `"="*80"` (separator)

---

### Task 6: Poll for Verification Completion (Prompt Template)
- Log: `"🔄 TASK 6 STARTED: Polling for verification completion"`
- Log: `"-"*80` (sub-separator)
- Use the prompt template at `~/.claude/commands/claude-poll.md`, substituting parameters as specified:
  - status_file=verification_status.json
  - expected_status=pass
  - timeout=600
  - log_file=task_execution.log
- Note: The template has "TASK 3" hardcoded in logs, but this is actually Task 6. Adjust the generated script accordingly.
- The polling script should check `verification_status.json` repeatedly until `"status": "pass"`, logging each attempt:
  ```
  logger.info(f"[POLL_ATTEMPT] #{attempt_number} at {timestamp}")
  logger.info("[FILE_READ] verification_status.json:")
  logger.info("```json")
  logger.info(open("verification_status.json").read())
  logger.info("```")
  logger.info(f"[POLL_RESULT] Status: {status} ({message})")
  ```
- When status is "pass", log: `"✅ TASK 6 COMPLETED: Verification passed"`
- Log: `"="*80"` (separator)

---

### Task 7: Answer Simple Question (Only After Verification Passes)
- Log: `"❓ TASK 7 STARTED: Answer question (verification passed)"`
- Log: `"-"*80` (sub-separator)
- Write the answer to "What is the capital of France?" in `final_answer.txt`.
- Log the file creation:
  ```
  logger.info("[FILE_WRITTEN] final_answer.txt:")
  logger.info("```")
  logger.info("Paris")
  logger.info("```")
  ```
- Log: `"🎉 TASK 7 COMPLETED: Sequential execution finished"`
- Log: `"="*80"` (separator)

---

## VERIFICATION CRITERIA
- All tasks execute in sequence (no parallel execution).
- Verification runs in a background subprocess without blocking.
- Polling prevents Task 7 from starting prematurely.
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
- All file paths and parameters are passed via prompt variables (no hardcoded values).
- **CRITICAL**: The verification and polling prompt files already exist in `~/.claude/commands/` and should NOT be re-implemented.  
  **Always thoroughly read and implement the instructions from those files.**
