# Task 001: Convert LLM Call Test Matrix to Usage Functions

## 1. Context & Limitations

**Critical**: Claude Code CANNOT accurately report test results. We will use:
- Usage functions with `sys.exit(1)` for verifiable failures
- Real API calls and operations (NO MOCKS)
- Explicit print statements showing actual vs expected
- Exit code verification (`echo $?`) as source of truth

**Based on Consultation with Gemini & Perplexity**:
- Both AIs confirmed: Don't trust Claude Code's test reporting
- Usage functions with exit codes are more verifiable
- Run everything locally and check exit codes yourself

## 2. Objective

Convert the comprehensive test matrix (97 tests across 14 categories) into organized usage functions that can be independently verified without relying on Claude Code's test result claims.

## 3. Current State Analysis

### Test Matrix Overview:
- **1. Functional Tests**: 15 tests (Basic operations, model routing, parameters)
- **2. Multimodal Tests**: 6 tests (Image analysis with Claude/GPT-4V)
- **3. Validation Tests**: 9 tests (JSON, code, content validation)
- **4. Conversation Management**: 7 tests (Multi-turn, context preservation)
- **5. Document Processing**: 5 tests (Corpus analysis)
- **6. Configuration Tests**: 9 tests (Config files, environment vars)
- **7. Security & Privacy**: 6 tests (API key handling, rate limiting)
- **8. Performance Tests**: 6 tests (Caching, response times)
- **9. Error Handling**: 9 tests (Invalid inputs, network errors)
- **10. Integration Tests**: 9 tests (Cross-provider, API endpoints)
- **11. Docker & Container**: 6 tests (Container orchestration)
- **12. MCP Server & Tool**: 3 tests (Claude Desktop integration)
- **13. Advanced Text Processing**: 5 tests (Chunking, summarization)
- **14. Embeddings & NLP**: 3 tests (Vector operations)

### Current Test Issues:
- Tests exist but Claude Code claims they pass when they fail
- Complex pytest structure makes verification difficult
- No clear way to verify actual results vs Claude's claims

## 4. Success Criteria (Verifiable with Exit Codes)

- [ ] All 97 tests converted to usage functions
- [ ] Each function exits with code 0 (success) or 1 (failure)
- [ ] Results can be verified with `echo $?` after execution
- [ ] Organized structure that's easy to navigate
- [ ] No reliance on Claude Code's test reporting

## 5. Implementation Plan

### Directory Structure

```
src/llm_call/usage/
├── __init__.py
├── README.md                    # How to run and verify
├── run_all.py                  # Master runner with exit code tracking
├── functional/
│   ├── __init__.py
│   ├── basic_operations.py     # F1.1-F1.3
│   ├── model_routing.py        # F2.1-F2.3
│   └── parameters.py           # F3.1-F3.3
├── multimodal/
│   ├── __init__.py
│   ├── image_analysis.py       # M1.1-M1.3
│   └── edge_cases.py           # M2.1-M2.3
├── validation/
│   ├── __init__.py
│   ├── json_validation.py      # V1.1-V1.3
│   ├── code_validation.py      # V2.1-V2.3
│   └── content_validation.py   # V3.1-V3.3
├── conversation/
│   ├── __init__.py
│   ├── multi_turn.py           # C1.1-C1.4
│   └── context_preservation.py # C2.1-C2.3
├── document_processing/
│   ├── __init__.py
│   ├── corpus_analysis.py      # D1.1-D1.3
│   └── documentation.py        # D2.1-D2.2
├── configuration/
│   ├── __init__.py
│   ├── config_files.py         # CF1.1-CF1.3
│   ├── environment_vars.py     # CF2.1-CF2.3
│   └── model_aliases.py        # CF3.1-CF3.3
├── security/
│   ├── __init__.py
│   ├── api_key_handling.py     # S1.1-S1.3
│   └── rate_limiting.py        # S2.1-S2.3
├── performance/
│   ├── __init__.py
│   ├── caching.py              # P1.1-P1.3
│   └── response_times.py       # P2.1-P2.3
├── error_handling/
│   ├── __init__.py
│   ├── invalid_inputs.py       # E1.1-E1.3
│   ├── network_errors.py       # E2.1-E2.3
│   └── validation_errors.py    # E3.1-E3.3
├── integration/
│   ├── __init__.py
│   ├── cross_provider.py       # I1.1-I1.3
│   ├── api_endpoints.py        # I2.1-I2.3
│   └── docker_integration.py   # I3.1-I3.3
├── docker/
│   ├── __init__.py
│   ├── container_basics.py     # DC1.1-DC1.3
│   └── orchestration.py        # DC2.1-DC2.3
├── mcp_server/
│   ├── __init__.py
│   └── tool_integration.py     # MCP1.1-MCP1.3
├── text_processing/
│   ├── __init__.py
│   ├── chunking.py             # T1.1-T1.2
│   └── summarization.py        # T2.1-T2.3
└── embeddings/
    ├── __init__.py
    └── nlp_operations.py       # EMB1.1-EMB1.3
```

