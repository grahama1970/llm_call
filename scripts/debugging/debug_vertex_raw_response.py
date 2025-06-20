#!/usr/bin/env python3
"""
Debug the raw Vertex AI response to understand why content is missing.
"""

import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

# Set up credentials
service_account_path = "/home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json"
credentials = service_account.Credentials.from_service_account_file(service_account_path)

# Initialize Vertex AI
with open(service_account_path) as f:
    service_account_info = json.load(f)
    project_id = service_account_info.get("project_id")

vertexai.init(project=project_id, credentials=credentials, location="us-central1")

# Create model
model = GenerativeModel("gemini-2.5-flash-preview-05-20")

# Simple test
print("Testing direct Vertex AI call...")
response = model.generate_content(
    "What is 2+2? Reply in exactly 5 words.",
    generation_config={
        "temperature": 0.1,
        "max_output_tokens": 100
    }
)

print(f"\nResponse type: {type(response)}")
print(f"Response: {response}")

if hasattr(response, 'text'):
    print(f"\nText: {response.text}")
    
if hasattr(response, 'candidates'):
    print(f"\nCandidates: {response.candidates}")
    for i, candidate in enumerate(response.candidates):
        print(f"\nCandidate {i}:")
        if hasattr(candidate, 'content'):
            print(f"  Content: {candidate.content}")
            if hasattr(candidate.content, 'parts'):
                for j, part in enumerate(candidate.content.parts):
                    print(f"    Part {j}: {part}")
                    if hasattr(part, 'text'):
                        print(f"      Text: {part.text}")

# Try with a different approach
print("\n" + "="*60)
print("Testing with thinking disabled...")

response2 = model.generate_content(
    "What is 2+2? Answer: ",
    generation_config={
        "temperature": 0,
        "max_output_tokens": 10,
        "top_k": 1
    }
)

print(f"\nResponse 2 text: {response2.text if hasattr(response2, 'text') else 'NO TEXT'}")

# Test with explicit instruction
print("\n" + "="*60)
print("Testing with explicit output instruction...")

response3 = model.generate_content(
    "Complete this sentence with exactly one word. The answer to 2+2 is ",
    generation_config={
        "temperature": 0,
        "max_output_tokens": 5,
        "top_k": 1
    }
)

print(f"\nResponse 3 text: {response3.text if hasattr(response3, 'text') else 'NO TEXT'}")