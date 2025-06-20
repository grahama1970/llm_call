#!/usr/bin/env python3
"""
Get Gemini's feedback on our test results and approach.
"""
import os
from pathlib import Path
from litellm import completion

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

# Read test results summary
summary = Path("test_results_summary.md").read_text()

# Read a sample test file
sample_test = Path("tests/local/critical/test_minimal_improved.py").read_text()[:2000]

prompt = f"""Review these test results for an LLM API wrapper called llm_call:

{summary}

Here's a sample of our test code:
```python
{sample_test}
```

Please provide:
1. Grade (A-F) for overall test coverage and quality
2. Are we testing the right things for an LLM API wrapper?
3. What critical tests are we missing?
4. Are our fixes (exception handling, import system) appropriate?
5. How should we handle the Vertex AI path issue?
6. Any other concerns or suggestions?

Be critical and thorough."""

response = completion(
    model="gemini/gemini-2.0-flash-exp",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1
)

if response and hasattr(response, 'choices'):
    content = response.choices[0].message.content
    print("GEMINI FEEDBACK ON TEST RESULTS:")
    print("="*80)
    print(content)
    print("="*80)
    
    # Save feedback
    with open("gemini_test_feedback.md", "w") as f:
        f.write(f"# Gemini Test Feedback\n\n{content}")
else:
    print("Error: No response from Gemini")