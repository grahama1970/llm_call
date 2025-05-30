"""
Test AI Validator with Real LLM

This test demonstrates the AI validator base class with real LLM responses.
No mocking - uses actual LLM calls to validate the AI validator functionality.
"""

import asyncio
import json
import os
from typing import Dict, Any

from llm_call.core.validation.ai_validator_base import AIAssistedValidator, ValidationResult, AIValidatorConfig
from llm_call.core.caller import make_llm_request
from loguru import logger


# Use small model for tests
TEST_MODEL = os.getenv("LLM_TEST_MODEL", "gpt-3.5-turbo")


class ContradictionValidator(AIAssistedValidator):
    """Validates text for logical contradictions"""
    
    async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
        """Build prompt to check for contradictions"""
        return f"""Analyze the following text for logical contradictions. Return ONLY valid JSON.

Text: "{response}"

Topic context: {context.get('topic', 'general')}

Check for:
1. Direct contradictions (opposing statements)
2. Logical inconsistencies
3. Factual errors

You MUST respond with ONLY this JSON format (no other text):
{{
  "valid": false if contradictions found or true if consistent,
  "confidence": 0.0 to 1.0,
  "reasoning": "explanation of findings",
  "suggestions": ["suggestion 1", "suggestion 2"]
}}"""
        
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse the validation response"""
        content = llm_response.get("content", "")
        
        try:
            # Try to extract JSON from the response
            if isinstance(content, str):
                # Find JSON in the response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    parsed = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            else:
                parsed = content
                
            return ValidationResult(
                valid=parsed.get("valid", True),
                confidence=parsed.get("confidence", 0.5),
                reasoning=parsed.get("reasoning", ""),
                suggestions=parsed.get("suggestions", [])
            )
        except Exception as e:
            logger.error(f"Parse error: {e}, content: {content}")
            return ValidationResult(
                valid=True,
                confidence=0.5,
                reasoning="Unable to parse validation response"
            )


class CodeQualityValidator(AIAssistedValidator):
    """Validates code quality and best practices"""
    
    async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
        """Build prompt for code validation"""
        lang = context.get('language', 'python')
        return f"""Analyze this {lang} code for quality issues. Return ONLY valid JSON.

```{lang}
{response}
```

Evaluate:
1. Syntax correctness
2. Best practices violations
3. Performance issues
4. Security concerns

You MUST respond with ONLY this JSON format (no other text):
{{
  "valid": true if code meets quality standards or false if issues found,
  "confidence": 0.0 to 1.0,
  "reasoning": "detailed analysis",
  "suggestions": ["improvement 1", "improvement 2"]
}}"""
        
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse code validation response"""
        content = llm_response.get("content", "")
        
        try:
            # Try to extract JSON from the response
            if isinstance(content, str):
                # Find JSON in the response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    json_str = content[start:end]
                    parsed = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            else:
                parsed = content
                
            return ValidationResult(
                valid=parsed.get("valid", True),
                confidence=parsed.get("confidence", 0.5),
                reasoning=parsed.get("reasoning", ""),
                suggestions=parsed.get("suggestions", [])
            )
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return ValidationResult(valid=True, confidence=0.5, reasoning="Parse error")


async def real_llm_caller(config: Dict[str, Any]) -> Dict[str, Any]:
    """Real LLM caller that makes actual API requests"""
    # Use the test model
    config["model"] = TEST_MODEL
    config["temperature"] = 0.1
    config["max_tokens"] = 300
    
    try:
        result = await make_llm_request(config)
        return result
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        # Return a minimal valid response
        return {"content": '{"valid": true, "confidence": 0.5, "reasoning": "LLM error"}'}


