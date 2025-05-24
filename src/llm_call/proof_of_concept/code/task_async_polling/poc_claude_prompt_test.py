#!/usr/bin/env python3
"""POC 2: Test Claude CLI with actual prompt"""

import subprocess
import json
import os

print("POC 2: Testing Claude prompt execution")

claude_path = "/home/graham/.nvm/versions/node/v22.15.0/bin/claude"

# Test 1: Simple command
print("\nTest 1: Simple test")
cmd = [claude_path, "-p", "Say hello", "--output-format", "json"]
print(f"Command: {' '.join(cmd)}")

result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
print(f"Exit code: {result.returncode}")
print(f"Stdout length: {len(result.stdout)}")
print(f"Stderr: {result.stderr[:200]}")
if result.returncode == 0 and result.stdout:
    print(f"Output preview: {result.stdout[:200]}...")

# Test 2: With workspace
print("\nTest 2: With workspace directory")
workspace = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/claude_poc_workspace"
if os.path.exists(workspace):
    os.chdir(workspace)
    print(f"Changed to workspace: {os.getcwd()}")
    
    cmd = [claude_path, "-p", "Say world", "--output-format", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    print(f"Exit code: {result.returncode}")
    if result.returncode == 0:
        print("Success!")
    else:
        print(f"Failed with stderr: {result.stderr[:500]}")
else:
    print(f"Workspace not found: {workspace}")
