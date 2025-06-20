#!/usr/bin/env python3
"""
Module: usage_F1_6_perplexity_weather.py
Description: Usage function for Test Matrix F1.6 - Perplexity online weather query

This usage function demonstrates:
1. Direct litellm call (baseline)
2. llm_call equivalent 
3. Side-by-side comparison for human verification

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/perplexity
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: F1.6
- Priority: MODERATE
- Category: Functional Tests > Basic Model Queries
- Model: perplexity/llama-3.1-sonar-small-128k-online
- Prompt: "What is the weather today?"
- Expected: Current weather information with sources
- Verification: Online data check

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # Run usage function:
>>> python usage_F1_6_perplexity_weather.py
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


def check_weather_response(text: str) -> Tuple[bool, str]:
    """
    Basic check if response contains weather-related information.
    Returns (has_weather_info, description)
    """
    if not text:
        return (False, "No response")
    
    # Look for weather-related keywords
    weather_keywords = ['weather', 'temperature', 'degrees', 'celsius', 'fahrenheit', 
                       'sunny', 'cloudy', 'rain', 'snow', 'forecast', 'humidity',
                       'wind', 'conditions']
    
    text_lower = text.lower()
    found_keywords = [kw for kw in weather_keywords if kw in text_lower]
    
    # Check for sources/citations (Perplexity typically includes these)
    has_sources = any(marker in text for marker in ['[1]', '[2]', 'Source:', 'http'])
    
    if found_keywords:
        source_note = " with sources" if has_sources else ""
        return (True, f"Contains weather info ({', '.join(found_keywords[:3])}...){source_note}")
    else:
        return (False, "No weather-related content found")


async def usage_function() -> Dict[str, Any]:
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md F1.6
    TEST_ID = "F1.6"
    PRIORITY = "MODERATE"
    MODEL = "perplexity/llama-3.1-sonar-small-128k-online"
    PROMPT = "What is the weather today?"
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix {TEST_ID} ({PRIORITY})")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: Current weather information with sources")
    logger.info("="*80)
    
    # Check PERPLEXITY_API_KEY
    if not os.getenv('PERPLEXITY_API_KEY'):
        logger.error("PERPLEXITY_API_KEY is not set!")
        logger.info("Set with: export PERPLEXITY_API_KEY=your_key")
        return {}
    else:
        logger.success("PERPLEXITY_API_KEY is set")
    
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
            temperature=0.1,  # Low temp for factual info
            max_tokens=300
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
            temperature=0.1,
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
        request_prompt = f"{PROMPT} [request-{timestamp}]"
        config = {
            "model": MODEL,
            "messages": [{"role": "user", "content": request_prompt}],
            "temperature": 0.1,
            "max_tokens": 300
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
    table.add_column("Weather Info Check", style="dim", width=50)
    
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
            has_weather, check_desc = check_weather_response(result)
            status = "✅ Response" if result else "❌ No Response"
            table.add_row(method_name, status, check_desc)
            results_data.append((json_key, result, has_weather, check_desc))
        else:
            table.add_row(method_name, "❌ Failed", "No response received")
            results_data.append((json_key, None, False, "No response"))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Show responses
    console.print("\n[bold]Weather Responses:[/bold]\n")
    for method_name, result, json_key in all_results:
        if result:
            console.print(f"[cyan]{method_name}:[/cyan]")
            # Truncate very long responses for display
            display_result = result[:500] + "..." if len(result) > 500 else result
            console.print(Panel(display_result, border_style="blue"))
    
    # Summary
    successful_calls = sum(1 for _, result, _, _ in results_data if result)
    
    summary = f"""
Test ID: {TEST_ID} ({PRIORITY})
Model: {MODEL}
Prompt: "{PROMPT}"
Expected: Current weather information with sources

Results: {successful_calls}/{len(results_data)} methods returned responses

Key Questions for Human Review:
1. Do all methods return current weather information?
2. Does Perplexity include sources/citations?
3. Is the weather data consistent across methods?
4. Does llm_call properly pass through the online search results?
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
        "expected": "Current weather information with sources",
        "summary": {
            "total_methods": len(results_data),
            "successful_calls": successful_calls,
            "key_question": "Do all methods return current weather with sources?"
        },
        "results": {
            "litellm": litellm_result,
            "llm_call_ask": llm_call_result,
            "llm_call_make_request": make_request_result
        },
        "weather_checks": {
            json_key: {
                "result": result,
                "has_weather_info": has_weather,
                "check_description": check_desc
            }
            for json_key, result, has_weather, check_desc in results_data
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
    logger.info(f"Starting usage function for Test Matrix F1.6")
    results = asyncio.run(usage_function())