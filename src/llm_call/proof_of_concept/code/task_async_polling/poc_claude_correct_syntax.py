#!/usr/bin/env python3
"""POC 3: Test Claude Code with correct syntax"""

import subprocess
import os
import time

print("POC 3: Testing Claude Code with correct syntax")

claude_path = "/home/graham/.nvm/versions/node/v22.15.0/bin/claude"

# Test 1: Check version
print("\nTest 1: Version check")
result = subprocess.run([claude_path, "--version"], capture_output=True, text=True)
print(f"Version: {result.stdout.strip()}")

# Test 2: Simple print mode command
print("\nTest 2: Print mode with simple query")
cmd = [claude_path, "-p", "Say hello"]
print(f"Command: {' '.join(cmd)}")

# Start the process
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Wait for output with timeout
try:
    stdout, stderr = proc.communicate(timeout=5)
    print(f"Exit code: {proc.returncode}")
    print(f"Stdout: {stdout[:500]}")
    print(f"Stderr: {stderr[:500]}")
except subprocess.TimeoutExpired:
    print("Process timed out after 5 seconds")
    proc.kill()
    stdout, stderr = proc.communicate()
    print(f"Partial stdout: {stdout[:500] if stdout else 'None'}")
    print(f"Partial stderr: {stderr[:500] if stderr else 'None'}")

# Test 3: Check config
print("\nTest 3: Check config")
result = subprocess.run([claude_path, "config", "list"], capture_output=True, text=True, timeout=5)
print(f"Config list exit code: {result.returncode}")
print(f"Config output: {result.stdout[:500]}")
if result.stderr:
    print(f"Config errors: {result.stderr[:500]}")
