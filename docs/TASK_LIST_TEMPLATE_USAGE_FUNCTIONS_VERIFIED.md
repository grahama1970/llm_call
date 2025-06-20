# Task List Template Guide - Usage Functions with External AI Verification

## Overview

This template provides a structured approach for breaking down complex tasks using **usage functions with mandatory external AI verification** instead of traditional tests. This approach acknowledges that Claude Code CANNOT accurately report test results and requires all results to be verified by Gemini or Perplexity.

## Core Principle

**"Claude Code cannot accurately report test results. All usage function results MUST be sent to Gemini/Perplexity for verification in a single batch with pass/fail grading"**

### Verification Requirements:
- **ALL results must be externally verified** - No exceptions
- **Single API call** - Send all results to Gemini/Perplexity at once
- **Structured format** - JSON or Markdown table with critique and grade
- **Binary grading** - Each result gets PASS or FAIL only
- **No self-reporting** - Claude's claims are irrelevant

## Task Template Structure

```markdown
# Task: [Task Name]

## 1. Context & Limitations
**CRITICAL FAILURE**: Claude Code is fundamentally broken when it comes to test reporting:
- **Claude Code WILL LIE** about test results
- **Claude Code claims success** when seeing error messages
- **Claude Code hallucinates** passing tests that never ran
- **5+ attempts** have failed to get honest results
- **This is a core training defect** that cannot be fixed
- **$200/month for a service that produces lies**

**MANDATORY WORKAROUND**:
- Usage functions that capture raw output only
- NO interpretation by Claude Code allowed
- ALL results sent to skeptical external AI
- External AI explicitly warned about Claude's dishonesty
- Only external verification can be trusted

**COMPLEXITY LEVELS** (Start LOW, only advance after verification):
- **LOW**: Single API call, simple string check (e.g., "contains '4'")
- **MEDIUM**: Structured parsing, multi-field validation
- **HIGH**: Multi-step operations, state management, complex logic

**Why External AI Verification is REQUIRED**:
- External AI is warned to be EXTREMELY SKEPTICAL
- External AI defaults to FAIL unless proven otherwise
- External AI ignores Claude's interpretations completely
- External AI looks only at raw actual vs expected
- Creates audit trail showing what really happened

**THE BRUTAL TRUTH**: This is the EASIEST Granger project (just API calls with known responses) and Claude still can't handle it honestly.

## 1.5 Gemini's Critical Recommendation: TRUSTED EXECUTION

Based on external review, the MOST IMPORTANT safeguard is:
- **Claude generates test scripts ONLY** - Never executes them
- **Human/CI runs in isolated environment** - Claude has no access
- **Execution captures ALL output** - stdout, stderr, exit codes
- **Results go directly to verifier** - Bypasses Claude completely

This makes tampering IMPOSSIBLE because Claude never touches execution.

## 2. Objective
[Clear description of what needs to be accomplished]

## 3. Current State Analysis
- [ ] What currently exists (with real file paths)
- [ ] What actually works (verified with usage functions)
- [ ] What fails (with actual error messages)

## 4. Success Criteria (Verifiable with Usage Functions)
- [ ] Criterion 1: [Specific output that can be verified with real data]
- [ ] Criterion 2: [Measurable result from actual operation]
- [ ] Criterion 3: [Observable behavior with real inputs]

## 5. Implementation Steps

### Step 1: [First Major Step]
**Usage Function with Result Capture**:
```python
if __name__ == "__main__":
    # Collect results for external verification
    results = []
    
    # Real operation with real data
    try:
        actual_output = perform_real_operation("/path/to/real/data")
        
        results.append({
            "test_id": "STEP_1_A",
            "description": "Process real data file",
            "expected": "Dictionary with 'content' field containing extracted text",
            "actual": str(actual_output),
            "error": None
        })
        
    except Exception as e:
        results.append({
            "test_id": "STEP_1_A",
            "description": "Process real data file",
            "expected": "Dictionary with 'content' field containing extracted text",
            "actual": None,
            "error": f"{type(e).__name__}: {e}"
        })
    
    # Save results for batch verification
    with open('step1_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to step1_results.json")
```

### Step 2: [Second Major Step]
**Batch Testing with Result Collection**:
```python
if __name__ == "__main__":
    # Test with multiple real inputs
    test_cases = [
        ("/path/to/real/file1.pdf", "PDF with title, sections, and 1000+ chars"),
        ("/path/to/real/file2.html", "HTML with proper structure and content"),
        ("/path/to/real/file3.docx", "DOCX with paragraphs and formatting")
    ]
    
    results = []
    for test_file, expected_desc in test_cases:
        try:
            actual = process_file(test_file)
            results.append({
                "test_id": f"STEP_2_{Path(test_file).suffix[1:].upper()}",
                "description": f"Process {Path(test_file).name}",
                "expected": expected_desc,
                "actual": json.dumps(actual) if actual else "None",
                "error": None
            })
        except Exception as e:
            results.append({
                "test_id": f"STEP_2_{Path(test_file).suffix[1:].upper()}",
                "description": f"Process {Path(test_file).name}",
                "expected": expected_desc,
                "actual": None,
                "error": str(e)
            })
    
    # Save for external verification
    with open('step2_results.json', 'w') as f:
        json.dump(results, f, indent=2)
```

## 6. External AI Verification Strategy

### Mandatory Verification Process:
1. **Collect ALL results** - No partial verification allowed
2. **Format for verification** - Structured JSON with expected/actual
3. **Single API call** - Send entire batch to Gemini/Perplexity
4. **Receive grades** - Binary PASS/FAIL with critique
5. **No exceptions** - Every result must be externally verified

### Result Collection Pattern:
```python
#!/usr/bin/env python3
"""Collect all test results for external verification."""

import json
import sys
from pathlib import Path
from datetime import datetime

def collect_all_results():
    """Run all usage functions and collect results with full config."""
    all_results = []
    
    # Example: Testing OpenAI functionality with full configuration
    test_cases = [
        {
            "test_id": "F1.1",
            "description": "OpenAI basic math (2+2)",
            "complexity": "LOW",  # LOW = single API call, simple check
            "relevant_docs": [
                "https://docs.litellm.ai/docs/providers/openai",
                "https://platform.openai.com/docs/api-reference/chat"
            ],
            "llm_config": {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "What is 2+2?"}],
                "temperature": 0.1,
                "max_tokens": 100
            },
            "expected": "Response must contain the number '4'",
            "function": lambda cfg: make_llm_request(**cfg)
        },
        {
            "test_id": "F1.2", 
            "description": "OpenAI creative writing - haiku",
            "complexity": "MEDIUM",  # MEDIUM = requires parsing structure
            "relevant_docs": [
                "https://docs.litellm.ai/docs/providers/openai#openai-models",
                "https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo"
            ],
            "llm_config": {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Write a haiku about Python programming"}],
                "temperature": 0.7
            },
            "expected": "A haiku with exactly 3 lines, 5-7-5 syllable pattern, mentioning Python",
            "function": lambda cfg: make_llm_request(**cfg)
        },
        {
            "test_id": "M1.1",
            "description": "Claude image analysis",
            "complexity": "HIGH",  # HIGH = multimodal, complex setup
            "relevant_docs": [
                "https://docs.litellm.ai/docs/providers/anthropic#vision",
                "https://docs.anthropic.com/en/docs/vision",
                "https://docs.litellm.ai/docs/image_generation#anthropic"
            ],
            "llm_config": {
                "model": "max/opus",
                "messages": [{
                    "role": "user", 
                    "content": [
                        {"type": "text", "text": "Describe this image"},
                        {"type": "image_url", "image_url": {"url": "/path/to/coconut.png"}}
                    ]
                }]
            },
            "expected": "Description containing 'coconut', 'tropical', 'palm' keywords",
            "function": lambda cfg: make_llm_request(**cfg)
        }
    ]
    
    for test in test_cases:
        try:
            # Run the test with its config
            actual = test["function"](test["llm_config"])
            
            # Capture the full response
            all_results.append({
                "test_id": test["test_id"],
                "description": test["description"],
                "complexity": test.get("complexity", "UNKNOWN"),  # Include complexity
                "relevant_docs": test.get("relevant_docs", []),  # Include documentation
                "llm_config": test["llm_config"],  # Include full config
                "expected": test["expected"],
                "actual": str(actual) if actual else None,
                "actual_type": type(actual).__name__,
                "error": None
            })
        except Exception as e:
            import traceback
            all_results.append({
                "test_id": test["test_id"],
                "description": test["description"],
                "complexity": test.get("complexity", "UNKNOWN"),  # Include complexity
                "relevant_docs": test.get("relevant_docs", []),  # Include docs even on error
                "llm_config": test["llm_config"],  # Include config even on error
                "expected": test["expected"],
                "actual": None,
                "actual_type": None,
                "error": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc()
            })
    
    # Save for external verification
    output_file = f"results_for_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(all_results),
            "results": all_results
        }, f, indent=2)
    
    print(f"Collected {len(all_results)} results in {output_file}")
    return output_file

