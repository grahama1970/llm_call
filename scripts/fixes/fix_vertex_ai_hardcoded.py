#!/usr/bin/env python3
"""
Fix hardcoded /home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json paths in the codebase.
"""
import os
from pathlib import Path

def fix_hardcoded_paths():
    """Fix all hardcoded Vertex AI paths."""
    actual_path = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"
    
    # Set environment variable
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = actual_path
    
    # Fix in all Python files
    for py_file in Path(".").rglob("*.py"):
        try:
            content = py_file.read_text()
            if "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json" in content:
                new_content = content.replace(
                    "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json",
                    actual_path
                )
                py_file.write_text(new_content)
                print(f"Fixed: {py_file}")
        except Exception as e:
            print(f"Error processing {py_file}: {e}")
    
    # Also check yml files
    for yml_file in Path(".").rglob("*.yml"):
        try:
            content = yml_file.read_text()
            if "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json" in content:
                new_content = content.replace(
                    "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json",
                    actual_path
                )
                yml_file.write_text(new_content)
                print(f"Fixed: {yml_file}")
        except Exception as e:
            print(f"Error processing {yml_file}: {e}")
    
    # Check where GOOGLE_APPLICATION_CREDENTIALS is being set
    print("\nSearching for GOOGLE_APPLICATION_CREDENTIALS usage...")
    for py_file in Path(".").rglob("*.py"):
        try:
            content = py_file.read_text()
            if "GOOGLE_APPLICATION_CREDENTIALS" in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "GOOGLE_APPLICATION_CREDENTIALS" in line and "/app/" in line:
                        print(f"{py_file}:{i+1}: {line.strip()}")
        except:
            pass

if __name__ == "__main__":
    fix_hardcoded_paths()