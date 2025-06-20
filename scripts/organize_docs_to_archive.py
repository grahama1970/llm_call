#!/usr/bin/env python3
"""
Module: organize_docs_to_archive.py
Description: Moves non-essential documentation files to the archive directory

External Dependencies:
- None (uses standard library only)

Sample Input:
>>> # Run the script to see which files would be moved
>>> python organize_docs_to_archive.py --dry-run

Expected Output:
>>> Would move: docs/verification/ -> docs/archive/verification/
>>> Would move: docs/99_tasks/ -> docs/archive/99_tasks/
>>> ... (list of files to be moved)

Example Usage:
>>> # Dry run to see what would be moved
>>> python organize_docs_to_archive.py --dry-run
>>> # Actually move the files
>>> python organize_docs_to_archive.py
"""

import os
import shutil
from pathlib import Path
import argparse
from datetime import datetime

def get_files_to_archive():
    """Define which files and directories should be moved to archive"""
    
    docs_dir = Path("docs")
    
    # Directories to move entirely
    dirs_to_move = [
        "verification",
        "99_tasks", 
        "testing",
        "research"
    ]
    
    # Individual files to move
    files_to_move = [
        "2025_STYLE_GUIDE_IMPROVEMENTS.md",
        "COMPLETE_FEATURE_CHECKLIST.md",
        "IMPROVEMENTS_IMPLEMENTED.md",
        "DOCKER_ARCHITECTURE_PROPOSAL.md",
        "DOCKER_SECURITY.md",
        "TASK_LIST_TEMPLATE_USAGE_FUNCTIONS_VERIFIED.md",
        "CLAUDE_CLI_DOCKER_SETUP.md",
        "prompt_scratch.md"
    ]
    
    # Patterns for files in reports/ directory (keep only essential ones)
    report_patterns_to_move = [
        "test_report_2025*.md",  # Timestamped test reports
        "daily_verification_*.md",
        "bug_fix_report_*.md",
        "bare_except_*.md",
        "bare_except_*.json",
        "fix_bare_excepts.py",  # Script in wrong location
        "*_analysis.md",
        "*_recommendations.md"
    ]
    
    return dirs_to_move, files_to_move, report_patterns_to_move

def ensure_archive_dir():
    """Ensure the archive directory exists"""
    archive_dir = Path("docs/archive")
    archive_dir.mkdir(exist_ok=True)
    return archive_dir

def move_to_archive(source_path: Path, archive_dir: Path, dry_run: bool = False):
    """Move a file or directory to the archive"""
    # Calculate relative path from docs/
    rel_path = source_path.relative_to(Path("docs"))
    dest_path = archive_dir / rel_path
    
    if dry_run:
        print(f"Would move: {source_path} -> {dest_path}")
    else:
        # Create parent directories
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the file/directory
        shutil.move(str(source_path), str(dest_path))
        print(f"Moved: {source_path} -> {dest_path}")

def main(dry_run: bool = False):
    """Main function to organize docs"""
    
    if dry_run:
        print("DRY RUN MODE - No files will be moved\n")
    
    docs_dir = Path("docs")
    archive_dir = ensure_archive_dir()
    
    dirs_to_move, files_to_move, report_patterns = get_files_to_archive()
    
    moved_count = 0
    
    # Move entire directories
    print("Moving directories to archive:")
    for dir_name in dirs_to_move:
        dir_path = docs_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            move_to_archive(dir_path, archive_dir, dry_run)
            moved_count += 1
    
    print("\nMoving individual files to archive:")
    # Move individual files
    for file_name in files_to_move:
        file_path = docs_dir / file_name
        if file_path.exists() and file_path.is_file():
            move_to_archive(file_path, archive_dir, dry_run)
            moved_count += 1
    
    print("\nMoving report files to archive:")
    # Move files from reports/ based on patterns
    reports_dir = docs_dir / "reports"
    if reports_dir.exists():
        for pattern in report_patterns:
            for file_path in reports_dir.glob(pattern):
                if file_path.is_file():
                    move_to_archive(file_path, archive_dir, dry_run)
                    moved_count += 1
        
        # Move dashboards subdirectory
        dashboards_path = reports_dir / "dashboards"
        if dashboards_path.exists() and dashboards_path.is_dir():
            move_to_archive(dashboards_path, archive_dir, dry_run)
            moved_count += 1
    
    print(f"\nTotal items {'would be' if dry_run else ''} moved: {moved_count}")
    
    if dry_run:
        print("\nTo actually move these files, run without --dry-run flag")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize docs by moving non-essential files to archive")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be moved without actually moving")
    args = parser.parse_args()
    
    main(dry_run=args.dry_run)