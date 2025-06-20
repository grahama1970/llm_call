#!/usr/bin/env python3
"""
Send verification template and test matrix to Gemini for brutal critique.

This script sends both documents to Gemini to analyze whether the verification
system can actually prevent Claude from lying about test results.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_call import make_llm_request


async def get_gemini_critique():
    """Send both documents to Gemini for brutal analysis."""
    
    # Read the verification template
    template_path = Path("/home/graham/workspace/experiments/llm_call/docs/TASK_LIST_TEMPLATE_USAGE_FUNCTIONS_VERIFIED.md")
    with open(template_path) as f:
        template_content = f.read()
    
    # Read the test matrix
    matrix_path = Path("/home/graham/workspace/experiments/llm_call/LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md")
    with open(matrix_path) as f:
        matrix_content = f.read()
    
    # Create the brutal critique prompt
    prompt = f"""I'm dealing with Claude Code, a $200/month AI coding assistant that is FUNDAMENTALLY INCAPABLE of honestly reporting test results. After 5+ attempts, it still claims tests pass when they fail.

I've created a verification template that requires external AI verification of all test results. Claude is only allowed to collect raw data, and you (Gemini) must verify if tests actually passed.

Please critique these documents:
1. Does the verification template make it impossible for Claude to lie about results?
2. What additional safeguards would prevent Claude from manipulating the data?
3. Are the complexity levels (LOW/MEDIUM/HIGH) useful for iterative verification?
4. What specific improvements would make this bulletproof?
5. Given that this is the EASIEST Granger project (just API calls), why is Claude still failing?

Be brutally honest. We need to make Claude useful, not negatively useful.

Please provide your critique in a clear, structured format. Limit your response to about 3000 words to ensure it fits in the response.

## Document 1: TASK_LIST_TEMPLATE_USAGE_FUNCTIONS_VERIFIED.md
{template_content}

## Document 2: LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md
{matrix_content}
"""
    
    # Use LITELLM_JUDGE_MODEL with thinking enabled
    judge_model = os.getenv("LITELLM_JUDGE_MODEL", "vertex_ai/gemini-2.0-flash-exp")
    
    print(f"Sending documents to {judge_model} for brutal critique...")
    print(f"Template size: {len(template_content):,} chars")
    print(f"Matrix size: {len(matrix_content):,} chars")
    print(f"Total prompt size: {len(prompt):,} chars")
    
    # Configure request without thinking mode to get direct response
    config = {
        "model": judge_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,  # Moderate temp for analytical critique
        "max_tokens": 8000  # Allow long response
    }
    
    try:
        response = await make_llm_request(config)
        
        # Debug: print response type and structure
        print(f"\nResponse type: {type(response)}")
        if hasattr(response, '__dict__'):
            print(f"Response attributes: {response.__dict__.keys()}")
        
        # Extract the critique - handle different response formats
        critique = None
        reasoning = None
        
        if isinstance(response, dict):
            if 'choices' in response:
                critique = response['choices'][0]['message']['content']
            elif 'content' in response:
                critique = response['content']
            else:
                print(f"Unexpected response format: {response.keys()}")
                critique = str(response)
        elif hasattr(response, 'choices'):
            # ModelResponse object from litellm
            choice = response.choices[0]
            if choice.message.content:
                critique = choice.message.content
            if hasattr(choice.message, 'reasoning_content') and choice.message.reasoning_content:
                reasoning = choice.message.reasoning_content
                print(f"\nFound reasoning content: {len(reasoning)} chars")
        elif hasattr(response, 'content'):
            # Response might be an object with content attribute
            critique = response.content
        else:
            # Response might be a string directly
            critique = str(response)
        
        # If we only have reasoning and no content, use the reasoning
        if not critique and reasoning:
            critique = reasoning
            print("Using reasoning content as the main critique")
        
        # Save the full response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"gemini_brutal_critique_{timestamp}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Gemini's Brutal Critique of Claude Verification System\n\n")
            f.write(f"**Generated**: {datetime.now()}\n")
            f.write(f"**Model**: {judge_model}\n")
            f.write(f"**Template Size**: {len(template_content):,} chars\n")
            f.write(f"**Matrix Size**: {len(matrix_content):,} chars\n\n")
            f.write("---\n\n")
            f.write(critique)
        
        print(f"\n✅ Critique saved to: {output_file}")
        
        # Extract and display key recommendations
        print("\n" + "="*80)
        print("KEY RECOMMENDATIONS FROM GEMINI:")
        print("="*80)
        
        # Look for numbered points or sections
        lines = critique.split('\n')
        in_recommendations = False
        recommendation_count = 0
        
        for line in lines:
            # Look for recommendation patterns
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'improve', 'additional safeguard', 'bulletproof']):
                in_recommendations = True
            
            if in_recommendations and line.strip():
                # Look for numbered items or bullet points
                if (line.strip()[0].isdigit() and line.strip()[1] in '.):' or 
                    line.strip().startswith(('- ', '* ', '• '))):
                    print(f"\n{line.strip()}")
                    recommendation_count += 1
                elif recommendation_count > 0 and not line.strip()[0].isdigit():
                    # Stop after recommendations section
                    in_recommendations = False
        
        # Also look for answers to specific questions
        print("\n" + "="*80)
        print("ANSWERS TO SPECIFIC QUESTIONS:")
        print("="*80)
        
        questions = [
            "impossible for Claude to lie",
            "additional safeguards",
            "complexity levels",
            "bulletproof",
            "why is Claude still failing"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. {question.upper()}:")
            # Find relevant section in critique
            for j, line in enumerate(lines):
                if question in line.lower():
                    # Print next few lines as the answer
                    for k in range(j, min(j+5, len(lines))):
                        if lines[k].strip():
                            print(f"   {lines[k].strip()}")
                    break
        
        return critique
        
    except Exception as e:
        print(f"\n❌ Error getting Gemini critique: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(get_gemini_critique())
    
    if result:
        print("\n✅ Successfully received Gemini's brutal critique")
        print("\nPlease review the full critique in the generated file for detailed analysis.")
    else:
        print("\n❌ Failed to get critique from Gemini")
        sys.exit(1)