"""
Polling Manager for Long-Running LLM Calls

Implements async polling pattern with SQLite persistence for handling
slow Claude agent responses without timeouts.

Based on patterns from claude-code-mcp project.
"""

import asyncio
import json
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable

from loguru import logger


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskData:
    """Task data structure."""
    task_id: str
    status: TaskStatus
    llm_config: Dict[str, Any]
    start_time: str
    end_time: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: int = 0
    validation_attempts: int = 0
    last_update: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskData':
        """Create from dictionary."""
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class PollingDatabase:
    """SQLite database for task persistence."""
    
    def __init__(self, db_path: Union[str, Path] = "claude_polling.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    llm_config TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    result TEXT,
                    error TEXT,
                    progress INTEGER DEFAULT 0,
                    validation_attempts INTEGER DEFAULT 0,
                    last_update TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for status queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_task_status 
                ON tasks(status)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=30.0,
            isolation_level=None  # Auto-commit mode
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_task(self, task_data: TaskData) -> None:
        """Create a new task."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO tasks (
                    task_id, status, llm_config, start_time,
                    end_time, result, error, progress,
                    validation_attempts, last_update
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task_data.task_id,
                task_data.status.value,
                json.dumps(task_data.llm_config),
                task_data.start_time,
                task_data.end_time,
                json.dumps(task_data.result) if task_data.result else None,
                task_data.error,
                task_data.progress,
                task_data.validation_attempts,
                task_data.last_update
            ))
    
    def update_task(self, task_id: str, **updates) -> None:
        """Update task fields."""
        # Convert status enum to string if present
        if 'status' in updates and isinstance(updates['status'], TaskStatus):
            updates['status'] = updates['status'].value
        
        # Serialize complex fields
        if 'result' in updates and updates['result'] is not None:
            updates['result'] = json.dumps(updates['result'])
        if 'llm_config' in updates:
            updates['llm_config'] = json.dumps(updates['llm_config'])
        
        # Add timestamp
        updates['updated_at'] = datetime.utcnow().isoformat()
        updates['last_update'] = updates['updated_at']
        
        # Build query
        fields = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [task_id]
        
        with self._get_connection() as conn:
            conn.execute(
                f"UPDATE tasks SET {fields} WHERE task_id = ?",
                values
            )
    
    def get_task(self, task_id: str) -> Optional[TaskData]:
        """Get task by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?",
                (task_id,)
            ).fetchone()
            
            if row:
                data = dict(row)
                # Deserialize JSON fields
                data['llm_config'] = json.loads(data['llm_config'])
                if data['result']:
                    data['result'] = json.loads(data['result'])
                # Remove database-specific fields
                data.pop('created_at', None)
                data.pop('updated_at', None)
                return TaskData.from_dict(data)
        
        return None
    
    def get_active_tasks(self) -> List[TaskData]:
        """Get all active (pending/running) tasks."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tasks 
                WHERE status IN (?, ?)
                ORDER BY created_at DESC
            """, (TaskStatus.PENDING.value, TaskStatus.RUNNING.value)).fetchall()
            
            tasks = []
            for row in rows:
                data = dict(row)
                data['llm_config'] = json.loads(data['llm_config'])
                if data['result']:
                    data['result'] = json.loads(data['result'])
                data.pop('created_at', None)
                data.pop('updated_at', None)
                tasks.append(TaskData.from_dict(data))
            
            return tasks
    
    def cleanup_old_tasks(self, days: int = 7) -> int:
        """Remove tasks older than specified days."""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM tasks 
                WHERE created_at < ? 
                AND status IN (?, ?, ?)
            """, (cutoff, TaskStatus.COMPLETED.value, 
                  TaskStatus.FAILED.value, TaskStatus.TIMEOUT.value))
            
            return cursor.rowcount


class PollingManager:
    """
    Manages polling for long-running LLM calls.
    
    Implements the pattern from claude-code-mcp where tasks run in
    background threads and status is tracked in persistent storage.
    """
    
    def __init__(self, db_path: Union[str, Path] = "claude_polling.db"):
        self.db = PollingDatabase(db_path)
        self.active_tasks: Dict[str, TaskData] = {}
        self._executor_func: Optional[Callable] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
    def set_executor(self, executor_func: Callable):
        """Set the LLM call executor function."""
        self._executor_func = executor_func
    
    async def submit_task(self, llm_config: Dict[str, Any]) -> str:
        """
        Submit a new LLM task for background execution.
        
        Returns task_id for polling.
        """
        # Generate task ID
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        
        # Create task data
        task_data = TaskData(
            task_id=task_id,
            status=TaskStatus.PENDING,
            llm_config=llm_config,
            start_time=datetime.utcnow().isoformat()
        )
        
        # Save to database
        self.db.create_task(task_data)
        
        # Add to active tasks
        self.active_tasks[task_id] = task_data
        
        # Start background execution
        self._start_background_execution(task_id, llm_config)
        
        logger.info(f"Submitted task {task_id} for background execution")
        
        return task_id
    
    def _start_background_execution(self, task_id: str, llm_config: Dict[str, Any]):
        """Start task execution in background thread."""
        if not self._executor_func:
            raise RuntimeError("Executor function not set")
        
        def run_async():
            """Run async task in new event loop."""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    self._execute_task(task_id, llm_config)
                )
            finally:
                loop.close()
        
        # Start in background thread
        thread = threading.Thread(
            target=run_async,
            name=f"llm_task_{task_id}",
            daemon=True
        )
        thread.start()
        
        logger.debug(f"Started background thread for task {task_id}")
    
    async def _execute_task(self, task_id: str, llm_config: Dict[str, Any]):
        """Execute the LLM task and update status."""
        try:
            # Update status to running
            self._update_task_status(task_id, TaskStatus.RUNNING, progress=10)
            
            # Add task_id to config for tracking
            llm_config['_task_id'] = task_id
            
            # Execute LLM call
            logger.debug(f"Executing LLM call for task {task_id}")
            
            # Add progress callback if validation is involved
            if 'validation' in llm_config:
                original_validation = llm_config.get('validation', [])
                llm_config['_progress_callback'] = lambda p: self._update_progress(task_id, p)
            
            result = await self._executor_func(llm_config)
            
            # Update with result
            self._update_task_status(
                task_id, 
                TaskStatus.COMPLETED,
                result=result,
                end_time=datetime.utcnow().isoformat(),
                progress=100
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self._update_task_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e),
                end_time=datetime.utcnow().isoformat()
            )
        finally:
            # Remove from active tasks after a delay
            await asyncio.sleep(5)
            self.active_tasks.pop(task_id, None)
    
    def _update_task_status(self, task_id: str, status: TaskStatus, **kwargs):
        """Update task status in memory and database."""
        # Update in memory
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = status
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
        
        # Update in database
        self.db.update_task(task_id, status=status, **kwargs)
        
        logger.debug(f"Updated task {task_id} status to {status}")
    
    def _update_progress(self, task_id: str, progress: int):
        """Update task progress."""
        self._update_task_status(task_id, TaskStatus.RUNNING, progress=progress)
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current task status."""
        # Check active tasks first
        if task_id in self.active_tasks:
            return self.active_tasks[task_id].to_dict()
        
        # Check database
        task = self.db.get_task(task_id)
        if task:
            return task.to_dict()
        
        return None
    
    async def wait_for_completion(
        self, 
        task_id: str, 
        timeout: float = 300.0,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """
        Wait for task completion with polling.
        
        Args:
            task_id: Task ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds
            
        Returns:
            Task result
            
        Raises:
            TimeoutError: If task doesn't complete within timeout
        """
        start_time = time.time()
        
        while True:
            # Check status
            status = await self.get_task_status(task_id)
            
            if not status:
                raise ValueError(f"Task {task_id} not found")
            
            # Check if completed
            if status['status'] in [TaskStatus.COMPLETED, TaskStatus.FAILED, 
                                   TaskStatus.TIMEOUT, TaskStatus.CANCELLED]:
                if status['status'] == TaskStatus.COMPLETED:
                    return status.get('result', {})
                else:
                    error_msg = status.get('error', f"Task {status['status']}")
                    raise RuntimeError(f"Task failed: {error_msg}")
            
            # Check timeout
            if time.time() - start_time > timeout:
                self._update_task_status(task_id, TaskStatus.TIMEOUT)
                raise TimeoutError(f"Task {task_id} timed out after {timeout}s")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        status = await self.get_task_status(task_id)
        
        if status and status['status'] in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            self._update_task_status(task_id, TaskStatus.CANCELLED)
            return True
        
        return False
    
    async def start_cleanup_job(self, interval: int = 3600):
        """Start periodic cleanup of old tasks."""
        async def cleanup_loop():
            while True:
                try:
                    count = self.db.cleanup_old_tasks()
                    if count > 0:
                        logger.info(f"Cleaned up {count} old tasks")
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                
                await asyncio.sleep(interval)
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())
    
    async def shutdown(self):
        """Shutdown polling manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cancel any active tasks
        for task_id in list(self.active_tasks.keys()):
            await self.cancel_task(task_id)
        
        logger.info("Polling manager shut down")


# Global instance
_polling_manager: Optional[PollingManager] = None


def get_polling_manager() -> PollingManager:
    """Get global polling manager instance."""
    global _polling_manager
    if _polling_manager is None:
        _polling_manager = PollingManager()
    return _polling_manager