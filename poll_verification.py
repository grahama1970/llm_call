import json
import time
import os
import sys
from datetime import datetime
from loguru import logger

# Parameters
status_file = "verification_status.json"
expected_status = "pass"
timeout = 600
log_file = "task_execution.log"

# Configure logger with clear format
logger.add(log_file, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("🔄 TASK 6 STARTED: Polling for verification completion")
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
                logger.info("✅ TASK 6 COMPLETED: Verification passed")
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
        logger.info("❌ TASK 6 FAILED: Timeout reached")
        logger.info("=" * 80)
        sys.exit(1)
    
    # Wait before next poll
    time.sleep(1)