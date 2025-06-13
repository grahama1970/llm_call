"""
Module: claude_executor.py
Description: Functions for claude executor operations

External Dependencies:
- shlex: [Documentation URL]
- loguru: [Documentation URL]
- : [Documentation URL]
- shutil: [Documentation URL]

Sample Input:
>>> # Add specific examples based on module functionality

Expected Output:
>>> # Add expected output examples

Example Usage:
>>> # Add usage examples
"""

# src/claude_comms/inter_module_communicator/core/claude_executor.py
"""
Core logic for executing the Claude CLI as a subprocess, streaming its output,
and yielding structured events or data.
"""
import subprocess
import json
import shlex
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Iterator, List, Union
from loguru import logger

from . import config # For DEFAULT_CLAUDE_PATH, DEFAULT_CLAUDE_CLI_VERBOSE

# Ensure logger is configured if this module is run standalone for validation
# In a full app, the CLI layer would typically configure logging.
if not logger.configured: # type: ignore
    logger.remove()
    logger.add(sys.stderr, level="DEBUG", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>")


def construct_claude_command(
    claude_exe_path: Path,
    prompt_text: str,
    system_prompt_content: Optional[str] = None,
    pass_verbose_to_claude_cli: bool = config.DEFAULT_CLAUDE_CLI_VERBOSE,
) -> List[str]:
    """
    Constructs the command list for executing the Claude CLI.

    Args:
        claude_exe_path: Path to the Claude CLI executable.
        prompt_text: The main prompt/question for Claude.
        system_prompt_content: Optional content for the system prompt.
        pass_verbose_to_claude_cli: Whether to add '--verbose' to the Claude command.

    Returns:
        A list of strings representing the command and its arguments.
    """
    if not claude_exe_path.is_file():
        msg = f"Claude executable not found at specified path: {claude_exe_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    cmd_list = [
        str(claude_exe_path),
        "-p", prompt_text,
        "--output-format", "stream-json",
    ]
    if pass_verbose_to_claude_cli:
        cmd_list.append("--verbose")
    
    if system_prompt_content:
        cmd_list.extend(["--system-prompt", system_prompt_content])
    
    return cmd_list

