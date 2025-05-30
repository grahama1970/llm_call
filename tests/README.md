# LLM Call Test Suite

This directory contains the comprehensive test suite for the `llm_call` package. The test structure mirrors the `src/` directory for easy navigation and maintenance.

## Test Structure

```
tests/
├── llm_call/
│   ├── cli/               # CLI command tests
│   ├── core/              # Core functionality tests
│   │   ├── api/           # API endpoint tests
│   │   ├── config/        # Configuration tests
│   │   ├── providers/     # Provider-specific tests
│   │   ├── utils/         # Utility function tests
│   │   └── validation/    # Validation strategy tests
│   ├── proof_of_concept/  # POC validation tests
│   ├── rl_integration/    # RL integration tests (if applicable)
│   └── tools/             # Tool integration tests
├── fixtures/              # Test data and fixtures
├── conftest.py           # Pytest configuration
└── run_tests_with_report.py  # Test runner with reporting
```

## Running Tests

### Run All Tests
```bash
# From project root
cd /home/graham/workspace/experiments/claude_max_proxy
source .venv/bin/activate

# Run all tests with pytest
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/llm_call --cov-report=html

# Run with detailed output
pytest tests/ -v -s
```

### Run Specific Test Categories

#### CLI Tests
```bash
pytest tests/llm_call/cli/ -v
```

#### Core Tests
```bash
pytest tests/llm_call/core/ -v
```

#### Validation Tests
```bash
pytest tests/llm_call/core/validation/ -v
```

### Run Tests with Custom Reporter
```bash
# This generates a detailed HTML report
python tests/run_tests_with_report.py
```

### Run Individual Test Files
```bash
# Example: Run router tests
pytest tests/llm_call/core/test_router.py -v

# Example: Run validation integration tests
pytest tests/llm_call/core/test_validation_integration.py -v
```

## Test Categories

### Unit Tests
- `test_router.py` - Router logic and model selection
- `test_retry_exponential.py` - Retry logic with exponential backoff
- `test_json_validators.py` - JSON validation strategies
- `test_image_encoding_enhancements.py` - Image processing utilities

### Integration Tests
- `test_core_integration.py` - Full core functionality integration
- `test_validation_integration.py` - Validation framework integration
- `test_llm_integration.py` - LLM provider integration
- `test_unified_integration.py` - End-to-end system tests

### Real LLM Tests
These tests use actual LLM calls and require API keys:
- `test_ai_validator_real_llm.py` - AI validator with real LLMs
- `test_claude_proxy_real.py` - Claude proxy integration
- `test_mcp_features_real.py` - MCP features with real calls

**Note**: Real LLM tests are expensive and should be run selectively:
```bash
# Skip real LLM tests
pytest tests/ -v -m "not real_llm"

# Run only real LLM tests
pytest tests/ -v -m "real_llm"
```

## Test Fixtures

Test fixtures are located in `tests/fixtures/`:
- `user_prompts.jsonl` - Sample user prompts for testing
- `user_prompts_extended.jsonl` - Extended prompt dataset

## Important Testing Guidelines

1. **No Mocking Core Functionality**: Tests should use real implementations, not mocks
2. **Real Data Validation**: Tests must verify actual outputs against expected results
3. **100% Non-Mocked Tests**: All tests should pass without mocking core LLM functionality
4. **Mirror Source Structure**: Test directory structure must exactly mirror `src/`

## Continuous Integration

Before pushing changes:
```bash
# Run full test suite
pytest tests/ -v

# Check for any broken tests
pytest tests/ --tb=short

# Verify no tests are skipped
pytest tests/ -v | grep -i skip
```

## Adding New Tests

When adding new functionality:
1. Create test file in the corresponding test directory
2. Follow naming convention: `test_<module_name>.py`
3. Include both positive and negative test cases
4. Test edge cases and error conditions
5. Use real data, not synthetic test data

Example test structure:
```python
import pytest
from llm_call.core.module import function_to_test

class TestModuleName:
    def test_normal_operation(self):
        """Test normal expected behavior."""
        result = function_to_test("input")
        assert result == "expected_output"
    
    def test_edge_case(self):
        """Test edge cases and boundaries."""
        result = function_to_test("")
        assert result is None
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            function_to_test(None)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH is set correctly
   ```bash
   export PYTHONPATH=./src:$PYTHONPATH
   ```

2. **API Key Errors**: Set required environment variables
   ```bash
   source .env  # Load from .env file
   ```

3. **Test Discovery Issues**: Ensure all test directories have `__init__.py` files

### Debug Tips

- Use `-s` flag to see print statements: `pytest tests/ -v -s`
- Use `--pdb` to drop into debugger on failure: `pytest tests/ --pdb`
- Run specific test: `pytest tests/path/to/test.py::TestClass::test_method`

## Performance Benchmarks

Run performance tests:
```bash
pytest tests/ -v --benchmark-only
```

## Test Coverage Goals

- Minimum coverage: 80%
- Critical paths: 100%
- Error handling: 100%
- Integration points: 90%

Check current coverage:
```bash
pytest tests/ --cov=src/llm_call --cov-report=term-missing
```