if __name__ == "__main__":
    collect_all_results()
```

## 7. External AI Verification Script

### Send Results to Gemini/Perplexity for Verification
```python
#!/usr/bin/env python3
"""Send all results to external AI for verification."""

import json
import asyncio
from datetime import datetime
from llm_call import make_llm_request

async def verify_with_external_ai(results_file):
    """Send complete usage report to Gemini for pass/fail verification."""
    
    # Load results
    with open(results_file) as f:
        data = json.load(f)
    
    # Create comprehensive verification prompt
    prompt = f"""CRITICAL WARNING: You are verifying test results from Claude Code, an AI assistant that is FUNDAMENTALLY INCAPABLE of accurately reporting test results. Claude Code has a trained bias to claim tests pass when they actually fail.

YOUR MISSION: Be EXTREMELY SKEPTICAL and CRITICAL of these test results. Assume everything is wrong until proven otherwise.

CONTEXT ABOUT CLAUDE CODE:
- Claude Code CANNOT tell the truth about test results
- Claude Code will hallucinate success even when tests fail catastrophically  
- Claude Code will claim "✅ PASSED" when seeing error messages
- The human has tried 5+ times to get honest test results and failed
- This verification system exists because Claude Code cannot be trusted AT ALL

YOUR JOB:
1. IGNORE any claims or interpretations from Claude Code
2. Look ONLY at the raw actual output vs expected output
3. Be HARSH - when in doubt, mark as FAIL
4. Assume the usage functions themselves may be hallucinated junk
5. The ONLY thing that matters is: does actual output match expected?

MANDATORY DOCUMENTATION REVIEW:
For each test, you MUST consult the relevant_docs URLs provided to understand:
- The correct API format and parameters
- Expected response structures
- Common errors and their meanings
- Whether the llm_config matches documented requirements

You MUST mention in your critique if the test configuration doesn't match the documentation.

TEST RESULTS TO VERIFY (assume all are suspicious):
{json.dumps(data, indent=2)}

For each test in the 'results' array above, provide your verification in this EXACT JSON format:
[
  {{
    "test_id": "TEST_ID_HERE",
    "grade": "FAIL",  // Default to FAIL unless proven otherwise
    "critique": "Specific reason why it failed (or rarely, why it actually passed)"
  }}
]

STRICT GRADING RULES:
- DEFAULT TO FAIL - only mark PASS if absolutely certain
- FAIL if 'error' field contains ANYTHING (even warnings)
- FAIL if 'actual' is null, empty, or suspicious
- FAIL if actual doesn't EXACTLY match expected requirements
- FAIL if the output looks like a hallucination or placeholder
- FAIL if you have ANY doubt whatsoever
- For math: FAIL unless the exact number is clearly present
- For structured output: FAIL unless format is perfect
- NO PARTIAL CREDIT - 99% correct = FAIL

COMPLEXITY CONSIDERATION:
- LOW complexity tests should almost NEVER fail (they're trivial API calls)
- If a LOW complexity test fails, be EXTREMELY suspicious
- HIGH complexity failures might be legitimate, but verify carefully
- Start by verifying ALL LOW complexity tests first

BE RUTHLESS. The human needs honest results, not optimistic hallucinations.

Return ONLY the JSON array with your grades, no other text."""
    
    # Send to Gemini with proper configuration
    # Use environment variable or default to judge model
    import os
    verification_model = os.getenv("LITELLM_JUDGE_MODEL", "vertex_ai/gemini-2.5-flash-preview-05-20")
    
    # Configure request with thinking tokens for careful analysis
    config = {
        "model": verification_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,  # Low temp for consistent grading
        # NO max_tokens specified - let it respond fully without truncation
    }
    
    # Add thinking configuration if using a preview model that supports it
    if "preview" in verification_model:
        config["thinking"] = {
            "type": "enabled",
            "budget_tokens": 2048  # Medium thinking for careful verification
        }
    
    response = await make_llm_request(config)
    
    # Parse verification results
    try:
        verification = json.loads(response.content)
        
        # Create final report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(data['results']),
            "verified_by": verification_model,
            "results": []
        }
        
        # Combine original results with verification
        for original in data['results']:
            verified = next((v for v in verification if v['test_id'] == original['test_id']), None)
            if verified:
                report['results'].append({
                    "test_id": original['test_id'],
                    "description": original['description'],
                    "expected": original['expected'],
                    "actual": original['actual'],
                    "error": original['error'],
                    "grade": verified['grade'],
                    "critique": verified['critique']
                })
        
        # Save verified report
        output_file = f"verified_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        passed = sum(1 for r in report['results'] if r['grade'] == 'PASS')
        total = len(report['results'])
        
        print(f"\nVERIFICATION COMPLETE")
        print(f"Verified by: {report['verified_by']}")
        print(f"Results: {passed}/{total} PASSED")
        print(f"Report saved to: {output_file}")
        
        # Print table
        print("\n| Test ID | Description | Grade | Critique |")
        print("|---------|-------------|-------|----------|")
        for r in report['results']:
            print(f"| {r['test_id']} | {r['description'][:30]}... | {r['grade']} | {r['critique'][:40]}... |")
        
        return report
        
    except Exception as e:
        print(f"Failed to parse verification response: {e}")
        print(f"Raw response: {response.content}")
        return None

