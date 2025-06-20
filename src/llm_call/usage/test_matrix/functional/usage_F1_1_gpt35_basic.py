#!/usr/bin/env python3
"""
Module: usage_01_gpt35_basic.py
Description: Usage function for Test Matrix F1.1 - Basic GPT-3.5-turbo query

This usage function demonstrates:
1. Direct litellm call (baseline)
2. llm_call equivalent 
3. Actual output for human verification

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/openai
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: F1.1
- Priority: CRITICAL
- Category: Functional Tests > Basic Model Queries
- Model: gpt-3.5-turbo
- Prompt: "What is 2+2?"
- Expected: "4" or "2+2 equals 4"
- Verification: Exact match

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # Run usage function:
>>> python usage_01_gpt35_basic.py
"""

import asyncio
import json
import os
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
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


async def usage_function():
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md F1.1
    MODEL = "gpt-3.5-turbo"
    PROMPT = "What is 2+2?"
    EXPECTED = ["4", "2+2 equals 4", "2 + 2 = 4", "two plus two equals four"]
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix F1.1 (CRITICAL)")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: {EXPECTED[0]} or variations")
    logger.info("="*80)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY not set")
        logger.info("Set with: export OPENAI_API_KEY=your-key-here")
        return
    
    # 1. DIRECT LITELLM
    logger.info("\n1. DIRECT LITELLM CALL:")
    logger.info("-" * 40)
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
        litellm_result = None
    
    # 2. LLM_CALL ASK()
    logger.info("\n2. LLM_CALL ASK() FUNCTION:")
    logger.info("-" * 40)
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
        llm_call_result = None
    
    # 3. LLM_CALL MAKE_LLM_REQUEST()
    logger.info("\n3. LLM_CALL MAKE_LLM_REQUEST():")
    logger.info("-" * 40)
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
        make_request_result = None
    
    # HUMAN VERIFICATION WITH RICH TABLE
    console = Console()
    
    # Create results table
    table = Table(title="Test Matrix F1.1 - Results for Human Review", box=box.ROUNDED)
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("LLM Output", style="magenta")
    table.add_column("Auto-Check", justify="center")
    table.add_column("Reason", style="dim")
    
    # Check results
    results_data = []
    
    def perform_simple_check(result_text: str, expected_variations: list[str]) -> tuple[bool, str]:
        """
        A simple, deterministic check. Returns a (passed, reason) tuple.
        This is not a final verdict, but a helpful first pass for the human reviewer.
        """
        if not result_text:
            return (False, "Result was empty.")
        
        # Normalize text for a more reliable check
        normalized_result = result_text.lower().strip().strip('.').strip()
        
        for expected in expected_variations:
            if expected.lower() in normalized_result:
                return (True, f"Result contained expected substring '{expected}'.")
        
        # Check for exact "4" match
        if normalized_result == "4":
            return (True, "Result was exactly '4'.")
        
        return (False, "Result did not contain any expected substrings.")
    
    # Collect all results for processing
    all_results = [
        ("Direct litellm", litellm_result, "litellm"),
        ("llm_call ask()", llm_call_result, "llm_call_ask"),
        ("make_llm_request()", make_request_result, "make_llm_request")
    ]
    
    # Process each result with the improved check
    for method_name, result, json_key in all_results:
        if result:
            is_correct, reason = perform_simple_check(result, EXPECTED)
            auto_check_status = "✅ OK" if is_correct else "⚠️ REVIEW"
            display_result = result[:80] + "..." if len(result) > 80 else result
            table.add_row(method_name, display_result, auto_check_status, reason)
            results_data.append((json_key, result, is_correct, reason))
        else:
            table.add_row(method_name, "ERROR: No result", "❌ FAIL", "No result returned")
            results_data.append((json_key, None, False, "No result returned"))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Summary panel
    total_tests = len(results_data)
    passed_auto_checks = sum(1 for _, result, is_correct, _ in results_data if result and is_correct)
    
    summary = f"""
Test ID: F1.1 (CRITICAL)
Model: {MODEL}
Prompt: "{PROMPT}"
Expected: {', '.join(EXPECTED[:2])}...

Results: {passed_auto_checks}/{total_tests} calls passed the simple automated check.
Status: Human verification required for final determination.
"""
    
    console.print("\n")
    console.print(Panel(summary, title="Test Summary", border_style="blue"))
    
    # Save results
    results = {
        "test_id": "F1.1",
        "priority": "CRITICAL",
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "prompt": PROMPT,
        "expected": EXPECTED,
        "summary": {
            "total_tests": total_tests,
            "passed_auto_check": passed_auto_checks,
            "failed_auto_check": total_tests - passed_auto_checks,
            "note": "Auto-check results are for human review, not final determination"
        },
        "results": {
            "litellm": litellm_result,
            "llm_call_ask": llm_call_result,
            "llm_call_make_request": make_request_result
        },
        "verification": {
            json_key: {
                "result": result, 
                "auto_check_passed": is_correct,
                "reason_for_check": reason
            } 
            for json_key, result, is_correct, reason in results_data
        }
    }
    
    # Save to results directory
    os.makedirs("../../results", exist_ok=True)
    filename = f"../../results/F1_1_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n💾 Results saved to: {filename}\n", style="bold yellow")


if __name__ == "__main__":
    logger.info("Starting usage function for Test Matrix F1.1")
    asyncio.run(usage_function())