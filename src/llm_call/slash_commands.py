"""
Module: slash_commands.py
Description: Slash command support for llm_call

External Dependencies:
- typing: https://docs.python.org/3/library/typing.html
"""

from typing import Dict, Callable, Optional, Any, List
import subprocess
import sys
import os
import json
import time
from pathlib import Path


class SlashCommandRegistry:
    """Registry for slash commands"""
    
    def __init__(self):
        self.commands: Dict[str, Dict[str, Any]] = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default slash commands"""
        self.register("/analyze-corpus", self._analyze_corpus, "Analyze a directory or corpus of files")
        self.register("/help", self._help, "Show available commands")
        self.register("/config", self._config, "Show current configuration")
        self.register("/models", self._models, "List available models")
        self.register("/claude-verify", self._claude_verify, "Launch background verification of code")
        self.register("/claude-poll", self._claude_poll, "Poll for status file completion")
    
    def register(self, command: str, handler: Callable, description: str = "") -> None:
        """Register a new slash command"""
        self.commands[command] = {
            "handler": handler,
            "description": description
        }
    
    def has_command(self, command: str) -> bool:
        """Check if a command exists"""
        return command in self.commands
    
    def execute(self, command: str, *args, **kwargs) -> Any:
        """Execute a slash command"""
        if command not in self.commands:
            return f"Unknown command: {command}"
        
        handler = self.commands[command]["handler"]
        return handler(*args, **kwargs)
    
    def list_commands(self) -> List[str]:
        """List all available commands"""
        return list(self.commands.keys())
    
    def _analyze_corpus(self, path: str, **kwargs) -> str:
        """Analyze a directory or corpus"""
        return f"Analyzing corpus at: {path}"
    
    def _help(self, **kwargs) -> str:
        """Show help for commands"""
        lines = ["Available commands:"]
        for cmd, info in self.commands.items():
            lines.append(f"  {cmd} - {info['description']}")
        return "\n".join(lines)
    
    def _config(self, **kwargs) -> str:
        """Show configuration"""
        from .core import get_config
        config = get_config
        return f"Current configuration: default_model={config.default_model}"
    
    def _models(self, **kwargs) -> str:
        """List available models"""
        from .api import get_available_providers
        providers = get_available_providers()
        return f"Available providers: {', '.join(providers[:10])}..."
    
    def _claude_verify(self, code_file: str = "simple_add.py", 
                      result_file: str = "add_results.txt",
                      status_file: str = "verification_status.json",
                      log_file: str = "task_execution.log", **kwargs) -> str:
        """Launch background verification of code"""
        verification_script = f'''
from loguru import logger
import subprocess, json, datetime, sys

code_file = "{code_file}"
result_file = "{result_file}"
status_file = "{status_file}"
log_file = "{log_file}"

logger.add(log_file, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
           format="{{time:YYYY-MM-DD HH:mm:ss.SSS}} | {{message}}")
logger.info("🔬 BACKGROUND CLAUDE VERIFICATION STARTED")
logger.info("-" * 80)

critique = ""
status = "fail"
stdout = ""
stderr = ""

# Analyze code quality
try:
    with open(code_file) as f:
        code = f.read()
    logger.info("[CODE_ANALYSIS] Reading {code_file}")
    logger.info("```python")
    logger.info(code)
    logger.info("```")
    if "def" in code and "add" in code:
        critique += "Function appears to be defined correctly. "
    else:
        critique += "Function definition may be missing or incorrect. "
except Exception as e:
    critique += f"Error reading code file: {{e}} "
    logger.error(f"[ERROR] Failed to read code file: {{e}}")

# Run the code and capture output
try:
    logger.info("[EXECUTION] Running python {code_file}")
    proc = subprocess.run(
        [sys.executable, code_file],
        capture_output=True, text=True, timeout=10
    )
    stdout = proc.stdout
    stderr = proc.stderr
    logger.info(f"[EXECUTION_OUTPUT]")
    logger.info(f"stdout: {{stdout.strip()}}")
    logger.info(f"stderr: {{stderr.strip()}}")
    logger.info(f"return_code: {{proc.returncode}}")
    if proc.returncode == 0:
        critique += "Code executed successfully. "
    else:
        critique += f"Code execution failed with return code {{proc.returncode}}. "
except Exception as e:
    stderr += f"Exception running code: {{e}}\\n"
    critique += "Exception during code execution. "
    logger.error(f"[ERROR] Exception during execution: {{e}}")

# Verify output file
try:
    with open(result_file) as f:
        result = f.read().strip()
    logger.info("[FILE_VERIFICATION] Reading {result_file}")
    logger.info("```")
    logger.info(result)
    logger.info("```")
    if result.isdigit() and int(result) == 5:
        critique += "Output result is correct. "
        status = "pass"
    else:
        critique += f"Output result is incorrect: {{result}}. "
except Exception as e:
    critique += f"Error reading result file: {{e}} "
    logger.error(f"[ERROR] Failed to read result file: {{e}}")

# Write verification status JSON
verification = {{
    "datetime": datetime.datetime.utcnow().isoformat() + "Z",
    "critique": critique.strip(),
    "status": status,
    "stdout": stdout.strip(),
    "stderr": stderr.strip()
}}
logger.info("[JSON_UPDATE] Writing final verification status")
logger.info("```json")
logger.info(json.dumps(verification, indent=2))
logger.info("```")

with open(status_file, "w") as f:
    json.dump(verification, f, indent=2)

logger.info(f"🔬 BACKGROUND VERIFICATION COMPLETE: {{status.upper()}}")
logger.info("=" * 80)
'''
        
        # Write verification script to temp file and run in background
        script_path = Path("verify_task.py")
        script_path.write_text(verification_script)
        
        # Launch in background
        subprocess.Popen([sys.executable, str(script_path)], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        return f"Background verification launched for {code_file}"
    
    def _claude_poll(self, status_file: str = "verification_status.json",
                    expected_status: str = "pass",
                    timeout: int = 600,
                    log_file: str = "task_execution.log", **kwargs) -> str:
        """Poll for status file completion"""
        polling_script = f'''
from loguru import logger
import json, time, datetime
from pathlib import Path

status_file = "{status_file}"
expected_status = "{expected_status}"
timeout = {timeout}
log_file = "{log_file}"

logger.add(log_file, rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
           format="{{time:YYYY-MM-DD HH:mm:ss.SSS}} | {{message}}")

start_time = time.time()
attempt = 0

while time.time() - start_time < timeout:
    attempt += 1
    logger.info(f"[POLL_ATTEMPT] #{{attempt}} at {{datetime.datetime.utcnow().isoformat()}}Z")
    
    if Path(status_file).exists():
        try:
            with open(status_file) as f:
                data = json.load(f)
            
            logger.info(f"[FILE_READ] {status_file}:")
            logger.info("```json")
            logger.info(json.dumps(data, indent=2))
            logger.info("```")
            
            current_status = data.get("status", "unknown")
            if current_status == expected_status:
                logger.info(f"[POLL_RESULT] Status: {{current_status}} (Expected status reached)")
                break
            else:
                logger.info(f"[POLL_RESULT] Status: {{current_status}} (Waiting for '{expected_status}')")
        except Exception as e:
            logger.info(f"[POLL_RESULT] Status: error ({{e}})")
    else:
        logger.info(f"[POLL_RESULT] Status: not_found (File does not exist yet)")
    
    time.sleep(2)

if time.time() - start_time >= timeout:
    logger.error(f"[POLL_TIMEOUT] Timeout reached after {{timeout}} seconds")
'''
        
        # Write and execute polling script
        script_path = Path("poll_task.py")
        script_path.write_text(polling_script)
        
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True)
        
        return f"Polling completed: {result.stdout}"


# Global registry instance
SLASH_COMMANDS = SlashCommandRegistry()