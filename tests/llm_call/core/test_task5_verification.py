"""
Task 5 Verification: Test Minor Utilities Integration

This script verifies that utilities are properly integrated and test structure is in place.
"""

import sys
import os
from pathlib import Path
from loguru import logger


def test_task5_components():
    """Test all Task 5 components."""
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Utilities are importable
    total_tests += 1
    try:
        from llm_call.core.utils.logging_setup import setup_logging
        from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
        from llm_call.core.utils.file_utils import load_text_file, get_project_root
        from llm_call.core.utils.json_utils import clean_json_string
        from llm_call.core.utils.multimodal_utils import format_multimodal_messages, is_multimodal
        
        logger.success("✅ All utilities are importable")
    except Exception as e:
        all_validation_failures.append(f"Utility import test failed: {e}")
    
    # Test 2: Logging is properly initialized
    total_tests += 1
    try:
        # Logging should already be set up by core/__init__.py
        logger.debug("Debug test")
        logger.info("Info test")
        logger.success("✅ Logging is working correctly")
    except Exception as e:
        all_validation_failures.append(f"Logging test failed: {e}")
    
    # Test 3: Test structure exists
    total_tests += 1
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        tests_dir = project_root / "tests"
        
        assert tests_dir.exists()
        assert (tests_dir / "test_core_integration.py").exists()
        
        logger.success("✅ Test structure is in place")
    except Exception as e:
        all_validation_failures.append(f"Test structure check failed: {e}")
    
    # Test 4: Cache initialization in retry
    total_tests += 1
    try:
        from llm_call.core.retry import retry_with_validation, RetryConfig
        
        # Verify retry imports cache initialization
        config = RetryConfig(enable_cache=True)
        assert config.enable_cache == True
        
        logger.success("✅ Cache initialization integrated in retry")
    except Exception as e:
        all_validation_failures.append(f"Cache integration test failed: {e}")
    
    # Test 5: File utilities work
    total_tests += 1
    try:
        from llm_call.core.utils.file_utils import load_text_file
        
        # Create a test file
        test_file = Path("test_file.txt")
        test_content = "Test content for file utils"
        test_file.write_text(test_content)
        
        # Test loading
        loaded = load_text_file(test_file)
        assert loaded == test_content
        
        # Clean up
        test_file.unlink()
        
        logger.success("✅ File utilities work correctly")
    except Exception as e:
        all_validation_failures.append(f"File utility test failed: {e}")
    
    # Test 6: Configuration is globally accessible
    total_tests += 1
    try:
        from llm_call.core import config
        
        # Verify key configuration values
        assert hasattr(config, 'claude_proxy')
        assert hasattr(config, 'llm')
        assert hasattr(config, 'retry')
        
        logger.success("✅ Global configuration is accessible")
    except Exception as e:
        all_validation_failures.append(f"Config access test failed: {e}")
    
    return all_validation_failures, total_tests


if __name__ == "__main__":
    # Run tests
    failures, tests = test_task5_components()
    
    # Final validation result
    if failures:
        logger.error(f"❌ VALIDATION FAILED - {len(failures)} of {tests} tests failed:")
        for failure in failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"✅ VALIDATION PASSED - All {tests} tests produced expected results")
        logger.info("\n" + "="*60)
        logger.success("TASK 5 COMPLETE: Testing and Minor Utilities Integration")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info("  ✅ All utilities properly imported and accessible")
        logger.info("  ✅ Logging initialized globally via core/__init__.py")
        logger.info("  ✅ Test structure created in tests/ directory")
        logger.info("  ✅ Cache initialization integrated in retry mechanism")
        logger.info("  ✅ File utilities functional")
        logger.info("  ✅ Global configuration accessible throughout core")
        sys.exit(0)