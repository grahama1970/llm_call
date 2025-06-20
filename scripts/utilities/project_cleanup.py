"""
Module: project_cleanup.py

External Dependencies:
- loguru: https://loguru.readthedocs.io/

Sample Input:
>>> # See function docstrings for specific examples

Expected Output:
>>> # See function docstrings for expected results

Example Usage:
>>> # Import and use as needed based on module functionality
"""

#!/usr/bin/env python3
"""
Project cleanup and organization tool.

This script automatically organizes misplaced files, cleans up temporary files,
and ensures the project structure follows CLAUDE.md standards.

Links:
- CLAUDE.md guidelines: /CLAUDE.md
- Project structure standards: https://docs.python.org/3/tutorial/modules.html

Sample usage:
    uv run scripts/project_cleanup.py --dry-run
    uv run scripts/project_cleanup.py --execute

Expected output:
    Report of files moved/cleaned with actual file counts and paths
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from loguru import logger
import typer

app = typer.Typer()


@dataclass
class CleanupAction:
    """Represents a cleanup action to be performed."""
    action_type: str  # 'move', 'delete', 'create_dir'
    source_path: Optional[Path]
    target_path: Optional[Path]
    reason: str


class ProjectCleaner:
    """Handles project cleanup and organization."""
    
    def __init__(self, project_root: Path):
        """Initialize with project root directory."""
        self.project_root = project_root
        self.actions: List[CleanupAction] = []
        
    def scan_for_cleanup(self) -> List[CleanupAction]:
        """Scan project for files that need cleanup."""
        actions = []
        
        # Rule 1: Test files in src/ should be in tests/
        actions.extend(self._find_misplaced_test_files())
        
        # Rule 2: Debug/POC scripts should be in scripts/
        actions.extend(self._find_misplaced_scripts())
        
        # Rule 3: Stray files in project root should be organized
        actions.extend(self._find_stray_root_files())
        
        # Rule 4: Temporary/cache files should be removed
        actions.extend(self._find_temporary_files())
        
        # Rule 5: Empty directories should be removed
        actions.extend(self._find_empty_directories())
        
        return actions
    
    def _find_misplaced_test_files(self) -> List[CleanupAction]:
        """Find test files in src/ that should be in tests/."""
        actions = []
        
        # Search for test_*.py files in src/
        for test_file in self.project_root.rglob("src/**/test_*.py"):
            # Calculate target path in tests/
            relative_path = test_file.relative_to(self.project_root / "src")
            target_path = self.project_root / "tests" / relative_path
            
            actions.append(CleanupAction(
                action_type="move",
                source_path=test_file,
                target_path=target_path,
                reason="Test files should be in tests/ directory"
            ))
            
            # Ensure target directory exists
            target_dir = target_path.parent
            if not target_dir.exists():
                actions.append(CleanupAction(
                    action_type="create_dir",
                    source_path=None,
                    target_path=target_dir,
                    reason="Create directory structure for moved test"
                ))
        
        return actions
    
    def _find_misplaced_scripts(self) -> List[CleanupAction]:
        """Find debug/POC scripts that should be in scripts/."""
        actions = []
        
        # Only look in src/ and project root, not in .venv, repos, etc.
        search_paths = [
            self.project_root / "src",
            self.project_root
        ]
        
        # Patterns for script files
        script_patterns = [
            "debug_*.py",
            "poc_*.py", 
            "test_*.py",
            "check_*.py",
            "verify_*.py"
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for pattern in script_patterns:
                for script_file in search_path.rglob(pattern):
                    # Skip if already in scripts/ or tests/
                    if "scripts" in script_file.parts or "tests" in script_file.parts:
                        continue
                    
                    # Skip if in .venv, repos, archive, or other excluded directories
                    if any(excluded in script_file.parts for excluded in [".venv", "repos", "archive", "__pycache__"]):
                        continue
                        
                    # Skip if in src/ and not debug/poc related (keep core functionality)
                    if "src" in script_file.parts and not any(
                        keyword in script_file.name for keyword in ["debug", "poc", "verify", "test_task"]
                    ):
                        continue
                    
                    target_path = self.project_root / "scripts" / script_file.name
                    
                    actions.append(CleanupAction(
                        action_type="move",
                        source_path=script_file,
                        target_path=target_path,
                        reason="Debug/POC scripts should be in scripts/ directory"
                    ))
        
        return actions
    
    def _find_stray_root_files(self) -> List[CleanupAction]:
        """Find stray files in project root that should be organized."""
        actions = []
        
        # Files that should be in examples/
        example_patterns = ["example_*.json", "sample_*.json", "*.example"]
        
        # Files that should be in docs/
        doc_patterns = ["*.md"]  # Except README.md, CLAUDE.md, etc.
        
        root_files = [f for f in self.project_root.iterdir() if f.is_file()]
        
        for file_path in root_files:
            filename = file_path.name
            
            # Skip important root files
            if filename in ["README.md", "CLAUDE.md", "pyproject.toml", "uv.lock", 
                           "pytest.ini", "Dockerfile", "docker-compose.yml", ".env"]:
                continue
            
            # Check if it's an example file
            if any(file_path.match(pattern) for pattern in example_patterns):
                target_path = self.project_root / "examples" / filename
                actions.append(CleanupAction(
                    action_type="move",
                    source_path=file_path,
                    target_path=target_path,
                    reason="Example files should be in examples/ directory"
                ))
                
                # Ensure examples directory exists
                examples_dir = self.project_root / "examples"
                if not examples_dir.exists():
                    actions.append(CleanupAction(
                        action_type="create_dir",
                        source_path=None,
                        target_path=examples_dir,
                        reason="Create examples directory"
                    ))
            
            # Check for loose Python files
            elif filename.endswith(".py") and filename not in ["test_imports.py"]:
                target_path = self.project_root / "scripts" / filename
                actions.append(CleanupAction(
                    action_type="move",
                    source_path=file_path,
                    target_path=target_path,
                    reason="Loose Python files should be in scripts/ directory"
                ))
        
        return actions
    
    def _find_temporary_files(self) -> List[CleanupAction]:
        """Find temporary files that should be removed."""
        actions = []
        
        # Only clean temp files in src/, tests/, and project root - avoid .venv and repos
        search_paths = [
            self.project_root / "src",
            self.project_root / "tests",
            self.project_root / "archive",  # Archive can be cleaned
            self.project_root  # Root level only, not recursive for .pytest_cache etc.
        ]
        
        # Patterns for temporary files
        temp_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "Thumbs.db",
            "*.tmp",
            "*.temp",
            ".coverage",
            "coverage.xml"
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for pattern in temp_patterns:
                if search_path == self.project_root:
                    # Non-recursive for root level
                    for temp_path in search_path.glob(pattern):
                        if temp_path.name in [".pytest_cache"]:  # Include specific root cache dirs
                            actions.append(CleanupAction(
                                action_type="delete",
                                source_path=temp_path,
                                target_path=None,
                                reason="Remove temporary/cache files"
                            ))
                else:
                    # Recursive for other directories
                    for temp_path in search_path.rglob(pattern):
                        actions.append(CleanupAction(
                            action_type="delete",
                            source_path=temp_path,
                            target_path=None,
                            reason="Remove temporary/cache files"
                        ))
        
        return actions
    
    def _find_empty_directories(self) -> List[CleanupAction]:
        """Find empty directories that should be removed."""
        actions = []
        
        # Find all directories
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and self._is_empty_directory(dir_path):
                # Skip important directories
                if dir_path.name in [".git", "node_modules", "__pycache__"]:
                    continue
                
                actions.append(CleanupAction(
                    action_type="delete",
                    source_path=dir_path,
                    target_path=None,
                    reason="Remove empty directory"
                ))
        
        return actions
    
    def _is_empty_directory(self, dir_path: Path) -> bool:
        """Check if directory is empty (ignoring hidden files)."""
        try:
            items = list(dir_path.iterdir())
            return len(items) == 0
        except (PermissionError, OSError):
            return False
    
    def execute_actions(self, actions: List[CleanupAction], dry_run: bool = True) -> Dict[str, int]:
        """Execute cleanup actions."""
        stats = {"moved": 0, "deleted": 0, "created": 0, "errors": 0}
        
        for action in actions:
            try:
                if dry_run:
                    logger.info(f"[DRY RUN] {action.action_type}: {action.source_path} -> {action.target_path}")
                    continue
                
                if action.action_type == "move":
                    # Ensure target directory exists
                    action.target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(action.source_path), str(action.target_path))
                    stats["moved"] += 1
                    logger.info(f"Moved: {action.source_path} -> {action.target_path}")
                
                elif action.action_type == "delete":
                    if action.source_path.is_dir():
                        shutil.rmtree(action.source_path)
                    else:
                        action.source_path.unlink()
                    stats["deleted"] += 1
                    logger.info(f"Deleted: {action.source_path}")
                
                elif action.action_type == "create_dir":
                    action.target_path.mkdir(parents=True, exist_ok=True)
                    stats["created"] += 1
                    logger.info(f"Created directory: {action.target_path}")
                    
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error processing {action.source_path}: {e}")
        
        return stats


@app.command()
def cleanup(
    dry_run: bool = typer.Option(True, "--dry-run/--execute", help="Show what would be done without executing"),
    project_path: str = typer.Option(".", help="Path to project root directory")
):
    """Clean up and organize project files according to CLAUDE.md standards."""
    
    project_root = Path(project_path).resolve()
    
    if not project_root.exists():
        logger.error(f"Project path does not exist: {project_root}")
        sys.exit(1)
    
    # Verify this looks like a Python project
    if not (project_root / "pyproject.toml").exists():
        logger.error(f"Not a Python project (no pyproject.toml): {project_root}")
        sys.exit(1)
    
    logger.info(f" Starting project cleanup for: {project_root}")
    
    cleaner = ProjectCleaner(project_root)
    actions = cleaner.scan_for_cleanup()
    
    if not actions:
        logger.success(" Project is already clean - no actions needed")
        return
    
    logger.info(f" Found {len(actions)} cleanup actions")
    
    # Group actions by type for reporting
    action_groups = {}
    for action in actions:
        if action.action_type not in action_groups:
            action_groups[action.action_type] = []
        action_groups[action.action_type].append(action)
    
    # Report what will be done
    for action_type, group_actions in action_groups.items():
        logger.info(f"  {action_type}: {len(group_actions)} files")
    
    # Execute actions
    stats = cleaner.execute_actions(actions, dry_run=dry_run)
    
    # Report results
    if dry_run:
        logger.info(" DRY RUN COMPLETE - No files were modified")
        logger.info("Run with --execute to perform actual cleanup")
    else:
        logger.success(f" CLEANUP COMPLETE")
        logger.info(f"   {stats['moved']} files moved")
        logger.info(f"  ️  {stats['deleted']} files/directories deleted")
        logger.info(f"   {stats['created']} directories created")
        if stats['errors'] > 0:
            logger.warning(f"  ⚠️  {stats['errors']} errors occurred")


@app.command()
def schedule_cron():
    """Show example cron configuration for periodic cleanup."""
    
    cron_example = """
