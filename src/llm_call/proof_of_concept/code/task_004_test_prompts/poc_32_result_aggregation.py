#!/usr/bin/env python3
"""
POC 32: Result Aggregation
Task: Aggregate test results from multiple sources and generate unified reports
Expected Output: Comprehensive test summary with statistics and insights
Links:
- https://docs.python.org/3/library/statistics.html
- https://pandas.pydata.org/docs/
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime
import statistics
from pathlib import Path
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class AggregatedStats:
    """Aggregated statistics for test results"""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    
    # Timing stats
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    p50_duration_ms: float = 0.0
    p95_duration_ms: float = 0.0
    p99_duration_ms: float = 0.0
    
    # Model stats
    model_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    validation_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)
    failure_patterns: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total_tests * 100) if self.total_tests > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return ((self.failed + self.errors) / self.total_tests * 100) if self.total_tests > 0 else 0.0


class ResultAggregator:
    """Aggregates test results from multiple sources"""
    
    def __init__(self):
        self.all_results: List[Dict[str, Any]] = []
        self.aggregated_stats = AggregatedStats()
        self.tag_performance: Dict[str, Dict[str, Any]] = defaultdict(dict)
    
    def add_results(self, results: List[Dict[str, Any]]) -> None:
        """Add test results to aggregator"""
        self.all_results.extend(results)
        logger.info(f"Added {len(results)} test results")
    
    def aggregate(self) -> AggregatedStats:
        """Perform aggregation on all results"""
        if not self.all_results:
            logger.warning("No results to aggregate")
            return self.aggregated_stats
        
        logger.info(f"Aggregating {len(self.all_results)} test results")
        
        # Basic counts
        self._aggregate_status_counts()
        
        # Timing statistics
        self._aggregate_timing_stats()
        
        # Model performance
        self._aggregate_model_stats()
        
        # Validation statistics
        self._aggregate_validation_stats()
        
        # Failure patterns
        self._analyze_failure_patterns()
        
        # Tag-based performance
        self._aggregate_by_tags()
        
        return self.aggregated_stats
    
    def _aggregate_status_counts(self) -> None:
        """Count tests by status"""
        for result in self.all_results:
            status = result.get("status", "unknown").lower()
            
            self.aggregated_stats.total_tests += 1
            
            if status == "passed":
                self.aggregated_stats.passed += 1
            elif status == "failed":
                self.aggregated_stats.failed += 1
            elif status == "error":
                self.aggregated_stats.errors += 1
            elif status == "skipped":
                self.aggregated_stats.skipped += 1
    
    def _aggregate_timing_stats(self) -> None:
        """Calculate timing statistics"""
        durations = []
        
        for result in self.all_results:
            duration = result.get("duration_ms", 0)
            if duration > 0:
                durations.append(duration)
                self.aggregated_stats.total_duration_ms += duration
                
                if duration < self.aggregated_stats.min_duration_ms:
                    self.aggregated_stats.min_duration_ms = duration
                if duration > self.aggregated_stats.max_duration_ms:
                    self.aggregated_stats.max_duration_ms = duration
        
        if durations:
            self.aggregated_stats.avg_duration_ms = statistics.mean(durations)
            
            # Calculate percentiles
            sorted_durations = sorted(durations)
            n = len(sorted_durations)
            
            self.aggregated_stats.p50_duration_ms = sorted_durations[n // 2]
            self.aggregated_stats.p95_duration_ms = sorted_durations[int(n * 0.95)]
            self.aggregated_stats.p99_duration_ms = sorted_durations[int(n * 0.99)]
    
    def _aggregate_model_stats(self) -> None:
        """Aggregate statistics by model"""
        for result in self.all_results:
            # Extract model from result or config
            model = "unknown"
            if "llm_config" in result:
                model = result["llm_config"].get("model", "unknown")
            elif "metadata" in result:
                model = result["metadata"].get("model", "unknown")
            
            if model not in self.aggregated_stats.model_stats:
                self.aggregated_stats.model_stats[model] = {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                    "errors": 0,
                    "avg_duration_ms": 0
                }
            
            stats = self.aggregated_stats.model_stats[model]
            stats["total"] += 1
            
            status = result.get("status", "unknown").lower()
            if status == "passed":
                stats["passed"] += 1
            elif status == "failed":
                stats["failed"] += 1
            elif status == "error":
                stats["errors"] += 1
    
    def _aggregate_validation_stats(self) -> None:
        """Aggregate validation statistics"""
        for result in self.all_results:
            validation_results = result.get("validation_results", [])
            
            for val_result in validation_results:
                val_type = val_result.get("type", "unknown")
                
                if val_type not in self.aggregated_stats.validation_stats:
                    self.aggregated_stats.validation_stats[val_type] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0
                    }
                
                stats = self.aggregated_stats.validation_stats[val_type]
                stats["total"] += 1
                
                if val_result.get("passed", False):
                    stats["passed"] += 1
                else:
                    stats["failed"] += 1
    
    def _analyze_failure_patterns(self) -> None:
        """Analyze common failure patterns"""
        for result in self.all_results:
            if result.get("status", "").lower() in ["failed", "error"]:
                # Extract error patterns
                error_msg = result.get("error_message", "")
                
                # Common patterns to look for
                if "timeout" in error_msg.lower():
                    self.aggregated_stats.failure_patterns["timeout"] += 1
                elif "validation" in error_msg.lower():
                    self.aggregated_stats.failure_patterns["validation"] += 1
                elif "json" in error_msg.lower():
                    self.aggregated_stats.failure_patterns["json_error"] += 1
                elif "connection" in error_msg.lower():
                    self.aggregated_stats.failure_patterns["connection"] += 1
                else:
                    self.aggregated_stats.failure_patterns["other"] += 1
    
    def _aggregate_by_tags(self) -> None:
        """Aggregate performance by tags"""
        for result in self.all_results:
            tags = result.get("tags", [])
            
            for tag in tags:
                if tag not in self.tag_performance:
                    self.tag_performance[tag] = {
                        "total": 0,
                        "passed": 0,
                        "avg_duration_ms": []
                    }
                
                self.tag_performance[tag]["total"] += 1
                
                if result.get("status", "").lower() == "passed":
                    self.tag_performance[tag]["passed"] += 1
                
                duration = result.get("duration_ms", 0)
                if duration > 0:
                    self.tag_performance[tag]["avg_duration_ms"].append(duration)
        
        # Calculate averages
        for tag, stats in self.tag_performance.items():
            durations = stats["avg_duration_ms"]
            if durations:
                stats["avg_duration_ms"] = statistics.mean(durations)
            else:
                stats["avg_duration_ms"] = 0
    
    def generate_report(self, output_format: str = "markdown") -> str:
        """Generate aggregated report"""
        if output_format == "markdown":
            return self._generate_markdown_report()
        elif output_format == "json":
            return self._generate_json_report()
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown format report"""
        stats = self.aggregated_stats
        
        report = []
        report.append("# Test Results Summary")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Overview
        report.append("\n## Overview")
        report.append(f"- **Total Tests**: {stats.total_tests}")
        report.append(f"- **Passed**: {stats.passed} ({stats.pass_rate:.1f}%)")
        report.append(f"- **Failed**: {stats.failed}")
        report.append(f"- **Errors**: {stats.errors}")
        report.append(f"- **Skipped**: {stats.skipped}")
        report.append(f"- **Error Rate**: {stats.error_rate:.1f}%")
        
        # Performance
        report.append("\n## Performance Metrics")
        report.append(f"- **Total Duration**: {stats.total_duration_ms:.0f}ms")
        report.append(f"- **Average**: {stats.avg_duration_ms:.0f}ms")
        report.append(f"- **Min**: {stats.min_duration_ms:.0f}ms")
        report.append(f"- **Max**: {stats.max_duration_ms:.0f}ms")
        report.append(f"- **P50**: {stats.p50_duration_ms:.0f}ms")
        report.append(f"- **P95**: {stats.p95_duration_ms:.0f}ms")
        report.append(f"- **P99**: {stats.p99_duration_ms:.0f}ms")
        
        # Model Performance
        if stats.model_stats:
            report.append("\n## Model Performance")
            report.append("\n| Model | Total | Passed | Failed | Pass Rate |")
            report.append("|-------|-------|--------|--------|-----------|")
            
            for model, model_stats in sorted(stats.model_stats.items()):
                pass_rate = (model_stats["passed"] / model_stats["total"] * 100) if model_stats["total"] > 0 else 0
                report.append(
                    f"| {model} | {model_stats['total']} | "
                    f"{model_stats['passed']} | {model_stats['failed']} | "
                    f"{pass_rate:.1f}% |"
                )
        
        # Validation Performance
        if stats.validation_stats:
            report.append("\n## Validation Performance")
            report.append("\n| Validator | Total | Passed | Failed | Success Rate |")
            report.append("|-----------|-------|--------|--------|--------------|")
            
            for val_type, val_stats in sorted(stats.validation_stats.items()):
                success_rate = (val_stats["passed"] / val_stats["total"] * 100) if val_stats["total"] > 0 else 0
                report.append(
                    f"| {val_type} | {val_stats['total']} | "
                    f"{val_stats['passed']} | {val_stats['failed']} | "
                    f"{success_rate:.1f}% |"
                )
        
        # Failure Patterns
        if stats.failure_patterns:
            report.append("\n## Failure Analysis")
            report.append("\n| Pattern | Count | Percentage |")
            report.append("|---------|-------|------------|")
            
            total_failures = sum(stats.failure_patterns.values())
            for pattern, count in sorted(stats.failure_patterns.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_failures * 100) if total_failures > 0 else 0
                report.append(f"| {pattern} | {count} | {percentage:.1f}% |")
        
        # Tag Performance
        if self.tag_performance:
            report.append("\n## Performance by Tags")
            report.append("\n| Tag | Total | Pass Rate | Avg Duration |")
            report.append("|-----|-------|-----------|--------------|")
            
            for tag, tag_stats in sorted(self.tag_performance.items()):
                pass_rate = (tag_stats["passed"] / tag_stats["total"] * 100) if tag_stats["total"] > 0 else 0
                avg_duration = tag_stats["avg_duration_ms"]
                report.append(
                    f"| {tag} | {tag_stats['total']} | "
                    f"{pass_rate:.1f}% | {avg_duration:.0f}ms |"
                )
        
        return "\n".join(report)
    
    def _generate_json_report(self) -> str:
        """Generate JSON format report"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.aggregated_stats.total_tests,
                "passed": self.aggregated_stats.passed,
                "failed": self.aggregated_stats.failed,
                "errors": self.aggregated_stats.errors,
                "skipped": self.aggregated_stats.skipped,
                "pass_rate": self.aggregated_stats.pass_rate,
                "error_rate": self.aggregated_stats.error_rate
            },
            "performance": {
                "total_duration_ms": self.aggregated_stats.total_duration_ms,
                "avg_duration_ms": self.aggregated_stats.avg_duration_ms,
                "min_duration_ms": self.aggregated_stats.min_duration_ms,
                "max_duration_ms": self.aggregated_stats.max_duration_ms,
                "p50_duration_ms": self.aggregated_stats.p50_duration_ms,
                "p95_duration_ms": self.aggregated_stats.p95_duration_ms,
                "p99_duration_ms": self.aggregated_stats.p99_duration_ms
            },
            "model_stats": self.aggregated_stats.model_stats,
            "validation_stats": self.aggregated_stats.validation_stats,
            "failure_patterns": dict(self.aggregated_stats.failure_patterns),
            "tag_performance": self.tag_performance
        }
        
        return json.dumps(report_data, indent=2)


def main():
    """Test result aggregation"""
    
    # Create sample test results
    sample_results = [
        {
            "test_case_id": "test_001",
            "status": "passed",
            "duration_ms": 150,
            "llm_config": {"model": "openai/gpt-3.5-turbo"},
            "tags": ["basic", "text"]
        },
        {
            "test_case_id": "test_002",
            "status": "passed",
            "duration_ms": 200,
            "llm_config": {"model": "openai/gpt-4"},
            "validation_results": [
                {"type": "json_string", "passed": True},
                {"type": "field_present", "passed": True}
            ],
            "tags": ["json", "validation"]
        },
        {
            "test_case_id": "test_003",
            "status": "failed",
            "duration_ms": 100,
            "error_message": "Validation failed: field not present",
            "llm_config": {"model": "openai/gpt-3.5-turbo"},
            "validation_results": [
                {"type": "field_present", "passed": False}
            ],
            "tags": ["json", "validation"]
        },
        {
            "test_case_id": "test_004",
            "status": "error",
            "duration_ms": 50,
            "error_message": "Connection timeout",
            "llm_config": {"model": "vertex_ai/gemini"},
            "tags": ["basic"]
        },
        {
            "test_case_id": "test_005",
            "status": "passed",
            "duration_ms": 300,
            "llm_config": {"model": "openai/gpt-4"},
            "tags": ["multimodal"]
        }
    ]
    
    logger.info("=" * 60)
    logger.info("RESULT AGGREGATION TESTING")
    logger.info("=" * 60)
    
    # Create aggregator
    aggregator = ResultAggregator()
    
    # Add results
    aggregator.add_results(sample_results)
    
    # Perform aggregation
    stats = aggregator.aggregate()
    
    # Generate reports
    logger.info("\n📊 Generating Markdown Report")
    markdown_report = aggregator.generate_report("markdown")
    print("\n" + markdown_report)
    
    logger.info("\n📊 Generating JSON Report")
    json_report = aggregator.generate_report("json")
    print("\nJSON Report Preview:")
    print(json_report[:500] + "...")
    
    # Verify aggregation
    if stats.total_tests == 5 and stats.passed == 3 and stats.failed == 1 and stats.errors == 1:
        logger.success("\n✅ Result aggregation working correctly")
        return 0
    else:
        logger.error("\n❌ Result aggregation has issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())