def execute_claude_task(
    progress_id: str, # For contextual logging
    cmd_list: List[str],
    target_cwd: Path,
) -> Iterator[Dict[str, Any]]:
    """
    Executes the constructed Claude command as a subprocess, streams its stdout,
    parses JSON lines, and yields structured event dictionaries.

    Args:
        progress_id: Unique ID for the task, used for logging context.
        cmd_list: The fully constructed command list to execute.
        target_cwd: The Path object for the current working directory for the subprocess.

    Yields:
        Dictionaries representing structured events from the Claude CLI stream
        or error/completion information. Examples:
        - {"type": "status_update", "status": "claude_init", "details": {"session_id": "..."}}
        - {"type": "text_chunk", "chunk": "some text"}
        - {"type": "final_result", "subtype": "success", "content": "full_text"}
        - {"type": "final_result", "subtype": "error", "details": {...}, "raw_stderr": "..."}
        - {"type": "subprocess_event", "event_type": "start", "pid": 123}
        - {"type": "subprocess_event", "event_type": "exit", "code": 0, "raw_stderr": "..."}
    """
    with logger.contextualize(progress_id=progress_id):
        if not target_cwd.is_dir():
            msg = f"Target CWD does not exist or is not a directory: {target_cwd}"
            logger.error(msg)
            yield {"type": "final_result", "subtype": "error", "details": {"message": msg, "reason": "invalid_target_dir"}, "raw_stderr": ""}
            return

        logger.info(f"Executing command in CWD '{target_cwd}': {' '.join(shlex.quote(c) for c in cmd_list)}")
        process = None
        
        try:
            process = subprocess.Popen(
                cmd_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(target_cwd),
                bufsize=1 # Line buffering
            )
            yield {"type": "subprocess_event", "event_type": "start", "pid": process.pid}
            logger.info(f"Claude subprocess started (PID: {process.pid}). Streaming output...")

            accumulated_text_chunks: List[str] = []

            for line in iter(process.stdout.readline, ''): # type: ignore
                stripped_line = line.strip()
                logger.debug(f"Raw stream line: {stripped_line}") # Will go to file log
                if not stripped_line:
                    continue
                
                try:
                    data = json.loads(stripped_line)
                    event_yielded = False
                    if data.get("type") == "assistant" and \
                       isinstance(data.get("message"), dict) and \
                       isinstance(data["message"].get("content"), list):
                        for item in data["message"]["content"]:
                            if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                                chunk = item["text"]
                                accumulated_text_chunks.append(chunk)
                                yield {"type": "text_chunk", "chunk": chunk}
                                event_yielded = True
                                # Assuming one primary text chunk per assistant message for simplicity
                                break 
                    elif data.get("type") == "system" and data.get("subtype") == "init":
                        yield {"type": "status_update", "status": "claude_init", "details": data}
                        event_yielded = True
                    elif data.get("type") == "result":
                        # This is a final result message from Claude CLI (success or error)
                        # The 'result' field in case of success often contains the full assembled text
                        final_content = data.get("result", "".join(accumulated_text_chunks))
                        if data.get("subtype") == "success":
                            yield {"type": "final_result", "subtype": "success", "content": final_content, "raw_data": data}
                        else: # error or other subtype
                            yield {"type": "final_result", "subtype": "error", "details": data, "content_so_far": final_content}
                        event_yielded = True
                        # After a 'result' message, the stream might end or send other metadata.
                        # For this PoC, we assume it's a terminal message for content.
                    
                    if not event_yielded: # Log other unhandled JSON structures
                         logger.debug(f"Other JSON object received: {data}")
                         yield {"type": "unhandled_json_event", "data": data}


                except json.JSONDecodeError:
                    logger.warning(f"Non-JSON line in stream or decode error: {stripped_line}")
                    yield {"type": "stream_parsing_error", "line": stripped_line}
                except Exception as e_parse:
                    logger.error(f"Error processing streamed JSON line '{stripped_line}': {e_parse}")
                    yield {"type": "stream_processing_error", "line": stripped_line, "error": str(e_parse)}
            
            # After loop, communicate to get final stderr and ensure process termination
            stdout_remaining, stderr_output = process.communicate(timeout=config.DEFAULT_SUBPROCESS_TIMEOUT)
            
            if stdout_remaining.strip():
                logger.debug(f"Remaining STDOUT after stream iter: {stdout_remaining.strip()}")
                # Process any final lines if necessary, though iter should have caught them
            
            logger.info(f"Claude subprocess exited with code {process.returncode}.")
            yield {"type": "subprocess_event", "event_type": "exit", "code": process.returncode, "raw_stderr": stderr_output.strip()}

        except subprocess.TimeoutExpired:
            logger.error("Claude subprocess timed out during communicate().")
            if process:
                process.kill()
                process.communicate() # Clean up pipes
            yield {"type": "final_result", "subtype": "error", "details": {"message": "Subprocess timed out"}, "raw_stderr": "Timeout during communicate()"}
        except FileNotFoundError as e_fnf: # For Popen itself
            logger.error(f"Failed to start Claude subprocess: {e_fnf}. Check claude_exe_path.")
            yield {"type": "final_result", "subtype": "error", "details": {"message": str(e_fnf), "reason": "executable_not_found"}, "raw_stderr": ""}
        except Exception as e_global:
            logger.exception(f"An unexpected error occurred during Claude execution: {e_global}")
            if process and process.poll() is None:
                process.kill()
                process.communicate()
            yield {"type": "final_result", "subtype": "error", "details": {"message": str(e_global), "reason": "unknown_execution_error"}, "raw_stderr": ""}
        finally:
            if process and process.poll() is None:
                logger.warning("Claude subprocess still running in finally, attempting to terminate.")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.error("Claude subprocess did not terminate gracefully, killing.")
                    process.kill()
            logger.debug("execute_claude_task generator finished.")

