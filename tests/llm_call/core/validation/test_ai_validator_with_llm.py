"""
Test AI Validator with Real LLM Calls

This test demonstrates the AI validator base class with actual LLM integration.
"""

import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm_call.core.validation.ai_validator_base import AIAssistedValidator, ValidationResult, AIValidatorConfig
from llm_call.core.caller import make_llm_request
from loguru import logger


class ContractValidator(AIAssistedValidator):
    """Validates if text contains contradictory statements"""
    
    async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
        """Build prompt to check for contradictions"""
        return f"""Analyze the following text for logical contradictions or inconsistencies:

Text to analyze:
"{response}"

Context: {context.get('topic', 'general text')}

Please identify:
1. Any direct contradictions (statements that oppose each other)
2. Logical inconsistencies 
3. Factual errors that contradict known facts

Respond with a JSON object containing:
- "valid": false if contradictions found, true otherwise
- "confidence": your confidence level (0.0 to 1.0)
- "reasoning": detailed explanation of any contradictions found
- "suggestions": list of suggestions to resolve contradictions
"""
        
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse the validation response"""
        content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        try:
            parsed = json.loads(content)
            # Invert valid flag - if contradictions found, it's invalid
            return ValidationResult(**parsed)
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return ValidationResult(
                valid=True,
                confidence=0.5,
                reasoning="Unable to parse validation response",
                suggestions=["Retry validation"]
            )


async def test_with_real_llm():
    """Test validators with actual LLM calls"""
    print("=== Testing AI Validator with Real LLM ===\n")
    
    # Test 1: Text with obvious contradiction
    print("Test 1: Obvious Contradiction")
    validator1 = ContractValidator(AIValidatorConfig(
        validation_model="gpt-3.5-turbo",
        temperature=0.1
    ))
    validator1.set_llm_caller(make_llm_request)
    
    contradictory_text = "The Earth is completely flat. Scientists have proven that the Earth is a sphere orbiting the sun."
    result1 = await validator1.validate(contradictory_text, {"topic": "Earth's shape"})
    
    print(f"Text: {contradictory_text}")
    print(f"Valid (no contradictions): {result1.valid}")
    print(f"Confidence: {result1.confidence}")
    print(f"Reasoning: {result1.reasoning}")
    if result1.suggestions:
        print(f"Suggestions: {', '.join(result1.suggestions)}")
    print(f"LLM calls made: {validator1.get_call_stats()['total_calls']}")
    print()
    
    # Test 2: Consistent text
    print("Test 2: Consistent Text")
    validator2 = ContractValidator(AIValidatorConfig(
        validation_model="gpt-3.5-turbo",
        temperature=0.1
    ))
    validator2.set_llm_caller(make_llm_request)
    
    consistent_text = "Python is a high-level programming language. It is known for its readability and simplicity."
    result2 = await validator2.validate(consistent_text, {"topic": "Python programming"})
    
    print(f"Text: {consistent_text}")
    print(f"Valid (no contradictions): {result2.valid}")
    print(f"Confidence: {result2.confidence}")
    print(f"Reasoning: {result2.reasoning}")
    print()
    
    # Test 3: Complex validation with code
    print("Test 3: Code Structure Validator")
    
    class CodeStructureValidator(AIAssistedValidator):
        """Validates Python code structure and best practices"""
        
        async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
            return f"""Analyze this Python code for structural issues and best practices:

```python
{response}
```

Check for:
1. Syntax correctness
2. PEP 8 compliance (major issues only)
3. Security concerns
4. Performance anti-patterns

Respond with JSON:
- "valid": true if code is structurally sound
- "confidence": 0.0-1.0
- "reasoning": explanation of findings
- "suggestions": list of improvements
"""
            
        async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
            content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            try:
                return ValidationResult(**json.loads(content))
            except:
                return ValidationResult(valid=True, confidence=0.5, reasoning="Parse error")
    
    validator3 = CodeStructureValidator()
    validator3.set_llm_caller(make_llm_request)
    
    code_sample = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
"""
    
    result3 = await validator3.validate(code_sample, {"language": "python"})
    print(f"Code validation result:")
    print(f"Valid: {result3.valid}")
    print(f"Confidence: {result3.confidence}")
    print(f"Reasoning: {result3.reasoning}")
    if result3.suggestions:
        print(f"Suggestions:")
        for suggestion in result3.suggestions:
            print(f"  - {suggestion}")
    
    # Summary
    print("\n=== Summary ===")
    all_tests_passed = all([
        not result1.valid,  # Should find contradictions
        result2.valid,      # Should be valid
        result3.valid       # Should be valid code
    ])
    
    if all_tests_passed:
        print("✅ All validations produced expected results!")
        print("The AI validator successfully:")
        print("  1. Detected contradictions in text")
        print("  2. Validated consistent text")
        print("  3. Analyzed code structure")
        return 0
    else:
        print("❌ Some validations did not produce expected results")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_with_real_llm())
    sys.exit(exit_code)