# Task 009: LLM CLI Slash Commands Implementation (V2 - Auto-Generated) ⏳ Not Started

**Objective**: Implement auto-generated slash commands and MCP integration for our litellm-based CLI using the proven v2_typer_automated pattern. This approach provides zero-maintenance slash commands that automatically stay in sync with CLI changes.

**Requirements**:
1. Auto-generate slash commands from existing Typer CLI
2. Generate MCP server configuration for AI tool usage
3. Work with our existing litellm infrastructure
4. Support all existing CLI commands automatically
5. Enable use across ALL our projects
6. NO MOCKING - real validation only

## Overview

This task implements the v2_typer_automated approach discovered in our POC, which auto-generates Claude slash commands and MCP integration from any Typer CLI. This is a paradigm shift from building a slash command system to simply exposing our existing CLI through auto-generated interfaces.

**Key Innovation**: The Typer CLI becomes the single source of truth. All slash commands and MCP tools are auto-generated, eliminating dual maintenance and synchronization issues.

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs.
2. Task 5 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks until 100% completion.

## Research Summary

The v2_typer_automated POC demonstrates that we can:
- Add ~15 lines to any Typer CLI for slash command generation
- Auto-generate `.claude/commands/*.md` files for each command
- Create MCP server configuration automatically
- Eliminate all maintenance overhead
- Apply this pattern universally across projects

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Auto-generation patterns for CLI tools 2025
   - FastMCP integration best practices
   - Claude Code command file specifications
   - Cross-project Python utilities

2. **Use `WebSearch`** to find:
   - GitHub examples of CLI auto-generation
   - FastMCP server implementations
   - Typer introspection patterns
   - Python packaging for shared utilities

3. **Document all findings** in task reports

Example Research Queries:
```
perplexity_ask: "Python CLI command introspection auto-generation patterns 2025"
WebSearch: "site:github.com typer command metadata extraction"
perplexity_ask: "FastMCP server integration with existing CLI"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Add Auto-Generation to Existing CLI ⏳ Not Started

**Priority**: HIGH | **Complexity**: LOW | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "Typer command introspection best practices"
- [ ] Use `WebSearch` for "site:github.com claude code command specifications"
- [ ] Research optimal file structure for Claude commands
- [ ] Find examples of successful auto-generation patterns

**Implementation Steps**:
- [ ] 1.1 Create generation command
  - Add to `/src/llm_call/cli/main.py` (create if needed)
  - Implement `generate_claude()` command
  - Use the proven 15-line implementation
  - Skip self-referential commands

- [ ] 1.2 Implement command introspection
  - Extract command names and docstrings
  - Handle parameter documentation
  - Generate proper markdown format
  - Use `$ARGUMENTS` placeholder

- [ ] 1.3 Test with existing commands
  - Generate commands for any existing CLI
  - Verify `.claude/commands/` structure
  - Test command execution in Claude Code
  - Document any issues

**Technical Specifications**:
- Minimal code addition (~15 lines)
- Zero configuration required
- Works with any Typer CLI
- Preserves all documentation

**Verification Method**:
```bash
# Add generation to CLI
python -m src.llm_call.cli.main generate-claude

# Check generated files
ls -la .claude/commands/

# Test in Claude Code
# /project:ask "What is Python?"
```

**Acceptance Criteria**:
- Generation command works
- All CLI commands have .md files
- Commands execute properly
- Documentation preserved

### Task 2: MCP Server Integration ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` for "FastMCP server setup 2025"
- [ ] Use `WebSearch` for "site:github.com fastmcp typer integration"
- [ ] Research MCP protocol specifications
- [ ] Find production MCP server examples

**Implementation Steps**:
- [ ] 2.1 Add MCP generation command
  - Implement `generate_mcp_config()`
  - Extract parameter types from Typer
  - Build tool definitions
  - Generate JSON configuration

- [ ] 2.2 Add MCP server command
  - Implement `serve_mcp()`
  - Install fastmcp dependency
  - Register CLI commands as tools
  - Handle async/sync conversion

- [ ] 2.3 Test MCP functionality
  - Generate MCP configuration
  - Start MCP server
  - Test with MCP client
  - Verify tool execution

**Technical Specifications**:
- FastMCP integration
- Automatic type inference
- Async wrapper for sync commands
- Debug mode support

**Verification Method**:
```bash
# Install FastMCP
uv add fastmcp

# Generate config
python -m src.llm_call.cli.main generate-mcp-config

# Start server
python -m src.llm_call.cli.main serve-mcp --debug

# Test with MCP client
# Tools should be available
```

**Acceptance Criteria**:
- MCP config generates correctly
- Server starts successfully
- Tools are registered
- Commands execute via MCP

### Task 3: Integration with LiteLLM Commands ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: LOW | **Impact**: HIGH

**Research Requirements**:
- [ ] Review our existing CLI structure
- [ ] Identify litellm-specific commands
- [ ] Research parameter passing patterns
- [ ] Find complex command examples

**Implementation Steps**:
- [ ] 3.1 Create litellm CLI commands
  - Add `/ask` command to CLI
  - Add `/chat` command
  - Add `/model` management
  - Use existing caller.py

