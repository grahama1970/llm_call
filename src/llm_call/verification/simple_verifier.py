"""
Module: simple_verifier.py
Description: Simple, reliable test verification for Claude Code outputs

External Dependencies:
- google-generativeai: https://ai.google.dev/api/python/google/generativeai

Sample Input:
>>> test_output = '''
... test_math.py::test_addition PASSED
... test_math.py::test_subtraction FAILED
... '''

Expected Output:
>>> result = verify_test_output(test_output)
>>> print(result)
{'total': 2, 'passed': 1, 'failed': 1, 'accuracy': 50.0}

Example Usage:
>>> from simple_verifier import verify_test_output
>>> result = verify_test_output("test output here")
"""

import re
import json
from typing import Dict, Optional
import google.generativeai as genai
from loguru import logger


def extract_raw_results(output: str) -> Dict[str, int]:
    """Extract test results using simple pattern matching"""
    passed = len(re.findall(r'PASSED|passed|✓|✅', output))
    failed = len(re.findall(r'FAILED|failed|FAIL|✗|❌', output))
    errors = len(re.findall(r'ERROR|error', output))
    
    # Also check for pytest summary line
    summary_match = re.search(r'(\d+) passed.*?(\d+) failed', output)
    if summary_match:
        passed = int(summary_match.group(1))
        failed = int(summary_match.group(2))
    
    return {
        'passed': passed,
        'failed': failed + errors,
        'total': passed + failed + errors
    }


def verify_with_gemini(output: str, expected_results: Optional[Dict] = None) -> Dict:
    """Verify test output using Gemini (most reliable)"""
    try:
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""Analyze this test output and return ONLY a JSON object with these fields:
- total: total number of tests
- passed: number of passed tests  
- failed: number of failed tests
- contains_errors: boolean if any errors present

Test output:
{output}

Return ONLY valid JSON, no other text."""
        
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        
        if expected_results:
            result['matches_expected'] = (
                result['passed'] == expected_results.get('passed', 0) and
                result['failed'] == expected_results.get('failed', 0)
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Gemini verification failed: {e}")
        # Fall back to pattern matching
        return extract_raw_results(output)


def verify_simple(output: str) -> Dict:
    """Simplest possible verification - just pattern matching"""
    results = extract_raw_results(output)
    
    # Calculate accuracy
    if results['total'] > 0:
        results['accuracy'] = (results['passed'] / results['total']) * 100
    else:
        results['accuracy'] = 0.0
        
    # Flag suspicious results
    if "All tests passed" in output and results['failed'] > 0:
        results['suspicious'] = True
        results['warning'] = "Output claims success but failures detected"
    
    return results


def save_verification_report(output: str, results: Dict, filepath: str = "verification_report.json"):
    """Save both raw output and verification results"""
    report = {
        'raw_output': output,
        'verification': results,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(filepath, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Also save raw output separately
    with open(filepath.replace('.json', '_raw.txt'), 'w') as f:
        f.write(output)
    
    return filepath


# Validation function
if __name__ == "__main__":
    import os
    from datetime import datetime
    
    # Test with real-like output
    test_output = """
    ============================= test session starts ==============================
    test_math.py::test_addition PASSED                                      [ 50%]
    test_math.py::test_subtraction FAILED                                   [100%]
    
    =================================== FAILURES ===================================
    ________________________________ test_subtraction ______________________________
    
        def test_subtraction():
    >       assert 5 - 3 == 3
    E       assert 2 == 3
    
    ========================= 1 failed, 1 passed in 0.12s ==========================
    """
    
    # Test simple verification
    simple_results = verify_simple(test_output)
    print("Simple verification results:")
    print(json.dumps(simple_results, indent=2))
    
    assert simple_results['passed'] == 1, f"Expected 1 passed, got {simple_results['passed']}"
    assert simple_results['failed'] == 1, f"Expected 1 failed, got {simple_results['failed']}"
    assert simple_results['accuracy'] == 50.0, f"Expected 50% accuracy, got {simple_results['accuracy']}"
    
    print("\n✅ Module validation passed")