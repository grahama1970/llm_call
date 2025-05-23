# src/claude_comms/inter_module_communicator/core/config.py
"""
Core configuration settings for the Inter-Module Communicator.
"""
from pathlib import Path

# --- IMPORTANT: Update this path to your actual Claude CLI executable ---
# This can be overridden by a CLI argument in the final app.
DEFAULT_CLAUDE_PATH: Path = Path("/home/graham/.nvm/versions/node/v22.15.0/bin/claude")
# --- End Important Path ---

DEFAULT_DB_FILENAME: str = "inter_module_comm_tasks.db"
DEFAULT_LOG_DIR_NAME: str = "task_logs"

# Default simulation mode for core functions if not specified by CLI
# This is more for internal testing of core functions if needed.
# The CLI layer will have its own --simulation flag.
DEFAULT_CORE_SIMULATION_MODE: bool = False

# Default verbosity for Claude CLI subprocess if not specified by CLI's verbose flag
DEFAULT_CLAUDE_CLI_VERBOSE: bool = False

# Timeout for subprocess communication (e.g., process.communicate())
DEFAULT_SUBPROCESS_TIMEOUT: int = 120 # seconds, increased from 60

# Loguru settings (can be overridden by CLI layer)
DEFAULT_CONSOLE_LOG_LEVEL: str = "INFO"
DEFAULT_FILE_LOG_LEVEL: str = "DEBUG"
LOG_ROTATION: str = "10 MB"
LOG_RETENTION: str = "7 days"

"""
pyproject.toml changes
# pyproject.toml (Additions/Modifications)
# Ensure these dependencies are present in your [project.dependencies] section

# [project.dependencies]
# ... (existing dependencies) ...
# "typer[all]>=0.9.0", # For the CLI layer
# "loguru>=0.7.0,<0.8", # Already present, ensure version compatibility
# "typing-extensions>=4.0.0" # Often needed by Typer/Pydantic

# Add a new script entry point for the refactored CLI
# [project.scripts]
# ... (existing scripts) ...
# imc-cli = "claude_comms.inter_module_communicator.cli.app:app"
"""