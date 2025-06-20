#!/usr/bin/env python3
"""
Final comprehensive test grading.
"""
import json
import httpx
import os
from litellm import completion

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

# Load test results
with open("complete_test_results.json") as f:
    test_results = json.load(f)

# Create the grading prompt directly
prompt = """Grade these LLM test results strictly.

GRADING RULES:
1. PASS only if actual response satisfies the expected requirement
2. "Exactly 5 languages with descriptions" means BOTH 5 languages AND descriptions
3. "Valid Python function" allows extra explanation
4. Minor formatting differences (spaces, punctuation) are acceptable

TEST RESULTS:
"""

for test in test_results:
    prompt += f"""
Test {test['test_id']}:
- Command: {test['command']}
- Model: {test['model']}
- Expected: {test['expected']}
- Actual Response:
{test['actual_response']}
---
"""

prompt += """

Fill in this table:

| Test ID | Grade | Critique |
|---------|-------|----------|

Grade = PASS/FAIL
Critique = What specifically passed/failed (max 20 words)
"""

print("Sending complete results to Gemini...")
print(f"Prompt length: {len(prompt)} chars")

# Send to Gemini with thinking
response = completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    extra_body={
        "thinking": {
            "type": "medium",
            "budget_tokens": 2048
        }
    }
)

content = response.choices[0].message.content
usage = response.usage

print(f"\nThinking tokens: {getattr(usage.completion_tokens_details, 'reasoning_tokens', 0)}")
print(f"Text tokens: {getattr(usage.completion_tokens_details, 'text_tokens', 0)}")

if content:
    print("\nFINAL GEMINI GRADING:")
    print("="*80)
    print(content)
    print("="*80)
    
    # Save final results
    final_report = {
        "graded_by": "vertex_ai/gemini-2.5-flash-preview-05-20",
        "thinking_tokens": getattr(usage.completion_tokens_details, 'reasoning_tokens', 0),
        "test_results": test_results,
        "grading_table": content
    }
    
    with open("final_test_grading.json", "w") as f:
        json.dump(final_report, f, indent=2)
    
    print("\nSaved complete grading to final_test_grading.json")
else:
    print("ERROR: Gemini returned null content")