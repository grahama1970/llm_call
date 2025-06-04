# Task 001: Claude MCP Integration for Module Communication 🔄 In Progress

**Objective**: Implement a background Claude instance architecture for module-to-module communication using the claude-code-mcp framework, with module descriptors to enable contextual translation between components.

**Requirements**:
1. Create module descriptor system to define module capabilities and relationships
2. Implement background Claude instance management using claude-code-mcp
3. Develop communication context generation for cross-module queries
4. Create a simplified API for module-to-module communication
5. Support persistence of conversations between modules
6. Enable proper translation between module contexts

## Overview

The claude-comms package needs to function as a true translation layer between different modules in the system. Currently, it lacks the context of what each module does and the relationship between modules, making it difficult to facilitate meaningful communication. Additionally, using the CLI for each query is inefficient and lacks persistence.

This task will transform claude-comms into a true translation layer by integrating with the claude-code-mcp project for background Claude instances and implementing a module descriptor system that provides context about who is asking questions and who is answering them.

**CRITICAL LANGUAGE CHALLENGE**: The claude-comms project is built in Python, while the claude-code-mcp project is primarily JavaScript/Node.js. This cross-language integration presents significant challenges that must be addressed:

1. We must either:
   - Create a Python wrapper around the JavaScript API
   - Use HTTP/REST API communication to the claude-code-mcp service
   - Implement a new Python version of the core claude-code-mcp functionality
   - Use subprocess calls to the Node.js application with proper IPC

2. Additional complexity:
   - Serialization/deserialization between languages
   - Process management across language boundaries
   - Error handling across different runtime environments
   - Ensuring compatible versioning and dependencies

**IMPORTANT**: 
1. Each sub-task MUST include creation of a verification report in `/docs/reports/` with actual command outputs and performance results.
2. Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion is achieved - no partial completion is acceptable.

## Research Summary

Background Claude instances provide significant performance and context benefits, while a structured module descriptor system enables proper communication context. The claude-code-mcp project provides an existing framework for managing background Claude instances that can be leveraged.

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH task, the agent MUST:

1. **Use `perplexity_ask`** to research:
   - Current best practices (2025-current) for large language model management
   - Production patterns for stateful LLM services
   - Context management techniques for LLMs
   - Module descriptor patterns in distributed systems

2. **Use `WebSearch`** to find:
   - GitHub repositories with LLM integration code
   - Real production examples of module communication
   - Descriptor-based communication systems
   - Context management in multi-agent systems

3. **Document all findings** in task reports:
   - Links to source repositories
   - Code snippets that work
   - Performance characteristics
   - Integration patterns

4. **DO NOT proceed without research**:
   - No theoretical implementations
   - No guessing at patterns
   - Must have real code examples
   - Must verify current best practices

Example Research Queries:
```
perplexity_ask: "background LLM instance management python 2025"
WebSearch: "site:github.com module communication descriptor pattern python"
perplexity_ask: "claude API background process management best practices 2025"
WebSearch: "site:github.com agent communication context management python"
```

## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Module Descriptor System ✅ Completed

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [x] Use `perplexity_ask` to research module descriptor patterns
- [x] Use `WebSearch` to find real-world module descriptor implementations
- [x] Research context management in multi-agent systems
- [x] Identify best practices for module capability descriptions
- [x] Find examples of descriptor-based communication

**Implementation Steps**:
- [x] 1.1 Create module descriptor infrastructure
  - Create `/claude_comms/descriptors/` directory
  - Create `__init__.py` files
  - Implement `ModuleDescriptor` class
  - Add serialization and deserialization methods
  - Add validation for descriptor fields

- [x] 1.2 Implement base descriptors
  - Create `BaseDescriptor` abstract class
  - Implement core descriptor fields
  - Add capability tagging system
  - Create prompt generation methods
  - Implement descriptor registry

- [x] 1.3 Create standard module descriptors
  - Implement Marker module descriptor
  - Implement ArangoDB module descriptor
  - Implement ClaudeMCP module descriptor
  - Add extensibility for custom descriptors
  - Create helper functions for descriptor creation
  - Document descriptor schema

