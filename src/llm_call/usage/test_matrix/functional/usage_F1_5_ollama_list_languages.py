#!/usr/bin/env python3
"""
Module: usage_F1_5_ollama_list_languages.py
Description: Usage function for Test Matrix F1.5 - Ollama qwen2.5:32b list programming languages

This usage function demonstrates:
1. Direct litellm call (baseline)
2. llm_call equivalent 
3. Side-by-side comparison for human verification

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/ollama
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: F1.5
- Priority: CRITICAL
- Category: Functional Tests > Basic Model Queries
- Model: ollama/qwen2.5:32b
- Prompt: "List 5 programming languages"
- Expected: Exactly 5 languages with descriptions
- Verification: Count validation

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # Ensure Ollama is running and model is available:
>>> ollama serve
>>> ollama pull qwen2.5:32b
>>> # Run usage function:
>>> python usage_F1_5_ollama_list_languages.py
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


def count_languages(text: str) -> Tuple[int, List[str]]:
    """
    Count programming languages in the response.
    Returns (count, list_of_languages)
    """
    if not text:
        return (0, [])
    
    # Common patterns for numbered lists
    patterns = [
        r'^\d+\.\s*([A-Za-z+#\-\.]+)',  # 1. Python
        r'^\*\s*([A-Za-z+#\-\.]+)',      # * Python
        r'^\-\s*([A-Za-z+#\-\.]+)',      # - Python
        r'^([A-Za-z+#\-\.]+):',          # Python:
    ]
    
    languages = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                lang = match.group(1)
                # Filter out common non-language words
                if lang.lower() not in ['the', 'a', 'an', 'and', 'or', 'but', 'for', 'with']:
                    languages.append(lang)
                break
    
    return (len(languages), languages)


async def usage_function() -> Dict[str, Any]:
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md F1.5
    # Using codellama:latest instead of qwen2.5:32b which isn't available here
    TEST_ID = "F1.5"
    PRIORITY = "CRITICAL"
    MODEL = "ollama/codellama:latest"
    PROMPT = "List 5 programming languages"
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix {TEST_ID} ({PRIORITY})")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: Exactly 5 languages with descriptions")
    logger.info("="*80)
    
    # Check if Ollama is running and model is available
    logger.info("\nChecking Ollama availability...")
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Ollama is not running. Start with: ollama serve")
            return {}
        logger.success("Ollama is available")
        
        # Check available models
        logger.info("Available models:")
        for line in result.stdout.split('\n'):
            if line.strip():
                logger.info(f"  {line}")
        
        # Check if our model exists
        if 'qwen2.5:32b' not in result.stdout:
            logger.warning(f"Model {MODEL} not found in Ollama")
            # Don't override MODEL, keep trying with the original
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
            max_tokens=200,
            api_base="http://localhost:11434"
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
        ask_prompt = f"{PROMPT} [ask-{timestamp}]"
        llm_call_result = await ask(
            prompt=ask_prompt,
            model=MODEL,
            temperature=0.7,
            max_tokens=200
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
            "max_tokens": 200
        }
        response = await make_llm_request(config)
        
        # Extract content
        if hasattr(response, 'choices'):
            make_request_result = response.choices[0].message.content
        elif isinstance(response, dict):
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
    
    # HUMAN VERIFICATION WITH COMPARISON
    console = Console()
    
    # Create results table
    table = Table(title=f"Test Matrix {TEST_ID} - Results Comparison", box=box.ROUNDED)
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Languages Found", justify="center")
    table.add_column("Language List", style="dim")
    
    # Collect all results
    all_results = [
        ("Direct litellm", litellm_result, "litellm"),
        ("llm_call ask()", llm_call_result, "llm_call_ask"),
        ("make_llm_request()", make_request_result, "make_llm_request")
    ]
    
    results_data = []
    
    # Process each result
    for method_name, result, json_key in all_results:
        if result:
            count, langs = count_languages(result)
            status = "✅ Response" if result else "❌ No Response"
            lang_list = ", ".join(langs[:3]) + "..." if len(langs) > 3 else ", ".join(langs)
            table.add_row(method_name, status, str(count), lang_list)
            results_data.append((json_key, result, count, langs))
        else:
            table.add_row(method_name, "❌ Failed", "0", "—")
            results_data.append((json_key, None, 0, []))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Show full responses
    console.print("\n[bold]Full Responses:[/bold]\n")
    for method_name, result, json_key in all_results:
        if result:
            console.print(f"[cyan]{method_name}:[/cyan]")
            console.print(Panel(result, border_style="blue"))
    
    # Summary
    successful_calls = sum(1 for _, result, _, _ in results_data if result)
    
    summary = f"""
Test ID: {TEST_ID} ({PRIORITY})
Model: {MODEL}
Prompt: "{PROMPT}"
Expected: Exactly 5 languages with descriptions

Results: {successful_calls}/{len(results_data)} methods returned responses

Key Questions for Human Review:
1. Do all methods return similar lists of programming languages?
2. Are the responses formatted consistently?
3. Does llm_call properly pass through the model responses?
"""
    
    console.print("\n")
    console.print(Panel(summary, title="Summary for Human Review", border_style="green"))
    
    # Save results
    results = {
        "test_id": TEST_ID,
        "priority": PRIORITY,
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "prompt": PROMPT,
        "expected": "Exactly 5 languages with descriptions",
        "summary": {
            "total_methods": len(results_data),
            "successful_calls": successful_calls,
            "key_question": "Do all methods return similar programming language lists?"
        },
        "results": {
            "litellm": litellm_result,
            "llm_call_ask": llm_call_result,
            "llm_call_make_request": make_request_result
        },
        "language_counts": {
            json_key: {
                "result": result,
                "count": count,
                "languages": langs
            }
            for json_key, result, count, langs in results_data
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
    logger.info(f"Starting usage function for Test Matrix F1.5")
    results = asyncio.run(usage_function())