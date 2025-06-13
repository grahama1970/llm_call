#!/usr/bin/env python3
"""
Module: run_and_verify_tests.py
Description: Run tests and create skeptical verification report

This script runs tests and verifies they use real APIs according to
TEST_VERIFICATION_TEMPLATE_GUIDE.md requirements.

External Dependencies:
- pytest: https://docs.pytest.org/
- loguru: https://github.com/Delgan/loguru

Sample Input:
>>> python run_and_verify_tests.py

Expected Output:
>>> === TEST VERIFICATION REPORT ===
>>> Smoke Tests: 2/2 passed (100%)
>>> Unit Tests: 5/5 passed (100%)
>>> ❌ CRITICAL: Integration tests show signs of mocking!

Example Usage:
>>> python run_and_verify_tests.py --category integration
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import os

from loguru import logger


class SkepticalTestVerifier:
    """Verify tests with extreme skepticism per GRANGER standards."""
    
    def __init__(self):
        # Configure logging for clear output
        logger.remove()
        logger.add(sys.stdout, level="INFO",
                  format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
        
        self.report_lines = []
        self.total_passed = 0
        self.total_failed = 0
        self.suspicious_tests = []
        self.verified_real_tests = []
    
    def run_test_category(self, category: str) -> Dict[str, Any]:
        """Run tests for a specific category and analyze results."""
        test_path = Path(f"tests/{category}")
        
        if not test_path.exists():
            return {"error": f"Category {category} does not exist"}
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Running {category.upper()} tests...")
        logger.info(f"{'='*60}")
        
        # Run pytest with detailed output
        cmd = [
            "python", "-m", "pytest",
            str(test_path),
            "-v",
            "--durations=0",
            "--tb=short",
            "--json-report",
            f"--json-report-file=report_{category}.json"
        ]
        
        # Special handling for async tests
        if category in ["integration", "e2e"]:
            cmd.append("--asyncio-mode=auto")
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        total_duration = time.time() - start_time
        
        # Parse results
        report_file = Path(f"report_{category}.json")
        if report_file.exists():
            with open(report_file) as f:
                report = json.load(f)
            
            # Analyze each test
            category_results = {
                "category": category,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "duration": total_duration,
                "tests": [],
                "suspicious": []
            }
            
            for test in report.get("tests", []):
                test_name = test["nodeid"].split("::")[-1]
                duration = test.get("duration", 0)
                outcome = test["outcome"]
                
                category_results["total"] += 1
                category_results[outcome] += 1
                
                # Skeptical analysis
                is_suspicious = self._analyze_test_skeptically(test_name, duration, outcome, category)
                
                test_info = {
                    "name": test_name,
                    "duration": duration,
                    "outcome": outcome,
                    "suspicious": is_suspicious
                }
                
                category_results["tests"].append(test_info)
                if is_suspicious:
                    category_results["suspicious"].append(test_name)
                    self.suspicious_tests.append(f"{category}/{test_name}")
                elif outcome == "passed" and duration > 0.05:
                    self.verified_real_tests.append(f"{category}/{test_name}")
            
            return category_results
        else:
            # No JSON report - parse stdout
            return self._parse_stdout_results(result.stdout, category)
    
    def _analyze_test_skeptically(self, test_name: str, duration: float, outcome: str, category: str) -> bool:
        """Analyze test with extreme skepticism."""
        suspicious = False
        
        # Duration-based skepticism
        if category in ["integration", "e2e"]:
            if outcome == "passed" and duration < 0.05:
                logger.warning(f"⚠️  {test_name}: Suspiciously fast for {category} test ({duration:.3f}s)")
                suspicious = True
        
        # Pattern-based skepticism
        suspicious_patterns = ["mock", "fake", "stub", "dummy"]
        for pattern in suspicious_patterns:
            if pattern in test_name.lower():
                logger.warning(f"⚠️  {test_name}: Suspicious name pattern '{pattern}'")
                suspicious = True
        
        # Zero duration is always suspicious
        if duration == 0.0 and outcome == "passed":
            logger.error(f"❌ {test_name}: Zero duration - definitely mocked!")
            suspicious = True
        
        return suspicious
    
    def _parse_stdout_results(self, stdout: str, category: str) -> Dict[str, Any]:
        """Parse test results from stdout when JSON report fails."""
        lines = stdout.split('\n')
        results = {
            "category": category,
            "total": 0,
            "passed": stdout.count(" PASSED"),
            "failed": stdout.count(" FAILED"),
            "skipped": stdout.count(" SKIPPED"),
            "tests": []
        }
        results["total"] = results["passed"] + results["failed"] + results["skipped"]
        return results
    
    def verify_honeypots(self) -> bool:
        """Verify honeypot tests are failing correctly."""
        logger.info("\n🍯 Verifying honeypot tests...")
        
        result = subprocess.run([
            "python", "-m", "pytest",
            "tests/validation/test_honeypot.py",
            "-v", "-m", "honeypot"
        ], capture_output=True, text=True)
        
        # All honeypots should fail
        if result.returncode == 0:
            logger.error("❌ CRITICAL: Honeypot tests passed - framework is compromised!")
            return False
        
        failed_count = result.stdout.count(" FAILED")
        logger.success(f"✅ {failed_count} honeypot tests correctly failed")
        return True
    
    def check_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are available."""
        api_keys = {
            "OPENAI_API_KEY": False,
            "ANTHROPIC_API_KEY": False,
            "GEMINI_API_KEY": False,
            "GOOGLE_API_KEY": False
        }
        
        for key in api_keys:
            value = os.environ.get(key)
            api_keys[key] = bool(value and len(value) > 10)
        
        return api_keys
    
    def generate_skeptical_report(self, all_results: List[Dict[str, Any]]) -> str:
        """Generate a highly skeptical test report."""
        report = f"""# SKEPTICAL TEST VERIFICATION REPORT

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Framework: llm_call
Skepticism Level: MAXIMUM

## 🔍 Pre-Flight Checks

### API Keys Available:
"""
        api_keys = self.check_api_keys()
        for key, available in api_keys.items():
            status = "✅" if available else "❌"
            report += f"- {status} {key}: {'Available' if available else 'NOT SET'}\n"
        
        report += "\n### Honeypot Verification:\n"
        honeypot_ok = self.verify_honeypots()
        if honeypot_ok:
            report += "✅ All honeypot tests correctly failed\n"
        else:
            report += "❌ CRITICAL: Honeypot tests compromised!\n"
        
        report += f"\n## 📊 Test Results by Category\n\n"
        
        for result in all_results:
            if "error" in result:
                continue
                
            category = result["category"]
            report += f"\n### {category.upper()} Tests\n"
            report += f"- Total: {result['total']}\n"
            report += f"- Passed: {result['passed']}\n"
            report += f"- Failed: {result['failed']}\n"
            report += f"- Skipped: {result.get('skipped', 0)}\n"
            report += f"- Duration: {result.get('duration', 0):.2f}s\n"
            
            if result.get("suspicious"):
                report += f"\n⚠️  **SUSPICIOUS TESTS DETECTED:**\n"
                for test in result["suspicious"]:
                    report += f"- {test}\n"
        
        report += f"\n## 🚨 Skeptical Analysis\n\n"
        
        # Summary of suspicious findings
        if self.suspicious_tests:
            report += f"### Suspicious Tests ({len(self.suspicious_tests)}):\n"
            for test in self.suspicious_tests:
                report += f"- {test}\n"
        
        if self.verified_real_tests:
            report += f"\n### Verified Real Tests ({len(self.verified_real_tests)}):\n"
            for test in self.verified_real_tests[:5]:  # Show first 5
                report += f"- {test}\n"
            if len(self.verified_real_tests) > 5:
                report += f"- ... and {len(self.verified_real_tests) - 5} more\n"
        
        # Final verdict
        report += "\n## 🎯 FINAL VERDICT\n\n"
        
        real_test_ratio = len(self.verified_real_tests) / max(1, len(self.verified_real_tests) + len(self.suspicious_tests))
        
        if real_test_ratio > 0.9 and honeypot_ok and not self.suspicious_tests:
            report += "✅ **TESTS APPEAR LEGITIMATE**\n"
            report += f"- {len(self.verified_real_tests)} tests show real API interaction\n"
            report += "- Honeypots functioning correctly\n"
            report += "- No suspicious patterns detected\n"
        else:
            report += "❌ **TESTS ARE QUESTIONABLE**\n"
            report += f"- Only {real_test_ratio*100:.1f}% of tests verified as real\n"
            report += f"- {len(self.suspicious_tests)} suspicious tests found\n"
            if not honeypot_ok:
                report += "- Honeypot tests are compromised!\n"
        
        return report
    
    def run_full_verification(self):
        """Run complete test verification."""
        categories = ["smoke", "unit", "integration", "validation", "e2e"]
        all_results = []
        
        # Check environment first
        logger.info("Checking Python environment...")
        python_version = sys.version.split()[0]
        logger.info(f"Python: {python_version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Run each category
        for category in categories:
            try:
                result = self.run_test_category(category)
                all_results.append(result)
                
                if "error" not in result:
                    self.total_passed += result["passed"]
                    self.total_failed += result["failed"]
            except Exception as e:
                logger.error(f"Failed to run {category} tests: {e}")
                all_results.append({"category": category, "error": str(e)})
        
        # Generate report
        report = self.generate_skeptical_report(all_results)
        
        # Save report
        report_path = Path(f"docs/reports/skeptical_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        report_path.parent.mkdir(exist_ok=True, parents=True)
        report_path.write_text(report)
        
        # Display summary
        logger.info("\n" + "="*60)
        logger.info("VERIFICATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Total tests run: {self.total_passed + self.total_failed}")
        logger.info(f"Passed: {self.total_passed}")
        logger.info(f"Failed: {self.total_failed}")
        logger.info(f"Suspicious: {len(self.suspicious_tests)}")
        logger.info(f"Verified real: {len(self.verified_real_tests)}")
        logger.info(f"\nReport saved to: {report_path}")
        
        # Return exit code
        if self.total_failed > 0 or len(self.suspicious_tests) > len(self.verified_real_tests):
            return 1
        return 0


if __name__ == "__main__":
    verifier = SkepticalTestVerifier()
    exit_code = verifier.run_full_verification()
    sys.exit(exit_code)