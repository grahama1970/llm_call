#!/usr/bin/env python3
"""
Simple direct Vertex AI call - no complexity
"""

import sys
sys.path.insert(0, './src')

from llm_call.api import ask_sync

# Simple test
response = ask_sync(
    prompt="Say hello",
    model="vertex_ai/gemini-2.5-flash-preview-05-20"
)

print(f"Response: {response}")
print(f"Type: {type(response)}")