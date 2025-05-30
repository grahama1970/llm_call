# Test Commands

Run tests for the LLM Call project.

## Quick Test Commands

/test-all
Description: Run all tests
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/ -v
```

/test-core
Description: Run core functionality tests
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/core/ -v
```

/test-cli
Description: Run CLI tests
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/cli/ -v
```

/test-validation
Description: Run validation framework tests
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/core/validation/ -v
```

/test-poc
Description: Run proof-of-concept tests
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/proof_of_concept/ -v
```

## Specific Test Suites

/test-router
Description: Test LLM routing functionality
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/core/test_router.py -v
```

/test-retry
Description: Test retry and exponential backoff
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/core/test_retry_exponential.py -v
```

/test-json-validators
Description: Test JSON validation strategies
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/core/validation/test_json_validators.py -v
```

/test-ai-validators
Description: Test AI-based validators
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/core/validation/test_ai_validator_real_llm.py -v
```

/test-polling
Description: Test async SQLite polling
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python tests/llm_call/core/test_claude_proxy_polling_final.py
```

## Coverage and Reports

/test-coverage
Description: Run tests with coverage report
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/ --cov=src/llm_call --cov-report=html --cov-report=term
# View HTML report
open htmlcov/index.html
```

/test-report
Description: Generate test report
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python tests/run_tests_with_report.py
```

## Integration Tests

/test-llm-integration
Description: Test real LLM integrations (requires API keys)
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/cli/test_llm_integration.py -v -s
```

/test-mcp-features
Description: Test MCP server features
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/llm_call/cli/test_mcp_features.py -v
```

/test-claude-proxy
Description: Test Claude proxy functionality
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
# Ensure proxy is running first
python src/llm_call/proof_of_concept/poc_claude_proxy_with_polling.py &
sleep 5
# Run tests
python tests/llm_call/core/test_claude_proxy_real.py
```

## Performance Tests

/test-performance
Description: Run performance benchmarks
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python -m pytest tests/ -v -k "performance" --benchmark-only
```

/test-concurrent
Description: Test concurrent request handling
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python tests/llm_call/core/test_claude_proxy_polling.py
```

## Test Utilities

/test-single [test_name]
Description: Run a single test by name
Arguments:
  - test_name: Name of the test function
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest -v -k "[test_name]"
```

/test-debug [test_file]
Description: Run test with debugging enabled
Arguments:
  - test_file: Path to test file
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest [test_file] -v -s --pdb
```

/test-parallel
Description: Run tests in parallel
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest tests/ -v -n auto
```

/test-markers
Description: List all test markers
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
pytest --markers
```

## Environment Setup

/test-env-check
Description: Check test environment
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python -c "
import os
import sys
print(f'Python: {sys.version}')
print(f'Working dir: {os.getcwd()}')

# Check for required env vars
env_vars = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'CLAUDE_CLI_PATH']
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f'{var}: Set ({len(value)} chars)')
    else:
        print(f'{var}: NOT SET')

# Check for test fixtures
import pathlib
fixtures = pathlib.Path('tests/fixtures/user_prompts.jsonl')
print(f'Test fixtures exist: {fixtures.exists()}')
"
```

/test-install-deps
Description: Install test dependencies
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
uv add --dev pytest pytest-asyncio pytest-cov pytest-xdist pytest-benchmark
```

## Common Test Workflows

### 1. Pre-commit Testing
```bash
# Run quick tests before committing
/test-core
/test-cli

# Check coverage
/test-coverage
```

### 2. Full Test Suite
```bash
# Run all tests with report
/test-report

# Review any failures
grep -E "(FAILED|ERROR)" test_report_latest.md
```

### 3. Debug Failing Test
```bash
# Run specific failing test with debug
/test-debug tests/llm_call/core/test_router.py::test_specific_function

# Run with verbose output
/test-single test_specific_function -v -s
```