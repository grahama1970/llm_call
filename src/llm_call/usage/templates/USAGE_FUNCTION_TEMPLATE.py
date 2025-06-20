#!/usr/bin/env python3
"""
Module: usage_[TEST_ID]_[SHORT_DESCRIPTION].py
Description: Usage function for Test Matrix [TEST_ID] - [FULL DESCRIPTION]

This usage function demonstrates:
1. Direct litellm call (baseline)
2. llm_call equivalent 
3. Actual output for human verification

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/[PROVIDER]
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: [TEST_ID]
- Priority: [PRIORITY]
- Category: [CATEGORY] > [SUBCATEGORY]
- Model: [MODEL]
- Prompt: "[PROMPT]"
- Expected: [EXPECTED_OUTPUT]
- Verification: [VERIFICATION_METHOD]

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # Run usage function:
>>> python usage_[TEST_ID]_[SHORT_DESCRIPTION].py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# Load environment variables from .env file
load_dotenv()

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    level="INFO"
)

# Suppress other loggers
import logging
logging.getLogger("LiteLLM").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

try:
    import litellm
    litellm.drop_params = True
except ImportError as e:
    logger.error(f"Cannot import litellm: {e}")
    logger.info("Install with: uv add litellm")
    exit(1)

try:
    from llm_call import ask
    from llm_call.core.caller import make_llm_request
    from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
except ImportError as e:
    logger.error(f"Cannot import llm_call: {e}")
    logger.info("Install with: uv sync")
    exit(1)


async def usage_function() -> Dict[str, Any]:
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md [TEST_ID]
    TEST_ID = "[TEST_ID]"
    PRIORITY = "[PRIORITY]"
    MODEL = "[MODEL]"
    PROMPT = "[PROMPT]"
    EXPECTED = ["[EXPECTED_1]", "[EXPECTED_2]"]  # List of acceptable responses
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix {TEST_ID} ({PRIORITY})")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: {EXPECTED[0]} or variations")
    logger.info("="*80)
    
    # Check required API keys based on model
    if "gpt" in MODEL.lower() and not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not set")
        logger.info("Set with: export OPENAI_API_KEY=your-key-here")
        return {}
    elif "vertex_ai" in MODEL.lower() and not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        logger.error("GOOGLE_APPLICATION_CREDENTIALS not set")
        logger.info("Set with: export GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json")
        return {}
    # Add more API key checks as needed
    
    # 1. DIRECT LITELLM
    logger.info("\n1. DIRECT LITELLM CALL:")
    logger.info("-" * 40)
    litellm_result = None
    try:
        response = litellm.completion(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            temperature=0.1,
            max_tokens=100
        )
        litellm_result = response.choices[0].message.content
        logger.success(f"Result: {litellm_result}")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # 2. LLM_CALL ASK()
    logger.info("\n2. LLM_CALL ASK() FUNCTION:")
    logger.info("-" * 40)
    llm_call_result = None
    try:
        llm_call_result = await ask(
            prompt=PROMPT,
            model=MODEL,
            temperature=0.1,
            max_tokens=100
        )
        logger.success(f"Result: {llm_call_result}")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # 3. LLM_CALL MAKE_LLM_REQUEST()
    logger.info("\n3. LLM_CALL MAKE_LLM_REQUEST():")
    logger.info("-" * 40)
    make_request_result = None
    try:
        config = {
            "model": MODEL,
            "messages": [{"role": "user", "content": PROMPT}],
            "temperature": 0.1,
            "max_tokens": 100
        }
        response = await make_llm_request(config)
        
        # Extract content
        if hasattr(response, 'choices'):
            make_request_result = response.choices[0].message.content
        elif isinstance(response, dict) and 'content' in response:
            make_request_result = response['content']
        else:
            make_request_result = str(response)
            
        logger.success(f"Result: {make_request_result}")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # HUMAN VERIFICATION WITH RICH TABLE
    console = Console()
    
    # Create results table
    table = Table(title=f"Test Matrix {TEST_ID} - Results Comparison", box=box.ROUNDED)
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Result", style="magenta")
    table.add_column("Matches Expected?", style="green")
    table.add_column("Status", justify="center")
    
    # Check results
    results_data = []
    
    def check_result(result: Optional[str]) -> bool:
        """Check if result matches expected output"""
        if not result:
            return False
        result_lower = result.lower().strip()
        # TODO: Customize this based on VERIFICATION_METHOD
        return any(expected.lower() in result_lower for expected in EXPECTED)
    
    # Process each result
    for method_name, result in [
        ("Direct litellm", litellm_result),
        ("llm_call ask()", llm_call_result),
        ("make_llm_request()", make_request_result)
    ]:
        if result:
            is_correct = check_result(result)
            status = "✅ PASS" if is_correct else "❌ FAIL"
            display_result = result[:100] + "..." if len(result) > 100 else result
            table.add_row(method_name, display_result, "Yes" if is_correct else "No", status)
            results_data.append((method_name, result, is_correct))
        else:
            table.add_row(method_name, "ERROR: No result", "N/A", "❌ FAIL")
            results_data.append((method_name, None, False))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Summary panel
    total_tests = len(results_data)
    passed_tests = sum(1 for _, result, is_correct in results_data if result and is_correct)
    
    summary = f"""
Test ID: {TEST_ID} ({PRIORITY})
Model: {MODEL}
Prompt: "{PROMPT}"
Expected: {', '.join(EXPECTED[:2])}...

Results: {passed_tests}/{total_tests} tests passed
Status: {"✅ ALL TESTS PASSED" if passed_tests == total_tests else "❌ SOME TESTS FAILED"}
"""
    
    console.print("\n")
    console.print(Panel(summary, title="Test Summary", border_style="blue"))
    
    # Save results
    results = {
        "test_id": TEST_ID,
        "priority": PRIORITY,
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "prompt": PROMPT,
        "expected": EXPECTED,
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests
        },
        "results": {
            "litellm": litellm_result,
            "llm_call_ask": llm_call_result,
            "llm_call_make_request": make_request_result
        },
        "verification": {
            method: {"result": result, "passed": is_correct} 
            for method, result, is_correct in results_data
        }
    }
    
    # Save to results directory
    os.makedirs("results", exist_ok=True)
    filename = f"results/{TEST_ID}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n💾 Results saved to: {filename}\n", style="bold yellow")
    
    return results


if __name__ == "__main__":
    logger.info(f"Starting usage function for Test Matrix [TEST_ID]")
    results = asyncio.run(usage_function())