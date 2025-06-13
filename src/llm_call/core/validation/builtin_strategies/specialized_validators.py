"""
Specialized validation strategies for specific use cases.
Module: specialized_validators.py

This module provides validators for domain-specific validation needs.
"""

import re
import json
from typing import Any, Dict, Optional, List
from loguru import logger

from llm_call.core.base import ValidationResult, AsyncValidationStrategy
from llm_call.core.strategies import validator


@validator("python")
class PythonCodeValidator(AsyncValidationStrategy):
    """Validates that response contains valid Python code."""
    
    @property
    def name(self) -> str:
        return "python"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate Python code in response."""
        # Use the existing code validator
        from llm_call.core.validation.builtin_strategies.advanced_validators import CodeValidator
        code_validator = CodeValidator(language="python")
        return await code_validator.validate(response, context)


@validator("json")
class JsonValidator(AsyncValidationStrategy):
    """Alias for json_string validator for compatibility."""
    
    @property
    def name(self) -> str:
        return "json"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate JSON in response."""
        # Use the existing json_string validator
        from llm_call.core.validation.builtin_strategies.basic_validators import JsonStringValidator
        json_validator = JsonStringValidator()
        return await json_validator.validate(response, context)


@validator("sql")
class SQLValidator(AsyncValidationStrategy):
    """Basic SQL syntax validation."""
    
    @property
    def name(self) -> str:
        return "sql"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Basic SQL validation - checks for common SQL keywords and structure."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        # Look for SQL keywords
        sql_keywords = [
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 
            'CREATE', 'DROP', 'ALTER', 'TABLE', 'JOIN', 'GROUP BY',
            'ORDER BY', 'HAVING', 'UNION', 'WITH'
        ]
        
        content_upper = content.upper()
        has_sql = any(keyword in content_upper for keyword in sql_keywords)
        
        if not has_sql:
            return ValidationResult(
                valid=False,
                error="No SQL statements found in response",
                suggestions=["Ensure response contains valid SQL"]
            )
        
        # Basic syntax checks
        # Check for unclosed quotes
        single_quotes = content.count("'")
        double_quotes = content.count('"')
        
        if single_quotes % 2 != 0:
            return ValidationResult(
                valid=False,
                error="Unclosed single quote in SQL",
                suggestions=["Check SQL string literals"]
            )
        
        if double_quotes % 2 != 0:
            return ValidationResult(
                valid=False,
                error="Unclosed double quote in SQL",
                suggestions=["Check SQL identifiers"]
            )
        
        # Check for semicolon termination (optional)
        statements = content.strip().split(';')
        non_empty_statements = [s.strip() for s in statements if s.strip()]
        
        return ValidationResult(
            valid=True,
            debug_info={
                "statement_count": len(non_empty_statements),
                "keywords_found": [kw for kw in sql_keywords if kw in content_upper][:5]
            }
        )


@validator("openapi_spec")
class OpenAPISpecValidator(AsyncValidationStrategy):
    """Validates OpenAPI/Swagger specifications."""
    
    @property
    def name(self) -> str:
        return "openapi_spec"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate OpenAPI specification."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        # Try to parse as JSON/YAML
        try:
            if content.strip().startswith('{'):
                # Likely JSON
                spec = json.loads(content)
            else:
                # Try YAML
                try:
                    import yaml
                    spec = yaml.safe_load(content)
                except ImportError:
                    return ValidationResult(
                        valid=False,
                        error="YAML support not available, please provide JSON format",
                        suggestions=["Convert to JSON format or install PyYAML"]
                    )
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Failed to parse OpenAPI spec: {e}",
                suggestions=["Ensure response is valid JSON or YAML"]
            )
        
        # Check for required OpenAPI fields
        if not isinstance(spec, dict):
            return ValidationResult(
                valid=False,
                error="OpenAPI spec must be an object",
                suggestions=["Root element should be an object/dict"]
            )
        
        # Check OpenAPI version
        openapi_version = spec.get("openapi", spec.get("swagger"))
        if not openapi_version:
            return ValidationResult(
                valid=False,
                error="Missing OpenAPI/Swagger version",
                suggestions=["Add 'openapi' field (e.g., '3.0.0') or 'swagger' field (e.g., '2.0')"]
            )
        
        # Check info section
        if "info" not in spec:
            return ValidationResult(
                valid=False,
                error="Missing 'info' section",
                suggestions=["Add 'info' with 'title' and 'version'"]
            )
        
        info = spec["info"]
        if not isinstance(info, dict):
            return ValidationResult(
                valid=False,
                error="'info' must be an object",
                suggestions=["'info' should contain 'title' and 'version'"]
            )
        
        if "title" not in info:
            return ValidationResult(
                valid=False,
                error="Missing 'info.title'",
                suggestions=["Add API title in info section"]
            )
        
        if "version" not in info:
            return ValidationResult(
                valid=False,
                error="Missing 'info.version'",
                suggestions=["Add API version in info section"]
            )
        
        # Check paths (for OpenAPI 3.x) or paths/swagger (for Swagger 2.0)
        if "3." in str(openapi_version):
            if "paths" not in spec and "components" not in spec:
                return ValidationResult(
                    valid=False,
                    error="OpenAPI 3.x spec missing both 'paths' and 'components'",
                    suggestions=["Add 'paths' for API endpoints or 'components' for reusable schemas"]
                )
        elif "2." in str(openapi_version):
            if "paths" not in spec:
                return ValidationResult(
                    valid=False,
                    error="Swagger 2.0 spec missing 'paths'",
                    suggestions=["Add 'paths' section with API endpoints"]
                )
        
        return ValidationResult(
            valid=True,
            debug_info={
                "version": openapi_version,
                "title": info.get("title", "N/A"),
                "paths_count": len(spec.get("paths", {}))
            }
        )