- [ ] 3.2 Generate slash commands
  - Run generate-claude
  - Verify litellm commands work
  - Test with real LLM calls
  - Check error handling

- [ ] 3.3 Test complex scenarios
  - Streaming responses
  - Model switching
  - Error cases
  - Performance validation

**Technical Specifications**:
- Direct integration with caller.py
- Support all model types
- Handle streaming (in CLI)
- Proper error messages

**Verification Method**:
```bash
# Test generated commands
/project:ask "Hello, world!"
/project:chat "Start a conversation"
/project:model list
/project:model set gpt-4
```

**Acceptance Criteria**:
- LiteLLM commands work
- Real LLM responses received
- Model switching functional
- Errors handled gracefully

### Task 4: Universal Module Creation ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: CRITICAL

**Research Requirements**:
- [ ] Use `perplexity_ask` for "Python decorators for CLI enhancement"
- [ ] Use `WebSearch` for "site:github.com python mixins typer"
- [ ] Research packaging patterns
- [ ] Find reusable CLI utilities

**Implementation Steps**:
- [ ] 4.1 Create reusable module
  - Create `/src/llm_call/cli/slash_mcp_mixin.py`
  - Implement as class mixin or decorators
  - Make it project-agnostic
  - Add configuration options

- [ ] 4.2 Simplify integration
  - One-line integration goal
  - Support for command filtering
  - Custom prefix support
  - Output directory control

- [ ] 4.3 Package for reuse
  - Create proper module structure
  - Add to our package imports
  - Write usage documentation
  - Create integration examples

- [ ] 4.4 Test across projects
  - Apply to different CLIs
  - Verify universal compatibility
  - Test edge cases
  - Document limitations

**Technical Specifications**:
- Maximum 1-line integration
- Work with any Typer app
- Configurable behavior
- Well-documented API

**Verification Method**:
```python
# One-line integration
from llm_call.cli.slash_mcp_mixin import add_slash_mcp_commands

app = typer.Typer()
add_slash_mcp_commands(app)  # That's it!

# Or as decorator
@add_slash_mcp_commands
app = typer.Typer()
```

**Acceptance Criteria**:
- Module works universally
- Single line integration
- All features available
- Clear documentation

### Task 5: Final Verification and Documentation ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 5.1 Review all implementations
  - Check each task report
  - Verify all features work
  - List any issues
  - Test in production

- [ ] 5.2 Create adoption guide
  - Write step-by-step guide
  - Include troubleshooting
  - Add best practices
  - Create video demo

- [ ] 5.3 Apply to all projects
  - List all our Typer CLIs
  - Add slash/MCP support
  - Verify each works
  - Document results

- [ ] 5.4 Create CI/CD automation
  - Auto-generate on changes
  - Include in build process
  - Version control commands
  - Deploy to team

- [ ] 5.5 Final report
  - Complete feature matrix
  - Performance metrics
  - Adoption statistics
  - Future improvements

**Technical Specifications**:
- 100% feature coverage
- All projects supported
- Full documentation
- Automated pipeline

**Verification Method**:
- Run full test suite
- Check all projects
- Review documentation
- Test CI/CD pipeline

**Acceptance Criteria**:
- ALL features working
- ALL projects integrated
- Documentation complete
- Team adoption successful

## Usage Table

| Command | Description | Example |
|---------|-------------|---------|
| `generate-claude` | Generate slash commands | `python cli.py generate-claude` |
| `generate-claude --prefix` | Generate with prefix | `python cli.py generate-claude --prefix myapp` |
| `generate-mcp-config` | Create MCP config | `python cli.py generate-mcp-config --port 6000` |
| `serve-mcp` | Start MCP server | `python cli.py serve-mcp --debug` |
| `/project:command` | Use generated command | `/project:ask "Hello"` |

## Version Control Plan

- **Initial Commit**: Create task-009-v2-start tag
- **Feature Branches**: feat/cli-autogen, feat/mcp-integration
- **Commit Convention**: Conventional commits
- **Integration**: Fast-track to main (low risk)
- **Final Tag**: Create task-009-v2-complete

## Resources

**Python Packages**:
- typer: Already in use
- fastmcp: MCP server framework
- pathlib: Built-in file handling

**Documentation**:
- [Typer Docs](https://typer.tiangolo.com/)
- [FastMCP Docs](https://github.com/fastmcp/fastmcp)
- [Claude Code Commands](https://claude.ai/docs/code-commands)

## Progress Tracking

- Start date: TBD
- Current phase: Planning
- Expected completion: 1-2 days (vs weeks for v1)
- Completion criteria: Universal slash/MCP support

## Key Advantages Over V1

1. **Time**: Hours vs weeks of development
2. **Maintenance**: Zero vs continuous synchronization
3. **Scope**: All projects vs single project
4. **Complexity**: ~50 lines vs thousands
5. **Risk**: Proven pattern vs new development

---

This task document reflects the paradigm shift from building infrastructure to leveraging auto-generation. Update status as tasks complete.