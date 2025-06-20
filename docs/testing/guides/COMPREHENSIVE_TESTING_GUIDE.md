# Comprehensive Testing Guide for LLM Call

## Overview

The llm_call project now includes a comprehensive test suite that thoroughly tests all features with real LLM calls. This guide documents the testing framework and how to use it.

## Test Suite Features

### 1. **Comprehensive Coverage**
The test suite covers all major features:
- Basic text queries across multiple models
- System prompts and custom configurations
- Multimodal image analysis
- Response validation strategies
- Conversation management
- Document processing and corpus analysis
- Configuration file support
- Error handling and recovery
- Streaming responses
- Model-specific features
- Performance and caching

### 2. **Cost Optimization with Caching**
To reduce API costs during testing:
- **Enable caching**: Add `--cache` flag when running tests
- **Redis cache**: Uses Redis if available (configured via REDIS_HOST, REDIS_PORT)
- **In-memory fallback**: Falls back to local cache if Redis unavailable
- **Automatic deduplication**: Identical requests are served from cache
- **Cache support in slash commands**: Use `/llm_call --query "test" --cache`
- **TTL**: Redis cache persists for 48 hours, in-memory for 1 hour

### 3. **Test Categories**

#### Core Functionality
- Basic queries with different models (max/opus, GPT-3.5, Gemini)
- System prompts and role-based conversations
- Parameter control (temperature, max tokens)

#### Multimodal
- Local image file analysis
- Support for different vision models (Claude Max, GPT-4 Vision)
- Mixed text and image content

#### Validation
- JSON validation with field presence checks
- Length validators for minimum content
- Custom validation chains

#### Advanced Features
- Conversation management with SQLite persistence
- Multi-turn conversations with context
- Cross-model conversation continuity
- Streaming response handling

#### Document Processing
- Corpus/directory analysis
- Document summarization
- File type filtering

#### Configuration
- JSON configuration files
- YAML configuration support
- Parameter overrides

#### Reliability
- Invalid model handling
- Timeout management
- Graceful error recovery

#### Model Features
- Gemini's large context window testing
- Claude's code analysis capabilities
- Model-specific optimizations

#### Performance
- Cache effectiveness testing
- Response time comparison
- Cost optimization verification

## Running the Tests

### Basic Test Run
```bash
cd /home/graham/workspace/experiments/llm_call
source .venv/bin/activate
python -m llm_call.verification.comprehensive_test_suite
```

### With Caching (Recommended)
```bash
python -m llm_call.verification.comprehensive_test_suite --cache
```

### Skip HTML Report
```bash
python -m llm_call.verification.comprehensive_test_suite --no-report
```

## Test Implementation

### Test Structure
Each test follows this pattern:
1. **Interface Testing**: Tests functionality across slash commands, CLI, and Python imports
2. **Result Verification**: Checks for expected output patterns
3. **Timing Capture**: Records execution duration for performance analysis
4. **Error Handling**: Gracefully handles failures without stopping the suite

### Adding New Tests
To add a new test category:

```python
def test_new_feature(self):
    """Test new feature across interfaces."""
    test = InterfaceTest("Feature Name", "Feature description")
    test.category = "Category Name"
    
    # Test slash command
    cmd = ["/home/graham/.claude/commands/llm_call", "--query", "test", "--new-param"]
    success, output, duration = self.run_command(cmd)
    test.add_result("slash_new_feature", success, output, ' '.join(cmd), duration)
    
    # Test Python interface
    code = '''
    from llm_call import ask
    result = await ask("test", new_param=True)
    '''
    success, output, duration = asyncio.run(self.run_python_interface(code))
    test.add_result("python_new_feature", success, output, "Python: new feature", duration)
    
    self.tests.append(test)
```

## Test Results

### HTML Report
- **Location**: `/home/graham/workspace/experiments/llm_call/verification_dashboard.html`
- **Access**: `http://localhost:8891/verification_dashboard.html`
- **Features**:
  - Interactive React/Tailwind interface
  - Test results by category
  - Detailed command outputs
  - Performance metrics
  - Success rate visualization

### Gemini Verification
The test suite uses Google Gemini to independently verify test results:
- Analyzes test patterns for authenticity
- Confirms feature functionality
- Provides external validation

## Caching Details

### Enable Caching in Code
```python
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache

# Initialize cache (automatically chooses Redis or in-memory)
initialize_litellm_cache()
```

The cache initialization:
1. Checks for Redis availability (REDIS_HOST, REDIS_PORT env vars)
2. Attempts Redis connection with 2-second timeout
3. Falls back to in-memory cache if Redis unavailable
4. Supports completion, acompletion, and embedding calls

### Cache Benefits
- **Cost Reduction**: Avoid duplicate API calls
- **Faster Testing**: Cached responses return instantly
- **Persistent Storage**: Cache survives between runs
- **Automatic Management**: LiteLLM handles cache expiration

### Cache Configuration
- **Redis**: Set `REDIS_HOST` and `REDIS_PORT` in `.env`
- **TTL**: 48 hours for Redis, 1 hour for in-memory
- **Supported Calls**: completion, acompletion, embedding
- **Clear Redis Cache**: `redis-cli FLUSHDB` (if using Redis)

## Integration with CI/CD

### GitHub Actions Example
```yaml
- name: Run LLM Call Tests
  run: |
    source .venv/bin/activate
    python -m llm_call.verification.comprehensive_test_suite --cache
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GOOGLE_CREDENTIALS }}
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit
python -m llm_call.verification.comprehensive_test_suite --cache --no-report
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

## Troubleshooting

### Cache Not Working
If you see "Could not enable cache":
```bash
pip install "litellm[caching]"
# or
uv add "litellm[caching]"
```

### Tests Timing Out
Increase timeout for slow operations:
```python
success, output, duration = self.run_command(cmd, timeout=120)  # 2 minutes
```

### API Key Issues
Ensure all required keys are in `.env`:
- `OPENAI_API_KEY`
- `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY` (handled automatically for max/claude)

## Best Practices

1. **Always Use Cache**: Run tests with `--cache` to minimize costs
2. **Test Incrementally**: Add tests for new features as you develop
3. **Monitor Success Rates**: Aim for >90% success rate
4. **Review Failed Tests**: Check HTML report for detailed failure reasons
5. **Update Tests**: Keep tests current with feature changes

## Future Enhancements

1. **Parallel Test Execution**: Run tests concurrently for speed
2. **Test Categorization**: Run specific test categories only
3. **Performance Benchmarking**: Track response times over time
4. **Cost Tracking**: Monitor API usage and costs
5. **Integration Tests**: Test llm_call with other Granger modules

---

The comprehensive test suite ensures llm_call remains reliable and feature-complete across all interfaces and use cases.