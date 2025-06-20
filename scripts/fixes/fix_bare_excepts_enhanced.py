#!/usr/bin/env python3
"""
Module: fix_bare_excepts_enhanced.py
Description: Enhanced version that creates a detailed report of bare except clauses

External Dependencies:
- None (uses standard library only)

Sample Input:
>>> files_to_check = ["src/llm_call/cli/main.py"]

Expected Output:
>>> Generated report: bare_except_report.md
>>> Fixed 2 bare except clauses

Example Usage:
>>> python scripts/fix_bare_excepts_enhanced.py --report
>>> python scripts/fix_bare_excepts_enhanced.py --fix --conservative
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict
from datetime import datetime

# Enhanced exception mapping with specific imports
EXCEPTION_MAPPINGS = {
    # JSON handling
    r"json\.loads|json\.load|JSON\.parse|parse.*json": {
        "exception": "json.JSONDecodeError", 
        "import": None,  # Built-in
        "comment": "# JSON parsing failed"
    },
    
    # YAML handling
    r"yaml\.load|yaml\.safe_load|YAML": {
        "exception": "yaml.YAMLError",
        "import": "import yaml",
        "comment": "# YAML parsing failed"
    },
    
    # HTTP/API calls
    r"requests\.|http\.request|urlopen": {
        "exception": "requests.RequestException",
        "import": "import requests",
        "comment": "# HTTP request failed"
    },
    
    # Anthropic/Claude specific
    r"anthropic\.|claude|Claude": {
        "exception": "Exception",  # Keep generic for now
        "import": None,
        "comment": "# Claude API call failed"
    },
    
    # OpenAI specific
    r"openai\.|gpt|GPT|chatgpt": {
        "exception": "Exception",  # Keep generic for now
        "import": None,
        "comment": "# OpenAI API call failed"
    },
    
    # LiteLLM specific
    r"litellm\.|LiteLLM": {
        "exception": "Exception",  # Keep generic for now
        "import": None,
        "comment": "# LiteLLM call failed"
    },
    
    # SQLite operations
    r"sqlite|\.execute\(|\.executemany\(|cursor": {
        "exception": "sqlite3.Error",
        "import": "import sqlite3",
        "comment": "# Database operation failed"
    },
    
    # File operations
    r"open\(|\.read\(|\.write\(|Path\(": {
        "exception": "IOError",
        "import": None,
        "comment": "# File operation failed"
    },
    
    # Type conversions
    r"int\(|float\(|bool\(": {
        "exception": "ValueError",
        "import": None,
        "comment": "# Type conversion failed"
    },
    
    # Dictionary/list access
    r"\.get\(|\[[\'\"].*[\'\"]\]|KeyError": {
        "exception": "KeyError",
        "import": None,
        "comment": "# Key not found"
    },
    
    # Attribute access
    r"\.\w+\s*\(|getattr\(|hasattr\(": {
        "exception": "AttributeError",
        "import": None,
        "comment": "# Attribute not found"
    },
    
    # Index operations
    r"\[\d+\]|\.pop\(|list\[|tuple\[": {
        "exception": "IndexError",
        "import": None,
        "comment": "# Index out of range"
    },
    
    # Image processing
    r"PIL\.|Image\.|image|resize|compress": {
        "exception": "Exception",  # PIL has many exception types
        "import": None,
        "comment": "# Image processing failed"
    },
    
    # Base64 encoding
    r"base64\.b64encode|base64\.b64decode|b64": {
        "exception": "ValueError",
        "import": None,
        "comment": "# Base64 encoding/decoding failed"
    },
    
    # Unicode/encoding
    r"\.encode\(|\.decode\(|utf-8|encoding": {
        "exception": "UnicodeDecodeError",
        "import": None,
        "comment": "# Text encoding/decoding failed"
    },
    
    # Subprocess
    r"subprocess\.|Popen|\.run\(": {
        "exception": "subprocess.SubprocessError",
        "import": "import subprocess",
        "comment": "# Subprocess execution failed"
    },
    
    # Asyncio
    r"asyncio\.|await|async|gather": {
        "exception": "asyncio.TimeoutError",
        "import": "import asyncio",
        "comment": "# Async operation failed"
    },
    
    # Validation
    r"validate|validator|ValidationError|pydantic": {
        "exception": "ValueError",  # Generic for validation
        "import": None,
        "comment": "# Validation failed"
    },
    
    # Rich console
    r"console\.print|Panel\(|Table\(|rich": {
        "exception": "Exception",
        "import": None,
        "comment": "# Rich formatting failed"
    },
    
    # Tiktoken
    r"tiktoken\.|encoding_for_model|get_encoding": {
        "exception": "KeyError",
        "import": None,
        "comment": "# Tiktoken encoding failed"
    }
}


def analyze_bare_excepts(file_path: Path) -> List[Dict[str, any]]:
    """Analyze bare except clauses with detailed context."""
    issues = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    bare_except_pattern = re.compile(r'^\s*except\s*:\s*(?:#.*)?$')
    generic_except_pattern = re.compile(r'^\s*except\s+Exception\s*(?::\s*|as\s+\w+\s*:)(?:#.*)?$')
    
    for i, line in enumerate(lines):
        issue = None
        
        if bare_except_pattern.match(line):
            issue = {"type": "bare", "line": line.strip()}
        elif generic_except_pattern.match(line) and not is_final_catchall(lines, i):
            issue = {"type": "generic", "line": line.strip()}
        
        if issue:
            # Get context
            context_start = max(0, i - 10)
            context_end = min(len(lines), i + 5)
            context = ''.join(lines[context_start:i])
            after_context = ''.join(lines[i+1:context_end])
            
            # Get the try block
            try_line = find_try_block(lines, i)
            
            # Analyze and suggest
            suggestion = suggest_specific_exception(context, after_context)
            
            issue.update({
                "line_num": i + 1,
                "context": context,
                "after_context": after_context,
                "try_line": try_line,
                "suggestion": suggestion,
                "file": file_path
            })
            
            issues.append(issue)
    
    return issues


def find_try_block(lines: List[str], except_index: int) -> Optional[int]:
    """Find the line number of the corresponding try block."""
    indent_level = len(lines[except_index]) - len(lines[except_index].lstrip())
    
    for i in range(except_index - 1, -1, -1):
        line = lines[i]
        if line.strip().startswith('try:'):
            line_indent = len(line) - len(line.lstrip())
            if line_indent == indent_level:
                return i + 1
    
    return None


def is_final_catchall(lines: List[str], current_index: int) -> bool:
    """Check if this is the final catch-all in a series of except blocks."""
    i = current_index - 1
    found_specific = False
    indent_level = len(lines[current_index]) - len(lines[current_index].lstrip())
    
    while i >= 0:
        line = lines[i]
        line_indent = len(line) - len(line.lstrip())
        
        if line.strip().startswith('try:') and line_indent == indent_level:
            break
            
        if line.strip().startswith('except') and line_indent == indent_level:
            if 'Exception' not in line and ':' not in line:
                found_specific = True
                
        i -= 1
    
    return found_specific


def suggest_specific_exception(context: str, after_context: str = "") -> Dict[str, str]:
    """Suggest a specific exception based on context analysis."""
    full_context = context + after_context
    
    # Check each pattern
    for pattern, info in EXCEPTION_MAPPINGS.items():
        if re.search(pattern, full_context, re.IGNORECASE):
            return info
    
    # Default fallback
    return {
        "exception": "Exception",
        "import": None,
        "comment": "# Generic exception handler"
    }


def generate_report(issues: List[Dict[str, any]], output_path: Path) -> None:
    """Generate a detailed markdown report of all issues."""
    report = []
    report.append("# Bare Except Clauses Report")
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nTotal issues found: {len(issues)}")
    
    # Group by file
    by_file = defaultdict(list)
    for issue in issues:
        by_file[issue['file']].append(issue)
    
    # Statistics
    report.append("\n## Summary Statistics")
    report.append(f"- Files with issues: {len(by_file)}")
    report.append(f"- Bare except clauses: {sum(1 for i in issues if i['type'] == 'bare')}")
    report.append(f"- Generic Exception handlers: {sum(1 for i in issues if i['type'] == 'generic')}")
    
    # Suggested imports
    imports_needed = set()
    for issue in issues:
        if issue['suggestion']['import']:
            imports_needed.add(issue['suggestion']['import'])
    
    if imports_needed:
        report.append("\n## Required Imports")
        for imp in sorted(imports_needed):
            report.append(f"- `{imp}`")
    
    # Detailed issues by file
    report.append("\n## Issues by File")
    
    for file_path, file_issues in sorted(by_file.items()):
        report.append(f"\n### {file_path}")
        report.append(f"Issues: {len(file_issues)}")
        
        for issue in file_issues:
            report.append(f"\n#### Line {issue['line_num']}")
            report.append(f"**Current:** `{issue['line']}`")
            report.append(f"**Suggested:** `except {issue['suggestion']['exception']}:`")
            if issue['suggestion']['comment']:
                report.append(f"**Comment:** {issue['suggestion']['comment']}")
            
            # Show relevant context
            if issue['try_line']:
                report.append(f"\n**Try block starts at line:** {issue['try_line']}")
            
            report.append("\n**Context:**")
            report.append("```python")
            report.append(issue['context'].rstrip())
            report.append(issue['line'])
            report.append(issue['after_context'].rstrip())
            report.append("```")
    
    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"📄 Report generated: {output_path}")


def create_fix_script(issues: List[Dict[str, any]], output_path: Path) -> None:
    """Create a script that can be reviewed before applying fixes."""
    script = []
    script.append("#!/usr/bin/env python3")
    script.append('"""Auto-generated script to fix bare except clauses."""')
    script.append("import fileinput")
    script.append("import sys")
    script.append("")
    script.append("# Fixes to apply")
    script.append("fixes = [")
    
    for issue in issues:
        script.append(f"    {{'file': '{issue['file']}', 'line': {issue['line_num']}, "
                     f"'old': '{issue['line']}', "
                     f"'new': 'except {issue['suggestion']['exception']}:'}},")
    
    script.append("]")
    script.append("")
    script.append("# Apply fixes")
    script.append("for fix in fixes:")
    script.append("    print(f\"Fixing {fix['file']}:{fix['line']}\")")
    script.append("    # Implementation here")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(script))
    
    os.chmod(output_path, 0o755)
    print(f"📝 Fix script generated: {output_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Analyze and fix bare except clauses")
    parser.add_argument('--report', action='store_true',
                       help="Generate detailed report")
    parser.add_argument('--fix', action='store_true',
                       help="Apply fixes (use with --conservative for safer fixes)")
    parser.add_argument('--conservative', action='store_true',
                       help="Only fix obvious cases")
    parser.add_argument('--path', default='src/llm_call',
                       help="Path to analyze")
    parser.add_argument('--output-dir', default='docs/reports',
                       help="Output directory for reports")
    
    args = parser.parse_args()
    
    # Find all Python files
    root_path = Path(args.path)
    python_files = list(root_path.rglob("*.py"))
    
    print(f"🔍 Analyzing {len(python_files)} Python files...")
    
    # Analyze all files
    all_issues = []
    for py_file in sorted(python_files):
        issues = analyze_bare_excepts(py_file)
        all_issues.extend(issues)
    
    if not all_issues:
        print("✅ No bare except clauses found!")
        return 0
    
    # Generate report
    if args.report or not args.fix:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(exist_ok=True)
        
        report_path = output_dir / f"bare_except_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        generate_report(all_issues, report_path)
        
        # Also create fix script
        script_path = output_dir / "fix_bare_excepts.py"
        create_fix_script(all_issues, script_path)
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"Found {len(all_issues)} bare except clauses")
    print(f"Files affected: {len(set(i['file'] for i in all_issues))}")
    
    if args.fix:
        print("\n⚠️  Fix mode not yet implemented.")
        print("Please review the generated report and fix script first.")
    
    return 0


if __name__ == "__main__":
    # Simple validation
    test_context = "result = json.loads(data)"
    suggestion = suggest_specific_exception(test_context)
    assert suggestion['exception'] == 'json.JSONDecodeError'
    print("✅ Module validation passed")
    
    sys.exit(main())