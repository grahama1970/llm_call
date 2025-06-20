#!/usr/bin/env python3
"""Send results to Gemini for verification - Simple version based on Claude Desktop advice"""

import json
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm_call import make_llm_request

async def verify_results(results_file):
    """Send captured results to Gemini for verification"""
    
    with open(results_file) as f:
        data = json.load(f)
    
    prompt = f"""You are verifying outputs from Claude Code's llm_call library usage functions.

CRITICAL: Claude Code CANNOT accurately report test results. Look ONLY at the raw outputs.

For each operation below, determine if the llm_call library actually worked correctly:
- If there's an error, mark as FAIL
- If the output doesn't match what was requested, mark as FAIL
- Only mark PASS if the output clearly shows success

Results to verify:
{json.dumps(data, indent=2)}

Respond with a table:
| Operation | Expected | Actual | PASS/FAIL | Reason |

Be EXTREMELY skeptical. Default to FAIL."""

    response = await make_llm_request({
        "model": "vertex_ai/gemini-1.5-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    })
    
    print("GEMINI VERIFICATION RESULTS:")
    print("="*60)
    
    # Extract content based on response type
    if hasattr(response, 'choices'):
        content = response.choices[0].message.content
    elif isinstance(response, dict) and 'choices' in response:
        content = response['choices'][0]['message']['content']
    else:
        content = str(response)
    
    print(content)
    
    # Save verification
    output_file = f"verified_{Path(results_file).name}"
    with open(output_file, "w") as f:
        json.dump({
            "original_results": data,
            "verification": content,
            "verified_by": "gemini-1.5-flash"
        }, f, indent=2)
    
    print(f"\nVerification saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify_with_gemini_simple.py <results.json>")
        sys.exit(1)
    
    asyncio.run(verify_results(sys.argv[1]))