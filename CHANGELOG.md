# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - 2025-05-31

#### Multi-Model Conversational Collaboration
- **Conversation State Persistence** - Major feature addition enabling fluid multi-model collaboration
  - Implemented SQLite-based conversation manager (`src/llm_call/core/conversation_manager.py`)
  - Tracks conversations across multiple model calls with full context preservation
  - Support for ArangoDB as alternative storage backend
  - Conversation search, retrieval, and history management
  
- **Conversational Delegator Tool** (`src/llm_call/tools/conversational_delegator.py`)
  - CLI tool for starting and continuing multi-model conversations
  - Maintains conversation state between Claude, Gemini, GPT-4, etc.
  - Supports viewing conversation history
  - Enables true iterative model collaboration
  
- **MCP Conversational Tools** (`src/llm_call/mcp_conversational_tools.py`)
  - Tool definitions for Claude Desktop/Code integration
  - Functions: start_collaboration, delegate_to_model, continue_conversation
  - Conversation summary and context-aware analysis tools

### Changed - 2025-05-31

- **README.md** - Complete rewrite for LLM agent clarity
  - Now explicitly identifies as a SPOKE module for claude-module-communicator HUB
  - Clear API documentation for orchestrator integration
  - Detailed examples of multi-model collaboration workflows
  - Current configuration status with working models
  - Integration points clearly documented

### Documentation - 2025-05-31

- Created `docs/reports/ACTUAL_FUNCTIONALITY_STATUS.md`
  - Clarifies "verified" vs "actually working" functionality
  - Shows what works with current API keys
  - Explains fluid collaboration capabilities
- Created `docs/reports/claude_capabilities_comprehensive_verification_report.md`
  - Detailed verification of all three requested capabilities
  - Skeptical analysis as requested
- Updated file structure documentation to reflect new components

### Added - 2025-05-23

#### POC Retry Manager Implementation
- Implemented sophisticated retry mechanism for LLM calls with staged escalation
- Added `poc_retry_manager.py` with the following features:
  - Configurable retry attempts with exponential backoff
  - Tool suggestion after N attempts (via `max_attempts_before_tool_use`)
  - Human escalation after M attempts (via `max_attempts_before_human`)
  - Dynamic MCP configuration injection for tool usage
  - Support for complex validation strategies including agent-based validators
  - Proper handling of various response formats (dict, ModelResponse, string)
- Added `PoCHumanReviewNeededError` exception for human review escalation
- Added `PoCRetryConfig` dataclass for retry configuration
- Integrated retry manager with `litellm_client_poc.py`
- Added real-world tests in `tests/proof_of_concept/test_poc_retry_real.py`

### Fixed
- Fixed import naming issue (renamed to `PoCHumanReviewNeededError`)
- Resolved duplicate `messages` argument error in retry function call
- Fixed indentation and syntax errors in `litellm_client_poc.py`

### Dependencies
- Added `wikipedia` package via `uv add wikipedia` for POC test cases

### Testing
- Created comprehensive real-world tests using actual LLM calls (no mocks)
- All tests use `initialize_litellm_cache()` as required
- Tests validate:
  - Basic retry with validation feedback
  - JSON validation with multiple validators
  - Human escalation at configured thresholds
### Fixed (Additional) - 2025-05-23
- Fixed missing return statement in litellm_client_poc.py that caused llm_call to return None
- Fixed human escalation test to properly check for dictionary response instead of expecting exception
- Verified all POC retry features work with real LLM calls (no mocks)

### Fixed - 2025-05-23

#### Core and CLI Module Verification
- Fixed router.py bug where 'provider' key was being passed to OpenAI API
  - Added  to remove utility keys
  - Verified fix resolves BadRequestError from litellm
- Created comprehensive verification scripts to test all core and CLI modules
  -  - Initial verification attempt
  -  - Updated with correct function/class names
  -  - Final version with all fixes and improvements
- Identified and documented module structure:
  - 54 Python files in core/ directory
  - 4 Python files in cli/ directory
  - 92% success rate on module verification tests

### Added - 2025-05-23

