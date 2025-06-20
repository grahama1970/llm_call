#!/usr/bin/env python3
"""
Find all silent failures in the codebase.
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple

class SilentFailureFinder(ast.NodeVisitor):
    """Find patterns that silently swallow errors."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.issues: List[Tuple[int, str, str]] = []
        
    def visit_Try(self, node):
        """Check try/except blocks for silent failures."""
        for handler in node.handlers:
            # Check if exception handler has problematic patterns
            if handler.body:
                for stmt in handler.body:
                    issue = self._check_statement(stmt)
                    if issue:
                        self.issues.append((stmt.lineno, issue, self._get_context(handler)))
        
        self.generic_visit(node)
    
    def _check_statement(self, stmt) -> str:
        """Check if statement represents a silent failure."""
        if isinstance(stmt, ast.Pass):
            return "Silent pass in exception handler"
        
        elif isinstance(stmt, ast.Assign):
            # Check for var = None patterns
            if (len(stmt.targets) == 1 and 
                isinstance(stmt.value, ast.Constant) and 
                stmt.value.value is None):
                return f"Setting {ast.unparse(stmt.targets[0])} = None in exception"
        
        elif isinstance(stmt, ast.Return):
            # Check for return None/False/[]/{}
            if stmt.value is None:
                return "Returning None (implicit) in exception"
            elif isinstance(stmt.value, ast.Constant):
                if stmt.value.value in (None, False, True, "", 0):
                    return f"Returning {stmt.value.value} in exception"
            elif isinstance(stmt.value, ast.List) and not stmt.value.elts:
                return "Returning empty list [] in exception"
            elif isinstance(stmt.value, ast.Dict) and not stmt.value.keys:
                return "Returning empty dict {} in exception"
        
        return None
    
    def _get_context(self, handler) -> str:
        """Get exception type being caught."""
        if handler.type:
            return f"except {ast.unparse(handler.type)}"
        return "except (bare)"

def scan_file(filepath: Path) -> List[Tuple[str, int, str, str]]:
    """Scan a single file for silent failures."""
    try:
        content = filepath.read_text()
        tree = ast.parse(content)
        
        finder = SilentFailureFinder(str(filepath))
        finder.visit(tree)
        
        return [(str(filepath), line, issue, context) for line, issue, context in finder.issues]
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
        return []

def main():
    """Find all silent failures in the codebase."""
    src_dir = Path("src")
    
    all_issues = []
    python_files = list(src_dir.rglob("*.py"))
    
    print(f"Scanning {len(python_files)} Python files for silent failures...")
    
    for filepath in python_files:
        issues = scan_file(filepath)
        all_issues.extend(issues)
    
    if all_issues:
        print(f"\n🚨 Found {len(all_issues)} silent failure patterns:\n")
        
        # Group by file
        by_file = {}
        for filepath, line, issue, context in all_issues:
            if filepath not in by_file:
                by_file[filepath] = []
            by_file[filepath].append((line, issue, context))
        
        # Sort by number of issues
        sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
        
        for filepath, issues in sorted_files:
            print(f"\n📄 {filepath} ({len(issues)} issues):")
            for line, issue, context in sorted(issues, key=lambda x: x[0]):
                print(f"   Line {line}: {issue} in {context}")
    else:
        print("\n✅ No silent failures found!")
    
    return len(all_issues)

if __name__ == "__main__":
    issue_count = main()
    sys.exit(1 if issue_count > 0 else 0)