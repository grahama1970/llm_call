#!/usr/bin/env python3
"""
Fix the Gemini critique with PROPER token allocation.

When asking Gemini to critique thousands of lines of code, we need:
- At least 2000-4000 tokens for a proper analysis
- Not the ridiculous 100 tokens we were giving it
"""

import httpx
import asyncio
from datetime import datetime

async def get_proper_gemini_critique():
    """Get a REAL critique with adequate tokens."""
    
    # Read the test file we want critiqued
    with open("tests/local/critical/test_final_working.py") as f:
        test_code = f.read()
    
    prompt = f"""Review this test code and provide detailed critique:

{test_code}

Please analyze:
1. Test coverage and edge cases
2. Code quality and structure
3. Error handling
4. Performance considerations
5. Suggestions for improvement

Provide a thorough analysis with specific examples."""
    
    print(f"Requesting Gemini critique at {datetime.now()}")
    print(f"Prompt length: {len(prompt)} chars")
    print("Max tokens: 4000 (enough for detailed analysis)")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/v1/chat/completions",
            json={
                "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 4000  # PROPER amount for analysis!
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            if content:
                print("\nGEMINI CRITIQUE:")
                print("="*60)
                print(content)
                print("="*60)
                
                # Save to file
                with open("gemini_proper_critique.txt", "w") as f:
                    f.write(content)
                print("\nSaved to gemini_proper_critique.txt")
                
                # Show token usage
                if "usage" in data:
                    usage = data["usage"]
                    print(f"\nToken usage:")
                    print(f"  Prompt: {usage['prompt_tokens']}")
                    print(f"  Completion: {usage['completion_tokens']}")
                    print(f"  Total: {usage['total_tokens']}")
            else:
                print("ERROR: Still got null content even with 4000 tokens!")
                print(f"Full response: {data}")
        else:
            print(f"ERROR {response.status_code}: {response.text}")

if __name__ == "__main__":
    asyncio.run(get_proper_gemini_critique())