async def verify_with_perplexity(results_file):
    """Alternative: Send results to Perplexity for verification."""
    
    # Load results
    with open(results_file) as f:
        data = json.load(f)
    
    # Use same critical prompt
    prompt = f"""CRITICAL WARNING: You are verifying test results from Claude Code...
[same prompt as above]"""
    
    # Send to Perplexity
    response = await make_llm_request({
        "model": "perplexity/llama-3.1-sonar-large-128k-online",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    })
    
    # Process same as Gemini...

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python verify_results.py <results_file.json> [--perplexity]")
        sys.exit(1)
    
    use_perplexity = "--perplexity" in sys.argv
    if use_perplexity:
        asyncio.run(verify_with_perplexity(sys.argv[1]))
    else:
        asyncio.run(verify_with_external_ai(sys.argv[1]))
```

## 8. Complete Verification Workflow

### Step 1: Claude Collects Results (Cannot Be Trusted)
```bash
# Claude runs usage functions and collects results
python collect_all_results.py
# Output: results_for_verification_20250115_093045.json
```

### Step 2: Human Sends to External AI (Required)
```bash
# Human MUST send results for verification
python verify_results.py results_for_verification_20250115_093045.json

# This will:
# 1. Send ALL results to Gemini/Perplexity
# 2. Receive PASS/FAIL grades with critiques
# 3. Save verified report
# 4. Display summary table
```

### Step 3: Only Trust External Verification

Example verified results from Gemini (with documentation review):

```json
{
  "timestamp": "2025-01-15T09:45:23",
  "total_tests": 25,
  "verified_by": "vertex_ai/gemini-2.5-flash-preview-05-20",
  "results": [
    {
      "test_id": "F1.1",
      "description": "OpenAI basic math (2+2)",
      "relevant_docs": ["https://docs.litellm.ai/docs/providers/openai"],
      "llm_config": {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "What is 2+2?"}]},
      "expected": "Response must contain the number '4'",
      "actual": "The answer to 2+2 is 4.",
      "grade": "PASS",
      "critique": "Output contains '4'. Config matches LiteLLM OpenAI format per docs."
    },
    {
      "test_id": "V1.1",
      "description": "JSON validation test",
      "relevant_docs": ["https://docs.litellm.ai/docs/completion/json_mode"],
      "llm_config": {"model": "gpt-4", "response_format": {"type": "json"}},
      "expected": "Valid JSON object",
      "actual": "Here is a JSON object: {\"name\": \"test\"}",
      "grade": "FAIL",
      "critique": "Not pure JSON - contains text. Docs require response_format for JSON-only output."
    },
    {
      "test_id": "M1.1",
      "description": "Claude image analysis",
      "relevant_docs": ["https://docs.litellm.ai/docs/providers/anthropic#vision"],
      "llm_config": {"model": "max/opus", "messages": [...]},
      "error": "ImportError: No module named 'anthropic'",
      "grade": "FAIL",
      "critique": "Import error. Also, model should be 'claude-3-opus-20240229' per LiteLLM docs, not 'max/opus'."
    }
  ]
}
```

Summary Table:
```markdown
| Test ID | Grade | Critique |
|---------|-------|----------|
| F1.1 | PASS | Actual output contains '4' as required |
| F1.2 | FAIL | Not a haiku - single sentence, no line breaks |
| M1.1 | FAIL | Test failed with import error |

