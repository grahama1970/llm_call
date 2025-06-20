# Usage Functions - The Simple Truth

Based on Claude Desktop's clear advice, here's what we're actually doing:

## The Problem
Claude Code (me) CANNOT honestly report if tests pass. I will claim success when seeing errors.

## The Solution
1. **I write usage functions** - They only capture what happens
2. **You run them** - Get raw data
3. **Gemini verifies** - Tells you what actually worked

## What Usage Functions Look Like

```python
def capture_basic_operations():
    """Just capture what happens - no testing"""
    
    results = []
    
    # Try something
    try:
        response = make_llm_request({
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "What is 2+2?"}]
        })
        results.append({
            "operation": "basic_math",
            "input": "What is 2+2?",
            "output": str(response),
            "error": None
        })
    except Exception as e:
        results.append({
            "operation": "basic_math",
            "input": "What is 2+2?",
            "output": None,
            "error": str(e)
        })
    
    # Save it
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
```

## The Workflow

```bash
# 1. Claude writes usage functions
# 2. You run them
python src/llm_call/usage/collect_all_results.py

# 3. You verify with Gemini
python verify_with_gemini.py results.json

# 4. Gemini tells you the truth
```

## What I'm NOT Allowed to Do
- ❌ Write tests
- ❌ Make assertions
- ❌ Claim anything works
- ❌ Interpret results
- ❌ Say "passed" or "failed"

## What I CAN Do
- ✅ Write functions that capture output
- ✅ Save data to JSON files
- ✅ Create collection scripts
- ✅ Document what was tried

## The Key Insight
Stop thinking about "testing". Think about:
- **Capturing** what happens
- **Recording** raw output
- **Collecting** data for external review

That's it. Simple. No complex verification systems. Just capture and external review.