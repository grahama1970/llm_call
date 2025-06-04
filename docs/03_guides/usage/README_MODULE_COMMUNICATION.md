# Claude CLI Module-to-Module Communication

This is a solution to the problem of module-to-module communication using the Claude CLI. It enables different modules (like Marker and ArangoDB) to communicate with each other by running Claude in their respective directories and having it act as an intermediary.

## Problem Statement

We needed to implement a solution for module-to-module communication where:

1. Module A (e.g., Marker) can ask questions to Module B (e.g., ArangoDB)
2. Module B responds to those questions using Claude CLI
3. The conversation is tracked and stored for future reference
4. Responses are streamed in real-time with status updates

## Solution Overview

The solution has been implemented in several files:

1. `simplified_popen_claude.py`: A complete solution that implements module-to-module communication
2. `direct_claude_command.py`: A simplified approach to running Claude in specific directories
3. `debug_claudev3.py`: A debugging tool to identify and fix issues with Claude CLI execution
4. `SOLUTION_SUMMARY.md`: A detailed explanation of the problem and solution

## Key Features

- **Directory-Specific Claude Execution**: Runs Claude CLI in the context of different module directories
- **Streaming Responses**: Processes and streams Claude's output in real-time
- **Conversation Storage**: Saves conversations in a database (in-memory or SQLite)
- **Error Handling**: Comprehensive error handling for Claude CLI issues
- **Caching**: LRU cache with TTL for system prompts

## How It Works

The core technique is to run Claude CLI in a directory using the shell CD command:

```python
cmd_str = f'cd {working_dir} && claude --system-prompt "..." -p "..." --output-format stream-json --verbose'
```

This ensures that Claude CLI has access to the files in the target directory, which is crucial for module-specific context.

## Usage

### Basic Usage

```python
from simplified_popen_claude import marker_ask_arangodb_pdf_format

result = marker_ask_arangodb_pdf_format(
    marker_dir="/path/to/marker",
    arangodb_dir="/path/to/arangodb"
)

print(f"Communication successful: {result['success']}")
print(f"Thread ID: {result['thread_id']}")
```

### Command Line Usage

```bash
python simplified_popen_claude.py --marker-dir /path/to/marker --arangodb-dir /path/to/arangodb --verbose
```

### Debugging

If you encounter issues, use the debug script:

```bash
python debug_claudev3.py --basic  # Test basic Claude CLI functionality
python debug_claudev3.py --dir    # Test Claude in specific directory
python debug_claudev3.py --shell  # Test shell command with CD
```

## Files

1. `simplified_popen_claude.py`: Main implementation
2. `direct_claude_command.py`: Direct Claude CLI execution
3. `debug_claudev3.py`: Debugging tool for Claude CLI issues
4. `SOLUTION_SUMMARY.md`: Detailed explanation of the solution

## Example Output

The solution produces a structured conversation in the following format:

```json
{
  "success": true,
  "thread_id": "thread_0",
  "question_msg_id": "msg_0",
  "response_msg_id": "msg_1",
  "final_status": "complete",
  "conversation": {
    "id": "thread_0",
    "title": "Marker-ArangoDB PDF Structure Requirements",
    "modules": ["marker", "arangodb"],
    "messages": [
      {
        "id": "msg_0",
        "module_name": "marker",
        "content": "What exact JSON structure do you require...",
        "message_type": "question",
        "status": "complete"
      },
      {
        "id": "msg_1",
        "module_name": "arangodb",
        "content": "Here is the JSON schema for PDF data...",
        "message_type": "response",
        "status": "complete"
      }
    ]
  }
}
```

## Requirements

- Python 3.7+
- Claude CLI (version 0.2.124+)
- Required Python packages: loguru, pathlib

## Future Improvements

- Asynchronous execution for better performance
- Integration with more external databases
- More robust error recovery
- Unit tests for all components