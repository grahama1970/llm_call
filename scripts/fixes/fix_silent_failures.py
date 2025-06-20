#!/usr/bin/env python3
"""
Fix all silent failures in the codebase.
"""
import re
from pathlib import Path
from typing import List, Tuple

# Define fixes for each pattern
FIXES = [
    # Critical fixes - these should always raise
    {
        "files": ["src/llm_call/core/caller.py"],
        "pattern": r"(\s+)return None(\s*#.*)?$",
        "replacement": r"\1raise",
        "in_except": True
    },
    {
        "files": ["src/llm_call/core/config/loader.py"],
        "pattern": r"(\s+)return \{\}(\s*#.*)?$",
        "replacement": r"\1raise",
        "in_except": True
    },
    {
        "files": ["src/llm_call/core/utils/text_chunker.py"],
        "pattern": r"(\s+)self\.encoding = None(\s*#.*)?$",
        "replacement": r"\1raise ImportError('Failed to load encoding')",
        "in_except": True
    },
    {
        "files": ["src/llm_call/core/utils/text_chunker.py"],
        "pattern": r"(\s+)self\.nlp = None(\s*#.*)?$",
        "replacement": r"\1raise ImportError('Failed to load spacy model')",
        "in_except": True
    },
    {
        "files": ["src/granger_common/pdf_handler.py"],
        "pattern": r"(\s+)PyPDF2 = None(\s*#.*)?$",
        "replacement": r"\1raise ImportError('PyPDF2 not installed')",
        "in_except": True
    },
    {
        "files": ["src/granger_common/pdf_handler.py"],
        "pattern": r"(\s+)PdfReader = None(\s*#.*)?$",
        "replacement": r"\1raise ImportError('PdfReader not available')",
        "in_except": True
    },
    # Image processing - should raise for critical paths
    {
        "files": ["src/llm_call/core/utils/image_processing_utils.py"],
        "pattern": r"(\s+)return None(\s*#.*)?$",
        "replacement": r"\1raise",
        "in_except": True
    },
    # Pass statements should at least log
    {
        "files": ["src/llm_call/core/api/mcp_handler_wrapper.py"],
        "pattern": r"(\s+)pass(\s*#.*)?$",
        "replacement": r"\1logger.warning(f'Ignoring error: {e}')",
        "in_except": True
    }
]

def fix_file(filepath: Path, fixes: List[dict]) -> int:
    """Fix silent failures in a single file."""
    try:
        content = filepath.read_text()
        original = content
        changes = 0
        
        # Apply relevant fixes
        for fix in fixes:
            if any(str(filepath).endswith(f) for f in fix["files"]):
                if fix.get("in_except"):
                    # Only fix patterns inside except blocks
                    # This is a simplified approach - a proper AST-based fix would be better
                    lines = content.split('\n')
                    new_lines = []
                    in_except = False
                    
                    for i, line in enumerate(lines):
                        if re.match(r'\s*except\s+.*:', line):
                            in_except = True
                        elif re.match(r'\s*(try|finally|else|elif|if|for|while|def|class).*:', line):
                            in_except = False
                        elif in_except and re.match(fix["pattern"], line):
                            new_line = re.sub(fix["pattern"], fix["replacement"], line)
                            new_lines.append(new_line)
                            changes += 1
                            continue
                        
                        new_lines.append(line)
                    
                    content = '\n'.join(new_lines)
                else:
                    # Apply globally
                    content, n = re.subn(fix["pattern"], fix["replacement"], content)
                    changes += n
        
        if content != original:
            filepath.write_text(content)
            return changes
        
        return 0
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return 0

def main():
    """Fix all silent failures."""
    print("🔧 Fixing silent failures in critical files...")
    
    total_changes = 0
    
    for fix_group in FIXES:
        for file_pattern in fix_group["files"]:
            for filepath in Path(".").glob(file_pattern):
                if filepath.exists():
                    changes = fix_file(filepath, [fix_group])
                    if changes > 0:
                        print(f"✅ Fixed {changes} issues in {filepath}")
                        total_changes += changes
    
    print(f"\n📊 Total fixes applied: {total_changes}")
    
    # Run the scanner again to see remaining issues
    print("\n🔍 Scanning for remaining silent failures...")
    import subprocess
    result = subprocess.run(
        ["python", "scripts/find_silent_failures.py"],
        capture_output=True,
        text=True
    )
    print(result.stdout)

if __name__ == "__main__":
    main()