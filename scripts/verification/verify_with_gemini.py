#!/usr/bin/env python3
"""
Verify test results with Gemini to ensure no fabrication.
"""
import os
import subprocess
from pathlib import Path
from litellm import completion

# Set up Vertex AI credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

print("Running actual tests to get real results...")
# Run the actual tests and capture output
result = subprocess.run(
    ["python", "-m", "pytest", "tests/local/critical/", "-v", "--tb=short"],
    capture_output=True,
    text=True,
    cwd="/home/graham/workspace/experiments/llm_call"
)

# Extract key information from test output
test_output = result.stdout + result.stderr
lines = test_output.split('\n')

# Find the summary line
summary_line = None
for line in lines:
    if "failed" in line and "passed" in line:
        summary_line = line
        break

print(f"\nActual Test Summary: {summary_line}")

# Read the tables we created
test_table = Path("/home/graham/workspace/experiments/llm_call/test_results_table.md").read_text()

# Create verification prompt
prompt = f"""Please verify these test results for the llm_call project:

ACTUAL PYTEST OUTPUT SUMMARY:
{summary_line}

CLAIMED TEST RESULTS TABLE:
{test_table}

Please verify:
1. Do the numbers match between actual output and the table?
2. Are the test names and categories accurate?
3. Is this an honest representation of the test results?
4. What grade would you give this test suite now?
5. Is this system production-ready based on these results?

Be critical and point out any discrepancies."""

print("\nAsking Gemini to verify results...")
response = completion(
    model="gemini/gemini-2.0-flash-exp",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1
)

if response and hasattr(response, 'choices'):
    verification = response.choices[0].message.content
    print("\n" + "="*80)
    print("GEMINI VERIFICATION OF TEST RESULTS:")
    print("="*80)
    print(verification)
    print("="*80)
    
    # Save verification
    with open("gemini_test_verification.md", "w") as f:
        f.write(f"# Gemini Test Results Verification\n\n")
        f.write(f"## Actual pytest output:\n```\n{summary_line}\n```\n\n")
        f.write(f"## Gemini's Verification:\n\n{verification}")
else:
    print("Error: No response from Gemini")