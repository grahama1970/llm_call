# Task 1 Revised: Make test max_text_001_simple_question pass

**Test ID**: max_text_001_simple_question  
**Model**: max/text-general  
**Priority**: Start here - simplest test

## Copy This Working Code

```python
#!/usr/bin/env python3
# Save as: test_max_text_001.py

import asyncio
import sys
from litellm import acompletion

async def test_max_text_001():
    """Test the simplest Claude proxy call."""
    
    # The EXACT test case:
    test_config = {
        "model": "max/text-general",
        "question": "What is the primary function of a CPU in a computer?"
    }
    
    # Convert to messages format (Claude proxy expects this)
    messages = [{"role": "user", "content": test_config["question"]}]
    
    try:
        # Make the call with 30s timeout (Claude takes 7-15s)
        response = await acompletion(
            model=test_config["model"],
            messages=messages,
            api_base="http://localhost:8080",
            timeout=30
        )
        
        # Validate response
        content = response.choices[0].message.content
        assert content, "Empty response"
        assert len(content) > 20, "Response too short"
        assert any(word in content.lower() for word in ["cpu", "processor", "central"]), \
            "Response doesn't mention CPU"
        
        print("✅ PASSED: max_text_001_simple_question")
        print(f"Response preview: {content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        
        # Common fixes:
        if "Connection" in str(e):
            print("\nFIX: Start Claude proxy:")
            print("  cd /home/graham/workspace/experiments/llm_call/")
            print("  docker-compose up -d")
        elif "Timeout" in str(e):
            print("\nFIX: Increase timeout or check proxy logs:")
            print("  docker-compose logs claude-proxy")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(test_max_text_001())
    sys.exit(0 if success else 1)
```

## Run It Now

```bash
# Save the code above, then:
python test_max_text_001.py
```

## Expected Success Output

```
✅ PASSED: max_text_001_simple_question
Response preview: The primary function of a CPU (Central Processing Unit) is to execute instructions and perform...
```

## If It Fails - Quick Fixes

### ConnectionError
```bash
# Proxy not running. Start it:
docker-compose up -d
# Wait 10 seconds for startup
sleep 10
# Try again
python test_max_text_001.py
```

### TimeoutError  
```python
# Already set to 30s. If still failing, check proxy:
curl http://localhost:8080/health
# Should return {"status": "ok"}
```

### KeyError on content
```python
# Response format might be different. Debug:
print(json.dumps(response, indent=2))
# Adjust extraction based on actual structure
```

## Done When

✅ Script prints "PASSED"  
✅ No errors  
✅ Takes < 30 seconds

**Next**: Task 2 - max_text_002_messages_format