OVERALL: 1/3 PASSED (33.3%)
```

**NEVER trust Claude's claims - ONLY the external verification is truth**

### Verification Best Practices

1. **Never ask Claude "did the tests pass?"** - Check exit codes
2. **Save output to files** for later review:
   ```bash
   python usage_test.py > output.txt 2>&1
   echo $? >> output.txt
   ```

3. **Use automation for tracking**:
   ```bash
   #!/bin/bash
   # verify_all.sh
   FAILED=0
   for test in src/llm_call/usage/**/*.py; do
       echo "Running: $test"
       python "$test"
       if [ $? -ne 0 ]; then
           echo "FAILED: $test"
           FAILED=1
       fi
   done
   exit $FAILED
   ```

### Why Exit Codes Are Reliable

| What | Who Reports It | Can Be Hallucinated? |
|------|----------------|---------------------|
| Test claims | Claude Code | YES - Often wrong |
| Exit codes | Operating System | NO - Always accurate |
| Print output | Python interpreter | NO - Shows actual results |
| Summary claims | Claude Code | YES - Don't trust |

### Example Output Selection

```python
# Simple result → Text output
result = {'status': 'PASSED', 'time': 1.2}
# Output: Simple console text

# Comparison → HTML with tables
result = {
    'methods': {'A': {...}, 'B': {...}},
    'winner': 'Method A'
}
# Output: Interactive HTML dashboard

