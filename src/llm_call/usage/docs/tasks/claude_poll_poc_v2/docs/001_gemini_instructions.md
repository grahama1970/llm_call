**Considering User Intent**

I'm currently dissecting the user's request. The key is understanding the underlying needs, especially given the existing prompt files and overall goal. The goal is the guiding light.


**Mapping User Requirements**

I've just finished outlining the user's specific requests, identifying the core goal and breaking down the features they're after. I'm thinking about how each feature interacts and impacts the task list design. The focus is on flexibility and control.


**Outlining the Core Concepts**

I'm now delving into the fundamental components. The user's goal centers on a flexible and readable task list. I'm examining the existing implementation's strengths and weaknesses, specifically `002_claude_poll_verification_tasks.md`, to extract best practices and areas ripe for enhancement. I see a need for a balance of explicitness and conciseness.


**Structuring a Solution**

I'm synthesizing the existing patterns and the user's needs into a better approach. The current implementation is too verbose, and the new structure should solve this. My focus is on developing a YAML or JSON-based task list format. This format should incorporate the core functionality described in the provided files.


**Defining a New Structure**

I'm now immersed in the detailed schema design for the YAML task list. I'm concentrating on all user-requested features, including background task execution, and inline execution, flexible verification steps, self-correction capabilities, and code optimization. I see a clear pathway towards a readable and robust structure. I am focusing on the balance between human readability and machine processability.


**Defining YAML Schema**

I'm now working on the YAML schema's nitty-gritty details, building on the user's specifications. I am focusing on defining the `action`, `verify`, and conditional execution components. I'm working on the structure's flexibility. It should clearly separate intention from implementation. The "llm_generate_and_run" task type will allow template and code generation.


**Defining the YAML Format**

I'm now starting to flesh out the example YAML schema. I need the structure to cover all the user requests. I'll focus on `action` (llm_generate_and_run, execute_command, write_file), `mode` (inline/background), and the crucial `verify` block. This will be the core for flexibility.


**Developing the New Format**

I'm now reviewing the YAML schema design, focusing on `action`, `verify`, and conditional execution. The goals are flexibility, readability, and a clear separation of intention from implementation. The llm_generate_and_run task type is where the code template is produced.


**Developing a YAML Task List**

I'm now defining the elements of the YAML schema. I want it to support `action`, `mode` (inline/background), and the `verify` block. The "llm\_generate\_and\_run" action will permit creating code templates for tasks. This provides a clearer separation between intent and implementation.


**Implementing the New Structure**

I'm starting to develop the example YAML task list, leveraging the detailed specifications I've crafted. I am including the `llm_generate_and_run`, `execute_command`, and `write_file` actions. The design allows for flexible, readable tasks. The user's request for a clearer separation of intent and implementation is central.


**Refining the Structure**

I'm now focusing on the final presentation structure. It should be split to cover the YAML format, improved templates, and the new orchestration logic. I'll provide a complete example YAML, along with explanations of its key elements. The self-correction loop is also critical.


**Analyzing the Proposed Schema**

I'm now evaluating the YAML schema design, focusing on how to ensure both human readability and machine processability. The `action`, `verify`, and `mode` components are especially key, along with the `llm_generate_and_run` task type's parameters. I am keeping a close watch on the integration of the self-correction.


Excellent. This is a crucial and fascinating challenge. You're moving from a rigid, proof-of-concept script to a flexible, self-correcting, and robust automation framework. This requires thinking about the system at multiple levels: the data structure for tasks, the content of the prompts, and the logic of the orchestrator that ties them together.

Let's break this down meticulously.

### The Core Problem with the Current System

The current `002_claude_poll_verification_tasks.md` is an **execution log**, not a **plan**. It's a linear sequence of code blocks that an orchestrator would execute verbatim.

*   **Pros:** It's explicit and leaves no room for ambiguity.
*   **Cons:**
    *   **Inflexible:** You can't easily say "run this in the background" or "only run this if X is true." The logic is hardcoded (e.g., `&` for background, `&&` for conditional execution).
    *   **Verbose:** The entire content of generated scripts is dumped into the master plan, making it hard to read and maintain.
    *   **Not Human-Friendly:** Writing such a file from scratch is tedious and error-prone.
    *   **Repetitive:** Boilerplate (logging, etc.) is copied everywhere.

