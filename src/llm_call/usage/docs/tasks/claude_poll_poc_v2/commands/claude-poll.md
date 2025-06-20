# Claude Poll Command

Generate a Python polling script that waits for a background process to write a JSON status file.

## Parameters:
- `status_file`: (string) The full path to the JSON file to poll
- `expected_status`: (string) The value in the 'status' key that indicates success
- `timeout`: (integer) The maximum number of seconds to wait before failing
- `log_file`: (string) The path to the log file for detailed logging

## Expected Output:
- A Python script that polls for the status file
- Logs detailed progress to the specified log file
- Exits with code 0 on success, 1 on failure/timeout

## Code Example:
```python
# This script is generated from the claude-poll.md template.
import json
import time
import os
import sys
from datetime import datetime
from loguru import logger

# Parameters injected by the orchestrator
status_file = "{{ params.status_file }}"
expected_status = "{{ params.expected_status }}"
timeout = int("{{ params.timeout }}")
log_file = "{{ params.log_file }}"

# Configure logger
logger.remove()
logger.add(log_file, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
   format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("🔄 POLLING STARTED: Waiting for verification completion")
logger.info(f" - Status File: {status_file}")
logger.info(f" - Expected Status: '{expected_status}'")
logger.info(f" - Timeout: {timeout}s")
logger.info("-" * 80)

start_time = time.time()
attempt = 0

while True:
    attempt += 1
    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    logger.info(f"[POLL_ATTEMPT] #{attempt} at {current_time}")

    if os.path.exists(status_file):
        try:
            with open(status_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"[FILE_READ] {status_file} content:")
            logger.info("```json\n" + json.dumps(data, indent=2) + "\n```")
            
            current_status = data.get('status', 'unknown')
            
            if current_status == expected_status:
                logger.info(f"✅ POLLING SUCCESS: Found expected status '{current_status}'")
                logger.info("=" * 80)
                sys.exit(0)
            else:
                logger.warning(f"[POLL_RESULT] Status is '{current_status}', waiting for '{expected_status}'...")

        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] Invalid JSON in {status_file}: {e}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to read or parse status file: {e}")
    else:
        logger.info(f"[POLL_RESULT] File not found yet. Waiting...")

    if time.time() - start_time > timeout:
        logger.error(f"[ERROR] Timeout after {timeout} seconds. Polling failed.")
        logger.info("=" * 80)
        sys.exit(1)

    time.sleep(2) # Using a 2-second interval for less log spam
```

---
<!--This section is for the orchestrating LLM. It defines how to fix this prompt if things go wrong.-->
## [SELF_CORRECTION]

**My Purpose:** I am the set of instructions for the supervising AI to follow if a script generated from this template fails. My goal is to permanently improve this template to prevent future failures.

**If the generated script fails, you MUST:**

1.  **Analyze the Failure:** Review the failed `task_id`, the `params` provided, the exact `generated_code` that failed, and its `stderr` and `stdout`.

2.  **Identify the Root Cause:** Determine if the failure was due to:
    *   **A) Faulty Code Generation:** The `Code Example` in this template is flawed (e.g., incorrect file handling, timing issues).
    *   **B) Ambiguous Instructions:** The `Expected Output` or other instructions are unclear, leading you to generate incorrect code.
    *   **C) An External Factor:** The environment is misconfigured or the status file was not created by the background process.

3.  **Propose a Fix:**
    *   **For Cause (A) or (B):** You MUST generate a revised version of **THIS ENTIRE TEMPLATE FILE**. Do not just fix the script; fix the source of the error.
    *   **For Cause (C):** Do not modify this template. Instead, report the external factor clearly so a human can intervene.

4.  **Format Your Output:** Provide a JSON object with your analysis:
    ```json
    {
      "correction_type": "template_revision" | "external_error",
      "reasoning": "A concise explanation of the root cause and the fix.",
      "revised_template_content": "The full, new content for this .md file. (null if external_error)"
    }
    ```
5.  **NEVER simulate fixes.** Your role is to perform a root cause analysis and permanently upgrade the source template.