"""
Advanced validation strategies for LLM responses.

This module provides validators for common validation needs like
length checking, regex matching, schema validation, and code validation.

Links:
- JSON Schema: https://json-schema.org/
- Python AST: https://docs.python.org/3/library/ast.html
- Regex: https://docs.python.org/3/library/re.html
"""

import re
import json
import ast
from typing import Any, Dict, Optional, Union, List
from loguru import logger

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    logger.warning("jsonschema not installed. Schema validation will not be available.")

from llm_call.core.base import ValidationResult, AsyncValidationStrategy
from llm_call.core.strategies import validator
from llm_call.core.utils.json_utils import clean_json_string


@validator("length")
class LengthValidator(AsyncValidationStrategy):
    """Validates response length constraints."""
    
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        """
        Initialize length validator.
        
        Args:
            min_length: Minimum allowed length (None for no minimum)
            max_length: Maximum allowed length (None for no maximum)
        """
        if min_length is None and max_length is None:
            raise ValueError("At least one of min_length or max_length must be specified")
        
        self.min_length = min_length
        self.max_length = max_length
    
    @property
    def name(self) -> str:
        parts = []
        if self.min_length is not None:
            parts.append(f"min_{self.min_length}")
        if self.max_length is not None:
            parts.append(f"max_{self.max_length}")
        return f"length_{'_'.join(parts)}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check if response length is within constraints."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        length = len(content)
        
        # Check constraints
        if self.min_length is not None and length < self.min_length:
            return ValidationResult(
                valid=False,
                error=f"Response too short: {length} characters (minimum: {self.min_length})",
                suggestions=[f"Response should be at least {self.min_length} characters"],
                debug_info={"actual_length": length, "min_required": self.min_length}
            )
        
        if self.max_length is not None and length > self.max_length:
            return ValidationResult(
                valid=False,
                error=f"Response too long: {length} characters (maximum: {self.max_length})",
                suggestions=[f"Response should be at most {self.max_length} characters"],
                debug_info={"actual_length": length, "max_allowed": self.max_length}
            )
        
        return ValidationResult(
            valid=True,
            debug_info={"length": length}
        )


@validator("regex")
class RegexValidator(AsyncValidationStrategy):
    """Validates response matches a regular expression pattern."""
    
    def __init__(self, pattern: str, flags: int = 0):
        """
        Initialize regex validator.
        
        Args:
            pattern: Regular expression pattern
            flags: Regex flags (e.g., re.IGNORECASE)
        """
        self.pattern = pattern
        self.flags = flags
        self.compiled_pattern = re.compile(pattern, flags)
    
    @property
    def name(self) -> str:
        # Create safe name from pattern
        safe_pattern = re.sub(r'[^a-zA-Z0-9]', '_', self.pattern[:30])
        return f"regex_{safe_pattern}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check if response matches regex pattern."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        if self.compiled_pattern.search(content):
            return ValidationResult(
                valid=True,
                debug_info={"pattern": self.pattern}
            )
        else:
            return ValidationResult(
                valid=False,
                error=f"Response does not match pattern: {self.pattern}",
                suggestions=["Ensure response matches the required pattern"],
                debug_info={"pattern": self.pattern, "content_preview": content[:100]}
            )


@validator("contains")
class ContainsValidator(AsyncValidationStrategy):
    """Validates response contains required text."""
    
    def __init__(self, required_text: Union[str, List[str]], case_sensitive: bool = False):
        """
        Initialize contains validator.
        
        Args:
            required_text: Text or list of texts that must be present
            case_sensitive: Whether to match case-sensitively
        """
        self.required_text = required_text if isinstance(required_text, list) else [required_text]
        self.case_sensitive = case_sensitive
    
    @property
    def name(self) -> str:
        text_summary = "_".join(t[:10] for t in self.required_text[:3])
        safe_summary = re.sub(r'[^a-zA-Z0-9_]', '', text_summary)
        return f"contains_{safe_summary}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check if response contains required text."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        if not self.case_sensitive:
            content = content.lower()
        
        missing = []
        for text in self.required_text:
            search_text = text if self.case_sensitive else text.lower()
            if search_text not in content:
                missing.append(text)
        
        if missing:
            return ValidationResult(
                valid=False,
                error=f"Response missing required text: {missing}",
                suggestions=[f"Response must contain: {', '.join(missing)}"],
                debug_info={"missing": missing}
            )
        
        return ValidationResult(valid=True)


