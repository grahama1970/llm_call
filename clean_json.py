#!/usr/bin/env python3
"""Remove comments and fix JSON."""

import re
import json

# Read the file starting from line 14
with open('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts.json', 'r') as f:
    lines = f.readlines()
    content = ''.join(lines[13:])  # Start from line 14 (0-indexed)

# Remove single-line comments (// ...)
content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

# Remove multi-line comments (/* ... */)
content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

# Remove trailing commas before closing brackets/braces
content = re.sub(r',(\s*[}\]])', r'\1', content)

# Try to parse it
try:
    data = json.loads(content)
    print(f"✅ Successfully parsed JSON with {len(data)} test cases")
    
    # Write the cleaned version
    with open('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts_clean.json', 'w') as f:
        json.dump(data, f, indent=4)
    print("✅ Wrote cleaned JSON to test_prompts_clean.json")
    
    # Show first test case
    print(f"\nFirst test case: {data[0]['test_case_id']}")
    
except json.JSONDecodeError as e:
    print(f"❌ Still has JSON error: {e}")
    # Show the area around the error
    lines = content.split('\n')
    error_line = e.lineno - 1
    print(f"\nLines around error (line {e.lineno}):")
    for i in range(max(0, error_line - 2), min(len(lines), error_line + 3)):
        print(f"{i+1:4d}: {lines[i]}")