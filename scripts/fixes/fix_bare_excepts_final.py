#!/usr/bin/env python3
"""
Module: fix_bare_excepts_final.py
Description: Production-ready script to fix bare except clauses in Python code

External Dependencies:
- None (uses standard library only)

Sample Input:
>>> # Files with bare except clauses in src/llm_call/

Expected Output:
>>> Fixed 12 bare except clauses across 9 files
>>> Added 3 import statements

Example Usage:
>>> python scripts/fix_bare_excepts_final.py --analyze  # Dry run
>>> python scripts/fix_bare_excepts_final.py --fix      # Apply fixes
>>> python scripts/fix_bare_excepts_final.py --fix --safe  # Only fix bare excepts, not generic
"""

import os
import re
import sys
import argparse
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
from datetime import datetime
import json

# Comprehensive exception mappings
EXCEPTION_PATTERNS = [
    # JSON operations - highest priority
    (r"json\.loads|json\.load|json\.dumps|json\.dump|JSON", "json.JSONDecodeError", None),
    
    # Type conversions
    (r"int\([^)]+\)|float\([^)]+\)|bool\([^)]+\)", "ValueError", None),
    
    # File operations
    (r"open\(|\.read\(\)|\.write\(|\.close\(\)|with\s+open", "IOError", None),
    (r"Path\(.*?\)\.|pathlib", "FileNotFoundError", None),
    
    # Dictionary/list operations
    (r"\.get\(|(?<!\w)get\(|(?<!\w)\[['\"][\w]+['\"]\]", "KeyError", None),
    (r"\[\d+\]|\.pop\(\d+\)|list\[|tuple\[", "IndexError", None),
    
    # Attribute access
    (r"(?<!\w)\.(\w+)(?:\(|$)|getattr\(|hasattr\(", "AttributeError", None),
    
    # Network/HTTP
    (r"requests\.|response\.|http|urllib|urlopen", "requests.RequestException", "requests"),
    (r"timeout|Timeout", "TimeoutError", None),
    
    # Database operations
    (r"\.execute\(|\.executemany\(|\.commit\(\)|\.rollback\(\)|cursor|sqlite", "sqlite3.Error", "sqlite3"),
    
    # Subprocess
    (r"subprocess\.|Popen|check_output|run\(.*shell", "subprocess.SubprocessError", "subprocess"),
    
    # Async operations
    (r"await\s+|async\s+|asyncio\.|gather\(|create_task", "asyncio.TimeoutError", "asyncio"),
    
    # String operations
    (r"\.encode\(|\.decode\(|encoding=|utf-8|unicode", "UnicodeDecodeError", None),
    
    # Math operations
    (r"math\.|sqrt\(|pow\(|\/\s*0|ZeroDivision", "ZeroDivisionError", None),
    
    # Import operations
    (r"import\s+|from\s+.*\s+import|__import__", "ImportError", None),
    
    # Parsing operations
    (r"parse\(|parser\.|ast\.", "SyntaxError", None),
    (r"yaml\.|YAML", "yaml.YAMLError", "yaml"),
    (r"xml\.|XML|ElementTree", "xml.etree.ElementTree.ParseError", "xml.etree.ElementTree"),
    
    # Rich console operations
    (r"console\.print|Panel\(|Table\(|rich\.", "Exception", None),  # Keep generic
    
    # Base64 operations
    (r"base64\.|b64encode|b64decode", "ValueError", None),
    
    # Default fallback
    (r".*", "Exception", None),
]


