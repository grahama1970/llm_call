# JWT Clock Skew Solutions for LiteLLM

## Problem Description

When using LiteLLM with Vertex AI (Google Cloud), JWT signature validation fails when the system clock is incorrect. The error typically appears as:

```
JWT signature error (system time is 2025 instead of 2024)
```

This occurs because JWT tokens include timestamp claims (`iat`, `exp`, `nbf`) that are validated against the current system time.

## Root Cause

Google's authentication library (`google-auth-library-python`) previously allowed a 10-second clock skew tolerance but reduced it to 0 seconds in version 2.1.0 (PR #858). This makes the authentication very sensitive to time differences between client and server.

## Practical Solutions

### 1. Fix System Time (Recommended)

The most reliable solution is to ensure your system clock is correctly synchronized:

#### Linux/Mac:
```bash
# Manual time sync
sudo ntpdate -s time.google.com

# Or set specific date/time
sudo date -s '2024-12-08 16:00:00'

# Enable automatic NTP sync
sudo timedatectl set-ntp true
```

#### Windows:
- Open Settings → Time & Language → Date & time
- Enable "Set time automatically"
- Enable "Set time zone automatically"

### 2. Use Service Account JSON Directly

Instead of relying on Application Default Credentials (ADC), you can explicitly provide service account credentials:

```python
from litellm import completion
import json
import os

# Method 1: Set environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/vertex_ai_service_account.json'

# Method 2: Pass credentials directly
with open('/path/to/vertex_ai_service_account.json', 'r') as file:
    vertex_credentials = json.load(file)

response = await completion(
    model="vertex_ai/gemini-2.5-flash-preview-05-20",
    messages=[{"role": "user", "content": "Hello"}],
    vertex_credentials=json.dumps(vertex_credentials)  # Pass as JSON string
)
```

### 3. Alternative Authentication Methods

#### Use Google Cloud SDK Authentication:
```bash
# Login with gcloud (creates ADC)
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

#### Use Workload Identity Federation (for production):
This is Google's recommended approach for authentication from outside Google Cloud, as it doesn't require service account keys.

### 4. LiteLLM-Specific Workarounds

#### Environment Variables:
```bash
# In .env file
GOOGLE_APPLICATION_CREDENTIALS=/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json
LITELLM_VERTEX_PROJECT=your-project-id
LITELLM_VERTEX_LOCATION=us-central1
```

#### Proxy Configuration:
If using LiteLLM proxy, you can configure authentication in the proxy config:

```yaml
model_list:
  - model_name: gemini
    litellm_params:
      model: vertex_ai/gemini-2.5-flash-preview-05-20
      vertex_project: your-project-id
      vertex_location: us-central1
      vertex_credentials: /path/to/service-account.json
```

### 5. Code-Level Workarounds

#### Retry with Time Adjustment:
```python
import time
from datetime import datetime
import subprocess

async def call_with_time_sync(model, messages):
    try:
        return await completion(model=model, messages=messages)
    except Exception as e:
        if "JWT" in str(e) or "token" in str(e).lower():
            # Attempt to sync time
            try:
                subprocess.run(['sudo', 'ntpdate', '-s', 'time.google.com'], 
                             capture_output=True, check=False)
                # Retry after sync
                return await completion(model=model, messages=messages)
            except:
                raise e
        raise e
```

### 6. Use Alternative Providers

If clock sync is not possible, consider using providers that don't rely on JWT time validation:

```python
# Use OpenAI instead
response = await completion(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello"}]
)

# Use Anthropic
response = await completion(
    model="claude-3-opus",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## Current Status

Based on the codebase analysis:

1. **No Built-in Clock Skew Configuration**: LiteLLM doesn't currently expose configuration options to adjust JWT clock skew tolerance.

2. **Service Account JSON Available**: The project already has a service account file at `/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json`

3. **Environment Configuration**: The `.env` file is already configured with:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json
   LITELLM_VERTEX_LOCATION=us-central1
   LITELLM_VERTEX_PROJECT=gen-lang-client-0870473940
   ```

## Recommendations

1. **Immediate Fix**: Sync system time using NTP
2. **Long-term Solution**: Set up automatic time synchronization
3. **Fallback**: Use explicit service account credentials instead of ADC
4. **Consider**: Opening an issue with LiteLLM to request configurable clock skew tolerance

## References

- [Google Auth Library Clock Skew PR #858](https://github.com/googleapis/google-auth-library-python/pull/858)
- [LiteLLM Vertex AI Documentation](https://docs.litellm.ai/docs/providers/vertex)
- [Google Cloud Authentication Best Practices](https://cloud.google.com/docs/authentication/best-practices)