### The Solution: A Declarative Task Definition

We need to separate the **"what"** from the **"how"**. The task list should be a high-level plan (the "what"), and the `commands/` templates should contain the detailed instructions for execution (the "how").

A structured format like **YAML** is perfect for this. It's human-readable and machine-parseable.

---

## 1. The New Task List: `tasks.yaml`

Instead of the lengthy Markdown file, we'll define a `tasks.yaml`. This file becomes the new master prompt or configuration for the orchestrator.

**Proposed `tasks.yaml` (replaces `002_claude_poll_verification_tasks.md`):**

```yaml
# This is the master plan for the Claude Code Orchestrator.
# It's declarative, readable, and defines the sequence of operations.

working_directory: "/home/graham/workspace/experiments/llm_call/src/llm_call/usage/docs/tasks/claude_poll_poc/"

# Global settings can be defined here
settings:
  log_file: "task_execution.log"

tasks:
  - task_id: T1_ENV_SETUP
    description: "Archive old artifacts and create a fresh environment."
    action:
      type: llm_generate_and_run # Use an LLM to generate a script from a template and run it.
      prompt_template: "commands/archive-setup.md"
      output_path: "generated_scripts/setup.py"
    # This task is critical, so we'll verify its output.
    verify:
      - type: file_exists
        path: "generated_scripts/"
      - type: log_contains
        log_file: "{{settings.log_file}}"
        pattern: "[TASK1] Environment setup complete."

  - task_id: T2_CREATE_CODE
    description: "Create a simple Python script for testing."
    action:
      type: write_file # A simple, direct action. No LLM needed.
      path: "generated_scripts/simple_add.py"
      content: |
        # A simple function to add two numbers and write to a file.
        def add_numbers():
          # Hardcoded for simplicity in this example.
          result = 2 + 3 
          with open("add_results.txt", "w") as f:
            f.write(f"The sum is: {result}")
        
        if __name__ == "__main__":
          add_numbers()
    # Idempotency: If this script already exists, do not overwrite it.
    # This is useful for re-running a failed workflow from a certain point.
    skip_if:
      - type: file_exists
        path: "generated_scripts/simple_add.py"

  - task_id: T3_RUN_CODE_INLINE
    description: "Execute the simple script directly."
    action:
      type: execute_command # Runs inline, blocks until complete.
      command: "python generated_scripts/simple_add.py"
    verify:
      - type: file_contains
        path: "add_results.txt"
        content: "The sum is: 5"

  - task_id: T4_BACKGROUND_VERIFICATION
    description: "Launch a background Claude instance to critique the code and verify its output."
    action:
      type: llm_generate_and_run
      mode: background # <-- This is new! It tells the orchestrator not to wait.
      prompt_template: "commands/claude-verify.md"
      output_path: "generated_scripts/verify_script.py"
      params: # <-- Parameters are passed explicitly to the template.
        code_file: "generated_scripts/simple_add.py"
        result_file: "add_results.txt"
        status_file: "verification_status.json"
        log_file: "{{settings.log_file}}"
        expected_result: 5

  - task_id: T5_POLL_FOR_VERIFICATION
    description: "Wait for the background verification to complete successfully."
    action:
      type: poll_file_status # A special action type for synchronization.
      status_file: "verification_status.json"
      # The orchestrator will parse the JSON and evaluate this condition.
      success_condition: "status == 'pass'" 
      timeout_seconds: 60
      # If this fails, the entire workflow stops.

  - task_id: T6_FINAL_ANSWER
    description: "Answer a final question to prove the sequence completed."
    action:
      type: write_file
      path: "final_answer.txt"
      content: "Paris"
    # No verification needed for this simple step; it's part of the final audit.

  - task_id: T7_FINAL_AUDIT
    description: "Use Gemini to perform a final, holistic audit of the entire run."
    action:
      type: llm_generate_and_run
      prompt_template: "commands/ask-gemini-flash.md"
      output_path: "gemini_validation_response.md"
      # The query for Gemini will be constructed by the orchestrator based on the run context.
      params:
        query_template: |
          Please critique the execution of a multi-step POC based on the following artifacts.
          Did the process succeed? Was the logging clear? 
          
          Final Log File:
          ```log
          {{ file_content('task_execution.log') }}
          ```

          Verification Status:
          ```json
          {{ file_content('verification_status.json') }}
          ```
```

