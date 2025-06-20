#!/usr/bin/env python3
"""
Claude Code script to create verification JSON file.
This will be executed by background Claude Code instance.
"""
import json
import subprocess
import sys
from datetime import datetime

def main():
    # Run the simple_add.py and capture output
    try:
        result = subprocess.run([sys.executable, "simple_add.py"], 
                              capture_output=True, text=True)
        stdout = result.stdout
        stderr = result.stderr
        returncode = result.returncode
    except Exception as e:
        stdout = ""
        stderr = str(e)
        returncode = -1
    
    # Analyze the code file
    try:
        with open("simple_add.py", "r") as f:
            code_content = f.read()
        code_has_function = "def add_numbers" in code_content
        code_has_main = 'if __name__ == "__main__"' in code_content
    except:
        code_has_function = False
        code_has_main = False
    
    # Check output file
    try:
        with open("add_results.txt", "r") as f:
            output_content = f.read()
        has_result = "Result: 8" in output_content
        has_success = "successfully" in output_content
    except:
        has_result = False
        has_success = False
    
    # Determine status
    if returncode == 0 and code_has_function and code_has_main and has_result:
        status = "pass"
        critique = "✅ Code quality: Good (has function, main block). ✅ Execution: Successful with correct output. ✅ Exit code: 0 (success)"
    else:
        status = "fail"
        critique = f"❌ Issues found: returncode={returncode}, has_function={code_has_function}, has_main={code_has_main}, has_result={has_result}"
    
    # Create the verification JSON
    verification_data = {
        "datetime": datetime.now().isoformat(),
        "critique": critique,
        "status": status,
        "stdout": stdout,
        "stderr": stderr
    }
    
    # Write to verification_status.json
    with open("verification_status.json", "w") as f:
        json.dump(verification_data, f, indent=2)
    
    print(f"Verification complete. Status: {status}")
    return status == "pass"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)