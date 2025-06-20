#!/usr/bin/env python3
"""Verify the dashboard is actually working by checking its content."""

import subprocess
import json
from pathlib import Path

if __name__ == "__main__":
    # URLs to check
    dashboards = {
        "test_minimal.html": "Simple test page",
        "verification_dashboard_final.html": "Final dashboard with 2025 styles",
        "verification_dashboard_working.html": "Working dashboard with lucide fix"
    }
    
    for filename, description in dashboards.items():
        print(f"\n{'='*60}")
        print(f"Checking: {filename}")
        print(f"Description: {description}")
        print('='*60)
        
        # Fetch the page
        url = f"http://localhost:9999/{filename}"
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Failed to fetch {url}")
            continue
            
        content = result.stdout
        
        # Check basic structure
        print("\n1. Basic HTML Structure:")
        print(f"   - Has <html>: {'✅' if '<html' in content else '❌'}")
        print(f"   - Has <body>: {'✅' if '<body' in content else '❌'}")
        print(f"   - Has <div id='root'>: {'✅' if 'id="root"' in content else '❌'}")
        
        # Check React setup
        print("\n2. React Setup:")
        print(f"   - React script: {'✅' if 'react.production.min.js' in content else '❌'}")
        print(f"   - ReactDOM script: {'✅' if 'react-dom.production.min.js' in content else '❌'}")
        print(f"   - Babel script: {'✅' if '@babel/standalone' in content else '❌'}")
        print(f"   - Lucide icons: {'✅' if 'lucide' in content else '❌'}")
        
        # Check test data
        print("\n3. Test Data:")
        has_test_data = 'const testData' in content
        print(f"   - Has testData: {'✅' if has_test_data else '❌'}")
        if has_test_data:
            # Count test items
            test_count = content.count('"id":')
            interface_count = content.count('"interface":')
            print(f"   - Test categories: {test_count}")
            print(f"   - Total interfaces: {interface_count}")
        
        # Check for React components
        print("\n4. React Components:")
        print(f"   - useState hook: {'✅' if 'useState' in content else '❌'}")
        print(f"   - ReactDOM.render: {'✅' if 'ReactDOM.render' in content or 'ReactDOM.createRoot' in content else '❌'}")
        print(f"   - Component defined: {'✅' if 'function App' in content or 'function Dashboard' in content else '❌'}")
        
        # Check 2025 styling
        print("\n5. 2025 Style Guide:")
        has_2025_styles = any(style in content for style in ['#4F46E5', 'Inter', '--color-primary-start'])
        print(f"   - 2025 colors: {'✅' if has_2025_styles else '❌'}")
        
        # Check for potential issues
        print("\n6. Potential Issues:")
        if 'lucide.icons' in content:
            print("   - ⚠️  Found 'lucide.icons' - should be just 'lucide'")
        if '<script type="text/babel">' not in content:
            print("   - ⚠️  Missing Babel script type")
        if 'testData =' in content and 'testData = [' not in content:
            print("   - ⚠️  testData might not be properly formatted")
            
    print("\n" + "="*60)
    print("💡 Debugging tips:")
    print("1. Open http://localhost:9999/{dashboard} in browser")
    print("2. Open Developer Console (F12)")
    print("3. Check Console tab for JavaScript errors")
    print("4. Check Network tab for failed resource loads")
    print("5. Try the minimal test page first to isolate issues")