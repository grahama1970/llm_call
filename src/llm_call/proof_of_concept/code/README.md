# Proof of Concept (POC) Code Directory

This directory contains small, focused proof-of-concept scripts that validate specific technical challenges before full implementation.

## Purpose

POC scripts help:
1. Break down complex problems into manageable pieces
2. Validate technical approaches before investing in full implementation
3. Identify and solve integration issues early
4. Create reusable reference implementations

## POC Guidelines

### Requirements for Each POC:
- **Single Focus**: Each POC tests ONE specific concept
- **Minimal Code**: Maximum 100 lines
- **Self-Contained**: Must run independently
- **Real Data**: Use actual files/APIs, not mocks
- **Clear Output**: Print explicit PASS/FAIL results

### POC Script Structure:
```python
#!/usr/bin/env python3
"""POC [NUMBER]: [SPECIFIC CHALLENGE]

Tests: [What specific functionality this validates]
Expected: [What should happen]
"""

print("=== POC: [CHALLENGE NAME] ===")

# Focused test implementation
# ...

# Clear result output
if success:
    print("✅ POC PASSED")
else:
    print("❌ POC FAILED")
```

## Directory Organization

```
code/
├── task_async_polling/          # SQLite async polling implementation
│   ├── poc_sqlite_basic.py     # Basic SQLite operations
│   ├── poc_model_response_serialization.py  # LiteLLM response handling
│   ├── poc_async_polling_complete.py        # Full async flow
│   └── poc_litellm_integration.py          # Real API integration
├── task_[number]_[name]/       # Future task POCs
│   └── poc_*.py
```

## Example POCs from Async Polling Task

1. **poc_sqlite_basic.py** - Validates SQLite can store/retrieve task data
2. **poc_model_response_serialization.py** - Tests ModelResponse JSON conversion
3. **poc_async_polling_complete.py** - Verifies complete async task flow
4. **poc_litellm_integration.py** - Tests real LiteLLM API calls with serialization

## Running POCs

```bash
# Navigate to specific task directory
cd src/llm_call/proof_of_concept/code/task_async_polling/

# Run individual POC
python3 poc_sqlite_basic.py

# Expected output format:
# === POC: SQLite Basic Functionality ===
# Test 1: Database creation
# ✓ Table created successfully
# ...
# ✅ POC PASSED
```

## When to Create POCs

Create a POC when:
- Integrating new technology/library
- Testing performance requirements
- Validating complex algorithms
- Verifying external dependencies
- Ensuring error handling works

## Anti-Patterns to Avoid

- ❌ Writing full implementations as "POC"
- ❌ Combining multiple concepts in one POC
- ❌ Using mocks instead of real connections
- ❌ Skipping POCs for "simple" features
- ❌ Not verifying actual output

## Success Metrics

A good POC:
- Runs in <5 seconds
- Produces clear PASS/FAIL output
- Uses <100 lines of code
- Tests exactly one concept
- Can be run repeatedly with same result
