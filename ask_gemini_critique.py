#!/usr/bin/env python3
"""
Ask Gemini to critique the verification script
"""

import sys
sys.path.insert(0, './src')

from llm_call.api import ask_sync

# Read the verification script
with open('verification_experiments/proper_verification.py', 'r') as f:
    script_content = f.read()

prompt = f"""Please critique this verification approach for detecting when Claude Code fakes test results:

{script_content[:8000]}

The key questions:
1. Is using Ollama with qwen2.5:32b a good approach for detecting fake implementations?
2. Is checking CLAUDE.md rule compliance useful for catching violations?
3. What improvements would you suggest to make this more reliable?
4. Are there any edge cases this approach might miss?
5. Is the concurrent execution properly implemented?

Please provide a thorough technical critique."""

print("Asking Gemini to critique the verification approach...")
response = ask_sync(
    prompt=prompt,
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    temperature=0.7
)

print("\n" + "="*80)
print("GEMINI CRITIQUE:")
print("="*80)
print(response)