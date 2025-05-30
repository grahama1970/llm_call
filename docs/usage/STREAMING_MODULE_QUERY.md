# Streaming Module Query Implementation

This document describes the implementation of the streaming module query system, 
which follows the pattern established in the `popen_claudev2.py` example.

## Overview

The streaming module query system allows modules to communicate with each other via Claude Code,
with real-time status updates stored in a shared SQLite database. This enables:

- Asynchronous communication between modules
- Real-time progress tracking and monitoring
- Status transitions (processing → complete/failed)
- Central storage of all conversations with advanced search capabilities

## Implementation Pattern

The implementation follows these key steps:

1. **Initial Status Setting**: Insert a message with status "processing" at the start
2. **Claude Command Construction**: Build Claude CLI command with streaming JSON output
3. **Process Launching**: Use `subprocess.Popen` to start Claude and capture output stream
4. **Real-time Updates**: Process stream output and update message content incrementally
5. **Status Finalization**: Set status to "complete" or "failed" at the end of processing

## Key Functions

### `stream_and_store_claude_response`

This is the core function that handles streaming Claude Code output and updating the
conversation store. It follows the exact pattern from `popen_claudev2.py`:

```python
def stream_and_store_claude_response(
    working_dir: str,
    thread_id: str,
    prompt: str,
    module_name: str = "module",
    system_prompt: Optional[str] = None,
    callback: Optional[Callable[[str], None]] = None
) -> Dict[str, Any]:
    # Insert initial message with status "processing"
    msg_id = conversation_store.add_message(
        thread_id=thread_id,
        module_name=module_name,
        content="",  # Initially empty
        message_type="response",
        status="processing"
    )
    
    # Build Claude command with streaming output
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
    
    # Stream and update content
    for line in proc.stdout:
        # Process JSON output
        # Update message in database with current content
    
    # At the end, set status to "complete"
    conversation_store.update_message(
        msg_id,
        content=full_content,
        status="complete"
    )
```

### `query_module`

A high-level wrapper function that:
1. Creates a thread if none is provided
2. Stores the prompt as a message
3. Calls `stream_and_store_claude_response` to execute the query

## Status Transitions

Messages go through these status transitions:
- `processing`: Initial state when query is running
- `complete`: Final state for successful queries
- `failed`: Final state for failed queries

## Database Schema Considerations

The database schema includes a `status` field in the `messages` table:

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

## Monitoring Progress

Other processes or modules can monitor the progress by querying the database:

```python
# Get all processing messages
processing_messages = conversation_store.get_processing_messages()

# Check status of a specific message
thread = conversation_store.get_thread(thread_id)
for message in thread["messages"]:
    if message["message_id"] == message_id:
        status = message["status"]
        # Do something based on status
```

## Thread Safety

When monitoring in separate threads, it's important to create new store instances
to avoid SQLite thread conflicts:

```python
def monitor_thread():
    # Create new store instance for this thread
    local_store = ConversationStoreFactory.create(store_type="sqlite")
    # Use local_store for operations
```

## Example Usage

```python
from claude_comms.core.streaming_module_query import query_module

# Run a query
result = query_module(
    prompt="Analyze this codebase and explain its architecture",
    module_path="/path/to/module",
    module_name="SomeModule",
    callback=lambda chunk: print(chunk, end="")
)

# Get IDs for monitoring
thread_id = result["thread_id"]
message_id = result["message_id"]

# Check status later
store = ConversationStoreFactory.create(store_type="sqlite")
thread = store.get_thread(thread_id)
for message in thread["messages"]:
    if message["message_id"] == message_id:
        print(f"Status: {message['status']}")
```