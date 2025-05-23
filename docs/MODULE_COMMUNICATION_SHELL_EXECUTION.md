# Module-to-Module Communication Using Claude CLI Shell Execution

This document outlines the working approach for enabling module-to-module communication using Claude CLI with proper directory context.

## Problem Statement

When modules need to communicate with each other using the Claude CLI:
- Each module needs to execute Claude CLI in its own directory context
- Module files need to be accessible during Claude CLI execution
- System prompts need to reflect the module's capabilities and context
- Output should be streamed and stored in a conversation database

## Solution: Shell=True with CD Command

The key solution is to use `subprocess.Popen` with `shell=True` and include a `cd` command to change to the target module's directory.

### Working Code Examples

#### 1. Basic Execution Pattern

```python
def run_claude_in_module_directory(working_dir, prompt, system_prompt, timeout=30):
    # Escape quotes for shell safety
    escaped_system_prompt = system_prompt.replace('"', '\\"')
    escaped_prompt = prompt.replace('"', '\\"')
    
    # Build shell command with cd
    cmd_str = f'cd {working_dir} && timeout {timeout}s claude --system-prompt "{escaped_system_prompt}" -p "{escaped_prompt}" --output-format stream-json --verbose'
    
    # Execute with shell=True
    proc = subprocess.Popen(
        cmd_str,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True  # Critical for cd command to work
    )
    
    # Process output...
    return proc
```

#### 2. JSON Streaming and Parsing

Claude CLI can output in several JSON formats which need to be handled correctly:

```python
content_chunks = []
for line in proc.stdout:
    line = line.strip()
    if not line or not line.startswith("{"):
        continue
        
    try:
        obj = json.loads(line)
        
        # Handle different JSON formats
        if "content" in obj:
            # Handle direct content field (older format)
            content_chunks.append(obj["content"])
        elif "type" in obj and obj.get("type") == "assistant" and "message" in obj:
            # Handle Claude CLI message format
            message = obj.get("message", {})
            if "content" in message and isinstance(message["content"], list):
                for content_item in message["content"]:
                    if content_item.get("type") == "text" and "text" in content_item:
                        content_chunks.append(content_item["text"])
        elif "type" in obj and obj.get("type") == "result" and "result" in obj:
            # Handle the result field in the final summary
            result_content = obj.get("result")
            if result_content and isinstance(result_content, str):
                content_chunks.append(result_content)
    except json.JSONDecodeError:
        continue
```

#### 3. Complete Module Communication Function

```python
def module_ask_module(questioner_dir, responder_dir, question, timeout=30):
    # Create conversation thread
    thread_id = conversation_store.create_thread(
        title=f"{questioner_dir.name}-{responder_dir.name} Communication",
        modules=[questioner_dir.name, responder_dir.name]
    )
    
    # Store question
    question_msg_id = conversation_store.add_message(
        thread_id=thread_id,
        module_name=questioner_dir.name,
        content=question
    )
    
    # Get responder's system prompt
    responder_system_prompt = f"""
    You are the {responder_dir.name} module, responsible for [description].
    Provide specific information requested by the {questioner_dir.name} module.
    """
    
    # Get response with streaming
    success, response_msg_id, content = stream_and_store_claude_response(
        working_dir=str(responder_dir),
        thread_id=thread_id,
        module_name=responder_dir.name,
        prompt=question,
        system_prompt=responder_system_prompt,
        timeout=timeout
    )
    
    return {
        "success": success,
        "thread_id": thread_id,
        "content": content,
        "conversation": conversation_store.get_thread(thread_id)
    }
```

## Verified Working Approach

1. **Use shell=True with cd command**
   - `cd {module_directory} && claude ...` with `shell=True` places Claude in the correct directory context

2. **Properly escape quotes in prompts and system prompts**
   - `system_prompt.replace('"', '\\"')` prevents shell injection issues

3. **Set timeouts to prevent hanging**
   - `timeout {seconds}s claude ...` ensures the command doesn't run indefinitely

4. **Handle multiple JSON output formats**
   - Parse and extract content from different Claude CLI output formats
   - Handle regular content, message format, and result format

5. **Track message status in conversation store**
   - Store initial "processing" status
   - Update with streamed content as it arrives
   - Mark "complete" when done or "failed" on error

## Terminal Command Testing

This approach was verified with the following terminal command:

```bash
cd /path/to/module_directory && claude --system-prompt "System prompt..." \
-p "User prompt..." --output-format stream-json --verbose | tee output.json
```

## Important Considerations

1. **Quote Escaping**: Always escape quotes in system prompts and user prompts
2. **Error Handling**: Capture and process stderr output
3. **Timeout Management**: Set appropriate timeouts to prevent hanging processes
4. **JSON Parsing**: Handle all Claude CLI output formats
5. **Content Deduplication**: Avoid duplicate content from different JSON sources

## Non-Working Approaches (Avoid These)

1. ❌ Using `cwd` parameter without shell=True
   ```python
   # DON'T DO THIS - doesn't properly set context for Claude CLI
   subprocess.Popen(
       ["claude", "--system-prompt", system_prompt, "-p", prompt],
       cwd=working_dir
   )
   ```

2. ❌ Using command list with shell=True
   ```python
   # DON'T DO THIS - shell=True with list doesn't properly handle cd
   subprocess.Popen(
       ["cd", working_dir, "&&", "claude", "--system-prompt", system_prompt],
       shell=True
   )
   ```

## Conclusion

The shell=True approach with cd commands is the most reliable way to execute Claude CLI in the context of different module directories, ensuring proper access to module files and maintaining appropriate context for inter-module communication.