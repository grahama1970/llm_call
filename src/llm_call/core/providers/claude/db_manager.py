"""
Module: db_manager.py
Description: Functions for db manager operations

External Dependencies:
- sqlite3: [Documentation URL]
- loguru: [Documentation URL]
- : [Documentation URL]
- claude_comms: [Documentation URL]

Sample Input:
>>> # Add specific examples based on module functionality

Expected Output:
>>> # Add expected output examples

Example Usage:
>>> # Add usage examples
"""

# src/claude_comms/inter_module_communicator/core/db_manager.py
"""
Core database management functions for handling task progress and details
in an SQLite database.
"""
import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict, Any, Union, Tuple
from loguru import logger

from . import config # For default DB path if needed, though usually passed in

def create_database(db_path: Path, progress_id_for_log: Optional[str] = "DB_INIT") -> sqlite3.Connection:
    """
    Creates or connects to an SQLite database and ensures the 'progress' table exists
    with the required schema.

    Args:
        db_path: Path object for the SQLite database file.
        progress_id_for_log: An identifier for logging context.

    Returns:
        A sqlite3.Connection object.
    """
    with logger.contextualize(progress_id=progress_id_for_log):
        logger.debug(f"Ensuring database exists at {db_path}")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        # Schema includes all contextual information for a task
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            content TEXT,
            chunk_count INTEGER DEFAULT 0,
            last_update REAL,
            created_at REAL,
            requester TEXT,
            responder_module TEXT,
            prompt TEXT,
            target_dir TEXT,
            system_prompt_file_path TEXT 
        )
        ''')
        conn.commit()
        logger.info(f"Database '{db_path}' is ready.")
        return conn

def insert_initial_task_record(
    conn: sqlite3.Connection, 
    progress_id: str, 
    prompt: str, 
    requester: str, 
    responder_module: str, 
    target_dir: Optional[Path], 
    system_prompt_file: Optional[Path]
):
    """
    Inserts an initial 'started' record for a new task.

    Args:
        conn: Active SQLite connection.
        progress_id: Unique ID for the task.
        prompt: The prompt for the task.
        requester: Identifier of the requester.
        responder_module: Identifier of the responder.
        target_dir: Target directory for Claude execution.
        system_prompt_file: Path to the system prompt file used.
    """
    with logger.contextualize(progress_id=progress_id):
        logger.debug(f"Inserting initial task record. Req: {requester}, Resp: {responder_module}")
        cursor = conn.cursor()
        now = time.time()
        try:
            cursor.execute('''
            INSERT INTO progress (id, status, content, chunk_count, last_update, created_at, 
                                  requester, responder_module, prompt, target_dir, system_prompt_file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (progress_id, "started", "", 0, now, now, 
                  requester, responder_module, prompt, 
                  str(target_dir) if target_dir else None, 
                  str(system_prompt_file) if system_prompt_file else None))
            conn.commit()
            logger.info("Initial task record inserted successfully.")
        except sqlite3.Error as e:
            logger.error(f"SQLite error inserting initial record: {e}")
            raise # Re-raise to be handled by caller

