# Proper Verification Script

## Purpose
This script detects when Claude Code (or other AI assistants) fake test results by printing success messages without implementing actual functionality. It uses multiple LLM verifiers running concurrently to achieve consensus.

## Key Features
- **Multi-model verification**: Uses Ollama (qwen2.5:32b), Claude CLI, and Gemini API
- **Concurrent execution**: All verifiers run in parallel for speed (~13s vs ~30s sequential)
- **CLAUDE.md rule checking**: Verifies compliance with specific anti-hallucination rules
- **Clear test cases**: Includes obvious fakes, real implementations, and tricky edge cases

## Results
- **Ollama**: 100% accuracy detecting fake implementations
- **Claude**: 75% accuracy checking CLAUDE.md rule compliance
- **Gemini**: Results vary due to API issues

## Critical Bug (Lines 128, 163)
**CODE TRUNCATION**: `verify_with_claude` and `verify_with_gemini_direct` only analyze the first 300 characters of code (`code[:300]`), while `verify_with_ollama_qwen` sees the full code. This severely limits their effectiveness on longer functions.

## Limitations (per Gemini's critique)
1. **Static analysis only** - no runtime execution to verify actual behavior
2. **Recursive problem** - using LLMs to judge LLMs
3. **Limited "fake" definition** - misses partial implementations or incorrect logic with success messages
4. **External dependencies** - requires Docker, Ollama, Claude CLI despite "self-contained" claim
5. **Code truncation** - Claude and Gemini miss fakes after character 300

## Edge Cases Not Covered
- Conditional faking (e.g., `if IS_CI: print("Success")`)
- Time-based faking (using sleep() to simulate work)
- Partial implementations that do some work but not all
- Sophisticated mocking that looks real
- Error suppression with fake success reporting

## Recommended Improvements
1. **Fix code truncation immediately** - pass full code to all verifiers
2. **Add sandboxed execution** - actually run the code to verify behavior
3. **Expand test cases** - include partial implementations and edge cases
4. **Better error handling** - catch specific exceptions not bare except
5. **Dynamic timeouts** - adjust based on code complexity

## Usage
```bash
python proper_verification.py
```

## Dependencies
- Docker with Ollama container running qwen2.5:32b
- Claude CLI installed and configured
- GOOGLE_API_KEY or GEMINI_API_KEY environment variable
- Python 3.6+ (uses only standard library)