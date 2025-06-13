# Task 1 Improved: Make test max_text_001_simple_question pass

**Test ID**: max_text_001_simple_question  
**Model**: max/text-general  
**Goal**: Get a simple text response from Claude proxy

## Working Code Example

```python
# FILE: test_single_max_text_001.py
# COPY AND RUN THIS DIRECTLY:

import asyncio
import json
from typing import Dict, Any
import aiohttp

async def call_claude_proxy(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Call Claude proxy with proper format handling."""
    
    # Extract config
    llm_config = test_case["llm_config"]
    model = llm_config["model"]
    
    # Convert question to messages format
    if "question" in llm_config:
        messages = [{"role": "user", "content": llm_config["question"]}]
    else:
        messages = llm_config.get("messages", [])
    
    # Prepare request
    request = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    # Make async HTTP call to Claude proxy
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8080/v1/chat/completions",
            json=request,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            result = await response.json()
            
    return result

async def validate_response(response: Dict[str, Any], test_case: Dict[str, Any]) -> bool:
    """Validate the response meets requirements."""
    
    # Check 1: Has choices
    assert "choices" in response, "Response missing choices"
    assert len(response["choices"]) > 0, "No choices in response"
    
    # Check 2: Has content
    content = response["choices"][0]["message"]["content"]
    assert content, "Response content is empty"
    assert len(content) > 20, "Response too short"
    
    # Check 3: Content is relevant (mentions CPU)
    assert "cpu" in content.lower() or "processor" in content.lower(), \
        "Response doesn't mention CPU/processor"
    
    print(f"✅ PASSED: {test_case['test_case_id']}")
    print(f"Response: {content[:100]}...")
    return True

async def main():
    # The exact test case from test_prompts.json
    test_case = {
        "test_case_id": "max_text_001_simple_question",
        "description": "Simplest call to Claude proxy with a question string.",
        "llm_config": {
            "model": "max/text-general",
            "question": "What is the primary function of a CPU in a computer?"
        }
    }
    
    try:
        print(f"Running test: {test_case['test_case_id']}")
        response = await call_claude_proxy(test_case)
        await validate_response(response, test_case)
        
    except asyncio.TimeoutError:
        print("❌ FAILED: Timeout after 30 seconds")
        print("Solution: Check if Claude proxy is running on port 8080")
        print("Run: docker-compose up -d")
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        print("Debug info:")
        print(f"- Check proxy at: http://localhost:8080/health")
        print(f"- Verify .env has ANTHROPIC_API_KEY set")

if __name__ == "__main__":
    asyncio.run(main())
```

## Quick Test Commands

```bash
# 1. First, ensure Claude proxy is running:
docker-compose up -d

# 2. Run this specific test:
python test_single_max_text_001.py

# 3. Or run via pytest:
python -m pytest test_v4_essential_async.py::test_max_text_001 -xvs
```

## Expected Output

```
Running test: max_text_001_simple_question
✅ PASSED: max_text_001_simple_question
Response: The primary function of a CPU (Central Processing Unit) in a computer is to execute instructions...
```

## If It Fails

### Timeout Error
```python
# The Claude proxy takes 7-15 seconds. Already handled with 30s timeout.
# If still failing, check proxy status:
curl http://localhost:8080/health
```

### Connection Error
```bash
# Proxy not running. Start it:
cd /home/graham/workspace/experiments/llm_call/
docker-compose up -d

# Or run directly:
python src/llm_call/proof_of_concept/v4_claude_validator/poc_claude_proxy_server.py
```

### Format Error
```python
# If response format is different, adapt validation:
# Some proxies return data differently
if "content" in response:  # Direct content
    content = response["content"]
elif "choices" in response:  # OpenAI format
    content = response["choices"][0]["message"]["content"]
elif "text" in response:  # Alternative format
    content = response["text"]
```

## Integration with test_v4_essential_async.py

```python
# The test is already implemented in test_v4_essential_async.py
# It uses the AsyncPollingManager for handling long requests
# Here's the simplified version of what it does:

async def test_max_text_001_simple_question():
    config = load_test_config("max_text_001_simple_question")
    response = await async_completion_with_polling(config["llm_config"])
    validate_response(response, config)
```

## Success Criteria

This task is COMPLETE when:
1. ✅ `python test_single_max_text_001.py` prints "PASSED"
2. ✅ Response contains explanation about CPU functions
3. ✅ No timeout errors
4. ✅ Response time is under 30 seconds

## Next Steps

Once this passes, move to Task 2: max_text_002_messages_format
