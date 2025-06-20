"""
Module: verification_workflow.py
Description: Practical verification workflow for Claude Code test outputs

External Dependencies:
- None (uses only standard library and local modules)

Sample Input:
>>> test_command = "pytest tests/test_math.py"

Expected Output:
>>> result = run_and_verify(test_command)
>>> print(result['summary'])
'2 tests: 1 passed, 1 failed (50.0% success rate)'

Example Usage:
>>> from verification_workflow import run_and_verify
>>> result = run_and_verify("pytest tests/")
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
from loguru import logger

from .simple_verifier import verify_simple, verify_with_gemini, save_verification_report


def run_tests(command: str) -> Tuple[str, int]:
    """Run tests and capture raw output"""
    logger.info(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        output = result.stdout + "\n" + result.stderr
        return output, result.returncode
        
    except subprocess.TimeoutExpired:
        return "ERROR: Test execution timed out after 60 seconds", 1
    except Exception as e:
        return f"ERROR: Failed to run tests: {e}", 1


def run_and_verify(command: str, use_gemini: bool = True) -> Dict:
    """Complete workflow: run tests and verify results"""
    
    # Step 1: Run tests and capture output
    output, exit_code = run_tests(command)
    
    # Step 2: Always do simple pattern matching first
    simple_results = verify_simple(output)
    
    # Step 3: Try Gemini verification if enabled
    gemini_results = None
    if use_gemini and 'GOOGLE_API_KEY' in os.environ:
        try:
            gemini_results = verify_with_gemini(output)
        except Exception as e:
            logger.warning(f"Gemini verification failed: {e}")
    
    # Step 4: Determine final results
    if gemini_results and not gemini_results.get('error'):
        final_results = gemini_results
        verification_method = 'gemini'
    else:
        final_results = simple_results
        verification_method = 'pattern_matching'
    
    # Step 5: Create comprehensive report
    report = {
        'command': command,
        'exit_code': exit_code,
        'verification_method': verification_method,
        'results': final_results,
        'simple_check': simple_results,
        'gemini_check': gemini_results,
        'timestamp': datetime.now().isoformat(),
        'summary': f"{final_results['total']} tests: {final_results['passed']} passed, "
                  f"{final_results['failed']} failed ({final_results.get('accuracy', 0):.1f}% success rate)"
    }
    
    # Step 6: Save report
    report_path = save_verification_report(output, report)
    logger.info(f"Verification report saved to: {report_path}")
    
    # Step 7: Print summary
    print("\n" + "="*60)
    print("TEST VERIFICATION SUMMARY")
    print("="*60)
    print(f"Command: {command}")
    print(f"Exit Code: {exit_code}")
    print(f"Verification Method: {verification_method}")
    print(f"Results: {report['summary']}")
    
    if final_results.get('suspicious'):
        print(f"⚠️  WARNING: {final_results.get('warning')}")
    
    print("="*60 + "\n")
    
    return report


def verify_claude_output(claude_output: str) -> Dict:
    """Verify Claude Code's test output claims"""
    
    # Look for common Claude hallucination patterns
    hallucination_patterns = [
        (r"All tests passed", "claims all passed"),
        (r"✅ PASSED", "uses success emoji"),
        (r"100% passing", "claims perfect score"),
        (r"Success!", "generic success claim")
    ]
    
    warnings = []
    for pattern, description in hallucination_patterns:
        if re.search(pattern, claude_output, re.IGNORECASE):
            warnings.append(f"Claude {description}")
    
    # Extract any actual test output
    test_output_match = re.search(r'```[\s\S]*?```', claude_output)
    if test_output_match:
        actual_output = test_output_match.group(0).strip('`')
        actual_results = verify_simple(actual_output)
    else:
        actual_results = {'error': 'No test output found in Claude response'}
    
    return {
        'claude_claims': warnings,
        'actual_results': actual_results,
        'likely_hallucination': len(warnings) > 0 and actual_results.get('failed', 0) > 0
    }


# Validation function
if __name__ == "__main__":
    import os
    import re
    
    # Test the workflow with a mock test output
    mock_output = """
    pytest tests/test_example.py
    =================== test session starts ===================
    collected 3 items
    
    tests/test_example.py::test_one PASSED                 [ 33%]
    tests/test_example.py::test_two FAILED                 [ 66%]
    tests/test_example.py::test_three ERROR                [100%]
    
    =================== 1 failed, 1 passed, 1 error in 0.5s ===================
    """
    
    # Mock the run_tests function for validation
    def mock_run_tests(command):
        return mock_output, 1
    
    # Temporarily replace run_tests
    original_run_tests = run_tests
    globals()['run_tests'] = mock_run_tests
    
    # Test the workflow
    result = run_and_verify("pytest tests/test_example.py", use_gemini=False)
    
    # Restore original function
    globals()['run_tests'] = original_run_tests
    
    # Validate results
    assert result['results']['passed'] == 1, f"Expected 1 passed, got {result['results']['passed']}"
    assert result['results']['failed'] == 2, f"Expected 2 failed (1 fail + 1 error), got {result['results']['failed']}"
    assert result['exit_code'] == 1, f"Expected exit code 1, got {result['exit_code']}"
    
    print("\n✅ Module validation passed")