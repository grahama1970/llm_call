# Streaming Claude Responses with Status Tracking

This document explains how the claude-comms system implements streaming responses with
real-time status tracking using SQLite.

## How It Works

1. **Initial Request with "processing" Status**
   - When a query is sent to Claude, a message is immediately added to the SQLite database with status="processing"
   - This allows other components to discover and monitor the query in real-time

2. **Streaming Response Updates**
   - Claude's response is streamed using the `--output-format stream-json` option
   - For each chunk of output, the message content in the database is updated
   - The status remains "processing" during streaming

3. **Completion Status**
   - When Claude completes the response, the message is updated with status="completed"
   - If any error occurs, the status is set to "failed" with error details

4. **Monitoring and Orchestration**
   - Other components can poll the database to check message status
   - This enables coordination between multiple Claude instances
   - The SQLite FTS5 index allows fast searching across all messages

## Code Implementation

The streaming functionality is implemented in the following files:

1. `src/claude_comms/core/streaming_query.py`: Core streaming implementation
2. `src/claude_comms/core/sqlite_conversation_store.py`: SQLite database with status field
3. `test_processing_status.py`: Demonstration of monitoring process

## Example Usage

```python
from claude_comms.core.streaming_query import query_module_streaming
from claude_comms.core.conversation_store_factory import ConversationStoreFactory

# Define a callback for streaming chunks (optional)
def on_chunk(chunk, current_content):
    print(f"Received chunk: {chunk[:50]}...")

# Send a query that will be tracked in the database
result = query_module_streaming(
    prompt="What format do you require for PDF data ingestion?",
    module_path="/path/to/module",
    module_name="ModuleName",
    callback=on_chunk  # Optional streaming callback
)

# Get the thread and message IDs for monitoring
thread_id = result["thread_id"]
message_id = result["message_id"]

# In another process or component, monitor the message status
store = ConversationStoreFactory.create(store_type="sqlite")
message = store.get_thread(thread_id)["messages"][-1]
print(f"Message status: {message['status']}")
```

## Monitor Processing Messages

You can get all currently processing messages with:

```python
store = ConversationStoreFactory.create(store_type="sqlite")
processing_messages = store.get_processing_messages()
```

This allows you to build dashboards or monitoring tools for long-running queries.

## Error Handling

If a query fails or times out, the message status is set to "failed" with error details
in the metadata. This provides robust error handling for distributed systems.

## Conclusion

This streaming implementation enables real-time progress tracking and response monitoring
for Claude, making it suitable for orchestration across multiple modules in a distributed
system. The use of SQLite with a status field allows any component to check query progress
without requiring direct API communication.