- [x] 1.4 Add descriptor loading from files
  - Support YAML descriptor format
  - Support JSON descriptor format
  - Implement directory scanning for descriptors
  - Add validation on load
  - Create descriptor update methods

- [x] 1.5 Create verification report
  - Create `/docs/reports/001_task_1_module_descriptors.md`
  - Document implementation details
  - Show descriptor examples
  - Include prompt generation samples
  - Document API usage examples

- [x] 1.6 Git commit feature

**Technical Specifications**:
- Support for capability and data type tagging
- JSON and YAML serialization
- Validation of descriptor fields
- Context-aware prompt generation
- Registry for descriptor management

**Verification Method**:
- Create test descriptors
- Generate and validate prompts
- Test serialization and deserialization
- Verify descriptor loading from files
- Check registry functionality

**Acceptance Criteria**:
- Module descriptors properly define module capabilities
- Descriptors can be serialized and deserialized
- Prompt generation creates useful context
- Registry correctly manages descriptors
- Documentation is complete

### Task 2: Background Claude Instance Integration ✅ Completed

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Research Requirements**:
- [x] CRITICAL: Thoroughly analyze the existing claude-code-mcp code at `/home/graham/workspace/experiments/claude-code-mcp/` to understand:
  - Its architectural design (JavaScript/Node.js based)
  - How background Claude tasks are launched
  - Command-line interface and parameters
  - Output tracking and capture mechanisms
  - Process management approach
  - API endpoints and protocols (especially any REST interfaces)
  - Error handling and recovery patterns
  - Authentication and security mechanisms
  - WebSocket or other real-time communication protocols
  - Dependency structure and version requirements
- [x] Use `perplexity_ask` to research background process management
- [x] Use `WebSearch` to find claude-code-mcp API examples
- [x] Research persistent LLM instance patterns
- [x] Find best practices for IPC with background processes
- [x] Research conversation persistence with Claude

**Implementation Steps**:
- [x] 2.1 Create cross-language integration approach
  - Evaluate and select the most appropriate integration method:
    * HTTP/REST API client to Node.js service
    * Python wrapper using subprocess to Node.js
    * WebSocket client for real-time communication
    * Implementation of core functionality in Python
  - Document the tradeoffs of each approach
  - Create proof-of-concept for the selected approach
  - Test cross-language serialization/deserialization
  - Benchmark performance across language boundary
  - Document language boundary challenges and solutions

- [x] 2.2 Create background instance manager
  - Create `/claude_comms/background/` directory
  - Implement `InstanceManager` class based on claude-code-mcp patterns but in Python
  - Add instance lifecycle management (start, stop, pause, resume)
  - Create instance configuration (memory limits, timeouts, etc.)
  - Add error handling and recovery
  - Document exactly how output is captured from background processes
  - Handle cross-language error scenarios

- [x] 2.3 Implement claude-code-mcp integration
  - Create connection to MCP API (likely REST or WebSocket)
  - Implement cross-language authentication if required
  - Add support for instance creation from Python to JavaScript service
  - Implement JSON-based query mechanism
  - Add conversation persistence with compatible serialization
  - Create instance cleanup that works across language boundary
  - Implement robust error handling for cross-language failures

- [x] 2.4 Add instance pooling
  - Implement instance pool compatible with JavaScript service architecture
  - Add multi-module instance management
  - Create instance affinity for module pairs
  - Implement instance reclamation with proper cross-language cleanup
  - Add performance monitoring
  - Implement reconnection logic for service disruptions
  - Create process monitoring across language boundary

- [x] 2.5 Implement conversation management
  - Add conversation persistence using JSON-compatible format
  - Create conversation retrieval across language boundary
  - Implement threading support that works with JavaScript service
  - Add conversation search compatible with both languages
  - Create conversation archiving
  - Ensure conversation state can be transferred between languages
  - Implement data validation for cross-language objects

- [x] 2.6 Create verification report
  - Create `/docs/reports/001_task_2_background_instance.md`
  - Document cross-language integration approach with justification
  - Document instance performance metrics
  - Show instance lifecycle examples
  - Include conversation management examples
  - Document API usage patterns
  - Create language boundary diagram showing data flow
  - Include serialization/deserialization examples
  - Document error handling across language boundary
  - Include performance comparison of language integration approaches