@validator("sql_safe")
class SQLSafetyValidator(AsyncValidationStrategy):
    """Validates SQL queries for safety (no DROP, DELETE, TRUNCATE)."""
    
    @property
    def name(self) -> str:
        return "sql_safe"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check SQL safety."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        # Dangerous keywords
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT", "REVOKE"]
        
        content_upper = content.upper()
        found_dangerous = [kw for kw in dangerous_keywords if kw in content_upper]
        
        if found_dangerous:
            return ValidationResult(
                valid=False,
                error=f"SQL contains potentially dangerous operations: {found_dangerous}",
                suggestions=["Use SELECT queries only", "Avoid data modification statements"],
                debug_info={"dangerous_keywords_found": found_dangerous}
            )
        
        return ValidationResult(
            valid=True,
            debug_info={"checked_for": dangerous_keywords}
        )


@validator("not_empty")
class NotEmptyValidator(AsyncValidationStrategy):
    """Alias for response_not_empty for compatibility."""
    
    @property
    def name(self) -> str:
        return "not_empty"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check response not empty."""
        from llm_call.core.validation.builtin_strategies.basic_validators import ResponseNotEmptyValidator
        validator = ResponseNotEmptyValidator()
        return await validator.validate(response, context)


# Test validators
if __name__ == "__main__":
    import asyncio
    
    async def test_specialized_validators():
        """Test specialized validators."""
        print("=== Testing Specialized Validators ===\n")
        
        # Test response format
        test_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": None
                }
            }]
        }
        
        # Test 1: Python validator
        print("Test 1: Python Validator")
        python_validator = PythonCodeValidator()
        test_response["choices"][0]["message"]["content"] = """
```python
def greet(name):
    return f"Hello, {name}!"
```
"""
        result = await python_validator.validate(test_response, {})
        assert result.valid
        print(" Accepted valid Python code")
        
        # Test 2: SQL validator
        print("\nTest 2: SQL Validator")
        sql_validator = SQLValidator()
        test_response["choices"][0]["message"]["content"] = """
SELECT users.name, COUNT(orders.id) as order_count
FROM users
LEFT JOIN orders ON users.id = orders.user_id
GROUP BY users.id, users.name
ORDER BY order_count DESC;
"""
        result = await sql_validator.validate(test_response, {})
        assert result.valid
        print(" Accepted valid SQL")
        
        # Test 3: SQL safety validator
        print("\nTest 3: SQL Safety Validator")
        safety_validator = SQLSafetyValidator()
        test_response["choices"][0]["message"]["content"] = "SELECT * FROM users WHERE active = 1"
        result = await safety_validator.validate(test_response, {})
        assert result.valid
        print(" Safe SQL accepted")
        
        test_response["choices"][0]["message"]["content"] = "DROP TABLE users"
        result = await safety_validator.validate(test_response, {})
        assert not result.valid
        print(f" Dangerous SQL rejected: {result.error}")
        
        # Test 4: OpenAPI validator
        print("\nTest 4: OpenAPI Validator")
        openapi_validator = OpenAPISpecValidator()
        test_response["choices"][0]["message"]["content"] = json.dumps({
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
                            "200": {"description": "Success"}
                        }
                    }
                }
            }
        })
        result = await openapi_validator.validate(test_response, {})
        assert result.valid
        print(" Valid OpenAPI spec accepted")
        
        print("\n All specialized validator tests passed!")
    
    asyncio.run(test_specialized_validators())