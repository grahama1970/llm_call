"""
JSON validation strategies for LLM responses.

This module provides validators for extracting and validating JSON from various
response formats including markdown code blocks and mixed content.

Links:
- JSON Schema validation: https://python-jsonschema.readthedocs.io/
- Regex patterns: https://docs.python.org/3/library/re.html

Sample usage:
    validator = JSONExtractionValidator()
    result = validator.validate("```json\n{\"key\": \"value\"}\n```")
    
Expected output:
    {"valid": True, "data": {"key": "value"}}
"""

import json
import re
from typing import Dict, Any, Optional, List, Union
from loguru import logger

try:
    from jsonschema import validate as jsonschema_validate, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logger.warning("jsonschema not available, schema validation disabled")


class JSONExtractionValidator:
    """Extract and validate JSON from LLM responses."""
    
    def __init__(self):
        """Initialize with common JSON patterns."""
        self.json_patterns = [
            r'```json\s*([\s\S]*?)\s*```',  # Markdown JSON block
            r'```\s*([\s\S]*?)\s*```',       # Generic code block
            r'\{[\s\S]*\}'                   # Raw JSON object
        ]
    
    def validate(self, response: str, expected_schema: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Extract JSON from response and optionally validate against schema.
        
        Args:
            response: Raw LLM response text
            expected_schema: Optional JSON schema to validate against
            
        Returns:
            Dict with 'valid' bool and either 'data' or 'error'
        """
        if not response:
            return {"valid": False, "error": "Empty response"}
        
        # Try each pattern
        for pattern in self.json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    # Extract JSON string
                    if '```' in pattern:
                        json_str = match.group(1) if match.lastindex else match.group(0)
                    else:
                        json_str = match.group(0)
                    
                    # Parse JSON
                    parsed = json.loads(json_str.strip())
                    
                    # Validate against schema if provided
                    if expected_schema and JSONSCHEMA_AVAILABLE:
                        try:
                            jsonschema_validate(instance=parsed, schema=expected_schema)
                        except ValidationError as e:
                            return {
                                "valid": False,
                                "error": f"Schema validation failed: {str(e)}",
                                "data": parsed  # Include parsed data even if schema fails
                            }
                    
                    return {"valid": True, "data": parsed}
                    
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error with pattern {pattern}: {e}")
                    continue
        
        return {"valid": False, "error": "No valid JSON found in response"}


class JSONFieldValidator:
    """Validate specific fields in JSON responses."""
    
    def validate_field_presence(self, 
                               data: Union[Dict, str], 
                               required_fields: List[str]) -> Dict[str, Any]:
        """
        Check if required fields are present in JSON data.
        
        Args:
            data: JSON data or string to parse
            required_fields: List of field names that must be present
            
        Returns:
            Dict with validation result
        """
        # Parse if string
        if isinstance(data, str):
            extractor = JSONExtractionValidator()
            result = extractor.validate(data)
            if not result["valid"]:
                return result
            data = result["data"]
        
        # Check fields
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            return {
                "valid": False,
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }
        
        return {"valid": True, "data": data}
    
    def validate_nested_field(self,
                             data: Union[Dict, str],
                             field_path: str,
                             expected_type: Optional[type] = None) -> Dict[str, Any]:
        """
        Validate nested field existence and type.
        
        Args:
            data: JSON data or string
            field_path: Dot-separated path like "user.profile.name"
            expected_type: Optional type to check
            
        Returns:
            Dict with validation result
        """
        # Parse if string
        if isinstance(data, str):
            extractor = JSONExtractionValidator()
            result = extractor.validate(data)
            if not result["valid"]:
                return result
            data = result["data"]
        
        # Navigate path
        current = data
        parts = field_path.split('.')
        
        for i, part in enumerate(parts):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return {
                    "valid": False,
                    "error": f"Field not found at path: {'.'.join(parts[:i+1])}"
                }
        
        # Check type if specified
        if expected_type and not isinstance(current, expected_type):
            return {
                "valid": False,
                "error": f"Field {field_path} has wrong type. Expected {expected_type.__name__}, got {type(current).__name__}",
                "value": current
            }
        
        return {"valid": True, "value": current}


class JSONErrorRecovery:
    """Attempt to fix common JSON errors in LLM responses."""
    
    def repair_json(self, malformed_json: str) -> Dict[str, Any]:
        """
        Attempt to repair common JSON formatting issues.
        
        Args:
            malformed_json: Potentially malformed JSON string
            
        Returns:
            Dict with repair result
        """
        if not malformed_json:
            return {"valid": False, "error": "Empty input"}
        
        # Common fixes
        repaired = malformed_json
        
        # Fix single quotes
        repaired = re.sub(r"'([^']*)':", r'"\1":', repaired)
        repaired = re.sub(r":\s*'([^']*)'", r': "\1"', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Fix unquoted keys
        repaired = re.sub(r'(\w+):', r'"\1":', repaired)
        
        # Try to parse
        try:
            parsed = json.loads(repaired)
            return {
                "valid": True, 
                "data": parsed,
                "repaired": True,
                "original": malformed_json
            }
        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "error": f"Could not repair JSON: {str(e)}",
                "attempted_repair": repaired
            }


# Convenience functions for common use cases
def extract_json(response: str) -> Optional[Dict]:
    """Quick extraction of JSON from response."""
    validator = JSONExtractionValidator()
    result = validator.validate(response)
    return result.get("data") if result["valid"] else None


def validate_json_schema(data: Union[Dict, str], schema: Dict) -> bool:
    """Quick schema validation."""
    if isinstance(data, str):
        data = extract_json(data)
        if not data:
            return False
    
    validator = JSONExtractionValidator()
    result = validator.validate(json.dumps(data), schema)
    return result["valid"]


# Self-test
if __name__ == "__main__":
    import sys
    
    logger.info("Testing JSON validators...")
    
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic JSON extraction
    total_tests += 1
    try:
        validator = JSONExtractionValidator()
        test_response = "Here's the data: ```json\n{\"name\": \"test\", \"value\": 42}\n```"
        result = validator.validate(test_response)
        
        assert result["valid"] == True
        assert result["data"]["name"] == "test"
        assert result["data"]["value"] == 42
        logger.success("✅ Basic JSON extraction works")
    except Exception as e:
        all_validation_failures.append(f"Basic extraction failed: {e}")
    
    # Test 2: Field validation
    total_tests += 1
    try:
        field_validator = JSONFieldValidator()
        test_data = {"user": {"name": "Alice", "age": 30}}
        
        result = field_validator.validate_field_presence(test_data, ["user"])
        assert result["valid"] == True
        
        result = field_validator.validate_nested_field(test_data, "user.name", str)
        assert result["valid"] == True
        assert result["value"] == "Alice"
        
        logger.success("✅ Field validation works")
    except Exception as e:
        all_validation_failures.append(f"Field validation failed: {e}")
    
    # Test 3: JSON repair
    total_tests += 1
    try:
        repairer = JSONErrorRecovery()
        malformed = "{'name': 'test', 'values': [1, 2, 3,]}"
        
        result = repairer.repair_json(malformed)
        assert result["valid"] == True
        assert result["data"]["name"] == "test"
        assert len(result["data"]["values"]) == 3
        logger.success("✅ JSON repair works")
    except Exception as e:
        all_validation_failures.append(f"JSON repair failed: {e}")
    
    # Test 4: Performance check
    total_tests += 1
    try:
        import time
        validator = JSONExtractionValidator()
        test_json = '{"test": "data"}' * 100
        
        start = time.perf_counter()
        for _ in range(100):
            result = validator.validate(f"```json\n{test_json}\n```")
        elapsed = (time.perf_counter() - start) / 100 * 1000
        
        assert elapsed < 10, f"Too slow: {elapsed:.2f}ms"
        logger.success(f"✅ Performance: {elapsed:.2f}ms per validation")
    except Exception as e:
        all_validation_failures.append(f"Performance test failed: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        sys.exit(0)