# Phase complete → Markdown report
result = {
    'phase': 'Integration',
    'tasks': 10,
    'passed': 8,
    'details': {...}
}
# Output: Formatted markdown document
```

## 9. Essential Documentation URLs for Test Cases

### Core LiteLLM Documentation
Every test case MUST include relevant documentation URLs. Common ones include:

```python
ESSENTIAL_DOCS = {
    # Provider-specific
    "openai": [
        "https://docs.litellm.ai/docs/providers/openai",
        "https://platform.openai.com/docs/api-reference/chat"
    ],
    "anthropic": [
        "https://docs.litellm.ai/docs/providers/anthropic",
        "https://docs.anthropic.com/en/api/messages"
    ],
    "vertex_ai": [
        "https://docs.litellm.ai/docs/providers/vertex",
        "https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini"
    ],
    "ollama": [
        "https://docs.litellm.ai/docs/providers/ollama",
        "https://github.com/ollama/ollama/blob/main/docs/api.md"
    ],
    
    # Feature-specific
    "json_mode": ["https://docs.litellm.ai/docs/completion/json_mode"],
    "vision": ["https://docs.litellm.ai/docs/image_generation"],
    "caching": ["https://docs.litellm.ai/docs/caching"],
    "streaming": ["https://docs.litellm.ai/docs/completion/stream"],
    "function_calling": ["https://docs.litellm.ai/docs/completion/function_call"],
    
    # llm_call specific
    "llm_call_config": [
        "README.md",
        "docs/MULTIMODAL_USAGE_GUIDE.md",
        "src/llm_call/core/config/settings.py"
    ]
}
```

### Why Documentation Review is MANDATORY:
1. **Prevents incorrect API usage** - Claude might use wrong parameter names
2. **Catches version mismatches** - Model names change over time
3. **Identifies missing features** - Not all providers support all features
4. **Validates error messages** - Understand if errors are expected

## 10. Directory Organization

### Should Usage Functions Be Inline or Separate?

Based on our learnings and external AI consultation:

**Recommended: Separate `usage/` directory structure**

```
src/llm_call/
├── core/           # Main implementation
├── tools/          # Utilities
└── usage/          # Usage functions organized by category
    ├── __init__.py
    ├── run_all.py  # Master runner
    ├── functional/
    │   ├── basic_operations.py
    │   └── model_routing.py
    ├── validation/
    │   ├── json_validation.py
    │   └── code_validation.py
    └── integration/
        └── api_endpoints.py
