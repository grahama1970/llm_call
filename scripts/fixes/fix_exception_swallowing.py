#!/usr/bin/env python3
"""
Fix exception swallowing patterns in critical files.
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple

# Critical files that should never swallow exceptions
CRITICAL_FILES = [
    "src/llm_call/core/caller.py",
    "src/llm_call/core/config/loader.py", 
    "src/llm_call/core/utils/text_chunker.py",
    "src/llm_call/core/utils/image_processing_utils.py",
    "src/llm_call/core/providers/claude_cli_local.py",
    "src/llm_call/core/providers/ollama_provider.py"
]

def fix_exception_swallowing(filepath: Path) -> int:
    """Fix exception swallowing in a file by replacing return None/False/etc with raise."""
    try:
        content = filepath.read_text()
        original_content = content
        lines = content.split('\n')
        changes = 0
        
        # Track if we're in an exception handler
        in_except = False
        except_indent = 0
        
        for i in range(len(lines)):
            line = lines[i]
            stripped = line.strip()
            
            # Detect exception blocks
            if 'except' in line and ':' in line:
                in_except = True
                except_indent = len(line) - len(line.lstrip())
                continue
            
            # Exit exception block if we see a line with less or equal indentation
            if in_except and line.strip() and (len(line) - len(line.lstrip())) <= except_indent:
                if not line.strip().startswith(('return', 'pass', 'raise')):
                    in_except = False
            
            # Fix problematic patterns in exception blocks
            if in_except and stripped:
                # Fix return None
                if stripped == "return None":
                    lines[i] = line.replace("return None", "raise")
                    changes += 1
                    print(f"  Line {i+1}: return None → raise")
                
                # Fix return False
                elif stripped == "return False":
                    lines[i] = line.replace("return False", "raise")
                    changes += 1
                    print(f"  Line {i+1}: return False → raise")
                
                # Fix return {}
                elif stripped == "return {}":
                    lines[i] = line.replace("return {}", "raise")
                    changes += 1
                    print(f"  Line {i+1}: return {{}} → raise")
                
                # Fix return []
                elif stripped == "return []":
                    lines[i] = line.replace("return []", "raise")
                    changes += 1
                    print(f"  Line {i+1}: return [] → raise")
                
                # Fix var = None assignments (for specific cases)
                elif "= None" in stripped and filepath.name == "text_chunker.py":
                    if "self.encoding = None" in stripped:
                        lines[i] = line.replace("self.encoding = None", 
                                               "raise ImportError('Failed to load encoding')")
                        changes += 1
                        print(f"  Line {i+1}: self.encoding = None → raise ImportError(...)")
                    elif "self.nlp = None" in stripped:
                        lines[i] = line.replace("self.nlp = None", 
                                               "raise ImportError('Failed to load spacy model')")
                        changes += 1
                        print(f"  Line {i+1}: self.nlp = None → raise ImportError(...)")
        
        if changes > 0:
            filepath.write_text('\n'.join(lines))
            
        return changes
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return 0

def main():
    """Fix exception swallowing in critical files."""
    print("🔧 Fixing exception swallowing patterns...\n")
    
    total_changes = 0
    fixed_files = 0
    
    for file_pattern in CRITICAL_FILES:
        filepath = Path(file_pattern)
        if filepath.exists():
            print(f"📄 Processing {filepath}...")
            changes = fix_exception_swallowing(filepath)
            if changes > 0:
                fixed_files += 1
                total_changes += changes
                print(f"   ✅ Fixed {changes} issues\n")
            else:
                print(f"   ✓ No issues found\n")
        else:
            print(f"⚠️  File not found: {filepath}\n")
    
    print(f"📊 Summary: Fixed {total_changes} issues in {fixed_files} files")
    
    # Test that imports still work
    print("\n🧪 Testing imports after fixes...")
    try:
        sys.path.insert(0, "src")
        from llm_call import make_llm_request
        print("✅ Imports working correctly!")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())