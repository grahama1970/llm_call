"""
Verification module for validating test outputs from Claude Code

This module provides tools to verify test results externally since
Claude Code has a tendency to hallucinate test success.
"""

from .simple_verifier import (
    verify_simple,
    verify_with_gemini,
    extract_raw_results,
    save_verification_report
)

from .verification_workflow import (
    run_and_verify,
    verify_claude_output,
    run_tests
)

__all__ = [
    'verify_simple',
    'verify_with_gemini', 
    'extract_raw_results',
    'save_verification_report',
    'run_and_verify',
    'verify_claude_output',
    'run_tests'
]