if __name__ == "__main__":
    # --- Validation Block ---
    print("Running validation for core/claude_executor.py...")
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Command Construction
    total_tests += 1
    logger.info("\nTest 1: Command Construction")
    try:
        test_exe_path = Path(config.DEFAULT_CLAUDE_PATH) # Assuming this exists for test
        if not test_exe_path.is_file():
             logger.warning(f"DEFAULT_CLAUDE_PATH '{test_exe_path}' not found, command construction test might be limited.")
        
        cmd = construct_claude_command(
            claude_exe_path=test_exe_path,
            prompt_text="Hello Claude",
            system_prompt_content="You are a helpful AI.",
            pass_verbose_to_claude_cli=True
        )
        expected_cmd_part = [str(test_exe_path), "-p", "Hello Claude", "--output-format", "stream-json", "--verbose", "--system-prompt", "You are a helpful AI."]
        if cmd == expected_cmd_part:
            logger.info("Test 1.1 PASSED: Command constructed correctly with system prompt and verbose.")
        else:
            all_validation_failures.append(f"Test 1.1 FAILED: Command mismatch. Expected: {expected_cmd_part}, Got: {cmd}")

        cmd_no_sys = construct_claude_command(test_exe_path, "Hi", pass_verbose_to_claude_cli=False)
        expected_cmd_no_sys = [str(test_exe_path), "-p", "Hi", "--output-format", "stream-json"]
        if cmd_no_sys == expected_cmd_no_sys:
            logger.info("Test 1.2 PASSED: Command constructed correctly without system prompt and no verbose.")
        else:
            all_validation_failures.append(f"Test 1.2 FAILED: Command mismatch. Expected: {expected_cmd_no_sys}, Got: {cmd_no_sys}")

    except Exception as e:
        all_validation_failures.append(f"Test 1 FAILED: Unexpected exception: {e}")

    # Test 2: Simulation Execution and Event Yielding
    total_tests += 1
    logger.info("\nTest 2: Simulation Execution and Event Yielding")
    
    # Create a dummy target directory for the test
    dummy_target_dir = Path("./dummy_claude_target_dir_executor_test")
    dummy_target_dir.mkdir(parents=True, exist_ok=True)
    
    test_sim_progress_id = "val_exec_sim_" + str(uuid.uuid4())
    
    # Simulation command (bash -c "echo ...")
    sim_prompt = "Simulate this"
    sim_sys_prompt = "You are a simulator."
    sim_json_output1 = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Sim chunk 1 "}]}}
    sim_json_output2 = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Sim chunk 2"}]}}
    sim_json_result = {"type": "result", "subtype": "success", "result": "Sim chunk 1 Sim chunk 2"}
    
    simulate_script_content = f"""
    echo '{json.dumps(sim_json_output1)}'
    sleep 0.1
    echo '{json.dumps(sim_json_output2)}'
    sleep 0.1
    echo '{json.dumps(sim_json_result)}'
    """
    sim_cmd_list = ["bash", "-c", simulate_script_content]
    
    events_received = []
    try:
        for event in execute_claude_task(test_sim_progress_id, sim_cmd_list, dummy_target_dir):
            logger.info(f"Validation received event: {event}")
            events_received.append(event)
        
        # Verification of events
        if not any(e.get("type") == "subprocess_event" and e.get("event_type") == "start" for e in events_received):
            all_validation_failures.append("Test 2.1 FAILED: Did not receive 'subprocess_event start'.")
        
        text_chunks = [e["chunk"] for e in events_received if e.get("type") == "text_chunk"]
        if len(text_chunks) != 2 or "".join(text_chunks) != "Sim chunk 1 Sim chunk 2":
            all_validation_failures.append(f"Test 2.2 FAILED: Text chunks mismatch. Got: {''.join(text_chunks)}")
        else:
            logger.info("Test 2.2 PASSED: Correct text chunks received.")

        final_result_event = next((e for e in events_received if e.get("type") == "final_result" and e.get("subtype") == "success"), None)
        if not final_result_event or final_result_event.get("content") != "Sim chunk 1 Sim chunk 2":
            all_validation_failures.append(f"Test 2.3 FAILED: Final result content mismatch. Got: {final_result_event}")
        else:
            logger.info("Test 2.3 PASSED: Correct final result event received.")

        if not any(e.get("type") == "subprocess_event" and e.get("event_type") == "exit" and e.get("code") == 0 for e in events_received):
            all_validation_failures.append("Test 2.4 FAILED: Did not receive 'subprocess_event exit' with code 0.")
        else:
            logger.info("Test 2.4 PASSED: Subprocess exit event with code 0 received.")

    except Exception as e:
        all_validation_failures.append(f"Test 2 FAILED: Unexpected exception during simulation: {e}")
    finally:
        if dummy_target_dir.exists():
            try:
                # Clean up dummy directory - be careful with rmtree
                import shutil
                shutil.rmtree(dummy_target_dir)
                logger.info(f"Cleaned up dummy target directory: {dummy_target_dir}")
            except Exception as e_clean:
                logger.error(f"Error cleaning up dummy target directory: {e_clean}")
    
    # Test 3: Handling Executable Not Found
    total_tests += 1
    logger.info("\nTest 3: Handling Executable Not Found")
    non_existent_exe = Path("./non_existent_claude_executable_for_test")
    try:
        cmd_fail = construct_claude_command(non_existent_exe, "test")
        # This should raise FileNotFoundError in construct_claude_command
        all_validation_failures.append("Test 3.1 FAILED: construct_claude_command did not raise FileNotFoundError for non-existent exe.")
    except FileNotFoundError:
        logger.info("Test 3.1 PASSED: construct_claude_command correctly raised FileNotFoundError.")
    except Exception as e:
        all_validation_failures.append(f"Test 3.1 FAILED: Unexpected exception: {e}")

    events_fail_exe = []
    try:
        # The execute_claude_task itself should yield an error if Popen fails due to FileNotFoundError
        # For this test, we'll directly test the scenario where Popen would fail.
        # To do this properly, we'd need to mock Popen or ensure the FileNotFoundError from construct_claude_command
        # is handled if execute_claude_task calls it.
        # The current execute_claude_task expects cmd_list as input.
        # Let's test its FileNotFoundError path for Popen.
        
        # Create a dummy command list with a non-existent executable
        fail_cmd_list = [str(non_existent_exe), "-p", "test"]
        for event in execute_claude_task("val_exec_fail", fail_cmd_list, dummy_target_dir): # dummy_target_dir might be cleaned up, recreate if needed
            if not dummy_target_dir.exists(): dummy_target_dir.mkdir(exist_ok=True)
            events_fail_exe.append(event)
        
        final_error_event = next((e for e in events_fail_exe if e.get("type") == "final_result" and e.get("subtype") == "error"), None)
        if final_error_event and final_error_event.get("details", {}).get("reason") == "executable_not_found":
            logger.info("Test 3.2 PASSED: execute_claude_task yielded correct error for non-existent executable.")
        else:
            all_validation_failures.append(f"Test 3.2 FAILED: Incorrect or missing error event for non-existent exe. Got: {final_error_event}")

    except Exception as e:
         all_validation_failures.append(f"Test 3.2 FAILED: Unexpected exception: {e}")
    finally:
        if dummy_target_dir.exists():
            try:
                import shutil
                shutil.rmtree(dummy_target_dir)
            except Exception: # nosec
                pass


    # Final validation result
    if all_validation_failures:
        logger.error(f" VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for i, failure in enumerate(all_validation_failures):
            logger.error(f"  Failure {i+1}: {failure}")
        sys.exit(1)
    else:
        logger.info(f" VALIDATION PASSED - All {total_tests} tests produced expected results for claude_executor.py.")
        logger.info("Module is validated and formal tests can now be written.")
        sys.exit(0)
