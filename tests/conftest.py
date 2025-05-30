"""Pytest configuration and fixtures for test reporting."""

import pytest
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Initialize LiteLLM cache before any tests run
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
initialize_litellm_cache()


class MarkdownReporter:
    """Custom pytest plugin for generating Markdown test reports."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None
        
    def pytest_sessionstart(self, session):
        """Called when test session starts."""
        self.start_time = datetime.now()
        self.test_results = []
        
    def pytest_runtest_logreport(self, report):
        """Called after each test phase (setup, call, teardown)."""
        if report.when == "call":  # Only capture the actual test execution
            test_result = {
                "name": report.nodeid.split("::")[-1],
                "module": report.nodeid.split("::")[0],
                "description": self._get_test_description(report),
                "result": self._get_result_message(report),
                "status": "Pass" if report.passed else "Fail" if report.failed else "Skip",
                "duration": f"{report.duration:.3f}s",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error_message": str(report.longrepr) if report.failed else ""
            }
            self.test_results.append(test_result)
    
    def pytest_sessionfinish(self, session):
        """Called when test session ends."""
        self.end_time = datetime.now()
        self._generate_markdown_report()
    
    def _get_test_description(self, report) -> str:
        """Extract test description from docstring or generate from name."""
        try:
            # Try to get the test function
            test_path = report.nodeid.split("::")
            if len(test_path) >= 2:
                module_path = test_path[0]
                test_name = test_path[-1]
                
                # Import the module and get the test function
                import importlib.util
                spec = importlib.util.spec_from_file_location("test_module", module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Try to get the test function/method
                    if hasattr(module, test_name):
                        test_func = getattr(module, test_name)
                        if test_func.__doc__:
                            return test_func.__doc__.strip().split('\n')[0]
                    
                    # Try to get from class if it's a method
                    for item in dir(module):
                        obj = getattr(module, item)
                        if hasattr(obj, test_name):
                            method = getattr(obj, test_name)
                            if method.__doc__:
                                return method.__doc__.strip().split('\n')[0]
        except Exception:
            pass
        
        # Fallback: generate description from test name
        name = report.nodeid.split("::")[-1]
        # Convert test_something_with_underscores to "Something with underscores"
        description = name.replace("test_", "").replace("_", " ").capitalize()
        return description
    
    def _get_result_message(self, report) -> str:
        """Get a concise result message."""
        if report.passed:
            return "Success"
        elif report.failed:
            # Extract the assertion message if available
            if hasattr(report, 'longrepr') and report.longrepr:
                repr_str = str(report.longrepr)
                # Try to extract assertion error
                if "AssertionError" in repr_str:
                    lines = repr_str.split('\n')
                    for line in lines:
                        if "assert" in line or "AssertionError" in line:
                            return line.strip()[:100]  # Limit length
            return "Test failed"
        elif report.skipped:
            return "Skipped"
        return "Unknown"
    
    def _generate_markdown_report(self):
        """Generate the Markdown report file."""
        if not self.test_results:
            return
            
        # Create reports directory if it doesn't exist
        reports_dir = Path("docs/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        filename = reports_dir / f"test_report_{timestamp}.md"
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "Pass")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "Fail")
        skipped_tests = sum(1 for r in self.test_results if r["status"] == "Skip")
        
        # Generate report content
        content = [
            f"# Test Report - {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Total Tests**: {total_tests}",
            f"- **Passed**: {passed_tests} ({passed_tests/total_tests*100:.1f}%)",
            f"- **Failed**: {failed_tests} ({failed_tests/total_tests*100:.1f}%)",
            f"- **Skipped**: {skipped_tests} ({skipped_tests/total_tests*100:.1f}%)",
            f"- **Duration**: {(self.end_time - self.start_time).total_seconds():.2f}s",
            "",
            "## Test Results",
            "",
            "| Test Name | Description | Result | Status | Duration | Timestamp | Error Message |",
            "|-----------|-------------|--------|--------|----------|-----------|---------------|"
        ]
        
        # Add test results
        for result in self.test_results:
            error_msg = result['error_message'].replace('\n', ' ')[:100] if result['error_message'] else ""
            if error_msg and len(error_msg) == 100:
                error_msg += "..."
                
            row = (
                f"| {result['name']} "
                f"| {result['description']} "
                f"| {result['result']} "
                f"| {result['status']} "
                f"| {result['duration']} "
                f"| {result['timestamp']} "
                f"| {error_msg} |"
            )
            content.append(row)
        
        # Add test distribution by module
        content.extend([
            "",
            "## Test Distribution by Module",
            "",
            "| Module | Total | Passed | Failed | Skipped |",
            "|--------|-------|--------|--------|---------|"
        ])
        
        # Group by module
        module_stats = {}
        for result in self.test_results:
            module = result['module']
            if module not in module_stats:
                module_stats[module] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
            
            module_stats[module]["total"] += 1
            if result["status"] == "Pass":
                module_stats[module]["passed"] += 1
            elif result["status"] == "Fail":
                module_stats[module]["failed"] += 1
            else:
                module_stats[module]["skipped"] += 1
        
        for module, stats in sorted(module_stats.items()):
            row = (
                f"| {module} "
                f"| {stats['total']} "
                f"| {stats['passed']} "
                f"| {stats['failed']} "
                f"| {stats['skipped']} |"
            )
            content.append(row)
        
        # Write report
        with open(filename, 'w') as f:
            f.write('\n'.join(content))
            
        print(f"\n📊 Test report generated: {filename}")
        
        # Also create a latest symlink for easy access
        latest_link = reports_dir / "test_report_latest.md"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(filename.name)


def pytest_configure(config):
    """Register the custom reporter plugin."""
    config.pluginmanager.register(MarkdownReporter(), "markdown_reporter")


# Common fixtures
@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def user_prompts(test_data_dir):
    """Load user prompts from fixture file."""
    prompts_file = test_data_dir / "user_prompts.jsonl"
    prompts = []
    if prompts_file.exists():
        with open(prompts_file, 'r') as f:
            for line in f:
                prompts.append(json.loads(line.strip()))
    return prompts


@pytest.fixture
def extended_user_prompts(test_data_dir):
    """Load extended user prompts from fixture file."""
    prompts_file = test_data_dir / "user_prompts_extended.jsonl"
    prompts = []
    if prompts_file.exists():
        with open(prompts_file, 'r') as f:
            for line in f:
                prompts.append(json.loads(line.strip()))
    return prompts