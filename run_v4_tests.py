#!/usr/bin/env python3
"""Run v4 validation tests using absolute imports."""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import the test runner
from src.llm_call.proof_of_concept.run_v4_tests_essential import main

if __name__ == "__main__":
    main()