#!/usr/bin/env python3
"""
Module: run_comprehensive_tests.py
Description: Run tests with both standard and skeptical verification reports

This script runs tests and generates both a standard test report and a
skeptical verification report to ensure tests are using real APIs.

External Dependencies:
- pytest: https://docs.pytest.org/
- pytest-json-report: https://pypi.org/project/pytest-json-report/
- loguru: https://github.com/Delgan/loguru

Sample Input:
>>> python run_comprehensive_tests.py

Expected Output:
>>> === TEST REPORT GENERATION ===
>>> Running tests...
>>> Standard report: docs/reports/test_report_20250110_094347.md
>>> Skeptical report: docs/reports/skeptical_test_report_20250110_094347.md

Example Usage:
>>> python run_comprehensive_tests.py --integration-only
>>> python run_comprehensive_tests.py --verify-apis
"""

import subprocess
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import argparse

from loguru import logger


class ComprehensiveTestRunner:
    """Run tests and generate comprehensive reports."""
    
    def __init__(self):
        # Configure logging
        logger.remove()
        logger.add(sys.stdout, level="INFO",
                  format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
        
        self.results = {}
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def check_environment(self) -> Dict[str, Any]:
        """Check test environment setup."""
        env_info = {
            "python_version": sys.version.split()[0],
            "working_dir": os.getcwd(),
            "api_keys": {},
            "pytest_available": False
        }
        
        # Check API keys
        api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]
        for key in api_keys:
            value = os.environ.get(key)
            env_info["api_keys"][key] = bool(value and len(value) > 10)
        
        # Check pytest
        try:
            subprocess.run(["python", "-m", "pytest", "--version"], 
                         capture_output=True, check=True)
            env_info["pytest_available"] = True
        except:
            logger.error("pytest not available!")
        
        return env_info
    
    def run_standard_tests(self) -> Dict[str, Any]:
        """Run standard pytest with detailed reporting."""
        logger.info("\n" + "="*60)
        logger.info("Running standard test suite...")
        logger.info("="*60)
        
        cmd = [
            "python", "-m", "pytest",
            "tests/",
            "-v",
            "--durations=10",
            "--tb=short",
            "--json-report",
            "--json-report-file=test_results.json",
            "--asyncio-mode=auto"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        # Parse results
        test_data = {"tests": [], "summary": {}}
        if Path("test_results.json").exists():
            with open("test_results.json") as f:
                data = json.load(f)
                test_data = data
        
        return {
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "test_data": test_data
        }
    
    def run_integration_test(self) -> Dict[str, Any]:
        """Run simple integration test to verify API connectivity."""
        logger.info("\n" + "="*60)
        logger.info("Running integration test...")
        logger.info("="*60)
        
        test_file = Path("tests/integration/test_openai_simple.py")
        if not test_file.exists():
            # Create the test file
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_content = '''"""Simple OpenAI integration test."""
import os
import pytest
from openai import OpenAI

def test_openai_hello_world():
    """Test OpenAI API with a simple hello world request."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello world"}],
            max_tokens=10
        )
        
        assert response.choices[0].message.content
        assert len(response.choices[0].message.content) > 0
        return "Success"
    except Exception as e:
        pytest.fail(f"API call failed: {e}")
'''
            test_file.write_text(test_content)
        
        # Run the test
        cmd = [
            "python", "-m", "pytest",
            str(test_file),
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=integration_test.json"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration = time.time() - start_time
        
        return {
            "duration": duration,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "passed": result.returncode == 0
        }
    
    def generate_standard_report(self, test_results: Dict[str, Any]) -> str:
        """Generate standard test report."""
        test_data = test_results["test_data"]
        summary = test_data.get("summary", {})
        
        report = f"""# Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Total Tests**: {summary.get('total', 0)}
- **Passed**: {summary.get('passed', 0)} ({summary.get('passed', 0) / max(1, summary.get('total', 1)) * 100:.1f}%)
- **Failed**: {summary.get('failed', 0)} ({summary.get('failed', 0) / max(1, summary.get('total', 1)) * 100:.1f}%)
- **Skipped**: {summary.get('skipped', 0)} ({summary.get('skipped', 0) / max(1, summary.get('total', 1)) * 100:.1f}%)
- **Duration**: {test_results['duration']:.2f}s

## Test Results

| Test Name | Description | Result | Status | Duration | Timestamp | Error Message |
|-----------|-------------|--------|--------|----------|-----------|---------------|
"""
        
        for test in test_data.get("tests", []):
            name = test.get("nodeid", "").split("::")[-1]
            outcome = test.get("outcome", "unknown")
            duration = test.get("duration", 0)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_msg = ""
            
            if outcome == "failed" and test.get("call", {}).get("longrepr"):
                error_msg = str(test["call"]["longrepr"]).split("\n")[0][:50]
            
            status = "Pass" if outcome == "passed" else "Fail" if outcome == "failed" else "Skip"
            description = name.replace("_", " ").title()
            
            report += f"| {name} | {description} | {outcome.title()} | {status} | {duration:.3f}s | {timestamp} | {error_msg} |\n"
        
        # Add module distribution
        module_stats = {}
        for test in test_data.get("tests", []):
            module = test.get("nodeid", "").split("::")[0]
            if module not in module_stats:
                module_stats[module] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
            module_stats[module]["total"] += 1
            outcome = test.get("outcome", "unknown")
            if outcome in module_stats[module]:
                module_stats[module][outcome] += 1
        
        report += "\n## Test Distribution by Module\n\n"
        report += "| Module | Total | Passed | Failed | Skipped |\n"
        report += "|--------|-------|--------|--------|---------|\n"
        
        for module, stats in module_stats.items():
            report += f"| {module} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['skipped']} |\n"
        
        return report
    
    def run_skeptical_verification(self) -> str:
        """Run skeptical verification and return report path."""
        logger.info("\n" + "="*60)
        logger.info("Running skeptical verification...")
        logger.info("="*60)
        
        # Import and run the skeptical verifier
        sys.path.insert(0, str(Path(__file__).parent))
        from run_and_verify_tests import SkepticalTestVerifier
        
        verifier = SkepticalTestVerifier()
        verifier.run_full_verification()
        
        # Find the generated report
        reports_dir = Path("docs/reports")
        skeptical_reports = sorted(reports_dir.glob("skeptical_test_report_*.md"))
        if skeptical_reports:
            return str(skeptical_reports[-1])
        return ""
    
    def run_all(self, integration_only: bool = False, verify_apis: bool = False):
        """Run all tests and generate reports."""
        # Check environment
        env_info = self.check_environment()
        logger.info(f"Python: {env_info['python_version']}")
        logger.info(f"Working directory: {env_info['working_dir']}")
        logger.info("API Keys:")
        for key, available in env_info["api_keys"].items():
            status = "✅" if available else "❌"
            logger.info(f"  {status} {key}: {'Available' if available else 'NOT SET'}")
        
        if not env_info["pytest_available"]:
            logger.error("pytest is not available. Please install test dependencies.")
            sys.exit(1)
        
        # Run integration test if requested
        if integration_only:
            integration_result = self.run_integration_test()
            logger.info(f"\nIntegration test {'PASSED' if integration_result['passed'] else 'FAILED'}")
            logger.info(f"Duration: {integration_result['duration']:.2f}s")
            if not integration_result['passed']:
                logger.error("Output:")
                logger.error(integration_result['stdout'])
            return
        
        # Run standard tests
        test_results = self.run_standard_tests()
        
        # Generate standard report
        standard_report = self.generate_standard_report(test_results)
        standard_path = Path(f"docs/reports/test_report_{self.timestamp}.md")
        standard_path.parent.mkdir(exist_ok=True, parents=True)
        standard_path.write_text(standard_report)
        
        # Also save as latest
        latest_path = Path("docs/reports/test_report_latest.md")
        latest_path.write_text(standard_report)
        
        logger.info(f"\n✅ Standard report saved: {standard_path}")
        
        # Run skeptical verification if requested
        if verify_apis:
            skeptical_path = self.run_skeptical_verification()
            if skeptical_path:
                logger.info(f"✅ Skeptical report saved: {skeptical_path}")
        
        # Display summary
        summary = test_results["test_data"].get("summary", {})
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Total: {summary.get('total', 0)}")
        logger.info(f"Passed: {summary.get('passed', 0)}")
        logger.info(f"Failed: {summary.get('failed', 0)}")
        logger.info(f"Skipped: {summary.get('skipped', 0)}")
        logger.info(f"Duration: {test_results['duration']:.2f}s")
        
        # Exit with appropriate code
        sys.exit(test_results["exit_code"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run comprehensive tests")
    parser.add_argument("--integration-only", action="store_true",
                       help="Run only the integration test")
    parser.add_argument("--verify-apis", action="store_true",
                       help="Run skeptical API verification")
    
    args = parser.parse_args()
    
    runner = ComprehensiveTestRunner()
    runner.run_all(
        integration_only=args.integration_only,
        verify_apis=args.verify_apis
    )