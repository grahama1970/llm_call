"""
Basic validation strategies for LLM responses.
Module: basic_validators.py

This module provides simple validators for common validation needs.

Links:
- JSON documentation: https://docs.python.org/3/library/json.html

Sample usage:
    validator = ResponseNotEmptyValidator()
    result = await validator.validate(response, context)

Expected output:
    ValidationResult with valid=True/False
"""

import json
from typing import Any, Dict
from loguru import logger

from llm_call.core.base import ValidationResult, AsyncValidationStrategy
from llm_call.core.strategies import validator


@validator("response_not_empty")
class ResponseNotEmptyValidator(AsyncValidationStrategy):
    """Validates that the response content is not empty."""
    
    @property
    def name(self) -> str:
        return "response_not_empty"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """
        Check if response has non-empty content.
        
        Args:
            response: LLM response (dict or ModelResponse)
            context: Additional context
            
        Returns:
            ValidationResult
        """
        try:
            # Handle dict responses (from Claude proxy)
            if isinstance(response, dict):
                # Check for error responses
                if "error" in response:
                    return ValidationResult(
                        valid=False,
                        error=f"Error response: {response['error']}",
                        debug_info={"response": response}
                    )
                
                # Check choices format
                choices = response.get("choices", [])
                if not choices:
                    return ValidationResult(
                        valid=False,
                        error="No choices in response",
                        debug_info={"response": response}
                    )
                
                content = choices[0].get("message", {}).get("content", "")
            
            # Handle ModelResponse objects (from LiteLLM)
            elif hasattr(response, "choices"):
                if not response.choices:
                    return ValidationResult(
                        valid=False,
                        error="No choices in response",
                        debug_info={"response_type": type(response).__name__}
                    )
                content = response.choices[0].message.content or ""
            
            # Handle string responses (for testing/direct usage)
            elif isinstance(response, str):
                content = response
            
            else:
                return ValidationResult(
                    valid=False,
                    error=f"Unknown response type: {type(response).__name__}",
                    debug_info={"response_type": type(response).__name__}
                )
            
            # Check content
            if not content or not content.strip():
                return ValidationResult(
                    valid=False,
                    error="Response content is empty",
                    suggestions=["Try rephrasing the prompt", "Check model availability"]
                )
            
            return ValidationResult(
                valid=True,
                debug_info={"content_length": len(content)}
            )
            
        except Exception as e:
            logger.error(f"Error in ResponseNotEmptyValidator: {e}")
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}",
                debug_info={"exception": str(e)}
            )


@validator("json_string")
class JsonStringValidator(AsyncValidationStrategy):
    """Validates that the response content is valid JSON."""
    
    @property
    def name(self) -> str:
        return "json_string"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """
        Check if response content is valid JSON.
        
        Args:
            response: LLM response
            context: Additional context
            
        Returns:
            ValidationResult
        """
        try:
            # Extract content (similar to ResponseNotEmptyValidator)
            if isinstance(response, dict):
                choices = response.get("choices", [])
                if not choices:
                    return ValidationResult(
                        valid=False,
                        error="No choices in response"
                    )
                content = choices[0].get("message", {}).get("content", "")
            
            elif hasattr(response, "choices") and response.choices:
                content = response.choices[0].message.content or ""
            
            # Handle string responses
            elif isinstance(response, str):
                content = response
            
            else:
                return ValidationResult(
                    valid=False,
                    error=f"Unknown response type: {type(response).__name__}"
                )
            
            # Try to parse as JSON
            if not content:
                return ValidationResult(
                    valid=False,
                    error="Empty content cannot be valid JSON"
                )
            
            # Attempt to parse
            try:
                json_data = json.loads(content)
                return ValidationResult(
                    valid=True,
                    debug_info={
                        "json_type": type(json_data).__name__,
                        "json_keys": list(json_data.keys()) if isinstance(json_data, dict) else None
                    }
                )
            except json.JSONDecodeError as e:
                return ValidationResult(
                    valid=False,
                    error=f"Invalid JSON: {str(e)}",
                    suggestions=[
                        "Ensure prompt requests JSON format",
                        "Try adding 'You must respond with valid JSON' to prompt",
                        "Check for trailing commas or unquoted strings"
                    ],
                    debug_info={
                        "parse_error": str(e),
                        "error_position": e.pos if hasattr(e, 'pos') else None
                    }
                )
                
        except Exception as e:
            logger.error(f"Error in JsonStringValidator: {e}")
            return ValidationResult(
                valid=False,
                error=f"Validation error: {str(e)}",
                debug_info={"exception": str(e)}
            )


# Test function
if __name__ == "__main__":
    import sys
    import asyncio
    
    logger.info("Testing basic validators...")
    
    async def test_validators():
        all_validation_failures = []
        total_tests = 0
        
        # Test 1: ResponseNotEmptyValidator with valid response
        total_tests += 1
        try:
            validator = ResponseNotEmptyValidator()
            
            # Test with dict response (Claude proxy format)
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": "Hello, world!"}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == True
            logger.success(" ResponseNotEmptyValidator accepts valid content")
        except Exception as e:
            all_validation_failures.append(f"Empty validator test failed: {e}")
        
        # Test 2: ResponseNotEmptyValidator with empty response
        total_tests += 1
        try:
            validator = ResponseNotEmptyValidator()
            
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": ""}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == False
            assert "empty" in result.error.lower()
            logger.success(" ResponseNotEmptyValidator rejects empty content")
        except Exception as e:
            all_validation_failures.append(f"Empty validator rejection test failed: {e}")
        
        # Test 3: JsonStringValidator with valid JSON
        total_tests += 1
        try:
            validator = JsonStringValidator()
            
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": '{"key": "value", "number": 42}'}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == True
            assert result.debug_info["json_keys"] == ["key", "number"]
            logger.success(" JsonStringValidator accepts valid JSON")
        except Exception as e:
            all_validation_failures.append(f"JSON validator test failed: {e}")
        
        # Test 4: JsonStringValidator with invalid JSON
        total_tests += 1
        try:
            validator = JsonStringValidator()
            
            test_response = {
                "choices": [{
                    "message": {"role": "assistant", "content": 'This is not JSON'}
                }]
            }
            
            result = await validator.validate(test_response, {})
            assert result.valid == False
            assert "Invalid JSON" in result.error
            assert len(result.suggestions) > 0
            logger.success(" JsonStringValidator rejects invalid JSON")
        except Exception as e:
            all_validation_failures.append(f"JSON validator rejection test failed: {e}")
        
        return all_validation_failures, total_tests
    
    # Run tests
    failures, tests = asyncio.run(test_validators())
    
    if failures:
        logger.error(f" VALIDATION FAILED - {len(failures)} of {tests} tests failed:")
        for failure in failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f" VALIDATION PASSED - All {tests} tests produced expected results")
        sys.exit(0)