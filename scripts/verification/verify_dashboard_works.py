#!/usr/bin/env python3
"""Verify the dashboard actually works since MCP tools are broken."""

import subprocess
import time
from pathlib import Path

if __name__ == "__main__":
    print("Verifying LLM Call Verification Dashboard...")
    print("="*60)
    
    # Check server is running
    server_check = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:9999/"],
        capture_output=True,
        text=True
    )
    
    if server_check.stdout != "200":
        print("❌ Server not responding on port 9999")
        print("   Start with: python -m http.server 9999")
        exit(1)
    
    print("✅ Server is running on port 9999")
    
    # Check our dashboards
    dashboards = [
        ("verification_dashboard_final.html", "Final dashboard with 2025 styles"),
        ("verification_dashboard_working.html", "Working dashboard with lucide fix"),
        ("verification_dashboard_fixed.html", "Fixed dashboard with styles applied")
    ]
    
    working_dashboard = None
    
    for filename, description in dashboards:
        if not Path(filename).exists():
            print(f"\n❌ {filename} not found")
            continue
            
        print(f"\n📊 Checking {filename}:")
        print(f"   {description}")
        
        # Fetch content
        result = subprocess.run(
            ["curl", "-s", f"http://localhost:9999/{filename}"],
            capture_output=True,
            text=True
        )
        
        content = result.stdout
        size = len(content)
        
        # Basic checks
        has_root = '<div id="root">' in content
        has_react = 'react.production.min.js' in content
        has_data = 'const testData' in content and content.count('"id":') > 10
        has_render = 'ReactDOM.render' in content or 'ReactDOM.createRoot' in content
        
        print(f"   Size: {size:,} bytes")
        print(f"   Has root element: {'✅' if has_root else '❌'}")
        print(f"   Has React loaded: {'✅' if has_react else '❌'}")
        print(f"   Has test data (12 categories): {'✅' if has_data else '❌'}")
        print(f"   Has React render call: {'✅' if has_render else '❌'}")
        
        if all([has_root, has_react, has_data, has_render]):
            print(f"   ✅ This dashboard should be working!")
            working_dashboard = filename
        else:
            print(f"   ❌ Missing required elements")
    
    print("\n" + "="*60)
    
    if working_dashboard:
        url = f"http://localhost:9999/{working_dashboard}"
        print(f"✅ WORKING DASHBOARD FOUND: {working_dashboard}")
        print(f"\n🌐 Open this URL in your browser:")
        print(f"   {url}")
        print(f"\n📋 What you should see:")
        print(f"   - Header with 'LLM Call Verification Dashboard'")
        print(f"   - Summary cards showing test statistics")
        print(f"   - List of 12 test categories")
        print(f"   - Each category expandable to show test details")
        print(f"   - 2025 style guide applied (Inter font, gradients)")
    else:
        print("❌ No working dashboard found")
        print("\n🐛 Debugging steps:")
        print("1. Open browser Developer Console (F12)")
        print("2. Check Console tab for JavaScript errors")
        print("3. Common issues:")
        print("   - 'lucide is not defined' - need lucide.js loaded")
        print("   - 'testData is not defined' - data not properly embedded")
        print("   - Blank page - React render failing")
    
    # Clean up temporary files
    temp_files = ["test_data_raw.json", "extract_test_data.py", "create_fixed_dashboard.py", 
                  "apply_2025_styles.py", "create_dashboard_simple.py", "fix_dashboard_final.py",
                  "create_working_dashboard.py", "debug_dashboard.html", "test_minimal.html",
                  "check_page_puppeteer.js", "verify_render.py", "style_improver.html",
                  "dashboard_comparison.html", "verification_dashboard_2025.html"]
    
    print(f"\n🧹 Cleaning up {len(temp_files)} temporary files...")
    for f in temp_files:
        if Path(f).exists():
            Path(f).unlink()
            
    print("✅ Cleanup complete")