- [x] 2.6 Git commit feature

**Technical Specifications**:
- Cross-language integration with JavaScript/Node.js claude-code-mcp
- JSON-compatible data structures for language interoperability
- Support for multiple concurrent instances
- Instance lifecycle management (create, pause, resume, terminate)
- Connection with claude-code-mcp API (likely REST or WebSocket)
- Persistent conversations for module pairs
- Error recovery and retry mechanisms
- Robust handling of cross-language failures
- Serialization/deserialization of complex data types
- Compatible authentication mechanisms

**Verification Method**:
- Demonstrate successful cross-language integration with JavaScript claude-code-mcp
- Test and benchmark JSON serialization/deserialization performance
- Start and manage background instances using the Python interface to JavaScript service
- Test instance persistence across calls with concrete metrics
- Measure performance improvements (response time, memory usage, etc.)
- Measure performance overhead of cross-language communication
- Test conversation continuity with multi-turn exchanges
- Verify memory management and resource utilization across language boundary
- Document exact commands used and their outputs
- Demonstrate output tracking from background processes
- Test error handling across language boundary
- Verify reconnection after service disruption

**Acceptance Criteria**:
- Successful cross-language integration with the JavaScript claude-code-mcp
- Cross-language communication overhead is less than 100ms per transaction
- JSON serialization correctly handles all required data types
- Background instances successfully manage Claude using the Python interface to JavaScript service
- Instances persist between API calls with verifiable state maintenance
- Conversations maintain context across multiple interactions and language boundaries
- Performance meets targets (specify response time improvements)
- Error handling works correctly and recovers from common failure modes, including cross-language failures
- Output tracking captures all Claude responses reliably across the language boundary
- Resource usage is optimized and properly managed
- Service disruptions are properly detected and handled
- Reconnection logic works reliably after JavaScript service restarts

### Task 3: Communication Context Generator ✅ Completed

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [x] Use `perplexity_ask` to research LLM context setting patterns
- [x] Use `WebSearch` to find cross-module communication examples
- [x] Research optimal prompt structures for Claude
- [x] Find best practices for context compression
- [x] Identify effective role-based prompting

**Implementation Steps**:
- [x] 3.1 Create context generator infrastructure
  - Create `/claude_comms/context/` directory
  - Implement `ContextGenerator` class
  - Add modular context components
  - Create context template system
  - Implement context validation

- [x] 3.2 Implement module-to-module context builder
  - Create source module context
  - Implement target module context
  - Add communication protocol definitions
  - Create context merging logic
  - Implement context optimization

- [x] 3.3 Add specialized context templates
  - Create query context template
  - Implement response context template
  - Add error handling context
  - Create follow-up query contexts
  - Implement multi-turn conversation context

- [x] 3.4 Create context customization API
  - Add custom context parameters
  - Implement context overrides
  - Create context extension points
  - Add context inheritance
  - Implement context versioning

- [x] 3.5 Create verification report
  - Create `/docs/reports/001_task_3_context_generator.md`
  - Document context generation examples
  - Show context templates
  - Include generated prompts
  - Document API usage patterns

- [x] 3.6 Git commit feature

**Technical Specifications**:
- Context generation for source and target modules
- Module capability-aware context building
- Support for conversation history
- Context template customization
- Performance optimization for context size

**Verification Method**:
- Generate contexts for different module pairs
- Test context with background instances
- Verify context effectiveness in communication
- Check context optimization
- Test context customization

**Acceptance Criteria**:
- Contexts properly define module roles
- Contexts include module capabilities
- Generated prompts facilitate good communication
- Context customization works correctly
- Contexts optimize for token usage

### Task 4: Enhanced Communication API ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] Use `perplexity_ask` to research module communication patterns
- [ ] Use `WebSearch` to find API design patterns for LLM interactions
- [ ] Research best practices for conversation management
- [ ] Find examples of stateful LLM communication
- [ ] Research error handling in distributed systems

