#!/usr/bin/env python3
"""
Verification logger that captures all task execution with timestamps.
Prevents hallucination by logging real operations as they happen.
"""
import os
import subprocess
import json
from datetime import datetime
from loguru import logger
from pathlib import Path

# Configure loguru to write to shared log file with precise timestamps
LOG_FILE = "/home/graham/workspace/experiments/llm_call/task_execution.log"
logger.remove()  # Remove default handler
logger.add(
    LOG_FILE, 
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name}:{function}:{line} | {message}",
    rotation="10 MB", 
    retention="7 days", 
    level="DEBUG"
)
logger.add(
    lambda msg: print(msg, end=""), 
    format="{time:HH:mm:ss.SSS} | {level:<8} | {message}",
    level="INFO"
)

class TaskVerificationLogger:
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.start_time = datetime.now()
        logger.info(f"🚀 Starting task: {task_name} at {self.start_time.isoformat()}")
    
    def log_file_operation(self, operation: str, filepath: str) -> bool:
        """Log file operations with actual verification."""
        try:
            path = Path(filepath)
            exists_before = path.exists()
            
            logger.info(f"📁 {operation}: {filepath}")
            logger.debug(f"   File exists before: {exists_before}")
            
            if operation == "create" and exists_before:
                logger.warning(f"   ⚠️ File already exists!")
            
            return True
        except Exception as e:
            logger.error(f"   ❌ File operation failed: {e}")
            return False
    
    def log_command_execution(self, command: str, cwd: str = None) -> tuple:
        """Log actual command execution with real outputs."""
        logger.info(f"🔧 Executing: {command}")
        logger.debug(f"   Working directory: {cwd or os.getcwd()}")
        
        try:
            start = datetime.now()
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd
            )
            end = datetime.now()
            duration = (end - start).total_seconds()
            
            logger.info(f"   ⏱️ Duration: {duration:.2f}s")
            logger.info(f"   📤 Exit code: {result.returncode}")
            
            if result.stdout:
                logger.info(f"   📋 STDOUT:")
                for line in result.stdout.strip().split('\n'):
                    logger.info(f"      {line}")
            
            if result.stderr:
                logger.warning(f"   🚨 STDERR:")
                for line in result.stderr.strip().split('\n'):
                    logger.warning(f"      {line}")
            
            return result.returncode, result.stdout, result.stderr
            
        except Exception as e:
            logger.error(f"   💥 Command execution failed: {e}")
            return -1, "", str(e)
    
    def log_file_content_verification(self, filepath: str, expected_content: str = None) -> bool:
        """Verify file content actually exists."""
        try:
            path = Path(filepath)
            if not path.exists():
                logger.error(f"   ❌ File does not exist: {filepath}")
                return False
            
            content = path.read_text()
            logger.info(f"📖 File content verification: {filepath}")
            logger.debug(f"   Size: {len(content)} chars")
            logger.debug(f"   Content preview: {repr(content[:100])}")
            
            if expected_content and expected_content not in content:
                logger.error(f"   ❌ Expected content not found: {expected_content}")
                return False
            
            logger.info(f"   ✅ File content verified")
            return True
            
        except Exception as e:
            logger.error(f"   💥 File verification failed: {e}")
            return False
    
    def log_json_status_check(self, json_file: str, expected_status: str) -> tuple:
        """Log actual JSON file parsing and status checking."""
        logger.info(f"🔍 Checking JSON status: {json_file}")
        
        try:
            if not Path(json_file).exists():
                logger.error(f"   ❌ JSON file does not exist")
                return False, "file_not_found"
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            actual_status = data.get('status', 'unknown')
            logger.info(f"   📊 Status found: '{actual_status}'")
            logger.info(f"   🎯 Expected: '{expected_status}'")
            
            if actual_status == expected_status:
                logger.info(f"   ✅ Status matches!")
                return True, actual_status
            else:
                logger.warning(f"   ⚠️ Status mismatch")
                return False, actual_status
                
        except json.JSONDecodeError as e:
            logger.error(f"   💥 Invalid JSON: {e}")
            return False, "invalid_json"
        except Exception as e:
            logger.error(f"   💥 JSON check failed: {e}")
            return False, "error"
    
    def log_polling_iteration(self, iteration: int, status: str, wait_time: float):
        """Log each polling iteration with real timing."""
        logger.info(f"🔄 Poll iteration {iteration}: status='{status}', waited={wait_time:.1f}s")
    
    def complete_task(self):
        """Mark task completion with duration."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        logger.info(f"🏁 Task '{self.task_name}' completed in {duration:.2f}s")
        logger.info(f"   Started: {self.start_time.isoformat()}")
        logger.info(f"   Ended: {end_time.isoformat()}")

# Usage example
if __name__ == "__main__":
    # Demo of how to use the logger
    task_logger = TaskVerificationLogger("Demo Task")
    
    # Log file creation
    task_logger.log_file_operation("create", "demo.txt")
    
    # Log command execution
    returncode, stdout, stderr = task_logger.log_command_execution("echo 'Hello World'")
    
    # Complete task
    task_logger.complete_task()