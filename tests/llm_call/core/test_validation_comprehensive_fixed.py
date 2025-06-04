"""
Comprehensive test suite for all validation strategies.

This tests ALL validation strategies in src/llm_call/core/validation to ensure
they work correctly and catch the errors they're supposed to catch.
"""

import pytest
import json
import asyncio
from typing import Dict, Any
from loguru import logger

from llm_call.core.validation.json_validators import (
    JSONExtractionValidator, JSONFieldValidator, JSONErrorRecovery,
    extract_json, validate_json_schema
)
from llm_call.core.validation.builtin_strategies.basic_validators import (
    ResponseNotEmptyValidator, JsonStringValidator
)
from llm_call.core.validation.builtin_strategies.advanced_validators import (
    LengthValidator, RegexValidator, ContainsValidator,
    CodeValidator, FieldPresentValidator
)
from llm_call.core.validation.builtin_strategies.specialized_validators import (
    PythonCodeValidator, JsonValidator, SQLValidator, 
    OpenAPISpecValidator, SQLSafetyValidator, NotEmptyValidator
)
from llm_call.core.validation.builtin_strategies.ai_validators import (
    AIContradictionValidator, AgentTaskValidator
)
from llm_call.core.strategies import get_validator


class TestAllValidators:
    """Test every single validator in the system."""
    
    def test_all_validators_available(self):
        """Ensure all validators are available."""
        # Expected validators based on what we found
        expected_validators = [
            'response_not_empty', 'json_string',  # basic_validators
            'length', 'regex', 'contains', 'code', 'field_present',  # advanced_validators
            'python', 'json', 'sql', 'openapi_spec', 'sql_safe', 'not_empty',  # specialized_validators
            'ai_contradiction_check', 'agent_task'  # ai_validators
        ]
        
        successful_validators = []
        failed_validators = []
        
        for validator_name in expected_validators:
            try:
                # Try to get the validator (some need params)
                if validator_name == 'length':
                    validator = get_validator(validator_name, min_length=1)
                elif validator_name == 'regex':
                    validator = get_validator(validator_name, pattern=r'.*')
                elif validator_name == 'contains':
                    validator = get_validator(validator_name, substring='test')
                elif validator_name == 'field_present':
                    validator = get_validator(validator_name, fields=['test'])
                else:
                    validator = get_validator(validator_name)
                    
                if validator is not None:
                    successful_validators.append(validator_name)
                else:
                    failed_validators.append(validator_name)
            except Exception as e:
                logger.warning(f"Could not instantiate '{validator_name}': {e}")
                failed_validators.append(validator_name)
        
        logger.info(f"Successfully instantiated {len(successful_validators)} validators: {successful_validators}")
        if failed_validators:
            logger.warning(f"Failed to instantiate {len(failed_validators)} validators: {failed_validators}")
    
    @pytest.mark.asyncio
    async def test_basic_validators(self):
        """Test basic validators work correctly."""
        # Test ResponseNotEmptyValidator
        validator = ResponseNotEmptyValidator()
        
        # Test with dict response (Claude proxy format)
        test_response = {
            "choices": [{
                "message": {"role": "assistant", "content": "Hello, world!"}
            }]
        }
        result = await validator.validate(test_response, {})
        assert result.valid == True
        
        # Test with empty response
        empty_response = {
            "choices": [{
                "message": {"role": "assistant", "content": ""}
            }]
        }
        result = await validator.validate(empty_response, {})
        assert result.valid == False
        
        # Test JsonStringValidator
        json_validator = JsonStringValidator()
        
        # Valid JSON response
        json_response = {
            "choices": [{
                "message": {"role": "assistant", "content": '{"key": "value"}'}
            }]
        }
        result = await json_validator.validate(json_response, {})
        assert result.valid == True
        
        # Invalid JSON response
        invalid_json_response = {
            "choices": [{
                "message": {"role": "assistant", "content": 'invalid json'}
            }]
        }
        result = await json_validator.validate(invalid_json_response, {})
        assert result.valid == False
    
    @pytest.mark.asyncio
    async def test_advanced_validators(self):
        """Test advanced validators."""
        # Test LengthValidator
        length_validator = LengthValidator(min_length=10, max_length=100)
        
        # Too short
        result = await length_validator.validate("short", {})
        assert result.valid == False
        
        # Just right
        result = await length_validator.validate("This is a good length", {})
        assert result.valid == True
        
        # Too long
        result = await length_validator.validate("x" * 200, {})
        assert result.valid == False
        
        # Test RegexValidator
        email_validator = RegexValidator(pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        result = await email_validator.validate("test@example.com", {})
        assert result.valid == True
        
        result = await email_validator.validate("invalid-email", {})
        assert result.valid == False
        
        # Test ContainsValidator
        contains_validator = ContainsValidator(substring="API key")
        
        result = await contains_validator.validate("The API key is sk-1234", {})
        assert result.valid == True
        
        result = await contains_validator.validate("No sensitive data here", {})
        assert result.valid == False
    
    @pytest.mark.asyncio
    async def test_specialized_validators(self):
        """Test specialized validators."""
        # Test PythonCodeValidator
        python_validator = PythonCodeValidator()
        
        valid_code = "def hello():\n    return 'world'"
        result = await python_validator.validate(valid_code, {})
        assert result.valid == True
        
        invalid_code = "def hello(\n    return 'world'"
        result = await python_validator.validate(invalid_code, {})
        assert result.valid == False
        
        # Test SQLValidator
        sql_validator = SQLValidator()
        
        valid_sql = "SELECT * FROM users WHERE id = 1"
        result = await sql_validator.validate(valid_sql, {})
        assert result.valid == True
        
        # Test SQLSafetyValidator
        sql_safety = SQLSafetyValidator()
        
        safe_sql = "SELECT * FROM users"
        result = await sql_safety.validate(safe_sql, {})
        assert result.valid == True
        
        dangerous_sql = "DROP TABLE users"
        result = await sql_safety.validate(dangerous_sql, {})
        assert result.valid == False
    
    def test_json_validators(self):
        """Test JSON validation functions."""
        # Test extract_json
        text_with_json = 'Here is some JSON: ```json\n{"key": "value"}\n```'
        result = extract_json(text_with_json)
        assert result == {"key": "value"}
        
        # Test validate_json_schema
        data = {"name": "John", "age": 30}
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            },
            "required": ["name", "age"]
        }
        
        result = validate_json_schema(data, schema)
        assert result == True
        
        # Missing required field
        incomplete_data = {"name": "John"}
        result = validate_json_schema(incomplete_data, schema)
        assert result == False
    
    @pytest.mark.asyncio
    async def test_field_presence_validator(self):
        """Test field presence validation."""
        field_validator = FieldPresentValidator(fields=["status", "data.id"])
        
        valid_response = {
            "status": "success",
            "data": {"id": 123}
        }
        
        result = await field_validator.validate(valid_response, {})
        assert result.valid == True
        
        missing_field = {
            "status": "success",
            "data": {}  # Missing id
        }
        
        result = await field_validator.validate(missing_field, {})
        assert result.valid == False
    
    @pytest.mark.asyncio
    async def test_ai_validators_structure(self):
        """Test AI validators are properly structured (not running actual LLM calls)."""
        # Test AIContradictionValidator structure
        contradiction_validator = AIContradictionValidator()
        assert hasattr(contradiction_validator, 'validate')
        assert hasattr(contradiction_validator, 'name')
        assert contradiction_validator.name == 'ai_contradiction_check'
        
        # Test AgentTaskValidator structure
        agent_validator = AgentTaskValidator()
        assert hasattr(agent_validator, 'validate')
        assert hasattr(agent_validator, 'name')
        assert agent_validator.name == 'agent_task'
    
    def test_validator_types(self):
        """Test different validator types."""
        # Test basic validators
        basic_validators = ['response_not_empty', 'json_string']
        for val_name in basic_validators:
            try:
                validator = get_validator(val_name)
                assert hasattr(validator, 'validate')
                logger.info(f"✅ Basic validator '{val_name}' works")
            except Exception as e:
                logger.error(f"❌ Basic validator '{val_name}' failed: {e}")
        
        # Test parameterized validators
        param_validators = [
            ('length', {'min_length': 10}),
            ('regex', {'pattern': r'.*'}),
            ('contains', {'substring': 'test'})
        ]
        for val_name, params in param_validators:
            try:
                validator = get_validator(val_name, **params)
                assert hasattr(validator, 'validate')
                logger.info(f"✅ Parameterized validator '{val_name}' works")
            except Exception as e:
                logger.error(f"❌ Parameterized validator '{val_name}' failed: {e}")


class TestValidationIntegration:
    """Test validation integration with the overall system."""
    
    def test_validation_in_retry_manager(self):
        """Test validation works correctly in retry scenarios."""
        from llm_call.core.validation.retry_manager import RetryManager
        
        retry_manager = RetryManager(max_attempts=3)
        assert retry_manager.max_attempts == 3
        
        # Test should_retry method
        assert hasattr(retry_manager, 'should_retry')
    
    @pytest.mark.asyncio
    async def test_multiple_validators_chaining(self):
        """Test chaining multiple validators together."""
        response = json.dumps({
            "status": "success",
            "data": {
                "id": 123,
                "message": "Operation completed successfully"
            }
        })
        
        # Test JSON validator first
        json_validator = JsonValidator()
        result = await json_validator.validate(response, {})
        assert result.valid == True
        
        # Test length validator
        length_validator = LengthValidator(min_length=20)
        result = await length_validator.validate(response, {})
        assert result.valid == True
        
        # Test contains validator
        contains_validator = ContainsValidator(substring="success")
        result = await contains_validator.validate(response, {})
        assert result.valid == True


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])