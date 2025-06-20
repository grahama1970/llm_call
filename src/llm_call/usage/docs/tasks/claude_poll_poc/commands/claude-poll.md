# Claude Poll Command

Generate a Python polling script that waits for a background Claude Code process to write a JSON status file: $ARGUMENTS

## Expected Output:
- Generate a Python script that polls for a JSON status file based on $ARGUMENTS
- Wait for specified file to exist, then parse and check status
- Log all polling attempts and results to the specified log file
- Exit with appropriate code when expected status is reached or timeout occurs
- Use $ARGUMENTS to determine file name, expected status, timeout, log file, etc.

## Code Example:
```python
# Generate a Python polling script with clear logging
# Parameters extracted from $ARGUMENTS

import json
import time
import os
import sys
from datetime import datetime
from loguru import logger

# Extract parameters from command arguments
status_file = "$status_file"
expected_status = "$expected_status"
timeout = int("$timeout")
log_file = "$log_file"

# Configure logger with clear format
# Remove default handler to prevent stderr output
logger.remove()
# Add only file handler
logger.add(log_file, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
      format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("🔄 POLLING STARTED: Waiting for verification completion")
logger.info("-" * 80)

start_time = time.time()
attempt = 0

while True:
  attempt += 1
  current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
  logger.info(f"[POLL_ATTEMPT] #{attempt} at {current_time}")
   
  # Check if file exists
  if os.path.exists(status_file):
    try:
      with open(status_file, 'r') as f:
        data = json.load(f)
       
      # Log the file content
      logger.info(f"[FILE_READ] {status_file}:")
      logger.info("```json")
      logger.info(json.dumps(data, indent=2))
      logger.info("```")
       
      # Check status
      status = data.get('status', 'unknown')
       
      if status == expected_status:
        logger.info(f"[POLL_RESULT] Status: {status} (SUCCESS!)")
        logger.info("✅ POLLING COMPLETED: Verification passed")
        logger.info("=" * 80)
        sys.exit(0)
      else:
        logger.info(f"[POLL_RESULT] Status: {status} (waiting...)")
     
    except json.JSONDecodeError as e:
      logger.error(f"[ERROR] Invalid JSON in {status_file}: {e}")
    except Exception as e:
      logger.error(f"[ERROR] Failed to read status file: {e}")
  else:
    logger.info(f"[POLL_RESULT] File not found (waiting...)")
   
  # Check timeout
  elapsed = time.time() - start_time
  if elapsed > timeout:
    logger.error(f"[ERROR] Timeout after {timeout} seconds")
    logger.info("❌ POLLING FAILED: Timeout reached")
    logger.info("=" * 80)
    sys.exit(1)
   
  # Wait before next poll
  time.sleep(1)
```

## Usage for Claude Code Background Tasks:
This command generates polling scripts specifically for Claude Code instances running in the background that write JSON status files when complete.

## Common Status Values:
- `"in-progress"`: Background task is still running
- `"pass"`: Verification completed successfully  
- `"fail"`: Verification failed
- `"completed"`: General completion status
- `"success"`: Alternative success status

## Environment Requirements:
- `python3`: Python 3.x interpreter
- `loguru`: Python logging library (install with `uv add loguru` or `pip install loguru`)

## Usage Examples:
- `/user:claude-poll status_file=verification_status.json expected_status=pass timeout=600 log_file=task_execution.log` 
- `/user:claude-poll status_file=verification_status.json expected_status=pass timeout=300 log_file=task_execution.log`
- `/user:claude-poll status_file=completion.json expected_status=completed timeout=600 log_file=task_execution.log`
- `/user:claude-poll status_file=background_verification.json expected_status=success timeout=300 log_file=task_execution.log`

## Notes:
- Designed specifically for Claude Code background task polling
- Simple, reliable approach without complex features
- Validates JSON before parsing
- Provides clear, structured logging for all polling attempts
- Logs are parseable by agents, humans, and verification models
- Timeout prevents infinite waiting on stuck Claude processes
- 1-second polling interval for simplicity (no exponential backoff in this POC)