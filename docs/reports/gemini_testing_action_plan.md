# Gemini's Testing Action Plan for llm_call

**Generated:** 2025-06-15 07:13:40

Okay, here's a concise action plan for testing your `llm_call` project, given Claude Code's unreliable test reporting:

**ACTION PLAN**

**1. Immediate Steps to Implement:**

1.  **Set up Environment Variables:**  Ensure you have `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GOOGLE_API_KEY` set in your environment.  This is crucial for the tests to run.
2.  **Choose `sys.exit(1)` Approach:** Commit to using usage functions with `sys.exit(1)` for failure signaling.  It's the most reliable method given the circumstances.
3.  **Create Initial Test File:** Create a file named `test_llm.py` (or similar) to house your usage functions.
4.  **Implement Basic Test:** Start with a single, simple test for one LLM provider (e.g., OpenAI).
5.  **Run Locally and Check Exit Code:**  Run the test from your terminal (`python test_llm.py`) and immediately check the exit code (`echo $?` on Linux/macOS, `echo %ERRORLEVEL%` on Windows).
6.  **Add Logging:**  Incorporate the `logging` module into your `llm_call.py` and test functions for detailed debugging information.
7.  **Version Control:** Commit your changes to Git *frequently*.

**2. Example Code Structure for a Usage Function:**

```python
import os
import sys
import logging
from llm_call import route_llm_call  # Assuming your main function is here

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_openai():
    logging.info("Running OpenAI test...")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logging.error("OPENAI_API_KEY not set in environment.")
        sys.exit(1)

    try:
        prompt = "Say hello"
        response = route_llm_call("openai", prompt, api_key=api_key)
        logging.info(f"OpenAI response: {response}")
        assert isinstance(response, str), "OpenAI response should be a string"
        assert "hello" in response.lower(), "OpenAI response should contain 'hello'"
        logging.info("OpenAI test passed.")

    except Exception as e:
        logging.exception("OpenAI test failed:") # Logs the exception with traceback
        sys.exit(1)


if __name__ == "__main__":
    test_openai()
    logging.info("All tests completed successfully.")
```

**3. Verification Checklist:**

*   [ ] **Environment Variables Set:** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY` are defined.
*   [ ] **Test File Created:** `test_llm.py` (or similar) exists.
*   [ ] **Basic Test Implemented:** At least one test function exists (e.g., `test_openai`).
*   [ ] **`sys.exit(1)` on Failure:** Test functions use `sys.exit(1)` within `except` blocks and when assertions fail.
*   [ ] **Logging Implemented:**  `logging` module is used for informative messages and error reporting.
*   [ ] **Local Execution Verified:**  Tests run locally without errors (initial run).
*   [ ] **Exit Code Checked:**  Exit code is `0` for successful runs and non-zero for failures.
*   [ ] **Git Commits Frequent:** Changes are committed to Git regularly.
*   [ ] **Manual Review of Claude Code:**  All code generated or modified by Claude Code is thoroughly reviewed before running tests.
*   [ ] **Provider Coverage:** Tests exist for OpenAI, Anthropic, and Google LLM providers.
*   [ ] **Error Handling:** Tests cover error conditions (e.g., invalid API keys, network errors).
*   [ ] **Input Validation:** Tests validate input parameters to `route_llm_call`.