def update_task_progress(
    conn: sqlite3.Connection, 
    progress_id: str, 
    status: str, 
    content_to_set: Optional[str] = None, 
    new_chunk_received: bool = False
):
    """
    Updates the progress of an existing task.

    Args:
        conn: Active SQLite connection.
        progress_id: Unique ID of the task to update.
        status: The new status of the task.
        content_to_set: The full content to set (optional).
        new_chunk_received: Boolean indicating if a new chunk was received,
                             which will increment chunk_count.
    """
    with logger.contextualize(progress_id=progress_id):
        # logger.debug(f"Updating task: status='{status}', new_chunk={new_chunk_received}, content_update={content_to_set is not None}")
        cursor = conn.cursor()
        now = time.time()
        
        current_chunk_count = 0
        if new_chunk_received:
            cursor.execute('SELECT chunk_count FROM progress WHERE id = ?', (progress_id,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                current_chunk_count = row[0] + 1
            else: # Should not happen if record exists, but as a fallback
                current_chunk_count = 1 
                logger.warning(f"Could not retrieve current chunk_count for task {progress_id}, starting at 1.")
            
        sql_parts = ["status = ?", "last_update = ?"]
        params: list[Union[str, float, int, None]] = [status, now]

        if content_to_set is not None:
            sql_parts.append("content = ?")
            params.append(content_to_set)
        
        if new_chunk_received:
            sql_parts.append("chunk_count = ?")
            params.append(current_chunk_count)

        sql = f"UPDATE progress SET {', '.join(sql_parts)} WHERE id = ?"
        params.append(progress_id)
        
        try:
            cursor.execute(sql, tuple(params))
            conn.commit()
            # logger.debug("Task progress updated successfully in DB.")
        except sqlite3.Error as e:
            logger.error(f"SQLite error updating task progress: {e}. SQL: {sql}, Params: {params}")
            raise

def get_task_details(conn: sqlite3.Connection, progress_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves all details for a specific task.

    Args:
        conn: Active SQLite connection.
        progress_id: Unique ID of the task.

    Returns:
        A dictionary containing task details, or None if not found.
    """
    with logger.contextualize(progress_id=progress_id):
        # logger.debug(f"Fetching details for task.")
        cursor = conn.cursor()
        try:
            cursor.execute('''
            SELECT id, status, content, chunk_count, last_update, created_at, 
                   requester, responder_module, prompt, target_dir, system_prompt_file_path
            FROM progress WHERE id = ?''', (progress_id,))
            row = cursor.fetchone()
            if row:
                elapsed_time = 0
                if row[4] and row[5]: # last_update and created_at
                    elapsed_time = row[4] - row[5]
                
                return {
                    "id": row[0], "status": row[1], "content": row[2],
                    "chunk_count": row[3], "last_update": row[4], "created_at": row[5],
                    "requester": row[6], "responder_module": row[7],
                    "prompt": row[8], "target_dir": row[9], 
                    "system_prompt_file_path": row[10],
                    "elapsed_time": elapsed_time 
                }
            logger.warning(f"No record found for task ID {progress_id}.")
            return None
        except sqlite3.Error as e:
            logger.error(f"SQLite error fetching task details: {e}")
            raise

if __name__ == "__main__":
    # --- Validation Block ---
    print("Running validation for core/db_manager.py...")
    all_validation_failures = []
    total_tests = 0
    
    # Setup a temporary DB for testing
    test_db_path = Path("./temp_test_db_manager.db")
    if test_db_path.exists():
        test_db_path.unlink()

    test_progress_id = "val_db_" + str(uuid.uuid4())
    
    # Configure logging for validation
    # Note: In a real test suite, logging might be configured globally or per test.
    # For this standalone validation, we set it up simply.
    from claude_comms.inter_module_communicator.core.logging_utils import setup_logging # Relative import for standalone run
    # Assuming logging_utils.py is in the same directory or Python path is set up.
    # For direct execution: python -m claude_comms.inter_module_communicator.core.db_manager
    try:
        setup_logging(progress_id="DB_VALIDATION", console_level="DEBUG", file_level="DEBUG", log_file_dir_base=Path("."))
    except ImportError:
        logger.warning("Could not import logging_utils for enhanced validation logging. Using basic logger.")
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")


    # Test 1: Database Creation and Connection
    total_tests += 1
    logger.info("Test 1: Database Creation and Connection")
    conn_test: Optional[sqlite3.Connection] = None
    try:
        conn_test = create_database(test_db_path, test_progress_id)
        if not isinstance(conn_test, sqlite3.Connection):
            all_validation_failures.append("Test 1.1 FAILED: create_database did not return a Connection object.")
        else:
            logger.info("Test 1.1 PASSED: Database connection established.")
            # Check if table exists
            cursor = conn_test.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='progress';")
            if cursor.fetchone() is None:
                all_validation_failures.append("Test 1.2 FAILED: 'progress' table not created.")
            else:
                logger.info("Test 1.2 PASSED: 'progress' table exists.")
    except Exception as e:
        all_validation_failures.append(f"Test 1 FAILED: Unexpected exception during DB creation: {e}")
    finally:
        if conn_test:
            conn_test.close() # Close after this initial test

    # Re-open connection for subsequent tests
    if not all_validation_failures: # Only proceed if DB creation was okay
        conn_test = sqlite3.connect(str(test_db_path))


    # Test 2: Insert Initial Task Record
    total_tests += 1
    logger.info("\nTest 2: Insert Initial Task Record")
    if conn_test:
        try:
            sample_prompt = "Test prompt"
            sample_requester = "TestRequester"
            sample_responder = "TestResponder"
            sample_target_dir = Path("/tmp/test_target")
            sample_sys_prompt_file = Path("/tmp/test_sys.md")

            insert_initial_task_record(
                conn_test, test_progress_id, sample_prompt, sample_requester, 
                sample_responder, sample_target_dir, sample_sys_prompt_file
            )
            # Verify insertion
            cursor = conn_test.cursor()
            cursor.execute("SELECT * FROM progress WHERE id = ?", (test_progress_id,))
            row = cursor.fetchone()
            if row is None:
                all_validation_failures.append("Test 2.1 FAILED: Record not inserted.")
            elif row[1] != "started":
                 all_validation_failures.append(f"Test 2.2 FAILED: Initial status is '{row[1]}', expected 'started'.")
            elif row[6] != sample_requester or row[7] != sample_responder:
                 all_validation_failures.append(f"Test 2.3 FAILED: Requester/Responder mismatch.")
            else:
                logger.info("Test 2 PASSED: Initial record inserted and basic fields verified.")
        except Exception as e:
            all_validation_failures.append(f"Test 2 FAILED: Unexpected exception during record insertion: {e}")
    else:
        all_validation_failures.append("Test 2 SKIPPED: DB connection not available.")


    # Test 3: Update Task Progress
    total_tests += 1
    logger.info("\nTest 3: Update Task Progress")
    if conn_test:
        try:
            update_task_progress(conn_test, test_progress_id, "running", content_to_set="First chunk.", new_chunk_received=True)
            cursor = conn_test.cursor()
            cursor.execute("SELECT status, content, chunk_count FROM progress WHERE id = ?", (test_progress_id,))
            row = cursor.fetchone()
            if row is None:
                all_validation_failures.append("Test 3.1 FAILED: Record disappeared after update.")
            elif row[0] != "running":
                all_validation_failures.append(f"Test 3.2 FAILED: Status not updated to 'running'. Got '{row[0]}'")
            elif row[1] != "First chunk.":
                all_validation_failures.append(f"Test 3.3 FAILED: Content not updated. Got '{row[1]}'")
            elif row[2] != 1: # Chunk count should be 1
                all_validation_failures.append(f"Test 3.4 FAILED: Chunk count not incremented to 1. Got '{row[2]}'")
            else:
                logger.info("Test 3.A PASSED: First update (status, content, chunk_count) successful.")

            update_task_progress(conn_test, test_progress_id, "receiving_chunk", content_to_set="First chunk.Second chunk.", new_chunk_received=True)
            cursor.execute("SELECT status, content, chunk_count FROM progress WHERE id = ?", (test_progress_id,))
            row = cursor.fetchone()
            if row and row[2] == 2 and row[1] == "First chunk.Second chunk.":
                 logger.info("Test 3.B PASSED: Second update (content, chunk_count) successful.")
            else:
                all_validation_failures.append(f"Test 3.B FAILED: Second update incorrect. Status: {row[0] if row else 'N/A'}, Content: {row[1] if row else 'N/A'}, Chunks: {row[2] if row else 'N/A'}")

            update_task_progress(conn_test, test_progress_id, "complete") # Update status only
            cursor.execute("SELECT status, chunk_count FROM progress WHERE id = ?", (test_progress_id,))
            row = cursor.fetchone()
            if row and row[0] == "complete" and row[1] == 2: # Chunk count should remain 2
                 logger.info("Test 3.C PASSED: Status-only update successful, chunk_count preserved.")
            else:
                all_validation_failures.append(f"Test 3.C FAILED: Status-only update incorrect. Status: {row[0] if row else 'N/A'}, Chunks: {row[1] if row else 'N/A'}")

        except Exception as e:
            all_validation_failures.append(f"Test 3 FAILED: Unexpected exception during progress update: {e}")
    else:
        all_validation_failures.append("Test 3 SKIPPED: DB connection not available.")

    # Test 4: Get Task Details
    total_tests += 1
    logger.info("\nTest 4: Get Task Details")
    if conn_test:
        try:
            details = get_task_details(conn_test, test_progress_id)
            if details is None:
                all_validation_failures.append("Test 4.1 FAILED: get_task_details returned None for existing ID.")
            elif details.get("id") != test_progress_id or details.get("status") != "complete":
                all_validation_failures.append(f"Test 4.2 FAILED: Retrieved details mismatch. Got: {details}")
            elif details.get("chunk_count") != 2:
                 all_validation_failures.append(f"Test 4.3 FAILED: Retrieved chunk_count mismatch. Expected 2, Got: {details.get('chunk_count')}")
            elif details.get("requester") != "TestRequester":
                 all_validation_failures.append(f"Test 4.4 FAILED: Retrieved requester mismatch.")
            else:
                logger.info(f"Test 4 PASSED: get_task_details retrieved correct data: {details.get('status')}, Chunks: {details.get('chunk_count')}")
            
            non_existent_details = get_task_details(conn_test, "non_existent_id")
            if non_existent_details is not None:
                all_validation_failures.append("Test 4.5 FAILED: get_task_details returned data for non-existent ID.")
            else:
                logger.info("Test 4.5 PASSED: get_task_details returned None for non-existent ID.")

        except Exception as e:
            all_validation_failures.append(f"Test 4 FAILED: Unexpected exception: {e}")
    else:
        all_validation_failures.append("Test 4 SKIPPED: DB connection not available.")


    # Cleanup
    if conn_test:
        conn_test.close()
    if test_db_path.exists():
        try:
            test_db_path.unlink()
            logger.info(f"Cleaned up test database: {test_db_path}")
        except Exception as e:
            logger.error(f"Could not clean up test database {test_db_path}: {e}")


    # Final validation result
    if all_validation_failures:
        logger.error(f" VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for i, failure in enumerate(all_validation_failures):
            logger.error(f"  Failure {i+1}: {failure}")
        sys.exit(1)
    else:
        logger.info(f" VALIDATION PASSED - All {total_tests} tests produced expected results for db_manager.py.")
        logger.info("Module is validated and formal tests can now be written.")
        sys.exit(0)
