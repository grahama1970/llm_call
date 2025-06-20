```markdown
# Automated Workflow with Explicit Polling Tasks

This markdown file documents and orchestrates an automated workflow using shell scripts and explicit polling steps. The goal is to ensure that each step only proceeds when the previous task is fully complete and verified. This approach is ideal for robust automation, especially when integrating AI verification or asynchronous tasks.

## Overview

- Each task is clearly defined and separated.
- After a task that requires verification or asynchronous completion, a polling task is inserted.
- Polling tasks wait for a specific condition (such as a status file) before allowing the workflow to continue.
- All steps are executed via shell scripts, following best practices for automation and security[1][2].

---

## Tasks List

1. **Generate Output**
   - Write a Python function that adds two numbers and saves the result to a file.

2. **Verify Output (Async)**
   - Run an AI verification (e.g., Claude Code) in the background to check the output and write a JSON status file.

3. **Poll for Verification Result**
   - Wait for the verification JSON file to appear and confirm the status is `"success"` before proceeding[3].

4. **Continue Workflow**
   - Proceed to the next automation task, assured that all previous steps have completed successfully.

---

## Example Implementation

### Task 1: Generate Output

```
cat > add_function.py  verification.log &
```

---

### Task 3: Poll for Verification Result

```
#!/bin/bash

STATUS_FILE="verification.json"
EXPECTED_STATUS="success"

while [ ! -f "$STATUS_FILE" ]; do
  sleep 5
done

STATUS=$(jq -r '.status' "$STATUS_FILE")
if [ "$STATUS" != "$EXPECTED_STATUS" ]; then
  echo "Error: Status in $STATUS_FILE is not '$EXPECTED_STATUS'"
  exit 1
fi

echo "Polling complete: status is '$EXPECTED_STATUS' in $STATUS_FILE"
exit 0
```

---

### Task 4: Continue Workflow

```
echo "Proceeding to next task"
```

---

## Why Use Polling?

Polling ensures that asynchronous or background tasks—such as AI verification—are fully complete before the workflow advances[1][3]. This prevents race conditions, increases reliability, and provides clear checkpoints for automation systems.

---

*This workflow leverages markdown-driven automation, explicit shell scripting, and robust polling mechanisms for secure and reliable orchestration of complex tasks[1][2][3].*
```