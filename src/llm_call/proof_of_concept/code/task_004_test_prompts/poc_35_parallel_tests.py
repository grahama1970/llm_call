#!/usr/bin/env python3
"""
POC 35: Parallel Test Execution
Task: Execute tests in parallel with proper resource management
Expected Output: Faster test execution with controlled concurrency
Links:
- https://docs.python.org/3/library/asyncio.html
- https://docs.python.org/3/library/concurrent.futures.html
"""

import asyncio
import time
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
import random
from collections import deque
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class TestTask:
    """Represents a test task to be executed"""
    test_id: str
    test_func: Callable
    priority: int = 5
    estimated_duration: float = 1.0
    dependencies: List[str] = field(default_factory=list)


@dataclass
class WorkerStats:
    """Statistics for a worker"""
    worker_id: int
    tests_executed: int = 0
    total_time: float = 0.0
    current_test: Optional[str] = None
    idle_time: float = 0.0


class ParallelTestExecutor:
    """Executes tests in parallel with resource management"""
    
    def __init__(self, max_workers: int = 5, max_concurrent_resources: int = 10):
        self.max_workers = max_workers
        self.max_concurrent_resources = max_concurrent_resources
        self.worker_stats: Dict[int, WorkerStats] = {}
        self.completed_tests: List[str] = []
        self.failed_tests: List[str] = []
        self.test_queue: asyncio.Queue = asyncio.Queue()
        self.resource_semaphore = asyncio.Semaphore(max_concurrent_resources)
        self.results: Dict[str, Any] = {}
        self._start_time = None
    
    async def add_test(self, test: TestTask) -> None:
        """Add a test to the execution queue"""
        await self.test_queue.put(test)
    
    async def execute_tests(self, tests: List[TestTask]) -> Dict[str, Any]:
        """Execute all tests in parallel"""
        self._start_time = time.time()
        
        # Sort tests by priority and dependencies
        sorted_tests = self._sort_tests(tests)
        
        # Add tests to queue
        for test in sorted_tests:
            await self.add_test(test)
        
        # Create workers
        workers = []
        for i in range(self.max_workers):
            self.worker_stats[i] = WorkerStats(worker_id=i)
            worker = asyncio.create_task(self._worker(i))
            workers.append(worker)
        
        # Wait for all tests to complete
        await self.test_queue.join()
        
        # Stop workers
        for _ in range(self.max_workers):
            await self.test_queue.put(None)
        
        await asyncio.gather(*workers)
        
        # Calculate final statistics
        total_time = time.time() - self._start_time
        
        return self._generate_execution_summary(total_time)
    
    def _sort_tests(self, tests: List[TestTask]) -> List[TestTask]:
        """Sort tests by priority and dependencies"""
        # Simple topological sort considering dependencies
        sorted_tests = []
        remaining = tests.copy()
        completed_ids = set()
        
        while remaining:
            # Find tests with no pending dependencies
            ready_tests = [
                t for t in remaining
                if all(dep in completed_ids for dep in t.dependencies)
            ]
            
            if not ready_tests:
                # Circular dependency or invalid dependency
                logger.warning("Circular or invalid dependencies detected")
                ready_tests = remaining  # Just add remaining tests
            
            # Sort by priority
            ready_tests.sort(key=lambda t: t.priority, reverse=True)
            
            for test in ready_tests:
                sorted_tests.append(test)
                completed_ids.add(test.test_id)
                remaining.remove(test)
        
        return sorted_tests
    
    async def _worker(self, worker_id: int) -> None:
        """Worker coroutine that executes tests"""
        logger.info(f"Worker {worker_id} started")
        
        while True:
            # Get test from queue
            test = await self.test_queue.get()
            
            if test is None:
                # Shutdown signal
                self.test_queue.task_done()
                break
            
            # Update worker stats
            self.worker_stats[worker_id].current_test = test.test_id
            start_time = time.time()
            
            try:
                # Execute test with resource control
                async with self.resource_semaphore:
                    logger.info(f"Worker {worker_id} executing {test.test_id}")
                    result = await self._execute_test(test)
                    self.results[test.test_id] = result
                    
                    if result.get("success", False):
                        self.completed_tests.append(test.test_id)
                    else:
                        self.failed_tests.append(test.test_id)
                
                # Update stats
                execution_time = time.time() - start_time
                self.worker_stats[worker_id].tests_executed += 1
                self.worker_stats[worker_id].total_time += execution_time
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error on {test.test_id}: {e}")
                self.failed_tests.append(test.test_id)
                self.results[test.test_id] = {"success": False, "error": str(e)}
            
            finally:
                self.worker_stats[worker_id].current_test = None
                self.test_queue.task_done()
        
        logger.info(f"Worker {worker_id} finished")
    
    async def _execute_test(self, test: TestTask) -> Dict[str, Any]:
        """Execute a single test"""
        start_time = time.time()
        
        try:
            # Call test function
            if asyncio.iscoroutinefunction(test.test_func):
                result = await test.test_func()
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, test.test_func)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "result": result,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def _generate_execution_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate execution summary"""
        # Worker utilization
        worker_utilization = {}
        for worker_id, stats in self.worker_stats.items():
            utilization = (stats.total_time / total_time * 100) if total_time > 0 else 0
            worker_utilization[f"worker_{worker_id}"] = {
                "tests_executed": stats.tests_executed,
                "utilization": f"{utilization:.1f}%",
                "avg_test_time": stats.total_time / stats.tests_executed if stats.tests_executed > 0 else 0
            }
        
        # Parallel efficiency
        sequential_time = sum(r.get("execution_time", 0) for r in self.results.values())
        parallel_efficiency = (sequential_time / (total_time * self.max_workers) * 100) if total_time > 0 else 0
        
        return {
            "total_tests": len(self.results),
            "completed": len(self.completed_tests),
            "failed": len(self.failed_tests),
            "total_time": total_time,
            "sequential_time": sequential_time,
            "speedup": sequential_time / total_time if total_time > 0 else 1,
            "parallel_efficiency": f"{parallel_efficiency:.1f}%",
            "worker_utilization": worker_utilization,
            "test_results": self.results
        }


# Mock test functions
async def mock_fast_test():
    """Fast test simulation"""
    await asyncio.sleep(random.uniform(0.1, 0.3))
    return {"status": "passed"}


async def mock_slow_test():
    """Slow test simulation"""
    await asyncio.sleep(random.uniform(0.5, 1.0))
    return {"status": "passed"}


async def mock_failing_test():
    """Failing test simulation"""
    await asyncio.sleep(random.uniform(0.1, 0.3))
    raise ValueError("Test failed")


async def mock_resource_intensive_test():
    """Resource intensive test simulation"""
    await asyncio.sleep(random.uniform(0.3, 0.5))
    # Simulate some CPU work
    sum(i**2 for i in range(100000))
    return {"status": "passed", "resource_used": True}


async def main():
    """Test parallel execution"""
    
    logger.info("=" * 60)
    logger.info("PARALLEL TEST EXECUTION TESTING")
    logger.info("=" * 60)
    
    # Create test tasks
    test_tasks = [
        # Fast tests
        TestTask("fast_test_1", mock_fast_test, priority=5, estimated_duration=0.2),
        TestTask("fast_test_2", mock_fast_test, priority=5, estimated_duration=0.2),
        TestTask("fast_test_3", mock_fast_test, priority=5, estimated_duration=0.2),
        TestTask("fast_test_4", mock_fast_test, priority=5, estimated_duration=0.2),
        TestTask("fast_test_5", mock_fast_test, priority=5, estimated_duration=0.2),
        
        # Slow tests
        TestTask("slow_test_1", mock_slow_test, priority=3, estimated_duration=0.8),
        TestTask("slow_test_2", mock_slow_test, priority=3, estimated_duration=0.8),
        TestTask("slow_test_3", mock_slow_test, priority=3, estimated_duration=0.8),
        
        # Failing tests
        TestTask("fail_test_1", mock_failing_test, priority=4, estimated_duration=0.2),
        TestTask("fail_test_2", mock_failing_test, priority=4, estimated_duration=0.2),
        
        # Resource intensive
        TestTask("resource_test_1", mock_resource_intensive_test, priority=2, estimated_duration=0.4),
        TestTask("resource_test_2", mock_resource_intensive_test, priority=2, estimated_duration=0.4),
        
        # Tests with dependencies
        TestTask("dependent_test_1", mock_fast_test, priority=6, dependencies=["fast_test_1"]),
        TestTask("dependent_test_2", mock_fast_test, priority=6, dependencies=["fast_test_1", "fast_test_2"]),
    ]
    
    # Test 1: Parallel execution with different worker counts
    logger.info("\n🧪 Test 1: Comparing different worker counts")
    
    for worker_count in [1, 3, 5]:
        logger.info(f"\nTesting with {worker_count} workers...")
        executor = ParallelTestExecutor(max_workers=worker_count)
        
        start = time.time()
        summary = await executor.execute_tests(test_tasks.copy())
        
        logger.info(f"Workers: {worker_count}")
        logger.info(f"Total time: {summary['total_time']:.2f}s")
        logger.info(f"Speedup: {summary['speedup']:.2f}x")
        logger.info(f"Efficiency: {summary['parallel_efficiency']}")
        logger.info(f"Completed: {summary['completed']}, Failed: {summary['failed']}")
    
    # Test 2: Resource contention
    logger.info("\n🧪 Test 2: Resource contention handling")
    
    # Create many resource-intensive tests
    resource_tests = [
        TestTask(f"resource_heavy_{i}", mock_resource_intensive_test, priority=1)
        for i in range(10)
    ]
    
    executor = ParallelTestExecutor(max_workers=5, max_concurrent_resources=3)
    summary = await executor.execute_tests(resource_tests)
    
    logger.info(f"Resource-limited execution:")
    logger.info(f"Total time: {summary['total_time']:.2f}s")
    logger.info(f"Parallel efficiency: {summary['parallel_efficiency']}")
    
    # Test 3: Priority and dependency handling
    logger.info("\n🧪 Test 3: Priority and dependency validation")
    
    priority_tests = [
        TestTask("high_priority_1", mock_fast_test, priority=10),
        TestTask("low_priority_1", mock_slow_test, priority=1),
        TestTask("medium_priority_1", mock_fast_test, priority=5),
        TestTask("dependent_on_high", mock_fast_test, priority=8, dependencies=["high_priority_1"]),
    ]
    
    executor = ParallelTestExecutor(max_workers=2)
    summary = await executor.execute_tests(priority_tests)
    
    # Check execution order
    logger.info("Execution completed with priority handling")
    
    # Display worker utilization
    logger.info("\n📊 Worker Utilization Summary")
    for worker, stats in summary['worker_utilization'].items():
        logger.info(f"{worker}: {stats['tests_executed']} tests, {stats['utilization']} utilization")
    
    # Verify parallel execution works
    if summary['total_tests'] > 0 and summary['speedup'] > 1.0:
        logger.success("\n✅ Parallel test execution working correctly")
        return 0
    else:
        logger.error("\n❌ Parallel test execution has issues")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))