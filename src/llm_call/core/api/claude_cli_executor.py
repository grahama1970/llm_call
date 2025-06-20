"""
Claude CLI executor module.
Module: claude_cli_executor.py
Description: Functions for claude cli executor operations

This module handles the execution of Claude CLI commands via subprocess,
capturing and parsing the JSON stream output.

Links:
- subprocess documentation: https://docs.python.org/3/library/subprocess.html

Sample usage:
    response = execute_claude_cli(prompt="Hello", system_prompt_content="Be helpful", ...)

Expected output:
    String containing Claude's response or error message'
"""

import json
import subprocess
import shlex
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from llm_call.core.api.mcp_handler import write_mcp_config, remove_mcp_config


def execute_claude_cli(
    prompt: str,
    system_prompt_content: str,
    target_dir: Path,
    claude_exe_path: Path,
    timeout: int = 120,
    mcp_config: Optional[Dict[str, Any]] = None,
    model_name: Optional[str] = None
) -> Optional[str]:
    """
    Execute Claude CLI and capture response.
    
    This function runs the Claude CLI as a subprocess, captures its JSON
    stream output, and extracts the response text. This is migrated from
    the POC's execute_claude_cli_for_poc function.'
    
    Args:
        prompt: User's prompt/question'
        system_prompt_content: System prompt for Claude
        target_dir: Working directory for Claude CLI
        claude_exe_path: Path to Claude executable
        timeout: Maximum time to wait for response
        
    Returns:
        Claude's response text or error message'
    """
    logger.info(f"[Claude Executor] Attempting to execute Claude CLI")
    
    # Validate inputs
    if not claude_exe_path.is_file():
        logger.error(f"[Claude Executor] Claude executable not found at: {claude_exe_path}")
        return f"Claude CLI not found at {claude_exe_path}"
    
    if not target_dir.is_dir():
        logger.error(f"[Claude Executor] Target directory not found: {target_dir}")
        return f"Target directory not found: {target_dir}"
    
    # Handle MCP configuration if provided
    mcp_file_path: Optional[Path] = None
    if mcp_config:
        try:
            mcp_file_path = write_mcp_config(target_dir, mcp_config)
            logger.info(f"[Claude Executor] Wrote MCP config with tools: {list(mcp_config.get('mcpServers', {}).keys())}")
        except Exception as e:
            logger.error(f"[Claude Executor] Failed to write MCP config: {e}")
            return f"Failed to write MCP configuration: {e}"
    
    # Parse model name from max/ prefix if provided
    claude_model_spec = None
    if model_name and model_name.lower().startswith("max/"):
        # Extract the part after "max/"
        model_suffix = model_name[4:]  # Skip "max/"
        if model_suffix:
            # Map common aliases or use as-is
            if model_suffix.lower() == "opus":
                claude_model_spec = "opus"
            elif model_suffix.lower() == "sonnet":
                claude_model_spec = "sonnet"
            elif model_suffix.startswith("claude-"):
                # Full model names like claude-opus-4-20250514
                claude_model_spec = model_suffix
            else:
                # Try to use as-is (could be other valid model names)
                claude_model_spec = model_suffix
                logger.warning(f"[Claude Executor] Using unrecognized model spec: {model_suffix}")
        else:
            # Default to opus if no model specified after max/
            claude_model_spec = "opus"
            logger.info("[Claude Executor] No model specified after max/, defaulting to opus")
    
    # Construct command (from POC)
    cmd_list = [
        str(claude_exe_path),
        "--system-prompt", system_prompt_content,
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose"  # Required for stream-json output
    ]
    
    # Add model flag if specified
    if claude_model_spec:
        cmd_list.extend(["--model", claude_model_spec])
        logger.info(f"[Claude Executor] Using model: {claude_model_spec}")
    
    logger.info(f"[Claude Executor] Executing in CWD '{target_dir}': {' '.join(shlex.quote(c) for c in cmd_list)}")
    
    process = None
    final_result_content: Optional[str] = None
    full_response_text = ""  # To accumulate text from assistant messages
    
    try:
        # Start subprocess (matching POC implementation)
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_dir),
            bufsize=1  # Line-buffered
        )
        logger.info(f"[Claude Executor] Claude subprocess started (PID: {process.pid})")
        
        # Process output stream (from POC)
        for line in iter(process.stdout.readline, ''):
            stripped_line = line.strip()
            logger.debug(f"[Claude Executor] Raw stream line: {stripped_line}")
            
            if not stripped_line:
                continue
                
            try:
                data = json.loads(stripped_line)
                
                # Accumulate text from 'assistant' type messages (from POC)
                if data.get("type") == "assistant" and isinstance(data.get("message"), dict):
                    content_list = data["message"].get("content", [])
                    for item in content_list:
                        if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                            full_response_text += item["text"]
                
                # Check for completion (from POC)
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"]
                        logger.info("[Claude Executor] Successfully extracted final 'result' content")
                    
                    # If no result field but we have accumulated text, use that
                    if not final_result_content and full_response_text:
                        final_result_content = full_response_text.strip()
                    elif not final_result_content and not full_response_text:
                        logger.warning("[Claude Executor] 'result:success' message had no content")
                    break
                
                # Handle errors (from POC)
                elif data.get("type") == "result" and data.get("subtype") == "error":
                    logger.error(f"[Claude Executor] Claude CLI stream reported error: {data}")
                    final_result_content = f"Error from Claude CLI: {data.get('error', 'Unknown error')}"
                    break
                    
            except json.JSONDecodeError:
                logger.warning(f"[Claude Executor] Non-JSON line in stream: {stripped_line}")
            except Exception as e:
                logger.error(f"[Claude Executor] Error processing streamed JSON: {e}")
        
        # If no result yet but we have accumulated text, use it (from POC)
        if final_result_content is None and full_response_text:
            logger.info("[Claude Executor] Using accumulated text from assistant messages")
            final_result_content = full_response_text.strip()
        elif final_result_content is None:
            logger.warning("[Claude Executor] No usable content extracted from Claude CLI stream")
            final_result_content = "No content received from Claude CLI."
        
        # Wait for process to complete
        _, stderr_output = process.communicate(timeout=timeout)
        
        if stderr_output:
            # Filter deprecation warnings (from POC)
            if "deprecated" not in stderr_output.lower():
                logger.error(f"[Claude Executor] STDERR: {stderr_output.strip()}")
            else:
                logger.debug(f"[Claude Executor] STDERR (deprecated warning): {stderr_output.strip()}")
        
        if process.returncode != 0:
            logger.error(f"[Claude Executor] Claude process exited with code {process.returncode}")
            if final_result_content is None or "Error from Claude CLI" not in final_result_content:
                return f"Claude CLI exited with code {process.returncode}. Stderr: {stderr_output.strip()}"
    
    except subprocess.TimeoutExpired:
        logger.error("[Claude Executor] Claude process timed out")
        if process:
            process.kill()
            process.communicate()
        return "Claude process timed out."
    
    except FileNotFoundError:
        logger.error(f"[Claude Executor] Claude CLI executable not found at {claude_exe_path}")
        return f"Claude CLI not found at {claude_exe_path}"
    
    except Exception as e:
        logger.exception(f"[Claude Executor] Unexpected error: {e}")
        return f"Unexpected server error: {e}"
    
    finally:
        # Ensure process is terminated (from POC)
        if process and process.poll() is None:
            logger.warning("[Claude Executor] Claude process still running, terminating")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Clean up MCP configuration file
        if mcp_file_path:
            remove_mcp_config(mcp_file_path)
    
    return final_result_content if final_result_content is not None else "No output from Claude CLI."


