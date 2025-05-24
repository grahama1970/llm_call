#!/usr/bin/env python3
"""
POC-2: Field presence checking

Purpose:
    Demonstrates checking for required fields in JSON responses.
    Supports simple and nested field paths with type validation.

Links:
    - jsonschema field validation: https://json-schema.org/learn/
    - Python dict traversal: https://docs.python.org/3/tutorial/datastructures.html

Sample Input:
    JSON object with nested structure

Expected Output:
    Validation results for field presence and type

Author: Task 004 Implementation
"""

import json
from typing import Any, Dict, List, Optional, Tuple, Union
from loguru import logger

# Configure logger
logger.add("poc_07_field_presence.log", rotation="10 MB")


def get_nested_value(data: Dict[str, Any], path: str, delimiter: str = ".") -> Tuple[bool, Any]:
    """
    Get value from nested dictionary using dot notation.
    
    Args:
        data: Dictionary to traverse
        path: Path to field (e.g., "user.profile.email")
        delimiter: Path delimiter
        
    Returns:
        Tuple of (exists, value)
    """
    keys = path.split(delimiter)
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list):
            # Handle array indices
            try:
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return False, None
            except ValueError:
                return False, None
        else:
            return False, None
    
    return True, current


def check_field_presence(
    data: Dict[str, Any],
    field_name: str,
    expected_type: Optional[type] = None,
    expected_value: Optional[Any] = None,
    allow_null: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Check if a field is present with optional type and value validation.
    
    Args:
        data: JSON data to check
        field_name: Field name or path (supports dot notation)
        expected_type: Expected type of the field
        expected_value: Expected value (exact match)
        allow_null: Whether to allow null/None values
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    exists, value = get_nested_value(data, field_name)
    
    if not exists:
        return False, f"Field '{field_name}' not found"
    
    if value is None and not allow_null:
        return False, f"Field '{field_name}' is null"
    
    if expected_type and value is not None:
        if not isinstance(value, expected_type):
            return False, f"Field '{field_name}' has type {type(value).__name__}, expected {expected_type.__name__}"
    
    if expected_value is not None and value != expected_value:
        return False, f"Field '{field_name}' has value {repr(value)}, expected {repr(expected_value)}"
    
    return True, None


def check_multiple_fields(
    data: Dict[str, Any],
    field_specs: List[Dict[str, Any]]
) -> Tuple[bool, List[str]]:
    """
    Check multiple fields with specifications.
    
    Args:
        data: JSON data to check
        field_specs: List of field specifications
        
    Returns:
        Tuple of (all_valid, error_messages)
    """
    errors = []
    
    for spec in field_specs:
        field_name = spec.get("name")
        if not field_name:
            continue
        
        is_valid, error = check_field_presence(
            data,
            field_name,
            expected_type=spec.get("type"),
            expected_value=spec.get("value"),
            allow_null=spec.get("allow_null", False)
        )
        
        if not is_valid:
            errors.append(error)
    
    return len(errors) == 0, errors


def test_field_presence():
    """Test various field presence scenarios."""
    
    test_data = {
        "simple": {
            "title": "Test Book",
            "author": "Test Author",
            "year_published": 2023,
            "isbn": None,
            "tags": ["fiction", "drama"]
        },
        "nested": {
            "user": {
                "id": 123,
                "profile": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "settings": {
                        "theme": "dark",
                        "notifications": True
                    }
                }
            },
            "metadata": {
                "created_at": "2023-01-01",
                "version": 2.0
            }
        },
        "array": {
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"},
                {"id": 3, "name": "Item 3"}
            ],
            "total": 3
        },
        "mixed": {
            "id": 1,
            "name": "Conference Session",
            "speaker": {
                "name": "Jane Smith",
                "bio": "Expert in AI"
            },
            "tags": ["AI", "ML", "Deep Learning"],
            "attendees": 150
        }
    }
    
    test_cases = [
        # Simple field checks
        {
            "name": "Simple field exists",
            "data": test_data["simple"],
            "checks": [{"name": "title", "type": str}],
            "expect_success": True
        },
        {
            "name": "Multiple fields with types",
            "data": test_data["simple"],
            "checks": [
                {"name": "title", "type": str},
                {"name": "author", "type": str},
                {"name": "year_published", "type": int},
                {"name": "tags", "type": list}
            ],
            "expect_success": True
        },
        {
            "name": "Field with null value",
            "data": test_data["simple"],
            "checks": [{"name": "isbn", "allow_null": False}],
            "expect_success": False
        },
        {
            "name": "Field with null allowed",
            "data": test_data["simple"],
            "checks": [{"name": "isbn", "allow_null": True}],
            "expect_success": True
        },
        # Nested field checks
        {
            "name": "Nested field access",
            "data": test_data["nested"],
            "checks": [{"name": "user.profile.email", "type": str}],
            "expect_success": True
        },
        {
            "name": "Deep nested field",
            "data": test_data["nested"],
            "checks": [{"name": "user.profile.settings.theme", "value": "dark"}],
            "expect_success": True
        },
        {
            "name": "Multiple nested fields",
            "data": test_data["nested"],
            "checks": [
                {"name": "user.id", "type": int},
                {"name": "user.profile.name", "type": str},
                {"name": "metadata.version", "type": float}
            ],
            "expect_success": True
        },
        # Array access
        {
            "name": "Array element access",
            "data": test_data["array"],
            "checks": [{"name": "items.0.name", "value": "Item 1"}],
            "expect_success": True
        },
        {
            "name": "Array index out of bounds",
            "data": test_data["array"],
            "checks": [{"name": "items.10.name"}],
            "expect_success": False
        },
        # Missing fields
        {
            "name": "Missing field",
            "data": test_data["simple"],
            "checks": [{"name": "publisher"}],
            "expect_success": False
        },
        {
            "name": "Missing nested field",
            "data": test_data["nested"],
            "checks": [{"name": "user.profile.phone"}],
            "expect_success": False
        },
        # Type mismatches
        {
            "name": "Type mismatch",
            "data": test_data["simple"],
            "checks": [{"name": "year_published", "type": str}],
            "expect_success": False
        },
        # Value checks
        {
            "name": "Exact value match",
            "data": test_data["mixed"],
            "checks": [{"name": "attendees", "value": 150}],
            "expect_success": True
        },
        {
            "name": "Value mismatch",
            "data": test_data["mixed"],
            "checks": [{"name": "attendees", "value": 200}],
            "expect_success": False
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("="*50)
        
        try:
            all_valid, errors = check_multiple_fields(
                test_case["data"],
                test_case["checks"]
            )
            
            if test_case["expect_success"]:
                if all_valid:
                    logger.success(f"✅ All fields validated successfully")
                    results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error(f"❌ Validation failed: {errors}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected success"})
            else:
                if not all_valid:
                    logger.success(f"✅ Expected validation failure: {errors}")
                    results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error(f"❌ Expected failure but validation passed")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected failure"})
            
        except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("FIELD PRESENCE TEST SUMMARY")
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
    
    # Test 1: Field presence functionality
    total_tests += 1
    try:
        if not test_field_presence():
            all_validation_failures.append("Field presence tests failed")
    except Exception as e:
        all_validation_failures.append(f"Field presence test exception: {str(e)}")
    
    # Test 2: Complex nested paths
    total_tests += 1
    complex_data = {
        "a": {
            "b": {
                "c": {
                    "d": {
                        "e": "deep_value"
                    }
                }
            }
        },
        "list": [
            {"nested": [{"value": 1}, {"value": 2}]},
            {"nested": [{"value": 3}, {"value": 4}]}
        ]
    }
    
    # Test deep nesting
    exists, value = get_nested_value(complex_data, "a.b.c.d.e")
    if not exists or value != "deep_value":
        all_validation_failures.append("Deep nesting failed")
    
    # Test array in array
    exists, value = get_nested_value(complex_data, "list.1.nested.0.value")
    if not exists or value != 3:
        all_validation_failures.append("Array in array access failed")
    
    # Test 3: Performance with many fields
    total_tests += 1
    import time
    
    large_data = {f"field_{i}": i for i in range(1000)}
    field_specs = [{"name": f"field_{i}", "type": int, "value": i} for i in range(100)]
    
    start_time = time.perf_counter()
    all_valid, errors = check_multiple_fields(large_data, field_specs)
    check_time = (time.perf_counter() - start_time) * 1000
    
    if not all_valid:
        all_validation_failures.append("Large data validation failed")
    elif check_time > 50:  # Should check in < 50ms
        all_validation_failures.append(f"Field checking too slow: {check_time:.2f}ms")
    else:
        logger.info(f"Checked 100 fields in {check_time:.2f}ms")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-7 Field presence checking is validated and ready")
        sys.exit(0)