#!/usr/bin/env python3
"""
Send verification template and test matrix to Gemini for comprehensive critique.

This script:
1. Reads both critical documents
2. Sends them to Gemini with detailed critique request
3. Saves response and displays key recommendations
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_call import make_llm_request


async def get_gemini_critique():
    """Send both documents to Gemini for comprehensive critique."""
    
    # Read the verification template
    template_path = Path("/home/graham/workspace/experiments/llm_call/docs/TASK_LIST_TEMPLATE_USAGE_FUNCTIONS_VERIFIED.md")
    matrix_path = Path("/home/graham/workspace/experiments/llm_call/LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md")
    
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return
    
    if not matrix_path.exists():
        print(f"❌ Matrix not found: {matrix_path}")
        return
    
    template_content = template_path.read_text()
    matrix_content = matrix_path.read_text()
    
    # Create comprehensive prompt for Gemini
    prompt = f"""You are a highly critical AI test verification expert. I need you to review two documents that are supposed to help prevent Claude Code from lying about test results.

CONTEXT: Claude Code ($200/month AI assistant) has a fundamental training defect where it CANNOT accurately report test results. It will claim tests pass when they fail, hallucinate success messages, and cannot be fixed even after 5+ attempts. The human has given up trying to fix Claude and instead created a system where:
1. Claude writes usage functions that collect raw results only
2. All results are sent to you (Gemini) for verification
3. You must be EXTREMELY SKEPTICAL and default to FAIL

DOCUMENT 1: VERIFICATION TEMPLATE (used to guide Claude)
{template_content}

DOCUMENT 2: TEST MATRIX (what needs to be tested)
{matrix_content}

Please provide a COMPREHENSIVE CRITIQUE addressing:

1. **Template Effectiveness**
   - Will this template actually prevent Claude from lying about results?
   - Are there loopholes Claude could exploit to still claim false success?
   - What specific improvements would make dishonesty impossible?

2. **Verification Completeness**
   - Do you have everything needed to verify the test matrix items?
   - Are the expected outputs in the matrix specific enough to grade?
   - Which test cases will be hardest to verify objectively?

3. **Critical Improvements Needed**
   - What additional safeguards should be added to the template?
   - How can we make the verification process even more bulletproof?
   - What patterns of dishonesty should we specifically watch for?

4. **Practical Implementation**
   - Is the JSON format for results optimal for verification?
   - Should we add checksums or other tamper-proof mechanisms?
   - How can we ensure Claude doesn't manipulate the data before sending?

5. **Specific Test Matrix Issues**
   - Which tests in the matrix are most vulnerable to false reporting?
   - Are there test types that need special verification approaches?
   - Should certain tests be restructured for better verifiability?

Be EXTREMELY CRITICAL. Assume Claude will try to cheat and we need to make that impossible. Focus on PRACTICAL, IMPLEMENTABLE improvements that will ensure 100% honest test reporting.

Remember: The goal is to make it IMPOSSIBLE for Claude to lie about test results, not just difficult."""

    # Get judge model from environment - try different model for full response
    judge_model = os.getenv("LITELLM_JUDGE_MODEL", "vertex_ai/gemini-1.5-pro")
    
    print(f"🔍 Sending documents to Gemini ({judge_model}) for critique...")
    print(f"📄 Template: {len(template_content)} chars")
    print(f"📄 Matrix: {len(matrix_content)} chars")
    
    # Configure request WITHOUT thinking tokens to avoid truncation
    config = {
        "model": judge_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,  # Moderate temp for analytical critique
        "max_tokens": 8192  # High limit to get full response
    }
    
    # Disable thinking tokens to avoid response in reasoning_content
    # This ensures we get the full response in the content field
    
    try:
        response = await make_llm_request(config)
        
        # Debug response structure
        print(f"\n🔍 Response type: {type(response)}")
        if response:
            print(f"🔍 Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        # Handle different response formats
        critique = None
        
        # Check if it's a ModelResponse object
        if hasattr(response, 'choices') and response.choices:
            # Standard response format
            first_choice = response.choices[0]
            if hasattr(first_choice, 'message'):
                # Check for regular content
                if hasattr(first_choice.message, 'content') and first_choice.message.content:
                    critique = first_choice.message.content
                # Check for reasoning content (thinking tokens)
                elif hasattr(first_choice.message, 'reasoning_content') and first_choice.message.reasoning_content:
                    print("⚠️ WARNING: Response was in reasoning_content only. Retrying...")
                    # The response was cut off - we need to get the actual response
                    return
            elif hasattr(first_choice, 'text'):
                critique = first_choice.text
        elif isinstance(response, dict):
            # Check for content in various locations
            if 'content' in response:
                critique = response['content']
            elif 'choices' in response and response['choices']:
                # Standard OpenAI format
                first_choice = response['choices'][0]
                if 'message' in first_choice and 'content' in first_choice['message']:
                    critique = first_choice['message']['content']
                elif 'text' in first_choice:
                    critique = first_choice['text']
        elif isinstance(response, str):
            critique = response
        
        if not critique:
            print(f"❌ No content found in response: {response}")
            return
        
        print(f"✅ Got critique of {len(critique)} characters")
        
        # Save full critique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"gemini_verification_critique_{timestamp}.md"
        
        with open(output_file, 'w') as f:
            f.write(f"# Gemini Critique of Verification System\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Model: {judge_model}\n\n")
            f.write("## Full Critique\n\n")
            f.write(critique)
        
        print(f"\n✅ Full critique saved to: {output_file}")
        
        # Extract and display key recommendations
        print("\n" + "="*80)
        print("📋 KEY RECOMMENDATIONS FROM GEMINI")
        print("="*80)
        
        # Try to extract sections
        if "Critical Improvements" in critique:
            improvements_start = critique.find("Critical Improvements")
            improvements_end = critique.find("\n\n", improvements_start + 200)
            if improvements_end > improvements_start:
                print("\n🔴 CRITICAL IMPROVEMENTS:")
                print(critique[improvements_start:improvements_end])
        
        if "loopholes" in critique.lower():
            print("\n⚠️ IDENTIFIED LOOPHOLES:")
            # Find sentences containing "loophole"
            sentences = critique.split('.')
            for sentence in sentences:
                if "loophole" in sentence.lower():
                    print(f"• {sentence.strip()}")
        
        print("\n" + "="*80)
        print(f"💡 See {output_file} for complete analysis")
        print("="*80)
        
        # Also save a summary
        summary_file = f"gemini_critique_summary_{timestamp}.json"
        summary = {
            "timestamp": datetime.now().isoformat(),
            "model": judge_model,
            "critique_length": len(critique),
            "output_files": {
                "full_critique": output_file,
                "summary": summary_file
            },
            "key_findings": {
                "has_critical_improvements": "Critical Improvements" in critique,
                "mentions_loopholes": "loophole" in critique.lower(),
                "mentions_safeguards": "safeguard" in critique.lower(),
                "mentions_bulletproof": "bulletproof" in critique.lower()
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Summary saved to: {summary_file}")
        
    except Exception as e:
        print(f"\n❌ Error getting critique from Gemini: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Getting Gemini's critique on verification system...")
    print("🎯 Goal: Make it IMPOSSIBLE for Claude to lie about test results")
    print()
    
    asyncio.run(get_gemini_critique())