#!/usr/bin/env python3
"""
POC-4: Test error handling for invalid models

Purpose:
    Demonstrates error handling for routing failures.
    Tests invalid models, missing configurations, and edge cases.

Links:
    - Error Handling Best Practices: https://docs.python.org/3/tutorial/errors.html
    - LiteLLM Error Types: https://docs.litellm.ai/docs/exception_handling

Sample Input:
    model: "invalid/model"
    messages: [{"role": "user", "content": "Test"}]

Expected Output:
    Clear error messages and graceful failure handling

Author: Task 004 Implementation
"""

import json
import time
from typing import Dict, Any, Tuple, Optional
from loguru import logger
from enum import Enum

# Configure logger
logger.add("poc_04_routing_errors.log", rotation="10 MB")


class RoutingError(Exception):
    """Custom exception for routing errors."""
    pass


class ErrorType(Enum):
    """Types of routing errors."""
    INVALID_MODEL = "invalid_model"
    MISSING_CONFIG = "missing_config"
    INVALID_FORMAT = "invalid_format"
    PROVIDER_ERROR = "provider_error"
    UNKNOWN = "unknown"


def detect_error_type(error: Exception) -> ErrorType:
    """
    Detect the type of error for better handling.
    
    Args:
        error: The exception that occurred
        
    Returns:
        ErrorType enum value
    """
    error_msg = str(error).lower()
    
    if "model" in error_msg:
        return ErrorType.INVALID_MODEL
    elif "config" in error_msg or "missing" in error_msg:
        return ErrorType.MISSING_CONFIG
    elif "format" in error_msg or "type" in error_msg:
        return ErrorType.INVALID_FORMAT
    elif "provider" in error_msg or "api" in error_msg:
        return ErrorType.PROVIDER_ERROR
    else:
        return ErrorType.UNKNOWN


def validate_model_name(model: str) -> Tuple[bool, Optional[str]]:
    """
    Validate model name format and known patterns.
    
    Args:
        model: Model name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not model:
        return False, "Model name cannot be empty"
    
    if not isinstance(model, str):
        return False, f"Model name must be a string, got {type(model).__name__}"
    
    # Check for common typos and issues
    if model.count("/") > 1:
        return False, "Model name should have at most one '/' separator"
    
    if model.startswith("/") or model.endswith("/"):
        return False, "Model name cannot start or end with '/'"
    
    if " " in model:
        return False, "Model name cannot contain spaces"
    
    # Check for known invalid patterns
    invalid_patterns = [
        "test/test",  # Common test pattern that should fail
        "unknown/unknown",  # Explicitly unknown
        "../",  # Path traversal attempt
        "\\",  # Windows path separator
    ]
    
    for pattern in invalid_patterns:
        if pattern in model:
            return False, f"Model name contains invalid pattern: {pattern}"
    
    return True, None


def handle_routing_error(
    config: Dict[str, Any], 
    error: Exception,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Handle routing errors with detailed information.
    
    Args:
        config: Original configuration that caused the error
        error: The exception that occurred
        context: Additional context information
        
    Returns:
        Error response with details
    """
    error_type = detect_error_type(error)
    
    error_response = {
        "error": True,
        "error_type": error_type.value,
        "error_message": str(error),
        "model": config.get("model", "unknown"),
        "timestamp": time.time(),
        "suggestions": []
    }
    
    # Add specific suggestions based on error type
    if error_type == ErrorType.INVALID_MODEL:
        error_response["suggestions"] = [
            "Check model name spelling",
            "Use format: provider/model-name",
            "Valid providers: openai, vertex_ai, anthropic, max"
        ]
    elif error_type == ErrorType.MISSING_CONFIG:
        error_response["suggestions"] = [
            "Ensure 'model' field is present",
            "Check for required API keys in environment",
            "Verify configuration structure"
        ]
    elif error_type == ErrorType.INVALID_FORMAT:
        error_response["suggestions"] = [
            "Check message format",
            "Ensure content is properly structured",
            "Validate JSON syntax"
        ]
    
    # Add context if provided
    if context:
        error_response["context"] = context
    
    # Log the error
    logger.error(f"Routing error: {error_type.value}")
    logger.error(f"Details: {error}")
    logger.debug(f"Config: {json.dumps(config, indent=2)}")
    
    return error_response


def safe_route_with_fallback(
    config: Dict[str, Any],
    fallback_model: Optional[str] = "openai/gpt-3.5-turbo"
) -> Tuple[bool, Dict[str, Any]]:
    """
    Attempt routing with fallback option.
    
    Args:
        config: Configuration to route
        fallback_model: Model to use if primary fails
        
    Returns:
        Tuple of (success, result_config_or_error)
    """
    original_model = config.get("model", "")
    
    # First, validate the model name
    is_valid, error_msg = validate_model_name(original_model)
    
    if not is_valid:
        # Try fallback if available
        if fallback_model and fallback_model != original_model:
            logger.warning(f"Model validation failed: {error_msg}")
            logger.info(f"Attempting fallback to: {fallback_model}")
            
            fallback_config = config.copy()
            fallback_config["model"] = fallback_model
            fallback_config["_original_model"] = original_model
            fallback_config["_fallback_used"] = True
            
            # Validate fallback
            fb_valid, fb_error = validate_model_name(fallback_model)
            if fb_valid:
                return True, fallback_config
            else:
                error = RoutingError(f"Both primary and fallback models invalid: {error_msg}, {fb_error}")
                return False, handle_routing_error(config, error)
        else:
            error = RoutingError(f"Model validation failed: {error_msg}")
            return False, handle_routing_error(config, error)
    
    # Model is valid, proceed with routing
    return True, config


