"""
Task 1 Verification: Test Core Utilities and Configuration

This script verifies that all Task 1 components work correctly together.
"""

import sys
import os
from pathlib import Path
from loguru import logger

# Test all Task 1 components
def test_task1_components():
    """Comprehensive test of Task 1 components."""
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Import and use logging setup
    total_tests += 1
    try:
        from llm_call.core.utils.logging_setup import setup_logging
        setup_logging(level="DEBUG")
        logger.debug("Debug message test")
        logger.info("Info message test")
        logger.success("✅ Logging setup works")
    except Exception as e:
        all_validation_failures.append(f"Logging setup failed: {e}")
    
    # Test 2: Import and use settings
    total_tests += 1
    try:
        from llm_call.core.config.settings import Settings, ClaudeProxySettings
        settings = Settings()
        assert settings.claude_proxy.port == 8001
        assert settings.retry.max_attempts == 3
        assert settings.llm.default_temperature == 0.1
        logger.success("✅ Settings models work correctly")
    except Exception as e:
        all_validation_failures.append(f"Settings test failed: {e}")
    
    # Test 3: Import and use config loader
    total_tests += 1
    try:
        from llm_call.core.config.loader import load_configuration
        config = load_configuration()
        assert hasattr(config, 'claude_proxy')
        assert hasattr(config, 'retry')
        assert hasattr(config, 'llm')
        logger.success("✅ Configuration loader works")
    except Exception as e:
        all_validation_failures.append(f"Config loader failed: {e}")
    
    # Test 4: Test core module initialization
    total_tests += 1
    try:
        import llm_call.core
        assert hasattr(llm_call.core, 'config')
        assert hasattr(llm_call.core, 'retry_with_validation')
        logger.success("✅ Core module initialization works")
    except Exception as e:
        all_validation_failures.append(f"Core module init failed: {e}")
    
    # Test 5: Verify POC compatibility
    total_tests += 1
    try:
        # Check that settings match POC expectations
        config = llm_call.core.config
        
        # From POC: POC_SERVER_HOST = "127.0.0.1", POC_SERVER_PORT = 8001
        assert config.claude_proxy.host == "127.0.0.1"
        assert config.claude_proxy.port == 8001
        
        # From POC: CLAUDE_CLI_PATH 
        assert config.claude_proxy.cli_path == "/home/graham/.nvm/versions/node/v22.15.0/bin/claude"
        
        # From POC: default temperature = 0.1, max_tokens = 250
        assert config.llm.default_temperature == 0.1
        assert config.llm.default_max_tokens == 250
        
        logger.success("✅ Configuration is POC-compatible")
    except Exception as e:
        all_validation_failures.append(f"POC compatibility check failed: {e}")
    
    # Test 6: Test environment variable override
    total_tests += 1
    try:
        # Set env vars
        os.environ["CLAUDE_PROXY_PORT"] = "8002"
        os.environ["LOG_LEVEL"] = "DEBUG"
        
        # Reload config
        from llm_call.core.config.loader import load_configuration
        new_config = load_configuration()
        
        assert new_config.claude_proxy.port == 8002
        assert new_config.log_level == "DEBUG"
        
        # Clean up
        os.environ.pop("CLAUDE_PROXY_PORT", None)
        os.environ.pop("LOG_LEVEL", None)
        
        logger.success("✅ Environment variable overrides work")
    except Exception as e:
        all_validation_failures.append(f"Env var override test failed: {e}")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        return False
    else:
        logger.success(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("Task 1 is complete and all components are working correctly")
        return True


if __name__ == "__main__":
    # Run comprehensive tests
    success = test_task1_components()
    
    if success:
        logger.info("\n" + "="*60)
        logger.success("TASK 1 COMPLETE: Core Utilities and Configuration")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info("  ✅ logging_setup.py created and tested")
        logger.info("  ✅ settings.py created with Pydantic v2 models")
        logger.info("  ✅ loader.py created with env/file loading")
        logger.info("  ✅ core/__init__.py updated with initialization")
        logger.info("  ✅ All components are POC-compatible")
        sys.exit(0)
    else:
        sys.exit(1)