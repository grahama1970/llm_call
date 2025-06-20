# TASK POLLING VERIFICATION TEST (WITH PROMPT TEMPLATES)

## IMPORTANT: USE EXISTING PROMPT TEMPLATES
**DO NOT RE-IMPLEMENT the logic for verification or polling!**  
Always use the existing prompt templates:
- `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-verify.md`
- `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-poll.md`

These prompt files contain all necessary instructions for verification and polling.  
**When verification or polling is required, thoroughly read and implement the instructions from the respective markdown prompt file.**

## PURPOSE
Test sequential task execution with background Claude Code verification and polling using prompt templates.
Verify that polling prevents race conditions and ensures proper task completion before proceeding.

**CORE OBJECTIVE:** Demonstrate that we can:
1. Launch a Claude Code instance in a background subprocess to verify results
2. Use a polling mechanism to wait for the background verification to complete
3. Block progression to subsequent tasks until verification confirms success
4. Prove this pattern works reliably for sequential task orchestration

**VERIFICATION GOAL:**  
Prove that the prompt templates in `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-verify.md` and `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-poll.md` can orchestrate sequential tasks, with Claude Code thoroughly reading and implementing these markdown files to manage background verification and polling, ensuring each step completes before proceeding.

## CRITICAL LIMITATIONS
- No extra Python files/modules beyond those explicitly required.
- All code and logging setup is included inline in generated scripts via prompts.
- All logs go to `task_execution.log`.
- All file paths and parameters are passed via prompt variables (no hardcoded values).
- **Do not change the logger format after initialization.**
- **Ensure only the verification script logs the source code for audit; the main script should not log its own source code.**
- **At the start and end of each run, log a clear separator and timestamp to demarcate runs.**
- **If log files from previous runs exist, archive or clear them before starting a new run, or ensure each run is clearly separated in the log.**
- **Loguru should be configured to log only to file, or if logging to stderr, document this behavior in the logs.**

---

## GLOBAL INSTRUCTION: LOGURU LOGGING SETUP

**Before starting Task 3 and beyond, ensure all generated Python scripts include the following Loguru setup at the top. All log messages must use this logger and append to `task_execution.log`. Do not change the logger format after initialization.**

```
from loguru import logger
import datetime

# Remove default handler to prevent stderr output
logger.remove()
# Add only file handler
logger.add('task_execution.log', 
           rotation='1 MB', 
           enqueue=True, 
           backtrace=True, 
           diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
```

**Note:** By removing the default handler and adding only a file handler, we prevent loguru from outputting to stderr, which avoids confusion when capturing subprocess output.

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

### Task 3: Verify Environment and Prepare Clean Log
- Log: `"🚀 NEW RUN STARTED at {datetime.now().isoformat()}"`
- Log: `"="*80` (major separator)
- Run `which python` to verify virtual environment is activated
- If the path does NOT contain `.venv`, STOP and run `source .venv/bin/activate` first
- This is MANDATORY per CLAUDE.md rules
- Check if `task_execution.log` exists from previous runs:
  ```
  if os.path.exists("task_execution.log"):
      # Archive the old log with timestamp
      archive_name = f"task_execution_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
      os.rename("task_execution.log", archive_name)
      logger.info(f"[LOG_ARCHIVED] Previous log moved to {archive_name}")
  ```

### Task 4: Create Simple Function with Output
- Log: `"📝 TASK 4 STARTED: Create simple function"`
- Log: `"-"*80` (sub-separator)
- Write `simple_add.py` containing:
  - The Loguru setup (as above) but configure it to **only** log to file, not stderr:
    ```python
    # Remove default handler to prevent stderr output
    logger.remove()
    # Add only file handler
    logger.add('task_execution.log', 
               rotation='1 MB', 
               enqueue=True, 
               backtrace=True, 
               diagnose=True,
               format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
    ```
  - A function that adds two numbers (specifically 2 + 3 = 5), logs the calculation, writes the result to `add_results.txt`, and logs completion. **Always use 2 + 3 = 5 for consistency across all runs.**
  - A main block that calls the function.
- After writing the file, log:
  ```
  logger.info("[CODE_WRITTEN] simple_add.py created.")
  ```
