#!/usr/bin/env python3
"""
Sequential task execution with comprehensive logging to prevent hallucination.
This script provides timestamped proof of actual execution.
"""
import time
import subprocess
import sys
from pathlib import Path
from verification_logger import TaskVerificationLogger, logger, LOG_FILE

def main():
    logger.info("=" * 60)
    logger.info("🚀 STARTING SEQUENTIAL TASK EXECUTION WITH LOGGING")
    logger.info(f"📋 Log file: {LOG_FILE}")
    logger.info("=" * 60)
    
    # Task 1: Create Simple Function
    task1 = TaskVerificationLogger("Task 1: Create Simple Function")
    
    logger.info("📝 Creating simple_add.py...")
    task1.log_file_operation("create", "simple_add.py")
    
    # Execute the function
    returncode, stdout, stderr = task1.log_command_execution("python simple_add.py")
    if returncode != 0:
        logger.error("❌ Task 1 failed!")
        return False
    
    # Verify output file was created
    if not task1.log_file_content_verification("add_results.txt", "Addition result: 8"):
        logger.error("❌ Task 1 output verification failed!")
        return False
    
    task1.complete_task()
    
    # Task 2: Launch Background Verification
    task2 = TaskVerificationLogger("Task 2: Background Verification")
    
    logger.info("📝 Creating initial JSON status file...")
    task2.log_file_operation("create", "verification_status.json")
    
    logger.info("🚀 Launching background Claude verification...")
    # Launch background process
    returncode, stdout, stderr = task2.log_command_execution("python run_verification.py &")
    
    # Give background process time to start
    time.sleep(1)
    
    task2.complete_task()
    
    # Task 3: Poll for Verification
    task3 = TaskVerificationLogger("Task 3: Poll for Verification")
    
    logger.info("🔄 Starting polling for verification completion...")
    max_polls = 10
    poll_count = 0
    
    while poll_count < max_polls:
        poll_count += 1
        start_poll = time.time()
        
        status_ok, actual_status = task3.log_json_status_check("verification_status.json", "pass")
        
        poll_duration = time.time() - start_poll
        task3.log_polling_iteration(poll_count, actual_status, poll_duration)
        
        if status_ok:
            logger.info("✅ Polling successful - verification passed!")
            break
        
        if poll_count < max_polls:
            logger.info("⏳ Waiting 2 seconds before next poll...")
            time.sleep(2)
    else:
        logger.error("❌ Polling timed out!")
        return False
    
    task3.complete_task()
    
    # Task 4: Final Answer (Only After Verification)
    task4 = TaskVerificationLogger("Task 4: Answer Question")
    
    logger.info("❓ Answering capital question...")
    task4.log_file_operation("create", "final_answer.txt")
    
    # Write answer
    Path("final_answer.txt").write_text("Paris")
    
    if not task4.log_file_content_verification("final_answer.txt", "Paris"):
        logger.error("❌ Task 4 verification failed!")
        return False
    
    task4.complete_task()
    
    logger.info("=" * 60)
    logger.info("🎉 ALL SEQUENTIAL TASKS COMPLETED SUCCESSFULLY")
    logger.info("📋 Raw log file available for verification")
    logger.info("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)