**Implementation Steps**:
- [ ] 4.1 Create enhanced communicator API
  - Update `ModuleCommunicator` class
  - Integrate with background instance manager
  - Add descriptor-aware communication
  - Create context-based messaging
  - Implement conversation persistence

- [ ] 4.2 Implement advanced query capabilities
  - Add streaming response support
  - Implement multi-turn conversations
  - Create query templates
  - Add query parameter validation
  - Implement query history

- [ ] 4.3 Add communication utilities
  - Create module discovery
  - Implement communication diagnostics
  - Add performance monitoring
  - Create communication logging
  - Implement retry policies

- [ ] 4.4 Implement session management
  - Add communication sessions
  - Create session persistence
  - Implement session recovery
  - Add session timeout management
  - Create session cleanup

- [ ] 4.5 Create verification report
  - Create `/docs/reports/001_task_4_enhanced_api.md`
  - Document API usage examples
  - Show multi-turn conversation examples
  - Include performance metrics
  - Document error handling scenarios

- [ ] 4.6 Git commit feature

**Technical Specifications**:
- Simple, intuitive API for module communication
- Support for streaming responses
- Session management for long-running conversations
- Efficient error handling and recovery
- Performance monitoring and logging

**Verification Method**:
- Test API with various module combinations
- Verify streaming response handling
- Test multi-turn conversations
- Check session persistence
- Measure API performance

**Acceptance Criteria**:
- API simplifies module communication
- Streaming responses work correctly
- Sessions maintain state across calls
- Error handling is robust
- Documentation is clear and complete

### Task 5: CLI for Background Claude Instances ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Research Requirements**:
- [ ] CRITICAL: Analyze the claude-code-mcp CLI to understand its command structure
- [ ] Understand how claude-code-mcp CLI invokes background instances
- [ ] Identify the CLI parameters used for background mode
- [ ] Determine how the CLI tracks and displays output from background processes
- [ ] Use `perplexity_ask` to research CLI design patterns
- [ ] Use `WebSearch` to find module integration examples
- [ ] Research best practices for CLI usability
- [ ] Find examples of LLM integration tutorials
- [ ] Research documentation patterns for APIs

**Implementation Steps**:
- [ ] 5.1 Design CLI architecture for background instances
  - Create command structure for managing background Claude instances
  - Define parameters for initializing, controlling, and monitoring instances
  - Design output tracking and display mechanism
  - Create CLI state persistence for tracking background processes
  - Design cross-language communication for CLI
  - Document CLI architecture with diagrams

- [ ] 5.2 Implement core CLI functionality
  - Create `claude-comms start-instance` command
  - Implement `claude-comms list-instances` command
  - Add `claude-comms stop-instance` command
  - Create `claude-comms query-instance` command
  - Implement `claude-comms monitor-instance` command
  - Add status indicators for background processes
  - Create real-time output streaming from background Claude
  - Implement instance health checks

- [ ] 5.3 Create module communication CLI
  - Implement `claude-comms register-module` command for module descriptors
  - Add `claude-comms query-module` command (with background mode)
  - Create `claude-comms listen-module` command for ongoing communication
  - Implement `claude-comms list-conversations` command
  - Add `claude-comms continue-conversation` command
  - Create `claude-comms export-conversation` command
  - Implement terminal UI for real-time monitoring

- [ ] 5.4 Create integration examples
  - Implement Marker to ArangoDB example using background instances
  - Create module discovery example with descriptor system
  - Add multi-turn conversation example with background Claude
  - Implement streaming response example with real-time output
  - Create custom context example with module descriptors
  - Add background process management examples

- [ ] 5.5 Update documentation
  - Create user guide for background instance management
  - Update README with background command examples
  - Add API documentation for background instance interfaces
  - Create tutorial files for module-to-module communication
  - Update module descriptions
  - Add troubleshooting guide for background instances
  - Create examples of output tracking and display
  - Document cross-language communication details

