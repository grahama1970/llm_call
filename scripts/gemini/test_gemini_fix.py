#!/usr/bin/env python3
"""
Test Gemini without thinking tokens.
"""
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

import litellm
from litellm import completion

# Test 1: Default call (might use thinking)
print("Test 1: Default Gemini call")
response1 = completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    messages=[{"role": "user", "content": "What is 2+2? Answer in one word."}],
    temperature=0
)

print(f"Content: {response1.choices[0].message.content}")
print(f"Usage: {response1.usage}")
print(f"Reasoning tokens: {getattr(response1.usage.completion_tokens_details, 'reasoning_tokens', 0)}")
print()

# Test 2: With explicit thinking disabled
print("Test 2: Explicitly disable thinking")
# According to Perplexity, we should not include thinking parameter
response2 = completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20", 
    messages=[{"role": "user", "content": "What is 2+2? Answer in one word."}],
    temperature=0,
    # No thinking parameter = disabled
)

print(f"Content: {response2.choices[0].message.content}")
print(f"Usage: {response2.usage}")
print(f"Reasoning tokens: {getattr(response2.usage.completion_tokens_details, 'reasoning_tokens', 0)}")