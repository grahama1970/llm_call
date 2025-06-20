#!/usr/bin/env python3
"""
Send test report to Gemini with proper context for informed grading.
"""
import json
import litellm
from litellm import completion
import os
from pathlib import Path

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

# Load test results
with open("complete_test_results.json") as f:
    test_results = json.load(f)

# Load relevant context
readme_path = Path("/home/graham/workspace/experiments/llm_call/README.md")
matrix_path = Path("/home/graham/workspace/experiments/llm_call/LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md")

context_sections = []

# Add README context
if readme_path.exists():
    with open(readme_path) as f:
        readme = f.read()
    context_sections.append(f"## Project README (excerpt):\n{readme[:1000]}...")

# Add test matrix context
if matrix_path.exists():
    with open(matrix_path) as f:
        matrix = f.read()
    # Extract just the test definitions
    matrix_lines = matrix.split('\n')
    test_section = []
    capturing = False
    for line in matrix_lines:
        if "| Test ID | Priority | Command |" in line:
            capturing = True
        if capturing and line.strip() and not line.startswith('#'):
            test_section.append(line)
        if capturing and line.strip() == "" and len(test_section) > 5:
            break
    context_sections.append("## Test Matrix Definitions:\n" + "\n".join(test_section[:20]))

# Create informed prompt
prompt = f"""You are grading test results for llm_call, a universal LLM interface that uses LiteLLM.

IMPORTANT CONTEXT:
- This project wraps multiple LLM providers (OpenAI, Anthropic, Google, etc.) through LiteLLM
- Different models may format responses differently (e.g., GPT often adds explanations)
- The test matrix defines strict expectations for each test

{"".join(context_sections)}

GRADING GUIDELINES:
1. Be STRICT about matching expected outputs
2. If expected says "with descriptions", the response MUST have descriptions
3. If expected says "Valid Python function", extra explanation is acceptable
4. Minor formatting differences (spaces, punctuation) are acceptable if core content matches
5. Consider how LiteLLM might affect response formatting

TEST RESULTS TO GRADE:
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

| Test ID | Grade | Critique | Reasoning |
|---------|-------|----------|-----------|

Where:
- Grade: PASS or FAIL
- Critique: What specifically passed/failed (max 15 words)
- Reasoning: Why you made this decision (max 20 words)

Be strict but fair, considering LiteLLM response patterns."""

print("Sending to Gemini with full context...")
print(f"Prompt length: {len(prompt)} chars")

# Call with medium thinking
response = completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,
    thinking={
        "type": "medium",
        "budget_tokens": 2048
    }
)

content = response.choices[0].message.content
usage = response.usage

print(f"\nThinking tokens: {getattr(usage.completion_tokens_details, 'reasoning_tokens', 0)}")
print(f"Text tokens: {getattr(usage.completion_tokens_details, 'text_tokens', 0)}")

if content:
    print("\nGEMINI INFORMED GRADING:")
    print("="*80)
    print(content)
    
    with open("gemini_informed_grading.md", "w") as f:
        f.write("# Gemini Informed Test Grading\n\n")
        f.write("Graded with project context and LiteLLM understanding\n\n")
        f.write(content)
else:
    print("ERROR: Null content")