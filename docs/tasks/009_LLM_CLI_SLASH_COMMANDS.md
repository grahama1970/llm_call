# Task 009: LLM CLI Slash Commands Implementation ⏳ Not Started

**Objective**: Implement a typer-based CLI with slash commands (like /ask, /chat, /model) that integrates with our existing litellm infrastructure, supports plugins, and enables seamless LLM interactions.

**Requirements**:
1. Slash commands usable in Claude Code and other environments
2. Plugin architecture for extensible commands
3. Stream support for real-time responses
4. Integration with existing litellm caller and router
5. Model configuration and switching
6. NO MOCKING - real validation only

## Overview

This task implements a Command Line Interface (CLI) for interacting with Large Language Models (LLMs) via our existing litellm infrastructure. The CLI will use `typer` for its structure and will support "slash commands" (e.g., `/ask`, `/chat`). Key features include a plugin system for extensibility, support for streaming responses, integration with our `src/llm_call/core/caller.py` and `src/llm_call/core/router.py`, and mechanisms for model configuration and switching. All development will be validated through real interactions with LLM APIs, adhering to the "NO MOCKING" requirement.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

The implementation leverages:
- **Typer**: For robust CLI structure with command parsing and context management
- **LiteLLM Integration**: Direct integration with our existing caller and router infrastructure
- **Plugin Architecture**: Dynamic command loading using Python's importlib
- **Streaming Support**: Real-time response display using litellm's stream capabilities
- **Model Management**: Persistent configuration for default model selection

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Typer CLI best practices 2025
   - Plugin architecture patterns for Python CLIs
   - Streaming output handling in terminal applications
   - LiteLLM integration patterns

2. **Use `WebSearch`** to find:
   - GitHub repositories with typer slash command implementations
   - Real-world CLI plugin systems
   - Streaming response handling examples
   - Model configuration management patterns

3. **Document all findings** in task reports:
   - Working code examples
   - Performance characteristics
   - Integration patterns
   - Best practices

4. **DO NOT proceed without research**:
   - Must find real typer examples
   - Must understand plugin loading patterns
   - Must locate streaming implementations
   - Must verify integration approaches

Example Research Queries:
```
perplexity_ask: "typer CLI slash commands implementation 2025"
WebSearch: "site:github.com typer plugin architecture dynamic loading"
perplexity_ask: "python CLI streaming response real-time display"
WebSearch: "site:github.com litellm CLI integration examples"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: CLI Foundation and Basic Structure ⏳ Not Started

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "typer slash command naming conventions"
- [ ] Use `WebSearch` for "site:github.com typer CLI structure examples"
- [ ] Search for "typer context object usage patterns"
- [ ] Find examples of typer apps with special command names

**Implementation Steps**:
- [ ] 1.1 Create CLI structure
  - Create `/src/llm_call/cli/main.py`
  - Create `/src/llm_call/cli/__init__.py`
  - Initialize typer.Typer() app
  - Set up proper module imports

- [ ] 1.2 Implement command parsing
  - Create central command dispatcher
  - Support slash-prefixed commands
  - Handle command arguments
  - Add context object for shared state

- [ ] 1.3 Test basic command
  - Implement `/hello` test command
  - Verify command execution
  - Test argument passing
  - Ensure proper error handling

**Technical Specifications**:
- Commands prefixed with `/`
- Typer context for state management
- Clean module structure
- Proper error messages

**Verification Method**:
```bash
# Test basic command
python -m src.llm_call.cli.main /hello "World"
# Should output: Hello World

