#!/usr/bin/env python3
"""
Module: fix_remaining_issues.py
Description: Fix the remaining failing tests

External Dependencies:
- None

Sample Input:
>>> python fix_remaining_issues.py

Expected Output:
>>> Fixed all remaining issues
"""

import os
import sys
import subprocess
from pathlib import Path

# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def diagnose_failures():
    """Run a quick test to see what's failing."""
    print("🔍 Diagnosing failures...")
    
    # Test 1: Core Features - ask function
    print("\n1. Testing ask function...")
    test_code = '''
import asyncio
from llm_call import ask

async def test():
    try:
        result = await ask("Reply with OK", model="gpt-3.5-turbo")
        print(f"Result: {result}")
        return "OK" in str(result)
    except Exception as e:
        print(f"Error: {e}")
        return False

result = asyncio.run(test())
print(f"Success: {result}")
'''
    
    with open("/tmp/test_ask.py", "w") as f:
        f.write(test_code)
    
    result = subprocess.run([sys.executable, "/tmp/test_ask.py"], capture_output=True, text=True)
    print(f"Output: {result.stdout}")
    print(f"Error: {result.stderr}")
    
    # Test 2: API Health endpoint
    print("\n2. Testing API health endpoint...")
    result = subprocess.run(["curl", "-s", "http://localhost:8001/health"], capture_output=True, text=True)
    print(f"API Response: {result.stdout}")
    
    # Test 3: Error handling - timeout
    print("\n3. Testing timeout handling...")
    result = subprocess.run([
        "/home/graham/.claude/commands/llm_call", 
        "--query", "Test", 
        "--model", "gpt-3.5-turbo",
        "--timeout", "0.001"
    ], capture_output=True, text=True)
    print(f"Timeout test output: {result.stdout}")
    print(f"Timeout test error: {result.stderr}")
    
    # Test 4: Cache test
    print("\n4. Testing cache...")
    cache_test = '''
import time
import subprocess

# First call
start1 = time.time()
result1 = subprocess.run([
    "/home/graham/.claude/commands/llm_call",
    "--query", "What is 2+2?",
    "--model", "gpt-3.5-turbo",
    "--cache"
], capture_output=True, text=True)
time1 = time.time() - start1

# Second call (cached)
start2 = time.time()
result2 = subprocess.run([
    "/home/graham/.claude/commands/llm_call",
    "--query", "What is 2+2?",
    "--model", "gpt-3.5-turbo",
    "--cache"
], capture_output=True, text=True)
time2 = time.time() - start2

print(f"First call: {time1:.2f}s")
print(f"Second call: {time2:.2f}s")
print(f"Cache speedup: {time1/time2:.2f}x")
print(f"Output1: {result1.stdout[:100]}")
print(f"Output2: {result2.stdout[:100]}")
'''
    
    with open("/tmp/test_cache.py", "w") as f:
        f.write(cache_test)
    
    result = subprocess.run([sys.executable, "/tmp/test_cache.py"], capture_output=True, text=True)
    print(f"Cache test: {result.stdout}")

def fix_ask_function():
    """Fix the ask function issue."""
    print("\n🔧 Fixing ask function...")
    
    # Check if timeout parameter is handled in api.py
    api_file = Path("src/llm_call/api.py")
    content = api_file.read_text()
    
    # Find the ask function and check if it handles timeout
    if "timeout" not in content:
        print("Adding timeout parameter to ask function...")
        lines = content.split('\n')
        
        # Find the ask function definition
        for i, line in enumerate(lines):
            if "async def ask(" in line:
                # Look for the kwargs line
                for j in range(i, min(i+20, len(lines))):
                    if "**kwargs" in lines[j]:
                        # Add timeout to kwargs description
                        lines.insert(j, '    timeout: Optional[float] = None,')
                        break
                break
        
        api_file.write_text('\n'.join(lines))
        print("✅ Added timeout parameter")

def fix_api_health():
    """Ensure API has proper health endpoint."""
    print("\n🔧 Fixing API health endpoint...")
    
    # Check if FastAPI app exists
    app_file = Path("src/llm_call/api_server.py")
    if not app_file.exists():
        app_file = Path("src/llm_call/core/api_server.py")
    
    if not app_file.exists():
        # Create a basic API server
        app_file = Path("src/llm_call/api_server.py")
        app_file.write_text('''"""
Module: api_server.py
Description: FastAPI server for LLM Call

External Dependencies:
- fastapi: https://fastapi.tiangolo.com/
- uvicorn: https://www.uvicorn.org/

Sample Input:
>>> GET /health

Expected Output:
>>> {"status": "healthy"}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import redis
from typing import Dict, Any

app = FastAPI(title="LLM Call API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    status = "healthy"
    services = {}
    
    # Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_timeout=1)
        r.ping()
        services["redis"] = "ok"
    except:
        services["redis"] = "unavailable"
        status = "degraded"
    
    return {
        "status": status,
        "services": services
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
''')
        print("✅ Created API server with health endpoint")

def fix_timeout_handling():
    """Fix timeout parameter handling in make_llm_request."""
    print("\n🔧 Fixing timeout handling...")
    
    # Check caller.py for timeout handling
    caller_file = Path("src/llm_call/core/caller.py")
    if caller_file.exists():
        content = caller_file.read_text()
        
        # Check if timeout is passed to litellm
        if "timeout" in content and "litellm.acompletion" in content:
            print("✅ Timeout already handled in caller.py")
        else:
            # Need to add timeout handling
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                if "litellm.acompletion(" in line or "litellm.completion(" in line:
                    # Check if we need to add timeout
                    bracket_count = 1
                    j = i + 1
                    while j < len(lines) and bracket_count > 0:
                        bracket_count += lines[j].count('(') - lines[j].count(')')
                        j += 1
                    
                    # Insert timeout parameter
                    if "timeout" not in content[lines[i]:lines[j]]:
                        lines.insert(j-1, '        timeout=config.get("timeout"),')
            
            caller_file.write_text('\n'.join(lines))
            print("✅ Added timeout handling to litellm calls")

def main():
    """Run all fixes."""
    print("🚀 Fixing remaining test failures...")
    
    diagnose_failures()
    fix_ask_function()
    fix_api_health()
    fix_timeout_handling()
    
    print("\n✅ Applied additional fixes! Re-run tests to check progress.")

if __name__ == "__main__":
    main()