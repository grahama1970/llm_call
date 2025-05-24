#!/usr/bin/env python3
"""
POC-3: Nested field validation

Purpose:
    Demonstrates validation of complex nested JSON structures.
    Handles recursive validation and deep path traversal.

Links:
    - JSON Schema nested objects: https://json-schema.org/understanding-json-schema/reference/object.html
    - Python recursive validation: https://docs.python.org/3/library/json.html

Sample Input:
    Complex nested JSON with multiple levels

Expected Output:
    Comprehensive validation of nested structure

Author: Task 004 Implementation
"""

import json
from typing import Any, Dict, List, Optional, Tuple, Union
from loguru import logger
from jsonschema import validate, ValidationError, Draft7Validator, FormatChecker

# Configure logger
logger.add("poc_08_nested_fields.log", rotation="10 MB")


def create_nested_schema(structure: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a JSON schema from a structure definition.
    
    Args:
        structure: Nested structure definition
        
    Returns:
        JSON schema
    """
    schema = {"type": "object", "properties": {}, "required": []}
    
    for key, value in structure.items():
        if isinstance(value, dict):
            if "_type" in value:
                # Field definition
                field_schema = {"type": value["_type"]}
                if "_format" in value:
                    field_schema["format"] = value["_format"]
                if "_enum" in value:
                    field_schema["enum"] = value["_enum"]
                if "_items" in value:
                    field_schema["items"] = value["_items"]
                if "_properties" in value:
                    field_schema["properties"] = value["_properties"]
                    field_schema["required"] = value.get("_required", [])
                
                schema["properties"][key] = field_schema
                
                if value.get("_required", True):
                    schema["required"].append(key)
            else:
                # Nested object
                schema["properties"][key] = create_nested_schema(value)
                schema["required"].append(key)
        else:
            # Simple type inference
            if isinstance(value, type):
                type_map = {
                    str: "string",
                    int: "integer",
                    float: "number",
                    bool: "boolean",
                    list: "array",
                    dict: "object"
                }
                schema["properties"][key] = {"type": type_map.get(value, "string")}
                schema["required"].append(key)
    
    return schema


def validate_nested_json(
    data: Dict[str, Any],
    schema: Dict[str, Any],
    return_all_errors: bool = True
) -> Tuple[bool, List[str]]:
    """
    Validate JSON data against a schema with detailed error reporting.
    
    Args:
        data: JSON data to validate
        schema: JSON schema
        return_all_errors: Whether to return all errors or stop at first
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if return_all_errors:
        validator = Draft7Validator(schema, format_checker=FormatChecker())
        for error in validator.iter_errors(data):
            error_path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{error_path}: {error.message}")
    else:
        try:
            validate(instance=data, schema=schema, format_checker=FormatChecker())
        except ValidationError as e:
            error_path = ".".join(str(p) for p in e.path) if e.path else "root"
            errors.append(f"{error_path}: {e.message}")
    
    return len(errors) == 0, errors


def test_nested_validation():
    """Test various nested JSON validation scenarios."""
    
    # Define test schemas
    schemas = {
        "conference_session": {
            "id": int,
            "title": str,
            "speaker": {
                "name": str,
                "bio": str,
                "contact": {
                    "email": {"_type": "string", "_format": "email"},
                    "phone": {"_type": "string", "_required": False}
                }
            },
            "tags": {"_type": "array", "_items": {"type": "string"}},
            "metadata": {
                "created_at": {"_type": "string", "_format": "date-time"},
                "updated_at": {"_type": "string", "_format": "date-time"},
                "version": {"_type": "number"}
            }
        },
        "user_profile": {
            "user_id": int,
            "username": str,
            "profile": {
                "personal": {
                    "first_name": str,
                    "last_name": str,
                    "age": {"_type": "integer", "_minimum": 0, "_maximum": 150}
                },
                "address": {
                    "street": str,
                    "city": str,
                    "country": str,
                    "postal_code": {"_type": "string"}
                },
                "preferences": {
                    "theme": {"_type": "string", "_enum": ["light", "dark", "auto"]},
                    "language": str,
                    "notifications": {
                        "email": bool,
                        "sms": bool,
                        "push": bool
                    }
                }
            },
            "roles": {"_type": "array", "_items": {"type": "string"}}
        },
        "api_response": {
            "status": {"_type": "string", "_enum": ["success", "error", "pending"]},
            "data": {
                "_type": "object",
                "_properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "name": {"type": "string"},
                                "value": {"type": "number"}
                            },
                            "required": ["id", "name"]
                        }
                    },
                    "pagination": {
                        "type": "object",
                        "properties": {
                            "page": {"type": "integer"},
                            "per_page": {"type": "integer"},
                            "total": {"type": "integer"}
                        },
                        "required": ["page", "total"]
                    }
                },
                "_required": ["items", "pagination"]
            },
            "meta": {
                "request_id": str,
                "timestamp": {"_type": "string", "_format": "date-time"}
            }
        }
    }
    
    # Test data
    test_cases = [
        {
            "name": "Valid conference session",
            "schema_name": "conference_session",
            "data": {
                "id": 1,
                "title": "AI in Production",
                "speaker": {
                    "name": "Dr. Jane Smith",
                    "bio": "AI researcher with 10 years experience",
                    "contact": {
                        "email": "jane@example.com"
                    }
                },
                "tags": ["AI", "Production", "Best Practices"],
                "metadata": {
                    "created_at": "2023-01-01T10:00:00Z",
                    "updated_at": "2023-01-02T15:30:00Z",
                    "version": 1.5
                }
            },
            "expect_valid": True
        },
        {
            "name": "Missing required nested field",
            "schema_name": "conference_session",
            "data": {
                "id": 2,
                "title": "Missing Speaker Bio",
                "speaker": {
                    "name": "John Doe",
                    # Missing bio
                    "contact": {
                        "email": "john@example.com"
                    }
                },
                "tags": ["Test"],
                "metadata": {
                    "created_at": "2023-01-01T10:00:00Z",
                    "updated_at": "2023-01-02T15:30:00Z",
                    "version": 1.0
                }
            },
            "expect_valid": False,
            "expect_error_contains": "bio"
        },
        {
            "name": "Invalid email format",
            "schema_name": "conference_session",
            "data": {
                "id": 3,
                "title": "Invalid Email",
                "speaker": {
                    "name": "Invalid Email User",
                    "bio": "Test bio",
                    "contact": {
                        "email": "not-an-email"
                    }
                },
                "tags": [],
                "metadata": {
                    "created_at": "2023-01-01T10:00:00Z",
                    "updated_at": "2023-01-02T15:30:00Z",
                    "version": 1.0
                }
            },
            "expect_valid": False,
            "expect_error_contains": "email"
        },
        {
            "name": "Valid user profile",
            "schema_name": "user_profile",
            "data": {
                "user_id": 123,
                "username": "johndoe",
                "profile": {
                    "personal": {
                        "first_name": "John",
                        "last_name": "Doe",
                        "age": 30
                    },
                    "address": {
                        "street": "123 Main St",
                        "city": "New York",
                        "country": "USA",
                        "postal_code": "10001"
                    },
                    "preferences": {
                        "theme": "dark",
                        "language": "en",
                        "notifications": {
                            "email": True,
                            "sms": False,
                            "push": True
                        }
                    }
                },
                "roles": ["user", "admin"]
            },
            "expect_valid": True
        },
        {
            "name": "Invalid theme enum",
            "schema_name": "user_profile",
            "data": {
                "user_id": 124,
                "username": "janedoe",
                "profile": {
                    "personal": {
                        "first_name": "Jane",
                        "last_name": "Doe",
                        "age": 25
                    },
                    "address": {
                        "street": "456 Oak Ave",
                        "city": "Los Angeles",
                        "country": "USA",
                        "postal_code": "90001"
                    },
                    "preferences": {
                        "theme": "blue",  # Invalid enum
                        "language": "en",
                        "notifications": {
                            "email": True,
                            "sms": True,
                            "push": False
                        }
                    }
                },
                "roles": ["user"]
            },
            "expect_valid": False,
            "expect_error_contains": "theme"
        },
        {
            "name": "Valid API response",
            "schema_name": "api_response",
            "data": {
                "status": "success",
                "data": {
                    "items": [
                        {"id": 1, "name": "Item A", "value": 10.5},
                        {"id": 2, "name": "Item B", "value": 20.0}
                    ],
                    "pagination": {
                        "page": 1,
                        "per_page": 10,
                        "total": 2
                    }
                },
                "meta": {
                    "request_id": "req-123",
                    "timestamp": "2023-01-01T12:00:00Z"
                }
            },
            "expect_valid": True
        },
        {
            "name": "Missing required in array item",
            "schema_name": "api_response",
            "data": {
                "status": "success",
                "data": {
                    "items": [
                        {"id": 1, "name": "Item A", "value": 10.5},
                        {"id": 2, "value": 20.0}  # Missing name
                    ],
                    "pagination": {
                        "page": 1,
                        "total": 2  # Missing per_page (not required)
                    }
                },
                "meta": {
                    "request_id": "req-124",
                    "timestamp": "2023-01-01T12:00:00Z"
                }
            },
            "expect_valid": False,
            "expect_error_contains": "name"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("="*50)
        
        try:
            # Generate schema
            schema_def = schemas[test_case["schema_name"]]
            schema = create_nested_schema(schema_def)
            
            logger.debug(f"Generated schema: {json.dumps(schema, indent=2)}")
            
            # Validate
            is_valid, errors = validate_nested_json(test_case["data"], schema)
            
            if test_case["expect_valid"]:
                if is_valid:
                    logger.success("✅ Validation passed as expected")
                    results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error(f"❌ Expected valid but got errors: {errors}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected valid"})
            else:
                if not is_valid:
                    error_str = " ".join(errors)
                    if test_case.get("expect_error_contains") and test_case["expect_error_contains"] in error_str:
                        logger.success(f"✅ Got expected error containing '{test_case['expect_error_contains']}'")
                        results.append({"test": test_case["name"], "passed": True})
                    else:
                        logger.error(f"❌ Got errors but not the expected ones: {errors}")
                        results.append({"test": test_case["name"], "passed": False, "reason": "Wrong error"})
                else:
                    logger.error("❌ Expected errors but validation passed")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected errors"})
            
        except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("NESTED VALIDATION TEST SUMMARY")
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
    
    # Test 1: Nested validation functionality
    total_tests += 1
    try:
        if not test_nested_validation():
            all_validation_failures.append("Nested validation tests failed")
    except Exception as e:
        all_validation_failures.append(f"Nested validation test exception: {str(e)}")
    
    # Test 2: Schema generation
    total_tests += 1
    test_structure = {
        "simple": str,
        "nested": {
            "field1": int,
            "field2": {"_type": "string", "_format": "email"}
        }
    }
    
    generated_schema = create_nested_schema(test_structure)
    if "properties" not in generated_schema:
        all_validation_failures.append("Schema generation failed - missing properties")
    elif "simple" not in generated_schema["properties"]:
        all_validation_failures.append("Schema generation failed - missing simple field")
    elif generated_schema["properties"]["simple"]["type"] != "string":
        all_validation_failures.append("Schema generation failed - wrong type for simple field")
    
    # Test 3: Deep nesting performance
    total_tests += 1
    import time
    
    # Create deeply nested structure
    deep_structure = {"level1": {"level2": {"level3": {"level4": {"level5": str}}}}}
    deep_data = {"level1": {"level2": {"level3": {"level4": {"level5": "value"}}}}}
    
    start_time = time.perf_counter()
    deep_schema = create_nested_schema(deep_structure)
    is_valid, errors = validate_nested_json(deep_data, deep_schema)
    validation_time = (time.perf_counter() - start_time) * 1000
    
    if not is_valid:
        all_validation_failures.append("Deep nesting validation failed")
    elif validation_time > 50:  # Should validate in < 50ms
        all_validation_failures.append(f"Deep nesting validation too slow: {validation_time:.2f}ms")
    else:
        logger.info(f"Deep nested validation completed in {validation_time:.2f}ms")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-8 Nested field validation is validated and ready")
        sys.exit(0)