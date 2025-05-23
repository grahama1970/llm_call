# Claude Streaming Module Query

This document explains how to use the Claude streaming implementation for module-to-module communication, following the pattern established in the `popen_claudev2.py` example.

## Overview

The Claude streaming implementation allows modules to communicate with each other through Claude, with real-time status updates stored in a SQLite database. This enables:

- Asynchronous communication between modules
- Real-time progress tracking
- Status transitions (processing → complete/failed)
- Storage of all conversations in a central database

## Status Lifecycle

Messages go through these status transitions:
1. `processing` - Initial state when query is running
2. `complete` - Final state for successful queries
3. `failed` - Final state for failed queries

## Usage Example

Here's how to use the implementation:

```python
from claude_comms.core.claude_streamer import stream_and_store_claude_response
from claude_comms.core.conversation_store_factory import ConversationStoreFactory

# Create or get a conversation store
store = ConversationStoreFactory.create(store_type="sqlite")

# Create a thread for the conversation
thread_id = store.create_thread(
    title="Module Communication Example",
    modules=["module_a", "module_b"],
    metadata={"purpose": "data ingestion"}
)

# Stream Claude response
msg_id = stream_and_store_claude_response(
    working_dir="/path/to/module/directory",
    thread_id=thread_id,
    module_name="module_b",
    prompt="What format should module_a use to send data?",
    system_prompt="You are module_b, responsible for explaining data formats."
)

# Monitor status in another process
def monitor_status(thread_id, msg_id):
    # Create a new store instance for thread safety
    store = ConversationStoreFactory.create(store_type="sqlite")
    
    # Get the thread
    thread = store.get_thread(thread_id)
    
    # Find the message
    for msg in thread["messages"]:
        if msg["message_id"] == msg_id:
            print(f"Status: {msg['status']}")
            print(f"Content: {msg['content']}")
            break
```

## Implementation Details

The core implementation follows these steps:

1. **Initial Status Setting**: Insert a message with status "processing" at the start
2. **Command Execution**: Run Claude with stream-json output format
3. **Content Updates**: Process streaming output and update message content in real-time
4. **Status Finalization**: Set status to "complete" or "failed" at the end

## SQLite Schema

The implementation relies on a SQLite database with a `messages` table that includes a `status` field:

```sql
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    thread_id TEXT NOT NULL,
    module TEXT NOT NULL,
    content TEXT NOT NULL,
    type TEXT NOT NULL,
    timestamp REAL NOT NULL,
    status TEXT DEFAULT "complete",
    metadata TEXT,
    FOREIGN KEY (thread_id) REFERENCES threads (thread_id) ON DELETE CASCADE
)
```

## Testing

To test the implementation without the actual Claude executable, set the `CLAUDE_MOCK_TEST` environment variable:

```python
import os
os.environ["CLAUDE_MOCK_TEST"] = "1"
```

This will simulate Claude's output for testing purposes.