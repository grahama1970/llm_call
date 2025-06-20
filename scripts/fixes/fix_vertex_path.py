#!/usr/bin/env python3
"""
Fix GOOGLE_APPLICATION_CREDENTIALS path in all test files.
"""
import os
from pathlib import Path

def fix_vertex_path():
    """Fix hardcoded /home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json paths."""
    # The actual path
    actual_path = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"
    
    # Set the environment variable correctly
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = actual_path
    
    # Fix any test files that might be setting it wrong
    test_files = list(Path("tests").rglob("*.py"))
    
    for test_file in test_files:
        try:
            content = test_file.read_text()
            if "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json" in content:
                new_content = content.replace(
                    "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json",
                    actual_path
                )
                test_file.write_text(new_content)
                print(f"Fixed: {test_file}")
        except Exception as e:
            print(f"Error processing {test_file}: {e}")

if __name__ == "__main__":
    fix_vertex_path()
    print(f"\nSet GOOGLE_APPLICATION_CREDENTIALS={os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")