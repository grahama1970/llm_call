#!/usr/bin/env python3
"""Run essential v4 validation tests one by one."""

import json
import sys
import subprocess
import time
from pathlib import Path
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

def run_single_test(test_case):
    """Run a single test case."""
    test_id = test_case['test_case_id']
    logger.info(f"Running test: {test_id}")
    logger.info(f"Description: {test_case['description']}")
    
    # Save test case to temp file
    temp_file = f"temp_test_{test_id}.json"
    with open(temp_file, 'w') as f:
        json.dump([test_case], f, indent=2)
    
    # Run the test
    cmd = [
        "python", 
        "src/llm_call/proof_of_concept/litellm_client_poc.py",
        "--config", temp_file,
        "--test-id", test_id
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.success(f"✅ Test {test_id} PASSED")
            # Show key output
            if "Response:" in result.stdout:
                response_start = result.stdout.find("Response:")
                response_preview = result.stdout[response_start:response_start+200]
                logger.info(f"Response preview: {response_preview}...")
        else:
            logger.error(f"❌ Test {test_id} FAILED")
            logger.error(f"Error: {result.stderr}")
            
        # Clean up temp file
        Path(temp_file).unlink(missing_ok=True)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Test {test_id} TIMED OUT")
        Path(temp_file).unlink(missing_ok=True)
        return False
    except Exception as e:
        logger.error(f"❌ Test {test_id} ERROR: {e}")
        Path(temp_file).unlink(missing_ok=True)
        return False

def main():
    """Run all essential tests."""
    # Load test cases
    test_file = "src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_essential.json"
    logger.info(f"Loading tests from: {test_file}")
    
    with open(test_file, 'r') as f:
        test_cases = json.load(f)
    
    logger.info(f"Found {len(test_cases)} test cases")
    
    # Check if proxy is running
    logger.info("Checking if proxy server is running...")
    try:
        import requests
        response = requests.get("http://localhost:3010/health", timeout=2)
        if response.status_code == 200:
            logger.success("✅ Proxy server is running")
        else:
            logger.warning("⚠️  Proxy server returned non-200 status")
    except:
        logger.error("❌ Proxy server is not running! Start it with:")
        logger.error("   python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return
    
    # Run tests one by one
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases):
        logger.info(f"\n{'='*60}")
        logger.info(f"Test {i+1}/{len(test_cases)}")
        
        if run_single_test(test_case):
            passed += 1
        else:
            failed += 1
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*60}")
    logger.success(f"Passed: {passed}")
    logger.error(f"Failed: {failed}")
    logger.info(f"Total:  {len(test_cases)}")
    
    if failed == 0:
        logger.success("✅ ALL TESTS PASSED!")
    else:
        logger.error(f"❌ {failed} tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()