# Test function
if __name__ == "__main__":
    import sys
    from llm_call.core.config.loader import load_configuration
    settings = load_configuration()
    
    logger.info("Testing Claude CLI executor...")
    
    # Test the executor with a simple prompt
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic execution test (only if Claude CLI exists)
    total_tests += 1
    cli_path = Path(settings.claude_proxy.cli_path)
    
    if cli_path.exists():
        try:
            response = execute_claude_cli(
                prompt="Say 'Hello, test successful!' and nothing else.",
                system_prompt_content="You are a test assistant. Follow instructions exactly.",
                target_dir=settings.claude_proxy.workspace_dir,
                claude_exe_path=cli_path,
                timeout=30
            )
            
            if response and "test successful" in response.lower():
                logger.success(f" Claude CLI execution works: {response[:100]}...")
            else:
                all_validation_failures.append(f"Unexpected response: {response}")
        except Exception as e:
            all_validation_failures.append(f"Execution test failed: {e}")
    else:
        logger.warning(f"⚠️ Skipping execution test - Claude CLI not found at {cli_path}")
        logger.info("This is expected in test environments without Claude CLI")
    
    # Test 2: Error handling for missing executable
    total_tests += 1
    try:
        response = execute_claude_cli(
            prompt="Test",
            system_prompt_content="Test",
            target_dir=settings.claude_proxy.workspace_dir,
            claude_exe_path=Path("/nonexistent/claude"),
            timeout=5
        )
        
        assert "Claude CLI not found" in response
        logger.success(" Missing executable error handling works")
    except Exception as e:
        all_validation_failures.append(f"Error handling test failed: {e}")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f" VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f" VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)