#### Verification Infrastructure
- Created verification summary report documenting all findings
- Added task documentation in 
- Implemented module verification system with:
  - Import verification for all modules
  - Attribute checking for expected functions/classes
  - Functional testing with real LLM calls
  - POC retry manager verification
  - Comprehensive file coverage analysis

### Known Issues
- LLM call test returns empty response (async handling investigation needed)
- ValidationResult test uses wrong attribute name (is_valid vs valid)
- POC Retry Manager import name mismatch in test

### Documentation
- Created  with complete findings
- Updated task tracking in 
- Documented all untested modules for future work


### Fixed - 2025-05-23

#### Core and CLI Module Verification
- Fixed router.py bug where provider key was being passed to OpenAI API
  - Added api_params.pop(provider, None) to remove utility keys
  - Verified fix resolves BadRequestError from litellm
- Created comprehensive verification scripts to test all core and CLI modules
  - comprehensive_verification.py - Initial verification attempt
  - comprehensive_verification_v2.py - Updated with correct function/class names
  - comprehensive_verification_v3.py - Final version with all fixes and improvements
- Identified and documented module structure:
  - 54 Python files in core/ directory
  - 4 Python files in cli/ directory
  - 92% success rate on module verification tests

### Added - 2025-05-23

#### Verification Infrastructure
- Created verification summary report documenting all findings
- Added task documentation in docs/tasks/task_007_complete_verification.md
- Implemented module verification system with:
  - Import verification for all modules
  - Attribute checking for expected functions/classes
  - Functional testing with real LLM calls
  - POC retry manager verification
  - Comprehensive file coverage analysis

### Known Issues
- LLM call test returns empty response (async handling investigation needed)
- ValidationResult test uses wrong attribute name (is_valid vs valid)
- POC Retry Manager import name mismatch in test

### Documentation
- Created verification_summary_report.md with complete findings
- Updated task tracking in docs/tasks/
- Documented all untested modules for future work


### Fixed - 2025-05-23

#### Core and CLI Module Verification
- Fixed critical router.py bug where 'provider' key was being passed to OpenAI API
  - Added  to remove utility keys
  - This was causing BadRequestError: "Unrecognized request argument supplied: provider"
- Created comprehensive verification infrastructure:
  -  - Initial verification script
  -  - Updated with correct function/class names
  -  - Final version with all fixes
- Verified 38 core and CLI modules with 92% success rate
- Identified and documented 32 untested utility modules for future coverage

### Added - 2025-05-23

#### Verification Infrastructure
- Created automated module verification system
- Added comprehensive test coverage reports
- Created task tracking documentation:
  - 
  - 
- Established module import validation for all core components

### Changed - 2025-05-23

#### Documentation
- Updated verification reports with current module status
- Added detailed task tracking for verification work
- Documented all critical paths and dependencies

### Known Issues
- LLM call test returns empty response (async handling investigation needed)
- ValidationResult test uses incorrect attribute name (is_valid → valid)
- POC Retry Manager import name mismatch (class name verification needed)

### Fixed - 2025-05-23

#### Core and CLI Module Verification
- Fixed critical router.py bug where provider key was being passed to OpenAI API
  - Added api_params.pop(provider, None) to remove utility keys
  - This was causing BadRequestError: Unrecognized request argument supplied: provider
- Created comprehensive verification infrastructure:
  - comprehensive_verification.py - Initial verification script
  - comprehensive_verification_v2.py - Updated with correct function/class names
  - comprehensive_verification_v3.py - Final version with all fixes
- Verified 38 core and CLI modules with 92% success rate
- Identified and documented 32 untested utility modules for future coverage

### Added - 2025-05-23

#### Verification Infrastructure
- Created automated module verification system
- Added comprehensive test coverage reports
- Created task tracking documentation:
  - docs/tasks/task_007_complete_verification.md
  - verification_summary_report.md
- Established module import validation for all core components

### Changed - 2025-05-23

#### Documentation
- Updated verification reports with current module status
- Added detailed task tracking for verification work
- Documented all critical paths and dependencies

### Known Issues
- LLM call test returns empty response (async handling investigation needed)
- ValidationResult test uses incorrect attribute name (is_valid should be valid)
- POC Retry Manager import name mismatch (class name verification needed)
