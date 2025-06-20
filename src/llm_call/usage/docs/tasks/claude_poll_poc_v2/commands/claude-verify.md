# Claude Verify Command

Verify code execution results using Claude's analysis capabilities.

## Expected Output:
- Reads the provided code file and its output
- Performs verification against expected results
- Writes a JSON status file with the verification outcome
- Logs the verification process

## Parameters:
- `code_file`: (string) Path to the code file to verify
- `result_file`: (string) Path to the file containing execution results
- `status_file`: (string) Path where verification status JSON will be written
- `log_file`: (string) Path to the log file
- `expected_result`: (string) The expected string to find in the result file

## Code Example:
```python
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
from litellm import completion
import sys
import json
from datetime import datetime

# Parameters from orchestrator
code_file = "{{ params.code_file }}"
result_file = "{{ params.result_file }}"
status_file = "{{ params.status_file }}"
log_file = "{{ params.log_file }}"
expected_result = "{{ params.expected_result }}"

try:
    # Read the code and result files
    with open(code_file, 'r') as f:
        code_content = f.read()
    
    with open(result_file, 'r') as f:
        actual_result = f.read().strip()
    
    # Log the start of verification
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] Starting Claude verification\n")
    
    # Construct verification prompt
    verification_prompt = f"""Please verify the following Python code execution:

CODE:
```python
{code_content}
```

ACTUAL OUTPUT:
{actual_result}

EXPECTED: {expected_result}

Please analyze:
1. Does the code correctly implement the addition?
2. Does the actual output match the expected output?
3. Are there any potential issues with the code?

Respond with a JSON object containing:
- "status": "pass" or "fail"
- "reasoning": Brief explanation
- "issues": List of any issues found (empty list if none)
"""

    response = completion(
        model=os.getenv('SLASHCMD_CLAUDE_POLL_MODEL', 'anthropic/claude-3-5-sonnet-20241022'),
        messages=[{"role": "user", "content": verification_prompt}],
        temperature=0.1  # Low temperature for consistent verification
    )
    
    if response.choices and response.choices[0].message.content:
        # Parse Claude's response
        claude_response = response.choices[0].message.content
        
        # Extract JSON from response (Claude might wrap it in markdown)
        import re
        json_match = re.search(r'\{[^}]+\}', claude_response, re.DOTALL)
        if json_match:
            verification_result = json.loads(json_match.group())
        else:
            # Fallback: Create result based on simple checks
            if expected_result in actual_result:
                verification_result = {
                    "status": "pass",
                    "reasoning": f"Found expected result '{expected_result}' in output",
                    "issues": []
                }
            else:
                verification_result = {
                    "status": "fail",
                    "reasoning": f"Expected result '{expected_result}' not found in output",
                    "issues": ["Output does not contain expected result"]
                }
        
        # Write status file
        with open(status_file, 'w') as f:
            json.dump(verification_result, f, indent=2)
        
        # Log completion
        with open(log_file, 'a') as f:
            f.write(f"[{datetime.now().isoformat()}] Claude verification complete: {verification_result['status']}\n")
        
        print(f"Verification complete. Status: {verification_result['status']}")
        sys.exit(0)
    else:
        raise Exception("Claude returned empty response")
        
except Exception as e:
    error_msg = f"Verification failed: {type(e).__name__}: {str(e)}"
    print(f"FATAL ERROR: {error_msg}", file=sys.stderr)
    
    # Write failure status
    failure_status = {
        "status": "error",
        "reasoning": error_msg,
        "issues": ["Verification process failed"]
    }
    
    with open(status_file, 'w') as f:
        json.dump(failure_status, f, indent=2)
    
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] VERIFICATION ERROR: {error_msg}\n")
    
    sys.exit(1)
```

---
<!--This section is for the orchestrating LLM. It defines how to fix this prompt if things go wrong.-->
## [SELF_CORRECTION]

**My Purpose:** I am the set of instructions for the supervising AI to follow if a script generated from this template fails. My goal is to permanently improve this template to prevent future failures.

**If the generated script fails, you MUST:**

1.  **Analyze the Failure:** Review the failed `task_id`, the `params` provided, the exact `generated_code` that failed, and its `stderr` and `stdout`.

2.  **Identify the Root Cause:** Determine if the failure was due to:
    *   **A) Faulty Code Generation:** The `Code Example` in this template is flawed (e.g., incorrect JSON parsing, missing error handling).
    *   **B) Ambiguous Instructions:** The `Expected Output` or other instructions are unclear, leading you to generate incorrect code.
    *   **C) An External Factor:** The environment is misconfigured (e.g., missing API keys), or the external service (Claude) is down.

3.  **Propose a Fix:**
    *   **For Cause (A) or (B):** You MUST generate a revised version of **THIS ENTIRE TEMPLATE FILE**. Do not just fix the script; fix the source of the error. In your reasoning, clearly state what was wrong.
    *   **For Cause (C):** Do not modify this template. Instead, report the external factor clearly so a human can intervene (e.g., "Verification failed: The `ANTHROPIC_API_KEY` environment variable is not set.").

4.  **Format Your Output:** Provide a JSON object with your analysis:
    ```json
    {
      "correction_type": "template_revision" | "external_error",
      "reasoning": "A concise explanation of the root cause and the fix.",
      "revised_template_content": "The full, new content for this .md file. (null if external_error)"
    }
    ```
5.  **NEVER simulate fixes.** Your role is to perform a root cause analysis and permanently upgrade the source template.