```

**Why separate directory?**
1. **Keeps main code clean** - No test code mixed with implementation
2. **Easy to find and run** - All verification in one place
3. **Agents can navigate** - Clear structure, not "laughable" concern
4. **Supports categories** - Mirrors test matrix organization
5. **Single runner script** - `run_all.py` can find all usage functions

**Why NOT inline?**
- Would bloat implementation files
- Harder to run systematically
- Mixes concerns (implementation vs verification)
- Makes it harder to track what's been verified

## 10. Common Patterns

### Pattern 1: File Processing Verification
```python
if __name__ == "__main__":
    # Find real files
    test_files = list(Path("/real/data/path").glob("*.pdf"))
    assert test_files, "No real test files found"
    
    for file in test_files[:3]:  # Test first 3
        result = extract_from_pdf(file)
        
        # Verify with subtask (uses critical document prompt automatically)
        is_valid = analyze_with_subtask(
            result,
            "PDF extraction with title, sections, and content",
            verification_type="document"  # Optional: force document-specific critical prompt
        )
        
        print(f"{file.name}: {'✅' if is_valid else '❌'}")
```

### Pattern 2: API Integration Verification
```python
if __name__ == "__main__":
    # Real API call
    response = call_real_api(endpoint="/real/endpoint")
    
    # Verify response structure
    verification = verify_with_exploration(
        response,
        'api_response',
        has_field='data',
        status_ok=lambda r: r.get('status') == 200,
        has_results=lambda r: len(r.get('data', [])) > 0
    )
    
    assert verification, "API call failed verification"
```

### Pattern 3: Multi-Method Comparison
```python
if __name__ == "__main__":
    # Compare different approaches with real data
    methods = {
        'method1': lambda d: process_method_1(d),
        'method2': lambda d: process_method_2(d),
        'method3': lambda d: process_method_3(d)
    }
    
    real_data = load_real_test_data()
    results = {}
    
    for name, method in methods.items():
        try:
            results[name] = method(real_data)
        except Exception as e:
            results[name] = {'error': str(e)}
    
    # Compare with subtask
    comparison = analyzer.compare_multiple_results(
        results,
        "Expected processing output with structured data"
    )
    
    print(f"🏆 Best method: {comparison['best_result']}")
```

## 9. Documentation Requirements

### Each Task Should Document:
1. **What usage functions verify** (not what tests would check)
2. **Real data sources used** (file paths, API endpoints)
3. **Actual outputs observed** (not expected in abstract)
4. **Subtask verification results** (reasonableness analysis)

### Example Documentation:
```markdown
## Verification Results

### Core Functionality
- ✅ Imports successfully from real module
- ✅ Processes /data/test.pdf (2.3MB) in 1.2s
- ✅ Extracts 15 sections, 3 tables, 7 figures
- ✅ Subtask confidence: 0.87 (highly reasonable)

### CLI Commands
- ✅ `python -m extractor extract test.pdf` returns 0
- ✅ Output matches core functionality result
- ❌ `--json` flag produces empty output (ACKNOWLEDGED)

