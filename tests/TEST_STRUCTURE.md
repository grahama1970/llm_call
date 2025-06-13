# Test Structure Documentation

## Overview

Tests are organized into categories based on their purpose and scope. All tests use real APIs and services - no mocking is allowed per CLAUDE.md standards.

## Two-Stage Testing Strategy

### Stage 1: Local Tests (No Docker)
- Run directly against the source code
- Test core functionality without containerization
- Faster feedback loop for development
- Categories: unit, integration, validation, e2e, smoke

### Stage 2: Container Tests (Docker Required)
- Test the fully containerized application
- Verify Docker configuration and security
- Test inter-service communication
- Ensure production-like behavior

Use `scripts/run_comprehensive_tests.py` to run both stages.

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- Fast, isolated tests for individual functions/classes
- No external dependencies or API calls
- Currently empty - most llm_call functionality requires external services

### 2. Integration Tests (`tests/integration/`)
- Verify integration with external services (LLMs, APIs)
- Real API calls to providers
- Files:
  - `test_llm_integration_real.py` - Comprehensive LLM provider tests
  - `test_claude_proxy.py` - Claude proxy server integration
  - `test_openai_simple.py` - OpenAI API integration

### 3. Validation Tests (`tests/validation/`)
- Output quality and correctness validation
- Honeypot tests to ensure testing integrity
- Files:
  - `test_honeypot.py` - Must-fail tests to verify no mocking

### 4. End-to-End Tests (`tests/e2e/`)
- Complete workflow tests
- Full system integration
- Files:
  - `test_hello_world_simple.py` - Basic end-to-end flow
  - `test_model_hello_world.py` - Model-specific workflows
  - `test_llm_call.py` - Complete llm_call workflows

### 5. Smoke Tests (`tests/smoke/`)
- Quick sanity checks
- Verify basic functionality
- Files:
  - `test_basic.py` - Import and environment checks

### 6. Performance Tests (`tests/performance/`)
- Benchmarks and load tests
- Response time measurements
- Currently empty - to be implemented

### 7. Container Tests (`tests/container/`)
- Docker-specific tests
- Inter-service communication
- Volume and security verification
- Files:
  - `test_docker_api.py` - Container API and security tests

### 8. Fixtures (`tests/fixtures/`)
- Test data and resources
- Shared test configurations
- Sample prompts and responses

## Running Tests

### Comprehensive Testing (Recommended)
```bash
# Run both local and container tests
python scripts/run_comprehensive_tests.py --stage all

# Run only local tests (faster)
python scripts/run_comprehensive_tests.py --stage local

# Run only container tests
python scripts/run_comprehensive_tests.py --stage container

# Verbose output
python scripts/run_comprehensive_tests.py --stage all --verbose
```

### Manual Testing
```bash
# Run all tests
pytest

# Run by category
pytest tests/unit/
pytest tests/integration/
pytest tests/validation/

# Run with markers
pytest -m "not slow"
pytest -m integration

# Run specific test
pytest tests/integration/test_llm_integration_real.py::TestLLMIntegration::test_vertex_ai

# Run with coverage
pytest --cov=src --cov-report=html

# Container tests (requires Docker)
docker-compose up -d
pytest tests/container/
docker-compose down
```

## Test Requirements

Per CLAUDE.md standards:
1. **No mocking** - All tests must use real services
2. **Real data only** - No fake/synthetic test data
3. **Track all failures** - Don't stop at first failure
4. **Exit codes** - 1 for failure, 0 for success
5. **Honeypot tests** - Include tests that must fail

## Archived Tests

Old debug and POC tests have been moved to `archive/old_tests/`:
- Various `*_debug.py` files
- OAuth and authentication tests
- Direct API tests
- Key management tests

These can be referenced if needed but are not part of the main test suite.