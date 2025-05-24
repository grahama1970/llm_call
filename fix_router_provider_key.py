#!/usr/bin/env python3
"""
Fix the router to remove 'provider' key from API parameters
"""

import fileinput
import sys

# Read the router.py file
with open('src/llm_call/core/router.py', 'r') as f:
    content = f.read()

# Find the section where utility keys are removed
old_section = '''        # Remove utility keys not meant for LiteLLM (from POC)
        api_params.pop("image_directory", None)
        api_params.pop("max_image_size_kb", None)
        api_params.pop("vertex_credentials_path", None)
        api_params.pop("retry_config", None)  # Remove retry config
        api_params.pop("skip_claude_multimodal", None)  # Remove internal flag'''

new_section = '''        # Remove utility keys not meant for LiteLLM (from POC)
        api_params.pop("image_directory", None)
        api_params.pop("max_image_size_kb", None)
        api_params.pop("vertex_credentials_path", None)
        api_params.pop("retry_config", None)  # Remove retry config
        api_params.pop("skip_claude_multimodal", None)  # Remove internal flag
        api_params.pop("provider", None)  # Remove provider key - not an API param'''

# Replace the content
content = content.replace(old_section, new_section)

# Write back to file
with open('src/llm_call/core/router.py', 'w') as f:
    f.write(content)

print("✅ Fixed router.py to remove 'provider' key from API parameters")
