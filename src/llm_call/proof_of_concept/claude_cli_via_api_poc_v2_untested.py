import asyncio
import httpx
import json
import os
import subprocess # For Popen
import shlex # For command construction
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn # To run FastAPI programmatically for the PoC
import time

from loguru import logger
from dotenv import load_dotenv
load_dotenv()

# from llm_call.core.utils.json_utils import clean_json_string

# --- PoC Configuration ---
POC_SERVER_HOST = "127.0.0.1" # Use 127.0.0.1 for localhost
POC_SERVER_PORT = 8001 # Use a different port to avoid conflict with other services like your main proxy
FASTAPI_POC_ENDPOINT_URL = f"http://{POC_SERVER_HOST}:{POC_SERVER_PORT}/v1/chat/completions"

# IMPORTANT: Path to your Claude CLI executable for this PoC
# Ensure this is correct for the environment where this script runs.
# It can be an absolute path.
# For this PoC, we are not using the config files from the main project to keep it self-contained.
CLAUDE_CLI_PATH = "/home/graham/.nvm/versions/node/v22.15.0/bin/claude" # ADJUST IF NECESSARY
# Directory where the Claude CLI should execute its commands (CWD for Popen)
# This directory might need to exist and have appropriate permissions.
# For simplicity, let's use the current script's directory or a subdir.
POC_TARGET_DIR = Path(__file__).parent.resolve() / "claude_poc_workspace" 
POC_TARGET_DIR.mkdir(exist_ok=True) # Ensure it exists

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}:{line}</cyan> - <level>{message}</level>", level="INFO")


# --- Minimal Claude CLI Interaction Logic (inspired by focused_claude_extractor.py) ---
def execute_claude_cli_for_poc(
    prompt: str,
    system_prompt_content: str,
    target_dir: Path,
    claude_exe_path: Path,
) -> Optional[str]:
    logger.info(f"[SERVER-SIDE PoC] Attempting to execute Claude CLI.")
    if not claude_exe_path.is_file():
        logger.error(f"[SERVER-SIDE PoC] Claude executable not found at: {claude_exe_path}")
        return None
    if not target_dir.is_dir():
        logger.error(f"[SERVER-SIDE PoC] Target directory not found: {target_dir}")
        return None

    cmd_list = [
        str(claude_exe_path),
        "--system-prompt", system_prompt_content,
        "-p", prompt,
        "--output-format", "stream-json", # We'll parse this stream
        "--verbose"
    ]


    logger.info(f"[SERVER-SIDE PoC] Executing command in CWD '{target_dir}': {' '.join(shlex.quote(c) for c in cmd_list)}")

    process = None
    final_result_content: Optional[str] = None
    
    try:
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(target_dir),
            bufsize=1
        )
        logger.info(f"[SERVER-SIDE PoC] Claude subprocess started (PID: {process.pid}).")

        full_response_text = "" # To accumulate text chunks if needed

        for line in iter(process.stdout.readline, ''):
            stripped_line = line.strip()
            logger.debug(f"[SERVER-SIDE PoC] Raw stream line: {stripped_line}")
            if not stripped_line:
                continue
            
            try:
                data = json.loads(stripped_line)
                if data.get("type") == "assistant" and isinstance(data.get("message"), dict):
                    content_list = data["message"].get("content", [])
                    for item in content_list:
                        if isinstance(item, dict) and item.get("type") == "text" and "text" in item:
                            full_response_text += item["text"] # Accumulate text
                elif data.get("type") == "result" and data.get("subtype") == "success":
                    if "result" in data and isinstance(data["result"], str):
                        final_result_content = data["result"] # This usually contains the full message
                        logger.info(f"[SERVER-SIDE PoC] Successfully extracted final 'result' content.")
                        # If the 'result' field is what we want, we can stop accumulating
                        # For this simple PoC, the last 'result' is typically the full one.
                    break # Assuming the first "success" result is the one we want
            except json.JSONDecodeError:
                logger.warning(f"[SERVER-SIDE PoC] Non-JSON line in stream: {stripped_line}")
            except Exception as e_parse:
                logger.error(f"[SERVER-SIDE PoC] Error processing streamed JSON: {e_parse}")
        
        # If final_result_content wasn't found in a "result" message, use accumulated text
        if final_result_content is None and full_response_text:
            logger.info("[SERVER-SIDE PoC] Using accumulated text as final result.")
            final_result_content = full_response_text.strip()

        stdout_remaining, stderr_output = process.communicate(timeout=60) # Wait for process to finish
        
        if stderr_output:
            logger.error(f"[SERVER-SIDE PoC] STDERR from Claude process:\n{stderr_output.strip()}")
        if process.returncode != 0:
            logger.error(f"[SERVER-SIDE PoC] Claude process exited with error code {process.returncode}.")
            # Return None or raise an exception to indicate failure to the FastAPI endpoint handler
            return None # Or more specific error

    except subprocess.TimeoutExpired:
        logger.error("[SERVER-SIDE PoC] Claude process timed out.")
        if process: process.kill(); process.communicate()
        return None
    except FileNotFoundError:
        logger.error(f"[SERVER-SIDE PoC] Claude CLI executable not found at {claude_exe_path}. Cannot run Popen.")
        return None
    except Exception as e:
        logger.exception(f"[SERVER-SIDE PoC] An error occurred while running Claude: {e}")
        return None
    finally:
        if process and process.poll() is None:
            logger.warning("[SERVER-SIDE PoC] Claude process still running, terminating.")
            process.terminate()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill()

    return final_result_content

