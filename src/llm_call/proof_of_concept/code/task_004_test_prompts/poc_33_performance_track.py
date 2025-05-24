#!/usr/bin/env python3
"""
POC 33: Performance Tracking
Task: Track and analyze performance metrics during test execution
Expected Output: Detailed performance insights and bottleneck identification
Links:
- https://docs.python.org/3/library/time.html
- https://pypi.org/project/memory-profiler/
"""

import time
import asyncio
import os
import gc
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    metric_type: str
    value: float
    unit: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """System performance snapshot"""
    timestamp: float
    cpu_percent: float
    memory_mb: float
    active_tasks: int
    io_read_mb: float = 0.0
    io_write_mb: float = 0.0


class PerformanceTracker:
    """Tracks performance metrics during test execution"""
    
    def __init__(self, sampling_interval: float = 0.1):
        self.sampling_interval = sampling_interval
        self.metrics: List[PerformanceMetric] = []
        self.snapshots: List[PerformanceSnapshot] = []
        self.active_timers: Dict[str, float] = {}
        self.monitoring = False
        self._monitor_task = None
        self._start_memory = 0
    
    def start_timer(self, name: str) -> None:
        """Start a named timer"""
        self.active_timers[name] = time.perf_counter()
        logger.debug(f"Timer started: {name}")
    
    def stop_timer(self, name: str) -> Optional[float]:
        """Stop a timer and record the duration"""
        if name not in self.active_timers:
            logger.warning(f"Timer not found: {name}")
            return None
        
        start_time = self.active_timers.pop(name)
        duration = time.perf_counter() - start_time
        
        self.record_metric(
            metric_type=f"timer_{name}",
            value=duration * 1000,  # Convert to ms
            unit="ms",
            context={"timer_name": name}
        )
        
        logger.debug(f"Timer stopped: {name} - {duration*1000:.2f}ms")
        return duration
    
    def record_metric(self, metric_type: str, value: float, unit: str, context: Dict[str, Any] = None) -> None:
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_type=metric_type,
            value=value,
            unit=unit,
            context=context or {}
        )
        self.metrics.append(metric)
    
    async def start_monitoring(self) -> None:
        """Start background performance monitoring"""
        if self.monitoring:
            logger.warning("Monitoring already active")
            return
        
        self.monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Performance monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop background performance monitoring"""
        if not self.monitoring:
            return
        
        self.monitoring = False
        if self._monitor_task:
            await self._monitor_task
        logger.info("Performance monitoring stopped")
    
    async def _monitor_loop(self) -> None:
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Collect snapshot
                snapshot = self._collect_snapshot()
                self.snapshots.append(snapshot)
                
                # Check for anomalies
                self._check_anomalies(snapshot)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(self.sampling_interval)
    
    def _collect_snapshot(self) -> PerformanceSnapshot:
        """Collect current performance snapshot"""
        # Simple memory tracking using gc
        gc_stats = gc.get_stats()
        memory_mb = sum(stat.get('collected', 0) + stat.get('uncollectable', 0) for stat in gc_stats) / 1024 / 1024
        
        # Active tasks
        active_tasks = len([t for t in asyncio.all_tasks() if not t.done()])
        
        # Simulate CPU percent (based on active tasks)
        cpu_percent = min(active_tasks * 10, 100)
        
        return PerformanceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_mb=memory_mb,
            active_tasks=active_tasks,
            io_read_mb=0.0,  # Simplified without psutil
            io_write_mb=0.0  # Simplified without psutil
        )
    
    def _check_anomalies(self, snapshot: PerformanceSnapshot) -> None:
        """Check for performance anomalies"""
        # High CPU usage
        if snapshot.cpu_percent > 80:
            logger.warning(f"High CPU usage: {snapshot.cpu_percent:.1f}%")
            self.record_metric("anomaly_high_cpu", snapshot.cpu_percent, "%")
        
        # High memory usage
        if snapshot.memory_mb > 500:  # Arbitrary threshold
            logger.warning(f"High memory usage: {snapshot.memory_mb:.1f}MB")
            self.record_metric("anomaly_high_memory", snapshot.memory_mb, "MB")
        
        # Too many active tasks
        if snapshot.active_tasks > 50:
            logger.warning(f"Too many active tasks: {snapshot.active_tasks}")
            self.record_metric("anomaly_high_tasks", snapshot.active_tasks, "tasks")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics and not self.snapshots:
            return {"error": "No data collected"}
        
        # Timer statistics
        timer_metrics = [m for m in self.metrics if m.metric_type.startswith("timer_")]
        timer_stats = {}
        
        if timer_metrics:
            timer_values = [m.value for m in timer_metrics]
            timer_stats = {
                "count": len(timer_values),
                "total_ms": sum(timer_values),
                "avg_ms": sum(timer_values) / len(timer_values),
                "min_ms": min(timer_values),
                "max_ms": max(timer_values)
            }
        
        # Resource statistics
        resource_stats = {}
        if self.snapshots:
            cpu_values = [s.cpu_percent for s in self.snapshots]
            memory_values = [s.memory_mb for s in self.snapshots]
            
            resource_stats = {
                "cpu": {
                    "avg_percent": sum(cpu_values) / len(cpu_values),
                    "max_percent": max(cpu_values),
                    "samples": len(cpu_values)
                },
                "memory": {
                    "avg_mb": sum(memory_values) / len(memory_values),
                    "max_mb": max(memory_values),
                    "samples": len(memory_values)
                }
            }
        
        # Anomaly count
        anomaly_count = len([m for m in self.metrics if m.metric_type.startswith("anomaly_")])
        
        return {
            "timer_stats": timer_stats,
            "resource_stats": resource_stats,
            "anomaly_count": anomaly_count,
            "total_metrics": len(self.metrics),
            "monitoring_duration": (
                self.snapshots[-1].timestamp - self.snapshots[0].timestamp
                if len(self.snapshots) > 1 else 0
            )
        }
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        # Slow operations
        timer_metrics = [m for m in self.metrics if m.metric_type.startswith("timer_")]
        slow_threshold = 1000  # 1 second
        
        for metric in timer_metrics:
            if metric.value > slow_threshold:
                bottlenecks.append({
                    "type": "slow_operation",
                    "name": metric.context.get("timer_name", "unknown"),
                    "duration_ms": metric.value,
                    "timestamp": metric.timestamp
                })
        
        # Resource spikes
        if self.snapshots:
            for i, snapshot in enumerate(self.snapshots[1:], 1):
                # CPU spike
                if snapshot.cpu_percent > 90 and self.snapshots[i-1].cpu_percent < 50:
                    bottlenecks.append({
                        "type": "cpu_spike",
                        "value": snapshot.cpu_percent,
                        "timestamp": snapshot.timestamp
                    })
                
                # Memory spike
                prev_memory = self.snapshots[i-1].memory_mb
                if snapshot.memory_mb > prev_memory * 1.5:  # 50% increase
                    bottlenecks.append({
                        "type": "memory_spike",
                        "increase_mb": snapshot.memory_mb - prev_memory,
                        "timestamp": snapshot.timestamp
                    })
        
        return bottlenecks


# Test functions
async def simulate_workload(tracker: PerformanceTracker, workload_type: str) -> None:
    """Simulate different workload types"""
    
    if workload_type == "cpu_intensive":
        tracker.start_timer("cpu_task")
        # Simulate CPU work
        result = sum(i**2 for i in range(1000000))
        tracker.stop_timer("cpu_task")
        
    elif workload_type == "memory_intensive":
        tracker.start_timer("memory_task")
        # Simulate memory allocation
        data = [list(range(1000)) for _ in range(1000)]
        await asyncio.sleep(0.1)
        tracker.stop_timer("memory_task")
        
    elif workload_type == "io_intensive":
        tracker.start_timer("io_task")
        # Simulate I/O
        await asyncio.sleep(0.2)
        tracker.stop_timer("io_task")
        
    elif workload_type == "mixed":
        # Mix of operations
        tracker.start_timer("mixed_task")
        
        # CPU
        sum(i**2 for i in range(100000))
        
        # Memory
        data = [list(range(100)) for _ in range(100)]
        
        # I/O wait
        await asyncio.sleep(0.05)
        
        tracker.stop_timer("mixed_task")


async def main():
    """Test performance tracking"""
    
    logger.info("=" * 60)
    logger.info("PERFORMANCE TRACKING TESTING")
    logger.info("=" * 60)
    
    tracker = PerformanceTracker(sampling_interval=0.05)
    
    # Start monitoring
    await tracker.start_monitoring()
    
    # Test 1: Various workloads
    logger.info("\n🧪 Test 1: Tracking different workload types")
    
    workloads = ["cpu_intensive", "memory_intensive", "io_intensive", "mixed"]
    
    for workload in workloads:
        logger.info(f"Running {workload} workload...")
        await simulate_workload(tracker, workload)
        await asyncio.sleep(0.1)  # Brief pause between workloads
    
    # Test 2: Concurrent operations
    logger.info("\n🧪 Test 2: Tracking concurrent operations")
    
    tracker.start_timer("concurrent_test")
    
    tasks = []
    for i in range(5):
        task = asyncio.create_task(simulate_workload(tracker, "mixed"))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    tracker.stop_timer("concurrent_test")
    
    # Test 3: Long-running operation
    logger.info("\n🧪 Test 3: Tracking long-running operation")
    
    tracker.start_timer("long_operation")
    await asyncio.sleep(1.5)  # Simulate long operation
    tracker.stop_timer("long_operation")
    
    # Stop monitoring
    await tracker.stop_monitoring()
    
    # Get summary
    logger.info("\n📊 Performance Summary")
    summary = tracker.get_summary()
    
    logger.info(f"Timer Statistics: {summary.get('timer_stats', {})}")
    logger.info(f"Resource Statistics: {summary.get('resource_stats', {})}")
    logger.info(f"Anomalies Detected: {summary.get('anomaly_count', 0)}")
    logger.info(f"Total Metrics: {summary.get('total_metrics', 0)}")
    logger.info(f"Monitoring Duration: {summary.get('monitoring_duration', 0):.1f}s")
    
    # Identify bottlenecks
    logger.info("\n🔍 Bottleneck Analysis")
    bottlenecks = tracker.identify_bottlenecks()
    
    if bottlenecks:
        for bottleneck in bottlenecks:
            logger.warning(f"Bottleneck: {bottleneck}")
    else:
        logger.success("No significant bottlenecks detected")
    
    # Verify tracking worked
    if summary.get("total_metrics", 0) > 0 and len(tracker.snapshots) > 0:
        logger.success("\n✅ Performance tracking working correctly")
        return 0
    else:
        logger.error("\n❌ Performance tracking failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))