def test_error_handling():
    """Test various error handling scenarios."""
    
    test_cases = [
        {
            "name": "Empty model name",
            "config": {"model": "", "messages": [{"role": "user", "content": "Test"}]},
            "expect_error": True,
            "error_type": ErrorType.INVALID_MODEL
        },
        {
            "name": "Invalid model format",
            "config": {"model": "provider/model/extra", "messages": [{"role": "user", "content": "Test"}]},
            "expect_error": True,
            "error_type": ErrorType.INVALID_MODEL
        },
        {
            "name": "Model with spaces",
            "config": {"model": "open ai/gpt 4", "messages": [{"role": "user", "content": "Test"}]},
            "expect_error": True,
            "error_type": ErrorType.INVALID_MODEL
        },
        {
            "name": "Path traversal attempt",
            "config": {"model": "../../../etc/passwd", "messages": [{"role": "user", "content": "Test"}]},
            "expect_error": True,
            "error_type": ErrorType.INVALID_MODEL
        },
        {
            "name": "Valid model with fallback",
            "config": {"model": "unknown/invalid", "messages": [{"role": "user", "content": "Test"}]},
            "expect_error": False,  # Fallback should work
            "with_fallback": True
        },
        {
            "name": "Missing model field",
            "config": {"messages": [{"role": "user", "content": "Test"}]},
            "expect_error": True,
            "error_type": ErrorType.INVALID_MODEL
        },
        {
            "name": "Non-string model",
            "config": {"model": 123, "messages": [{"role": "user", "content": "Test"}]},
            "expect_error": True,
            "error_type": ErrorType.INVALID_MODEL
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("="*50)
        
        try:
            config = test_case["config"]
            use_fallback = test_case.get("with_fallback", False)
            
            if use_fallback:
                success, result = safe_route_with_fallback(config)
            else:
                success, result = safe_route_with_fallback(config, fallback_model=None)
            
            # Check expectations
            if test_case["expect_error"]:
                if success:
                    logger.error(f"❌ Expected error but got success")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected error"})
                elif result.get("error_type") != test_case.get("error_type", "").value:
                    logger.error(f"❌ Wrong error type: expected {test_case.get('error_type', '')}, got {result.get('error_type')}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Wrong error type"})
                else:
                    logger.success(f"✅ Correctly handled error: {result['error_type']}")
                    logger.info(f"   Suggestions: {result.get('suggestions', [])}")
                    results.append({"test": test_case["name"], "passed": True})
            else:
                if not success:
                    logger.error(f"❌ Expected success but got error: {result.get('error_message')}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected success"})
                else:
                    if use_fallback and result.get("_fallback_used"):
                        logger.success(f"✅ Successfully used fallback model")
                    else:
                        logger.success(f"✅ Routing succeeded")
                    results.append({"test": test_case["name"], "passed": True})
            
        except Exception as e:
            logger.exception(f"Unexpected error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("ERROR HANDLING TEST SUMMARY")
    logger.info("="*50)
    
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    
    logger.info(f"Total: {passed}/{total} tests passed")
    
    for result in results:
        status = "✅" if result["passed"] else "❌"
        logger.info(f"{status} {result['test']}")
        if not result["passed"] and "reason" in result:
            logger.info(f"   Reason: {result['reason']}")
    
    return passed == total


if __name__ == "__main__":
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Error handling scenarios
    total_tests += 1
    try:
        if not test_error_handling():
            all_validation_failures.append("Error handling tests failed")
    except Exception as e:
        all_validation_failures.append(f"Error handling test exception: {str(e)}")
    
    # Test 2: Error type detection
    total_tests += 1
    error_detection_tests = [
        (Exception("Invalid model: xyz"), ErrorType.INVALID_MODEL),
        (Exception("Missing configuration"), ErrorType.MISSING_CONFIG),
        (Exception("Invalid format for field"), ErrorType.INVALID_FORMAT),
        (Exception("API provider error"), ErrorType.PROVIDER_ERROR),
        (Exception("Something else"), ErrorType.UNKNOWN),
    ]
    
    for error, expected_type in error_detection_tests:
        detected = detect_error_type(error)
        if detected != expected_type:
            all_validation_failures.append(
                f"Error type detection failed: {error} -> expected {expected_type}, got {detected}"
            )
    
    # Test 3: Model validation edge cases
    total_tests += 1
    validation_tests = [
        ("valid/model", True),
        ("openai/gpt-4", True),
        ("max/claude", True),
        ("", False),
        ("/invalid", False),
        ("invalid/", False),
        ("too/many/slashes", False),
        ("has spaces", False),
        ("test/test", False),
        ("../../../etc", False),
    ]
    
    for model, expected_valid in validation_tests:
        is_valid, _ = validate_model_name(model)
        if is_valid != expected_valid:
            all_validation_failures.append(
                f"Model validation failed: '{model}' -> expected valid={expected_valid}, got {is_valid}"
            )
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-4 Routing error handling is validated and ready")
        sys.exit(0)