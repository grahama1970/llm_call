#!/usr/bin/env python3
"""
Simple litellm call to Gemini for critique
"""

import litellm
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read the verification script
with open('verification_experiments/proper_verification.py', 'r') as f:
    script_content = f.read()

prompt = f"""Please critique this verification script that detects when Claude Code fakes test results:

```python
{script_content}
```

The results showed:
- Ollama with qwen2.5:32b achieved 100% accuracy detecting fake implementations
- Claude achieved 75% accuracy checking CLAUDE.md rule compliance
- Test cases include obvious fakes that just print "All tests passed!" and real implementations with actual logic

Given the code above, what are the main limitations and what edge cases might we miss?"""

# Make the call
response = litellm.completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    messages=[{"role": "user", "content": prompt}]
)

print("="*80)
print("GEMINI CRITIQUE:")
print("="*80)
print(response.choices[0].message.content)