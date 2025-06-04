#!/usr/bin/env python3
"""Test the test reporting engine setup."""

import subprocess
import sys
from pathlib import Path
import json

def test_reporting_engine():
    """Test that the reporting engine is properly configured."""
    project_root = Path(__file__).parent.parent
    
    print("🧪 Testing the test reporting engine...")
    print(f"📁 Project root: {project_root}")
    
    # Run a simple test with the reporting engine
    cmd = [
        "uv", "run", "pytest",
        "-v",
        "--json-report",
        "--json-report-file=test_results.json",
        "--json-report-indent=2",
        "-k", "test_basic",
        "--tb=short"
    ]
    
    print(f"🔧 Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)
    
    print("\n--- STDOUT ---")
    print(result.stdout)
    print("\n--- STDERR ---")
    print(result.stderr)
    
    # Check if JSON report was created
    json_report = project_root / "test_results.json"
    if json_report.exists():
        print(f"\n✅ JSON report created: {json_report}")
        
        # Load and display summary
        with open(json_report) as f:
            data = json.load(f)
            summary = data.get('summary', {})
            print(f"\n📊 Test Summary:")
            print(f"  - Total: {summary.get('total', 0)}")
            print(f"  - Passed: {summary.get('passed', 0)}")
            print(f"  - Failed: {summary.get('failed', 0)}")
            print(f"  - Duration: {summary.get('duration', 0):.2f}s")
    else:
        print(f"\n❌ JSON report not created!")
        return 1
    
    # Check if markdown report was created
    md_report = project_root / "docs" / "reports" / "test_report_latest.md"
    if md_report.exists():
        print(f"\n✅ Markdown report created: {md_report}")
    else:
        print(f"\n⚠️  Markdown report not found at: {md_report}")
        print("   (This may be normal if no tests ran successfully)")
    
    # Check test reports directory
    test_reports_dir = project_root / "test_reports"
    if test_reports_dir.exists():
        reports = list(test_reports_dir.glob("*.md")) + list(test_reports_dir.glob("*.json"))
        if reports:
            print(f"\n✅ Test reports directory has {len(reports)} files")
            for report in reports[:5]:  # Show first 5
                print(f"   - {report.name}")
    
    return 0

if __name__ == "__main__":
    sys.exit(test_reporting_engine())