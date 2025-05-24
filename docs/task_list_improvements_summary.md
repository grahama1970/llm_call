# Summary: Key Improvements for Task Lists

## What's Missing from Current Task Lists

### 1. **Concrete Working Examples**
Current tasks tell the executor to "research and implement" but don't provide working code to start from.

**Missing**:
- Complete, runnable code examples
- Exact API usage patterns
- Pre-tested solutions

**Needed**:
```python
# Like this - complete working example:
async def call_claude_proxy(model, question):
    async with aiohttp.ClientSession() as session:
        response = await session.post(
            "http://localhost:8080/v1/chat/completions",
            json={"model": model, "messages": [{"role": "user", "content": question}]}
        )
        return await response.json()
```

### 2. **Exact Test Data**
Tasks reference test cases but don't include the actual JSON.

**Missing**:
- The exact test case from test_prompts.json
- Expected response structure
- Specific validation criteria

**Needed**:
```json
// Include the EXACT test case:
{
    "test_case_id": "max_text_001_simple_question",
    "llm_config": {
        "model": "max/text-general",
        "question": "What is the primary function of a CPU in a computer?"
    }
}
```

### 3. **Pre-Solved Common Issues**
Tasks don't warn about known problems or provide solutions.

**Missing**:
- Timeout handling (Claude takes 7-15s)
- Format conversion (question vs messages)
- Async patterns for long-running calls

**Needed**:
```python
# Include solutions for known issues:
# ISSUE: Timeout
# SOLUTION: Use 30s timeout
timeout=aiohttp.ClientTimeout(total=30)

# ISSUE: Format mismatch
# SOLUTION: Convert question to messages
if "question" in config:
    messages = [{"role": "user", "content": config["question"]}]
```

### 4. **Simple Test Commands**
Tasks lack specific commands to verify success.

**Missing**:
- Exact command to run one test
- How to check if it passed
- Debug commands

**Needed**:
```bash
# Run this exact command:
python test_v4_essential_async.py -k max_text_001

# Or create single test file:
python test_single_max_text_001.py
```

### 5. **Clear Success Criteria**
Tasks have vague completion criteria.

**Missing**:
- Specific assertions that must pass
- Expected output examples
- Pass/fail indicators

**Needed**:
```python
# This test passes when ALL of these are true:
assert "choices" in response
assert response["choices"][0]["message"]["content"]
assert "cpu" in response["choices"][0]["message"]["content"].lower()
print("✅ PASSED: max_text_001_simple_question")
```

## Recommended Changes to Task Structure

### From Research-Heavy to Example-Driven

**OLD APPROACH**:
```
Task 1: Research and implement routing
- Study LiteLLM documentation
- Understand model routing patterns  
- Implement flexible routing system
- Test with various models
```

**NEW APPROACH**:
```
Task 1: Make max_text_001 pass
[Working code example]
[Exact test command]
[Expected output]
[Common fixes]
```

### From Groups to Individual Tests

**OLD**: "Implement all basic text scenarios"
**NEW**: "Make test max_text_001_simple_question pass"

### From Theory to Practice

**OLD**: "Implement validation strategies"
**NEW**: "Make this exact validation work: assert 'cpu' in response.lower()"

## Updated Task List Structure

Each task should be:
1. **Focused**: One test case only
2. **Concrete**: Working code provided
3. **Testable**: Exact command to verify
4. **Debuggable**: Common issues pre-solved
5. **Brief**: Under 100 lines total

## Benefits for Code Executor

1. **No Research Needed**: Solutions provided upfront
2. **Clear Target**: One specific test to pass
3. **Less Confusion**: No theory or documentation diving
4. **Faster Success**: Common issues already solved
5. **Obvious Progress**: Each test either passes or fails

## Implementation Priority

1. Start with simplest tests (max_text_001)
2. Provide complete working examples
3. Include exact test data
4. Pre-solve timeout and format issues
5. Give clear pass/fail output

The key insight: Code executors work best with concrete examples and clear targets, not abstract research tasks.
