#!/usr/bin/env python3
"""
Comprehensive test script for all validation strategies.

This script tests each validator type with real examples to ensure
they work correctly.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
from loguru import logger

from llm_call.core.strategies import get_validator, registry
from llm_call.core.validation.builtin_strategies.basic_validators import (
    ResponseNotEmptyValidator,
    JsonStringValidator
)
from llm_call.core.validation.builtin_strategies.ai_validators import (
    AIContradictionValidator,
    AgentTaskValidator
)
from llm_call.core.validation.builtin_strategies.advanced_validators import (
    LengthValidator,
    RegexValidator,
    ContainsValidator,
    CodeValidator,
    SchemaValidator,
    FieldPresentValidator
)
from llm_call.core.validation.builtin_strategies.specialized_validators import (
    PythonCodeValidator,
    JsonValidator,
    SQLValidator,
    OpenAPISpecValidator,
    SQLSafetyValidator,
    NotEmptyValidator
)


class ValidationTester:
    """Test runner for validation strategies."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results: List[Dict[str, Any]] = []
    
    async def test_validator(
        self,
        name: str,
        validator,
        test_cases: List[Dict[str, Any]]
    ):
        """Test a validator with multiple test cases."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {name}")
        logger.info(f"{'='*60}")
        
        for i, test_case in enumerate(test_cases):
            response = test_case.get("response", "")
            expected = test_case.get("expected", True)
            description = test_case.get("description", f"Test case {i+1}")
            
            try:
                # Create empty context for validators
                context = {}
                result = await validator.validate(response, context)
                success = result.valid == expected
                
                if success:
                    self.passed += 1
                    logger.success(f"✅ {description}: PASSED")
                    if result.error:
                        logger.debug(f"   Expected error: {result.error}")
                else:
                    self.failed += 1
                    logger.error(f"❌ {description}: FAILED")
                    logger.error(f"   Expected: {expected}, Got: {result.valid}")
                    if result.error:
                        logger.error(f"   Error: {result.error}")
                
                self.results.append({
                    "validator": name,
                    "test": description,
                    "passed": success,
                    "expected": expected,
                    "actual": result.valid,
                    "error": result.error
                })
                
            except Exception as e:
                self.failed += 1
                logger.error(f"❌ {description}: EXCEPTION")
                logger.error(f"   Error: {str(e)}")
                self.results.append({
                    "validator": name,
                    "test": description,
                    "passed": False,
                    "exception": str(e)
                })
    
    def print_summary(self):
        """Print test summary."""
        total = self.passed + self.failed
        logger.info(f"\n{'='*60}")
        logger.info(f"VALIDATION TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total tests: {total}")
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        
        if self.failed > 0:
            logger.error(f"\n❌ {self.failed} tests failed:")
            for result in self.results:
                if not result.get("passed", False):
                    logger.error(f"  - {result['validator']}: {result['test']}")
                    if "exception" in result:
                        logger.error(f"    Exception: {result['exception']}")
                    else:
                        logger.error(f"    Expected: {result['expected']}, Got: {result['actual']}")
        else:
            logger.success(f"\n✅ All {total} tests passed!")


async def main():
    """Run all validator tests."""
    tester = ValidationTester()
    
    # Test 1: ResponseNotEmptyValidator
    await tester.test_validator(
        "ResponseNotEmptyValidator",
        ResponseNotEmptyValidator(),
        [
            {"response": "Hello world", "expected": True, "description": "Non-empty string"},
            {"response": "", "expected": False, "description": "Empty string"},
            {"response": "   ", "expected": False, "description": "Whitespace only"},
            {"response": None, "expected": False, "description": "None value"},
        ]
    )
    
    # Test 2: JsonStringValidator
    await tester.test_validator(
        "JsonStringValidator",
        JsonStringValidator(),
        [
            {"response": '{"key": "value"}', "expected": True, "description": "Valid JSON"},
            {"response": '{"items": [1, 2, 3]}', "expected": True, "description": "JSON with array"},
            {"response": 'invalid json', "expected": False, "description": "Invalid JSON"},
            {"response": '{"key": }', "expected": False, "description": "Malformed JSON"},
        ]
    )
    
    # Test 3: LengthValidator
    await tester.test_validator(
        "LengthValidator (min=10, max=50)",
        LengthValidator(min_length=10, max_length=50),
        [
            {"response": "This is exactly long enough", "expected": True, "description": "Within range"},
            {"response": "Short", "expected": False, "description": "Too short"},
            {"response": "This is a very long response that exceeds the maximum length limit set for validation", "expected": False, "description": "Too long"},
            {"response": "Perfect fit", "expected": True, "description": "Just right"},
        ]
    )
    
    # Test 4: RegexValidator
    await tester.test_validator(
        "RegexValidator (email pattern)",
        RegexValidator(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'),
        [
            {"response": "user@example.com", "expected": True, "description": "Valid email"},
            {"response": "test.user@domain.co.uk", "expected": True, "description": "Complex email"},
            {"response": "invalid.email", "expected": False, "description": "Missing @"},
            {"response": "@example.com", "expected": False, "description": "Missing username"},
        ]
    )
    
    # Test 5: ContainsValidator
    await tester.test_validator(
        "ContainsValidator (required_text='Python')",
        ContainsValidator(required_text="Python"),
        [
            {"response": "I love Python programming", "expected": True, "description": "Contains Python"},
            {"response": "python is great", "expected": True, "description": "Case insensitive - lowercase (default)"},
            {"response": "Java and JavaScript", "expected": False, "description": "Doesn't contain Python"},
            {"response": "Python", "expected": True, "description": "Exact match"},
        ]
    )
    
    # Test 6: CodeValidator
    await tester.test_validator(
        "CodeValidator",
        CodeValidator(),
        [
            {"response": "def add(a, b):\n    return a + b", "expected": True, "description": "Valid Python function"},
            {"response": "print('Hello')", "expected": True, "description": "Valid Python statement"},
            {"response": "def broken(:\n    pass", "expected": False, "description": "Syntax error"},
            {"response": "Just plain text", "expected": False, "description": "Not code"},
        ]
    )
    
    # Test 7: SchemaValidator
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name", "age"]
    }
    await tester.test_validator(
        "SchemaValidator (person schema)",
        SchemaValidator(schema=schema),
        [
            {"response": '{"name": "John", "age": 30}', "expected": True, "description": "Valid person object"},
            {"response": '{"name": "Jane"}', "expected": False, "description": "Missing required field"},
            {"response": '{"name": "Bob", "age": "thirty"}', "expected": False, "description": "Wrong type for age"},
            {"response": 'invalid json', "expected": False, "description": "Not even JSON"},
        ]
    )
    
    # Test 8: FieldPresentValidator
    await tester.test_validator(
        "FieldPresentValidator (field='result')",
        FieldPresentValidator(field_name="result"),
        [
            {"response": '{"result": "success", "data": {}}', "expected": True, "description": "Field present"},
            {"response": '{"status": "ok", "result": null}', "expected": True, "description": "Field present (null value)"},
            {"response": '{"status": "ok", "data": {}}', "expected": False, "description": "Field missing"},
            {"response": 'not json', "expected": False, "description": "Invalid JSON"},
        ]
    )
    
    # Test 9: PythonCodeValidator
    await tester.test_validator(
        "PythonCodeValidator",
        PythonCodeValidator(),
        [
            {"response": "class Person:\n    def __init__(self, name):\n        self.name = name", "expected": True, "description": "Valid class"},
            {"response": "import sys\nprint(sys.version)", "expected": True, "description": "Valid imports"},
            {"response": "def func(\n    pass", "expected": False, "description": "Syntax error"},
            {"response": "This is not Python code", "expected": False, "description": "Plain text"},
        ]
    )
    
    # Test 10: SQLValidator
    await tester.test_validator(
        "SQLValidator",
        SQLValidator(),
        [
            {"response": "SELECT * FROM users WHERE id = 1", "expected": True, "description": "Valid SELECT"},
            {"response": "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')", "expected": True, "description": "Valid INSERT"},
            {"response": "UPDATE users SET name = 'Jane' WHERE id = 2", "expected": True, "description": "Valid UPDATE"},
            {"response": "Not SQL at all", "expected": False, "description": "Not SQL"},
        ]
    )
    
    # Test 11: SQLSafetyValidator
    await tester.test_validator(
        "SQLSafetyValidator",
        SQLSafetyValidator(),
        [
            {"response": "SELECT name FROM users WHERE id = 1", "expected": True, "description": "Safe SELECT"},
            {"response": "DROP TABLE users", "expected": False, "description": "Dangerous DROP"},
            {"response": "DELETE FROM users", "expected": False, "description": "Dangerous DELETE without WHERE"},
            {"response": "TRUNCATE TABLE logs", "expected": False, "description": "Dangerous TRUNCATE"},
        ]
    )
    
    # Test 12: OpenAPISpecValidator
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0"
        },
        "paths": {
            "/users": {
                "get": {
                    "summary": "Get users",
                    "responses": {
                        "200": {
                            "description": "Success"
                        }
                    }
                }
            }
        }
    }
    await tester.test_validator(
        "OpenAPISpecValidator",
        OpenAPISpecValidator(),
        [
            {"response": json.dumps(openapi_spec), "expected": True, "description": "Valid OpenAPI spec"},
            {"response": '{"swagger": "2.0", "info": {"title": "API", "version": "1.0"}, "paths": {}}', "expected": True, "description": "Valid Swagger 2.0"},
            {"response": '{"info": {"title": "API"}}', "expected": False, "description": "Missing required fields"},
            {"response": "not json", "expected": False, "description": "Invalid format"},
        ]
    )
    
    # Test 13: NotEmptyValidator (alias test)
    await tester.test_validator(
        "NotEmptyValidator",
        NotEmptyValidator(),
        [
            {"response": "Content", "expected": True, "description": "Has content"},
            {"response": "", "expected": False, "description": "Empty"},
        ]
    )
    
    # Test 14: JsonValidator (alias test)
    await tester.test_validator(
        "JsonValidator",
        JsonValidator(),
        [
            {"response": '{"valid": true}', "expected": True, "description": "Valid JSON"},
            {"response": 'invalid', "expected": False, "description": "Invalid JSON"},
        ]
    )
    
    # Print summary
    tester.print_summary()
    
    # Test registry access
    logger.info(f"\n{'='*60}")
    logger.info("Testing Registry Access")
    logger.info(f"{'='*60}")
    
    validator_names = [
        "response_not_empty", "json_string", "length", "regex",
        "contains", "code", "schema", "field_present",
        "python", "json", "sql", "openapi_spec", "sql_safe", "not_empty"
    ]
    
    registry_test_passed = 0
    registry_test_failed = 0
    
    for name in validator_names:
        try:
            if name == "length":
                validator = get_validator(name, min_length=1)
            elif name == "regex":
                validator = get_validator(name, pattern=".*")
            elif name == "contains":
                validator = get_validator(name, required_text="test")
            elif name == "schema":
                validator = get_validator(name, schema={"type": "object"})
            elif name == "field_present":
                validator = get_validator(name, field_name="test")
            else:
                validator = get_validator(name)
            
            if validator:
                registry_test_passed += 1
                logger.success(f"✅ Registry access for '{name}': SUCCESS")
            else:
                registry_test_failed += 1
                logger.error(f"❌ Registry access for '{name}': FAILED - returned None")
        except Exception as e:
            registry_test_failed += 1
            logger.error(f"❌ Registry access for '{name}': FAILED - {str(e)}")
    
    logger.info(f"\nRegistry access: {registry_test_passed} passed, {registry_test_failed} failed")
    
    # Final summary
    total_tests = tester.passed + tester.failed + registry_test_passed + registry_test_failed
    total_passed = tester.passed + registry_test_passed
    total_failed = tester.failed + registry_test_failed
    
    logger.info(f"\n{'='*60}")
    logger.info("FINAL SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total tests run: {total_tests}")
    logger.info(f"Total passed: {total_passed}")
    logger.info(f"Total failed: {total_failed}")
    
    if total_failed == 0:
        logger.success("\n✅ ALL VALIDATORS ARE WORKING CORRECTLY!")
        return 0
    else:
        logger.error(f"\n❌ {total_failed} TESTS FAILED - VALIDATORS NEED FIXING")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))