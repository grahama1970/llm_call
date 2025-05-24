#!/usr/bin/env python3
"""
POC 34: Failure Reporting
Task: Generate detailed failure reports with actionable insights
Expected Output: Comprehensive failure analysis with debugging information
Links:
- https://docs.python.org/3/library/traceback.html
- https://rich.readthedocs.io/en/stable/
"""

import json
import traceback
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class FailureDetail:
    """Detailed information about a test failure"""
    test_case_id: str
    failure_type: str  # validation, error, timeout, etc.
    error_message: str
    stack_trace: Optional[str]
    timestamp: datetime
    context: Dict[str, Any]
    
    # Analysis fields
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None
    related_failures: List[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high, critical


class FailureReporter:
    """Generates comprehensive failure reports"""
    
    def __init__(self):
        self.failures: List[FailureDetail] = []
        self.failure_patterns: Dict[str, List[FailureDetail]] = defaultdict(list)
    
    def add_failure(self, failure: FailureDetail) -> None:
        """Add a failure to the reporter"""
        self.failures.append(failure)
        
        # Analyze and categorize
        self._analyze_failure(failure)
        
        # Group by pattern
        pattern = self._identify_pattern(failure)
        self.failure_patterns[pattern].append(failure)
    
    def _analyze_failure(self, failure: FailureDetail) -> None:
        """Analyze failure to determine root cause and fixes"""
        error_msg = failure.error_message.lower()
        
        # Common root causes and fixes
        if "timeout" in error_msg:
            failure.root_cause = "Operation exceeded time limit"
            failure.suggested_fix = "Increase timeout or optimize operation"
            failure.severity = "high"
            
        elif "connection" in error_msg or "network" in error_msg:
            failure.root_cause = "Network connectivity issue"
            failure.suggested_fix = "Check network connection and API endpoints"
            failure.severity = "high"
            
        elif "validation" in error_msg:
            if "json" in error_msg:
                failure.root_cause = "Invalid JSON structure"
                failure.suggested_fix = "Ensure response format matches expected schema"
            elif "field" in error_msg:
                failure.root_cause = "Missing or invalid field"
                failure.suggested_fix = "Check field requirements and data types"
            else:
                failure.root_cause = "Validation rule not satisfied"
                failure.suggested_fix = "Review validation criteria"
            failure.severity = "medium"
            
        elif "permission" in error_msg or "auth" in error_msg:
            failure.root_cause = "Authentication/Authorization failure"
            failure.suggested_fix = "Check API keys and permissions"
            failure.severity = "critical"
            
        elif "rate limit" in error_msg:
            failure.root_cause = "API rate limit exceeded"
            failure.suggested_fix = "Implement rate limiting or request throttling"
            failure.severity = "high"
            
        else:
            failure.root_cause = "Unknown error"
            failure.suggested_fix = "Review error details and logs"
            failure.severity = "medium"
    
    def _identify_pattern(self, failure: FailureDetail) -> str:
        """Identify failure pattern for grouping"""
        # Simple pattern identification based on error type
        error_msg = failure.error_message.lower()
        
        if failure.failure_type == "validation":
            if "json" in error_msg:
                return "json_validation"
            elif "field" in error_msg:
                return "field_validation"
            else:
                return "general_validation"
        elif failure.failure_type == "error":
            if "timeout" in error_msg:
                return "timeout"
            elif "connection" in error_msg:
                return "connection"
            else:
                return "runtime_error"
        else:
            return failure.failure_type
    
    def find_related_failures(self) -> None:
        """Find related failures across test cases"""
        # Simple approach: failures with same pattern are related
        for pattern, failures in self.failure_patterns.items():
            if len(failures) > 1:
                test_ids = [f.test_case_id for f in failures]
                for failure in failures:
                    failure.related_failures = [
                        tid for tid in test_ids if tid != failure.test_case_id
                    ]
    
    def generate_report(self, format: str = "detailed") -> str:
        """Generate failure report"""
        if not self.failures:
            return "No failures to report"
        
        self.find_related_failures()
        
        if format == "detailed":
            return self._generate_detailed_report()
        elif format == "summary":
            return self._generate_summary_report()
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def _generate_detailed_report(self) -> str:
        """Generate detailed failure report"""
        report = []
        report.append("# FAILURE ANALYSIS REPORT")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Failures: {len(self.failures)}")
        
        # Summary by severity
        severity_counts = defaultdict(int)
        for failure in self.failures:
            severity_counts[failure.severity] += 1
        
        report.append("\n## Severity Summary")
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                report.append(f"- **{severity.upper()}**: {count} failures")
        
        # Pattern analysis
        report.append("\n## Failure Patterns")
        report.append(f"Identified {len(self.failure_patterns)} distinct patterns:")
        
        for pattern, failures in sorted(self.failure_patterns.items(), 
                                      key=lambda x: len(x[1]), reverse=True):
            report.append(f"\n### Pattern: {pattern}")
            report.append(f"Occurrences: {len(failures)}")
            report.append("Affected tests:")
            for f in failures[:5]:  # Show first 5
                report.append(f"- {f.test_case_id}")
            if len(failures) > 5:
                report.append(f"- ... and {len(failures) - 5} more")
        
        # Individual failures
        report.append("\n## Detailed Failures")
        
        # Sort by severity
        sorted_failures = sorted(
            self.failures,
            key=lambda f: ["low", "medium", "high", "critical"].index(f.severity),
            reverse=True
        )
        
        for i, failure in enumerate(sorted_failures[:10], 1):  # Top 10
            report.append(f"\n### {i}. {failure.test_case_id}")
            report.append(f"**Severity**: {failure.severity.upper()}")
            report.append(f"**Type**: {failure.failure_type}")
            report.append(f"**Error**: {failure.error_message}")
            
            if failure.root_cause:
                report.append(f"**Root Cause**: {failure.root_cause}")
            
            if failure.suggested_fix:
                report.append(f"**Suggested Fix**: {failure.suggested_fix}")
            
            if failure.related_failures:
                report.append(f"**Related Failures**: {', '.join(failure.related_failures[:3])}")
            
            if failure.stack_trace:
                report.append("\n**Stack Trace**:")
                report.append("```")
                report.append(failure.stack_trace[:500] + "..." if len(failure.stack_trace) > 500 else failure.stack_trace)
                report.append("```")
        
        if len(self.failures) > 10:
            report.append(f"\n... and {len(self.failures) - 10} more failures")
        
        # Recommendations
        report.append("\n## Recommendations")
        recommendations = self._generate_recommendations()
        for rec in recommendations:
            report.append(f"- {rec}")
        
        return "\n".join(report)
    
    def _generate_summary_report(self) -> str:
        """Generate summary failure report"""
        report = []
        report.append("# FAILURE SUMMARY")
        report.append(f"Total: {len(self.failures)} failures")
        
        # By pattern
        report.append("\nBy Pattern:")
        for pattern, failures in sorted(self.failure_patterns.items(), 
                                      key=lambda x: len(x[1]), reverse=True):
            report.append(f"- {pattern}: {len(failures)}")
        
        # Top issues
        report.append("\nTop Issues:")
        for failure in self.failures[:5]:
            report.append(f"- {failure.test_case_id}: {failure.error_message[:50]}...")
        
        return "\n".join(report)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on patterns
        if "timeout" in self.failure_patterns and len(self.failure_patterns["timeout"]) > 2:
            recommendations.append("Multiple timeout failures detected - consider increasing global timeout settings")
        
        if "connection" in self.failure_patterns:
            recommendations.append("Network connectivity issues detected - verify API endpoints and network configuration")
        
        if "json_validation" in self.failure_patterns and len(self.failure_patterns["json_validation"]) > 3:
            recommendations.append("Frequent JSON validation failures - review response format specifications")
        
        # Based on severity
        critical_count = sum(1 for f in self.failures if f.severity == "critical")
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} CRITICAL failures immediately")
        
        # General recommendations
        if len(self.failures) > 10:
            recommendations.append("High failure rate detected - consider reviewing test suite configuration")
        
        related_groups = sum(1 for f in self.failures if f.related_failures)
        if related_groups > 5:
            recommendations.append("Multiple related failures detected - likely systemic issues")
        
        return recommendations
    
    def export_json(self, filepath: Path) -> None:
        """Export failures to JSON for further analysis"""
        data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_failures": len(self.failures),
                "patterns": list(self.failure_patterns.keys())
            },
            "failures": [
                {
                    "test_case_id": f.test_case_id,
                    "failure_type": f.failure_type,
                    "error_message": f.error_message,
                    "severity": f.severity,
                    "root_cause": f.root_cause,
                    "suggested_fix": f.suggested_fix,
                    "related_failures": f.related_failures,
                    "timestamp": f.timestamp.isoformat()
                }
                for f in self.failures
            ],
            "pattern_summary": {
                pattern: len(failures) 
                for pattern, failures in self.failure_patterns.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """Test failure reporting"""
    
    logger.info("=" * 60)
    logger.info("FAILURE REPORTING TESTING")
    logger.info("=" * 60)
    
    reporter = FailureReporter()
    
    # Create sample failures
    sample_failures = [
        FailureDetail(
            test_case_id="test_001",
            failure_type="validation",
            error_message="JSON validation failed: missing field 'title'",
            stack_trace=None,
            timestamp=datetime.now(),
            context={"model": "gpt-3.5-turbo"}
        ),
        FailureDetail(
            test_case_id="test_002",
            failure_type="error",
            error_message="Connection timeout after 30s",
            stack_trace="Traceback...\nTimeoutError",
            timestamp=datetime.now(),
            context={"endpoint": "https://api.example.com"}
        ),
        FailureDetail(
            test_case_id="test_003",
            failure_type="validation",
            error_message="JSON validation failed: invalid format",
            stack_trace=None,
            timestamp=datetime.now(),
            context={"model": "gpt-4"}
        ),
        FailureDetail(
            test_case_id="test_004",
            failure_type="error",
            error_message="Authentication failed: Invalid API key",
            stack_trace="Traceback...\nAuthError",
            timestamp=datetime.now(),
            context={"service": "openai"}
        ),
        FailureDetail(
            test_case_id="test_005",
            failure_type="validation",
            error_message="Field validation failed: 'author' not present",
            stack_trace=None,
            timestamp=datetime.now(),
            context={"model": "gpt-3.5-turbo"}
        ),
        FailureDetail(
            test_case_id="test_006",
            failure_type="error",
            error_message="Connection timeout after 30s",
            stack_trace="Traceback...\nTimeoutError",
            timestamp=datetime.now(),
            context={"endpoint": "https://api.example.com"}
        ),
    ]
    
    # Add failures
    for failure in sample_failures:
        reporter.add_failure(failure)
    
    # Generate reports
    logger.info("\n📊 Generating Detailed Report")
    detailed_report = reporter.generate_report("detailed")
    print("\n" + detailed_report)
    
    logger.info("\n📊 Generating Summary Report")
    summary_report = reporter.generate_report("summary")
    print("\n" + summary_report)
    
    # Export JSON
    json_path = Path("failure_report.json")
    reporter.export_json(json_path)
    logger.info(f"\n📁 Exported JSON report to {json_path}")
    
    # Clean up
    if json_path.exists():
        json_path.unlink()
    
    # Verify reporter functionality
    if len(reporter.failures) == 6 and len(reporter.failure_patterns) > 0:
        logger.success("\n✅ Failure reporting working correctly")
        return 0
    else:
        logger.error("\n❌ Failure reporting has issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())