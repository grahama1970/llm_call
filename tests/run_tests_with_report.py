#!/usr/bin/env python3
"""Run tests with automatic Markdown report generation."""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_tests_with_report(test_path=None, extra_args=None):
    """Run pytest with markdown report generation.
    
    Args:
        test_path: Specific test path to run (default: all tests)
        extra_args: Additional pytest arguments
    """
    # Base pytest command
    cmd = ["uv", "run", "pytest"]
    
    # Add test path if specified
    if test_path:
        cmd.append(test_path)
    
    # Add default arguments
    cmd.extend([
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--no-header",  # No pytest header
    ])
    
    # Add any extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    
    print(f"🧪 Running tests with report generation...")
    print(f"📁 Project root: {project_root}")
    print(f"🔧 Command: {' '.join(cmd)}")
    print("-" * 80)
    
    # Run tests
    result = subprocess.run(cmd, cwd=project_root)
    
    # Check if report was generated
    reports_dir = project_root / "docs" / "reports"
    latest_report = reports_dir / "test_report_latest.md"
    
    if latest_report.exists():
        print("\n" + "=" * 80)
        print(f"✅ Test report generated: {latest_report}")
        print(f"📊 View the latest report: {latest_report.resolve()}")
        
        # Show summary from report
        with open(latest_report, 'r') as f:
            lines = f.readlines()
            in_summary = False
            for line in lines:
                if line.strip() == "## Summary":
                    in_summary = True
                elif line.strip().startswith("##") and in_summary:
                    break
                elif in_summary and line.strip():
                    print(f"   {line.strip()}")
    
    return result.returncode


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests with Markdown report generation")
    parser.add_argument("test_path", nargs="?", help="Specific test path to run")
    parser.add_argument("--cov", action="store_true", help="Run with coverage")
    parser.add_argument("--markers", "-m", help="Run tests matching given mark expression")
    parser.add_argument("--keyword", "-k", help="Run tests matching given keyword expression")
    
    args, unknown = parser.parse_known_args()
    
    # Build extra arguments
    extra_args = []
    if args.cov:
        extra_args.extend(["--cov=src/llm_call", "--cov-report=term-missing"])
    if args.markers:
        extra_args.extend(["-m", args.markers])
    if args.keyword:
        extra_args.extend(["-k", args.keyword])
    
    # Add any unknown arguments
    extra_args.extend(unknown)
    
    # Run tests
    exit_code = run_tests_with_report(args.test_path, extra_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()