- [ ] 5.6 Implement CLI usage tests
  - Create test script for background instance management
  - Implement streaming output test from background Claude
  - Add background session management test
  - Create error handling and recovery test
  - Implement performance benchmark comparing CLI vs. background
  - Test cross-language communication from CLI
  - Create long-running background task tests
  - Add output tracking verification test

- [ ] 5.7 Create verification report
  - Create `/docs/reports/001_task_5_background_cli.md`
  - Document background instance CLI usage examples
  - Show real-time output tracking with screenshots/logs
  - Include benchmark results comparing CLI vs background mode
  - Document background instance management commands
  - Include examples of long-running conversation tracking
  - Show error recovery in action
  - Provide cross-language communication examples
  - Document usability improvements over standard CLI

- [ ] 5.6 Git commit feature

**Technical Specifications**:
- Background instance management through CLI
- Real-time output streaming from background processes
- Process status monitoring and health checks
- Cross-language communication from CLI to JavaScript service
- Intuitive CLI commands for background instance control
- Well-documented API examples for background management
- Complete integration examples using background instances
- Performance benchmarks comparing CLI vs background mode
- Terminal UI for monitoring background instances
- Comprehensive documentation for background processes

**Verification Method**:
- Test background instance management CLI commands
- Verify real-time output streaming functionality
- Check background instance monitoring capabilities
- Test long-running background tasks
- Validate background instance error recovery
- Measure performance improvements with background mode
- Test cross-language communication from CLI
- Verify instance persistence across CLI sessions
- Check documentation completeness for background features
- Validate integration examples with background instances
- Test usability with different background scenarios

**Acceptance Criteria**:
- CLI provides complete background instance management functionality
- Background instances can be started, monitored, and stopped via CLI
- Real-time output streaming from background instances works reliably
- Cross-language communication from CLI to JavaScript service is stable
- Background instance monitoring provides accurate status information
- Long-running background tasks maintain state correctly
- Error recovery mechanisms work for background instances
- Examples demonstrate background instance capabilities
- Documentation clearly explains background instance management
- Integration examples with background instances work as expected
- Benchmarks show significant performance improvements with background mode
- Terminal UI provides useful monitoring of background processes

### Task 6: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 6.1 Review all task reports
  - Read all reports in `/docs/reports/001_task_*`
  - Create checklist of incomplete features
  - Identify failed tests or missing functionality
  - Document specific issues preventing completion
  - Prioritize fixes by impact

- [ ] 6.2 Create task completion matrix
  - Build comprehensive status table
  - Mark each sub-task as COMPLETE/INCOMPLETE
  - List specific failures for incomplete tasks
  - Identify blocking dependencies
  - Calculate overall completion percentage

- [ ] 6.3 Iterate on incomplete tasks
  - Return to first incomplete task
  - Fix identified issues
  - Re-run validation tests
  - Update verification report
  - Continue until task passes

- [ ] 6.4 Re-validate completed tasks
  - Ensure no regressions from fixes
  - Run integration tests
  - Verify cross-task compatibility
  - Update affected reports
  - Document any new limitations

- [ ] 6.5 Final comprehensive validation
  - Run full integration test
  - Execute performance benchmarks
  - Test all API functions
  - Verify documentation accuracy
  - Confirm all features work together

- [ ] 6.6 Create final summary report
  - Create `/docs/reports/001_final_summary.md`
  - Include completion matrix
  - Document all working features
  - List any remaining limitations
  - Provide usage recommendations

- [ ] 6.7 Mark task complete only if ALL sub-tasks pass
  - Verify 100% task completion
  - Confirm all reports show success
  - Ensure no critical issues remain
  - Get final approval
  - Update task status to ✅ Complete

**Technical Specifications**:
- Zero tolerance for incomplete features
- Mandatory iteration until completion
- All tests must pass
- All reports must verify success
- No theoretical completions allowed

**Verification Method**:
- Task completion matrix showing 100%
- All reports confirming success
- Rich table with final status

**Acceptance Criteria**:
- ALL tasks marked COMPLETE
- ALL verification reports show success
- ALL tests pass without issues
- ALL features work in production
- NO incomplete functionality

