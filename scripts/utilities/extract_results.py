#!/usr/bin/env python3
"""Extract Gemini verification results from HTML report."""

import re
import json
from pathlib import Path

html_file = Path("verification_dashboard.html")
content = html_file.read_text()

# Find JSON in the HTML
json_pattern = r'<pre[^>]*>({[^<]+})</pre>'
matches = re.findall(json_pattern, content, re.DOTALL)

for match in matches:
    try:
        data = json.loads(match)
        if 'verdict' in data and 'totalFeaturesDocumented' in data:
            print("GEMINI VERIFICATION RESULTS:")
            print("=" * 70)
            print(json.dumps(data, indent=2))
            break
    except:
        continue

# Also extract summary stats
summary_pattern = r'<h3>Summary Statistics</h3>(.*?)</div>'
summary_match = re.search(summary_pattern, content, re.DOTALL)
if summary_match:
    print("\n\nSUMMARY STATISTICS:")
    print("=" * 70)
    # Extract key numbers
    text = summary_match.group(1)
    numbers = re.findall(r'<strong>([^<]+)</strong>: ([^<]+)', text)
    for label, value in numbers:
        print(f"{label}: {value}")