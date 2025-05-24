#!/usr/bin/env python3
"""
LLM Call Delegator Tool for Claude Agents.

This script enables Claude agents to make recursive LLM calls to other models.
It's designed to be executed by Claude CLI via MCP tool configuration.

Usage:
    python llm_call_delegator.py --model "vertex_ai/gemini-1.5-pro" --prompt "Analyze this text" --text "long content..."

The script uses the same llm_call framework, allowing delegation to models with
different capabilities (e.g., larger context windows).
"""

import asyncio
import json
import sys
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from dotenv import load_dotenv

# Configure minimal logging for tool execution
logger.remove()
logger.add(sys.stderr, level="ERROR")

# Import the llm_call function
try:
    # Try importing from PoC first
    from src.llm_call.proof_of_concept.litellm_client_poc import llm_call
    logger.info("Using PoC llm_call implementation")
except ImportError:
    try:
        # Fall back to core implementation
        from src.llm_call.core.caller import make_llm_request as llm_call
        logger.info("Using core llm_call implementation")
    except ImportError:
        logger.error("Could not import llm_call from either PoC or core")
        sys.exit(1)


async def delegate_llm_call(
    model: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    json_mode: bool = False,
    max_recursion_depth: int = 3,
    current_depth: int = 0
) -> Dict[str, Any]:
    """
    Make a delegated LLM call with recursion protection.
    
    Args:
        model: Target model (e.g., "vertex_ai/gemini-1.5-pro")
        prompt: User prompt
        system_prompt: Optional system prompt
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        json_mode: Whether to request JSON output
        max_recursion_depth: Maximum allowed recursion depth
        current_depth: Current recursion depth
        
    Returns:
        Dict with response or error information
    """
    # Check recursion depth
    if current_depth >= max_recursion_depth:
        return {
            "error": f"Maximum recursion depth ({max_recursion_depth}) exceeded",
            "model": model,
            "depth": current_depth
        }
    
    # Build messages
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Build LLM config
    llm_config = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "recursion_depth": current_depth + 1,  # Track depth
        "default_validate": False  # Don't validate delegated calls
    }
    
    if json_mode:
        llm_config["response_format"] = {"type": "json_object"}
    
    try:
        # Make the LLM call
        response = await llm_call(llm_config)
        
        if response is None:
            return {
                "error": "LLM call returned None",
                "model": model
            }
        
        # Extract content based on response type
        content = None
        if isinstance(response, dict):
            if "error" in response:
                return response  # Pass through error
            elif response.get("choices"):
                content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content
        else:
            content = str(response)
        
        return {
            "success": True,
            "model": model,
            "content": content,
            "recursion_depth": current_depth + 1
        }
        
    except Exception as e:
        logger.exception(f"Error in delegated LLM call to {model}")
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "model": model
        }


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Delegate LLM calls to other models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic call
  python llm_call_delegator.py --model "openai/gpt-4" --prompt "Summarize quantum computing"
  
  # With system prompt
  python llm_call_delegator.py --model "anthropic/claude-3-opus" \\
    --system "You are a helpful assistant" \\
    --prompt "Explain recursion"
  
  # JSON mode with higher temperature
  python llm_call_delegator.py --model "vertex_ai/gemini-1.5-pro" \\
    --prompt "Generate a JSON object with fields: name, age, city" \\
    --json --temperature 0.7
  
  # From file
  python llm_call_delegator.py --model "openai/gpt-4" \\
    --prompt "Analyze this document" \\
    --file /path/to/document.txt
"""
    )
    
    parser.add_argument(
        "--model", "-m",
        required=True,
        help="Target model (e.g., vertex_ai/gemini-1.5-pro, openai/gpt-4)"
    )
    
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="User prompt"
    )
    
    parser.add_argument(
        "--system", "-s",
        help="System prompt (optional)"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.0,
        help="Temperature (0.0-2.0, default: 0.0)"
    )
    
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4096,
        help="Maximum tokens (default: 4096)"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Request JSON output"
    )
    
    parser.add_argument(
        "--file", "-f",
        help="Read additional content from file to append to prompt"
    )
    
    parser.add_argument(
        "--max-recursion",
        type=int,
        default=3,
        help="Maximum recursion depth (default: 3)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Build the full prompt
    full_prompt = args.prompt
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_content = f.read()
            full_prompt = f"{args.prompt}\n\nContent from {args.file}:\n{file_content}"
        except Exception as e:
            error_result = {
                "error": f"Failed to read file {args.file}: {e}",
                "error_type": "FileReadError"
            }
            print(json.dumps(error_result, indent=2))
            sys.exit(1)
    
    # Run the async function
    result = asyncio.run(delegate_llm_call(
        model=args.model,
        prompt=full_prompt,
        system_prompt=args.system,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        json_mode=args.json,
        max_recursion_depth=args.max_recursion
    ))
    
    # Output the result as JSON to stdout
    print(json.dumps(result, indent=2))
    
    # Exit with appropriate code
    if result.get("success"):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()