from loguru import logger
import json
import subprocess
import datetime
import os
import sys

logger.add('task_execution.log', 
           rotation='1 MB', 
           enqueue=True, 
           backtrace=True, 
           diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("🔬 TASK 5 STARTED: Launch background verification")
logger.info("-"*80)

# Write initial status
with open("verification_status.json", "w") as f:
    json.dump({"status": "in-progress"}, f, indent=2)

logger.info("[JSON_WRITTEN] verification_status.json:")
logger.info("```json")
with open("verification_status.json", "r") as f:
    logger.info(f.read())
logger.info("```")

# Create the verification script based on the template
verification_script = """from loguru import logger
import json
import subprocess
import datetime
import os
import sys

logger.add('task_execution.log', rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")

logger.info("🔬 BACKGROUND CLAUDE VERIFICATION STARTED")
logger.info("-" * 80)

# Read the Python file and critique it
logger.info("[CODE_ANALYSIS] Reading simple_add.py")
with open("simple_add.py", "r") as f:
    code_content = f.read()
logger.info("```python")
logger.info(code_content)
logger.info("```")

# Analyze code quality
critique = []
tweaks = []

# Check for readability issues
if " a:" in code_content or " b:" in code_content:
    critique.append("Single-letter variable names (a, b) reduce readability")
    tweaks.append('''Use descriptive names:
```python
def add_numbers(num1: int, num2: int) -> int:
    \"\"\"Add two numbers and return the result.\"\"\"
    logger.info(f"Calculating {num1} + {num2}")
    result = num1 + num2
```''')

# Check for comments
if code_content.count("#") < 3 and '\"\"\"' not in code_content:
    critique.append("Limited comments found; consider adding more explanatory comments")
    tweaks.append('''Add comments:
```python
# Function to add two numbers and log the operation
def add_numbers(a: int, b: int) -> int:
    \"\"\"Add two numbers and return the result.\"\"\"
    # Log the calculation for debugging
    logger.info(f"Calculating {a} + {b}")
```''')

# Check for error handling
if "try:" not in code_content:
    critique.append("No error handling for file operations")
    tweaks.append('''Add error handling:
```python
try:
    with open("add_results.txt", "w") as f:
        f.write(f"The sum of {a} and {b} is {result}")
    logger.info("Result written to add_results.txt")
except IOError as e:
    logger.error(f"Failed to write results: {e}")
```''')

# Execute the script
logger.info("[EXECUTION] Running python simple_add.py")
try:
    result = subprocess.run(
        ["python", "simple_add.py"],
        capture_output=True,
        text=True,
        timeout=10
    )
    stdout = result.stdout
    stderr = result.stderr
    return_code = result.returncode
except subprocess.TimeoutExpired:
    stdout = ""
    stderr = "Script execution timed out after 10 seconds"
    return_code = -1

logger.info("[EXECUTION_OUTPUT]")
logger.info(f"stdout: {stdout}")
logger.info(f"stderr: {stderr}")
logger.info(f"return_code: {return_code}")

# Read and verify the output file
logger.info("[FILE_VERIFICATION] Reading add_results.txt")
try:
    with open("add_results.txt", "r") as f:
        file_content = f.read()
    logger.info("```")
    logger.info(file_content)
    logger.info("```")
    
    # Check if result matches expected
    expected_result = 5
    status = "fail"
    if "5" in file_content and return_code == 0:
        status = "pass"
        critique.append("Code executed successfully and produced expected result")
    else:
        critique.append(f"Output does not match expected result {expected_result}")
except FileNotFoundError:
    file_content = ""
    status = "fail"
    critique.append("Output file add_results.txt not found")

# Prepare verification data
verification_data = {
    "datetime": datetime.datetime.utcnow().isoformat() + "Z",
    "critique": ". ".join(critique) if critique else "No issues found",
    "tweaks": "\\n\\n".join(tweaks) if tweaks else "No improvements suggested",
    "status": status,
    "stdout": stdout,
    "stderr": stderr
}

logger.info("[JSON_UPDATE] Writing final verification status")
logger.info("```json")
logger.info(json.dumps(verification_data, indent=2))
logger.info("```")

# Write JSON atomically
temp_file = "verification_status.json.tmp"
with open(temp_file, "w") as f:
    json.dump(verification_data, indent=2, fp=f)
os.rename(temp_file, "verification_status.json")

logger.info(f"🔬 BACKGROUND VERIFICATION COMPLETE: {status}")
logger.info("=" * 80)
"""

# Write the verification script
with open("verify_task.py", "w") as f:
    f.write(verification_script)

logger.info("Created verify_task.py")

# Launch the verification script in background
logger.info("Launching background verification...")
process = subprocess.Popen([sys.executable, "verify_task.py"])
logger.info(f"Background verification launched with PID: {process.pid}")

logger.info("="*80)