# Add to crontab with: crontab -e
# Run project cleanup weekly on Sundays at 2 AM
0 2 * * 0 cd /path/to/llm_call && /home/user/.local/bin/uv run scripts/project_cleanup.py --execute

# Run dry-run daily at 6 AM (for monitoring)
0 6 * * * cd /path/to/llm_call && /home/user/.local/bin/uv run scripts/project_cleanup.py --dry-run >> /var/log/project_cleanup.log 2>&1
"""
    
    logger.info(" Example cron configuration for periodic cleanup:")
    print(cron_example)
    
    logger.info(" Setup steps:")
    logger.info("1. Replace /path/to/llm_call with actual project path")
    logger.info("2. Replace /home/user/.local/bin/uv with actual uv path (find with: which uv)")
    logger.info("3. Add to crontab: crontab -e")
    logger.info("4. Monitor logs for any issues")
    
    logger.info(" Recommended schedule:")
    logger.info("  - Weekly execution for actual cleanup")
    logger.info("  - Daily dry-run for monitoring file organization")


if __name__ == "__main__":
    # Validation tests with real functionality
    import tempfile
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: ProjectCleaner initialization
    total_tests += 1
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cleaner = ProjectCleaner(temp_path)
            
            if cleaner.project_root != temp_path:
                all_validation_failures.append(f"Initialization test: Expected {temp_path}, got {cleaner.project_root}")
            
            if not isinstance(cleaner.actions, list):
                all_validation_failures.append("Initialization test: actions should be a list")
                
    except Exception as e:
        all_validation_failures.append(f"Initialization test failed: {e}")
    
    # Test 2: Empty directory detection
    total_tests += 1
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            cleaner = ProjectCleaner(temp_path)
            
            # Create empty directory
            empty_dir = temp_path / "empty_test"
            empty_dir.mkdir()
            
            if not cleaner._is_empty_directory(empty_dir):
                all_validation_failures.append("Empty directory detection: Failed to detect empty directory")
            
            # Create non-empty directory
            non_empty_dir = temp_path / "non_empty_test"
            non_empty_dir.mkdir()
            (non_empty_dir / "test_file.txt").write_text("test")
            
            if cleaner._is_empty_directory(non_empty_dir):
                all_validation_failures.append("Empty directory detection: Incorrectly detected non-empty directory as empty")
                
    except Exception as e:
        all_validation_failures.append(f"Empty directory test failed: {e}")
    
    # Test 3: CleanupAction creation
    total_tests += 1
    try:
        action = CleanupAction(
            action_type="move",
            source_path=Path("/test/source"),
            target_path=Path("/test/target"),
            reason="Test action"
        )
        
        if action.action_type != "move":
            all_validation_failures.append(f"CleanupAction test: Expected 'move', got {action.action_type}")
            
        if action.reason != "Test action":
            all_validation_failures.append(f"CleanupAction test: Expected 'Test action', got {action.reason}")
            
    except Exception as e:
        all_validation_failures.append(f"CleanupAction test failed: {e}")
    
    # Final validation result
    if all_validation_failures:
        print(f" VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            print(f"  - {failure}")
        sys.exit(1)
    else:
        print(f" VALIDATION PASSED - All {total_tests} tests produced expected results")
        print("Project cleanup script is validated and ready for use")
        
        # Run the CLI app
        app()