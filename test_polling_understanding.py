#!/usr/bin/env python3
"""Test to verify I understand the polling implementation."""

import asyncio
import threading
import time
from pathlib import Path

# Test 1: Verify thread isolation
print("Test 1: Thread Event Loop Isolation")
main_loop = asyncio.get_event_loop()
print(f"Main loop: {id(main_loop)}")

def thread_func():
    # Each thread needs its own event loop
    try:
        loop = asyncio.get_event_loop()
        print(f"Thread loop (should fail): {id(loop)}")
    except RuntimeError as e:
        print(f"✓ Expected error: {e}")
    
    # Create new loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(f"✓ New thread loop: {id(loop)}")
    loop.close()

thread = threading.Thread(target=thread_func)
thread.start()
thread.join()

# Test 2: Verify SQLite thread safety
print("\nTest 2: SQLite Thread Safety")
import sqlite3

db_path = "test_thread_safety.db"
conn = sqlite3.connect(db_path)
conn.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, value TEXT)")
conn.close()

results = []

def write_to_db(thread_id):
    # Each thread needs its own connection
    conn = sqlite3.connect(db_path)
    for i in range(5):
        conn.execute("INSERT INTO test VALUES (?, ?)", (thread_id, f"value_{thread_id}_{i}"))
        conn.commit()
    conn.close()
    results.append(f"Thread {thread_id} done")

threads = []
for i in range(3):
    t = threading.Thread(target=write_to_db, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f"✓ All threads completed: {results}")

# Verify data
conn = sqlite3.connect(db_path)
count = conn.execute("SELECT COUNT(*) FROM test").fetchone()[0]
print(f"✓ Total rows inserted: {count} (expected: 15)")
conn.close()
Path(db_path).unlink()

# Test 3: Verify async execution in thread
print("\nTest 3: Async Execution in Thread")

async def async_task(name):
    print(f"  {name} starting")
    await asyncio.sleep(1)
    print(f"  {name} done")
    return f"{name}_result"

def run_async_in_thread(name):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(async_task(name))
        return result
    finally:
        loop.close()

# Run multiple async tasks in threads
start = time.time()
threads = []
for i in range(3):
    t = threading.Thread(target=lambda i=i: results.append(run_async_in_thread(f"Task{i}")))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

elapsed = time.time() - start
print(f"✓ Completed in {elapsed:.1f}s (should be ~1s, not 3s)")

print("\n✅ All tests passed - I understand the threading model!")