#!/usr/bin/env python3
"""
Show status of implemented usage functions vs TEST_MATRIX.md
"""
import os
import re
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# Parse TEST_MATRIX.md to get all test IDs
usage_root = Path(__file__).parent.parent
test_matrix_path = usage_root / "docs" / "TEST_MATRIX.md"
implemented_tests = set()
all_tests = {}

# Find implemented tests
test_dir = usage_root / "test_matrix"
for category_dir in test_dir.iterdir():
    if category_dir.is_dir():
        for test_file in category_dir.glob("usage_*.py"):
            # Extract test ID from filename
            match = re.search(r"usage_([FMVCDSPE]\d+\.\d+)_", test_file.name)
            if match:
                implemented_tests.add(match.group(1))

# Parse TEST_MATRIX.md
with open(test_matrix_path, 'r') as f:
    content = f.read()
    # Find all test IDs in tables
    pattern = r'\| ([FMVCDSPE]\d+\.\d+) \| (\*\*)?(\w+)(\*\*)? \|'
    for match in re.finditer(pattern, content):
        test_id = match.group(1)
        priority = "CRITICAL" if match.group(2) else match.group(3)
        all_tests[test_id] = priority

# Create status table
table = Table(title="Usage Function Implementation Status", box=box.ROUNDED)
table.add_column("Category", style="cyan")
table.add_column("Total", justify="right")
table.add_column("Implemented", justify="right", style="green")
table.add_column("Missing", justify="right", style="red")
table.add_column("Coverage", justify="right")

# Count by category
categories = {
    'F': 'Functional',
    'M': 'Multimodal', 
    'V': 'Validation',
    'C': 'Conversation',
    'D': 'Document',
    'S': 'Security',
    'P': 'Performance',
    'E': 'Error Handling'
}

for prefix, name in categories.items():
    total = sum(1 for tid in all_tests if tid.startswith(prefix))
    implemented = sum(1 for tid in implemented_tests if tid.startswith(prefix))
    missing = total - implemented
    coverage = f"{implemented/total*100:.0f}%" if total > 0 else "N/A"
    
    table.add_row(name, str(total), str(implemented), str(missing), coverage)

# Add total row
total_all = len(all_tests)
total_impl = len(implemented_tests)
total_missing = total_all - total_impl
total_coverage = f"{total_impl/total_all*100:.0f}%" if total_all > 0 else "0%"

table.add_section()
table.add_row("TOTAL", str(total_all), str(total_impl), str(total_missing), total_coverage, style="bold")

console.print("\n")
console.print(table)

# Show critical missing tests
critical_missing = [tid for tid, priority in all_tests.items() 
                   if tid not in implemented_tests and priority == "CRITICAL"]

if critical_missing:
    console.print("\n⚠️  Critical Tests Missing:", style="bold red")
    for test_id in sorted(critical_missing):
        console.print(f"   - {test_id}", style="red")

console.print(f"\n📁 Implemented tests found in: test_matrix/*/usage_*.py")
console.print(f"📊 Overall Coverage: {total_coverage} ({total_impl}/{total_all} tests)")