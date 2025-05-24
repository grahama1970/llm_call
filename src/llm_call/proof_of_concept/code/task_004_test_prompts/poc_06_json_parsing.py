#!/usr/bin/env python3
"""
POC-1: JSON parsing and validation

Purpose:
    Demonstrates JSON parsing from LLM responses and basic validation.
    Tests JSON extraction, error handling, and format verification.

Links:
    - jsonschema: https://python-jsonschema.readthedocs.io/
    - LiteLLM JSON mode: https://docs.litellm.ai/docs/completion/json_mode

Sample Input:
    LLM response with JSON content

Expected Output:
    Parsed JSON object with validation results

Author: Task 004 Implementation
"""

import json
from typing import Any, Dict, Tuple, Optional
from loguru import logger
import re

# Configure logger
logger.add("poc_06_json_parsing.log", rotation="10 MB")


def extract_json_from_response(response: Any) -> Tuple[Optional[Dict], Optional[str]]:
    """
    Extract JSON content from various response formats.
    
    Args:
        response: LLM response in various formats
        
    Returns:
        Tuple of (parsed_json, error_message)
    """
    content_str = None
    
    # Extract content string from different response types
    if isinstance(response, dict):
        if "choices" in response and response["choices"]:
            content_str = response["choices"][0].get("message", {}).get("content", "")
        elif "content" in response:
            content_str = response["content"]
        elif "error" in response:
            return None, f"Error response: {response['error']}"
    elif hasattr(response, "choices") and response.choices:
        content_str = response.choices[0].message.content
    elif isinstance(response, str):
        content_str = response
    else:
        return None, f"Unknown response type: {type(response).__name__}"
    
    if not content_str:
        return None, "Empty content"
    
    # Try direct JSON parsing
    try:
        parsed = json.loads(content_str)
        logger.debug(f"Successfully parsed JSON directly: {type(parsed).__name__}")
        return parsed, None
    except json.JSONDecodeError as e:
        logger.debug(f"Direct JSON parsing failed: {e}")
    
    # Try to extract JSON from markdown code blocks
    json_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
    matches = re.findall(json_pattern, content_str)
    
    if matches:
        for match in matches:
            try:
                parsed = json.loads(match.strip())
                logger.debug("Extracted JSON from markdown code block")
                return parsed, None
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON-like content
    json_like_pattern = r'\{[^{}]*\}'
    json_matches = re.findall(json_like_pattern, content_str)
    
    for match in json_matches:
        try:
            parsed = json.loads(match)
            logger.debug("Extracted JSON from text content")
            return parsed, None
        except json.JSONDecodeError:
            continue
    
    # Last resort: try to clean common issues
    cleaned = content_str.strip()
    if cleaned.startswith("'") and cleaned.endswith("'"):
        cleaned = cleaned[1:-1]
    cleaned = cleaned.replace("'", '"')  # Replace single quotes
    
    try:
        parsed = json.loads(cleaned)
        logger.debug("Parsed JSON after cleaning")
        return parsed, None
    except json.JSONDecodeError as e:
        return None, f"Failed to parse JSON: {str(e)}"


