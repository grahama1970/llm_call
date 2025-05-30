"""
Async Polling Manager for Long-Running LLM Calls

This implementation uses pure async/await patterns instead of threads,
properly leveraging Python's asyncio capabilities.

Documentation:
- AsyncIO Tasks: https://docs.python.org/3/library/asyncio-task.html
- Concurrent execution: https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently

Sample usage:
    manager = AsyncPollingManager()
    
    # Submit a task (returns immediately)
    task_id = await manager.submit_task(llm_config)
    
    # Check status
    status = await manager.get_status(task_id)
    
    # Wait for completion (with timeout)
    result = await manager.wait_for_task(task_id, timeout=300)
"""

import asyncio
import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from contextlib import asynccontextmanager

from loguru import logger


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class TaskInfo:
    """Information about a polling task."""
    task_id: str
    status: TaskStatus
    llm_config: Dict[str, Any]
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskInfo':
        """Create from dictionary."""
        data['status'] = TaskStatus(data['status'])
        return cls(**data)


class AsyncPollingManager:
    """
    Async polling manager using pure asyncio patterns.
    
    Key improvements over thread-based approach:
    - Uses asyncio.create_task() instead of threads
    - Shares the same event loop for all tasks
    - Proper async context management
    - Built-in task cancellation support
    """
    
    def __init__(self, 
                 db_path: str = "llm_polling_tasks.db",
                 cleanup_after_hours: int = 24,
                 max_concurrent_tasks: int = 10):
        """Initialize the async polling manager."""
        self.db_path = db_path
        self.cleanup_after_hours = cleanup_after_hours
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Active asyncio tasks
        self._active_tasks: Dict[str, asyncio.Task] = {}
        
        # Task semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent_tasks)
        
        # Executor function (to be set by user)
        self._executor_func: Optional[Callable] = None
        
        # Initialize database
        self._init_db()
        
        # Cleanup task will be started when first task is submitted
        self._cleanup_task_started = False
        
    def _init_db(self):
        """Initialize SQLite database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                llm_config TEXT NOT NULL,
                created_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                result TEXT,
                error TEXT,
                progress TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def set_executor(self, executor_func: Callable):
        """Set the function to execute LLM calls."""
        self._executor_func = executor_func
        
    async def submit_task(self, llm_config: Dict[str, Any]) -> str:
        """
        Submit a new task for execution.
        
        Returns task_id immediately while task runs in background.
        """
        # Start cleanup task on first submission
        if not self._cleanup_task_started:
            asyncio.create_task(self._periodic_cleanup())
            self._cleanup_task_started = True
            
        task_id = str(uuid.uuid4())
        
        # Create task info
        task_info = TaskInfo(
            task_id=task_id,
            status=TaskStatus.PENDING,
            llm_config=llm_config,
            created_at=time.time()
        )
        
        # Store in database
        self._save_task(task_info)
        
        # Create asyncio task
        task = asyncio.create_task(
            self._execute_with_semaphore(task_id, llm_config)
        )
        
        # Store reference
        self._active_tasks[task_id] = task
        
        # Add cleanup callback
        task.add_done_callback(
            lambda t: self._active_tasks.pop(task_id, None)
        )
        
        logger.info(f"Submitted task {task_id}")
        return task_id
        
    async def _execute_with_semaphore(self, task_id: str, llm_config: Dict[str, Any]):
        """Execute task with semaphore for concurrency control."""
        async with self._semaphore:
            await self._execute_task(task_id, llm_config)
            
    async def _execute_task(self, task_id: str, llm_config: Dict[str, Any]):
        """Execute the actual LLM call."""
        if not self._executor_func:
            raise RuntimeError("Executor function not set")
            
        # Update status to running
        await self._update_status(task_id, TaskStatus.RUNNING, started_at=time.time())
        
        try:
            # Execute the LLM call
            result = await self._executor_func(llm_config)
            
            # Update status to completed
            await self._update_status(
                task_id, 
                TaskStatus.COMPLETED,
                completed_at=time.time(),
                result=result
            )
            
            logger.info(f"Task {task_id} completed successfully")
            
        except asyncio.CancelledError:
            # Handle cancellation
            await self._update_status(
                task_id,
                TaskStatus.CANCELLED,
                completed_at=time.time(),
                error="Task cancelled"
            )
            raise
            
        except Exception as e:
            # Handle errors
            await self._update_status(
                task_id,
                TaskStatus.FAILED,
                completed_at=time.time(),
                error=str(e)
            )
            logger.error(f"Task {task_id} failed: {e}")
            
    async def get_status(self, task_id: str) -> Optional[TaskInfo]:
        """Get current task status."""
        return await asyncio.to_thread(self._load_task, task_id)
        
    async def wait_for_task(self, 
                          task_id: str, 
                          timeout: Optional[float] = None,
                          poll_interval: float = 0.5) -> Dict[str, Any]:
        """
        Wait for task completion with optional timeout.
        
        Uses async polling instead of blocking.
        """
        start_time = time.time()
        
        while True:
            task_info = await self.get_status(task_id)
            
            if not task_info:
                raise ValueError(f"Task {task_id} not found")
                
            if task_info.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, 
                                  TaskStatus.TIMEOUT, TaskStatus.CANCELLED]:
                if task_info.status == TaskStatus.COMPLETED:
                    return task_info.result
                else:
                    raise RuntimeError(f"Task {task_id} {task_info.status.value}: {task_info.error}")
                    
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                await self._update_status(
                    task_id,
                    TaskStatus.TIMEOUT,
                    completed_at=time.time(),
                    error=f"Timeout after {timeout}s"
                )
                raise TimeoutError(f"Task {task_id} timed out after {timeout}s")
                
            # Async sleep
            await asyncio.sleep(poll_interval)
            
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        task = self._active_tasks.get(task_id)
        
        if task and not task.done():
            task.cancel()
            logger.info(f"Cancelled task {task_id}")
            return True
            
        return False
        
    async def get_active_tasks(self) -> List[TaskInfo]:
        """Get all active tasks."""
        return await asyncio.to_thread(self._get_active_tasks_sync)
        
    def _get_active_tasks_sync(self) -> List[TaskInfo]:
        """Synchronous version for thread execution."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM tasks WHERE status IN (?, ?)",
            (TaskStatus.PENDING.value, TaskStatus.RUNNING.value)
        )
        
        tasks = []
        for row in cursor.fetchall():
            task_data = {
                'task_id': row[0],
                'status': row[1],
                'llm_config': json.loads(row[2]),
                'created_at': row[3],
                'started_at': row[4],
                'completed_at': row[5],
                'result': json.loads(row[6]) if row[6] else None,
                'error': row[7],
                'progress': json.loads(row[8]) if row[8] else None
            }
            tasks.append(TaskInfo.from_dict(task_data))
            
        conn.close()
        return tasks
        
    async def _update_status(self, task_id: str, status: TaskStatus, **kwargs):
        """Update task status in database."""
        await asyncio.to_thread(self._update_status_sync, task_id, status, **kwargs)
        
    def _update_status_sync(self, task_id: str, status: TaskStatus, **kwargs):
        """Synchronous status update."""
        conn = sqlite3.connect(self.db_path)
        
        # Build update query
        updates = ['status = ?']
        values = [status.value]
        
        for key, value in kwargs.items():
            if key == 'result' or key == 'progress':
                updates.append(f'{key} = ?')
                values.append(json.dumps(value, default=str))
            else:
                updates.append(f'{key} = ?')
                values.append(value)
                
        values.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?"
        conn.execute(query, values)
        conn.commit()
        conn.close()
        
    def _save_task(self, task_info: TaskInfo):
        """Save task to database."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            '''INSERT INTO tasks 
            (task_id, status, llm_config, created_at, started_at, 
             completed_at, result, error, progress)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                task_info.task_id,
                task_info.status.value,
                json.dumps(task_info.llm_config),
                task_info.created_at,
                task_info.started_at,
                task_info.completed_at,
                json.dumps(task_info.result, default=str) if task_info.result else None,
                task_info.error,
                json.dumps(task_info.progress, default=str) if task_info.progress else None
            )
        )
        conn.commit()
        conn.close()
        
    def _load_task(self, task_id: str) -> Optional[TaskInfo]:
        """Load task from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        task_data = {
            'task_id': row[0],
            'status': row[1],
            'llm_config': json.loads(row[2]),
            'created_at': row[3],
            'started_at': row[4],
            'completed_at': row[5],
            'result': json.loads(row[6]) if row[6] else None,
            'error': row[7],
            'progress': json.loads(row[8]) if row[8] else None
        }
        
        return TaskInfo.from_dict(task_data)
        
    async def _periodic_cleanup(self):
        """Periodically clean up old tasks."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                
                cutoff = time.time() - (self.cleanup_after_hours * 3600)
                
                await asyncio.to_thread(self._cleanup_old_tasks, cutoff)
                
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                
    def _cleanup_old_tasks(self, cutoff: float):
        """Clean up tasks older than cutoff."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "DELETE FROM tasks WHERE completed_at < ? AND status IN (?, ?, ?, ?)",
            (cutoff, TaskStatus.COMPLETED.value, TaskStatus.FAILED.value,
             TaskStatus.TIMEOUT.value, TaskStatus.CANCELLED.value)
        )
        deleted = conn.total_changes
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old tasks")


# Validation test
if __name__ == "__main__":
    async def test_async_polling():
        """Test the async polling manager."""
        from llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc import llm_call
        
        # Create manager
        manager = AsyncPollingManager()
        
        # Set executor
        manager.set_executor(llm_call)
        
        # Test config
        test_config = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }
        
        # Submit task
        task_id = await manager.submit_task(test_config)
        print(f"Submitted task: {task_id}")
        
        # Check status
        status = await manager.get_status(task_id)
        print(f"Initial status: {status.status.value}")
        
        # Wait for completion
        try:
            result = await manager.wait_for_task(task_id, timeout=30)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
            
        # Check final status
        final_status = await manager.get_status(task_id)
        print(f"Final status: {final_status.status.value}")
        
        # List active tasks
        active = await manager.get_active_tasks()
        print(f"Active tasks: {len(active)}")
        
    # Run test
    asyncio.run(test_async_polling())