@validator("code")
class CodeValidator(AsyncValidationStrategy):
    """Validates response contains valid code."""
    
    def __init__(self, language: str = "python"):
        """
        Initialize code validator.
        
        Args:
            language: Programming language to validate (currently only "python" supported)
        """
        self.language = language.lower()
        if self.language not in ["python"]:
            raise ValueError(f"Unsupported language: {language}")
    
    @property
    def name(self) -> str:
        return f"code_{self.language}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check if response contains valid code."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        
        if not code_blocks:
            # Try to validate the entire content as code
            code_blocks = [content]
        
        errors = []
        for i, code in enumerate(code_blocks):
            if self.language == "python":
                error = self._validate_python(code)
                if error:
                    errors.append(f"Block {i+1}: {error}")
        
        if errors:
            return ValidationResult(
                valid=False,
                error=f"Invalid {self.language} code: {'; '.join(errors)}",
                suggestions=[f"Fix syntax errors in {self.language} code"],
                debug_info={"errors": errors}
            )
        
        return ValidationResult(
            valid=True,
            debug_info={"code_blocks": len(code_blocks)}
        )
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown or plain text."""
        # Look for ```language blocks
        pattern = rf'```{self.language}?\s*\n(.*?)```'
        blocks = re.findall(pattern, text, re.DOTALL)
        
        # If no markdown code blocks found, return empty list
        # The main validate method will use the entire content
        return blocks
    
    def _validate_python(self, code: str) -> Optional[str]:
        """Validate Python code syntax."""
        try:
            ast.parse(code)
            return None
        except SyntaxError as e:
            return f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return str(e)


if HAS_JSONSCHEMA:
    @validator("schema")
    class SchemaValidator(AsyncValidationStrategy):
        """Validates JSON response against a JSON Schema."""
        
        def __init__(self, schema: Dict[str, Any]):
            """
            Initialize schema validator.
            
            Args:
                schema: JSON Schema to validate against
            """
            self.schema = schema
            # Pre-compile the schema for better performance
            self.validator = jsonschema.Draft7Validator(schema)
        
        @property
        def name(self) -> str:
            # Use schema title if available
            title = self.schema.get("title", "unnamed")
            safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', title)
            return f"schema_{safe_title}"
        
        async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
            """Check if response matches JSON schema."""
            # Extract content
            content = ""
            if isinstance(response, dict) and response.get("choices"):
                content = response["choices"][0].get("message", {}).get("content", "")
            elif hasattr(response, "choices") and response.choices:
                content = response.choices[0].message.content or ""
            elif isinstance(response, str):
                content = response
            
            # Try to parse JSON
            try:
                data = clean_json_string(content, return_dict=True)
                if data is None:
                    return ValidationResult(
                        valid=False,
                        error="No valid JSON found in response",
                        suggestions=["Ensure response contains valid JSON"]
                    )
            except Exception as e:
                return ValidationResult(
                    valid=False,
                    error=f"Failed to parse JSON: {e}",
                    suggestions=["Ensure response is valid JSON"]
                )
            
            # Validate against schema
            errors = list(self.validator.iter_errors(data))
            if errors:
                error_messages = []
                for error in errors[:3]:  # Show first 3 errors
                    path = " -> ".join(str(p) for p in error.path) if error.path else "root"
                    error_messages.append(f"{path}: {error.message}")
                
                return ValidationResult(
                    valid=False,
                    error=f"Schema validation failed: {'; '.join(error_messages)}",
                    suggestions=["Ensure response matches the required schema"],
                    debug_info={"errors": error_messages, "error_count": len(errors)}
                )
            
            return ValidationResult(
                valid=True,
                debug_info={"schema_title": self.schema.get("title", "unnamed")}
            )


@validator("field_present")
class FieldPresentValidator(AsyncValidationStrategy):
    """Validates that specific fields are present (or absent) in JSON response."""
    
    def __init__(self, 
                 field_name: str, 
                 expected_value: Optional[Any] = None,
                 should_exist: bool = True):
        """
        Initialize field validator.
        
        Args:
            field_name: Name of the field to check (supports dot notation)
            expected_value: If provided, field must equal this value
            should_exist: Whether field should exist (True) or not exist (False)
        """
        self.field_name = field_name
        self.expected_value = expected_value
        self.should_exist = should_exist
    
    @property
    def name(self) -> str:
        existence = "present" if self.should_exist else "absent"
        safe_field = re.sub(r'[^a-zA-Z0-9_]', '_', self.field_name)
        return f"field_{existence}_{safe_field}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """Check field presence/absence and value."""
        # Extract content
        content = ""
        if isinstance(response, dict) and response.get("choices"):
            content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content or ""
        elif isinstance(response, str):
            content = response
        
        # Parse JSON
        try:
            data = clean_json_string(content, return_dict=True)
            if data is None:
                return ValidationResult(
                    valid=False,
                    error="No valid JSON found to check fields",
                    suggestions=["Ensure response contains valid JSON"]
                )
        except Exception as e:
            return ValidationResult(
                valid=False,
                error=f"Failed to parse JSON: {e}"
            )
        
        # Navigate to field using dot notation
        current = data
        parts = self.field_name.split('.')
        field_exists = True
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                field_exists = False
                break
        
        # Check existence
        if self.should_exist and not field_exists:
            return ValidationResult(
                valid=False,
                error=f"Required field '{self.field_name}' not found",
                suggestions=[f"Include field '{self.field_name}' in response"]
            )
        elif not self.should_exist and field_exists:
            return ValidationResult(
                valid=False,
                error=f"Field '{self.field_name}' should not be present",
                suggestions=[f"Remove field '{self.field_name}' from response"]
            )
        
        # Check value if field should exist and we have an expected value
        if self.should_exist and field_exists and self.expected_value is not None:
            if current != self.expected_value:
                return ValidationResult(
                    valid=False,
                    error=f"Field '{self.field_name}' has value {current!r}, expected {self.expected_value!r}",
                    suggestions=[f"Set '{self.field_name}' to {self.expected_value!r}"]
                )
        
        return ValidationResult(
            valid=True,
            debug_info={"field": self.field_name, "exists": field_exists}
        )


# Validation function for testing
if __name__ == "__main__":
    import asyncio
    
    async def test_validators():
        """Test advanced validators."""
        print("=== Testing Advanced Validators ===\n")
        
        # Test response format for testing
        test_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": None  # Will be set for each test
                }
            }]
        }
        
        # Test 1: Length validator
        print("Test 1: Length Validator")
        validator = LengthValidator(min_length=10, max_length=100)
        
        test_response["choices"][0]["message"]["content"] = "Short"
        result = await validator.validate(test_response, {})
        assert not result.valid
        print(f"✅ Correctly rejected short text: {result.error}")
        
        test_response["choices"][0]["message"]["content"] = "This is a longer text that meets the minimum length requirement."
        result = await validator.validate(test_response, {})
        assert result.valid
        print("✅ Accepted valid length text")
        
        # Test 2: Regex validator
        print("\nTest 2: Regex Validator")
        email_validator = RegexValidator(r'^[\w\.-]+@[\w\.-]+\.\w+$')
        
        test_response["choices"][0]["message"]["content"] = "test@example.com"
        result = await email_validator.validate(test_response, {})
        assert result.valid
        print("✅ Accepted valid email")
        
        test_response["choices"][0]["message"]["content"] = "not-an-email"
        result = await email_validator.validate(test_response, {})
        assert not result.valid
        print(f"✅ Rejected invalid email: {result.error}")
        
        # Test 3: Contains validator
        print("\nTest 3: Contains Validator")
        validator = ContainsValidator(["Python", "programming"], case_sensitive=False)
        
        test_response["choices"][0]["message"]["content"] = "python is a great PROGRAMMING language"
        result = await validator.validate(test_response, {})
        assert result.valid
        print("✅ Found all required text (case-insensitive)")
        
        # Test 4: Code validator
        print("\nTest 4: Code Validator")
        code_validator = CodeValidator(language="python")
        
        test_response["choices"][0]["message"]["content"] = """