- Do **not** have `simple_add.py` log its own source code (i.e., don't have the script read and log itself). This prevents recursive logging where the code appears multiple times in nested formats. The verification script will handle logging the source code for analysis.
- Execute the script and log:
  ```
  logger.info("[EXECUTION] Running simple_add.py")
  result = subprocess.run([sys.executable, "simple_add.py"], capture_output=True, text=True)
  logger.info("[EXECUTION_OUTPUT]")
  logger.info(f"stdout: {result.stdout}")
  if result.stderr:
      logger.info(f"stderr (note: loguru may output here, this is not an error): {result.stderr}")
  logger.info(f"return_code: {result.returncode}")
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
- Use the prompt template at `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-verify.md`, substituting parameters as specified:
  - code_file=simple_add.py
  - result_file=add_results.txt
  - status_file=verification_status.json
  - log_file=task_execution.log
  - expected_result=5
- Execute the verification script in a background subprocess (e.g., using `subprocess.Popen` in Python), so the main workflow can proceed to polling without blocking.
- The verification script should:
  - Import and configure Loguru as in the global instruction.
  - Log start and all actions.
  - **MUST** read and log the source code of `simple_add.py` for analysis and critique (this is essential for the verification to work).
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
- Use the prompt template at `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-poll.md`, substituting parameters as specified:
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
- Log: `"="*80` (separator)

---

### Task 8: Gemini Flash Verification of Results (Final Reality Check)
- Log: `"🤖 TASK 8 STARTED: Gemini Flash verification of results"`
- Log: `"-"*80` (sub-separator)
- Create a summary file `execution_summary.txt` containing:
  ```
  EXECUTION SUMMARY
  =================
  
  Files Created:
  - simple_add.py: A Python script that adds 2 + 3
  - add_results.txt: Contains "The sum of 2 and 3 is 5"
  - verification_status.json: Contains verification results with status "pass"
  - final_answer.txt: Contains "Paris"
  - task_execution.log: Contains detailed logs of all operations
  
  Key Results:
  - Background verification process completed successfully
  - Polling mechanism detected completion and allowed progression
  - Sequential execution was maintained throughout
  - All expected files were created with correct content
  ```
- Use the prompt template at `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/ask-gemini-flash.md` to verify:
  - That all listed files actually exist
  - That the contents match what's claimed
  - That the execution flow was logical and sequential
  - That there's no evidence of hallucination or false claims
- Log the Gemini Flash response
- Log: `"✅ TASK 8 COMPLETED: Independent verification complete"`
- Log: `"="*80` (separator)
- Log: `"🏁 RUN COMPLETED at {datetime.now().isoformat()}"`
- Log: `"="*80` (major separator)

---

## VERIFICATION CRITERIA
- All tasks execute in sequence (no parallel execution).
- Verification runs in a background subprocess without blocking.
- Polling prevents Task 7 from starting prematurely.
- All output files contain expected content:
  - `add_results.txt`: Contains addition results.
  - `verification_status.json`: Contains "pass" status with critique.
  - `final_answer.txt`: Contains "Paris".
  - `task_execution.log`: Contains logs from all steps with clear separation between runs.
  - `execution_summary.txt`: Contains accurate summary of execution.
- Gemini Flash confirms no hallucination occurred and all results are real.

---

## SUCCESS INDICATORS
- Sequential execution maintained.
- Background verification completes without manual intervention.
- Polling mechanism works correctly.
- JSON status file updates properly.
- All output files created with correct content.
- Gemini Flash independently confirms results are real and not hallucinated.

---

## NOTES
- No extra Python modules or files beyond those explicitly required.
- All code and logging setup is included inline in generated scripts via prompts.
- All logs go to `task_execution.log`.
- All file paths and parameters are passed via prompt variables (no hardcoded values).
- **CRITICAL**: The verification and polling prompt files already exist at:
  - `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-verify.md`
  - `/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/commands/claude-poll.md`
  
  These should NOT be re-implemented. **Always thoroughly read and implement the instructions from those files.**
- **If logs are captured in stderr, clarify in logs that this is expected and not an error.**
- **At the start and end of each run, log a clear separator and timestamp.**

