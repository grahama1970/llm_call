# Analysis: What's Missing from Task Lists for Code Executor Success

## Current Problems

1. **Too Much Theory, Not Enough Examples**
   - Tasks describe what to do conceptually
   - Missing concrete working code examples
   - No clear input/output pairs to test against

2. **Information Overload**
   - Long research sections that distract from implementation
   - Too many conceptual explanations
   - Code executor gets lost in documentation references

3. **Missing Concrete Test Data**
   - No exact test inputs from test_prompts.json
   - No expected outputs to validate against
   - No clear success criteria with specific values

## What the Code Executor Actually Needs

### 1. Working Code Examples First
Instead of: "Research LiteLLM routing patterns"
Provide: 
```python
# WORKING EXAMPLE - Copy this pattern:
from litellm import completion

# For OpenAI models:
response = completion(
    model="openai/gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello"}]
)

# For Claude proxy models:
response = completion(
    model="max/text-general",
    messages=[{"role": "user", "content": "Hello"}],
    api_base="http://localhost:8080"  # Claude proxy server
)
```

### 2. Exact Test Cases with Expected Results
For each test_prompts.json entry, provide:
```
TEST: max_text_001_simple_question
INPUT: {"model": "max/text-general", "question": "What is the primary function of a CPU in a computer?"}
EXPECTED OUTPUT STRUCTURE: {"content": "The CPU...", "model": "max/text-general", ...}
VALIDATION: Check content field exists and is not empty
RUN COMMAND: python test_single_case.py max_text_001_simple_question
```

### 3. Specific Validation Examples
Instead of: "Implement field validation"
Provide:
```python
# VALIDATION EXAMPLE - Field checking:
def validate_response(response):
    # Check 1: Response not empty
    assert response.get("content"), "Response content is empty"
    
    # Check 2: Specific fields exist
    required_fields = ["content", "model", "usage"]
    for field in required_fields:
        assert field in response, f"Missing required field: {field}"
    
    # Check 3: Content contains expected keywords
    content = response["content"].lower()
    assert "cpu" in content or "processor" in content, "Response doesn't mention CPU"
```

### 4. Common Pitfalls with Solutions
```python
# PITFALL 1: Claude proxy takes 7-15 seconds
# SOLUTION: Use async with timeout
async def call_with_timeout(model, messages, timeout=30):
    try:
        return await asyncio.wait_for(
            completion(model=model, messages=messages),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        # Implement polling logic here
        pass

# PITFALL 2: Message format differences
# SOLUTION: Normalize format
def normalize_messages(input_data):
    if "question" in input_data:
        return [{"role": "user", "content": input_data["question"]}]
    return input_data.get("messages", [])
```

## Recommended Task Structure

### BEFORE (Current Approach):
```
Task 1: Implement routing infrastructure
- Research LiteLLM patterns
- Create routing module
- Test with various models
- Document findings
```

### AFTER (Example-Driven Approach):
```
Task 1: Make test max_text_001_simple_question pass

WORKING CODE TO START WITH:
[paste exact working example]

TEST COMMAND:
python run_test.py max_text_001_simple_question

EXPECTED OUTPUT:
{
  "content": "The primary function of a CPU is...",
  "model": "max/text-general",
  "usage": {...}
}

IF IT FAILS WITH TIMEOUT:
[paste async solution]

IF IT FAILS WITH FORMAT ERROR:
[paste format conversion code]
```

## Key Improvements Needed

1. **Front-load working examples** - Don't make the executor search
2. **Provide exact test commands** - No ambiguity about what to run
3. **Show expected outputs** - Clear success criteria
4. **Include common fixes** - Pre-solve known issues
5. **Keep it focused** - One test case at a time
6. **Minimize research burden** - Provide the answers upfront