### Usage Function Template

```python
#!/usr/bin/env python3
"""
Module: {category}_{test_id}.py
Description: Usage function for {test description}

External Dependencies:
- llm_call: Local package
- {other deps}: {urls}

Test ID: {test_id}
Expected: {expected_output}
"""

import sys
import os
from datetime import datetime

# Add src to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

try:
    from llm_call import make_llm_request
    # Other imports
except ImportError as e:
    print(f"❌ FAIL: Import error: {e}")
    sys.exit(1)


def test_{test_id_lower}():
    """Test {test_id}: {test_description}"""
    print(f"\n{'='*60}")
    print(f"TEST {test_id}: {test_description}")
    print(f"{'='*60}")
    
    try:
        # Actual test implementation
        print(f"Executing: {command_or_operation}")
        result = actual_operation()
        
        print(f"Result: {result}")
        
        # Verification
        if expected_condition:
            print(f"✅ PASS: {success_message}")
            return True
        else:
            print(f"❌ FAIL: Expected {expected}, got {actual}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    passed = test_{test_id_lower}()
    exit_code = 0 if passed else 1
    print(f"\nExit code: {exit_code}")
    sys.exit(exit_code)
```

### Master Runner (run_all.py)

```python
#!/usr/bin/env python3
"""
Master runner for all usage functions.
Tracks exit codes and provides summary.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_usage_function(file_path):
    """Run a usage function and return result."""
    print(f"\nRunning: {file_path}")
    result = subprocess.run(
        [sys.executable, str(file_path)],
        capture_output=True,
        text=True
    )
    
    return {
        'file': file_path.name,
        'exit_code': result.returncode,
        'passed': result.returncode == 0,
        'stdout': result.stdout,
        'stderr': result.stderr
    }


def main():
    """Run all usage functions."""
    usage_dir = Path(__file__).parent
    
    # Find all usage functions
    usage_files = []
    for category_dir in usage_dir.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith('__'):
            for py_file in category_dir.glob('*.py'):
                if not py_file.name.startswith('__'):
                    usage_files.append(py_file)
    
    print(f"Found {len(usage_files)} usage functions")
    
    # Run each function
    results = []
    for usage_file in sorted(usage_files):
        result = run_usage_function(usage_file)
        results.append(result)
        
        # Print immediate feedback
        status = "✅ PASS" if result['passed'] else "❌ FAIL"
        print(f"{status}: {result['file']}")
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print(f"{'='*60}")
    
    # Save detailed report
    report_path = usage_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w') as f:
        for result in results:
            f.write(f"\n{'='*60}\n")
            f.write(f"File: {result['file']}\n")
            f.write(f"Exit Code: {result['exit_code']}\n")
            f.write(f"Status: {'PASS' if result['passed'] else 'FAIL'}\n")
            f.write(f"\nOutput:\n{result['stdout']}\n")
            if result['stderr']:
                f.write(f"\nErrors:\n{result['stderr']}\n")
    
    print(f"\nDetailed report: {report_path}")
    
    # Exit with failure if any test failed
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
```

## 6. Conversion Strategy

