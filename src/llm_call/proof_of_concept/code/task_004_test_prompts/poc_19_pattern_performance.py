#!/usr/bin/env python3
"""
POC 19: Pattern Performance and Optimization
Task: Benchmark and optimize pattern validation performance
Expected Output: Performance metrics and optimization recommendations
Links:
- https://docs.python.org/3/library/re.html#re.compile
- https://docs.python.org/3/library/timeit.html
"""

import re
import time
from typing import Dict, List, Tuple, Pattern, Callable
from dataclasses import dataclass
import statistics
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark"""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    ops_per_second: float


class PatternPerformanceBenchmark:
    """Benchmarks pattern validation performance"""
    
    def __init__(self):
        # Pre-compiled patterns (best practice)
        self.compiled_patterns = {
            "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            "url": re.compile(r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'),
            "phone": re.compile(r'^\+?[1-9]\d{1,14}$'),
            "ipv4": re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'),
        }
        
        # Raw pattern strings (for comparison)
        self.pattern_strings = {
            "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            "url": r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$',
            "phone": r'^\+?[1-9]\d{1,14}$',
            "ipv4": r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
        }
        
        # Test data
        self.test_data = {
            "email": [
                "user@example.com",
                "invalid.email",
                "john.doe+tag@company.co.uk",
                "test@test@test.com",
                "admin123@subdomain.example.org",
            ],
            "url": [
                "https://www.example.com",
                "not-a-url",
                "http://subdomain.example.com/path?query=value&param=123",
                "ftp://invalid.com",
                "https://api.service.com/v1/users/123456",
            ],
            "phone": [
                "+14155552671",
                "invalid-phone",
                "12025551234",
                "+442079460123",
                "00000000000",
            ],
            "ipv4": [
                "192.168.1.1",
                "256.1.1.1",
                "10.0.0.0",
                "172.16.254.1",
                "not.an.ip.address",
            ],
        }
    
    def benchmark_function(self, func: Callable, iterations: int = 10000) -> BenchmarkResult:
        """Benchmark a function with multiple iterations"""
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)
        
        total_time = sum(times)
        avg_time = statistics.mean(times)
        
        return BenchmarkResult(
            name=func.__name__,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min(times),
            max_time=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            ops_per_second=iterations / total_time if total_time > 0 else 0
        )
    
    def test_compiled_pattern(self, pattern_name: str) -> None:
        """Test using pre-compiled pattern"""
        pattern = self.compiled_patterns[pattern_name]
        for test_string in self.test_data[pattern_name]:
            pattern.match(test_string)
    
    def test_match_on_string(self, pattern_name: str) -> None:
        """Test using re.match with string pattern"""
        pattern = self.pattern_strings[pattern_name]
        for test_string in self.test_data[pattern_name]:
            re.match(pattern, test_string)
    
    def test_search_vs_match(self, pattern_name: str) -> None:
        """Test using search instead of match"""
        pattern = self.compiled_patterns[pattern_name]
        for test_string in self.test_data[pattern_name]:
            pattern.search(test_string)
    
    def test_fullmatch(self, pattern_name: str) -> None:
        """Test using fullmatch (Python 3.4+)"""
        pattern = self.compiled_patterns[pattern_name]
        for test_string in self.test_data[pattern_name]:
            pattern.fullmatch(test_string)
    
    def test_findall(self, pattern_name: str) -> None:
        """Test using findall (less efficient for validation)"""
        pattern = self.compiled_patterns[pattern_name]
        for test_string in self.test_data[pattern_name]:
            pattern.findall(test_string)
    
    def run_benchmarks(self) -> Dict[str, List[BenchmarkResult]]:
        """Run all benchmarks"""
        results = {}
        
        for pattern_name in self.compiled_patterns:
            logger.info(f"Benchmarking {pattern_name} pattern...")
            
            results[pattern_name] = [
                self.benchmark_function(
                    lambda: self.test_compiled_pattern(pattern_name),
                    iterations=10000
                ),
                self.benchmark_function(
                    lambda: self.test_match_on_string(pattern_name),
                    iterations=10000
                ),
                self.benchmark_function(
                    lambda: self.test_fullmatch(pattern_name),
                    iterations=10000
                ),
                self.benchmark_function(
                    lambda: self.test_search_vs_match(pattern_name),
                    iterations=10000
                ),
                self.benchmark_function(
                    lambda: self.test_findall(pattern_name),
                    iterations=10000
                ),
            ]
            
            # Update function names for clarity
            results[pattern_name][0].name = "compiled_match"
            results[pattern_name][1].name = "string_match"
            results[pattern_name][2].name = "fullmatch"
            results[pattern_name][3].name = "search"
            results[pattern_name][4].name = "findall"
        
        return results
    
    def test_pattern_complexity(self) -> Dict[str, float]:
        """Test how pattern complexity affects performance"""
        complexity_tests = {
            "simple": r'^test$',
            "moderate": r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$',
            "complex": r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',
            "very_complex": r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        }
        
        test_string = "test123@example.com"
        results = {}
        
        for name, pattern in complexity_tests.items():
            compiled = re.compile(pattern)
            
            # Benchmark
            times = []
            for _ in range(10000):
                start = time.perf_counter()
                compiled.match(test_string)
                end = time.perf_counter()
                times.append(end - start)
            
            avg_time = statistics.mean(times)
            results[name] = avg_time
            
            logger.info(f"Pattern complexity '{name}': {avg_time*1000000:.2f} μs per match")
        
        return results
    
    def test_string_length_impact(self) -> Dict[int, float]:
        """Test how input string length affects performance"""
        pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        results = {}
        lengths = [10, 50, 100, 500, 1000]
        
        for length in lengths:
            # Create test string of specified length
            if length <= 20:
                test_string = "a" * (length - 10) + "@test.com"
            else:
                test_string = "a" * (length - 10) + "@test.com"
            
            # Benchmark
            times = []
            for _ in range(5000):
                start = time.perf_counter()
                pattern.match(test_string)
                end = time.perf_counter()
                times.append(end - start)
            
            avg_time = statistics.mean(times)
            results[length] = avg_time
            
            logger.info(f"String length {length}: {avg_time*1000000:.2f} μs per match")
        
        return results


def main():
    """Run performance benchmarks and provide optimization recommendations"""
    benchmark = PatternPerformanceBenchmark()
    
    logger.info("=" * 60)
    logger.info("PATTERN VALIDATION PERFORMANCE BENCHMARKS")
    logger.info("=" * 60)
    
    # Run main benchmarks
    results = benchmark.run_benchmarks()
    
    # Display results
    for pattern_name, pattern_results in results.items():
        logger.info(f"\n{pattern_name.upper()} Pattern Results:")
        logger.info("-" * 40)
        
        # Sort by average time
        sorted_results = sorted(pattern_results, key=lambda x: x.avg_time)
        
        for i, result in enumerate(sorted_results):
            logger.info(
                f"{i+1}. {result.name:<15} - "
                f"Avg: {result.avg_time*1000000:.2f} μs, "
                f"Ops/sec: {result.ops_per_second:,.0f}"
            )
            
            # Mark best performer
            if i == 0:
                logger.success(f"   ⚡ BEST PERFORMER for {pattern_name}")
    
    # Test pattern complexity impact
    logger.info("\n" + "=" * 60)
    logger.info("PATTERN COMPLEXITY IMPACT")
    logger.info("=" * 60)
    
    complexity_results = benchmark.test_pattern_complexity()
    
    # Test string length impact
    logger.info("\n" + "=" * 60)
    logger.info("STRING LENGTH IMPACT")
    logger.info("=" * 60)
    
    length_results = benchmark.test_string_length_impact()
    
    # Performance recommendations
    logger.info("\n" + "=" * 60)
    logger.info("PERFORMANCE OPTIMIZATION RECOMMENDATIONS")
    logger.info("=" * 60)
    
    recommendations = [
        "1. **Always compile patterns**: Pre-compiled patterns are consistently faster",
        "2. **Use fullmatch() when possible**: More explicit and often faster than match()",
        "3. **Avoid findall() for validation**: It's designed for extraction, not validation",
        "4. **Cache compiled patterns**: Store in class attributes or module level",
        "5. **Simplify patterns when possible**: Complex patterns have significant overhead",
        "6. **Consider string operations first**: For simple checks, string methods can be faster",
        "7. **Batch validation**: Process multiple strings with the same pattern together",
        "8. **Profile real-world data**: Performance varies with actual input patterns",
    ]
    
    for rec in recommendations:
        logger.info(f"✓ {rec}")
    
    # Verify all benchmarks completed
    total_benchmarks = len(results) * 5 + len(complexity_results) + len(length_results)
    logger.info(f"\n📊 Total benchmarks completed: {total_benchmarks}")
    
    # Calculate performance improvement potential
    improvement_potential = []
    for pattern_name, pattern_results in results.items():
        slowest = max(r.avg_time for r in pattern_results)
        fastest = min(r.avg_time for r in pattern_results)
        improvement = ((slowest - fastest) / slowest) * 100
        improvement_potential.append((pattern_name, improvement))
    
    logger.info("\n" + "=" * 60)
    logger.info("PERFORMANCE IMPROVEMENT POTENTIAL")
    logger.info("=" * 60)
    
    for pattern, improvement in improvement_potential:
        logger.info(f"{pattern}: {improvement:.1f}% potential improvement")
    
    # Verify benchmarks show expected patterns
    all_tests_valid = True
    
    # Check that compiled patterns are faster than string patterns
    for pattern_name, pattern_results in results.items():
        compiled_time = next(r.avg_time for r in pattern_results if r.name == "compiled_match")
        string_time = next(r.avg_time for r in pattern_results if r.name == "string_match")
        
        if compiled_time >= string_time:
            logger.warning(f"⚠️  Unexpected: compiled pattern not faster for {pattern_name}")
            all_tests_valid = False
    
    # Check that complexity affects performance
    if complexity_results["simple"] >= complexity_results["very_complex"]:
        logger.warning("⚠️  Unexpected: simple patterns not faster than complex")
        all_tests_valid = False
    
    # Final validation
    if all_tests_valid and total_benchmarks > 0:
        logger.success(f"\n✅ ALL PERFORMANCE BENCHMARKS COMPLETED SUCCESSFULLY")
        logger.info(f"Total benchmarks: {total_benchmarks}")
        sys.exit(0)
    else:
        logger.error(f"\n❌ PERFORMANCE VALIDATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()