#!/usr/bin/env python3
"""Quick test to verify llm_call functionality"""

import sys
import asyncio
from pathlib import Path

# Add llm_call to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test imports
print("Testing imports...")
try:
    from llm_call import ask
    print("✓ Basic import works")
except Exception as e:
    print(f"✗ Basic import failed: {e}")
    
try:
    from llm_call.api import ask_sync, ChatSessionSync
    print("✓ API imports work")
except Exception as e:
    print(f"✗ API imports failed: {e}")

try:
    from llm_call.core.providers import get_available_providers
    print("✓ Provider imports work")
except Exception as e:
    print(f"✗ Provider imports failed: {e}")

try:
    from llm_call.core.validation import validate_llm_response
    print("✓ Validation imports work")
except Exception as e:
    print(f"✗ Validation imports failed: {e}")

# Test basic functionality
print("\nTesting basic functionality...")
try:
    result = ask_sync("Say 'OK' if you can hear me", model="gpt-3.5-turbo")
    if result and "OK" in result:
        print("✓ Basic ask_sync works")
    else:
        print(f"✗ Basic ask_sync returned unexpected: {result}")
except Exception as e:
    print(f"✗ Basic ask_sync failed: {e}")

# Test chat session
print("\nTesting chat session...")
try:
    session = ChatSessionSync()
    response = session.send("Say 'Hello' back to me")
    if response and "Hello" in response:
        print("✓ Chat session works")
    else:
        print(f"✗ Chat session returned unexpected: {response}")
except Exception as e:
    print(f"✗ Chat session failed: {e}")

# Test validation
print("\nTesting validation...")
try:
    from llm_call.api import register_validator
    
    def length_check(response: str) -> bool:
        return len(response) > 10
    
    register_validator("length_check", length_check)
    
    result = ask_sync(
        "Generate a paragraph about AI",
        model="gpt-3.5-turbo",
        validation_strategy="length_check"
    )
    if result and len(result) > 10:
        print("✓ Validation works")
    else:
        print(f"✗ Validation failed: {result}")
except Exception as e:
    print(f"✗ Validation failed: {e}")

# Test caching
print("\nTesting caching...")
try:
    import time
    start = time.time()
    r1 = ask_sync("What is 2+2?", model="gpt-3.5-turbo")
    t1 = time.time() - start
    
    start = time.time()
    r2 = ask_sync("What is 2+2?", model="gpt-3.5-turbo")
    t2 = time.time() - start
    
    if r1 == r2 and t2 < t1 * 0.5:
        print(f"✓ Caching works (first: {t1:.2f}s, cached: {t2:.2f}s)")
    else:
        print(f"✗ Caching may not be working (first: {t1:.2f}s, second: {t2:.2f}s)")
except Exception as e:
    print(f"✗ Caching test failed: {e}")

print("\nDone!")