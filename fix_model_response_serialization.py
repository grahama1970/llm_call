#!/usr/bin/env python3
"""Fix ModelResponse serialization"""

import sys
from pathlib import Path

# Read the file
file_path = Path('src/llm_call/proof_of_concept/v4_claude_validator/litellm_client_poc_async.py')
content = file_path.read_text()

# Replace the executor setup with proper serialization handling
old_executor = '''async def clean_executor(config):
            # Remove custom polling parameters before calling original
            clean_config = {k: v for k, v in config.items() 
                           if k not in ['polling', 'wait_for_completion', 'timeout']}
            return await original_llm_call(clean_config)
        _polling_manager.set_executor(clean_executor)'''

new_executor = '''async def clean_executor(config):
            # Remove custom polling parameters before calling original
            clean_config = {k: v for k, v in config.items() 
                           if k not in ['polling', 'wait_for_completion', 'timeout']}
            result = await original_llm_call(clean_config)
            
            # Convert ModelResponse to dict for JSON serialization
            if hasattr(result, 'model_dump_json'):
                # Use pydantic v2 method if available
                import json
                return json.loads(result.model_dump_json())
            elif hasattr(result, 'dict'):
                # Use pydantic v1 method
                return result.dict()
            elif hasattr(result, '__dict__'):
                # Fallback to dict conversion
                return result.__dict__
            else:
                # Already a dict or basic type
                return result
                
        _polling_manager.set_executor(clean_executor)'''

content = content.replace(old_executor, new_executor)

# Write back
file_path.write_text(content)
print("Fixed ModelResponse serialization")