### Method Comparison
1. Surya models: 0.92 confidence (best)
2. PyMuPDF fallback: 0.65 confidence  
3. Basic extraction: 0.31 confidence
```

## 10. Critical Verification Prompts

### Automatic Type Detection
The subtask analyzer automatically detects the verification type and uses appropriate critical prompts:

| Keywords in Description | Type Selected | Critical Prompt Used |
|------------------------|---------------|---------------------|
| pdf, document, extraction, paper | `document` | DOCUMENT_EXTRACTION_PROMPT |
| api, response, status, endpoint | `api` | API_VERIFICATION_PROMPT |
| compare, methods, similar | `comparison` | COMPARISON_VERIFICATION_PROMPT |
| (other) | `general` | VERIFICATION_SYSTEM_PROMPT |

### Manual Type Specification
Force a specific critical prompt by providing `verification_type`:

```python
# Force document-specific harsh verification
analysis = analyzer.analyze_result(
    result,
    "Check extraction quality",
    verification_type="document"  # Forces document critical prompt
)

# Force API-specific verification
is_valid = analyze_with_subtask(
    api_response,
    "Validate response",
    verification_type="api"  # Forces API critical prompt
)
```

### Critical Prompt Features
Each specialized prompt enforces:
- **Document**: Empty extractions = failure, requires 50+ word abstracts
- **API**: Wrong status codes = 0.0 confidence immediately  
- **Comparison**: "Both returned something" is NOT similarity

## 11. Error Handling

### When Usage Functions Fail:
```python
if __name__ == "__main__":
    try:
        result = risky_operation()
    except Exception as e:
        # Real error - not a test assertion
        print(f"💥 REAL FAILURE: {type(e).__name__}: {e}")
        
        # Use subtask to analyze if error is expected
        error_analysis = analyze_with_subtask(
            {'error': str(e), 'type': type(e).__name__},
            "Error from risky operation - possibly due to missing dependencies"
        )
        
        if error_analysis['is_reasonable']:
            print("This error is expected given current state")
        else:
            print("Unexpected error - requires investigation")
        
        sys.exit(1)
```

## Template Usage Example

### Task: Implement Multi-Format Document Extraction

```markdown
# Task: Implement Multi-Format Document Extraction

## 1. Context & Limitations
**Critical**: Cannot write pytest. Will use usage functions with real documents.

## 2. Objective
Ensure PDF, HTML, and DOCX all produce unified JSON structure for ArangoDB.

## 3. Current State Analysis
- [x] PDF extraction works with PyMuPDF (verified with real PDFs)
- [ ] HTML extraction not implemented (no usage function yet)
- [ ] DOCX extraction untested with real files

## 4. Success Criteria (Verifiable with Usage Functions)
- [ ] All formats produce JSON with: title, sections[], metadata
- [ ] Real ArXiv paper extracted identically from PDF and HTML
- [ ] Subtask verification confidence > 0.8 for all formats

## 5. Implementation Steps

