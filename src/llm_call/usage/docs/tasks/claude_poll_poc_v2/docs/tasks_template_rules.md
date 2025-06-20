### 1. The Rules File (`tasks_template_rules.md`)

This file contains the codified principles we've developed. It should be saved and provided to Claude as context.

```markdown
# Rules for Creating Robust, Verifiable Task Lists

## Preamble
You are an expert AI workflow designer. When rewriting a task list according to these rules, your goal is to produce a plan that is unambiguous, deterministic, auditable, and resilient. Each instruction must be a direct, procedural command.

---

### Rule 1: Standard File Structure
Every task list file MUST begin with the following standard headers. Populate them based on the task's context.

-  `# [Title of the Workflow]`
-  `## Objective`: A one-sentence summary of the goal.
-  `## Working Directory`: The absolute path where all commands should be run.
-  `## Generated Files`: A bulleted list of all files that will be created during execution.
-  `## Tasks`: The main body of the workflow.

### Rule 2: Atomic and Procedural Tasks
Break down every high-level goal into its smallest, most explicit, and purely procedural steps.
-  **Bad (Vague):** "Process the file."
-  **Good (Procedural):**
  -  "Create a script named `process_data.py`."
  -  "Add a function to the script to read `input.csv`."
  -  "Execute the script: `python process_data.py`."
  -  "Verify the output file `results.txt` exists."

### Rule 3: Hybrid Command Strategy
Use the `commands/` directory for helper instructions, employing a hybrid strategy:
-  **For High-Complexity or Evolving Tasks (Declarative Prompts):** Instruct the AI to *generate a new script* based on a detailed prompt template (e.g., `commands/claude-verify.md`). This provides flexibility.
-  **For Common, Stable Tasks (Declarative Code):** Instruct the AI to *create a script by copying the full code* from a helper file and substituting variables (e.g., `commands/claude-poll.md`). This provides speed, reliability, and security.

### Rule 4: The Core Verification Pattern
For any task identified as high-risk, complex, or foundational, you MUST apply the full `Do -> Verify -> Poll -> Proceed` pattern. Structure this as three explicit sub-tasks:

1. **Launch Background Verification:**
  -  Generate a verification script from a `claude-verify.md`-style helper.
  -  Launch this script as a non-blocking background process.

2. **Wait for Completion:**
  -  Generate a polling script from a `claude-poll.md`-style helper.
  -  Execute this script and block until it completes.

3. **Check Exit Code and Proceed Conditionally:**
  -  After the poll script finishes, add a mandatory step to check its exit code.
  -  Use the exit code to determine the next action: `If the exit code is 0, proceed... If the exit code is not 0, stop all further tasks...`.

### Rule 5: Selective Verification
Apply Rule 4 strategically. Do not verify every step.
-  **Apply to:** Code generation, critical data transformations, API calls with important results, steps that are prerequisites for many others.
-  **Skip for:** Simple file I/O (e.g., writing a known string), simple knowledge lookups (like answering a question), or steps where failure is easily caught by the final audit.

### Rule 6: Mandatory and Structured Logging
Every single action, no matter how small, MUST be followed by a `Log:` instruction.
-  Logs MUST have a structured prefix indicating their context (e.g., `[TASK1]`, `[VERIFY]`, `[POLL_ATTEMPT]`, `[EXECUTION_HALTED]`).
-  This creates a complete, machine-parseable audit trail.

### Rule 7: Final Holistic Audit
Every task list MUST conclude with a final validation task.
-  This task's purpose is to summarize the entire execution into a single report (`execution_summary.txt`).
-  It should then simulate (or actually call) an external validator (like Gemini) to review this summary and the logs for overall coherence and success.

### Rule 8: No Ambiguity
-  All file paths should be absolute or clearly relative to the specified `Working Directory`.
-  Avoid descriptive or conversational text within the task steps. Be a commander, not a commentator.
```

---

### 2. The Prompt Template (For the User)

This is the template a user would employ to transform their basic ideas into a robust plan.

```text
You are an expert AI workflow designer specialized in creating detailed, robust, and verifiable execution plans.

Your task is to take a basic, high-level list of tasks and rewrite it into a formal task list that complies with a strict set of architectural rules.

The rules are defined in the file `tasks_template_rules.md`, which I have provided below.

<RULES_FILE>
---
# Rules for Creating Robust, Verifiable Task Lists

[... Paste the full content of tasks_template_rules.md here ...]
---
</RULES_FILE>

Now, analyze the following basic task list and rewrite it to fully comply with all the rules you have been given.

<BASIC_TASK_LIST>
---
[... User pastes their simple, high-level task list here ...]
---
</BASIC_TASK_LIST>

**Your Process:**

1. First, thoroughly study the principles in `<RULES_FILE>`.
2. Next, analyze the user's high-level goals in `<BASIC_TASK_LIST>`.
3. Rewrite the basic list into a new, detailed task list that follows every rule.
4. Identify the most complex or critical step and apply the full `Do -> Verify -> Poll -> Proceed` pattern (Rule 4).
5. For simpler steps, ensure they are procedural and have structured logging, but skip the inline verification (Rule 5).
6. Ensure the plan concludes with a final holistic audit task (Rule 7).

Your final output should be a single, complete, unabridged markdown file containing the new, compliant task list. Do not add any conversational text before or after the markdown.
```

### Example Usage

A user wants to automate a data processing task. They would fill out the prompt template like this:

**User's Filled-Out Prompt:**
```text
You are an expert AI workflow designer...

<RULES_FILE>
---
# Rules for Creating Robust, Verifiable Task Lists

[... Full content of tasks_template_rules.md ...]
---
</RULES_FILE>

Now, analyze the following basic task list and rewrite it to fully comply with all the rules you have been given.

<BASIC_TASK_LIST>
---
1. Download a user data CSV from 'https://example.com/users.csv'.
2. Write a Python script to calculate the average age from the 'age' column.
3. Save the result to a file called 'average_age.txt'.
---
</BASIC_TASK_LIST>

**Your Process:**
...
```

**Expected Claude Output:**
Claude would then generate a complete, robust markdown file that looks very much like your final `claude_poll_poc` task list, but for this new CSV processing task. It would identify step #2 (writing the Python script) as the high-risk action and wrap it in the full verification pattern, while treating the download and final save steps as simpler actions requiring only logging.