### Phase 1: Critical Path (Tests that must work)
1. **Basic Operations** (F1.1-F1.3) - Core functionality
2. **Model Routing** (F2.1-F2.3) - Provider selection
3. **Configuration** (CF1.1-CF3.3) - Setup validation
4. **Error Handling** (E1.1-E3.3) - Graceful failures

### Phase 2: Feature Tests
5. **Validation** (V1.1-V3.3) - Output quality
6. **Conversation** (C1.1-C2.3) - State management
7. **Document Processing** (D1.1-D2.2) - Corpus handling
8. **Performance** (P1.1-P2.3) - Caching/speed

### Phase 3: Advanced Features
9. **Multimodal** (M1.1-M2.3) - Image analysis
10. **Integration** (I1.1-I3.3) - Cross-system
11. **Text Processing** (T1.1-T2.3) - NLP features
12. **Docker/MCP** - Deployment specific

## 7. Verification Instructions

### For Each Usage Function:
```bash
# Run the function
python src/llm_call/usage/functional/basic_operations.py

# Check exit code immediately
echo $?  # Should be 0 for pass, 1 for fail

# Run all and check overall status
python src/llm_call/usage/run_all.py
echo $?
```

### Key Points:
- **NEVER trust Claude's claims** about what passed/failed
- **ALWAYS check exit codes** yourself
- **Read the actual output** to see what happened
- **Save outputs** for later verification

## 8. Example Conversions

### Example 1: Basic Math Test (F1.1)
```python
def test_f1_1_openai_basic_math():
    """Test F1.1: Basic OpenAI math calculation"""
    print("\n" + "="*60)
    print("TEST F1.1: OpenAI Basic Math (2+2)")
    print("="*60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ FAIL: OPENAI_API_KEY not set")
        return False
    
    try:
        response = make_llm_request(
            prompt="What is 2+2?",
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        content = extract_content(response)
        print(f"Response: {content}")
        
        if "4" in str(content):
            print("✅ PASS: Response contains '4'")
            return True
        else:
            print(f"❌ FAIL: Expected '4' in response")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
```

### Example 2: Image Analysis (M1.1)
```python
def test_m1_1_claude_image_description():
    """Test M1.1: Claude image description"""
    print("\n" + "="*60)
    print("TEST M1.1: Claude Image Analysis")
    print("="*60)
    
    # Must unset for OAuth
    if os.getenv("ANTHROPIC_API_KEY"):
        print("❌ FAIL: ANTHROPIC_API_KEY must be unset for max/opus")
        return False
    
    test_image = "/path/to/coconut_image.png"
    if not os.path.exists(test_image):
        print(f"❌ FAIL: Test image not found: {test_image}")
        return False
    
    try:
        response = make_llm_request(
            prompt="Describe this image",
            model="max/opus",
            image=test_image
        )
        
        content = extract_content(response)
        print(f"Response: {content}")
        
        # Check for expected keywords
        keywords = ["coconut", "tropical", "palm"]
        found = [k for k in keywords if k in content.lower()]
        
        if found:
            print(f"✅ PASS: Found keywords: {found}")
            return True
        else:
            print(f"❌ FAIL: Expected keywords {keywords} not found")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False
```

## 9. Progress Tracking

### Immediate Actions:
1. Create directory structure
2. Convert first 5 tests as proof of concept
3. Verify exit codes work correctly
4. Convert remaining tests by category

### Milestones:
- [ ] Phase 1: Critical path tests (25 tests)
- [ ] Phase 2: Feature tests (35 tests)
- [ ] Phase 3: Advanced features (37 tests)
- [ ] Documentation and runner complete

## 10. Notes

### Why This Approach Works:
1. **Exit codes can't be hallucinated** - OS reports them
2. **Explicit output** shows what actually happened
3. **Independent verification** - run yourself, check yourself
4. **Simple structure** - easy to understand and debug

### Remember:
- Each function is standalone - can run individually
- Always print actual vs expected for debugging
- Exit code is the ONLY truth about pass/fail
- Claude Code's claims about results are irrelevant

This approach completely sidesteps the test reporting problem by making verification external and verifiable.