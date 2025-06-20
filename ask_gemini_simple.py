#!/usr/bin/env python3
"""
Ask Gemini a simple question about the verification approach
"""

import sys
sys.path.insert(0, './src')

from llm_call.api import ask_sync

prompt = """Is using Ollama with qwen2.5:32b a good approach for detecting when Claude Code fakes test results by just printing success messages without implementing actual logic?"""

print("Asking Gemini...")
response = ask_sync(
    prompt=prompt,
    model="vertex_ai/gemini-2.5-flash-preview-05-20"
)

if response is None:
    print("Gemini returned None")
else:
    print(f"\nGemini says: {response}")