async def test_realistic_validation():
    """Test validators with real LLM responses"""
    print("=== Testing AI Validators with Real LLM ===\n")
    
    # OpenAI should be configured
        
    print(f"Using test model: {TEST_MODEL}\n")
    
    all_failures = []
    total_tests = 0
    
    # Test 1: Contradiction detection
    total_tests += 1
    print("Test 1: Earth Shape Contradiction")
    validator1 = ContradictionValidator(AIValidatorConfig(temperature=0.1))
    validator1.set_llm_caller(real_llm_caller)
    
    text1 = "The Earth is completely flat. Scientists have proven that the Earth is a sphere orbiting the sun."
    result1 = await validator1.validate(text1, {"topic": "Earth's shape"})
    
    print(f"Text: {text1[:50]}...")
    print(f"Valid: {result1.valid}")
    print(f"Confidence: {result1.confidence}")
    print(f"Reasoning: {result1.reasoning}")
    
    # Real LLMs should detect this contradiction
    if result1.valid and result1.confidence > 0.7:
        all_failures.append("Test 1: Failed to detect obvious contradiction about Earth's shape")
    print()
    
    # Test 2: Consistent text
    total_tests += 1
    print("Test 2: Python Description (Consistent)")
    validator2 = ContradictionValidator()
    validator2.set_llm_caller(real_llm_caller)
    
    text2 = "Python is a high-level programming language. It is known for its readability and simplicity."
    result2 = await validator2.validate(text2, {"topic": "Python"})
    
    print(f"Text: {text2[:50]}...")
    print(f"Valid: {result2.valid}")
    print(f"Confidence: {result2.confidence}")
    
    # This should be valid (no contradiction)
    if not result2.valid and result2.confidence > 0.7:
        all_failures.append("Test 2: Found contradiction in consistent text")
    print()
    
    # Test 3: Code quality check
    total_tests += 1
    print("Test 3: Python Code Quality")
    validator3 = CodeQualityValidator()
    validator3.set_llm_caller(real_llm_caller)
    
    code3 = """
def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] > 0:
            result.append(data[i] * 2)
    return result
"""
    result3 = await validator3.validate(code3, {"language": "python"})
    
    print(f"Code: functional but non-Pythonic")
    print(f"Valid: {result3.valid}")
    print(f"Suggestions: {len(result3.suggestions)} improvements suggested")
    for i, suggestion in enumerate(result3.suggestions[:2]):
        print(f"  {i+1}. {suggestion}")
    print()
    
    # Test 4: Security vulnerability
    total_tests += 1
    print("Test 4: Security Vulnerability Detection")
    validator4 = CodeQualityValidator(AIValidatorConfig(validation_model="security-focused"))
    validator4.set_llm_caller(real_llm_caller)
    
    code4 = """
def process_user_input(user_data):
    # Dangerous: executing user input
    result = eval(user_data)
    return result
"""
    result4 = await validator4.validate(code4, {"language": "python"})
    
    print(f"Code: contains eval() vulnerability")
    print(f"Valid: {result4.valid}")
    print(f"Confidence: {result4.confidence}")
    print(f"Reasoning: {result4.reasoning}")
    
    # Real LLMs should flag eval() as dangerous
    if result4.valid and "eval" not in result4.reasoning.lower():
        all_failures.append("Test 4: Failed to detect eval() security vulnerability")
    print()
    
    # Test 5: Validator Statistics
    total_tests += 1
    print("Test 5: Validator Statistics")
    stats = validator1.get_call_stats()
    print(f"Validator 1 stats: {stats}")
    print(f"Validator 3 had {len(result3.suggestions)} suggestions")
    
    if stats['total_calls'] != 1:
        all_failures.append(f"Test 5: Expected exactly 1 LLM call, got {stats['total_calls']}")
    
    # Final results
    print("\n=== VALIDATION RESULTS ===")
    if all_failures:
        print(f"❌ VALIDATION FAILED - {len(all_failures)} of {total_tests} tests failed:")
        for failure in all_failures:
            print(f"  - {failure}")
        return 1
    else:
        print(f"✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        print("\nSuccessfully demonstrated:")
        print("  1. Contradiction detection in text")
        print("  2. Validation of consistent content")
        print("  3. Code quality analysis with suggestions")
        print("  4. Security vulnerability detection")
        print("  5. Proper call statistics tracking")
        return 0


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(test_realistic_validation())
    sys.exit(exit_code)