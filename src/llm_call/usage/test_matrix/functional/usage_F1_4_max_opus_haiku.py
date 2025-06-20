#!/usr/bin/env python3
"""
Module: usage_F1_4_max_opus_haiku.py
Description: Usage function for Test Matrix F1.4 - Max/Opus haiku generation

This usage function demonstrates:
1. Direct litellm call (NOT POSSIBLE for max/opus)
2. llm_call methods (ask and make_llm_request)
3. Side-by-side comparison for human verification

IMPORTANT: max/opus uses Claude CLI via subprocess and OAuth authentication.
Direct litellm calls are not possible. This test only compares llm_call methods.

External Dependencies:
- litellm: https://docs.litellm.ai/docs/providers/anthropic
- loguru: https://loguru.readthedocs.io/
- llm_call: Local package (installed via uv)
- rich: https://rich.readthedocs.io/
- subprocess: https://docs.python.org/3/library/subprocess.html
- claude cli: https://docs.anthropic.com/en/docs/claude-code/cli-reference

Test Matrix Reference (from ../../docs/TEST_MATRIX.md):
- Test ID: F1.4
- Priority: CRITICAL
- Category: Functional Tests > Basic Model Queries
- Model: max/opus
- Prompt: "Write a haiku about coding"
- Expected: 3 lines, 5-7-5 syllable pattern
- Verification: Format check

Usage:
>>> # Install dependencies first:
>>> uv sync
>>> # IMPORTANT: Unset ANTHROPIC_API_KEY for max/opus
>>> unset ANTHROPIC_API_KEY
>>> # Ensure Claude proxy is running:
>>> docker compose up -d claude-proxy
>>> # Run usage function:
>>> python usage_F1_4_max_opus_haiku.py
"""

import asyncio
import json
import os
import subprocess
import shlex
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.columns import Columns

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


def basic_haiku_check(text: str) -> Tuple[bool, str]:
    """
    Basic check if response looks like it could be a haiku.
    Not validating syllables, just checking format.
    """
    if not text:
        return (False, "No response")
    
    # Count lines (haiku should have 3)
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    
    if len(lines) < 3:
        return (False, f"Only {len(lines)} lines")
    
    # Look for coding-related words
    coding_words = ['code', 'coding', 'program', 'debug', 'compile', 'syntax', 'bug', 'function', 'loop', 'variable']
    has_coding = any(word in text.lower() for word in coding_words)
    
    if has_coding:
        return (True, f"Appears to be a haiku ({len(lines)} lines, coding theme)")
    else:
        return (True, f"Appears to be a haiku ({len(lines)} lines)")


