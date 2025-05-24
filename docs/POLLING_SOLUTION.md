# Polling Solution for Long-Running LLM Calls

## Overview

This solution implements a polling pattern based on the claude-code-mcp project to handle long-running LLM calls (especially Claude agent calls) without hitting timeouts.

## Architecture

### 1. **Background Execution**
- Tasks run in separate threads with their own event loops
- Non-blocking submission returns immediately with task_id
- Status tracked in SQLite database for persistence

### 2. **Components**

#### `polling_manager.py`
- Core polling infrastructure
- SQLite database for task persistence
- Background thread execution
- Status tracking and updates

#### `litellm_client_poc_polling.py`
- Enhanced LLM client with polling support
- Automatic detection of long-running calls
- Backward compatible with original API

#### `polling_server.py`
- FastAPI REST API server
- Endpoints for task submission, status, and control
- Health monitoring

## Usage Patterns

### 1. **Direct Python Usage**

```python
from llm_call.proof_of_concept.litellm_client_poc_polling import llm_call, get_task_status, wait_for_task

# Immediate mode (default) - waits for completion
response = await llm_call(config)

# Polling mode - returns immediately
response = await llm_call(config, polling_mode=True)
# Returns: {"task_id": "task_abc123", "status": "pending"}

# Check status
status = await get_task_status("task_abc123")

# Wait for completion
result = await wait_for_task("task_abc123", timeout=300)
```

### 2. **REST API Usage**

```bash
# Submit task
curl -X POST http://localhost:8000/v1/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "llm_config": {
      "model": "max/text-general",
      "messages": [{"role": "user", "content": "Hello"}]
    }
  }'

# Get status
curl http://localhost:8000/v1/tasks/{task_id}/status

# Wait for completion (long polling)
curl http://localhost:8000/v1/tasks/{task_id}/wait?timeout=300
```

## Key Features

### 1. **Automatic Long-Running Detection**
- Claude proxy calls (`max/*` models)
- Agent validation tasks
- Configurable timeout thresholds

### 2. **Database Persistence**
- SQLite storage for reliability
- Survives server restarts
- Automatic cleanup of old tasks

### 3. **Progress Tracking**
- Real-time progress updates
- Validation attempt counting
- Detailed error information

### 4. **Thread Safety**
- Connection pooling
- Transaction support
- Concurrent task execution

## Implementation Details

### Task States
- `pending` - Task submitted, not started
- `running` - Task executing
- `completed` - Successfully finished
- `failed` - Error occurred
- `timeout` - Exceeded time limit
- `cancelled` - User cancelled

### Database Schema
```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    llm_config TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    result TEXT,
    error TEXT,
    progress INTEGER DEFAULT 0,
    validation_attempts INTEGER DEFAULT 0,
    last_update TEXT
);
```

### Threading Model
- Main thread handles submission
- Background threads execute tasks
- Each thread has its own event loop
- No blocking of main application

## Performance Considerations

### 1. **Timeouts**
- Default: 300s for Claude, 60s for others
- Configurable per call
- Automatic timeout detection

### 2. **Polling Intervals**
- Client polls every 2-3 seconds
- Long polling support for efficiency
- Progress updates reduce perceived latency

### 3. **Resource Management**
- Thread pool limits
- Database connection pooling
- Automatic cleanup of completed tasks

## Testing

### Run Tests
```bash
# Test core polling functionality
python test_polling_functionality.py

# Test REST API server
python src/llm_call/proof_of_concept/polling_server.py

# Test client examples
python test_polling_client.py
```

### Test Coverage
- ✅ Simple synchronous calls
- ✅ Background task submission
- ✅ Status polling
- ✅ Long-running validation
- ✅ Task cancellation
- ✅ Parallel task execution

## Integration with V4 Core

This polling solution addresses the timeout issues identified during v4 POC testing:

1. **No More Timeouts** - Long-running calls execute in background
2. **Better UX** - Users can check progress instead of waiting
3. **Reliability** - Database persistence survives failures
4. **Scalability** - Supports multiple concurrent tasks

## Next Steps

1. Integrate polling into core retry.py
2. Add polling support to CLI
3. Implement progress callbacks for validators
4. Add metrics and monitoring
5. Create dashboard for task status

## Conclusion

The polling solution successfully handles long-running LLM calls without timeouts, providing a robust foundation for the v4 implementation. It follows proven patterns from the claude-code-mcp project while integrating seamlessly with the existing POC architecture.