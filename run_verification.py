#!/usr/bin/env python3
"""
Background verification script that analyzes simple_add.py and updates verification_status.json
"""
import json
import subprocess
import sys
from datetime import datetime
import os
from verification_logger import TaskVerificationLogger, logger

def run_code_analysis():
    """Run the simple_add.py and capture output."""
    try:
        result = subprocess.run([sys.executable, "simple_add.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def analyze_code_file():
    """Analyze the simple_add.py file."""
    try:
        with open("simple_add.py", "r") as f:
            code_content = f.read()
        
        # Basic code analysis
        has_function = "def add_two_numbers" in code_content
        has_main_block = 'if __name__ == "__main__"' in code_content
        has_type_hints = ": int" in code_content
        has_docstring = '"""' in code_content
        
        analysis = {
            "has_function": has_function,
            "has_main_block": has_main_block, 
            "has_type_hints": has_type_hints,
            "has_docstring": has_docstring,
            "file_exists": True
        }
        
        return analysis
    except Exception as e:
        return {"error": str(e), "file_exists": False}

def check_output_file():
    """Check if add_results.txt was created and has expected content."""
    try:
        with open("add_results.txt", "r") as f:
            content = f.read()
        
        has_result = "Addition result: 8" in content
        has_calculation = "5 + 3 = 8" in content
        has_success = "successfully" in content
        
        return {
            "file_exists": True,
            "has_result": has_result,
            "has_calculation": has_calculation,
            "has_success": has_success,
            "content": content.strip()
        }
    except Exception as e:
        return {"file_exists": False, "error": str(e)}

def update_verification_status():
    """Update the verification status JSON file."""
    logger.info("🔬 Starting verification analysis...")
    
    # Run analysis
    logger.info("🔬 Running code execution analysis...")
    returncode, stdout, stderr = run_code_analysis()
    logger.info(f"🔬 Code execution result: returncode={returncode}")
    
    logger.info("🔬 Analyzing code file structure...")
    code_analysis = analyze_code_file()
    logger.info(f"🔬 Code analysis: {code_analysis}")
    
    logger.info("🔬 Checking output file...")
    output_analysis = check_output_file()
    logger.info(f"🔬 Output analysis: {output_analysis}")
    
    # Determine overall status
    code_quality_good = (
        code_analysis.get("has_function", False) and
        code_analysis.get("has_main_block", False) and
        code_analysis.get("has_type_hints", False)
    )
    
    output_correct = (
        output_analysis.get("file_exists", False) and
        output_analysis.get("has_result", False) and
        returncode == 0
    )
    
    overall_status = "pass" if (code_quality_good and output_correct) else "fail"
    
    # Create critique
    critique_parts = []
    if code_quality_good:
        critique_parts.append("✅ Code quality: Good (has function, main block, type hints)")
    else:
        critique_parts.append("❌ Code quality issues found")
    
    if output_correct:
        critique_parts.append("✅ Execution: Successful with correct output")
    else:
        critique_parts.append("❌ Execution or output issues")
    
    if returncode == 0:
        critique_parts.append("✅ Exit code: 0 (success)")
    else:
        critique_parts.append(f"❌ Exit code: {returncode}")
    
    critique = "; ".join(critique_parts)
    
    # Update JSON file
    status_data = {
        "datetime": datetime.now().isoformat(),
        "critique": critique,
        "status": overall_status,
        "stdout": stdout,
        "stderr": stderr,
        "code_analysis": code_analysis,
        "output_analysis": output_analysis
    }
    
    logger.info(f"🔬 Writing verification status: {overall_status}")
    with open("verification_status.json", "w") as f:
        json.dump(status_data, f, indent=2)
    
    logger.info(f"🔬 Verification JSON file updated")
    print(f"Verification complete. Status: {overall_status}")
    return overall_status

if __name__ == "__main__":
    # Initialize background verification logger
    bg_logger = TaskVerificationLogger("Background Claude Verification")
    logger.info("🔬 BACKGROUND CLAUDE INSTANCE STARTED")
    
    status = update_verification_status()
    
    logger.info(f"🔬 BACKGROUND VERIFICATION COMPLETED: {status}")
    bg_logger.complete_task()
    
    sys.exit(0 if status == "pass" else 1)