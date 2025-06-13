#!/usr/bin/env python3
"""
Module: fix_bare_excepts_only.py  
Description: Fixes only bare 'except:' clauses, leaving 'except Exception:' untouched

External Dependencies:
- None (uses standard library only)

Sample Input:
>>> # Python files with bare except: clauses

Expected Output:
>>> Fixed 9 bare except clauses in 7 files

Example Usage:
>>> python scripts/fix_bare_excepts_only.py  # Preview changes
>>> python scripts/fix_bare_excepts_only.py --apply  # Apply changes
"""

import re
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Dict

# File-specific exception mappings based on actual usage
SPECIFIC_FIXES = {
    "cli/main.py": {
        222: ("Exception", "# Fallback to plain output if JSON parsing fails"),
        1097: ("ValueError", "# Handle non-integer input")
    },
    "core/utils/document_summarizer.py": {
        104: ("KeyError", "# Model not found, fallback to default encoding"),
        385: ("Exception", "# Generic file processing error")
    },
    "core/validation/ai_validator_base.py": {
        365: ("(json.JSONDecodeError, KeyError, TypeError)", "# Parse error in validation response")
    },
    "core/providers/claude/focused_claude_extractor.py": {
        149: ("Exception", "# Keep generic as marked with #nosec")
    },
    "proof_of_concept/litellm_client_poc.py": {
        402: ("ImportError", "# Pillow not installed")
    },
    "proof_of_concept/polling_server.py": {
        214: ("Exception", "# Server shutdown handler")
    },
    "proof_of_concept/code/task_004_test_prompts/poc_27_exponential_backoff.py": {
        352: ("KeyError", "# Missing response key")
    }
}


def fix_bare_except(file_path: Path, preview_only: bool = True) -> List[Tuple[int, str, str]]:
    """Fix bare except clauses in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    changes = []
    modified_lines = lines.copy()
    
    # Get relative path for matching
    rel_path = str(file_path).replace("src/llm_call/", "")
    specific_fixes = SPECIFIC_FIXES.get(rel_path, {})
    
    for i, line in enumerate(lines):
        if re.match(r'^\s*except\s*:\s*(?:#.*)?$', line):
            line_num = i + 1
            indent = len(line) - len(line.lstrip())
            
            # Use specific fix if available
            if line_num in specific_fixes:
                exception_type, comment = specific_fixes[line_num]
            else:
                # Default based on context
                exception_type = "Exception"
                comment = ""
            
            new_line = ' ' * indent + f"except {exception_type}:  {comment}\n"
            changes.append((line_num, line.strip(), new_line.strip()))
            modified_lines[i] = new_line
    
    if changes and not preview_only:
        # Backup original
        shutil.copy2(file_path, f"{file_path}.bak")
        
        # Write modified file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
    
    return changes


def main():
    """Fix bare except clauses in llm_call codebase."""
    preview_only = "--apply" not in sys.argv
    
    if preview_only:
        print("🔍 Preview mode - no files will be modified")
        print("   Run with --apply to make changes\n")
    else:
        print("🔧 Applying fixes...\n")
    
    # Files known to have bare except clauses
    files_to_check = [
        "src/llm_call/cli/main.py",
        "src/llm_call/core/utils/document_summarizer.py", 
        "src/llm_call/core/validation/ai_validator_base.py",
        "src/llm_call/core/providers/claude/focused_claude_extractor.py",
        "src/llm_call/proof_of_concept/litellm_client_poc.py",
        "src/llm_call/proof_of_concept/polling_server.py",
        "src/llm_call/proof_of_concept/code/task_004_test_prompts/poc_27_exponential_backoff.py"
    ]
    
    total_changes = 0
    files_modified = 0
    
    for file_path in files_to_check:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        changes = fix_bare_except(path, preview_only)
        
        if changes:
            files_modified += 1
            total_changes += len(changes)
            print(f"📄 {file_path}")
            
            for line_num, old, new in changes:
                print(f"  Line {line_num}: {old}")
                print(f"         → {new}")
            print()
    
    # Summary
    print("=" * 60)
    if preview_only:
        print(f"Would fix {total_changes} bare except clauses in {files_modified} files")
        print("\nRun with --apply to make these changes")
    else:
        print(f"✅ Fixed {total_changes} bare except clauses in {files_modified} files")
        print("📁 Backup files created with .bak extension")
        
        # Verify fixes
        print("\n🔍 Verifying fixes...")
        bare_count = 0
        for file_path in files_to_check:
            path = Path(file_path)
            if path.exists():
                with open(path, 'r') as f:
                    content = f.read()
                    matches = re.findall(r'^\s*except\s*:\s*(?:#.*)?$', content, re.MULTILINE)
                    bare_count += len(matches)
        
        if bare_count == 0:
            print("✅ All bare except clauses have been fixed!")
        else:
            print(f"⚠️  {bare_count} bare except clauses remain")
    
    return 0


if __name__ == "__main__":
    # Test the specific fixes are valid
    test_line = "    except:"
    match = re.match(r'^\s*except\s*:\s*(?:#.*)?$', test_line)
    assert match is not None, "Regex pattern failed to match bare except"
    
    print("✅ Module validation passed\n")
    sys.exit(main())