def validate_json_structure(
    json_obj: Dict[str, Any], 
    expected_type: type = dict,
    required_keys: Optional[list] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate basic JSON structure.
    
    Args:
        json_obj: Parsed JSON object
        expected_type: Expected type (dict, list, etc.)
        required_keys: List of required keys for dict
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(json_obj, expected_type):
        return False, f"Expected {expected_type.__name__}, got {type(json_obj).__name__}"
    
    if expected_type == dict and required_keys:
        missing_keys = [key for key in required_keys if key not in json_obj]
        if missing_keys:
            return False, f"Missing required keys: {missing_keys}"
    
    return True, None


def test_json_parsing():
    """Test various JSON parsing scenarios."""
    
    test_cases = [
        {
            "name": "Direct JSON response",
            "response": {
                "choices": [{
                    "message": {
                        "content": '{"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year_published": 1925}'
                    }
                }]
            },
            "expected_keys": ["title", "author", "year_published"],
            "expected_type": dict
        },
        {
            "name": "JSON in markdown",
            "response": {
                "choices": [{
                    "message": {
                        "content": 'Here is the JSON:\n```json\n{"city": "Paris", "country": "France"}\n```'
                    }
                }]
            },
            "expected_keys": ["city", "country"],
            "expected_type": dict
        },
        {
            "name": "Nested JSON",
            "response": {
                "choices": [{
                    "message": {
                        "content": '{"user": {"name": "John", "email": "john@example.com"}, "active": true}'
                    }
                }]
            },
            "expected_keys": ["user", "active"],
            "expected_type": dict
        },
        {
            "name": "Array JSON",
            "response": {
                "choices": [{
                    "message": {
                        "content": '["apple", "banana", "orange"]'
                    }
                }]
            },
            "expected_type": list
        },
        {
            "name": "Malformed JSON recovery",
            "response": {
                "choices": [{
                    "message": {
                        "content": "{'name': 'test', 'value': 123}"  # Single quotes
                    }
                }]
            },
            "expected_keys": ["name", "value"],
            "expected_type": dict
        },
        {
            "name": "Error response",
            "response": {
                "error": "Model overloaded"
            },
            "expect_error": True
        },
        {
            "name": "Empty response",
            "response": {
                "choices": [{
                    "message": {
                        "content": ""
                    }
                }]
            },
            "expect_error": True
        },
        {
            "name": "Mixed content with JSON",
            "response": {
                "choices": [{
                    "message": {
                        "content": 'The result is: {"status": "success", "code": 200} as shown above.'
                    }
                }]
            },
            "expected_keys": ["status", "code"],
            "expected_type": dict
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("="*50)
        
        try:
            # Extract JSON
            json_obj, error = extract_json_from_response(test_case["response"])
            
            if test_case.get("expect_error", False):
                if error:
                    logger.success(f"✅ Expected error occurred: {error}")
                    results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error(f"❌ Expected error but got success")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected error"})
                continue
            
            if error:
                logger.error(f"❌ Extraction failed: {error}")
                results.append({"test": test_case["name"], "passed": False, "reason": error})
                continue
            
            # Validate structure
            expected_type = test_case.get("expected_type", dict)
            required_keys = test_case.get("expected_keys", [])
            
            is_valid, validation_error = validate_json_structure(
                json_obj, expected_type, required_keys
            )
            
            if not is_valid:
                logger.error(f"❌ Validation failed: {validation_error}")
                results.append({"test": test_case["name"], "passed": False, "reason": validation_error})
            else:
                logger.success(f"✅ JSON parsed and validated successfully")
                logger.debug(f"Parsed content: {json.dumps(json_obj, indent=2)}")
                results.append({"test": test_case["name"], "passed": True})
            
        except Exception as e:
            logger.exception(f"Unexpected error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("JSON PARSING TEST SUMMARY")
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
    
    # Test 1: JSON parsing functionality
    total_tests += 1
    try:
        if not test_json_parsing():
            all_validation_failures.append("JSON parsing tests failed")
    except Exception as e:
        all_validation_failures.append(f"JSON parsing test exception: {str(e)}")
    
    # Test 2: Edge cases
    total_tests += 1
    edge_cases = [
        ('{"valid": true}', ({"valid": True}, None)),
        ('{"number": 42.5}', ({"number": 42.5}, None)),
        ('{"null": null}', ({"null": None}, None)),
        ('{"unicode": "👍"}', ({"unicode": "👍"}, None)),
        ('invalid json', (None, "Failed to parse JSON")),
    ]
    
    for json_str, (expected_obj, expected_error) in edge_cases:
        obj, error = extract_json_from_response(json_str)
        if expected_error:
            if not error or expected_error not in error:
                all_validation_failures.append(
                    f"Edge case failed: '{json_str}' expected error containing '{expected_error}'"
                )
        else:
            if obj != expected_obj:
                all_validation_failures.append(
                    f"Edge case failed: '{json_str}' expected {expected_obj}, got {obj}"
                )
    
    # Test 3: Performance with large JSON
    total_tests += 1
    import time
    
    large_json = json.dumps({f"key_{i}": f"value_{i}" for i in range(1000)})
    start_time = time.perf_counter()
    
    obj, error = extract_json_from_response(large_json)
    parse_time = (time.perf_counter() - start_time) * 1000
    
    if error or len(obj) != 1000:
        all_validation_failures.append("Large JSON parsing failed")
    elif parse_time > 100:  # Should parse in < 100ms
        all_validation_failures.append(f"Large JSON parsing too slow: {parse_time:.2f}ms")
    else:
        logger.info(f"Large JSON (1000 keys) parsed in {parse_time:.2f}ms")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-6 JSON parsing is validated and ready")
        sys.exit(0)