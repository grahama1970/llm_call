#!/usr/bin/env python3
"""
Proper Gemini critique of the verification script
"""

import sys
sys.path.insert(0, './src')

from llm_call.api import ask_sync

# Read the actual verification script
with open('verification_experiments/proper_verification.py', 'r') as f:
    script_content = f.read()

# Create a focused prompt with the actual code
prompt = f"""Please critique this verification script that attempts to detect when Claude Code fakes test results:

```python
{script_content}
```

Specifically address:
1. The effectiveness of using Ollama with qwen2.5:32b for detecting fake implementations
2. The quality and coverage of the test cases in the main() function
3. Edge cases this approach might miss
4. The concurrent execution implementation
5. Any security or reliability concerns

Be direct and technical in your critique."""

print("Asking Gemini for critique...")
response = ask_sync(
    prompt=prompt,
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    temperature=0.7
)

if response:
    print("\n" + "="*80)
    print("GEMINI CRITIQUE:")
    print("="*80)
    print(response)
else:
    print("Gemini returned None - possibly due to prompt length")