# Test help
python -m src.llm_call.cli.main --help
# Should show available commands
```

**Acceptance Criteria**:
- CLI launches successfully
- Commands are recognized
- Arguments are parsed correctly
- Help text is clear
- No import errors

### Task 2: Core /ask Command with LiteLLM Integration ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "litellm completion function usage"
- [ ] Use `WebSearch` for "site:github.com litellm CLI examples"
- [ ] Find error handling patterns for API calls
- [ ] Research message formatting for litellm

**Implementation Steps**:
- [ ] 2.1 Create /ask command
  - Define command with typer decorator
  - Add prompt parameter
  - Add optional model parameter
  - Set default model

- [ ] 2.2 Integrate with caller.py
  - Import make_llm_request
  - Format messages properly
  - Handle configuration
  - Pass through our router

- [ ] 2.3 Implement error handling
  - Catch API errors
  - Handle network issues
  - Display user-friendly messages
  - Log errors appropriately

- [ ] 2.4 Test with real LLMs
  - Test with GPT models
  - Test with Claude via max/
  - Verify response formatting
  - Check error scenarios

**Technical Specifications**:
- Uses existing make_llm_request
- Supports all configured models
- Proper message formatting
- Comprehensive error handling

**Verification Method**:
```bash
# Test basic ask
python -m src.llm_call.cli.main /ask "What is Python?"

# Test with specific model
python -m src.llm_call.cli.main /ask "Explain typer" --model gpt-3.5-turbo

# Test Claude proxy
python -m src.llm_call.cli.main /ask "Hello" --model max/claude-3-haiku
```

**Acceptance Criteria**:
- Real LLM responses received
- All models work correctly
- Errors handled gracefully
- Integration with caller.py verified

### Task 3: Streaming Support Implementation ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "python CLI streaming output real-time"
- [ ] Use `WebSearch` for "site:github.com typer streaming responses"
- [ ] Find rich library live display examples
- [ ] Research async handling in typer

**Implementation Steps**:
- [ ] 3.1 Add streaming to /ask
  - Add --stream flag
  - Modify litellm call for streaming
  - Handle response chunks
  - Display incrementally

- [ ] 3.2 Implement /chat command
  - Create new command
  - Default to streaming
  - Support conversation context
  - Handle multi-turn (future)

- [ ] 3.3 Handle streaming display
  - Use flush=True for print
  - Consider rich for formatting
  - Handle interrupts gracefully
  - Show typing indicators

- [ ] 3.4 Test streaming behavior
  - Verify real-time display
  - Test long responses
  - Check interrupt handling
  - Measure performance

**Technical Specifications**:
- Real-time token display
- Graceful interrupt handling
- Optional rich formatting
- Performance optimized

**Verification Method**:
```bash
# Test streaming ask
python -m src.llm_call.cli.main /ask "Write a story" --stream

# Test non-streaming
python -m src.llm_call.cli.main /ask "Short answer" --no-stream

# Test chat streaming
python -m src.llm_call.cli.main /chat "Hello, how are you?"
```

**Acceptance Criteria**:
- Tokens appear in real-time
- No buffering issues
- Interrupts work properly
- Both modes functional

### Task 4: Model Management Commands ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "CLI configuration management best practices"
- [ ] Use `WebSearch` for "site:github.com python CLI model switching"
- [ ] Find config file format examples
- [ ] Research user preferences storage

**Implementation Steps**:
- [ ] 4.1 Create /model command group
  - Set up sub-commands structure
  - Implement list command
  - Implement set command
  - Implement current command

- [ ] 4.2 Add configuration storage
  - Choose config location (~/.llm_cli/)
  - Implement JSON/TOML storage
  - Handle missing config
  - Provide defaults

- [ ] 4.3 Integrate with commands
  - Read default from config
  - Allow per-command override
  - Update caller parameters
  - Persist selections

- [ ] 4.4 List available models
  - Query litellm for models
  - Show configured models
  - Display current default
  - Format output nicely

**Technical Specifications**:
- Persistent configuration
- Session-based overrides
- Clean config format
- User-friendly output

**Verification Method**:
```bash
# List models
python -m src.llm_call.cli.main /model list

# Set default
python -m src.llm_call.cli.main /model set gpt-4

# Check current
python -m src.llm_call.cli.main /model current

