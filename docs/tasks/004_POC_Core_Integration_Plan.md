# Task 004: POC to Core Module Integration Plan

## Overview
This document outlines the plan for integrating the 29 successful POC implementations from Task 004 into the core modules at `/src/llm_call/core/` and `/src/llm_call/cli/`.

## Integration Priority Order

### Phase 1: Core Infrastructure (High Priority)
1. **Router Module Updates** (`/src/llm_call/core/router.py`)
   - Integrate POCs 1-5 routing logic
   - Add max/* model handling from POC 1
   - Add provider-specific request formatting from POC 3
   - Add error handling and fallback from POC 4
   - Performance optimizations from POC 5

2. **Retry Module Enhancement** (`/src/llm_call/core/retry.py`)
   - Replace basic retry with advanced strategies from POCs 26-30
   - Add exponential backoff with jitter (POC 27)
   - Add circuit breaker implementation (POC 27)
   - Add tool-assisted retry (POC 28)
   - Add human escalation workflow (POC 29)
   - Add debug mode from POC 30

### Phase 2: Validation Framework (High Priority)
3. **Validation Strategies** (`/src/llm_call/core/validation/`)
   - Create new validators:
     - `json_validators.py` from POCs 6-10
     - `string_validators.py` from POCs 17-19
     - `agent_validators.py` from POCs 14-16
   - Update base validator to support new patterns
   - Add performance optimizations

4. **Validation Manager Updates** (`/src/llm_call/core/validation/retry_manager.py`)
   - Integrate staged retry logic
   - Add escalation rules
   - Add validation result aggregation from POC 16

### Phase 3: Utilities and Support (Medium Priority)
5. **Multimodal Utils** (`/src/llm_call/core/utils/multimodal_utils.py`)
   - Add image encoding from POC 11
   - Add size optimization from POC 12
   - Add provider-specific formatting from POC 13
   - Support multiple image formats

6. **JSON Utils Enhancement** (`/src/llm_call/core/utils/json_utils.py`)
   - Add markdown extraction from POC 6
   - Add malformed JSON repair from POC 10
   - Add nested field validation helpers

### Phase 4: CLI Integration (Medium Priority)
7. **CLI Commands** (`/src/llm_call/cli/main.py`)
   - Add test runner command from POC 31
   - Add performance tracking options from POC 33
   - Add failure report generation from POC 34
   - Add debug mode flag

8. **CLI Test Runner** (`/src/llm_call/cli/test_runner.py`) - NEW FILE
   - Implement full test runner from POCs 31-35
   - Add parallel execution support
   - Add result aggregation
   - Add performance tracking

## Implementation Strategy

### Step 1: Create Feature Branches
```bash
git checkout -b feature/poc-routing-integration
git checkout -b feature/poc-validation-integration
git checkout -b feature/poc-retry-integration
git checkout -b feature/poc-multimodal-integration
git checkout -b feature/poc-cli-integration
```

### Step 2: Integration Pattern
For each module integration:
1. Read existing module code
2. Identify integration points
3. Copy relevant POC code
4. Adapt to existing patterns
5. Add tests
6. Update documentation

### Step 3: Testing Strategy
- Unit tests for each integrated component
- Integration tests for combined functionality
- Performance benchmarks to ensure targets are met
- Run full test suite from `test_prompts.json`

## Success Criteria
- [ ] All 29 POC features integrated
- [ ] No regression in existing functionality
- [ ] Performance targets maintained
- [ ] All tests passing
- [ ] Documentation updated

## Risk Mitigation
- Create backups before major changes
- Test incrementally
- Use feature flags for gradual rollout
- Maintain backwards compatibility

## Timeline Estimate
- Phase 1: 2-3 hours
- Phase 2: 2-3 hours
- Phase 3: 1-2 hours
- Phase 4: 1-2 hours
- Testing & Documentation: 2-3 hours

**Total: 8-13 hours of focused work**

## Next Steps
1. Review this plan
2. Create feature branches
3. Start with Phase 1 (Router module)
4. Test after each integration
5. Document changes in CHANGELOG.md