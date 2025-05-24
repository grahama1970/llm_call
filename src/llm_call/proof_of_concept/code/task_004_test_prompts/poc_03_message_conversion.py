#!/usr/bin/env python3
"""
POC-3: Test message format conversion

Purpose:
    Demonstrates conversion between different message formats.
    Handles question -> messages, multimodal content, and role mappings.

Links:
    - OpenAI Message Format: https://platform.openai.com/docs/api-reference/chat
    - Anthropic Message Format: https://docs.anthropic.com/claude/reference/messages

Sample Input:
    question: "What is AI?"
    OR
    messages: [{"role": "user", "content": [{"type": "text", "text": "..."}]}]

Expected Output:
    Standardized messages array with proper role and content structure

Author: Task 004 Implementation
"""

import json
import copy
from typing import Dict, Any, List, Union, Tuple, Optional
from loguru import logger

# Configure logger
logger.add("poc_03_message_conversion.log", rotation="10 MB")


def convert_question_to_messages(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert question format to messages format.
    
    Args:
        config: Configuration with possible 'question' field
        
    Returns:
        Config with standardized messages format
    """
    result = config.copy()
    
    if "question" in result and "messages" not in result:
        result["messages"] = [
            {"role": "user", "content": result["question"]}
        ]
        del result["question"]
        logger.debug("Converted 'question' to 'messages' format")
    
    return result


def normalize_content_format(content: Union[str, List[Dict], Dict]) -> Union[str, List[Dict]]:
    """
    Normalize content to either string or list of content parts.
    
    Args:
        content: Content in various formats
        
    Returns:
        Normalized content
    """
    # Already a string
    if isinstance(content, str):
        return content
    
    # Single content part dict (e.g., {"type": "text", "text": "..."})
    if isinstance(content, dict):
        return [content]
    
    # Already a list
    if isinstance(content, list):
        return content
    
    # Unknown format
    logger.warning(f"Unknown content format: {type(content)}")
    return str(content)


def convert_multimodal_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert multimodal message formats.
    
    Handles:
    - OpenAI style: content as list of {type, text/image_url}
    - Anthropic style: content as string or list
    - Mixed formats
    
    Args:
        message: Single message dict
        
    Returns:
        Message with normalized content
    """
    result = message.copy()
    
    if "content" in result:
        result["content"] = normalize_content_format(result["content"])
    
    return result


def convert_message_roles(messages: List[Dict[str, Any]], target_format: str = "openai") -> List[Dict[str, Any]]:
    """
    Convert message roles between different formats.
    
    Args:
        messages: List of messages
        target_format: "openai" or "anthropic"
        
    Returns:
        Messages with converted roles
    """
    result = []
    
    for msg in messages:
        new_msg = msg.copy()
        
        # Handle role conversions
        if target_format == "anthropic":
            # OpenAI -> Anthropic role mapping
            if new_msg.get("role") == "system":
                # Anthropic doesn't have system role in messages
                # Convert to user message with system prefix
                new_msg["role"] = "user"
                content = new_msg.get("content", "")
                if isinstance(content, str):
                    new_msg["content"] = f"[System]: {content}"
                logger.debug("Converted system role to user role for Anthropic")
        
        result.append(new_msg)
    
    return result


def validate_message_format(messages: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
    """
    Validate message format correctness.
    
    Args:
        messages: List of messages to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(messages, list):
        return False, "Messages must be a list"
    
    if len(messages) == 0:
        return False, "Messages list cannot be empty"
    
    valid_roles = {"system", "user", "assistant", "function", "tool"}
    
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return False, f"Message {i} must be a dict"
        
        if "role" not in msg:
            return False, f"Message {i} missing 'role' field"
        
        if msg["role"] not in valid_roles:
            return False, f"Message {i} has invalid role: {msg['role']}"
        
        if "content" not in msg:
            return False, f"Message {i} missing 'content' field"
        
        # Validate multimodal content structure
        content = msg["content"]
        if isinstance(content, list):
            for j, part in enumerate(content):
                if not isinstance(part, dict):
                    return False, f"Message {i} content part {j} must be a dict"
                
                if "type" not in part:
                    return False, f"Message {i} content part {j} missing 'type' field"
                
                if part["type"] == "text" and "text" not in part:
                    return False, f"Message {i} content part {j} of type 'text' missing 'text' field"
                
                if part["type"] == "image_url" and "image_url" not in part:
                    return False, f"Message {i} content part {j} of type 'image_url' missing 'image_url' field"
    
    return True, None


def full_message_conversion_pipeline(config: Dict[str, Any], target_format: str = "openai") -> Dict[str, Any]:
    """
    Full conversion pipeline for message formats.
    
    Args:
        config: Original configuration
        target_format: Target format for conversion
        
    Returns:
        Fully converted configuration
    """
    # Step 1: Convert question to messages
    result = convert_question_to_messages(config)
    
    # Step 2: Normalize multimodal content
    if "messages" in result:
        result["messages"] = [
            convert_multimodal_message(msg) 
            for msg in result["messages"]
        ]
    
    # Step 3: Convert roles if needed
    if "messages" in result and target_format:
        result["messages"] = convert_message_roles(result["messages"], target_format)
    
    # Step 4: Validate final format
    if "messages" in result:
        is_valid, error = validate_message_format(result["messages"])
        if not is_valid:
            logger.error(f"Message validation failed: {error}")
            result["_validation_error"] = error
    
    return result


def test_message_conversions():
    """Test various message format conversions."""
    
    test_cases = [
        {
            "name": "Simple question to messages",
            "input": {
                "model": "gpt-4",
                "question": "What is machine learning?"
            },
            "expected_messages": 1,
            "expected_first_role": "user",
            "expected_first_content": "What is machine learning?"
        },
        {
            "name": "Multimodal content normalization",
            "input": {
                "model": "gpt-4-vision",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What's in this image?"},
                        {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
                    ]
                }]
            },
            "expected_messages": 1,
            "expected_content_parts": 2
        },
        {
            "name": "System role conversion for Anthropic",
            "input": {
                "model": "claude-3",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello!"}
                ]
            },
            "target_format": "anthropic",
            "expected_messages": 2,
            "expected_first_role": "user",
            "expected_first_content_prefix": "[System]:"
        },
        {
            "name": "Mixed content types",
            "input": {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": "Text only"},
                    {"role": "assistant", "content": {"type": "text", "text": "Response"}},
                    {"role": "user", "content": [{"type": "text", "text": "Another"}]}
                ]
            },
            "expected_messages": 3
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("="*50)
        
        try:
            # Run conversion
            target_format = test_case.get("target_format", "openai")
            converted = full_message_conversion_pipeline(test_case["input"], target_format)
            
            # Validate results
            messages = converted.get("messages", [])
            success = True
            errors = []
            
            # Check message count
            if "expected_messages" in test_case:
                if len(messages) != test_case["expected_messages"]:
                    errors.append(f"Expected {test_case['expected_messages']} messages, got {len(messages)}")
                    success = False
            
            # Check first message
            if messages and "expected_first_role" in test_case:
                if messages[0]["role"] != test_case["expected_first_role"]:
                    errors.append(f"Expected first role '{test_case['expected_first_role']}', got '{messages[0]['role']}'")
                    success = False
            
            if messages and "expected_first_content" in test_case:
                content = messages[0]["content"]
                if isinstance(content, list):
                    content = content[0].get("text", "") if content else ""
                if content != test_case["expected_first_content"]:
                    errors.append(f"Content mismatch: expected '{test_case['expected_first_content']}', got '{content}'")
                    success = False
            
            if messages and "expected_first_content_prefix" in test_case:
                content = messages[0]["content"]
                if isinstance(content, list):
                    content = content[0].get("text", "") if content else ""
                if not content.startswith(test_case["expected_first_content_prefix"]):
                    errors.append(f"Content should start with '{test_case['expected_first_content_prefix']}'")
                    success = False
            
            # Check multimodal content
            if messages and "expected_content_parts" in test_case:
                content = messages[0]["content"]
                if not isinstance(content, list) or len(content) != test_case["expected_content_parts"]:
                    errors.append(f"Expected {test_case['expected_content_parts']} content parts")
                    success = False
            
            # Format validation
            is_valid, validation_error = validate_message_format(messages)
            if not is_valid:
                errors.append(f"Validation failed: {validation_error}")
                success = False
            
            result = {
                "test": test_case["name"],
                "success": success,
                "errors": errors,
                "message_count": len(messages),
                "validation_error": converted.get("_validation_error")
            }
            
            if success:
                logger.success(f"✅ {test_case['name']} passed")
            else:
                logger.error(f"❌ {test_case['name']} failed:")
                for error in errors:
                    logger.error(f"   - {error}")
            
            logger.debug(f"Converted messages: {json.dumps(messages, indent=2)}")
            
        except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            result = {
                "test": test_case["name"],
                "success": False,
                "errors": [str(e)]
            }
        
        results.append(result)
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("CONVERSION TEST SUMMARY")
    logger.info("="*50)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    logger.info(f"Total: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    import sys
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Message conversion pipeline
    total_tests += 1
    try:
        if not test_message_conversions():
            all_validation_failures.append("Message conversion tests failed")
    except Exception as e:
        all_validation_failures.append(f"Conversion test exception: {str(e)}")
    
    # Test 2: Edge cases
    total_tests += 1
    edge_cases = [
        # Empty content
        ({"content": ""}, ""),
        # Nested list
        ({"content": [[{"type": "text", "text": "nested"}]]}, [[{"type": "text", "text": "nested"}]]),
        # Number content (should convert to string)
        ({"content": 123}, "123"),
    ]
    
    for content_input, expected in edge_cases:
        result = normalize_content_format(content_input["content"])
        if str(result) != str(expected):
            all_validation_failures.append(
                f"Content normalization failed: {content_input} -> expected {expected}, got {result}"
            )
    
    # Test 3: Validation edge cases
    total_tests += 1
    invalid_messages = [
        ([], "Messages list cannot be empty"),
        ([{"content": "test"}], "Message 0 missing 'role' field"),
        ([{"role": "invalid", "content": "test"}], "Message 0 has invalid role: invalid"),
        ([{"role": "user"}], "Message 0 missing 'content' field"),
        ([{"role": "user", "content": [{"text": "missing type"}]}], "Message 0 content part 0 missing 'type' field"),
    ]
    
    for invalid_msg, expected_error in invalid_messages:
        is_valid, error = validate_message_format(invalid_msg)
        if is_valid or expected_error not in str(error):
            all_validation_failures.append(
                f"Validation should fail with '{expected_error}', got: valid={is_valid}, error={error}"
            )
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-3 Message format conversion is validated and ready")
        sys.exit(0)