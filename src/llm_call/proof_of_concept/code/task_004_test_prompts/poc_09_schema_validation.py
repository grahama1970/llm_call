#!/usr/bin/env python3
"""
POC-4: JSON schema validation

Purpose:
    Demonstrates comprehensive JSON schema validation.
    Uses jsonschema library with custom validators and formats.

Links:
    - JSON Schema Specification: https://json-schema.org/
    - jsonschema Python: https://python-jsonschema.readthedocs.io/
    - LiteLLM JSON validation: https://github.com/BerriAI/litellm

Sample Input:
    JSON response with complex schema requirements

Expected Output:
    Detailed validation results with error messages

Author: Task 004 Implementation
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger
from jsonschema import validate, ValidationError, Draft7Validator, FormatChecker
import jsonschema.validators

# Configure logger
logger.add("poc_09_schema_validation.log", rotation="10 MB")


# Common schemas for reuse
COMMON_SCHEMAS = {
    "email": {
        "type": "string",
        "format": "email",
        "minLength": 5,
        "maxLength": 255
    },
    "timestamp": {
        "type": "string",
        "format": "date-time"
    },
    "uuid": {
        "type": "string",
        "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    },
    "positive_integer": {
        "type": "integer",
        "minimum": 1
    },
    "percentage": {
        "type": "number",
        "minimum": 0,
        "maximum": 100
    }
}


def create_custom_validator():
    """
    Create a custom validator with additional format checks.
    
    Returns:
        Custom validator class
    """
    # Add custom format checkers
    format_checker = FormatChecker()
    
    @format_checker.checks("phone", raises=ValueError)
    def check_phone(instance):
        """Check if phone number is valid."""
        import re
        pattern = r'^\+?1?\d{9,15}$'
        if not re.match(pattern, instance):
            raise ValueError("Invalid phone number format")
        return True
    
    @format_checker.checks("url", raises=ValueError)
    def check_url(instance):
        """Check if URL is valid."""
        import re
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(pattern, instance):
            raise ValueError("Invalid URL format")
        return True
    
    # Create custom validator with format checker
    CustomValidator = jsonschema.validators.create(
        meta_schema=Draft7Validator.META_SCHEMA,
        validators=Draft7Validator.VALIDATORS,
        version="custom_draft7"
    )
    
    return CustomValidator, format_checker


def validate_with_schema(
    data: Any,
    schema: Dict[str, Any],
    use_custom_validator: bool = True
) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate data against a JSON schema with detailed error reporting.
    
    Args:
        data: Data to validate
        schema: JSON schema
        use_custom_validator: Whether to use custom format validators
        
    Returns:
        Tuple of (is_valid, error_details)
    """
    errors = []
    
    if use_custom_validator:
        CustomValidator, format_checker = create_custom_validator()
        validator = CustomValidator(schema, format_checker=format_checker)
    else:
        validator = Draft7Validator(schema, format_checker=FormatChecker())
    
    for error in validator.iter_errors(data):
        error_detail = {
            "path": list(error.path),
            "message": error.message,
            "schema_path": list(error.schema_path),
            "instance": error.instance,
            "validator": error.validator,
            "validator_value": error.validator_value
        }
        errors.append(error_detail)
    
    return len(errors) == 0, errors


