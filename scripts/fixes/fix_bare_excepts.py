#!/usr/bin/env python3
"""
Module: fix_bare_excepts.py
Description: Finds and fixes bare except clauses in the llm_call codebase

External Dependencies:
- None (uses standard library only)

Sample Input:
>>> files_to_check = ["src/llm_call/cli/main.py"]

Expected Output:
>>> Fixed 2 bare except clauses in src/llm_call/cli/main.py

Example Usage:
>>> python scripts/fix_bare_excepts.py --dry-run
>>> python scripts/fix_bare_excepts.py --fix
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

# Exception mapping based on common patterns
EXCEPTION_MAPPINGS = {
    # Import and module errors
    r"import|from\s+\w+\s+import|\bimport\s+": "ImportError",
    r"module|package": "ModuleNotFoundError",
    
    # Parsing errors
    r"json\.loads|json\.load|JSON|parse.*json": "json.JSONDecodeError",
    r"yaml\.load|yaml\.safe_load|YAML": "yaml.YAMLError",
    r"xml\.parse|ElementTree|XML": "xml.etree.ElementTree.ParseError",
    r"ast\.parse|compile\(": "SyntaxError",
    
    # Type and value errors
    r"int\(|float\(|bool\(|str\(": "ValueError",
    r"\.get\(|getattr\(|\[.*\]|dict|list|tuple": "KeyError",
    r"None\.|NoneType": "AttributeError",
    r"index|indices|\[\d+\]": "IndexError",
    
    # File operations
    r"open\(|read\(|write\(|Path\(.*\)\.": "IOError",
    r"os\.path|pathlib|file|directory": "FileNotFoundError",
    r"permission|access denied": "PermissionError",
    
    # Network and API errors
    r"requests\.|http|url|api|endpoint": "requests.RequestException",
    r"socket|connection|network": "ConnectionError",
    r"timeout": "TimeoutError",
    
    # Database errors
    r"sqlite|database|cursor|execute\(.*SELECT|INSERT|UPDATE|DELETE": "sqlite3.Error",
    r"redis|cache": "redis.RedisError",
    
    # LLM-specific errors
    r"anthropic|claude": "anthropic.APIError",
    r"openai|gpt": "openai.OpenAIError",
    r"litellm": "litellm.exceptions.APIError",
    r"google.*ai|gemini": "google.generativeai.types.GenerativeAIError",
    
    # Image processing
    r"PIL|Image|Pillow|image|resize|compress": "PIL.UnidentifiedImageError",
    r"base64\.b64encode|base64\.b64decode": "binascii.Error",
    
    # Encoding errors
    r"encode\(|decode\(|encoding|utf-8": "UnicodeDecodeError",
    r"tiktoken|encoding_for_model": "KeyError",
    
    # Process/subprocess errors
    r"subprocess|Popen|run\(": "subprocess.SubprocessError",
    r"asyncio|await|async": "asyncio.TimeoutError",
    
    # Validation specific
    r"validate|validation|schema": "ValidationError",
    r"pydantic|BaseModel": "pydantic.ValidationError",
}

# Common context-specific replacements
CONTEXT_SPECIFIC = {
    # tiktoken specific
    "tiktoken.encoding_for_model": ("KeyError", "# Model not found, fallback to default"),
    "tiktoken.get_encoding": ("Exception", "# Encoding initialization failed"),
    
    # Rich console specific
    "console.print(Panel": ("Exception", "# Rich formatting failed, fallback to simple print"),
    
    # JSON parsing with fallback
    "json.loads": ("json.JSONDecodeError", "# JSON parsing failed"),
    
    # General parsing
    "ValidationResult(**parsed)": ("(TypeError, ValueError)", "# Validation result parsing failed"),
}


def find_bare_excepts(file_path: Path) -> List[Tuple[int, str, str]]:
    """Find all bare except clauses in a file."""
    bare_excepts = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Patterns to match
    bare_except_pattern = re.compile(r'^\s*except\s*:\s*(?:#.*)?$')
    generic_except_pattern = re.compile(r'^\s*except\s+Exception\s*:\s*(?:#.*)?$')
    generic_except_as_pattern = re.compile(r'^\s*except\s+Exception\s+as\s+\w+\s*:\s*(?:#.*)?$')
    
    for i, line in enumerate(lines):
        if bare_except_pattern.match(line):
            # Get context (previous 5 lines)
            context_start = max(0, i - 5)
            context = ''.join(lines[context_start:i])
            bare_excepts.append((i + 1, line.strip(), context))
        elif generic_except_pattern.match(line) or generic_except_as_pattern.match(line):
            # Only report generic Exception if it's not already specific enough
            context_start = max(0, i - 5)
            context = ''.join(lines[context_start:i])
            # Check if this is a catch-all at the end of multiple except blocks
            if not is_final_catchall(lines, i):
                bare_excepts.append((i + 1, line.strip(), context))
    
    return bare_excepts


def is_final_catchall(lines: List[str], current_index: int) -> bool:
    """Check if this Exception handler is the final catch-all in a try block."""
    # Look backwards for other except clauses
    i = current_index - 1
    found_specific_except = False
    
    while i >= 0:
        line = lines[i].strip()
        if line.startswith('try:'):
            break
        if line.startswith('except') and not line.startswith('except Exception'):
            found_specific_except = True
        i -= 1
    
    return found_specific_except


def suggest_exception_type(context: str, line: str) -> str:
    """Suggest appropriate exception type based on context."""
    # Check for specific known patterns first
    for pattern, replacement in CONTEXT_SPECIFIC.items():
        if pattern in context:
            return replacement[0]
    
    # Check general patterns
    for pattern, exception_type in EXCEPTION_MAPPINGS.items():
        if re.search(pattern, context, re.IGNORECASE):
            return exception_type
    
    # Default based on the line content
    if "except:" in line:
        return "Exception"  # Generic but explicit
    
    return "Exception"  # Keep generic Exception as is


def fix_file(file_path: Path, dry_run: bool = True) -> int:
    """Fix bare except clauses in a file."""
    bare_excepts = find_bare_excepts(file_path)
    
    if not bare_excepts:
        return 0
    
    if dry_run:
        print(f"\n{file_path}:")
        for line_num, line, context in bare_excepts:
            suggested = suggest_exception_type(context, line)
            print(f"  Line {line_num}: {line}")
            print(f"    Suggested: except {suggested}:")
            if suggested in ["ValidationError", "pydantic.ValidationError"]:
                print(f"    Note: May need to import {suggested}")
        return len(bare_excepts)
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track what we need to import
    needed_imports = set()
    
    # Fix each bare except
    changes_made = 0
    for line_num, line_content, context in reversed(bare_excepts):  # Reverse to maintain line numbers
        idx = line_num - 1
        current_line = lines[idx]
        indent = len(current_line) - len(current_line.lstrip())
        
        suggested = suggest_exception_type(context, line_content)
        
        # Add to imports if needed
        if suggested in ["json.JSONDecodeError", "yaml.YAMLError", "pydantic.ValidationError"]:
            module = suggested.split('.')[0]
            needed_imports.add(module)
        
        # Replace the line
        if "except:" in line_content:
            new_line = ' ' * indent + f"except {suggested}:\n"
        elif "except Exception:" in line_content:
            new_line = ' ' * indent + f"except {suggested}:\n"
        elif "except Exception as" in line_content:
            var_name = re.search(r'as\s+(\w+)', line_content).group(1)
            new_line = ' ' * indent + f"except {suggested} as {var_name}:\n"
        else:
            continue
        
        lines[idx] = new_line
        changes_made += 1
    
    # Add imports if needed
    if needed_imports:
        import_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('#'):
                import_idx = i
                break
        
        for module in sorted(needed_imports):
            if module == 'json':
                # json is usually already imported
                continue
            import_line = f"import {module}\n"
            if import_line not in lines[:20]:  # Check first 20 lines
                lines.insert(import_idx, import_line)
                import_idx += 1
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fixed {changes_made} bare except clauses in {file_path}")
    return changes_made


def main():
    """Main function to fix bare except clauses."""
    parser = argparse.ArgumentParser(description="Fix bare except clauses in Python code")
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help="Show what would be changed without modifying files (default)")
    parser.add_argument('--fix', action='store_true',
                       help="Actually fix the files")
    parser.add_argument('--path', default='src/llm_call',
                       help="Path to search for Python files (default: src/llm_call)")
    
    args = parser.parse_args()
    
    if args.fix:
        dry_run = False
        print("🔧 Fixing bare except clauses...")
    else:
        dry_run = True
        print("🔍 Analyzing bare except clauses (dry run)...")
    
    # Find all Python files
    root_path = Path(args.path)
    python_files = list(root_path.rglob("*.py"))
    
    # Statistics
    total_files = 0
    total_issues = 0
    files_with_issues = []
    
    for py_file in sorted(python_files):
        issues = fix_file(py_file, dry_run=dry_run)
        if issues > 0:
            total_files += 1
            total_issues += issues
            files_with_issues.append((py_file, issues))
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"Summary:")
    print(f"  Total files scanned: {len(python_files)}")
    print(f"  Files with issues: {total_files}")
    print(f"  Total bare except clauses: {total_issues}")
    
    if files_with_issues and dry_run:
        print(f"\nTo fix these issues, run:")
        print(f"  python {__file__} --fix")
    elif not dry_run and total_issues > 0:
        print(f"\n✅ Fixed {total_issues} bare except clauses!")
        print(f"\nPlease review the changes and ensure:")
        print(f"  1. The suggested exception types are appropriate")
        print(f"  2. Any required imports have been added")
        print(f"  3. The error handling logic still makes sense")
    
    return 0 if dry_run else (1 if total_issues > 0 else 0)


if __name__ == "__main__":
    # Test with sample data
    test_context = """
        try:
            result = json.loads(response)
        except:
            return None
    """
    
    # This would suggest json.JSONDecodeError
    suggested = suggest_exception_type(test_context, "except:")
    assert suggested == "json.JSONDecodeError", f"Expected json.JSONDecodeError, got {suggested}"
    
    print("✅ Module validation passed")
    
    # Run main if not in test mode
    if len(sys.argv) > 1:
        sys.exit(main())