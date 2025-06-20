#!/usr/bin/env python3
"""
Module: usage_F1_3_ollama_ml_definition.py
Description: Usage function for Test Matrix F1.3 - Ollama phi3:mini ML definition in one sentence

This usage function demonstrates:
1. Direct litellm call (baseline)
2. llm_call equivalent 
3. Actual output for human verification

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/ollama
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: F1.3
- Priority: MODERATE
- Category: Functional Tests > Basic Model Queries
- Model: ollama/phi3:mini
- Prompt: "Define ML in one sentence"
- Expected: Single sentence, 10-30 words
- Verification: Length validation

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # Ensure Ollama is running:
>>> ollama serve
>>> # Run usage function:
>>> python usage_F1_3_ollama_ml_definition.py
"""

import asyncio
import json
import os
import re
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


def perform_sentence_validation(text: str) -> Tuple[bool, str]:
    """
    Validate that the response is a single sentence of 10-30 words.
    Returns a (passed, reason) tuple.
    """
    if not text:
        return (False, "Result was empty.")
    
    # Clean up the text
    cleaned_text = text.strip()
    
    # Check for multiple sentences (crude but effective)
    # Count periods that are followed by space and uppercase or at end
    sentence_pattern = r'[.!?]+(?:\s+[A-Z]|$)'
    sentence_ends = re.findall(sentence_pattern, cleaned_text)
    
    # Also check for newlines which might indicate multiple sentences
    if '\n' in cleaned_text:
        return (False, f"Contains multiple lines (found newline characters).")
    
    if len(sentence_ends) > 1:
        return (False, f"Contains multiple sentences (found {len(sentence_ends)} sentence endings).")
    
    # Count words
    words = cleaned_text.split()
    word_count = len(words)
    
    if word_count < 10:
        return (False, f"Too short: {word_count} words (expected 10-30).")
    elif word_count > 30:
        return (False, f"Too long: {word_count} words (expected 10-30).")
    
    # Check it actually defines ML (look for key terms)
    ml_keywords = ['machine learning', 'ml', 'learn', 'data', 'algorithm', 'model', 'pattern', 'prediction']
    has_ml_content = any(keyword in cleaned_text.lower() for keyword in ml_keywords)
    
    if not has_ml_content:
        return (False, "Response doesn't appear to define machine learning.")
    
    return (True, f"Valid single sentence with {word_count} words about ML.")


async def usage_function() -> Dict[str, Any]:
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md F1.3
    TEST_ID = "F1.3"
    PRIORITY = "MODERATE"
    MODEL = "ollama/phi3:mini"
    PROMPT = "Define ML in one sentence"
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix {TEST_ID} ({PRIORITY})")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: Single sentence, 10-30 words")
    logger.info("="*80)
    
    # Check if Ollama is running
    logger.info("\nChecking Ollama availability...")
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Ollama is not running. Start with: ollama serve")
            return {}
        logger.success("Ollama is available")
        
        # Check if phi3:mini model is available
        if 'phi3:mini' not in result.stdout:
            logger.warning("phi3:mini model not found. Pulling model...")
            subprocess.run(['ollama', 'pull', 'phi3:mini'])
    except Exception as e:
        logger.error(f"Could not check Ollama status: {e}")
        return {}
    
    # Add timestamp to make each prompt unique and avoid caching
    import time
    timestamp = int(time.time() * 1000)
    
    # 1. DIRECT LITELLM
    logger.info("\n1. DIRECT LITELLM CALL:")
    logger.info("-" * 40)
    litellm_result = None
    try:
        litellm_prompt = f"{PROMPT} [litellm-{timestamp}]"
        response = litellm.completion(
            model=MODEL,
            messages=[{"role": "user", "content": litellm_prompt}],
            temperature=0.7,
            max_tokens=50,  # Limit to encourage single sentence
            api_base="http://localhost:11434"  # Ollama default
        )
        litellm_result = response.choices[0].message.content
        logger.success(f"Result received ({len(litellm_result)} chars)")
    except Exception as e:
        logger.error(f"Error: {e}")
        logger.info("Make sure Ollama is running and phi3:mini is pulled")
    
    # 2. LLM_CALL ASK()
    logger.info("\n2. LLM_CALL ASK() FUNCTION:")
    logger.info("-" * 40)
    llm_call_result = None
    try:
        ask_prompt = f"{PROMPT} [ask-{timestamp}]"
        llm_call_result = await ask(
            prompt=ask_prompt,
            model=MODEL,
            temperature=0.7,
            max_tokens=50
        )
        logger.success(f"Result received ({len(llm_call_result)} chars)")
    except Exception as e:
        logger.error(f"Error: {e}")
    
    # 3. LLM_CALL MAKE_LLM_REQUEST()
    logger.info("\n3. LLM_CALL MAKE_LLM_REQUEST():")
    logger.info("-" * 40)
    make_request_result = None
    try:
        request_prompt = f"{PROMPT} [request-{timestamp}]"
        config = {
            "model": MODEL,
            "messages": [{"role": "user", "content": request_prompt}],
            "temperature": 0.7,
            "max_tokens": 50
        }
        response = await make_llm_request(config)
        
        # Extract content
        if hasattr(response, 'choices'):
            make_request_result = response.choices[0].message.content
        elif isinstance(response, dict):
            # Handle dict response from Ollama
            if 'choices' in response and len(response['choices']) > 0:
                make_request_result = response['choices'][0]['message']['content']
            elif 'content' in response:
                make_request_result = response['content']
            else:
                make_request_result = str(response)
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
    table.add_column("Response", style="white", max_width=40)
    
    # Collect all results for processing
    all_results = [
        ("Direct litellm", litellm_result, "litellm"),
        ("llm_call ask()", llm_call_result, "llm_call_ask"),
        ("make_llm_request()", make_request_result, "make_llm_request")
    ]
    
    results_data = []
    
    # Process each result with validation
    for method_name, result, json_key in all_results:
        if result:
            is_valid, reason = perform_sentence_validation(result)
            auto_check_status = "✅ OK" if is_valid else "⚠️ REVIEW"
            # Truncate response for display
            display_result = result[:40] + "..." if len(result) > 40 else result
            table.add_row(method_name, auto_check_status, reason, display_result)
            results_data.append((json_key, result, is_valid, reason))
        else:
            table.add_row(method_name, "❌ FAIL", "No result returned", "—")
            results_data.append((json_key, None, False, "No result returned"))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Show full responses
    console.print("\n[bold]Full Responses:[/bold]\n")
    for method_name, result, json_key in all_results:
        if result:
            console.print(f"[cyan]{method_name}:[/cyan]")
            console.print(Panel(result, border_style="blue"))
    
    # Summary panel
    total_tests = len(results_data)
    passed_checks = sum(1 for _, result, is_valid, _ in results_data if result and is_valid)
    
    summary = f"""
Test ID: {TEST_ID} ({PRIORITY})
Model: {MODEL}
Prompt: "{PROMPT}"
Expected: Single sentence, 10-30 words

Results: {passed_checks}/{total_tests} calls passed the validation check.
Status: Human verification required for content quality assessment.
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
        "expected": "Single sentence, 10-30 words",
        "summary": {
            "total_tests": total_tests,
            "passed_auto_check": passed_checks,
            "failed_auto_check": total_tests - passed_checks,
            "note": "Auto-check validates sentence structure and word count only"
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
    logger.info(f"Starting usage function for Test Matrix F1.3")
    results = asyncio.run(usage_function())