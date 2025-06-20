#!/usr/bin/env python3
"""
Send test report to Gemini with medium thinking for grading.
"""
import json
import litellm
from litellm import completion
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

# Load the test results
with open("complete_test_results.json") as f:
    test_results = json.load(f)

# Create grading prompt
prompt = """Analyze these test results and fill in a markdown table with grades and concise critiques.

TEST RESULTS:
"""

for test in test_results:
    prompt += f"""
Test {test['test_id']}:
- Command: {test['command']}
- Model: {test['model']}
- Expected: {test['expected']}
- Actual Response: {test['actual_response']}
---
"""

prompt += """

Create this markdown table with your analysis:

| Test ID | Command | Model | Expected | Grade | Critique |
|---------|---------|-------|----------|-------|----------|

Where:
- Grade: PASS or FAIL based on whether actual matches expected
- Critique: Concise explanation (max 15 words)

Focus on whether the actual response satisfies the expected output."""

print("Sending to Gemini with medium thinking...")

# Call with medium thinking
response = completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    thinking={
        "type": "medium",
        "budget_tokens": 2048
    }
    # NO max_tokens limit!
)

content = response.choices[0].message.content
usage = response.usage

print(f"\nThinking tokens used: {getattr(usage.completion_tokens_details, 'reasoning_tokens', 0)}")
print(f"Text tokens: {getattr(usage.completion_tokens_details, 'text_tokens', 0)}")
print(f"Total completion tokens: {usage.completion_tokens}")

if content:
    print("\nGEMINI GRADING WITH MEDIUM THINKING:")
    print("="*80)
    print(content)
    
    # Save the graded table
    with open("gemini_graded_table.md", "w") as f:
        f.write("# Gemini Test Grading (Medium Thinking)\n\n")
        f.write(content)
else:
    print("\nERROR: Gemini returned null content")
    print(f"Full response: {response}")