class ExceptionFixer:
    def __init__(self, safe_mode: bool = False, backup: bool = True):
        self.safe_mode = safe_mode
        self.backup = backup
        self.stats = {
            'files_modified': 0,
            'bare_excepts_fixed': 0,
            'generic_excepts_fixed': 0,
            'imports_added': 0,
            'errors': []
        }
    
    def find_matching_exception(self, context: str) -> Tuple[str, Optional[str]]:
        """Find the most appropriate exception for the given context."""
        # Check each pattern in order
        for pattern, exception, import_module in EXCEPTION_PATTERNS:
            if re.search(pattern, context, re.IGNORECASE | re.DOTALL):
                return exception, import_module
        
        # Default fallback
        return "Exception", None
    
    def get_try_block_context(self, lines: List[str], except_line: int) -> str:
        """Extract the try block context for better exception matching."""
        indent = len(lines[except_line]) - len(lines[except_line].lstrip())
        context_lines = []
        
        # Look backwards for the try statement
        i = except_line - 1
        while i >= 0:
            line = lines[i]
            line_indent = len(line) - len(line.lstrip())
            
            # Found the matching try block
            if line.strip().startswith('try:') and line_indent == indent:
                # Collect all lines in the try block
                j = i + 1
                while j < except_line:
                    if lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) > indent:
                        context_lines.append(lines[j])
                    j += 1
                break
            i -= 1
        
        return '\n'.join(context_lines)
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix bare except clauses in a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            original_lines = lines.copy()
            modifications = []
            required_imports = set()
            
            # Find all except clauses
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Skip if it's a comment or string
                if stripped.startswith('#') or '"""' in line or "'''" in line:
                    continue
                
                # Check for bare except
                if re.match(r'^\s*except\s*:\s*(?:#.*)?$', line):
                    context = self.get_try_block_context(lines, i)
                    exception_type, import_needed = self.find_matching_exception(context)
                    
                    if import_needed:
                        required_imports.add(import_needed)
                    
                    # Replace the line
                    indent = len(line) - len(line.lstrip())
                    new_line = ' ' * indent + f"except {exception_type}:\n"
                    modifications.append((i, 'bare', line.strip(), new_line))
                    lines[i] = new_line
                
                # Check for generic Exception (unless in safe mode)
                elif not self.safe_mode and re.match(r'^\s*except\s+Exception\s*(as\s+\w+)?\s*:\s*(?:#.*)?$', line):
                    # Check if this is a final catch-all
                    if not self.is_final_catchall(lines, i):
                        context = self.get_try_block_context(lines, i)
                        exception_type, import_needed = self.find_matching_exception(context)
                        
                        # Only replace if we found something more specific
                        if exception_type != "Exception":
                            if import_needed:
                                required_imports.add(import_needed)
                            
                            # Preserve the variable name if present
                            match = re.match(r'^\s*except\s+Exception\s+(as\s+\w+)?\s*:', line)
                            var_clause = match.group(1) if match.group(1) else ""
                            
                            indent = len(line) - len(line.lstrip())
                            new_line = ' ' * indent + f"except {exception_type}{' ' + var_clause if var_clause else ''}:\n"
                            modifications.append((i, 'generic', line.strip(), new_line))
                            lines[i] = new_line
            
            # Add required imports
            if required_imports:
                import_line_idx = self.find_import_location(lines)
                for module in sorted(required_imports):
                    if not self.has_import(lines, module):
                        lines.insert(import_line_idx, f"import {module}\n")
                        import_line_idx += 1
                        self.stats['imports_added'] += 1
            
            # Only write if changes were made
            if modifications or required_imports:
                # Create backup if requested
                if self.backup:
                    shutil.copy2(file_path, f"{file_path}.bak")
                
                # Write the fixed file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                # Update statistics
                self.stats['files_modified'] += 1
                for _, fix_type, _, _ in modifications:
                    if fix_type == 'bare':
                        self.stats['bare_excepts_fixed'] += 1
                    else:
                        self.stats['generic_excepts_fixed'] += 1
                
                # Report modifications
                print(f"\n✅ Fixed {file_path}")
                for line_num, fix_type, old, new in modifications:
                    print(f"  Line {line_num + 1}: {old} → {new.strip()}")
                
                return True
            
            return False
            
        except Exception as e:
            self.stats['errors'].append(f"{file_path}: {str(e)}")
            print(f"❌ Error processing {file_path}: {e}")
            return False
    
    def is_final_catchall(self, lines: List[str], current_idx: int) -> bool:
        """Check if this Exception handler is a final catch-all."""
        indent = len(lines[current_idx]) - len(lines[current_idx].lstrip())
        
        # Look for other except clauses before this one
        i = current_idx - 1
        while i >= 0:
            line = lines[i]
            line_indent = len(line) - len(line.lstrip())
            
            if line.strip().startswith('try:') and line_indent == indent:
                break
            
            if line.strip().startswith('except') and line_indent == indent:
                # If we find a more specific except, this is a catch-all
                if not re.match(r'^\s*except\s*:\s*$', line) and 'Exception' not in line:
                    return True
            
            i -= 1
        
        return False
    
    def find_import_location(self, lines: List[str]) -> int:
        """Find the best location to add imports."""
        # Look for existing imports
        last_import = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                last_import = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                # First non-comment, non-import line
                if last_import == 0:
                    return i
                break
        
        return last_import
    
    def has_import(self, lines: List[str], module: str) -> bool:
        """Check if module is already imported."""
        for line in lines[:50]:  # Check first 50 lines
            if f"import {module}" in line or f"from {module}" in line:
                return True
        return False
    
    def analyze_files(self, files: List[Path]) -> Dict[str, List[Dict]]:
        """Analyze files without making changes."""
        analysis = {}
        
        for file_path in files:
            issues = []
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines):
                    if re.match(r'^\s*except\s*:\s*(?:#.*)?$', line):
                        context = self.get_try_block_context(lines, i)
                        exception_type, _ = self.find_matching_exception(context)
                        issues.append({
                            'line': i + 1,
                            'type': 'bare',
                            'current': line.strip(),
                            'suggested': f"except {exception_type}:",
                            'context': context[:200]
                        })
                    
                    elif not self.safe_mode and re.match(r'^\s*except\s+Exception\s*(as\s+\w+)?\s*:\s*(?:#.*)?$', line):
                        if not self.is_final_catchall(lines, i):
                            context = self.get_try_block_context(lines, i)
                            exception_type, _ = self.find_matching_exception(context)
                            
                            if exception_type != "Exception":
                                issues.append({
                                    'line': i + 1,
                                    'type': 'generic',
                                    'current': line.strip(),
                                    'suggested': f"except {exception_type}:",
                                    'context': context[:200]
                                })
                
                if issues:
                    analysis[str(file_path)] = issues
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return analysis


