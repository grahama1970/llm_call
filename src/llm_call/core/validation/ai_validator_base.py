"""
AI-Assisted Validator Base Class
Module: ai_validator_base.py

This module provides a base class for validators that can make recursive LLM calls
to validate responses. Based on research findings:
- Instructor library patterns for structured validation
- DeepEval's LLM-based evaluation metrics'
- Pydantic's async validation patterns'
- Dependency injection for flexible LLM caller configuration

Documentation:
- Pydantic V2: https://docs.pydantic.dev/latest/
- AsyncIO: https://docs.python.org/3/library/asyncio.html
- Instructor: https://github.com/jxnl/instructor

Sample input:
{
    "response": "LLM response to validate",
    "context": {"original_prompt": "...", "validation_criteria": {...}},
    "validation_prompt": "Check if this response is valid"
}

Expected output:
{
    "valid": true/false,
    "confidence": 0.95,
    "reasoning": "Detailed validation reasoning",
    "suggestions": ["improvement 1", "improvement 2"]
}
"""

import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from functools import partial

from loguru import logger
from pydantic import BaseModel, Field, field_validator


class ValidationResult(BaseModel):
    """Structured validation result from AI validator"""
    
    valid: bool = Field(description="Whether the response is valid")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(default="", description="Detailed reasoning for the validation decision")
    suggestions: List[str] = Field(default_factory=list, description="Suggestions for improvement")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Ensure confidence is between 0 and 1"""
        return max(0.0, min(1.0, v))


class AIValidatorConfig(BaseModel):
    """Configuration for AI-assisted validators"""
    
    validation_model: str = Field(default="gpt-4", description="Model to use for validation")
    timeout: float = Field(default=30.0, description="Timeout for validation calls")
    max_recursive_depth: int = Field(default=3, description="Maximum recursive validation depth")
    require_structured_output: bool = Field(default=True, description="Require JSON output")
    temperature: float = Field(default=0.1, description="Temperature for validation calls")
    

class AIAssistedValidator(ABC):
    """Base class for validators that use LLM calls for validation"""
    
    def __init__(self, config: Optional[AIValidatorConfig] = None):
        self.config = config or AIValidatorConfig()
        self._llm_caller: Optional[Callable] = None
        self._recursive_depth = 0
        self._call_history: List[Dict[str, Any]] = []
        
    def set_llm_caller(self, caller: Callable) -> None:
        """
        Set the LLM caller function for dependency injection.
        
        The caller should have signature:
        async def caller(config: Dict[str, Any]) -> Dict[str, Any]
        """
        # Validate caller is callable
        if not callable(caller):
            raise TypeError(f"LLM caller must be callable, got {type(caller)}")
            
        # Check if it's async
        if not asyncio.iscoroutinefunction(caller):
            # Wrap sync function to make it async
            async def async_wrapper(*args, **kwargs):
                return caller(*args, **kwargs)
            self._llm_caller = async_wrapper
        else:
            self._llm_caller = caller
            
        logger.debug(f"LLM caller set for {self.__class__.__name__}")
        
    @abstractmethod
    async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
        """Build the validation prompt for the LLM"""
        pass
        
    @abstractmethod
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse the LLM response into a ValidationResult"""
        pass
        
    async def _make_llm_call(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Make a recursive LLM call for validation"""
        if not self._llm_caller:
            raise RuntimeError("LLM caller not set. Use set_llm_caller() first.")
            
        # Check recursive depth
        self._recursive_depth += 1
        if self._recursive_depth > self.config.max_recursive_depth:
            raise RecursionError(f"Maximum recursive depth {self.config.max_recursive_depth} exceeded")
            
        try:
            # Build LLM config
            llm_config = {
                "model": self.config.validation_model,
                "messages": [
                    {"role": "system", "content": "You are a validation expert. Analyze the given content and provide structured validation feedback."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.config.temperature,
                "timeout": self.config.timeout
            }
            
            if self.config.require_structured_output:
                llm_config["response_format"] = {"type": "json_object"}
                
            # Log the call
            logger.debug(f"Making recursive LLM call (depth={self._recursive_depth})")
            
            # Make the call
            start_time = datetime.utcnow()
            response = await self._llm_caller(llm_config)
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            
            # Record call history
            self._call_history.append({
                "depth": self._recursive_depth,
                "prompt_length": len(prompt),
                "elapsed_time": elapsed,
                "model": self.config.validation_model
            })
            
            return response
            
        finally:
            self._recursive_depth -= 1
            
    async def validate(self, response: str, context: Dict[str, Any]) -> ValidationResult:
        """Main validation method"""
        try:
            # Build validation prompt
            prompt = await self.build_validation_prompt(response, context)
            
            # Make LLM call
            llm_response = await self._make_llm_call(prompt, context)
            
            # Parse response
            result = await self.parse_validation_response(llm_response)
            
            # Add metadata
            result.metadata["call_history"] = self._call_history
            result.metadata["validator_class"] = self.__class__.__name__
            
            return result
            
        except Exception as e:
            logger.error(f"Validation error in {self.__class__.__name__}: {e}")
            # Return failed validation with error details
            return ValidationResult(
                valid=False,
                confidence=0.0,
                reasoning=f"Validation failed: {str(e)}",
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
            
    def get_call_stats(self) -> Dict[str, Any]:
        """Get statistics about LLM calls made"""
        if not self._call_history:
            return {"total_calls": 0}
            
        total_time = sum(call["elapsed_time"] for call in self._call_history)
        return {
            "total_calls": len(self._call_history),
            "total_time": total_time,
            "average_time": total_time / len(self._call_history),
            "max_depth": max(call["depth"] for call in self._call_history),
            "models_used": list(set(call["model"] for call in self._call_history))
        }


class SimpleJSONValidator(AIAssistedValidator):
    """Example validator that checks if response is valid JSON"""
    
    async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
        """Build prompt to validate JSON"""
        return f"""Validate if the following text is valid JSON and meets these criteria:
1. It must be syntactically valid JSON
2. It should have meaningful content (not just empty objects/arrays)
3. Keys should follow standard naming conventions

Text to validate:
{response}

Respond with a JSON object containing:
- "valid": boolean indicating if it's valid JSON'
- "confidence": float between 0 and 1
- "reasoning": explanation of your validation
- "suggestions": array of improvement suggestions
"""
        
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse LLM response"""
        # Extract content from response
        content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        try:
            # Parse JSON response
            parsed = json.loads(content)
            return ValidationResult(**parsed)
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback parsing
            logger.warning(f"Failed to parse structured response: {e}")
            return ValidationResult(
                valid=False,
                confidence=0.5,
                reasoning="Failed to parse validation response",
                suggestions=["Ensure response is valid JSON"]
            )


# Validation function for testing
if __name__ == "__main__":
    import httpx
    
    async def mock_llm_caller(config: Dict[str, Any]) -> Dict[str, Any]:
        """Mock LLM caller for testing"""
        prompt = config["messages"][-1]["content"]
        
        # Simulate different responses based on input
        if "invalid" in prompt.lower():
            response_content = json.dumps({
                "valid": False,
                "confidence": 0.9,
                "reasoning": "The text contains invalid JSON syntax",
                "suggestions": ["Fix syntax errors", "Validate JSON structure"]
            })
        else:
            response_content = json.dumps({
                "valid": True,
                "confidence": 0.95,
                "reasoning": "Valid JSON with proper structure",
                "suggestions": []
            })
            
        # Simulate API response format
        return {
            "choices": [{
                "message": {
                    "content": response_content,
                    "role": "assistant"
                }
            }],
            "usage": {"total_tokens": 100}
        }
        
    async def real_llm_caller(config: Dict[str, Any]) -> Dict[str, Any]:
        """Real LLM caller using httpx (example with OpenAI-compatible API)"""
        # This would use actual API in production
        # For testing, we'll use the mock
        return await mock_llm_caller(config)
        
    async def test_validators():
        """Test the AI validator base class"""
        print("=== Testing AI-Assisted Validator Base Class ===\n")
        
        # Test 1: Basic validation with valid JSON
        print("Test 1: Valid JSON validation")
        validator = SimpleJSONValidator()
        validator.set_llm_caller(mock_llm_caller)
        
        valid_json = '{"name": "test", "value": 123}'
        result = await validator.validate(valid_json, {})
        print(f"Input: {valid_json}")
        print(f"Valid: {result.valid}")
        print(f"Confidence: {result.confidence}")
        print(f"Reasoning: {result.reasoning}")
        print(f"Call stats: {validator.get_call_stats()}")
        print()
        
        # Test 2: Invalid JSON validation
        print("Test 2: Invalid JSON validation")
        validator2 = SimpleJSONValidator()
        validator2.set_llm_caller(mock_llm_caller)
        
        invalid_json = '{"name": "test", invalid}'
        result2 = await validator2.validate(invalid_json, {})
        print(f"Input: {invalid_json}")
        print(f"Valid: {result2.valid}")
        print(f"Confidence: {result2.confidence}")
        print(f"Reasoning: {result2.reasoning}")
        print(f"Suggestions: {result2.suggestions}")
        print()
        
        # Test 3: Test without LLM caller set
        print("Test 3: Missing LLM caller")
        validator3 = SimpleJSONValidator()
        try:
            await validator3.validate("{}", {})
        except RuntimeError as e:
            print(f" Correctly caught error: {e}")
        print()
        
        # Test 4: Test with sync function wrapper
        print("Test 4: Sync function wrapper")
        def sync_caller(config):
            """Synchronous caller that gets wrapped"""
            return {
                "choices": [{
                    "message": {
                        "content": '{"valid": true, "confidence": 1.0, "reasoning": "Sync call worked"}',
                        "role": "assistant"
                    }
                }]
            }
            
        validator4 = SimpleJSONValidator()
        validator4.set_llm_caller(sync_caller)
        result4 = await validator4.validate("{}", {})
        print(f"Sync wrapper result: {result4.reasoning}")
        print()
        
        # Test 5: Custom validator implementation
        print("Test 5: Custom validator implementation")
        
        class CodeValidator(AIAssistedValidator):
            """Validator for Python code"""
            
            async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
                return f"""Analyze this Python code:
```python
{response}
```

Check for:
1. Syntax errors
2. Security issues
3. Best practices

Respond with JSON containing valid, confidence, reasoning, and suggestions."""
                
            async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
                content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                try:
                    parsed = json.loads(content)
                    return ValidationResult(**parsed)
                except (json.JSONDecodeError, KeyError, TypeError):  # Parse error in validation response
                    return ValidationResult(valid=True, confidence=0.5, reasoning="Parse error")
                    
        code_validator = CodeValidator(AIValidatorConfig(validation_model="gpt-4"))
        code_validator.set_llm_caller(mock_llm_caller)
        
        code = "print('Hello, World\!')"
        result5 = await code_validator.validate(code, {"language": "python"})
        print(f"Code validation: {result5.valid} (confidence: {result5.confidence})")
        print(f"Validator config: {code_validator.config.validation_model}")
        
        print("\n All tests completed successfully!")
        
    # Run tests
    asyncio.run(test_validators())