"""
Module: focused_claude_extractor.py
Description: Functions for focused claude extractor operations

External Dependencies:
- loguru: [Documentation URL]
- shlex: [Documentation URL]

Sample Input:
>>> # Add specific examples based on module functionality

Expected Output:
>>> # Add expected output examples

Example Usage:
>>> # Add usage examples
"""

# focused_claude_executor.py
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger # Using loguru for internal logging of this function
import sys
import shlex

# Configure logger for this module
logger.remove()
logger.add(sys.stderr, level="DEBUG", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>")

# --- IMPORTANT: Update this path to your actual Claude CLI executable ---
DEFAULT_CLAUDE_PATH = "/home/graham/.nvm/versions/node/v22.15.0/bin/claude"
# --- End Important Path ---

def execute_claude_and_get_result(
    prompt: str,
    system_prompt_content: str,
    target_dir: Path,
    claude_exe_path: Path = Path(DEFAULT_CLAUDE_PATH),
    pass_verbose_to_claude: bool = True, # Controls if --verbose is added to claude command
) -> Optional[str]:
    """
    Executes the Claude CLI with a given prompt and system prompt in a specific
    target directory, streams its JSON output, and attempts to extract the
    final 'result' field from the success message.

    Args:
        prompt: The user prompt for Claude.
        system_prompt_content: The content of the system prompt.
        target_dir: The directory where the Claude command should be executed (CWD).
        claude_exe_path: Path to the Claude CLI executable.
        pass_verbose_to_claude: If True, passes '--verbose' to the Claude CLI.

    Returns:
        The string content of the 'result' field from the final successful JSON message,
        or None if not found or an error occurs.
    """
    if not claude_exe_path.is_file():
        logger.error(f"Claude executable not found at: {claude_exe_path}")
        return None
    if not target_dir.is_dir():
        logger.error(f"Target directory not found: {target_dir}")
        return None

    cmd_list = [
        str(claude_exe_path),
        "--system-prompt", system_prompt_content,
        "-p", prompt,
        "--output-format", "stream-json",
    ]
    if pass_verbose_to_claude:
        cmd_list.append("--verbose")

    logger.info(f"Executing command in CWD '{target_dir}': {' '.join(shlex.quote(c) for c in cmd_list)}")

    process = None
    final_result_content: Optional[str] = None
    full_stdout_capture = [] # To capture all lines for debugging if needed

    try:
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_dir), # Set Current Working Directory
            bufsize=1 # Line buffering
        )

        logger.info(f"Claude subprocess started (PID: {process.pid}). Streaming output...")

        for line in iter(process.stdout.readline, ''):
            stripped_line = line.strip()
            full_stdout_capture.append(stripped_line) # Store all lines
            logger.debug(f"Raw stream line: {stripped_line}")
            if not stripped_line:
                continue
            
            try:
                data = json.loads(stripped_line)
                # Look for the final result message which typically has type "result" and subtype "success"
                if data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"]
                        logger.info(f"Successfully extracted final 'result' content (length: {len(final_result_content)}).")
                        # We could break here if we only care about the final result object,
                        # but Claude might send other messages after. Let's consume all stdout.
                elif data.get("type") == "assistant" and isinstance(data.get("message"), dict):
                    # Log assistant message chunks for context if needed during debugging
                    message_content_list = data["message"].get("content", [])
                    for content_item in message_content_list:
                        if content_item.get("type") == "text":
                            logger.debug(f"Assistant text chunk: {content_item.get('text', '')[:100]}...")
                elif data.get("type") == "result" and data.get("subtype") == "error":
                    logger.error(f"Claude stream reported an error: {data}")
                    # Continue streaming to see if more info comes, but note the error

            except json.JSONDecodeError:
                logger.warning(f"Non-JSON line in stream or decode error: {stripped_line}")
            except Exception as e:
                logger.error(f"Error processing streamed JSON line '{stripped_line}': {e}")
        
        # Wait for the process to complete and get remaining outputs
        stdout_remaining, stderr_output = process.communicate(timeout=60) # Timeout for safety
        
        if stdout_remaining:
            full_stdout_capture.append(stdout_remaining.strip())
            logger.debug(f"Remaining STDOUT after stream: {stdout_remaining.strip()}")
        if stderr_output:
            logger.error(f"STDERR from Claude process:\n{stderr_output.strip()}")

        if process.returncode != 0:
            logger.error(f"Claude process exited with error code {process.returncode}.")
            # If final_result_content wasn't found via a "success" message,
            # and there was an error, we might not have the desired result.
            # Consider returning None or raising an exception. For now, returns what was found.

        if not final_result_content:
            logger.warning("Final 'result' field not found in Claude's output stream from a 'success' message.")
            # Attempt to find it in the full capture if it was the last object and not fully streamed
            for captured_line in reversed(full_stdout_capture):
                try:
                    data = json.loads(captured_line)
                    if data.get("type") == "result" and data.get("subtype") == "success" and "result" in data:
                        final_result_content = data["result"]
                        logger.info("Found 'result' in late-stage captured output.")
                        break
                except Exception:  # Keep generic as marked with #nosec
                    pass


    except subprocess.TimeoutExpired:
        logger.error("Claude process timed out.")
        if process:
            process.kill()
            process.communicate() # Clean up pipes
        return None
    except Exception as e:
        logger.exception(f"An error occurred while running Claude: {e}")
        return None
    finally:
        if process and process.poll() is None:
            logger.warning("Claude process still running in finally block, attempting to terminate.")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        logger.info("Claude execution function finished.")

    return final_result_content


if __name__ == "__main__":
    logger.info("Starting focused Claude execution test...")

    # Parameters for your specific scenario
    test_prompt = "What is the exact pdf export schema you expect from me. Give me a JSON of the schema with a summary description"
    test_target_dir_str = "/home/graham/workspace/experiments/arangodb/"
    test_system_prompt_file_str = "/home/graham/workspace/experiments/marker/system_prompt.md"
    
    test_target_dir = Path(test_target_dir_str)
    test_system_prompt_file = Path(test_system_prompt_file_str)

    system_prompt_text_content = ""
    if test_system_prompt_file.is_file():
        try:
            with open(test_system_prompt_file, 'r') as f:
                system_prompt_text_content = f.read()
            logger.info(f"Read system prompt from: {test_system_prompt_file}")
        except Exception as e:
            logger.error(f"Could not read system prompt file {test_system_prompt_file}: {e}")
            sys.exit(1)
    else:
        logger.error(f"System prompt file not found: {test_system_prompt_file}")
        # Example: Fallback or exit
        # system_prompt_text_content = "You are a helpful assistant for ArangoDB." 
        sys.exit(1)


    if not test_target_dir.is_dir():
        logger.error(f"Target directory does not exist: {test_target_dir}")
        sys.exit(1)

    # Execute the focused function
    result = execute_claude_and_get_result(
        prompt=test_prompt,
        system_prompt_content=system_prompt_text_content,
        target_dir=test_target_dir,
        # claude_exe_path=Path("/path/to/your/claude"), # Uncomment and set if different from DEFAULT_CLAUDE_PATH
        pass_verbose_to_claude=True 
    )

    if result:
        logger.info("Successfully retrieved result from Claude.")
        print("\n--- CLAUDE FINAL RESULT ---")
        try:
            # Attempt to pretty-print if it's JSON
            parsed_json_result = json.loads(result)
            print(json.dumps(parsed_json_result, indent=4))
        except json.JSONDecodeError:
            # If not JSON, print as is
            print(result)
        print("--- END OF RESULT ---")
    else:
        logger.error("Failed to retrieve a result from Claude.")

