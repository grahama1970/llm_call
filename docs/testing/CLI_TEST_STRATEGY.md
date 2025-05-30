# CLI Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the LLM CLI, ensuring all features work correctly and align with documentation.

## Test Structure

### 1. **test_cli_comprehensive.py**
Comprehensive test suite covering all CLI commands and features:
- Core LLM Commands (ask, chat, call, models, validators)
- Configuration Management (config files, overrides)
- Auto-generation Commands (generate-claude, generate-mcp-config)
- MCP Server Features (serve-mcp)
- Test Runner Commands (test, test-poc)
- README Alignment Verification

### 2. **test_mcp_features.py**
Focused testing of MCP (Model Context Protocol) functionality:
- MCP configuration generation and structure
- MCP server initialization
- Tool registration and mapping
- Claude slash command integration
- Slash/MCP mixin functionality

### 3. **test_llm_integration.py**
Integration tests with underlying LLM infrastructure:
- Router integration and model selection
- Validation framework integration
- Retry mechanism testing
- Provider-specific integration
- Streaming response handling
- Error propagation

### 4. **run_all_cli_tests.py**
Master test runner that:
- Runs all test suites
- Verifies README alignment
- Checks feature coverage
- Validates real CLI execution
- Generates comprehensive report

## Key Testing Areas

### A. Command Functionality
Every CLI command must be tested with:
- Basic usage
- All parameter combinations
- Error conditions
- Help text verification

### B. Configuration Management
- JSON/YAML config loading
- CLI parameter overrides
- Configuration priority (CLI > file > defaults)
- Invalid configuration handling

### C. MCP Integration
- MCP config generation correctness
- Tool parameter mapping
- Server command construction
- Claude slash command format

### D. Documentation Alignment
- All README examples must work
- Command names must match documentation
- Feature descriptions must be accurate
- Model routing must match documentation

### E. Error Handling
- Invalid inputs
- Missing dependencies
- API failures
- Configuration errors

## Test Execution

### Quick Test
```bash
# Run basic CLI validation
python tests/llm_call/cli/run_all_cli_tests.py
```

### Full Test Suite
```bash
# Run all tests with coverage
pytest tests/llm_call/cli/ -v --cov=llm_call.cli --cov-report=html
```

### Individual Test Suites
```bash
# Comprehensive tests
pytest tests/llm_call/cli/test_cli_comprehensive.py -v

# MCP tests
pytest tests/llm_call/cli/test_mcp_features.py -v

# Integration tests
pytest tests/llm_call/cli/test_llm_integration.py -v
```

## Test Coverage Goals

1. **Command Coverage**: 100% of CLI commands tested
2. **Parameter Coverage**: All command parameters tested
3. **Error Coverage**: All error conditions handled
4. **Documentation Coverage**: All README examples verified
5. **Integration Coverage**: All provider integrations tested

## Continuous Testing

### Pre-commit Checks
1. Run quick validation test
2. Verify no broken commands
3. Check README alignment

### CI/CD Pipeline
1. Run full test suite
2. Generate coverage report
3. Verify MCP generation
4. Test with multiple Python versions

## Test Maintenance

### When Adding New Features
1. Add corresponding tests
2. Update README with examples
3. Verify examples in tests
4. Update this strategy document

### When Modifying Commands
1. Update all affected tests
2. Verify README examples still work
3. Check MCP/slash command generation
4. Run full test suite

## Known Issues and Limitations

1. **FastMCP Dependency**: MCP server tests require mocking when fastmcp not installed
2. **API Keys**: Integration tests may skip if API keys not configured
3. **Async Testing**: Some async patterns require special handling in tests

## Test Data

Test data is minimal and generated on-the-fly:
- Temporary config files
- Mock LLM responses
- Sample command outputs

No large test fixtures are required, keeping tests fast and maintainable.