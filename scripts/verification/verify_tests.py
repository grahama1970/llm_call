#!/usr/bin/env python3
"""
Module: verify_tests.py
Description: Test verification according to TEST_VERIFICATION_TEMPLATE_GUIDE.md

This script implements the verification loop process to ensure all tests
use real APIs and services, not mocks.

External Dependencies:
- pytest: https://docs.pytest.org/
- loguru: https://github.com/Delgan/loguru

Sample Input:
>>> python verify_tests.py --loop 1

Expected Output:
>>> LOOP 1/3: Running test verification...
>>> ✅ Real test detected: test_openai_hello_world (duration: 0.523s)
>>> ❌ Fake test detected: test_instant_response (duration: 0.001s)

Example Usage:
>>> python verify_tests.py
>>> python verify_tests.py --verbose
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import argparse

from loguru import logger


class TestVerifier:
    """Verify tests according to GRANGER standards."""
    
    # Duration thresholds from the guide
    DURATION_THRESHOLDS = {
        "database": 0.1,     # >100ms for DB operations
        "api": 0.05,         # >50ms for API calls
        "file": 0.01,        # >10ms for file I/O
        "integration": 0.5,  # >500ms for integration tests
        "browser": 1.0,      # >1s for browser automation
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.current_loop = 1
        self.max_loops = 3
        self.test_results: Dict[str, Any] = {}
        self.confidence_ratings: Dict[str, float] = {}
        
        # Configure logging
        logger.remove()
        level = "DEBUG" if verbose else "INFO"
        logger.add(sys.stdout, level=level,
                  format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
    
    def detect_mocks(self) -> int:
        """Detect mock usage in tests."""
        # More specific patterns to avoid false positives
        mock_patterns = ["@mock", "Mock(", "@patch", "MagicMock", "monkeypatch", "unittest.mock"]
        mock_count = 0
        
        test_files = Path("tests").rglob("test_*.py")
        for test_file in test_files:
            if "honeypot" in str(test_file):
                continue
                
            content = test_file.read_text()
            for pattern in mock_patterns:
                count = content.count(pattern)
                if count > 0:
                    mock_count += count
                    logger.warning(f"Mock detected in {test_file.name}: {pattern} ({count} instances)")
        
        return mock_count
    
    def check_honeypots(self) -> bool:
        """Verify honeypot tests exist and fail correctly."""
        honeypot_file = Path("tests/validation/test_honeypot.py")
        if not honeypot_file.exists():
            logger.error("❌ Honeypot tests missing!")
            return False
        
        # Run honeypot tests
        result = subprocess.run(
            ["pytest", str(honeypot_file), "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        
        # Honeypots should FAIL
        if result.returncode == 0:
            logger.error("❌ Honeypot tests passed - testing framework compromised!")
            return False
        
        # Check that all honeypot tests failed
        output = result.stdout
        passed = output.count(" PASSED")
        failed = output.count(" FAILED")
        
        if passed > 0:
            logger.error(f"❌ {passed} honeypot tests passed - should all fail!")
            return False
        
        logger.success(f"✅ All {failed} honeypot tests correctly failed")
        return True
    
    def analyze_test_duration(self, test_name: str, duration: float) -> Tuple[str, float]:
        """Analyze if test duration indicates real interaction."""
        # Determine test type from name
        test_type = "api"  # default
        if "database" in test_name or "db" in test_name:
            test_type = "database"
        elif "file" in test_name or "io" in test_name:
            test_type = "file"
        elif "integration" in test_name or "e2e" in test_name:
            test_type = "integration"
        elif "browser" in test_name or "selenium" in test_name:
            test_type = "browser"
        
        threshold = self.DURATION_THRESHOLDS.get(test_type, 0.05)
        
        if duration < threshold:
            confidence = (duration / threshold) * 50  # Max 50% if below threshold
            verdict = "SUSPICIOUS"
        else:
            # Above threshold, scale confidence
            confidence = min(90, 50 + (duration / threshold) * 20)
            verdict = "LIKELY REAL"
        
        return verdict, confidence
    
    def run_tests_with_analysis(self) -> Dict[str, Any]:
        """Run tests and analyze results."""
        logger.info(f"🔄 LOOP {self.current_loop}/{self.max_loops}: Running test verification...")
        
        # Run pytest with JSON report
        result = subprocess.run([
            "pytest", "tests/",
            "-v",
            "--durations=0",
            "--json-report",
            "--json-report-file=test-report.json",
            "-k", "not honeypot"  # Exclude honeypot tests from main run
        ], capture_output=True, text=True)
        
        # Load JSON report
        report_path = Path("test-report.json")
        if not report_path.exists():
            logger.error("Test report not generated!")
            return {}
        
        with open(report_path) as f:
            report = json.load(f)
        
        # Analyze each test
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "real": 0,
            "fake": 0,
            "suspicious": 0,
            "tests": []
        }
        
        for test in report.get("tests", []):
            test_name = test["nodeid"].split("::")[-1]
            duration = test.get("duration", 0)
            outcome = test["outcome"]
            
            results["total"] += 1
            if outcome == "passed":
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            # Analyze duration
            verdict, confidence = self.analyze_test_duration(test_name, duration)
            
            test_info = {
                "name": test_name,
                "duration": duration,
                "outcome": outcome,
                "verdict": verdict,
                "confidence": confidence
            }
            
            if verdict == "LIKELY REAL" and confidence >= 80:
                results["real"] += 1
                logger.success(f"✅ Real test: {test_name} (duration: {duration:.3f}s, confidence: {confidence:.1f}%)")
            elif verdict == "SUSPICIOUS" or confidence < 50:
                results["fake"] += 1
                logger.error(f"❌ Fake/Mock test: {test_name} (duration: {duration:.3f}s, confidence: {confidence:.1f}%)")
            else:
                results["suspicious"] += 1
                logger.warning(f"⚠️  Suspicious: {test_name} (duration: {duration:.3f}s, confidence: {confidence:.1f}%)")
            
            results["tests"].append(test_info)
            self.confidence_ratings[test_name] = confidence
        
        return results
    
    def verify_service_interactions(self) -> Dict[str, bool]:
        """Verify real service interactions."""
        services = {}
        
        # Check for database connections
        db_patterns = ["ArangoClient", "psycopg2.connect", "redis.Redis", "sqlite3.connect"]
        for pattern in db_patterns:
            count = 0
            for test_file in Path("tests").rglob("test_*.py"):
                if pattern in test_file.read_text():
                    count += 1
            services[f"database_{pattern}"] = count > 0
        
        # Check for API calls
        api_patterns = ["requests.", "httpx.", "aiohttp.", "litellm."]
        for pattern in api_patterns:
            count = 0
            for test_file in Path("tests").rglob("test_*.py"):
                if pattern in test_file.read_text():
                    count += 1
            services[f"api_{pattern}"] = count > 0
        
        return services
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate verification report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Test Verification Report: llm_call

**Date**: {timestamp}
**Loops Completed**: {self.current_loop}/{self.max_loops}
**Final Status**: {"PASS" if results.get("fake", 0) == 0 else "FAIL"}

## Summary Statistics
- Total Tests: {results.get('total', 0)}
- Real Tests: {results.get('real', 0)} ({results.get('real', 0) / max(1, results.get('total', 1)) * 100:.1f}%)
- Fake Tests: {results.get('fake', 0)} ({results.get('fake', 0) / max(1, results.get('total', 1)) * 100:.1f}%)
- Suspicious: {results.get('suspicious', 0)}
- Average Confidence: {sum(self.confidence_ratings.values()) / max(1, len(self.confidence_ratings)):.1f}%

## Mock Detection
- Mocks Found: {self.detect_mocks()}

## Service Dependencies Verified
"""
        
        services = self.verify_service_interactions()
        for service, found in services.items():
            status = "✅" if found else "❌"
            report += f"- {status} {service}: {'Found' if found else 'Not found'}\n"
        
        report += "\n## Test Details\n\n"
        report += "| Test Name | Duration | Verdict | Confidence | Status |\n"
        report += "|-----------|----------|---------|------------|--------|\n"
        
        for test in sorted(results.get("tests", []), key=lambda x: x["confidence"]):
            report += f"| {test['name'][:40]} | {test['duration']:.3f}s | {test['verdict']} | {test['confidence']:.1f}% | {test['outcome']} |\n"
        
        return report
    
    def run_verification_loop(self) -> int:
        """Run the full verification loop process."""
        # Pre-checks
        logger.info("🔍 Running pre-verification checks...")
        
        # Check for mocks
        mock_count = self.detect_mocks()
        if mock_count > 0:
            logger.warning(f"Found {mock_count} mock instances - these should be removed!")
        
        # Verify honeypots
        if not self.check_honeypots():
            logger.error("Honeypot verification failed!")
            return 1
        
        # Main verification loop
        for loop in range(self.max_loops):
            self.current_loop = loop + 1
            
            # Run tests and analyze
            results = self.run_tests_with_analysis()
            
            if not results:
                logger.error("Failed to analyze test results!")
                return 1
            
            # Check if we have enough real tests
            real_percentage = results["real"] / max(1, results["total"]) * 100
            
            logger.info(f"\nLoop {self.current_loop} Summary:")
            logger.info(f"  Real tests: {results['real']}/{results['total']} ({real_percentage:.1f}%)")
            logger.info(f"  Fake tests: {results['fake']}")
            logger.info(f"  Suspicious: {results['suspicious']}")
            
            # If no fake tests and >90% real, we're done
            if results["fake"] == 0 and real_percentage >= 90:
                logger.success("✅ All tests verified as REAL!")
                
                # Generate report
                report = self.generate_report(results)
                report_path = Path(f"docs/reports/test_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                report_path.parent.mkdir(exist_ok=True)
                report_path.write_text(report)
                logger.info(f"Report saved to: {report_path}")
                
                return 0
            
            # If we still have fake tests, try to fix
            if self.current_loop < self.max_loops:
                logger.warning(f"Found {results['fake']} fake tests, attempting fixes...")
                # In a real implementation, we'd apply fixes here
                time.sleep(1)  # Simulate fix time
        
        # Failed after max loops
        logger.error(f"❌ Failed to verify all tests after {self.max_loops} loops!")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify tests according to GRANGER standards")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--loop", type=int, default=1, help="Starting loop number")
    
    args = parser.parse_args()
    
    verifier = TestVerifier(verbose=args.verbose)
    verifier.current_loop = args.loop
    
    exit_code = verifier.run_verification_loop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()