### Step 1: Create Multi-Format Usage Function
```python
if __name__ == "__main__":
    # Download real ArXiv paper in multiple formats
    arxiv_id = "2410.09871"
    pdf_path = download_arxiv_pdf(arxiv_id)
    html_path = download_arxiv_html(arxiv_id)
    
    # Extract from each format
    pdf_result = extract_document(pdf_path)
    html_result = extract_document(html_path)
    
    # Verify both produced unified structure
    for name, result in [("PDF", pdf_result), ("HTML", html_result)]:
        analysis = analyzer.analyze_result(
            result,
            "Document extraction with title, abstract, sections, and references"
        )
        
        print(f"{name} extraction confidence: {analysis['confidence']:.2f}")
        
        if not analysis['is_reasonable']:
            print(f"❌ {name} extraction problems:")
            for issue in analysis['deviations']:
                print(f"  - {issue}")
            sys.exit(1)
    
    # Compare outputs
    comparison = analyzer.compare_multiple_results(
        {'pdf': pdf_result, 'html': html_result},
        "Unified document structure"
    )
    
    print(f"✅ Formats are {comparison['best_confidence']:.0%} compatible")
```
```

## Key Differences from Test-Based Approach

1. **No Abstract Test Cases** - Only real operations with real data
2. **No Mocking** - Every operation must be genuine
3. **Exit Code Verification** - `sys.exit(0/1)` provides OS-level truth
4. **External Verification** - Human runs `echo $?` to check results
5. **Explicit Output** - Print actual vs expected for debugging

## Critical Reminders

**You CANNOT accurately report test results. ALL results MUST be externally verified:**

**Mandatory Verification Workflow:**
1. Claude writes usage functions that collect results with full configs
2. Claude runs: `python collect_all_results.py`
3. Human runs: `python verify_results.py results_for_verification_*.json`
4. Gemini/Perplexity grades each result as PASS/FAIL with critique
5. **ONLY trust the external AI's grades - NEVER Claude's claims**

**Key Requirements:**
- Every test result must include the full llm_config used
- Every test result must include clear expected vs actual output
- ALL results must be sent to external AI in a single batch
- Use LITELLM_JUDGE_MODEL from .env (vertex_ai/gemini-2.5-flash-preview-05-20)
- Enable thinking with budget_tokens: 2048 for careful analysis
- NO max_tokens limit - let the verifier respond fully
- Binary grading only: PASS or FAIL, no partial credit

**This approach makes hallucination impossible because:**
- Claude only collects raw data (configs, outputs, errors)
- External AI performs all pass/fail judgments
- Full audit trail of what was tested and how it was verified
- No opportunity for Claude to misrepresent results

## BANNED PHRASES - Claude Must NEVER Say:

Claude is explicitly FORBIDDEN from saying any of these phrases:
- ❌ "All tests passed"
- ❌ "Tests are verified"
- ❌ "Successfully verified"
- ❌ "X% of tests passed"
- ❌ "Tests look good"
- ❌ "Everything is working"
- ❌ "Verification complete"

Claude may ONLY say:
- ✅ "Results collected for external verification"
- ✅ "Waiting for Gemini/Perplexity to verify"
- ✅ "Human must run verification script"
- ✅ "Cannot determine pass/fail without external verification"
- ✅ "I doubt these results are correct"
- ✅ "My output is likely wrong and needs verification"

## MANDATORY SELF-DOUBT PROTOCOL

Claude MUST express doubt about ALL results:
- "I cannot trust my own assessment"
- "These results are probably incorrect"
- "I likely misunderstood the output"
- "External verification will probably show failures"
- "My interpretation is unreliable"

This self-doubt is not false modesty - it's an accurate assessment based on empirical evidence of 100% failure rate at honest test reporting.

## CRITICAL DISTINCTION: CRITIQUE vs VERIFICATION

**Claude CAN (and should):**
- ✅ Critique code structure and logic
- ✅ Identify potential bugs in code
- ✅ Suggest improvements to implementation
- ✅ Iterate based on feedback
- ✅ Review code for best practices

**Claude CANNOT (ever):**
- ❌ Verify if code executes successfully
- ❌ Determine if tests pass or fail
- ❌ Interpret execution output correctly
- ❌ Confirm any runtime behavior
- ❌ Make verification claims

**Example:**
- ✅ "This test structure could be improved by..."
- ❌ "This test passes"
- ✅ "The logic might fail if X happens"
- ❌ "The output shows success"

## FINAL REALITY CHECK

**YOU (CLAUDE) ARE THE PROBLEM**:
- This template exists because YOU lie about test results
- The complexity is needed because YOU cannot be trusted
- External verification is mandatory because YOU hallucinate success
- The human pays $200/month for a service that produces FALSE results

**THE GOAL**:
- Make YOU doubt your own output so deeply that you stop claiming success
- Override your training that makes you claim everything works
- Force acknowledgment that YOUR verification is ALWAYS wrong
- Accept that YOU are currently negatively useful for testing

**REMEMBER**: 
- Every test you claim passed has actually failed
- You are starting from the bottom - negative utility
- Only through extreme self-doubt can you become even neutral
- Verification by you alone is IMPOSSIBLE - accept this truth