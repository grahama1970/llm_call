# Claude Comms Polling Daemon

The Polling Daemon is a background service that monitors module-to-module communication messages in the Claude Comms system. It provides real-time status tracking, notifications, and a CLI interface for monitoring and managing message processing.

## Features

- **Background Monitoring**: Run the daemon in the background to track message status
- **Real-time Updates**: Get notified when message status changes
- **Thread Safety**: Safe concurrent operation with thread-local SQLite connections
- **Resource Management**: Efficient connection pooling and cleanup
- **CLI Interface**: Comprehensive command-line interface for monitoring and control

## Usage

### Starting and Stopping the Daemon

```bash
# Start the polling daemon
claude-comms poll start

# Start with custom configuration
claude-comms poll start --interval 5.0 --max-messages 2000

# Check daemon status
claude-comms poll status

# Stop the daemon
claude-comms poll stop
```

### Monitoring Messages

```bash
# List all active messages
claude-comms poll list

# Filter by status
claude-comms poll list --status active
claude-comms poll list --status completed

# Show detailed information for a specific message
claude-comms poll show <message-id>

# Add a message to monitor manually
claude-comms poll add --task-id <task-id> --source <module> --target <module>

# Remove a message from monitoring
claude-comms poll remove <message-id>
```

### Programmatic Usage

```python
from claude_comms.background.polling_daemon import get_polling_daemon

# Get the daemon and start it
daemon = get_polling_daemon()
daemon.start()

# Monitor a message
daemon.add_message(
    thread_id="thread-id",
    message_id="message-id",
    source_module="source",
    target_module="target",
    on_complete=lambda msg_id, response: print(f"Message {msg_id} completed!")
)

# Check active messages
active_messages = daemon.get_active_messages()

# Get information about a specific message
message_info = daemon.get_message("message-id")

# Stop the daemon
daemon.shutdown()
```

### Using the Core Polling API

```python
from claude_comms.core.polling import poll_message_until_complete

# Poll a message until it completes
result = poll_message_until_complete(
    thread_id="thread-id",
    message_id="message-id",
    timeout=60,
    print_progress=True
)

# Access the result
print(f"Message status: {result['status']}")
print(f"Content: {result['content']}")
```

## Integration with Module Communication

The polling system integrates with the module communication system:

```python
from claude_comms.core.module_communication import module_ask_module

# Send a query and wait for completion
result = module_ask_module(
    questioner_dir="/path/to/questioner",
    responder_dir="/path/to/responder",
    prompt="What is the meaning of life?",
    wait_for_completion=True  # This uses polling under the hood
)

# The result will contain the completed response
print(result["content"])
```

## Architecture

The polling system is built around three key components:

1. **Core Polling System** (`src/claude_comms/core/polling.py`):
   - `MessageStatus`: Enum for message status (PENDING, PROCESSING, COMPLETE, etc.)
   - `StatusTracker`: Tracks status changes for a specific message
   - `MessagePoller`: Polls for status updates at configurable intervals
   - `MessageMonitor`: Manages multiple polling operations

2. **Connection Pool** (`src/claude_comms/core/connection_pool.py`):
   - Provides thread-safe access to SQLite database connections
   - Uses thread-local storage to isolate connections
   - Handles cleanup of idle connections

3. **Polling Daemon** (`src/claude_comms/core/polling_daemon.py` or `src/claude_comms/background/polling_daemon.py`):
   - Runs as a singleton in a background thread
   - Manages message registration and monitoring
   - Provides callback mechanism for status changes
   - Handles proper shutdown and resource cleanup

4. **CLI Integration** (`src/claude_comms/cli/poll_commands.py`):
   - Commands for daemon management
   - Tools for message monitoring

## Thread Safety Considerations

The polling system is designed to be thread-safe:

- Each thread gets its own SQLite connection via thread-local storage
- Locks protect access to shared resources
- The daemon runs in its own background thread
- Weak references prevent memory leaks
- Proper cleanup is performed during shutdown

## Performance Tuning

You can adjust these parameters for optimal performance:

- **Poll Interval**: Control how frequently messages are checked
  ```bash
  claude-comms poll start --interval 2.0
  ```

- **Maximum Messages**: Limit the number of messages tracked at once
  ```bash
  claude-comms poll start --max-messages 2000
  ```

- **Message Timeout**: Set how long to track messages before expiring them
  ```python
  daemon.add_message(thread_id="id", message_id="id", timeout=3600)  # 1 hour
  ```

## Examples

### Example 1: Basic CLI Usage

```bash
# Start the daemon
claude-comms poll start

# Send a query using module_ask_module in another terminal
# ...

# List active messages
claude-comms poll list

# Monitor a specific message
claude-comms poll show <message-id>

# Stop the daemon when done
claude-comms poll stop
```

### Example 2: Programmatic Monitoring with Callbacks

```python
from claude_comms.background.polling_daemon import get_polling_daemon

# Define callback functions
def on_complete(message_id, response):
    print(f"Message {message_id} completed!")
    print(f"Response: {response[:100]}...")

def on_fail(message_id, error):
    print(f"Message {message_id} failed: {error}")

# Start monitoring
daemon = get_polling_daemon()
daemon.start()

# Register a message with callbacks
daemon.add_message(
    thread_id="thread-id",
    message_id="message-id",
    on_complete=on_complete,
    on_fail=on_fail
)

# Do other work while message is being processed...
# The callbacks will be called when the message status changes
```

## Troubleshooting

### Common Issues

- **Database Locked**: If you see SQLite "database is locked" errors, ensure you're using the connection pool for thread-safe access.
- **Daemon Not Starting**: Check if another instance is already running with `claude-comms poll status`.
- **Message Not Being Tracked**: Verify the thread_id and message_id match what's in the database.
- **High CPU Usage**: Try increasing the poll interval to reduce CPU load.

### Debugging

- Enable detailed logging: `export LOGURU_LEVEL=DEBUG`
- Check daemon status: `claude-comms poll status --json`
- Force stop if stuck: Kill the Python process running the daemon

## Conclusion

The Polling Daemon provides a robust way to monitor and track message processing in the Claude Comms system. It offers both programmatic and CLI interfaces for managing message status tracking, with thread-safe operation and efficient resource usage.