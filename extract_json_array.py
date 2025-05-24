#!/usr/bin/env python3
"""Extract and validate JSON array from test_prompts.json."""

import json
import re

# Read the file
with open('src/llm_call/proof_of_concept/v4_claude_validator/test_prompts.json', 'r') as f:
    content = f.read()

# Find the JSON array start
array_start = content.find('[')
if array_start == -1:
    print("❌ No JSON array found")
    exit(1)

# Extract from array start
json_content = content[array_start:]

# Remove comments more aggressively
# Remove single-line comments
json_content = re.sub(r'//.*?(?=\n|$)', '', json_content)
# Remove multi-line comments
json_content = re.sub(r'/\*.*?\*/', '', json_content, flags=re.DOTALL)

# Fix common JSON issues
# Remove trailing commas
json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)

# Replace any control characters
json_content = re.sub(r'[\x00-\x1f\x7f]', ' ', json_content)

# Try to find where the JSON might be broken
try:
    data = json.loads(json_content)
    print(f"✅ Successfully parsed {len(data)} test cases")
    
    # Save the clean JSON
    with open('test_prompts_fixed.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("✅ Saved to test_prompts_fixed.json")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON error: {e}")
    
    # Try to find the problem area
    lines = json_content.split('\n')
    if e.lineno and e.lineno <= len(lines):
        print(f"\nProblem around line {e.lineno}:")
        start = max(0, e.lineno - 3)
        end = min(len(lines), e.lineno + 2)
        for i in range(start, end):
            marker = ">>> " if i == e.lineno - 1 else "    "
            print(f"{marker}{i+1:4d}: {lines[i][:100]}...")