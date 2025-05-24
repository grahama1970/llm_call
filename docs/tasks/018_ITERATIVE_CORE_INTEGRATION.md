# Task 018: Iterative Core Integration ⏳ Not Started

**Objective**: Systematically integrate validated POC implementations into core modules using concrete examples and test-driven approach per TASK_LIST_TEMPLATE_GUIDE.md

**Requirements**:
1. Each integration must make a specific test pass
2. No breaking changes to existing functionality
3. Performance must meet POC benchmarks
4. Code must follow existing module patterns
5. Each task completes in 1-2 hours with working code examples

## Task 1: Make test max_text_001 pass with enhanced routing

**Test ID**: max_text_001_simple_question
**Model**: max/text-general
**Goal**: Update router.py to handle max/* models using POC 1 pattern

## Working Code Example

```python
# COPY THIS PATTERN INTO /src/llm_call/core/router.py:

async def route_request(self, model: str, messages: List[Dict], **kwargs) -> Dict:
    """Enhanced routing with max/* model support"""
    # Add this pattern to existing route_request method:
    
    # Handle max/* models via Claude proxy
    if model.startswith("max/"):
        return {
            "provider": "claude_proxy",
            "endpoint": "http://localhost:8002",
            "headers": {"X-Model-Type": model.split("/")[1]},
            "model": model,
            "formatted_request": {
                "model": model,
                "messages": messages,
                **kwargs
            }
        }
    
    # Existing routing logic continues here...
    return await self._original_route_request(model, messages, **kwargs)
```

## Test Details

**Run Command**:
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python -m pytest tests/llm_call/core/test_router.py -k test_max_model_routing -v
```

**Expected Output Structure**:
```json
{
  "provider": "claude_proxy",
  "endpoint": "http://localhost:8002",
  "model": "max/text-general"
}
```

## Common Issues & Solutions

### Issue 1: Router doesn't recognize max/* pattern
```python
# Solution: Add to PROVIDER_PATTERNS in router.py
PROVIDER_PATTERNS = {
    "max/*": "claude_proxy",  # Add this line
    "openai/*": "litellm",
    # ... existing patterns
}
```

### Issue 2: Import error for POC code
```python
# Solution: Don't import POC, copy the pattern directly
# POCs are examples, not dependencies
```

## Validation Requirements

```python
# This update passes when:
router = Router()
result = await router.route_request("max/text-general", [{"role": "user", "content": "test"}])
assert result["provider"] == "claude_proxy"
assert result["model"] == "max/text-general"
assert "endpoint" in result
```

---

## Task 2: Make JSON validation tests pass with POC 6 pattern

**Test ID**: json_parse_001_valid_json
**Model**: openai/gpt-3.5-turbo
**Goal**: Add JSON extraction to validation strategies

## Working Code Example

```python
# CREATE NEW FILE /src/llm_call/core/validation/json_validators.py:

import json
import re
from typing import Dict, Any, Optional

class JSONExtractionValidator:
    """Extract and validate JSON from LLM responses"""
    
    def validate(self, response: str, expected_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract JSON from markdown or mixed content"""
        # Pattern from POC 6
        json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',
            r'```\s*([\s\S]*?)\s*```',
            r'\{[\s\S]*\}'
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1) if '```' in pattern else match.group(0)
                    parsed = json.loads(json_str)
                    return {"valid": True, "data": parsed}
                except json.JSONDecodeError:
                    continue
        
        return {"valid": False, "error": "No valid JSON found"}

# ADD TO /src/llm_call/core/validation/__init__.py:
from .json_validators import JSONExtractionValidator
```

## Test Details

**Run Command**:
```bash
python -m pytest tests/llm_call/core/validation/test_json_validators.py -v
```

**Expected Output**:
```python
validator = JSONExtractionValidator()
result = validator.validate("Here's the data: ```json\n{\"key\": \"value\"}\n```")
assert result["valid"] == True
assert result["data"]["key"] == "value"
```

## Common Issues & Solutions

### Issue 1: Import path conflicts
```python
# Solution: Use relative imports in validation/__init__.py
from .json_validators import JSONExtractionValidator
```

### Issue 2: Schema validation needed
```python
# Solution: Use jsonschema if expected_schema provided
if expected_schema and parsed:
    from jsonschema import validate
    validate(instance=parsed, schema=expected_schema)
```

---

## Task 3: Make retry tests pass with exponential backoff

**Test ID**: retry_expo_001_backoff_test  
**Model**: any
**Goal**: Enhance retry.py with POC 27 exponential backoff pattern

## Working Code Example

```python
# UPDATE /src/llm_call/core/retry.py - add this class:

import asyncio
import random
from typing import Optional, Callable, Any

class ExponentialBackoffRetry:
    """Enhanced retry with exponential backoff and jitter"""
    
    def __init__(self, 
                 max_attempts: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with exponential backoff retry"""
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_attempts - 1:
                    raise
                
                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                
                # Add jitter if enabled
                if self.jitter:
                    delay *= (0.5 + random.random())
                
                await asyncio.sleep(delay)
        
        raise Exception("Max retries exceeded")

# Update existing retry function to use this pattern
```

## Test Details

**Run Command**:
```bash
python -m pytest tests/llm_call/core/test_retry.py -k test_exponential_backoff -v
```

**Expected Behavior**:
- Attempt 1: Immediate
- Attempt 2: ~1 second delay (with jitter: 0.5-1.5s)
- Attempt 3: ~2 second delay (with jitter: 1-3s)
- Attempt 4: ~4 second delay (with jitter: 2-6s)

## Common Issues & Solutions

### Issue 1: Breaking existing retry interface
```python
# Solution: Keep backward compatibility
class RetryManager:
    def __init__(self, strategy="exponential", **kwargs):
        if strategy == "exponential":
            self.impl = ExponentialBackoffRetry(**kwargs)
        else:
            self.impl = BasicRetry(**kwargs)  # Keep old behavior
```

---

## Task 4: Make multimodal test pass with image handling

**Test ID**: openai_multimodal_001_image_description
**Model**: openai/gpt-4-vision-preview
**Goal**: Update multimodal_utils.py with POC 11 image encoding

## Working Code Example

```python
# UPDATE /src/llm_call/core/utils/multimodal_utils.py:

import base64
from pathlib import Path
from typing import Dict, Union

def encode_image(image_path: Union[str, Path]) -> Dict[str, str]:
    """Encode image for multimodal LLM requests"""
    path = Path(image_path)
    
    # Validate file exists and is an image
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    suffix = path.suffix.lower()
    if suffix not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        raise ValueError(f"Unsupported image format: {suffix}")
    
    # Read and encode
    with open(path, 'rb') as f:
        image_data = f.read()
    
    base64_image = base64.b64encode(image_data).decode('utf-8')
    mime_type = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }[suffix]
    
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:{mime_type};base64,{base64_image}"
        }
    }

# Add this import to the file
```

## Test Details

**Run Command**:
```bash
# Create test image first
echo "test" > /tmp/test.png
python -m pytest tests/llm_call/core/utils/test_multimodal.py -k test_image_encoding -v
```

**Expected Output**:
```python
result = encode_image("/tmp/test.png")
assert result["type"] == "image_url"
assert result["image_url"]["url"].startswith("data:image/png;base64,")
```

---

## Task 5: Make CLI test runner work with POC 31

**Test ID**: cli_runner_001_basic_execution
**Model**: any
**Goal**: Create CLI test runner command

## Working Code Example

```python
# CREATE NEW FILE /src/llm_call/cli/test_runner.py:

import asyncio
import json
from pathlib import Path
from typing import List, Dict
import typer
from loguru import logger

app = typer.Typer()

@app.command()
def run(
    test_file: Path = typer.Argument(..., help="Path to test JSON file"),
    test_id: str = typer.Option(None, "--test-id", "-t", help="Run specific test"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Run tests in parallel")
):
    """Run validation tests from JSON file"""
    # Load tests
    with open(test_file) as f:
        tests = json.load(f)
    
    # Filter if test_id specified
    if test_id:
        tests = [t for t in tests if t.get("test_case_id") == test_id]
    
    if not tests:
        logger.error(f"No tests found{f' with id {test_id}' if test_id else ''}")
        raise typer.Exit(1)
    
    # Run tests
    if parallel:
        asyncio.run(run_parallel(tests))
    else:
        run_sequential(tests)

def run_sequential(tests: List[Dict]):
    """Run tests one by one"""
    passed = 0
    failed = 0
    
    for test in tests:
        logger.info(f"Running {test['test_case_id']}...")
        try:
            # Execute test logic here
            passed += 1
            logger.success(f"✅ {test['test_case_id']} passed")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test['test_case_id']} failed: {e}")
    
    logger.info(f"\nResults: {passed} passed, {failed} failed")

# ADD TO /src/llm_call/cli/main.py:
from .test_runner import app as test_app
app.add_typer(test_app, name="test", help="Run validation tests")
```

## Test Details

**Run Command**:
```bash
python -m llm_call.cli.main test run /path/to/test_prompts.json --test-id max_text_001
```

**Expected Output**:
```
Running max_text_001_simple_question...
✅ max_text_001_simple_question passed

Results: 1 passed, 0 failed
```

---

## Integration Order & Dependencies

1. **Router (Task 1)** - No dependencies, safe to start
2. **JSON Validators (Task 2)** - New module, low risk
3. **Retry (Task 3)** - Update carefully, many dependencies
4. **Multimodal (Task 4)** - Isolated utility, safe
5. **CLI Runner (Task 5)** - New feature, no conflicts

## Success Criteria

Each task is complete when:
1. The specific test case passes
2. No existing tests break
3. The code follows the existing patterns in the module
4. Performance meets or exceeds POC benchmarks

## Timeline

- Task 1: 1 hour (simple addition)
- Task 2: 2 hours (new module)
- Task 3: 2 hours (careful integration)
- Task 4: 1 hour (utility update)
- Task 5: 2 hours (new CLI feature)

**Total: 8 hours of focused integration**

## Verification Requirements

Each task MUST include:
1. **Before**: Show current behavior/error
2. **After**: Show working test output
3. **Performance**: Verify meets POC benchmarks
4. **Report**: Create verification report in `/docs/reports/018_task_N_*.md`

## Task Status Tracking

- [ ] Task 1: Router max/* models support
- [ ] Task 2: JSON validators module
- [ ] Task 3: Exponential backoff retry
- [ ] Task 4: Multimodal image encoding
- [ ] Task 5: CLI test runner

**Status**: ⏳ Not Started | **Priority**: HIGH | **Complexity**: MEDIUM