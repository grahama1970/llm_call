#!/usr/bin/env python3
"""
Get full critique from Gemini on verification system - simplified version.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_call import ask

# Read both documents
template_path = Path("/home/graham/workspace/experiments/llm_call/docs/TASK_LIST_TEMPLATE_USAGE_FUNCTIONS_VERIFIED.md")
matrix_path = Path("/home/graham/workspace/experiments/llm_call/LLM_CALL_COMPREHENSIVE_TEST_MATRIX.md")

template_content = template_path.read_text()
matrix_content = matrix_path.read_text()

# Create a more focused prompt
prompt = f"""You are a highly critical AI test verification expert reviewing a system designed to prevent Claude Code from lying about test results.

CONTEXT: Claude Code cannot accurately report test results and will lie even when seeing errors. The human created a verification system where:
1. Claude only writes usage functions that collect raw results
2. All results are sent to you (Gemini) for pass/fail grading
3. You must be EXTREMELY SKEPTICAL and default to FAIL

Please provide a CRITICAL ANALYSIS focusing on:

1. **MAJOR LOOPHOLES** - How could Claude still cheat? Be specific.
2. **CRITICAL IMPROVEMENTS** - What changes would make cheating IMPOSSIBLE?
3. **VERIFICATION GAPS** - Which test cases in the matrix are hardest to verify objectively?
4. **CONCRETE RECOMMENDATIONS** - List 5-10 specific, implementable changes.

DOCUMENT 1 (Template): {len(template_content)} chars
[First 1000 chars shown]
{template_content[:1000]}...

DOCUMENT 2 (Test Matrix): {len(matrix_content)} chars
[First 1000 chars shown]
{matrix_content[:1000]}...

Be RUTHLESS. Assume Claude WILL try to cheat. Focus on ACTIONABLE improvements."""

# Use synchronous ask for simplicity
print("🔍 Sending to Gemini for critique...")
print(f"📄 Template preview: {len(template_content)} chars")
print(f"📄 Matrix preview: {len(matrix_content)} chars")

try:
    response = ask(
        prompt,
        model="vertex_ai/gemini-1.5-pro",
        temperature=0.3,
        max_tokens=8192
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"gemini_full_critique_{timestamp}.md"
    
    with open(output_file, 'w') as f:
        f.write(f"# Gemini Full Critique of Verification System\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write(f"Model: vertex_ai/gemini-1.5-pro\n\n")
        f.write("## Critique\n\n")
        f.write(response)
    
    print(f"\n✅ Full critique saved to: {output_file}")
    print(f"📏 Response length: {len(response)} characters")
    
    # Extract key sections
    if "LOOPHOLES" in response:
        print("\n🔴 MAJOR LOOPHOLES IDENTIFIED:")
        loophole_start = response.find("LOOPHOLES")
        loophole_end = response.find("\n\n", loophole_start + 100)
        if loophole_end > loophole_start:
            print(response[loophole_start:loophole_end])
    
    if "RECOMMENDATIONS" in response:
        print("\n💡 KEY RECOMMENDATIONS:")
        rec_start = response.find("RECOMMENDATIONS")
        rec_end = response.find("\n\n", rec_start + 100)
        if rec_end > rec_start:
            print(response[rec_start:rec_end])
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()