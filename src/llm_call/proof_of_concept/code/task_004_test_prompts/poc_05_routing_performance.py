#!/usr/bin/env python3
"""
POC-5: Performance benchmark for routing overhead

Purpose:
    Measures routing performance across different scenarios.
    Tests caching, parallel routing, and optimization strategies.

Links:
    - Python Performance: https://docs.python.org/3/library/timeit.html
    - Asyncio Performance: https://docs.python.org/3/library/asyncio-task.html

Sample Input:
    Various model configurations for performance testing

Expected Output:
    Performance metrics meeting <50ms routing decision target

Author: Task 004 Implementation
"""

import asyncio
import time
import statistics
from typing import Dict, Any, List, Tuple
from loguru import logger
import concurrent.futures
from functools import lru_cache

# Configure logger
logger.add("poc_05_routing_performance.log", rotation="10 MB")


class PerformanceMetrics:
    """Track performance metrics for routing operations."""
    
    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}
    
    def record(self, operation: str, duration_ms: float):
        """Record a performance measurement."""
        if operation not in self.measurements:
            self.measurements[operation] = []
        self.measurements[operation].append(duration_ms)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Get statistics for an operation."""
        if operation not in self.measurements:
            return {}
        
        values = self.measurements[operation]
        if not values:
            return {}
        
        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "p95": sorted(values)[int(len(values) * 0.95)] if values else 0,
            "p99": sorted(values)[int(len(values) * 0.99)] if values else 0,
        }
    
    def summary(self) -> str:
        """Generate a summary report."""
        lines = ["Performance Summary", "=" * 50]
        
        for operation, values in self.measurements.items():
            if values:
                stats = self.get_stats(operation)
                lines.append(f"\n{operation}:")
                lines.append(f"  Count: {stats['count']}")
                lines.append(f"  Mean: {stats['mean']:.3f}ms")
                lines.append(f"  Median: {stats['median']:.3f}ms")
                lines.append(f"  Min: {stats['min']:.3f}ms")
                lines.append(f"  Max: {stats['max']:.3f}ms")
                lines.append(f"  P95: {stats['p95']:.3f}ms")
                lines.append(f"  P99: {stats['p99']:.3f}ms")
        
        return "\n".join(lines)


# Global metrics tracker
metrics = PerformanceMetrics()


@lru_cache(maxsize=128)
def cached_route_decision(model: str) -> str:
    """Cached routing decision for performance."""
    # Simulate routing logic
    if model.startswith("max/") or model.startswith("claude/"):
        return "claude_proxy"
    elif "/" in model:
        provider = model.split("/")[0]
        return f"litellm_{provider}"
    else:
        return "litellm_default"


def route_with_timing(config: Dict[str, Any], use_cache: bool = False) -> Tuple[str, float]:
    """
    Route with performance timing.
    
    Args:
        config: Configuration to route
        use_cache: Whether to use cached routing
        
    Returns:
        Tuple of (route_decision, duration_ms)
    """
    start_time = time.perf_counter()
    
    model = config.get("model", "")
    
    if use_cache:
        route = cached_route_decision(model)
    else:
        # Direct routing logic
        if model.startswith("max/") or model.startswith("claude/"):
            route = "claude_proxy"
        elif "/" in model:
            provider = model.split("/")[0]
            route = f"litellm_{provider}"
        else:
            route = "litellm_default"
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    return route, duration_ms


async def async_route_with_timing(config: Dict[str, Any]) -> Tuple[str, float]:
    """Async version of routing for comparison."""
    start_time = time.perf_counter()
    
    # Simulate async operation
    await asyncio.sleep(0)  # Yield to event loop
    
    model = config.get("model", "")
    if model.startswith("max/") or model.startswith("claude/"):
        route = "claude_proxy"
    elif "/" in model:
        provider = model.split("/")[0]
        route = f"litellm_{provider}"
    else:
        route = "litellm_default"
    
    duration_ms = (time.perf_counter() - start_time) * 1000
    
    return route, duration_ms


def parallel_routing_test(configs: List[Dict[str, Any]], max_workers: int = 4) -> List[float]:
    """Test parallel routing performance."""
    times = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        start_time = time.perf_counter()
        
        futures = [
            executor.submit(route_with_timing, config, use_cache=True)
            for config in configs
        ]
        
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        total_time = (time.perf_counter() - start_time) * 1000
        times.append(total_time)
    
    return times


async def run_performance_tests():
    """Run comprehensive performance tests."""
    
    # Test configurations
    test_configs = [
        {"model": "max/claude-3", "messages": [{"role": "user", "content": "test"}]},
        {"model": "openai/gpt-4", "messages": [{"role": "user", "content": "test"}]},
        {"model": "vertex_ai/gemini", "messages": [{"role": "user", "content": "test"}]},
        {"model": "anthropic/claude", "messages": [{"role": "user", "content": "test"}]},
        {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "test"}]},
    ]
    
    logger.info("Starting performance tests...")
    
    # Test 1: Basic routing performance
    logger.info("\n1. Basic Routing Performance")
    for config in test_configs:
        for _ in range(100):
            route, duration = route_with_timing(config, use_cache=False)
            metrics.record("basic_routing", duration)
    
    # Test 2: Cached routing performance
    logger.info("\n2. Cached Routing Performance")
    for config in test_configs:
        for _ in range(100):
            route, duration = route_with_timing(config, use_cache=True)
            metrics.record("cached_routing", duration)
    
    # Test 3: Async routing performance
    logger.info("\n3. Async Routing Performance")
    for config in test_configs:
        for _ in range(100):
            route, duration = await async_route_with_timing(config)
            metrics.record("async_routing", duration)
    
    # Test 4: Parallel routing
    logger.info("\n4. Parallel Routing Performance")
    parallel_configs = test_configs * 20  # 100 configs
    parallel_times = parallel_routing_test(parallel_configs, max_workers=4)
    for t in parallel_times:
        metrics.record("parallel_routing_batch", t)
    
    # Test 5: Worst case scenario (many different models)
    logger.info("\n5. Worst Case Scenario")
    worst_case_configs = [
        {"model": f"provider{i}/model{j}", "messages": [{"role": "user", "content": "test"}]}
        for i in range(10)
        for j in range(10)
    ]
    
    start_time = time.perf_counter()
    for config in worst_case_configs:
        route_with_timing(config, use_cache=False)
    worst_case_total = (time.perf_counter() - start_time) * 1000
    metrics.record("worst_case_100_models", worst_case_total)
    
    # Clear cache and test again
    cached_route_decision.cache_clear()
    
    start_time = time.perf_counter()
    for config in worst_case_configs:
        route_with_timing(config, use_cache=True)
    worst_case_cached = (time.perf_counter() - start_time) * 1000
    metrics.record("worst_case_100_models_cached", worst_case_cached)
    
    # Print summary
    logger.info(f"\n{metrics.summary()}")
    
    # Check against target
    basic_stats = metrics.get_stats("basic_routing")
    cached_stats = metrics.get_stats("cached_routing")
    
    logger.info("\nPerformance vs Target (50ms):")
    logger.info(f"Basic Routing P95: {basic_stats.get('p95', 0):.3f}ms")
    logger.info(f"Cached Routing P95: {cached_stats.get('p95', 0):.3f}ms")
    
    return basic_stats.get('p95', 100) < 50  # Check if P95 is under 50ms


def test_optimization_strategies():
    """Test various optimization strategies."""
    
    logger.info("\nTesting Optimization Strategies")
    logger.info("="*50)
    
    # Strategy 1: Model prefix indexing
    model_prefixes = {
        "max": "claude_proxy",
        "claude": "claude_proxy",
        "openai": "litellm_openai",
        "vertex_ai": "litellm_vertex",
        "anthropic": "litellm_anthropic",
    }
    
    def optimized_route_v1(model: str) -> str:
        """Optimized routing using prefix dict."""
        if "/" in model:
            prefix = model.split("/")[0]
            return model_prefixes.get(prefix, "litellm_default")
        return "litellm_default"
    
    # Strategy 2: Early return for common cases
    def optimized_route_v2(model: str) -> str:
        """Optimized with early returns."""
        # Most common case first
        if model.startswith("openai/"):
            return "litellm_openai"
        if model.startswith("max/"):
            return "claude_proxy"
        if "/" in model:
            prefix = model.split("/", 1)[0]
            return f"litellm_{prefix}"
        return "litellm_default"
    
    # Test strategies
    test_models = ["openai/gpt-4", "max/claude", "vertex_ai/gemini"] * 1000
    
    # Test v1
    start = time.perf_counter()
    for model in test_models:
        optimized_route_v1(model)
    v1_time = (time.perf_counter() - start) * 1000
    
    # Test v2
    start = time.perf_counter()
    for model in test_models:
        optimized_route_v2(model)
    v2_time = (time.perf_counter() - start) * 1000
    
    logger.info(f"Strategy V1 (prefix dict): {v1_time:.2f}ms for {len(test_models)} routes")
    logger.info(f"Strategy V2 (early return): {v2_time:.2f}ms for {len(test_models)} routes")
    logger.info(f"Per-route V1: {v1_time/len(test_models):.4f}ms")
    logger.info(f"Per-route V2: {v2_time/len(test_models):.4f}ms")
    
    return min(v1_time, v2_time) / len(test_models) < 0.05  # <0.05ms per route


if __name__ == "__main__":
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Comprehensive performance tests
    total_tests += 1
    try:
        meets_target = asyncio.run(run_performance_tests())
        if not meets_target:
            all_validation_failures.append("Performance target not met (P95 > 50ms)")
    except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
    
    # Test 2: Optimization strategies
    total_tests += 1
    try:
        if not test_optimization_strategies():
            all_validation_failures.append("Optimization strategies too slow")
    except Exception as e:
        all_validation_failures.append(f"Optimization test exception: {str(e)}")
    
    # Test 3: Cache effectiveness
    total_tests += 1
    cached_route_decision.cache_clear()
    
    # First calls (cache miss)
    miss_times = []
    for i in range(10):
        start = time.perf_counter()
        cached_route_decision(f"model_{i}")
        miss_times.append((time.perf_counter() - start) * 1000)
    
    # Second calls (cache hit)
    hit_times = []
    for i in range(10):
        start = time.perf_counter()
        cached_route_decision(f"model_{i}")
        hit_times.append((time.perf_counter() - start) * 1000)
    
    cache_speedup = statistics.mean(miss_times) / statistics.mean(hit_times)
    logger.info(f"\nCache speedup: {cache_speedup:.1f}x")
    
    if cache_speedup < 2:  # Expect at least 2x speedup from cache
        all_validation_failures.append(f"Cache speedup too low: {cache_speedup:.1f}x")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-5 Routing performance benchmarks validated and ready")
        sys.exit(0)