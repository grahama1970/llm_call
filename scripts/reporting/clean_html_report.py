#!/usr/bin/env python3
"""Clean ANSI codes from HTML report."""

import re
from pathlib import Path

def remove_ansi_codes(text):
    """Remove ANSI escape sequences from text."""
    # Pattern to match ANSI escape codes
    ansi_escape = re.compile(r'''
        \x1B  # ESC
        (?:   # 7-bit C1 Fe (except CSI)
            [@-Z\\-_]
        |     # or [ for CSI, followed by parameter bytes
            \[
            [0-?]*  # Parameter bytes
            [ -/]*  # Intermediate bytes
            [@-~]   # Final byte
        )
    ''', re.VERBOSE)
    return ansi_escape.sub('', text)

# Read the HTML file
html_path = Path("/home/graham/workspace/experiments/llm_call/verification_report.html")
content = html_path.read_text()

# Clean ANSI codes
cleaned_content = remove_ansi_codes(content)

# Also clean up some specific patterns
cleaned_content = cleaned_content.replace('[1;31m', '')
cleaned_content = cleaned_content.replace('[0m', '')
cleaned_content = cleaned_content.replace('[32m', '')
cleaned_content = cleaned_content.replace('[1m', '')
cleaned_content = cleaned_content.replace('[36m', '')
cleaned_content = cleaned_content.replace('[33m', '')
cleaned_content = cleaned_content.replace('[92m', '')

# Save cleaned version
cleaned_path = Path("/home/graham/workspace/experiments/llm_call/verification_report_clean.html")
cleaned_path.write_text(cleaned_content)

print(f"✅ Cleaned HTML report saved to: {cleaned_path}")
print("View at: http://localhost:8891/verification_report_clean.html")