async def usage_function() -> Dict[str, Any]:
    """Demonstrate usage of litellm vs llm_call for human verification"""
    
    # Initialize litellm cache first
    logger.info("Initializing litellm cache...")
    initialize_litellm_cache()
    
    # Configuration from TEST_MATRIX.md F1.4
    TEST_ID = "F1.4"
    PRIORITY = "CRITICAL"
    MODEL = "max/opus"  # Uses Claude CLI subprocess
    PROMPT = "Write a haiku about coding"
    
    logger.info("="*80)
    logger.info(f"USAGE FUNCTION - Test Matrix {TEST_ID} ({PRIORITY})")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Prompt: \"{PROMPT}\"")
    logger.info(f"Expected: 3 lines, 5-7-5 syllable pattern")
    logger.info("="*80)
    
    # Check ANTHROPIC_API_KEY - Must be UNSET for max/opus
    if os.getenv('ANTHROPIC_API_KEY'):
        logger.error("ANTHROPIC_API_KEY is set! Must be UNSET for max/opus.")
        logger.info("Run: unset ANTHROPIC_API_KEY")
        return {}
    else:
        logger.success("ANTHROPIC_API_KEY is not set (correct for max/opus)")
    
    # Find claude executable path
    claude_path_result = subprocess.run(["which", "claude"], capture_output=True, text=True)
    claude_path = claude_path_result.stdout.strip()
    if claude_path:
        # Set the Claude CLI path for llm_call to use
        os.environ['CLAUDE_CLI_PATH'] = claude_path
        logger.info(f"Found claude at: {claude_path}")
    
    # Add timestamp to make each prompt unique and avoid caching
    import time
    timestamp = int(time.time() * 1000)
    
    # 1. DIRECT SUBPROCESS CALL TO CLAUDE CLI (BASELINE)
    logger.info("\n1. DIRECT SUBPROCESS CALL (claude -p):")
    logger.info("-" * 40)
    direct_result = None
    try:
        # Find claude executable
        claude_path = subprocess.run(["which", "claude"], capture_output=True, text=True).stdout.strip()
        if not claude_path:
            raise FileNotFoundError("claude CLI not found in PATH")
        
        # Make direct subprocess call
        cmd = [claude_path, "-p", f"{PROMPT} [direct-{timestamp}]"]
        logger.info(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            direct_result = result.stdout.strip()
            logger.success(f"Result received ({len(direct_result)} chars)")
        else:
            logger.error(f"Claude CLI error: {result.stderr}")
            
    except FileNotFoundError as e:
        logger.warning(f"Claude CLI not found: {e}")
        logger.info("This is expected if claude is not installed globally")
    except subprocess.TimeoutExpired:
        logger.error("Claude CLI timed out")
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
            max_tokens=100
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
            "max_tokens": 100
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
    
    # HUMAN VERIFICATION - SIDE BY SIDE COMPARISON
    console = Console()
    
    # Create comparison table
    table = Table(title=f"Test Matrix {TEST_ID} - Method Comparison", box=box.ROUNDED)
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Basic Check", style="dim")
    
    # Collect all results
    all_results = [
        ("Direct subprocess", direct_result, "direct_subprocess"),
        ("llm_call ask()", llm_call_result, "llm_call_ask"),
        ("make_llm_request()", make_request_result, "make_llm_request")
    ]
    
    results_data = []
    
    # Process each result
    for method_name, result, json_key in all_results:
        if result:
            is_valid, reason = basic_haiku_check(result)
            status = "✅ Response" if result else "❌ No Response"
            table.add_row(method_name, status, reason)
            results_data.append((json_key, result, is_valid, reason))
        else:
            table.add_row(method_name, "❌ Failed", "No response received")
            results_data.append((json_key, None, False, "No response"))
    
    # Display table
    console.print("\n")
    console.print(table)
    
    # Show haikus side by side
    console.print("\n[bold]Generated Haikus:[/bold]\n")
    
    panels = []
    for method_name, result, json_key in all_results:
        if result:
            panel = Panel(
                result,
                title=f"[cyan]{method_name}[/cyan]",
                border_style="blue",
                padding=(1, 2)
            )
            panels.append(panel)
    
    if panels:
        console.print(Columns(panels, equal=True, expand=True))
    
    # Summary
    successful_calls = sum(1 for _, result, _, _ in results_data if result)
    
    summary = f"""
Test ID: {TEST_ID} ({PRIORITY})
Model: {MODEL}
Prompt: "{PROMPT}"

Results: {successful_calls}/{len(results_data)} methods returned responses

Key Question for Human Review:
Are the responses from all methods similar in content and format?
(They should all be haikus about coding)
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
        "expected": "3 lines, 5-7-5 syllable pattern",
        "summary": {
            "total_methods": len(results_data),
            "successful_calls": successful_calls,
            "key_question": "Are all responses similar haikus about coding?"
        },
        "results": {
            "direct_subprocess": direct_result,
            "llm_call_ask": llm_call_result,
            "llm_call_make_request": make_request_result
        },
        "basic_checks": {
            json_key: {
                "result": result, 
                "has_response": result is not None,
                "basic_check": reason
            } 
            for json_key, result, _, reason in results_data
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
    logger.info(f"Starting usage function for Test Matrix F1.4")
    results = asyncio.run(usage_function())