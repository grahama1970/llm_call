#!/usr/bin/env python3
"""Open the verification dashboard in the default browser."""

import webbrowser
import subprocess
import time

if __name__ == "__main__":
    # Ensure server is running
    subprocess.Popen(["python", "-m", "http.server", "9999"], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
    
    time.sleep(1)  # Give server time to start
    
    url = "http://localhost:9999/verification_dashboard_final.html"
    print(f"Opening dashboard at: {url}")
    print("\nWhat to check:")
    print("1. Open Developer Console (F12)")
    print("2. Check Console tab for JavaScript errors")
    print("3. Look for:")
    print("   - 'lucide is not defined' errors")
    print("   - React rendering errors")
    print("   - Missing resource errors")
    
    webbrowser.open(url)
    
    print("\n✅ Dashboard opened in browser")
    print("📋 The dashboard should show:")
    print("   - LLM Call Verification Dashboard header")
    print("   - Summary cards with test statistics")
    print("   - 12 test categories (expandable)")
    print("   - 2025 style guide applied")