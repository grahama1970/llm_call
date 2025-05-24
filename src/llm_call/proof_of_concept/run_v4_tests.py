#!/usr/bin/env python3
"""
Run V4 test cases from test_prompts.json.

This script:
1. Loads test cases from the JSON file
2. Runs each test through the actual implementation
3. Reports results

Usage:
    1. Start the proxy server: python poc_claude_proxy_server.py
    2. Run this script: python run_v4_tests.py [--test-id TEST_ID]
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse

from loguru import logger
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Now import from the correct location
from src.llm_call.proof_of_concept.litellm_client_poc import llm_call

# Configure logger
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)

def load_test_cases(json_file: Path) -> List[Dict[str, Any]]:
    """Load test cases from JSON file."""
    with open(json_file, 'r') as f:
        content = f.read()
    
    # The file starts with explanatory text, find the JSON array
    json_start = content.find('[')
    if json_start == -1:
        raise ValueError("Could not find JSON array in test file")
    
    json_content = content[json_start:]
    
    # Fix the JSON - remove comments and Python-specific syntax
    lines = json_content.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove // comments
        if '//' in line:
            line = line[:line.index('//')]
        # Fix Python False to JSON false
        line = line.replace('False', 'false')
        line = line.replace('True', 'true')
        cleaned_lines.append(line)
    
    cleaned_json = '\n'.join(cleaned_lines)
    
    try:
        test_cases = json.loads(cleaned_json)
        return test_cases
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.error(f"Error at position {e.pos}")
        # Show context around error
        start = max(0, e.pos - 100)
        end = min(len(cleaned_json), e.pos + 100)
        logger.error(f"Context: ...{cleaned_json[start:end]}...")
        raise

def extract_response_content(response: Any) -> str:
    """Extract content from various response formats."""
    if response is None:
        return "None"
    
    if isinstance(response, dict):
        if "error" in response:
            return f"Error: {response.get('error', 'Unknown error')}"
        elif response.get("choices"):
            return response["choices"][0].get("message", {}).get("content", "")
    elif hasattr(response, "choices") and response.choices:
        return response.choices[0].message.content or ""
    
    return str(response)

async def run_single_test(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test case."""
    test_id = test_case.get("test_case_id", "unknown")
    description = test_case.get("description", "No description")
    llm_config = test_case.get("llm_config", {})
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Running test: {test_id}")
    logger.info(f"Description: {description}")
    
    # Handle environment variable substitution in the config
    config_str = json.dumps(llm_config)
    config_str = config_str.replace("${PERPLEXITY_API_KEY_FOR_MCP}", 
                                    os.environ.get("PERPLEXITY_API_KEY", ""))
    llm_config = json.loads(config_str)
    
    try:
        # Make the LLM call
        start_time = asyncio.get_event_loop().time()
        response = await llm_call(llm_config)
        end_time = asyncio.get_event_loop().time()
        
        duration = end_time - start_time
        content = extract_response_content(response)
        
        # Determine if test passed
        if response is None:
            status = "FAILED"
            reason = "No response received"
        elif isinstance(response, dict) and "error" in response:
            # For validation tests, error might be expected
            if "validation" in llm_config and llm_config.get("validation"):
                status = "PASSED"  # Validation correctly rejected
                reason = f"Validation failed as expected: {response.get('error', '')[:100]}"
            else:
                status = "FAILED"
                reason = response.get("error", "Unknown error")
        else:
            status = "PASSED"
            reason = "Got response"
        
        result = {
            "test_id": test_id,
            "status": status,
            "duration": duration,
            "reason": reason,
            "response_preview": content[:200] + "..." if len(content) > 200 else content
        }
        
        if status == "PASSED":
            logger.success(f"✅ Test {test_id} PASSED in {duration:.2f}s")
        else:
            logger.error(f"❌ Test {test_id} FAILED: {reason}")
        
        logger.debug(f"Response preview: {result['response_preview']}")
        
        return result
        
    except Exception as e:
        logger.exception(f"Test {test_id} crashed with exception")
        return {
            "test_id": test_id,
            "status": "ERROR",
            "duration": 0,
            "reason": f"Exception: {type(e).__name__}: {str(e)}",
            "response_preview": ""
        }

async def run_all_tests(test_cases: List[Dict[str, Any]], 
                       test_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Run all test cases or filtered subset."""
    results = []
    
    # Filter tests if requested
    if test_filter:
        test_cases = [t for t in test_cases if test_filter in t.get("test_case_id", "")]
        logger.info(f"Running {len(test_cases)} filtered tests")
    
    for i, test_case in enumerate(test_cases):
        logger.info(f"\n📋 Test {i+1}/{len(test_cases)}")
        result = await run_single_test(test_case)
        results.append(result)
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    return results

def print_summary(results: List[Dict[str, Any]]):
    """Print test summary."""
    logger.info(f"\n{'='*60}")
    logger.info("📊 Test Summary")
    logger.info(f"{'='*60}")
    
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    
    logger.info(f"Total tests: {total}")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"💥 Errors: {errors}")
    
    if failed > 0 or errors > 0:
        logger.info(f"\n❌ Failed/Error Tests:")
        for result in results:
            if result["status"] in ["FAILED", "ERROR"]:
                logger.error(f"  - {result['test_id']}: {result['reason']}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    logger.info(f"\n🎯 Success rate: {success_rate:.1f}%")

async def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run V4 test cases")
    parser.add_argument("--test-id", help="Run only tests containing this ID")
    parser.add_argument("--json-file", 
                       default="v4_claude_validator/test_prompts.json",
                       help="Path to test JSON file")
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Check proxy server is running
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get("http://127.0.0.1:3010/health", timeout=2.0)
            health.raise_for_status()
            logger.success("✅ Proxy server is running")
    except:
        logger.error("❌ Proxy server not running! Start it with:")
        logger.error("   python src/llm_call/proof_of_concept/poc_claude_proxy_server.py")
        return
    
    # Load test cases
    json_file = Path(__file__).parent / args.json_file
    if not json_file.exists():
        logger.error(f"Test file not found: {json_file}")
        return
    
    logger.info(f"Loading tests from: {json_file}")
    test_cases = load_test_cases(json_file)
    logger.info(f"Loaded {len(test_cases)} test cases")
    
    # Run tests
    results = await run_all_tests(test_cases, args.test_id)
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    import os
    asyncio.run(main())