# --- Minimal FastAPI Application (embedded in PoC) ---
poc_fastapi_app = FastAPI(title="PoC Claude CLI Proxy")

@poc_fastapi_app.post("/v1/chat/completions")
async def poc_chat_completions(request: Request):
    logger.info("[FastAPI PoC Endpoint] Received request.")
    try:
        data = await request.json()
        logger.info(f"[FastAPI PoC Endpoint] Request data: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        logger.error("[FastAPI PoC Endpoint] Invalid JSON received.")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    messages = data.get("messages", [])
    user_message_content = ""
    system_message_content = "You are a helpful assistant." # Default system prompt

    for m in messages:
        if m.get("role") == "user":
            user_message_content = m.get("content", "")
        elif m.get("role") == "system":
            system_message_content = m.get("content", "") # Override default if provided
    
    if not user_message_content:
        logger.warning("[FastAPI PoC Endpoint] No user message found in request.")
        raise HTTPException(status_code=400, detail="No user message provided.")

    # Execute the Claude CLI
    claude_response_text = execute_claude_cli_for_poc(
        prompt=user_message_content,
        system_prompt_content=system_message_content,
        target_dir=Path(POC_TARGET_DIR), # Use defined PoC target directory
        claude_exe_path=Path(CLAUDE_CLI_PATH)
    )

    if claude_response_text is None:
        logger.error("[FastAPI PoC Endpoint] Failed to get response from Claude CLI.")
        raise HTTPException(status_code=500, detail="Failed to get response from Claude CLI")

    # Construct OpenAI-like response
    response_payload = {
        "id": f"poc-claude-{os.urandom(8).hex()}",
        "object": "chat.completion",
        "created": int(time.time()), # Using java.time for timestamp
        "model": "poc/claude-cli-default", # Label for the PoC
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": claude_response_text
            },
            "finish_reason": "stop"
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0} # Dummy usage
    }
    logger.success("[FastAPI PoC Endpoint] Sending response back to client.")
    return JSONResponse(content=response_payload)

