"""
Module: test_imports.py
Description: Test suite for imports functionality

Sample Input:
>>> # See function docstrings for specific examples

Expected Output:
>>> # See function docstrings for expected results

Example Usage:
>>> # Import and use as needed based on module functionality
"""

# llm_call/test_import.py
import os
import sys
from pathlib import Path

print(f"--- Current Working Directory: {Path.cwd()} ---")
print(f"--- Script Path: {Path(__file__).resolve()} ---")

try:
    from dotenv import load_dotenv
    # Explicitly point to the .env file in the current directory (project root)
    dotenv_path = Path(__file__).resolve().parent / '.env' # Assuming test_import.py is in project root
    if dotenv_path.is_file():
        loaded = load_dotenv(dotenv_path=dotenv_path, override=True) 
        print(f"--- .env loaded from {dotenv_path}: {loaded} ---")
        # Verify PYTHONPATH immediately after loading
        print(f"--- os.environ.get('PYTHONPATH') AFTER load_dotenv: {os.environ.get('PYTHONPATH')} ---")
    else:
        print(f"--- .env file not found at {dotenv_path} ---")
except ImportError:
    print("--- python-dotenv not found. Skipping load_dotenv(). ---")
    print(f"--- os.environ.get('PYTHONPATH') (dotenv not loaded): {os.environ.get('PYTHONPATH')} ---")


print(f"--- sys.path entries (full list): ---")
for i, p_item in enumerate(sys.path):
    print(f"    {i}: {p_item}")


print("\n--- Attempting import 'llm_call'... ---")
try:
    import llm_call
    print(f"SUCCESS: `import llm_call` worked.")
    print(f"Location of imported llm_call: {getattr(llm_call, '__file__', 'N/A (namespace package?)')}")
    print(f"llm_call package paths: {getattr(llm_call, '__path__', 'N/A')}")

    print("\n--- Attempting import 'llm_call.core.utils.json_utils'... ---")
    from llm_call.core.utils import json_utils 
    print(f"SUCCESS: `from llm_call.core.utils import json_utils` worked.")
    print(f"Location of imported json_utils: {getattr(json_utils, '__file__', 'N/A')}")

    print("\n--- Attempting import 'clean_json_string' from 'llm_call.core.utils.json_utils'... ---")
    from llm_call.core.utils.json_utils import clean_json_string
    print(f"SUCCESS: `from llm_call.core.utils.json_utils import clean_json_string` worked.")
    print(f"clean_json_string type: {type(clean_json_string)}")

except ModuleNotFoundError as e:
    print(f"ERROR: ModuleNotFoundError: {e}")
except ImportError as e:
    print(f"ERROR: ImportError: {e}")
except Exception as e:
    print(f"ERROR: An unexpected error occurred: {e}")
    import traceback
    traceback.print_exc()