```python
def hello(name):
    print(f"Hello, {name}!")
```
"""
        result = await code_validator.validate(test_response, {})
        assert result.valid
        print("✅ Accepted valid Python code")
        
        test_response["choices"][0]["message"]["content"] = """
```python
def broken(
    print("Missing closing parenthesis"
```
"""
        result = await code_validator.validate(test_response, {})
        assert not result.valid
        print(f"✅ Rejected invalid Python: {result.error}")
        
        # Test 5: Field validator
        print("\nTest 5: Field Validator")
        field_validator = FieldPresentValidator("data.results", should_exist=True)
        
        test_response["choices"][0]["message"]["content"] = '{"data": {"results": [1, 2, 3]}}'
        result = await field_validator.validate(test_response, {})
        assert result.valid
        print("✅ Found required nested field")
        
        # Test 6: Schema validator (if available)
        if HAS_JSONSCHEMA:
            print("\nTest 6: Schema Validator")
            schema = {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "number", "minimum": 0}
                },
                "required": ["name", "age"]
            }
            schema_validator = SchemaValidator(schema)
            
            test_response["choices"][0]["message"]["content"] = '{"name": "Alice", "age": 30}'
            result = await schema_validator.validate(test_response, {})
            assert result.valid
            print("✅ Valid JSON matches schema")
            
            test_response["choices"][0]["message"]["content"] = '{"name": "Bob"}'
            result = await schema_validator.validate(test_response, {})
            assert not result.valid
            print(f"✅ Rejected invalid JSON: {result.error}")
        
        print("\n✅ All advanced validator tests passed!")
    
    asyncio.run(test_validators())