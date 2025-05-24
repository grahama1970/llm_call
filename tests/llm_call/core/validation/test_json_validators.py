"""
Test JSON validators functionality.

Tests for JSON extraction, field validation, and error recovery.
"""

import pytest
from llm_call.core.validation.json_validators import (
    JSONExtractionValidator,
    JSONFieldValidator,
    JSONErrorRecovery,
    extract_json,
    validate_json_schema
)


def test_json_extraction_from_markdown():
    """Test extracting JSON from markdown code blocks."""
    validator = JSONExtractionValidator()
    
    # Test markdown JSON block
    response = """
    Here's the response:
    ```json
    {
        "name": "test",
        "value": 42,
        "nested": {"key": "value"}
    }
    ```
    """
    
    result = validator.validate(response)
    assert result["valid"] == True
    assert result["data"]["name"] == "test"
    assert result["data"]["value"] == 42
    assert result["data"]["nested"]["key"] == "value"


def test_json_extraction_from_generic_block():
    """Test extracting JSON from generic code blocks."""
    validator = JSONExtractionValidator()
    
    response = """
    Output:
    ```
    {"status": "success", "count": 100}
    ```
    """
    
    result = validator.validate(response)
    assert result["valid"] == True
    assert result["data"]["status"] == "success"
    assert result["data"]["count"] == 100


def test_json_extraction_raw():
    """Test extracting raw JSON without code blocks."""
    validator = JSONExtractionValidator()
    
    response = '{"id": 123, "active": true}'
    
    result = validator.validate(response)
    assert result["valid"] == True
    assert result["data"]["id"] == 123
    assert result["data"]["active"] == True


def test_json_schema_validation():
    """Test JSON schema validation."""
    validator = JSONExtractionValidator()
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        },
        "required": ["name", "age"]
    }
    
    # Valid data
    response = '{"name": "Alice", "age": 30}'
    result = validator.validate(response, schema)
    assert result["valid"] == True
    
    # Invalid data (missing required field)
    response = '{"name": "Bob"}'
    result = validator.validate(response, schema)
    assert result["valid"] == False
    assert "Schema validation failed" in result["error"]


def test_field_presence_validation():
    """Test field presence validation."""
    validator = JSONFieldValidator()
    
    data = {
        "user": {"name": "Alice", "email": "alice@example.com"},
        "status": "active"
    }
    
    # All required fields present
    result = validator.validate_field_presence(data, ["user", "status"])
    assert result["valid"] == True
    
    # Missing field
    result = validator.validate_field_presence(data, ["user", "status", "timestamp"])
    assert result["valid"] == False
    assert "timestamp" in result["missing_fields"]


def test_nested_field_validation():
    """Test nested field validation."""
    validator = JSONFieldValidator()
    
    data = {
        "user": {
            "profile": {
                "name": "Alice",
                "age": 30
            }
        }
    }
    
    # Valid nested field
    result = validator.validate_nested_field(data, "user.profile.name", str)
    assert result["valid"] == True
    assert result["value"] == "Alice"
    
    # Valid type check
    result = validator.validate_nested_field(data, "user.profile.age", int)
    assert result["valid"] == True
    assert result["value"] == 30
    
    # Invalid type
    result = validator.validate_nested_field(data, "user.profile.name", int)
    assert result["valid"] == False
    assert "wrong type" in result["error"]
    
    # Missing nested field
    result = validator.validate_nested_field(data, "user.profile.email")
    assert result["valid"] == False
    assert "Field not found" in result["error"]


def test_json_error_recovery():
    """Test JSON error recovery."""
    repairer = JSONErrorRecovery()
    
    # Single quotes
    malformed = "{'name': 'test', 'value': 123}"
    result = repairer.repair_json(malformed)
    assert result["valid"] == True
    assert result["data"]["name"] == "test"
    assert result["repaired"] == True
    
    # Trailing commas
    malformed = '{"items": [1, 2, 3,], "total": 3,}'
    result = repairer.repair_json(malformed)
    assert result["valid"] == True
    assert len(result["data"]["items"]) == 3
    
    # Unquoted keys
    malformed = '{name: "test", value: 42}'
    result = repairer.repair_json(malformed)
    assert result["valid"] == True
    assert result["data"]["name"] == "test"


def test_convenience_functions():
    """Test convenience functions."""
    # extract_json
    response = '```json\n{"test": true}\n```'
    data = extract_json(response)
    assert data is not None
    assert data["test"] == True
    
    # Invalid JSON
    data = extract_json("not json")
    assert data is None
    
    # validate_json_schema
    schema = {
        "type": "object",
        "properties": {"test": {"type": "boolean"}}
    }
    assert validate_json_schema({"test": True}, schema) == True
    assert validate_json_schema({"test": "not bool"}, schema) == False


def test_performance():
    """Test performance meets target (<10ms)."""
    import time
    
    validator = JSONExtractionValidator()
    test_json = '{"test": "data", "nested": {"values": [1, 2, 3]}}'
    response = f"```json\n{test_json}\n```"
    
    # Warm up
    validator.validate(response)
    
    # Measure
    iterations = 1000
    start = time.perf_counter()
    for _ in range(iterations):
        result = validator.validate(response)
    elapsed = time.perf_counter() - start
    
    avg_time_ms = (elapsed / iterations) * 1000
    assert avg_time_ms < 10, f"Too slow: {avg_time_ms:.2f}ms per validation"
    print(f"✅ Performance: {avg_time_ms:.2f}ms per validation")


if __name__ == "__main__":
    # Run key tests directly
    print("Testing JSON validators...")
    
    try:
        test_json_extraction_from_markdown()
        test_field_presence_validation()
        test_json_error_recovery()
        test_performance()
        
        print("\n✅ All JSON validator tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        raise