# --- PoC Client Function ---
async def run_poc_client_call():
    await asyncio.sleep(2) # Give server a moment to start (crude, but simple for PoC)
    logger.info(f"🚀 [PoC Client] Attempting to call PoC FastAPI server at {FASTAPI_POC_ENDPOINT_URL}")

    client_payload = {
        "model": "max/poc-test", 
        "messages": [
            {"role": "system", "content": "You are Claude Max, a very friendly AI."},
            {"role": "user", "content": "Hi there! What's your name?"}
        ]
    }
    logger.info(f"📦 [PoC Client] Sending payload: {json.dumps(client_payload, indent=2)}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(FASTAPI_POC_ENDPOINT_URL, json=client_payload, timeout=120.0)
        
        logger.info(f"🚦 [PoC Client] Server Response Status Code: {response.status_code}")
        response.raise_for_status()
        response_data = response.json()
        logger.success("🎉 [PoC Client] Successfully received JSON response from PoC server!")
        
        if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
            assistant_message = response_data["choices"][0].get("message", {}).get("content", "")
            print("\n" + "="*30)
            print(f"💬 Claude (via PoC Server) says: '{assistant_message}'")
            print("="*30 + "\n")
        else:
            logger.warning(f"⚠️ [PoC Client] Response structure might be unexpected: {json.dumps(response_data, indent=2)}")

    except Exception as e:
        logger.error(f"💥 [PoC Client] An error occurred: {e}")
        import traceback
        traceback.print_exc()

# --- Main Orchestrator for Self-Contained PoC ---
async def main_self_contained_poc():
    # This setup is a bit tricky for a single script.
    # Ideally, you run the server, then run the client.
    # For a fully automated single script, we can try to run uvicorn programmatically.
    
    config = uvicorn.Config(poc_fastapi_app, host=POC_SERVER_HOST, port=POC_SERVER_PORT, log_level="info")
    server = uvicorn.Server(config)
    
    logger.info("Starting PoC FastAPI server programmatically...")
    # Run the server in a separate task so it doesn't block
    server_task = asyncio.create_task(server.serve())

    # Give the server a moment to start up
    await asyncio.sleep(2) 

    # Now run the client call
    await run_poc_client_call()

    # Stop the server (optional, or let it run until script ends)
    logger.info("PoC client call finished. Attempting to stop server...")
    # server.should_exit = True # This is one way to signal uvicorn to stop
    # await server_task # Wait for server to clean up

    # Forcing a more immediate stop for a script might be tricky with programmatic uvicorn.
    # Often, you'd run the server externally or use a different method for in-process testing.
    # For this PoC, we might just let the script end, which will stop the server task.
    # Or, simply instruct the user to Ctrl+C the script after client call.

    # A cleaner way to stop for a script:
    if server.started:
        server.should_exit = True
        # Wait for the server task to complete, or it might get cancelled abruptly
        # when main_self_contained_poc finishes.
        # We need to allow the server loop to process the should_exit.
        # This can be tricky to get right without proper signal handling or more complex async management.
        # For a simple PoC, after the client call, the server_task might just get cancelled when the script ends.
        # Let's try to await it with a timeout.
        try:
            await asyncio.wait_for(server_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Server shutdown timed out.")
        except asyncio.CancelledError:
             logger.info("Server task was cancelled.") # Expected if main exits
    logger.info("PoC script finished.")


if __name__ == "__main__":
    # Ensure the CLAUDE_CLI_PATH is correct and executable
    if not Path(CLAUDE_CLI_PATH).is_file():
        logger.error(f"CRITICAL: Claude CLI not found at '{CLAUDE_CLI_PATH}'. Please set the correct path.")
        exit(1)
    
    logger.info(f"Claude CLI path set to: {CLAUDE_CLI_PATH}")
    logger.info(f"Claude CLI will be executed in: {POC_TARGET_DIR}")

    # For programmatic uvicorn, it's better if it's the main entry point.
    # The following `asyncio.run(main_self_contained_poc())` might have issues if uvicorn
    # tries to manage its own loop in certain ways.
    # A more robust way for a single-file PoC like this is often:
    # 1. Start server (uvicorn command in one terminal)
    # 2. Run client (python this_script.py --client-only in another terminal)

    # However, let's try the programmatic approach first for self-containment.
    try:
        asyncio.run(main_self_contained_poc())
    except KeyboardInterrupt:
        logger.info("PoC interrupted by user.")
    except Exception as e:
        logger.error(f"Main PoC runner encountered an error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Exiting PoC.")