**CRITICAL ITERATION REQUIREMENT**:
This task CANNOT be marked complete until ALL previous tasks are verified as COMPLETE with passing tests and working functionality. The agent MUST continue iterating on incomplete tasks until 100% completion is achieved.

## Usage Table

| Command / Function | Description | Example Usage | Expected Output |
|-------------------|-------------|---------------|-----------------|
| **Background Instance Commands** | | | |
| `claude-comms start-instance` | Start background Claude instance | `claude-comms start-instance --name marker_arangodb` | Instance ID and status |
| `claude-comms list-instances` | List running instances | `claude-comms list-instances` | Table of active instances |
| `claude-comms stop-instance` | Stop background instance | `claude-comms stop-instance --id abc123` | Confirmation message |
| `claude-comms monitor-instance` | Show real-time output | `claude-comms monitor-instance --id abc123` | Live output stream |
| **Module Communication** | | | |
| `create_communicator` | Create module communicator | `comm = create_communicator("marker", marker_path, use_background=True)` | ModuleCommunicator instance |
| `send_message` | Send message to another module | `result = comm.send_message(target="arangodb", prompt="...")` | Response dictionary |
| `create_conversation` | Start a new conversation | `thread_id = comm.create_conversation("arangodb")` | Thread ID string |
| `list_conversations` | List active conversations | `convs = comm.list_conversations()` | List of conversation objects |
| **CLI Module Commands** | | | |
| `claude-comms register-module` | Register module descriptor | `claude-comms register-module marker --path /path/to/marker --desc module.yaml` | Confirmation message |
| `claude-comms query-module` | Query module (background) | `claude-comms query-module arangodb "..." --background` | Background job ID |
| `claude-comms listen-module` | Listen for module responses | `claude-comms listen-module --module arangodb` | Real-time updates |
| `claude-comms export-conversation` | Export conversation | `claude-comms export-conversation --id abc123 --format json` | Saved conversation file |

## Version Control Plan

- **Initial Commit**: Create task-001-start tag before implementation
- **Feature Commits**: After each major feature
- **Integration Commits**: After component integration  
- **Test Commits**: After test suite completion
- **Final Tag**: Create task-001-complete after all tests pass

## Resources

**Python Packages**:
- pydantic: Data validation for descriptors
- loguru: Logging
- typer: CLI functionality
- requests: HTTP client for MCP API
- websockets: For WebSocket communication if needed
- fastapi: For potential REST API implementation
- httpx: Modern HTTP client with async support

**JavaScript/Node.js Resources**:
- claude-code-mcp: Background Claude instance management (JavaScript)
- express: Node.js web framework for APIs
- ws: WebSocket library for Node.js
- axios: HTTP client for Node.js

**Documentation**:
- [Claude API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Claude Code MCP Repository](https://github.com/example/claude-code-mcp)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Typer Documentation](https://typer.tiangolo.com/)

## Progress Tracking

- Start date: 2025-05-20
- Current phase: Planning
- Expected completion: TBD
- Completion criteria: All features working, tests passing, documented

## Report Documentation Requirements

Each sub-task MUST have a corresponding verification report in `/docs/reports/` following these requirements:

### Report Structure:
Each report must include:
1. **Task Summary**: Brief description of what was implemented
2. **Research Findings**: Links to repos, code examples found, best practices discovered
3. **Claude-Code-MCP Analysis**: Detailed analysis of the relevant parts of the claude-code-mcp codebase
4. **Non-Mocked Results**: Real command outputs and performance metrics
5. **Performance Metrics**: Actual benchmarks with real data
   - Response time comparisons (background vs CLI)
   - Memory usage statistics
   - Throughput metrics for different query types
6. **Output Tracking Evidence**: Demonstration of how output is captured from background processes
7. **Code Examples**: Working code with verified output
8. **Verification Evidence**: Logs or metrics proving functionality
9. **Limitations Found**: Any discovered issues or constraints
10. **External Resources Used**: All GitHub repos, articles, and examples referenced

### Report Naming Convention:
`/docs/reports/001_task_[SUBTASK]_[feature_name].md`

---

This task document serves as the comprehensive implementation guide. Update status emojis and checkboxes as tasks are completed to maintain progress tracking.