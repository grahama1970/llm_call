#!/usr/bin/env python3
"""POC: Test ModelResponse serialization for SQLite storage"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=== POC: ModelResponse Serialization ===")

# Test 1: Understand ModelResponse structure
print("\nTest 1: ModelResponse structure")
try:
    from litellm.types.utils import ModelResponse
    from litellm import completion
    
    # Create a mock ModelResponse to understand its structure
    # First, let's see what attributes it has
    print("Creating a sample ModelResponse...")
    
    # Make a simple call to get a real ModelResponse
    response = completion(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Say hello"}],
        mock_response="Hello!"  # Use mock to avoid API call
    )
    
    print(f"Response type: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    
    # Test different serialization methods
    print("\nTest 2: Serialization methods")
    
    # Method 1: model_dump_json (Pydantic v2)
    if hasattr(response, 'model_dump_json'):
        print("✓ Has model_dump_json method")
        json_str = response.model_dump_json()
        data = json.loads(json_str)
        print(f"  Serialized keys: {list(data.keys())[:5]}...")
    
    # Method 2: dict() (Pydantic v1)  
    elif hasattr(response, 'dict'):
        print("✓ Has dict method")
        data = response.dict()
        print(f"  Dict keys: {list(data.keys())[:5]}...")
    
    # Method 3: __dict__
    elif hasattr(response, '__dict__'):
        print("✓ Has __dict__ attribute")
        data = response.__dict__
        print(f"  Dict keys: {list(data.keys())[:5]}...")
    
    else:
        print("✗ No standard serialization method found")
        
    # Test JSON serialization
    print("\nTest 3: JSON serialization")
    try:
        json_str = json.dumps(data)
        print(f"✓ Successfully serialized to JSON ({len(json_str)} chars)")
        
        # Test deserialization
        loaded = json.loads(json_str)
        print(f"✓ Successfully deserialized from JSON")
        if 'choices' in loaded and loaded['choices']:
            content = loaded['choices'][0].get('message', {}).get('content', 'N/A')
            print(f"  Content: {content}")
    except Exception as e:
        print(f"✗ JSON serialization failed: {e}")

except ImportError as e:
    print(f"✗ Import error: {e}")
    print("  Make sure litellm is installed: uv add litellm")
except Exception as e:
    print(f"✗ Unexpected error: {type(e).__name__}: {e}")

print("\n=== POC Complete ===")
