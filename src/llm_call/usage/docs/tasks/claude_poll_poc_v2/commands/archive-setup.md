# Archive Setup Command

Archive old artifacts and create a fresh environment for the task execution.

## Parameters:
- `log_file`: (string) Path to the log file - typically passed as {{settings.log_file}}

## Expected Output:
- Archives any existing artifacts into a timestamped backup directory
- Creates fresh directories for the new run
- Logs the setup completion with timestamp

## Code Example:
```python
import os
import shutil
from datetime import datetime
import sys

# Get timestamp for archive directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archive_dir = f"archive_{timestamp}"
log_file = "{{ params.log_file }}"

try:
    # Create archive directory if we have existing artifacts
    artifacts_to_archive = ["generated_scripts", "add_results.txt", "verification_status.json", 
                           "final_answer.txt", "gemini_validation_response.md", log_file]
    
    artifacts_exist = any(os.path.exists(artifact) for artifact in artifacts_to_archive)
    
    if artifacts_exist:
        os.makedirs(archive_dir, exist_ok=True)
        print(f"Archiving existing artifacts to {archive_dir}/")
        
        for artifact in artifacts_to_archive:
            if os.path.exists(artifact):
                if os.path.isdir(artifact):
                    shutil.move(artifact, os.path.join(archive_dir, artifact))
                else:
                    shutil.move(artifact, archive_dir)
                print(f"  Archived: {artifact}")
    
    # Create fresh directories
    os.makedirs("generated_scripts", exist_ok=True)
    print("Created fresh generated_scripts/ directory")
    
    # Initialize log file
    with open(log_file, "w") as f:
        f.write(f"[{datetime.now().isoformat()}] Task execution started\n")
        f.write(f"[TASK1] Environment setup complete.\n")
    
    print(f"[TASK1] Environment setup complete.")
    sys.exit(0)
    
except Exception as e:
    print(f"FATAL ERROR during setup: {type(e).__name__}: {str(e)}", file=sys.stderr)
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
    *   **C) An External Factor:** The environment is misconfigured or permissions are insufficient.

3.  **Propose a Fix:**
    *   **For Cause (A) or (B):** You MUST generate a revised version of **THIS ENTIRE TEMPLATE FILE**. Do not just fix the script; fix the source of the error.
    *   **For Cause (C):** Do not modify this template. Instead, report the external factor clearly so a human can intervene.

4.  **Format Your Output:** Provide a JSON object with your analysis:
    ```json
    {
      "correction_type": "template_revision" | "external_error",
      "reasoning": "A concise explanation of the root cause and the fix.",
      "revised_template_content": "The full, new content for this .md file. (null if external_error)"
    }
    ```
5.  **NEVER simulate fixes.** Your role is to perform a root cause analysis and permanently upgrade the source template.