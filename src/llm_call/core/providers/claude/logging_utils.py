# src/claude_comms/inter_module_communicator/core/logging_utils.py
"""
Logging utilities for the Inter-Module Communicator, using Loguru.
"""
import sys
from pathlib import Path
from loguru import logger
from claude_comms.core import config # Import from local core package

def setup_logging(
    progress_id: str,
    console_level: str = config.DEFAULT_CONSOLE_LOG_LEVEL,
    file_level: str = config.DEFAULT_FILE_LOG_LEVEL,
    log_file_dir_base: Path = None, # Base directory for logs, e.g., where DB is
    log_dir_name: str = config.DEFAULT_LOG_DIR_NAME,
    log_file_name_prefix: str = "task"
):
    """
    Configures Loguru with console and file sinks.

    Args:
        progress_id: The unique ID for the current task, used for contextualizing file logs
                     and potentially in the log file name.
        console_level: Minimum log level for console output.
        file_level: Minimum log level for file output.
        log_file_dir_base: The base directory where the log_dir_name subdirectory will be created.
                           If None, defaults to current working directory.
        log_dir_name: Name of the subdirectory to store log files.
        log_file_name_prefix: Prefix for the log file name.
    """
    logger.remove()  # Remove any default or pre-existing handlers

    # Console Logger
    logger.add(
        sys.stderr,
        level=console_level.upper(),
        format=(
            "<cyan>{time:YYYY-MM-DD HH:mm:ss.SSS}</cyan> | "
            "<level>{level: <8}</level> | "
            # Contextual progress_id will be shown if set via logger.contextualize
            "<green>{extra[progress_id]}</green> | " 
            "<level>{message}</level>" # Simplified format for console progress
        ),
        colorize=True,
    )

    # File Logger
    if log_file_dir_base is None:
        log_file_dir_base = Path.cwd() # Default to current working directory
    
    log_directory = Path(log_file_dir_base) / log_dir_name
    log_directory.mkdir(parents=True, exist_ok=True)
    log_file_path = log_directory / f"{log_file_name_prefix}_{progress_id}.log"

    logger.add(
        log_file_path,
        level=file_level.upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[progress_id]} | "
            "{name}:{function}:{line} - {message}"
        ),
        rotation=config.LOG_ROTATION,
        retention=config.LOG_RETENTION,
        enqueue=True,  # For async logging, good for performance
        # Ensure progress_id is available in the 'extra' dict for the formatter
        # This is typically done using logger.contextualize elsewhere
    )
    
    # Initial message indicating where logs are stored
    # This message will go to both console and file if their levels permit
    logger.info(f"Logging initialized. Console level: {console_level.upper()}. File level: {file_level.upper()}.")
    logger.info(f"Detailed logs for task {progress_id} will be in: {log_file_path}")

if __name__ == "__main__":
    # Example of using the logging setup
    test_progress_id = "test_log_setup_123"
    
    # Simulate setting up logging for a task
    # In a real app, log_file_dir_base might be derived from db_path.parent
    setup_logging(progress_id=test_progress_id, console_level="INFO", file_level="DEBUG", log_file_dir_base=Path("."))

    # Use contextualize to ensure progress_id is available for the file log format
    with logger.contextualize(progress_id=test_progress_id):
        logger.debug("This is a debug message for the file log.")
        logger.info("This is an info message for console and file log.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        try:
            1 / 0
        except ZeroDivisionError:
            logger.exception("An exception occurred!")

    print(f"\nCheck for log file in ./task_logs/task_{test_progress_id}.log")
    print("Check console output for INFO, WARNING, ERROR, and EXCEPTION messages.")