# Verify persistence
python -m src.llm_call.cli.main /ask "Test" # Should use new default
```

**Acceptance Criteria**:
- Models listed correctly
- Default persists across runs
- Override works per-command
- Config file created properly

### Task 5: Plugin Architecture Implementation ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "python plugin architecture patterns 2025"
- [ ] Use `WebSearch` for "site:github.com typer plugin system"
- [ ] Find importlib dynamic loading examples
- [ ] Research plugin interface design

**Implementation Steps**:
- [ ] 5.1 Design plugin interface
  - Define register_commands function
  - Create plugin base class
  - Document plugin API
  - Set plugin directory

- [ ] 5.2 Implement plugin discovery
  - Scan plugin directory
  - Use importlib for loading
  - Handle import errors
  - Validate plugin interface

- [ ] 5.3 Register plugin commands
  - Call registration function
  - Add to main app
  - Handle conflicts
  - Enable/disable plugins

- [ ] 5.4 Create example plugin
  - Implement sample command
  - Show best practices
  - Document structure
  - Test loading/unloading

**Technical Specifications**:
- Clean plugin API
- Safe dynamic loading
- Error isolation
- Hot reload support (future)

**Verification Method**:
```bash
# Create plugin
mkdir -p ~/.llm_cli/plugins
cat > ~/.llm_cli/plugins/hello_plugin.py << 'EOF'
import typer

def hello_world():
    print("Hello from plugin!")

def register_commands(app: typer.Typer):
    app.command("/hello-plugin")(hello_world)
EOF

# Test plugin
python -m src.llm_call.cli.main /hello-plugin
```

**Acceptance Criteria**:
- Plugins load automatically
- Commands register correctly
- Errors don't crash CLI
- Documentation clear

### Task 6: Final Integration and Verification ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 6.1 Review all reports
  - Check each task report
  - List incomplete features
  - Identify failures
  - Document issues

- [ ] 6.2 Create completion matrix
  - Build status table
  - Mark COMPLETE/INCOMPLETE
  - Calculate completion %
  - Identify blockers

- [ ] 6.3 Iterate on incomplete
  - Fix all issues
  - Re-run all tests
  - Update reports
  - NO PARTIAL COMPLETION

- [ ] 6.4 End-to-end testing
  - Test all commands
  - Verify all features
  - Check integrations
  - Measure performance

- [ ] 6.5 Create final report
  - Document all features
  - Show working examples
  - Include performance data
  - List any limitations

**Technical Specifications**:
- 100% feature completion
- All tests passing
- Full integration verified
- Production ready

**Verification Method**:
- Run full test suite
- Execute all commands
- Verify all integrations
- Check performance metrics

**Acceptance Criteria**:
- ALL features working
- ALL tests passing
- Documentation complete
- Ready for production use

## Usage Table

| Command | Description | Example |
|---------|-------------|---------|
| `/ask "<prompt>"` | Ask a single question | `python -m src.llm_call.cli.main /ask "What is Python?"` |
| `/ask "<prompt>" --model <model>` | Ask with specific model | `python -m src.llm_call.cli.main /ask "Explain AI" --model gpt-4` |
| `/ask "<prompt>" --stream` | Stream the response | `python -m src.llm_call.cli.main /ask "Tell a story" --stream` |
| `/chat "<message>"` | Start a chat conversation | `python -m src.llm_call.cli.main /chat "Hello!"` |
| `/model list` | List available models | `python -m src.llm_call.cli.main /model list` |
| `/model set <model>` | Set default model | `python -m src.llm_call.cli.main /model set gpt-4` |
| `/model current` | Show current model | `python -m src.llm_call.cli.main /model current` |
| `/<plugin-command>` | Run plugin command | `python -m src.llm_call.cli.main /translate "Hello"` |

## Version Control Plan

- **Initial Commit**: Create task-009-start tag
- **Feature Branches**: One per sub-task (feat/cli-foundation, feat/ask-command, etc.)
- **Commit Convention**: Conventional commits (feat:, fix:, docs:)
- **Integration**: Merge to main after verification
- **Final Tag**: Create task-009-complete after 100% done

## Resources

**Python Packages**:
- typer: CLI framework
- litellm: LLM integration (existing)
- rich: Terminal formatting (optional)
- importlib: Plugin loading

**Documentation**:
- [Typer Docs](https://typer.tiangolo.com/)
- [LiteLLM Docs](https://docs.litellm.ai/)
- [Rich Docs](https://rich.readthedocs.io/)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All commands working with real LLMs

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.