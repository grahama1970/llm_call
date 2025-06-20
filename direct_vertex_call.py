#!/usr/bin/env python3
"""
Direct Vertex AI call - no dependencies, just pure API
"""

import json
import os
from google.oauth2 import service_account
import google.auth.transport.requests

# Load credentials with proper scope
creds_path = "/home/graham/workspace/experiments/llm_call/config/vertex_ai_service_account.json"
credentials = service_account.Credentials.from_service_account_file(
    creds_path,
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)

# Create auth request
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)

# Build the request
project_id = "gen-lang-client-0870473940"
location = "us-central1"
model = "gemini-2.5-flash-preview-05-20"

url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent"

# Read the verification script
with open('verification_experiments/proper_verification.py', 'r') as f:
    script_content = f.read()

# Create the request body
data = {
    "contents": [{
        "role": "user",
        "parts": [{
            "text": f"""Please critique this verification approach for detecting when Claude Code fakes test results:

{script_content[:6000]}

Focus on:
1. Is Ollama with qwen2.5:32b effective for detecting fake implementations?
2. Are the test cases good examples?
3. What edge cases might this miss?
4. Any improvements to suggest?

Be concise but thorough."""
        }]
    }],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 2048
    }
}

# Make the request with urllib
import urllib.request
import urllib.error

headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(url, 
                           data=json.dumps(data).encode('utf-8'),
                           headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        
    # Extract the text
    if "candidates" in result and result["candidates"]:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        print("="*80)
        print("GEMINI CRITIQUE:")
        print("="*80)
        print(text)
    else:
        print("No response from Gemini")
        print(json.dumps(result, indent=2))
        
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.reason}")
    print(e.read().decode())