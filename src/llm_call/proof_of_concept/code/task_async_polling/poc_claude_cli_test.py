#!/usr/bin/env python3
"""POC 1: Test Claude CLI execution directly"""

import subprocess
import os

# Simple test - just check if claude command exists
print("POC 1: Testing Claude CLI")

# Try different paths
paths_to_try = [
    "claude",
    "/home/graham/.nvm/versions/node/v22.15.0/bin/claude",
    "npx claude"
]

for path in paths_to_try:
    print(f"\nTrying: {path}")
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout[:100]}...")
        print(f"Stderr: {result.stderr[:100]}...")
    except subprocess.TimeoutExpired:
        print("Timed out")
    except FileNotFoundError:
        print("Command not found")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

# Check if it's an npm package
print("\nChecking NPM:")
try:
    result = subprocess.run(["npm", "list", "-g", "claude"], capture_output=True, text=True)
    print(f"NPM global packages: {result.stdout[:200]}")
except Exception as e:
    print(f"NPM check failed: {e}")