### Why this `tasks.yaml` is better:

1.  **Flexibility:** The `action.mode` (`inline`/`background`) and dedicated `action.type` (`poll_file_status`) provide the control you need.
2.  **Readability:** The high-level plan is clear. The implementation details are abstracted away into the `commands/` templates.
3.  **Configurability:** `params` allow you to reuse the same prompt template for different tasks.
4.  **Integrated Verification:** The `verify` block makes it an optional, first-class citizen of any task.
5.  **Idempotency:** The `skip_if` block allows for more resilient and efficient re-runs.

---

## 2. Amending the Helper Prompts (`commands/*.md`) for Self-Correction

The `commands/*.md` files are excellent. We just need to make them smarter and more robust, especially regarding error handling and self-improvement.

**Key Idea: The [SELF_CORRECTION] Block**

We'll add a new, standardized section to every command template. When a script generated from a template fails, the orchestrating LLM will use this section to debug and amend the template itself.

Here's the revised `ask-gemini-flash.md` as an example.

**`src/llm_call/usage/docs/tasks/claude_poll_poc/commands/ask-gemini-flash.md` (Amended)**

``````markdown
# Ask Gemini Flash Command

Ask Gemini Flash this question and get a quick, balanced response: $ARGUMENTS

## Expected Output:
... (same as before) ...

## Code Example:
```python
# This is a sample implementation. You should adapt it based on the specific query.
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
from litellm import completion
import sys

# Parameters will be passed in from the orchestrator
query = "{{params.query}}" # Use a templating engine like Jinja2
output_path = "{{params.output_path}}"
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
``````

---

## 3. How the Orchestrator Uses This System

The "Claude Code Orchestrator" is the master AI agent responsible for executing the `tasks.yaml`.

**The Orchestrator's Main Loop:**

1.  **Parse `tasks.yaml`**.
2.  For each task in `tasks`:
    a. **Log Start:** Log `[START] task_id: {task.id}`.
    b. **Check `skip_if`:** Evaluate the conditions. If true, log `[SKIP]` and go to the next task.
    c. **Execute Action:**
        *   If `type` is `llm_generate_and_run`:
            i. Read the `prompt_template`.
            ii. Inject `params` into the template.
            iii. Send the filled template to an LLM (Claude) to generate the script content.
            iv. **Save the generated script to `output_path`. This is critical for idempotency and debugging.**
            v. Run the script (inline or background).
        *   If `type` is `execute_command`: Run the command.
        *   If `type` is `poll_file_status`: Start polling.
    d. **Handle Result:**
        *   **On Success:** Log `[SUCCESS]`. Run the `verify` block. If verification fails, treat it as a task failure.
        *   **On Failure (non-zero exit code or timeout):** Log `[FAIL]` with `stderr`. **This triggers the self-correction flow.**
3.  **The Self-Correction Flow (on task failure):**
    a. The orchestrator re-prompts itself (or a dedicated "Reflector" AI).
    b. It provides the context: the failed task from `tasks.yaml`, the `prompt_template` used, the generated code, and the error log.
    c. It specifically instructs the AI to follow the `[SELF_CORRECTION]` section of the failed template.
    d. It receives the JSON response.
    e. If `correction_type` is `template_revision`, it **overwrites the original `commands/*.md` file**. It then retries the failed task.
    f. If `correction_type` is `external_error`, it halts and reports the issue for human review.

### Regarding Your Specific Questions:

*   **Launching Claude background instances:** Handled by `action.mode: background` in the YAML.
*   **Executing inline:** This is the default mode (`action.mode: inline` or omitted).
*   **Choosing when to verify:** Handled by the optional `verify:` block in the YAML for any task.
*   **Giving Claude code to amend:** The self-correction flow does exactly this, but at the *template level*, which is more robust. For one-off fixes, a task could be `action.type: llm_fix_code` with `params: { file_to_fix: 'path/to/code.py' }`.
*   **Claude amending the prompt itself:** This is the core of the `[SELF_CORRECTION]` block.
*   **Running existing finished code:** Handled by the `skip_if:` block combined with the orchestrator always saving generated code to a known `output_path`. If the file exists, the generation step is skipped, and the orchestrator can just run the existing file.

This revised framework creates a system that is not only flexible and legible but has the built-in capacity to learn from its mistakes and become more reliable over time.