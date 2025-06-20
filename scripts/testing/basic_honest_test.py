#!/usr/bin/env python3
"""
Basic honest testing - what a week-1 student would write.
"""
import httpx

print("Testing each provider:\n")

providers = [
    "gpt-3.5-turbo",
    "claude-3-haiku-20240307", 
    "vertex_ai/gemini-2.5-flash-preview-05-20"
]

for model in providers:
    print(f"Testing {model}:")
    
    response = httpx.post(
        "http://localhost:8001/v1/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 50
        }
    )
    
    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content")
    
    # Week 1 student logic:
    if content is None:
        print(f"  Result: FAILED - Got None\n")
    elif content == "None":
        print(f"  Result: FAILED - Got string 'None'\n")
    elif len(str(content).strip()) == 0:
        print(f"  Result: FAILED - Empty response\n")
    else:
        print(f"  Result: SUCCESS - Got: {content}\n")