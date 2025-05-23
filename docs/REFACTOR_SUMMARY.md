# Refactoring Summary: Streaming Module Query

This document summarizes the refactoring of the streaming module query implementation to more closely align with the pattern established in the `popen_claudev2.py` example.

## Key Changes

1. **Streamlined Implementation**: Created a focused `stream_and_store_claude_response` function that follows the exact pattern from the example, ensuring consistent behavior.

2. **Status Transitions**: Properly tracks message status through the three states:
   - "processing" - Initial state when query is running
   - "complete" - Final state for successful queries
   - "failed" - Final state for failed queries

3. **Command Arguments**: Use the exact Claude command-line arguments shown in the example:
   ```
   claude -p <prompt> --output-format stream-json --verbose
   ```

4. **Real-time Updates**: Implemented incremental content updates during streaming, allowing other processes to monitor progress.

5. **Claude Executable Handling**: Added robust Claude executable discovery and error handling to address potential path issues.

6. **Error Handling**: Improved error trapping and reporting for all steps of the process.

7. **Testing**: Created a simple test script that verifies the implementation using a mock Claude executable.

## Implementation Details

The refactored implementation focuses on these key aspects:

### 1. Initial Status Setting

```python
# Insert an initial message with status "processing"
msg_id = conversation_store.add_message(
    thread_id=thread_id,
    module_name=module_name,
    content="",  # Initially empty
    message_type="response",
    status="processing",
    metadata={
        "query_id": query_id,
        "source": "claude_code",
        "started_at": time.time()
    }
)
```

### 2. Streaming Content Updates

```python
# Process streaming output
for line in proc.stdout:
    try:
        obj = json.loads(line)
        if "content" in obj:
            # Append to chunks
            content_chunks.append(obj["content"])
            
            # Update content in DB for real-time progress
            conversation_store.update_message(
                msg_id,
                content="".join(content_chunks),
                status="processing"
            )
    except Exception:
        continue
```

### 3. Final Status Update

```python
# At the end, set status to "complete"
full_content = "".join(content_chunks)

# Update the message with complete status
conversation_store.update_message(
    msg_id,
    content=final_content,
    status="complete",
    metadata={
        "query_id": query_id,
        "timestamp": time.time()
    }
)
```

## Testing Approach

We created both a comprehensive test (`test_streaming_module_query.py`) and a simple test (`test_simple_streaming.py`) to verify the implementation. The tests:

1. Create a mock Claude script that simulates streaming output
2. Run the query using our refactored implementation
3. Monitor status transitions from "processing" to "complete"
4. Verify the final content is properly stored in the database

## Key Differences from Previous Implementation

1. **Simplified Function**: More focused implementation with clearer responsibilities
2. **Empty Initial Content**: Starts with empty content instead of "Processing..."
3. **Standard Command Format**: Uses exact command format from the example
4. **Error Handling**: More robust error handling and reporting
5. **Status Terminology**: Uses "complete" instead of "completed" for consistency
6. **Robust Claude Executable Handling**: Added discovery mechanism

## Usage Example

```python
from claude_comms.core.streaming_module_query import query_module

# Run a query
result = query_module(
    prompt="Please analyze this module and explain its purpose",
    module_path="/path/to/module/directory",
    module_name="SomeModule"
)

# Access results
thread_id = result["thread_id"]
message_id = result["message_id"]
status = result["status"]  # Will be "complete" or "error"
```

## Next Steps

1. **Integration**: Integrate the refactored implementation across the codebase, replacing the old streaming query implementation.

2. **Documentation**: Update all relevant documentation to reference the new implementation.

3. **Additional Tests**: Create more comprehensive tests for edge cases (network errors, timeouts, etc.).

4. **Performance Benchmarking**: Compare the performance of the new implementation against the old one.

5. **User Interface**: Consider adding a simple CLI or web interface to monitor streaming queries in real-time.

6. **Breaking Changes**: Note any breaking changes in the API and update dependent code accordingly.

7. **MongoDB Support**: Consider adding MongoDB as an alternative to SQLite for larger deployments.

8. **Metrics Collection**: Add metrics collection for query duration, content size, etc.

9. **Message Finalization**: Add hooks for message finalization to trigger downstream processes when a message transitions to "complete" or "failed".

10. **Async Implementation**: Consider adding an async/await version of the implementation for use in async applications.