#!/usr/bin/env python3
"""Fix the async implementation to clean parameters"""

import sys
from pathlib import Path

# Read the file
file_path = Path('src/llm_call/proof_of_concept/v4_claude_validator/litellm_client_poc_async.py')
content = file_path.read_text()

# Find the llm_call function and add parameter cleaning
new_content = content.replace(
    'if not use_polling:\n        # Direct call - wait for completion\n        return await original_llm_call(llm_config_input)',
    '''if not use_polling:
        # Direct call - wait for completion
        # Clean config by removing custom parameters
        clean_config = {k: v for k, v in llm_config_input.items() 
                       if k not in ['polling', 'wait_for_completion', 'timeout']}
        return await original_llm_call(clean_config)'''
)

# Also fix the executor to clean parameters
new_content = new_content.replace(
    '_polling_manager.set_executor(original_llm_call)',
    '''async def clean_executor(config):
            # Remove custom polling parameters before calling original
            clean_config = {k: v for k, v in config.items() 
                           if k not in ['polling', 'wait_for_completion', 'timeout']}
            return await original_llm_call(clean_config)
        _polling_manager.set_executor(clean_executor)'''
)

# Write back
file_path.write_text(new_content)
print("Fixed async parameter handling")
