#!/usr/bin/env python3
"""
Module: usage_F1_2_vertex_python.py
Description: Usage function for Test Matrix F1.2 - Vertex AI Gemini Flash Python code generation

This usage function demonstrates:
1. Direct litellm call (baseline)
2. llm_call equivalent 
3. Actual output for human verification

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/vertex
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: F1.2
- Priority: CRITICAL
- Category: Functional Tests > Basic Model Queries
- Model: vertex_ai/gemini-1.5-flash
- Prompt: "Write a Python function to reverse a string"
- Expected: Valid Python function with proper syntax
- Verification: Python syntax check

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # Run usage function:
>>> python usage_F1_2_vertex_python.py
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import ast

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.syntax import Syntax

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


def perform_python_syntax_check(code_text: str) -> Tuple[bool, str]:
    """
    Check if the response contains valid Python syntax.
    Returns a (passed, reason) tuple.
    """
    if not code_text:
        return (False, "Result was empty.")
    
    # Try to extract Python code from the response
    # Look for code blocks first
    code_to_check = code_text
    if "```python" in code_text:
        # Extract code between ```python and ```
        start = code_text.find("```python") + 9
        end = code_text.find("```", start)
        if end > start:
            code_to_check = code_text[start:end].strip()
    elif "```" in code_text:
        # Extract code between ``` and ```
        start = code_text.find("```") + 3
        end = code_text.find("```", start)
        if end > start:
            code_to_check = code_text[start:end].strip()
    elif "def " in code_text:
        # Try to extract just the function definition
        lines = code_text.split('\n')
        func_lines = []
        in_func = False
        for line in lines:
            if line.strip().startswith("def "):
                in_func = True
            if in_func:
                func_lines.append(line)
        if func_lines:
            code_to_check = '\n'.join(func_lines)
    
    # Check if it contains a function to reverse a string
    if "reverse" not in code_to_check.lower() and "[::-1]" not in code_to_check:
        return (False, "Code does not appear to reverse a string.")
    
    # Try to parse the Python code
    try:
        ast.parse(code_to_check)
        return (True, "Valid Python syntax for string reversal function.")
    except SyntaxError as e:
        return (False, f"Python syntax error: {str(e)}")
    except Exception as e:
        return (False, f"Failed to parse Python code: {str(e)}")


async def usage_function() -> Dict[str, Any]:
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md F1.2
    TEST_ID = "F1.2"
    PRIORITY = "CRITICAL"
    MODEL = "vertex_ai/gemini-1.5-flash"
    PROMPT = "Write a Python function to reverse a string"
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix {TEST_ID} ({PRIORITY})")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: Valid Python function with proper syntax")
    logger.info("="*80)
    
    # Check required environment for Vertex AI
    if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        logger.error("GOOGLE_APPLICATION_CREDENTIALS not set")
        logger.info("Set with: export GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json")
        return {}
    
    # Clear any existing cache for this test
    import hashlib
    cache_key = hashlib.md5(f"{MODEL}:{PROMPT}".encode()).hexdigest()
    logger.info(f"Test cache key: {cache_key}")
    
    # 1. DIRECT LITELLM
    logger.info("\n1. DIRECT LITELLM CALL:")
    logger.info("-" * 40)
    litellm_result = None
    try:
        response = litellm.completion(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            temperature=0.7,  # Higher temp for variation
            max_tokens=300,
            caching=False  # Disable caching for this test
        )
        litellm_result = response.choices[0].message.content
        logger.success(f"Result received ({len(litellm_result)} chars)")
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
            temperature=0.7,
            max_tokens=300
        )
        logger.success(f"Result received ({len(llm_call_result)} chars)")
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
            "temperature": 0.7,
            "max_tokens": 300
        }
        response = await make_llm_request(config)
        
        # Extract content
        if hasattr(response, 'choices'):
            make_request_result = response.choices[0].message.content
        elif isinstance(response, dict) and 'content' in response:
            make_request_result = response['content']
        else:
            make_request_result = str(response)
            
        logger.success(f"Result received ({len(make_request_result)} chars)")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # HUMAN VERIFICATION WITH RICH TABLE
    console = Console()
    
    # Create results table
    table = Table(title=f"Test Matrix {TEST_ID} - Results for Human Review", box=box.ROUNDED)
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Auto-Check", justify="center")
    table.add_column("Reason", style="dim")
    
    # Collect all results for processing
    all_results = [
        ("Direct litellm", litellm_result, "litellm"),
        ("llm_call ask()", llm_call_result, "llm_call_ask"),
        ("make_llm_request()", make_request_result, "make_llm_request")
    ]
    
    results_data = []
    
    # Process each result with the syntax check
    for method_name, result, json_key in all_results:
        if result:
            is_valid, reason = perform_python_syntax_check(result)
            auto_check_status = "✅ OK" if is_valid else "⚠️ REVIEW"
            table.add_row(method_name, auto_check_status, reason)
            results_data.append((json_key, result, is_valid, reason))
        else:
            table.add_row(method_name, "❌ FAIL", "No result returned")
            results_data.append((json_key, None, False, "No result returned"))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Show code samples
    console.print("\n[bold]Generated Code Samples:[/bold]\n")
    for method_name, result, json_key in all_results:
        if result:
            console.print(f"[cyan]{method_name}:[/cyan]")
            # Extract and display Python code with syntax highlighting
            code = result
            if "```python" in result:
                start = result.find("```python") + 9
                end = result.find("```", start)
                if end > start:
                    code = result[start:end].strip()
            elif "```" in result:
                start = result.find("```") + 3
                end = result.find("```", start)
                if end > start:
                    code = result[start:end].strip()
            
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            console.print(syntax)
            console.print()
    
    # Summary panel
    total_tests = len(results_data)
    passed_auto_checks = sum(1 for _, result, is_valid, _ in results_data if result and is_valid)
    
    summary = f"""
Test ID: {TEST_ID} ({PRIORITY})
Model: {MODEL}
Prompt: "{PROMPT}"
Expected: Valid Python function with proper syntax

Results: {passed_auto_checks}/{total_tests} calls passed the syntax check.
Status: Human verification required for code quality assessment.
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
        "expected": "Valid Python function with proper syntax",
        "summary": {
            "total_tests": total_tests,
            "passed_auto_check": passed_auto_checks,
            "failed_auto_check": total_tests - passed_auto_checks,
            "note": "Auto-check verifies syntax only, not code quality"
        },
        "results": {
            "litellm": litellm_result,
            "llm_call_ask": llm_call_result,
            "llm_call_make_request": make_request_result
        },
        "verification": {
            json_key: {
                "result": result, 
                "auto_check_passed": is_valid,
                "reason_for_check": reason
            } 
            for json_key, result, is_valid, reason in results_data
        }
    }
    
    # Save to results directory
    os.makedirs("../../results", exist_ok=True)
    filename = f"../../results/{TEST_ID}_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n💾 Results saved to: {filename}\n", style="bold yellow")
    
    return results


if __name__ == "__main__":
    logger.info(f"Starting usage function for Test Matrix F1.2")
    results = asyncio.run(usage_function())