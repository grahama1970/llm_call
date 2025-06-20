import json
import subprocess
import os
import sys
from datetime import datetime
from loguru import logger

# Remove default handler to prevent stderr output
logger.remove()
# Add only file handler
logger.add('task_execution.log', rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

# Parameters
code_file = "simple_add.py"
result_file = "add_results.txt"
status_file = "verification_status.json"
expected_result = "5"

logger.info("🔬 BACKGROUND CLAUDE VERIFICATION STARTED")
logger.info("-" * 80)

# Initialize verification data
verification_data = {
    "datetime": datetime.utcnow().isoformat() + "Z",
    "critique": "",
    "tweaks": "",
    "status": "fail",
    "stdout": "",
    "stderr": ""
}

try:
    # Read and analyze the code file
    logger.info(f"[CODE_ANALYSIS] Reading {code_file}")
    with open(code_file, 'r') as f:
        code_content = f.read()
    
    logger.info("```python")
    logger.info(code_content)
    logger.info("```")
    
    # Critique the code
    critique_points = []
    tweaks = []
    
    # Check for function definition
    if "def add_numbers(" in code_content:
        critique_points.append("✓ Function add_numbers found and properly defined.")
    else:
        critique_points.append("✗ Function add_numbers not found.")
    
    # Check for single-letter variable names
    if "def add_numbers(a, b):" in code_content:
        critique_points.append("✗ Single-letter variable names (a, b) reduce readability.")
        tweaks.append("""Use descriptive names:
```python
def add_numbers(num1, num2):
    \"\"\"Add two numbers and return the result.\"\"\"
    return num1 + num2
```""")
    
    # Check for comments
    if code_content.count("#") > 2 or '"""' in code_content:
        critique_points.append("✓ Code contains comments/docstrings for readability.")
    else:
        critique_points.append("✗ Limited comments found; consider adding more explanatory comments.")
        tweaks.append("""Add function-level comments:
```python
# Add two numbers and return the sum
def add_numbers(a, b):
    \"\"\"Add two numbers and return the result.\"\"\"
    return a + b
```""")
    
    # Check for error handling
    if "try:" in code_content and "except" in code_content:
        critique_points.append("✓ Error handling found for file operations.")
    else:
        critique_points.append("✗ No try-except blocks for file operations.")
        tweaks.append("""Add error handling for file operations:
```python
try:
    with open('add_results.txt', 'w') as f:
        f.write(f"The sum of 2 and 3 is {result}")
except IOError as e:
    logger.error(f"Failed to write results: {e}")
```""")
    
    # Check line lengths (simplified check)
    long_lines = [i+1 for i, line in enumerate(code_content.split('\n')) if len(line) > 79]
    if long_lines:
        critique_points.append(f"✗ Lines {long_lines} exceed 79 characters (PEP 8).")
    else:
        critique_points.append("✓ All lines comply with PEP 8 line length guidelines.")
    
    verification_data["critique"] = "\n".join(critique_points)
    verification_data["tweaks"] = "\n\n".join(tweaks) if tweaks else "No improvements needed."
    
    # Execute the script
    logger.info(f"[EXECUTION] Running python {code_file}")
    try:
        result = subprocess.run(
            ["python", code_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        verification_data["stdout"] = result.stdout
        verification_data["stderr"] = result.stderr
        
        logger.info("[EXECUTION_OUTPUT]")
        logger.info(f"stdout: {result.stdout}")
        logger.info(f"stderr: {result.stderr}")
        logger.info(f"return_code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        verification_data["stderr"] = "Script execution timed out after 10 seconds"
        logger.error("Script execution timed out")
    
    # Verify the output file
    logger.info(f"[FILE_VERIFICATION] Reading {result_file}")
    try:
        with open(result_file, 'r') as f:
            file_content = f.read()
        
        logger.info("```")
        logger.info(file_content)
        logger.info("```")
        
        # Check if the result matches expected
        if expected_result in file_content:
            verification_data["status"] = "pass"
            logger.info(f"✓ Output matches expected result: {expected_result}")
        else:
            logger.error(f"✗ Output does not match expected result: {expected_result}")
            
    except FileNotFoundError:
        logger.error(f"Output file {result_file} not found")
        verification_data["stderr"] += f"\nOutput file {result_file} not found"
        
except Exception as e:
    logger.error(f"Verification error: {e}")
    verification_data["stderr"] += f"\nVerification error: {str(e)}"

# Write status atomically
logger.info("[JSON_UPDATE] Writing final verification status")
logger.info("```json")
logger.info(json.dumps(verification_data, indent=2))
logger.info("```")

# Write to temporary file first, then rename (atomic operation)
temp_file = status_file + ".tmp"
with open(temp_file, 'w') as f:
    json.dump(verification_data, f, indent=2)
os.rename(temp_file, status_file)

logger.info(f"🔬 BACKGROUND VERIFICATION COMPLETE: {verification_data['status']}")
logger.info("=" * 80)