def main():
    parser = argparse.ArgumentParser(description="Fix bare except clauses in Python code")
    parser.add_argument('--analyze', action='store_true', 
                       help="Analyze without making changes (default)")
    parser.add_argument('--fix', action='store_true',
                       help="Apply fixes to files")
    parser.add_argument('--safe', action='store_true',
                       help="Only fix bare excepts, leave generic Exception handlers")
    parser.add_argument('--no-backup', action='store_true',
                       help="Don't create backup files")
    parser.add_argument('--path', default='src/llm_call',
                       help="Path to search for Python files")
    parser.add_argument('--report', type=str,
                       help="Save analysis report to file")
    
    args = parser.parse_args()
    
    # Default to analyze if neither flag is set
    if not args.fix and not args.analyze:
        args.analyze = True
    
    # Find Python files
    root = Path(args.path)
    if not root.exists():
        print(f"Error: Path {root} does not exist")
        return 1
    
    py_files = list(root.rglob("*.py"))
    print(f"Found {len(py_files)} Python files in {root}")
    
    # Create fixer instance
    fixer = ExceptionFixer(safe_mode=args.safe, backup=not args.no_backup)
    
    if args.analyze:
        print("\n🔍 Analyzing files...")
        analysis = fixer.analyze_files(py_files)
        
        if not analysis:
            print("✅ No bare except clauses found!")
            return 0
        
        # Display analysis
        total_issues = sum(len(issues) for issues in analysis.values())
        print(f"\nFound {total_issues} issues in {len(analysis)} files:")
        
        for file_path, issues in analysis.items():
            print(f"\n📄 {file_path} ({len(issues)} issues)")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"  Line {issue['line']}: {issue['current']}")
                print(f"    → Suggested: {issue['suggested']}")
            if len(issues) > 3:
                print(f"  ... and {len(issues) - 3} more")
        
        # Save report if requested
        if args.report:
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'total_files': len(py_files),
                'files_with_issues': len(analysis),
                'total_issues': total_issues,
                'analysis': analysis
            }
            
            with open(args.report, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"\n📊 Report saved to {args.report}")
        
        print(f"\nTo fix these issues, run: {sys.argv[0]} --fix")
        
    elif args.fix:
        print("\n🔧 Fixing bare except clauses...")
        
        for py_file in py_files:
            fixer.fix_file(py_file)
        
        # Print summary
        print(f"\n{'=' * 60}")
        print("Summary:")
        print(f"  Files modified: {fixer.stats['files_modified']}")
        print(f"  Bare excepts fixed: {fixer.stats['bare_excepts_fixed']}")
        print(f"  Generic excepts fixed: {fixer.stats['generic_excepts_fixed']}")
        print(f"  Imports added: {fixer.stats['imports_added']}")
        
        if fixer.stats['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in fixer.stats['errors']:
                print(f"  - {error}")
        
        if fixer.stats['files_modified'] > 0:
            print(f"\n✅ Successfully fixed {fixer.stats['bare_excepts_fixed'] + fixer.stats['generic_excepts_fixed']} exceptions!")
            if not args.no_backup:
                print("📁 Backup files created with .bak extension")
    
    return 0


if __name__ == "__main__":
    # Module validation
    fixer = ExceptionFixer()
    context = "result = json.loads(data)"
    exception, module = fixer.find_matching_exception(context)
    assert exception == "json.JSONDecodeError", f"Expected json.JSONDecodeError, got {exception}"
    print("✅ Module validation passed")
    
    sys.exit(main())