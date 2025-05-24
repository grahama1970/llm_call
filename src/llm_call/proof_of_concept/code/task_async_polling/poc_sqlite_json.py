#!/usr/bin/env python3
"""POC 4: Test SQLite JSON serialization"""

import sqlite3
import json
from dataclasses import dataclass
import time

print("POC 4: SQLite JSON Serialization Test")

# Create test database
conn = sqlite3.connect(":memory:")
conn.execute("""
    CREATE TABLE tasks (
        task_id TEXT PRIMARY KEY,
        result TEXT
    )
""")

# Test 1: Simple dict
print("\nTest 1: Simple dict")
simple_dict = {"message": "Hello world", "status": "ok"}
try:
    conn.execute("INSERT INTO tasks VALUES (?, ?)", ("task1", json.dumps(simple_dict)))
    print("✅ Simple dict serialized successfully")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 2: Complex nested structure (like LiteLLM response)
print("\nTest 2: Complex nested structure")
complex_dict = {
    "id": "chatcmpl-123",
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "Hello!"
        },
        "index": 0
    }],
    "usage": {"total_tokens": 10}
}
try:
    conn.execute("INSERT INTO tasks VALUES (?, ?)", ("task2", json.dumps(complex_dict)))
    print("✅ Complex dict serialized successfully")
    
    # Read it back
    cursor = conn.execute("SELECT result FROM tasks WHERE task_id = ?", ("task2",))
    stored_json = cursor.fetchone()[0]
    restored = json.loads(stored_json)
    print(f"✅ Restored content: {restored['choices'][0]['message']['content']}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 3: Object with __dict__
print("\nTest 3: Object with __dict__")
@dataclass
class MockResponse:
    id: str
    choices: list
    
obj = MockResponse("test-123", [{"message": {"content": "Test"}}])
try:
    # Convert using __dict__
    obj_dict = obj.__dict__
    conn.execute("INSERT INTO tasks VALUES (?, ?)", ("task3", json.dumps(obj_dict)))
    print("✅ Object serialized via __dict__")
except Exception as e:
    print(f"❌ Failed: {e}")

conn.close()
print("\nDone!")
