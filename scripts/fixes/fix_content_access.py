#!/usr/bin/env python3
"""
Fix content access in test files to handle ModelResponse objects.
"""
from pathlib import Path
import re

def fix_content_access(filepath: Path):
    """Fix content access patterns."""
    content = filepath.read_text()
    original = content
    
    # Fix the pattern that accesses content from choices
    pattern = r'(result\.choices if hasattr\(result, "choices"\) else result\["choices"\])\[0\]\["message"\]\["content"\]'
    
    # Find all occurrences and replace them with proper access
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        if pattern in line or '[0]["message"]["content"]' in line:
            # Check if we already have the message variable defined
            if i > 0 and "message = " in lines[i-1]:
                # Use the message variable
                new_line = re.sub(r'.*\["message"\]\["content"\].*\.strip\(\)', 
                                '        content = message.content if hasattr(message, "content") else message["content"]\n        content = content.strip()', 
                                line)
            else:
                # Need to access through first_choice
                new_line = re.sub(pattern + r'\.strip\(\)',
                                'first_choice = (result.choices if hasattr(result, "choices") else result["choices"])[0]\n        message = first_choice.message if hasattr(first_choice, "message") else first_choice["message"]\n        content = message.content if hasattr(message, "content") else message["content"]\n        content = content.strip()',
                                line)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    if new_content != original:
        filepath.write_text(new_content)
        return True
    return False

def main():
    """Fix all test files."""
    test_file = Path("tests/local/critical/test_minimal_improved.py")
    
    if fix_content_access(test_file):
        print(f"Fixed: {test_file}")
    else:
        print("No changes needed")

if __name__ == "__main__":
    main()