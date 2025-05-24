#!/usr/bin/env python3
"""Fix JSON control character issues."""

import json
import re

# Read the file
with open('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts.json', 'r') as f:
    content = f.read()

# Remove any control characters (except newlines, tabs, etc.)
cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', content)

# Try to parse it
try:
    data = json.loads(cleaned)
    print(f"✅ Successfully parsed JSON with {len(data)} test cases")
    
    # Write the cleaned version back
    with open('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("✅ Wrote cleaned JSON back to file")
    
except json.JSONDecodeError as e:
    print(f"❌ Still has JSON error: {e}")
    # Show the area around the error
    lines = cleaned.split('\n')
    error_line = e.lineno - 1
    print(f"\nLines around error (line {e.lineno}):")
    for i in range(max(0, error_line - 2), min(len(lines), error_line + 3)):
        print(f"{i+1:4d}: {lines[i]}")