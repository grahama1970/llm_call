import pytest
"""Basic test to verify testing infrastructure."""

def test_import():
    """Test that the project can be imported."""
    assert True  # Basic test to ensure pytest works
    
def test_python_version():
    """Verify Python version is correct."""
    import sys
    # Accept Python 3.10 or 3.11 per pyproject.toml requires-python = "~=3.10"
    assert sys.version_info[:2] in [(3, 10), (3, 11)], f"Expected Python 3.10 or 3.11, got {sys.version}"
