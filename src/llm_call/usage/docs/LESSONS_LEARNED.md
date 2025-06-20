# Lessons Learned - Usage Function Development

## Key Principles from Gemini's Critique

### 1. Frame Automated Checks as Assistants, Not Judges
- **DON'T**: Use "PASS/FAIL" status that implies final verdict
- **DO**: Use "OK/REVIEW" or similar framing that shows it's a helper
- **WHY**: The simple keyword checks are not definitive - they assist human review

### 2. Always Include Reasoning in Results
- **DON'T**: Just return `passed: true/false`
- **DO**: Return `(passed, reason)` tuples like `(True, "Result contained expected substring '4'.")`
- **WHY**: Creates an auditable, "lie-proof" record of what the check actually did

### 3. Avoid Code Repetition
- **DON'T**: Copy-paste similar blocks for each test method
- **DO**: Use loops to process results uniformly
- **WHY**: Cleaner code, easier maintenance, less chance of inconsistency

### 4. Complexity is the Enemy
- **DON'T**: Add regex parsers, AST analysis, semantic similarity, or other brittle techniques
- **DO**: Keep checks simple and deterministic
- **WHY**: Complex solutions fail in unexpected ways; simple checks are predictable

### 5. Human-in-the-Loop is the Goal
- **DON'T**: Try to replace human judgment
- **DO**: Augment human verification with clear, helpful information
- **WHY**: LLMs are unpredictable; humans need to make final determinations

## Template Improvements Applied

1. **Table Headers**: Changed from "Status" to "Auto-Check"
2. **Table Content**: Added "Reason" column to explain the check
3. **JSON Format**: Added `reason_for_check` field to verification data
4. **Summary Message**: Changed from "ALL TESTS PASSED" to "Human verification required"
5. **Code Structure**: Consolidated repetitive blocks into clean loops

## Anti-Patterns to Avoid

### L Binary Pass/Fail Thinking
```python
# BAD
status = " PASS" if is_correct else "L FAIL"
```

```python
# GOOD
auto_check_status = " OK" if is_correct else "  REVIEW"
```

### L Opaque Results
```python
# BAD
return is_correct
```

```python
# GOOD
return (is_correct, f"Result contained expected substring '{expected}'.")
```

### L Claiming Final Authority
```python
# BAD
"Status:  ALL TESTS PASSED"
```

```python
# GOOD
"Status: Human verification required for final determination."
```

## Remember: The Three Small Changes

When improving usage functions, focus on:
1. Reframe automated checks as assistants
2. Add reasons for verdicts
3. Clean up code repetition

These are conservative, respectful changes that honor the purpose of human verification.

## Final Wisdom

> "The goal is to **augment human verification, not replace it.**"

Every usage function should make it easier for humans to verify results, not harder. Clear output, transparent reasoning, and humble framing are key.