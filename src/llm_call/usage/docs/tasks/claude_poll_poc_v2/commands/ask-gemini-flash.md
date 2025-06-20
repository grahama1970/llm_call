# Ask Gemini Flash Command

Ask Gemini Flash this question and get a quick, balanced response.

## Parameters:
- `query`: (string) The full text of the question/prompt to send to Gemini
- `output_path`: (string) The file path where the Gemini response should be saved

## Expected Output:
- Provide clear, concise answers (limit ~500 tokens per answer/critique)
- Use creative but accurate tone
- For complex code tasks, suggest using ask-gemini-pro instead
- If unable to answer, explain why clearly

## Code Example:
```python
# This is a sample implementation. You should adapt it based on the specific query.
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
from litellm import completion
import sys

# Parameters will be passed in from the orchestrator
query = """{{ params.query }}"""
output_path = "{{ params.output_path }}"
model = os.getenv('SLASHCMD_ASK_GEMINI_FLASH_MODEL', 'vertex_ai/gemini-1.5-flash')

try:
  response = completion(
    model=model,
   messages=[{"role": "user", "content": query}],
    temperature=0.7
  )
  
  if response.choices and response.choices[0].message.content:
    result = response.choices[0].message.content
    with open(output_path, "w") as f:
      f.write(result)
    print(f"Successfully wrote response to {output_path}")
    sys.exit(0)
  else:
    finish_reason = response.choices[0].finish_reason if response.choices else 'unknown'
    error_message = f"ERROR: Gemini returned empty content. Finish reason: {finish_reason}"
    print(error_message, file=sys.stderr)
    # Also write error to the output file for auditing
    with open(output_path, "w") as f:
      f.write(error_message)
    sys.exit(1)
    
except Exception as e:
  print(f"FATAL ERROR calling Gemini: {type(e).__name__}: {str(e)}", file=sys.stderr)
  import traceback
  with open(output_path, "w") as f:
      f.write(f"FATAL ERROR:\n{traceback.format_exc()}")
  sys.exit(1)
```

---
<!--This section is for the orchestrating LLM. It defines how to fix this prompt if things go wrong.-->
## [SELF_CORRECTION]

**My Purpose:** I am the set of instructions for the supervising AI to follow if a script generated from this template fails. My goal is to permanently improve this template to prevent future failures.

**If the generated script fails, you MUST:**

1.  **Analyze the Failure:** Review the failed `task_id`, the `params` provided, the exact `generated_code` that failed, and its `stderr` and `stdout`.

2.  **Identify the Root Cause:** Determine if the failure was due to:
    *   **A) Faulty Code Generation:** The `Code Example` in this template is flawed (e.g., incorrect library usage, missing error handling).
    *   **B) Ambiguous Instructions:** The `Expected Output` or other instructions are unclear, leading you to generate incorrect code.
    *   **C) An External Factor:** The environment is misconfigured (e.g., missing API keys), or the external service (Gemini) is down.

3.  **Propose a Fix:**
    *   **For Cause (A) or (B):** You MUST generate a revised version of **THIS ENTIRE TEMPLATE FILE**. Do not just fix the script; fix the source of the error. In your reasoning, clearly state what was wrong (e.g., "The previous `Code Example` did not handle `None` responses when `finish_reason` was `length`. The new example adds a check for this.").
    *   **For Cause (C):** Do not modify this template. Instead, report the external factor clearly so a human can intervene (e.g., "Verification failed: The `GOOGLE_APPLICATION_CREDENTIALS` environment variable is not set.").

4.  **Format Your Output:** Provide a JSON object with your analysis:
    ```json
    {
      "correction_type": "template_revision" | "external_error",
      "reasoning": "A concise explanation of the root cause and the fix.",
      "revised_template_content": "The full, new content for this .md file. (null if external_error)"
    }
    ```
5.  **NEVER simulate fixes.** Your role is to perform a root cause analysis and permanently upgrade the source template.