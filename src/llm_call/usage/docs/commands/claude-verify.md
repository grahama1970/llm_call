# /user:claude-verify

Run a background verification of a Python script and its output file, logging every step and writing a structured JSON status file. This command uses Claude Code as a language model to critique the code quality, verify outputs, and suggest improvements, all driven by a flexible prompt with no reliance on the `ast` module or hardcoded scripts.

---

## Usage

```
/user:claude-verify code_file=simple_add.py result_file=add_results.txt status_file=verification_status.json log_file=task_execution.log expected_result=5
```

---

## Prompt Template

Replace the variables with the arguments provided to the slash command.

```
Verify the correctness of a Python script and its output, and critique the code quality as a language model with suggested improvements.

**Instructions:**
- Use Loguru for logging. At the top of the generated script, include:
  ```python
  from loguru import logger
  # Remove default handler to prevent stderr output
  logger.remove()
  # Add only file handler
  logger.add('$log_file', rotation="1 MB", enqueue=True, backtrace=True, diagnose=True,
             format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {message}")
  ```
- Log: "🔬 BACKGROUND CLAUDE VERIFICATION STARTED"
- Log: "-" * 80 (sub-separator for clarity)
- Read the Python file `$code_file` as raw text and critique its quality as a language model, focusing on:
  - **Readability**: Are variable names descriptive (e.g., avoid single-letter names like `a` or `b`)? Are comments present and clear?
  - **Structure**: Is the code logically organized? Is the function `add_numbers` clearly defined with appropriate inputs and outputs?
  - **Error Handling**: Are try-except blocks used for file operations or other risky actions?
  - **Style**: Does the code follow PEP 8 guidelines (e.g., indentation, line length under 79 characters)?
  - **Correctness**: Does the code appear to perform the intended task (add two numbers and write the result to `$result_file`)?
- When reading the code file, log:
  ```
  logger.info("[CODE_ANALYSIS] Reading $code_file")
  logger.info("```python")
  logger.info(code_content)
  logger.info("```")
  ```
- Run the script using `python $code_file`, capturing stdout, stderr, and return code with a 10-second timeout.
- When executing, log:
  ```
  logger.info("[EXECUTION] Running python $code_file")
  logger.info("[EXECUTION_OUTPUT]")
  logger.info(f"stdout: {stdout}")
  logger.info(f"stderr: {stderr}")
  logger.info(f"return_code: {return_code}")
  ```
- Read the output file `$result_file` and check if the result matches `$expected_result`.
- When verifying output, log:
  ```
  logger.info("[FILE_VERIFICATION] Reading $result_file")
  logger.info("```")
  logger.info(file_content)
  logger.info("```")
  ```
- Suggest specific code tweaks to address any issues found (e.g., add comments, improve variable names, add error handling). Format tweaks as code snippets for clarity.
- Write a JSON status file `$status_file` with the following keys:
  - `datetime`: Current UTC timestamp in ISO format (e.g., "2025-06-18T15:37:00.123456Z").
  - `critique`: Detailed analysis of code quality and output verification.
  - `tweaks`: Suggested code improvements (code snippets or full code).
  - `status`: "pass" if the output in `$result_file` matches `$expected_result` and no errors occur, "fail" otherwise.
  - `stdout`: Output from running the code.
  - `stderr`: Any error messages.
- Before writing the JSON, log it:
  ```
  logger.info("[JSON_UPDATE] Writing final verification status")
  logger.info("```json")
  logger.info(json.dumps(verification_data, indent=2))
  logger.info("```")
  ```
- Write the JSON file atomically (use a temporary file and rename) to avoid race conditions with polling.
- Log completion: "🔬 BACKGROUND VERIFICATION COMPLETE: [status]"
- Log: "=" * 80 (section separator)

**Example Generated Script Behavior:**
- Read `$code_file` and check for:
  - Presence of `def add_numbers(` to confirm the function exists.
  - Comments (e.g., `#` or `'''`) for readability.
  - Single-letter variable names (e.g., `a, b`) and suggest descriptive names (e.g., `num1, num2`).
  - Try-except blocks for file operations.
  - Line lengths exceeding 79 characters (PEP 8).
- Run `python $code_file` and capture outputs.
- Compare `$result_file` content with `$expected_result`.
- Example critique: "Function add_numbers found. No comments found; consider adding explanatory comments. Single-letter variable names (a, b) reduce readability."
- Example tweaks: 
  ```python
  Add comments:
  ```python
  # Add two numbers and return the sum
  def add_numbers(a, b):
  ```
  Use descriptive names:
  ```python
  def add_numbers(num1, num2):
      return num1 + num2
  ```
  ```
- Write `$status_file` atomically with critique, tweaks, status, stdout, and stderr.

**Constraints:**
- Do not use the `ast` module or other parsing libraries for code analysis; rely on raw text analysis and language model capabilities.
- Ensure all file paths and parameters (`$code_file`, `$result_file`, `$status_file`, `$log_file`, `$expected_result`) are substituted from the slash command.
- Handle errors gracefully (e.g., file not found, invalid output) and include them in the critique.
- Keep the generated script self-contained with no external dependencies beyond `loguru`, `subprocess`, `json`, `datetime`, `sys`, and `os`.
```
```

