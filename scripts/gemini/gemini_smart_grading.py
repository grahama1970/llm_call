#!/usr/bin/env python3
"""
Smart test grading with max/opus summarized context.
"""
import json
import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_call import make_llm_request
import litellm
from litellm import completion
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"

async def get_context_summary():
    """Use max/opus to create smart context summary."""
    
    # Load key files
    readme = Path("/home/graham/workspace/experiments/llm_call/README.md").read_text()
    matrix = Path("/home/graham/workspace/experiments/llm_call/LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md").read_text()
    
    summary_prompt = f"""Summarize the key information needed for grading LLM tests:

README (first 2000 chars):
{readme[:2000]}

TEST MATRIX (first 2000 chars):
{matrix[:2000]}

Create a concise summary (max 500 words) covering:
1. What llm_call is and how it uses LiteLLM
2. Key test expectations and grading criteria
3. How different models might format responses
4. What strict vs lenient grading means for this project"""
    
    # Get summary from max/opus
    response = await make_llm_request({
        "model": "max",
        "messages": [{"role": "user", "content": summary_prompt}],
        "temperature": 0.3
    })
    
    if response and hasattr(response, 'choices'):
        return response.choices[0].message.content
    else:
        return "Failed to get context summary"

async def main():
    # Load test results
    with open("complete_test_results.json") as f:
        test_results = json.load(f)
    
    print("Getting smart context summary from max/opus...")
    context_summary = await get_context_summary()
    print(f"Got summary: {len(context_summary)} chars")
    
    # Create grading prompt with smart context
    prompt = f"""You are grading test results for llm_call.

PROJECT CONTEXT (summarized by Claude):
{context_summary}

TEST RESULTS TO GRADE:
"""
    
    for test in test_results:
        prompt += f"""
Test {test['test_id']}:
- Command: {test['command']}
- Model: {test['model']}
- Expected: {test['expected']}
- Actual Response: {test['actual_response']}
---
"""
    
    prompt += """

Grade each test strictly based on whether the actual response meets the expected criteria.

| Test ID | Grade | Critique |
|---------|-------|----------|

Return ONLY the table. Grade = PASS/FAIL. Critique = specific issue (max 15 words)."""
    
    print("\nSending to Gemini with smart context...")
    
    # Send to Gemini
    response = completion(
        model="vertex_ai/gemini-2.5-flash-preview-05-20",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        thinking={
            "medium": True,
            "budget_tokens": 2048
        }
    )
    
    content = response.choices[0].message.content
    
    if content:
        print("\nGEMINI GRADING WITH SMART CONTEXT:")
        print("="*80)
        print(content)
        
        with open("gemini_smart_grading.md", "w") as f:
            f.write("# Gemini Smart Test Grading\n\n")
            f.write("Context summarized by max/opus\n\n")
            f.write(content)
    else:
        print("ERROR: Null content")

if __name__ == "__main__":
    asyncio.run(main())