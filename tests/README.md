# CLAUDE.md

## GLOBAL CODING & ORGANIZATION STANDARDS

> This document defines all non-negotiable standards for project structure, coding, validation, testing, and reporting. **Every agent and contributor must follow these guidelines before executing any task.**

---

## 1. Project Structure & Directory Organization

```
project_name/
├── docs/
│   ├── CHANGELOG.md
│   ├── memory_bank/
│   └── tasks/
├── examples/
├── pyproject.toml
├── README.md
├── src/
│   └── project_name/
├── tests/
│   ├── fixtures/
│   └── project_name/
└── uv.lock
```

- **Package Management:** Always use `uv` with `pyproject.toml`; never use `pip`.
- **Project Activation:**
    1. `cd` into the project directory
    2. `source .venv/bin/activate`
    3. Install dependencies if necessary: `uv sync --active`
- **Mirror Structure:**  
  The `examples/` and `tests/` directories **must exactly mirror the structure of the `src/` directory**. This is best practice for clarity and easy navigation.
- **Documentation:** All comprehensive docs go in `docs/`.

---

## 2. Cleanup & Organization Protocol

- **Stray Source Files:** Move misplaced source files into their correct subdirectories within `src/`.
- **Log Files:** Place all logs in a dedicated `logs/` directory or archive them if obsolete.
- **Test Files:** All test files must be in the mirrored `tests/` directory. Move any test files found elsewhere.
- **Debug/Iteration Files:** Remove or archive any temporary, debug, or iteration files not required.
- **Unorganized Markdown/JSON Files:** Move unorganized or temporary `.md` or `.json` files to a logical location or `archive/`.
- **General Review:** Ensure all files are in logical, organized locations. Move obsolete or unnecessary files to the `archive/` directory.

**Goal:**  
A clean, well-organized, and clutter-free project directory, with all files—especially source, test, log, and Markdown files—stored in their appropriate locations.

---

## 3. Test Directory Standards

- The `tests/` directory **must be an exact mirror of the `src/` directory** for best practice and easier navigation.
- Remove or archive obsolete or iteration tests.
- Update `tests/README.md` to clearly explain how to run all tests and verify project integrity after updates.

---

## 4. Security & Permissions

**If running in `--dangerously-skip-permissions` mode:**

- Claude is strictly forbidden from executing `rm -rf` or any destructive command without explicit user permission.
- Never assume permission for destructive actions, even in skip-permissions mode.

**Version Control Discipline in Dangerous Mode:**

- After every file change, immediately stage and commit the change in Git.
- Commit messages must clearly indicate *Bypassing Permissions* mode and specify the file(s) and action(s), e.g.
- This ensures all risky operations are tracked and can be reverted.

**Summary:**  
Every file change in dangerous mode must be committed with a clear, descriptive message, ensuring project safety and traceability.

---

## 5. Module Requirements

- **Max 500 lines of code per file**
- **Documentation Header:** Every file must include:
    - Purpose
    - Links to third-party docs
    - Sample input and expected output
- **Validation Function:** Every file needs a `main` block that tests with real data
- **File Location:** No stray files in project root; organize as follows:
    - Python modules: `src/project_name/`
    - Tests: `tests/`
    - Docs: `src/project_name/docs/`
    - Examples: `src/project_name/examples/`

---

## 6. Architecture Principles

- **Function-First:** Prefer simple functions; use classes only when necessary
- **Async:** Never use `asyncio.run()` inside functions—only in main blocks
- **Type Hints:** Use type hints for all function parameters and return values; prefer concrete types
- **No Conditional Imports:** Import required packages directly; handle errors during usage, not import

---

## 7. Validation & Testing

- **Real Data:** Always test with actual data, never fake inputs
- **No Mocking:** Never mock core functionality; MagicMock is strictly forbidden for core tests
- **Assertions:** Use meaningful assertions against specific expected values
- **No unconditional "All Tests Passed" messages:** Only report success if all tests genuinely pass
- **Track All Failures:** Always track and report all validation failures; never stop at the first failure
- **External Research:** If a function fails validation 3+ times, use external research tools and document findings in comments

---

## 8. Automated Markdown Test Report Requirements

After every full test suite run, **automatically generate a well-formatted Markdown report** summarizing the results. Save the report in the `@docs/reports/` directory.

**Report Table Requirements:**
- Table columns:
    - Test Name
    - Short Description
    - Actual Result (no hallucinated or placeholder data)
    - Pass/Fail Status
    - Additional relevant fields (e.g., Duration, Error Message, Timestamp)
- The table **must be clear, easy to read, and use valid Markdown table syntax.**
- Each report file must have a unique name (timestamp or test run ID).
- **No mocking of core functionality is allowed.** All results must reflect actual test outcomes.

**Example Table Format:**
```
| Test Name      | Description                 | Result        | Status | Duration | Timestamp           | Error Message      |
|----------------|----------------------------|---------------|--------|----------|---------------------|--------------------|
| LoginTest      | User login with valid creds | Success       | Pass   | 1.2s     | 2025-05-25 17:50:00 |                    |
| PaymentTest    | Payment with expired card   | Card Expired  | Fail   | 0.8s     | 2025-05-25 17:50:01 | Card expired error |
| DataExportTest | Export user data to CSV     | File exported | Pass   | 2.0s     | 2025-05-25 17:50:03 |                    |
```

**Instructions:**
- Ensure the report is generated and saved automatically after every full test suite run.
- Place the generated `.md` file in `@docs/reports/`.

---

## 9. Validation Output Requirements

- Never print "All Tests Passed" or similar unless **all** tests actually passed
- Always verify actual results against expected results before printing any success message
- Always test multiple cases, including normal, edge, and error cases
- Always track all failures and report them at the end—don't stop at first failure
- All validation functions must exit with code 1 if any tests fail; exit with code 0 only if all tests pass
- Always include the count of failed tests and total tests in the output
- Always include details of each failure when tests fail
- Never include irrelevant test output that could hide failures
- Structure validation to explicitly check each test case
- Never claim success if search returns 0 results—this is always a failure
- Highlight critical test results with visual markers (emojis, headers, or formatting)
- Clearly separate test output from implementation details with visual dividers
- Summarize test results at the top or bottom of output with PASS/FAIL counts
- Ensure critical information (errors, results, success/failure) is immediately visible
- Never bury important results in verbose logs—highlight them explicitly

---

## 10. Compliance Checklist

Before completing a task, verify that your work adheres to **all** standards in this document. Confirm each of the following:

1. All files have appropriate documentation headers
2. Each module has a working validation function with real data
3. Type hints are used properly and consistently
4. All functionality is validated before addressing linting issues
5. No `asyncio.run()` inside functions
6. Code is under the 500-line limit per file
7. If function failed validation 3+ times, external research was conducted and documented
8. Validation functions never include unconditional "All Tests Passed" messages
9. Validation functions only report success if explicitly verified by comparing actual to expected results
10. Validation functions track and report all failures, not just the first one encountered
11. Validation output includes count of failed tests out of total tests run
12. Search results must return actual data—0 results is always a failure that must be investigated

If any standard is not met, fix the issue before submitting the work.

