#!/usr/bin/env python3
"""POC: Basic SQLite functionality test"""

import sqlite3
import json
import uuid
from datetime import datetime

print("=== POC: SQLite Basic Functionality ===")

# Test 1: Create database and table
print("\nTest 1: Database creation")
db_path = "test_poc.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create tasks table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        status TEXT NOT NULL,
        llm_config TEXT NOT NULL,
        created_at REAL NOT NULL,
        started_at REAL,
        completed_at REAL,
        result TEXT,
        error TEXT,
        progress TEXT
    )
''')
conn.commit()
print("✓ Table created successfully")

# Test 2: Insert a task
print("\nTest 2: Insert task")
task_id = str(uuid.uuid4())
llm_config = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}]}

cursor.execute(
    '''INSERT INTO tasks 
    (task_id, status, llm_config, created_at, started_at, completed_at, result, error, progress)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
    (
        task_id,
        "pending",
        json.dumps(llm_config),
        datetime.now().timestamp(),
        None,
        None,
        None,
        None,
        None
    )
)
conn.commit()
print(f"✓ Inserted task: {task_id}")

# Test 3: Retrieve task
print("\nTest 3: Retrieve task")
cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
row = cursor.fetchone()
if row:
    print(f"✓ Retrieved task: {row[0]}, status: {row[1]}")
    print(f"  Config: {json.loads(row[2])}")
else:
    print("✗ Failed to retrieve task")

# Test 4: Update task with result
print("\nTest 4: Update task with result")
result = {"choices": [{"message": {"content": "Hello! How can I help you?"}}]}
cursor.execute(
    "UPDATE tasks SET status = ?, completed_at = ?, result = ? WHERE task_id = ?",
    ("completed", datetime.now().timestamp(), json.dumps(result), task_id)
)
conn.commit()
print("✓ Updated task status to completed")

# Test 5: Verify update
cursor.execute("SELECT status, result FROM tasks WHERE task_id = ?", (task_id,))
row = cursor.fetchone()
if row and row[0] == "completed":
    result_data = json.loads(row[1])
    print(f"✓ Task completed with result: {result_data['choices'][0]['message']['content']}")
else:
    print("✗ Update verification failed")

# Cleanup
conn.close()
import os
os.remove(db_path)
print("\n✓ All SQLite basic tests passed!")
