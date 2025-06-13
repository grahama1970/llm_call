# Task 013: Verify Router Provider Key Fix

## Objective
Verify the critical fix that removes the provider key from API parameters in router.py.

## Background
The router was passing 'provider' to the OpenAI API causing: BadRequestError: Unrecognized request argument supplied: provider

## Commands to Execute

### 1. Verify Fix in Source Code
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/llm_call/ && grep -n "api_params.pop.*provider" src/llm_call/core/router.py'"
```

Expected output: Line showing api_params.pop("provider", None)

### 2. Test Router Removes Provider Key
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/llm_call/ && source .venv/bin/activate && cd src && python -c "
from llm_call.core.router import resolve_route
test_config = {
    \"model\": \"gpt-4o-mini\",
    \"messages\": [{\"role\": \"user\", \"content\": \"test\"}],
    \"provider\": \"litellm\",
    \"temperature\": 0.5
}
provider_class, params = resolve_route(test_config)
print(f\"Provider class: {provider_class.__name__}\")
print(f\"Provider key in params: {\"provider\" in params}\")
print(f\"Expected: False, Actual: {\"provider\" in params}\")
if \"provider\" not in params:
    print(\"✅ Router correctly removes provider key\")
else:
    print(\"❌ FAILED: provider key still present\")
"'"
```

### 3. Test All Utility Keys Removed
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/llm_call/ && source .venv/bin/activate && cd src && python -c "
from llm_call.core.router import resolve_route
test_config = {
    \"model\": \"gpt-4\",
    \"messages\": [{\"role\": \"user\", \"content\": \"test\"}],
    \"provider\": \"openai\",
    \"image_directory\": \"/tmp/images\",
    \"max_image_size_kb\": 1024,
    \"vertex_credentials_path\": \"/path/to/creds\",
    \"retry_config\": {\"max_attempts\": 3},
    \"skip_claude_multimodal\": True
}
_, params = resolve_route(test_config)
utility_keys = [\"provider\", \"image_directory\", \"max_image_size_kb\", 
                \"vertex_credentials_path\", \"retry_config\", \"skip_claude_multimodal\"]
all_removed = True
for key in utility_keys:
    if key in params:
        print(f\"❌ {key} still present in params\")
        all_removed = False
if all_removed:
    print(\"✅ All utility keys correctly removed\")
"'"
```

### 4. Integration Test - No Provider Error
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/llm_call/ && source .venv/bin/activate && cd src && python -c "
import asyncio
from llm_call.core.caller import make_llm_request
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache

async def test_no_provider_error():
    initialize_litellm_cache()
    config = {
        \"model\": \"gpt-4o-mini\",
        \"messages\": [{\"role\": \"user\", \"content\": \"Say OK\"}],
        \"provider\": \"litellm\",
        \"max_tokens\": 5
    }
    try:
        result = await make_llm_request(config)
        # Check if error mentions provider
        print(\"✅ No provider key error - fix is working\")
        return True
    except Exception as e:
        if \"provider\" in str(e):
            print(f\"❌ Provider key error still occurring: {e}\")
            return False
        else:
            print(f\"Different error (not provider related): {str(e)[:50]}\")
            return True

asyncio.run(test_no_provider_error())
"'"
```

## Expected Results
1. grep shows the fix is present
2. Router removes provider key from params
3. All utility keys are removed
4. No BadRequestError about provider key

## Success Criteria
- Fix is present in source code
- provider key not in API parameters
- Integration test completes without provider errors
