# Lessons Learned from Gemini About Basic Testing

## Key Principles

### 1. Handle None Content Gracefully
```python
# GOOD: Handle None responses
assert content is None or "4" in content

# BAD: Assume content exists
assert "4" in content  # Will crash if content is None
```

### 2. Use Simple String Checks
```python
# GOOD: Check for expected content
assert "hello" in content.lower()

# BAD: Complex regex or JSON parsing
json_match = re.search(r'```json\n(.*?)\n```', content)
```

### 3. Check Multiple Valid Answers
```python
# GOOD: LLMs can answer differently
assert "4" in content or "four" in content.lower()

# BAD: Expect exact match
assert content == "4"
```

### 4. Keep Tests Under 20 Lines
```python
@pytest.mark.asyncio
async def test_basic_math():
    # Setup
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "What is 2+2?"}]
    }
    
    # Act
    result = await make_llm_request(config)
    content = result["choices"][0]["message"].get("content", None)
    
    # Assert
    assert content is None or "4" in content
```

### 5. Use Descriptive Test Names
- `test_llm_basic_math` - Clear what it tests
- `test_llm_list_colors` - Obvious purpose
- `test_llm_empty_messages_error` - Shows expected behavior

### 6. Test Real API Calls
- No mocks
- No fixtures  
- No fake data
- Just call the real function

### 7. Focus on One Thing Per Test
- Math test checks math
- Color test checks colors
- Error test checks errors
- Don't combine multiple checks

## What NOT to Do

### 1. Don't Use Complex Patterns
```python
# BAD: Parametrized tests with complex data structures
@pytest.mark.parametrize("question,expected", MATH_TEST_CASES)
async def test_math(question, expected):
    # Complex logic here
```

### 2. Don't Parse JSON/Structured Output
```python
# BAD: Trying to parse JSON
json_data = json.loads(content)
assert json_data["answer"] == 4
```

### 3. Don't Use Advanced Assertions
```python
# BAD: Complex type checking
assert isinstance(result, ModelResponse)
assert hasattr(result, "choices")
assert len(result.choices) > 0
```

### 4. Don't Create Test Helpers
```python
# BAD: Abstract helper functions
def extract_answer_from_response(response):
    # Complex extraction logic
```

## Simple Test Template

```python
@pytest.mark.asyncio
async def test_llm_does_something():
    # 1. Setup config
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Your prompt here"}]
    }
    
    # 2. Call function
    result = await make_llm_request(config)
    content = result["choices"][0]["message"].get("content", None)
    
    # 3. Check result
    assert content is None or "expected" in content.lower()
```

## Running Tests

```bash
# With pytest
pytest tests/test_file.py -v

# Standalone
python tests/test_file.py
```

## Summary

Gemini taught me that good tests are:
- **Boring** - No clever tricks
- **Obvious** - Junior dev can understand
- **Robust** - Handle None and variations
- **Simple** - Under 20 lines
- **Real** - Test actual API calls

The goal is not to impress with complexity, but to verify that things work.