def test_schema_validation():
    """Test various JSON schema validation scenarios."""
    
    # Define test schemas
    schemas = {
        "user_registration": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "minLength": 3,
                    "maxLength": 20,
                    "pattern": "^[a-zA-Z0-9_]+$"
                },
                "email": COMMON_SCHEMAS["email"],
                "password": {
                    "type": "string",
                    "minLength": 8,
                    "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$",
                    "description": "Must contain lowercase, uppercase, and digit"
                },
                "age": {
                    "type": "integer",
                    "minimum": 13,
                    "maximum": 120
                },
                "phone": {
                    "type": "string",
                    "format": "phone"  # Custom format
                },
                "website": {
                    "type": "string",
                    "format": "url"  # Custom format
                },
                "preferences": {
                    "type": "object",
                    "properties": {
                        "newsletter": {"type": "boolean"},
                        "notifications": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["email", "sms", "push"]
                            },
                            "uniqueItems": True
                        }
                    },
                    "required": ["newsletter"]
                }
            },
            "required": ["username", "email", "password", "age"],
            "additionalProperties": False
        },
        "api_request": {
            "type": "object",
            "properties": {
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                },
                "endpoint": {
                    "type": "string",
                    "pattern": "^/api/v[0-9]+/.*$"
                },
                "headers": {
                    "type": "object",
                    "patternProperties": {
                        "^[A-Za-z0-9-]+$": {"type": "string"}
                    },
                    "additionalProperties": False
                },
                "body": {
                    "oneOf": [
                        {"type": "object"},
                        {"type": "array"},
                        {"type": "string"},
                        {"type": "null"}
                    ]
                },
                "query_params": {
                    "type": "object",
                    "additionalProperties": {"type": ["string", "number", "boolean"]}
                }
            },
            "required": ["method", "endpoint"],
            "if": {
                "properties": {"method": {"const": "GET"}}
            },
            "then": {
                "properties": {"body": {"type": "null"}}
            }
        },
        "product_catalog": {
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": COMMON_SCHEMAS["positive_integer"],
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 100
                            },
                            "price": {
                                "type": "number",
                                "minimum": 0,
                                "multipleOf": 0.01
                            },
                            "discount_percentage": COMMON_SCHEMAS["percentage"],
                            "categories": {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 1,
                                "maxItems": 5
                            },
                            "in_stock": {"type": "boolean"},
                            "variants": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "size": {"type": "string"},
                                        "color": {"type": "string"},
                                        "sku": {
                                            "type": "string",
                                            "pattern": "^[A-Z]{3}-[0-9]{4}$"
                                        }
                                    },
                                    "required": ["sku"]
                                }
                            }
                        },
                        "required": ["id", "name", "price", "categories"],
                        "dependencies": {
                            "discount_percentage": ["price"]
                        }
                    }
                },
                "total_count": COMMON_SCHEMAS["positive_integer"],
                "last_updated": COMMON_SCHEMAS["timestamp"]
            },
            "required": ["products", "total_count", "last_updated"]
        }
    }
    
    # Test cases
    test_cases = [
        {
            "name": "Valid user registration",
            "schema": "user_registration",
            "data": {
                "username": "john_doe123",
                "email": "john@example.com",
                "password": "SecurePass123",
                "age": 25,
                "phone": "+1234567890",
                "website": "https://johndoe.com",
                "preferences": {
                    "newsletter": True,
                    "notifications": ["email", "push"]
                }
            },
            "expect_valid": True
        },
        {
            "name": "Invalid password pattern",
            "schema": "user_registration",
            "data": {
                "username": "jane_doe",
                "email": "jane@example.com",
                "password": "weakpass",  # No uppercase or digit
                "age": 30
            },
            "expect_valid": False,
            "expect_error_count": 1
        },
        {
            "name": "Extra properties not allowed",
            "schema": "user_registration",
            "data": {
                "username": "bob_smith",
                "email": "bob@example.com",
                "password": "StrongPass1",
                "age": 40,
                "extra_field": "not allowed"  # additionalProperties: false
            },
            "expect_valid": False,
            "expect_error_contains": "additional"
        },
        {
            "name": "Valid API request GET",
            "schema": "api_request",
            "data": {
                "method": "GET",
                "endpoint": "/api/v1/users",
                "headers": {
                    "Authorization": "Bearer token123",
                    "Accept": "application/json"
                },
                "body": None,
                "query_params": {
                    "page": 1,
                    "limit": 10
                }
            },
            "expect_valid": True
        },
        {
            "name": "Invalid API request - GET with body",
            "schema": "api_request",
            "data": {
                "method": "GET",
                "endpoint": "/api/v1/users",
                "body": {"data": "not allowed for GET"}  # Conditional validation
            },
            "expect_valid": False
        },
        {
            "name": "Valid product catalog",
            "schema": "product_catalog",
            "data": {
                "products": [
                    {
                        "id": 1,
                        "name": "Laptop",
                        "price": 999.99,
                        "discount_percentage": 10,
                        "categories": ["Electronics", "Computers"],
                        "in_stock": True,
                        "variants": [
                            {"size": "13-inch", "color": "Silver", "sku": "LAP-0001"},
                            {"size": "15-inch", "color": "Space Gray", "sku": "LAP-0002"}
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Mouse",
                        "price": 29.99,
                        "categories": ["Electronics", "Accessories"]
                    }
                ],
                "total_count": 2,
                "last_updated": "2023-01-01T12:00:00Z"
            },
            "expect_valid": True
        },
        {
            "name": "Invalid SKU pattern",
            "schema": "product_catalog",
            "data": {
                "products": [
                    {
                        "id": 1,
                        "name": "Keyboard",
                        "price": 79.99,
                        "categories": ["Electronics"],
                        "variants": [
                            {"sku": "INVALID-SKU"}  # Wrong pattern
                        ]
                    }
                ],
                "total_count": 1,
                "last_updated": "2023-01-01T12:00:00Z"
            },
            "expect_valid": False,
            "expect_error_contains": "match"
        },
        {
            "name": "Invalid custom phone format",
            "schema": "user_registration",
            "data": {
                "username": "test_user",
                "email": "test@example.com",
                "password": "TestPass123",
                "age": 20,
                "phone": "not-a-phone"  # Custom format validation
            },
            "expect_valid": False,
            "expect_error_contains": "phone"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("="*50)
        
        try:
            schema = schemas[test_case["schema"]]
            is_valid, errors = validate_with_schema(test_case["data"], schema)
            
            if test_case["expect_valid"]:
                if is_valid:
                    logger.success("✅ Validation passed as expected")
                    results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error(f"❌ Expected valid but got {len(errors)} errors:")
                    for err in errors[:3]:  # Show first 3 errors
                        logger.error(f"   - {'.'.join(map(str, err['path']))}: {err['message']}")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected valid"})
            else:
                if not is_valid:
                    error_str = " ".join(err["message"] for err in errors)
                    if test_case.get("expect_error_contains"):
                        if test_case["expect_error_contains"].lower() in error_str.lower():
                            logger.success(f"✅ Got expected error containing '{test_case['expect_error_contains']}'")
                            results.append({"test": test_case["name"], "passed": True})
                        else:
                            logger.error(f"❌ Got errors but not containing expected text")
                            logger.error(f"   Error string: {error_str}")
                            results.append({"test": test_case["name"], "passed": False, "reason": "Wrong error"})
                    elif test_case.get("expect_error_count"):
                        if len(errors) == test_case["expect_error_count"]:
                            logger.success(f"✅ Got expected {len(errors)} error(s)")
                            results.append({"test": test_case["name"], "passed": True})
                        else:
                            logger.error(f"❌ Expected {test_case['expect_error_count']} errors, got {len(errors)}")
                            results.append({"test": test_case["name"], "passed": False, "reason": "Wrong error count"})
                    else:
                        logger.success(f"✅ Validation failed as expected ({len(errors)} errors)")
                        results.append({"test": test_case["name"], "passed": True})
                else:
                    logger.error("❌ Expected errors but validation passed")
                    results.append({"test": test_case["name"], "passed": False, "reason": "Expected errors"})
            
        except Exception as e:
            logger.exception(f"Error in test: {test_case['name']}")
            results.append({"test": test_case["name"], "passed": False, "reason": str(e)})
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("SCHEMA VALIDATION TEST SUMMARY")
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
    
    # Test 1: Schema validation functionality
    total_tests += 1
    try:
        if not test_schema_validation():
            all_validation_failures.append("Schema validation tests failed")
    except Exception as e:
        all_validation_failures.append(f"Schema validation test exception: {str(e)}")
    
    # Test 2: Complex schema features
    total_tests += 1
    complex_schema = {
        "type": "object",
        "properties": {
            "value": {"type": "number"},
            "flag": {"type": "boolean"}
        },
        "allOf": [
            {
                "if": {"properties": {"flag": {"const": True}}},
                "then": {"properties": {"value": {"minimum": 0}}}
            }
        ]
    }
    
    # Should pass
    is_valid, errors = validate_with_schema({"flag": True, "value": 10}, complex_schema)
    if not is_valid:
        all_validation_failures.append("Complex schema validation failed for valid data")
    
    # Should fail
    is_valid, errors = validate_with_schema({"flag": True, "value": -5}, complex_schema)
    if is_valid:
        all_validation_failures.append("Complex schema validation passed for invalid data")
    
    # Test 3: Performance with large schema
    total_tests += 1
    import time
    
    large_schema = {
        "type": "object",
        "properties": {
            f"field_{i}": {"type": "string", "minLength": 1, "maxLength": 100}
            for i in range(100)
        },
        "required": [f"field_{i}" for i in range(50)]
    }
    
    large_data = {f"field_{i}": f"value_{i}" for i in range(100)}
    
    start_time = time.perf_counter()
    is_valid, errors = validate_with_schema(large_data, large_schema)
    validation_time = (time.perf_counter() - start_time) * 1000
    
    if not is_valid:
        all_validation_failures.append("Large schema validation failed")
    elif validation_time > 100:  # Should validate in < 100ms
        all_validation_failures.append(f"Large schema validation too slow: {validation_time:.2f}ms")
    else:
        logger.info(f"Large schema validation completed in {validation_time:.2f}ms")
    
    # Final validation result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-9 JSON schema validation is validated and ready")
        sys.exit(0)