"""
Test AI Validator with Realistic Mock LLM

This test demonstrates the AI validator base class with realistic mock responses
that simulate actual LLM behavior.
"""

import asyncio
import json
from typing import Dict, Any

from llm_call.core.validation.ai_validator_base import AIAssistedValidator, ValidationResult, AIValidatorConfig
from loguru import logger


class ContradictionValidator(AIAssistedValidator):
    """Validates text for logical contradictions"""
    
    async def build_validation_prompt(self, response: str, context: Dict[str, Any]) -> str:
        """Build prompt to check for contradictions"""
        return f"""Analyze the following text for logical contradictions:

Text: "{response}"

Topic context: {context.get('topic', 'general')}

Check for:
1. Direct contradictions (opposing statements)
2. Logical inconsistencies
3. Factual errors

Respond with JSON containing:
- "valid": false if contradictions found, true if consistent
- "confidence": 0.0 to 1.0
- "reasoning": explanation of findings
- "suggestions": list of suggestions to resolve issues
"""
        
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse the validation response"""
        content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        try:
            parsed = json.loads(content)
            return ValidationResult(**parsed)
        except Exception as e:
            logger.error(f"Parse error: {e}")
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
        return f"""Analyze this {lang} code for quality issues:

```{lang}
{response}
```

Evaluate:
1. Syntax correctness
2. Best practices violations
3. Performance issues
4. Security concerns

Respond with JSON:
- "valid": true if code meets quality standards
- "confidence": 0.0 to 1.0
- "reasoning": detailed analysis
- "suggestions": specific improvements
"""
        
    async def parse_validation_response(self, llm_response: Dict[str, Any]) -> ValidationResult:
        """Parse code validation response"""
        content = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        
        try:
            parsed = json.loads(content)
            return ValidationResult(**parsed)
        except:
            return ValidationResult(valid=True, confidence=0.5, reasoning="Parse error")


async def realistic_mock_llm(config: Dict[str, Any]) -> Dict[str, Any]:
    """Realistic mock LLM that simulates actual responses"""
    prompt = config["messages"][-1]["content"]
    
    # Simulate processing delay
    await asyncio.sleep(0.1)
    
    # Generate realistic responses based on content
    if "flat" in prompt.lower() and "sphere" in prompt.lower():
        # Contradiction about Earth's shape
        response = {
            "valid": False,
            "confidence": 0.95,
            "reasoning": "The text contains a direct contradiction: it states the Earth is 'completely flat' while also saying 'Scientists have proven that the Earth is a sphere'. These are mutually exclusive statements.",
            "suggestions": [
                "Remove the contradictory statement about Earth being flat",
                "Clarify which position is being taken",
                "Add context if discussing historical perspectives vs current science"
            ]
        }
    elif "high-level programming language" in prompt.lower():
        # Consistent Python description
        response = {
            "valid": True,
            "confidence": 0.98,
            "reasoning": "The text is internally consistent. Both statements about Python being high-level and known for readability/simplicity are accurate and non-contradictory.",
            "suggestions": []
        }
    elif "range(len(data))" in prompt:
        # Code with minor issues
        response = {
            "valid": True,
            "confidence": 0.8,
            "reasoning": "The code is syntactically correct and functional, but uses non-Pythonic patterns.",
            "suggestions": [
                "Use 'for item in data:' instead of 'for i in range(len(data))'",
                "Consider list comprehension: [x * 2 for x in data if x > 0]",
                "Add type hints for better code documentation"
            ]
        }
    elif "eval(" in prompt.lower() or "exec(" in prompt.lower():
        # Security issue
        response = {
            "valid": False,
            "confidence": 0.99,
            "reasoning": "Critical security vulnerability: using eval() or exec() with user input can lead to arbitrary code execution.",
            "suggestions": [
                "Use ast.literal_eval() for safe evaluation of literals",
                "Parse input manually instead of using eval()",
                "Implement proper input validation and sanitization"
            ]
        }
    else:
        # Generic response
        response = {
            "valid": True,
            "confidence": 0.7,
            "reasoning": "No specific issues detected in the provided content.",
            "suggestions": []
        }
    
    # Format as LLM API response
    return {
        "choices": [{
            "message": {
                "content": json.dumps(response),
                "role": "assistant"
            }
        }],
        "usage": {"total_tokens": len(prompt) // 4}
    }


async def test_realistic_validation():
    """Test validators with realistic mock responses"""
    print("=== Testing AI Validators with Realistic Mocks ===\n")
    
    all_failures = []
    total_tests = 0
    
    # Test 1: Contradiction detection
    total_tests += 1
    print("Test 1: Earth Shape Contradiction")
    validator1 = ContradictionValidator(AIValidatorConfig(temperature=0.1))
    validator1.set_llm_caller(realistic_mock_llm)
    
    text1 = "The Earth is completely flat. Scientists have proven that the Earth is a sphere orbiting the sun."
    result1 = await validator1.validate(text1, {"topic": "Earth's shape"})
    
    print(f"Text: {text1[:50]}...")
    print(f"Valid: {result1.valid}")
    print(f"Confidence: {result1.confidence}")
    print(f"Reasoning: {result1.reasoning}")
    
    if result1.valid:  # Should be False (contradiction found)
        all_failures.append("Test 1: Expected to find contradiction but didn't")
    print()
    
    # Test 2: Consistent text
    total_tests += 1
    print("Test 2: Python Description (Consistent)")
    validator2 = ContradictionValidator()
    validator2.set_llm_caller(realistic_mock_llm)
    
    text2 = "Python is a high-level programming language. It is known for its readability and simplicity."
    result2 = await validator2.validate(text2, {"topic": "Python"})
    
    print(f"Text: {text2[:50]}...")
    print(f"Valid: {result2.valid}")
    print(f"Confidence: {result2.confidence}")
    
    if not result2.valid:  # Should be True (no contradiction)
        all_failures.append("Test 2: Expected consistent text but found issues")
    print()
    
    # Test 3: Code quality check
    total_tests += 1
    print("Test 3: Python Code Quality")
    validator3 = CodeQualityValidator()
    validator3.set_llm_caller(realistic_mock_llm)
    
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
        
    if not result3.valid or len(result3.suggestions) == 0:
        all_failures.append("Test 3: Expected valid code with improvement suggestions")
    print()
    
    # Test 4: Security vulnerability
    total_tests += 1
    print("Test 4: Security Vulnerability Detection")
    validator4 = CodeQualityValidator(AIValidatorConfig(validation_model="security-focused"))
    validator4.set_llm_caller(realistic_mock_llm)
    
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
    
    if result4.valid:  # Should be False (security issue)
        all_failures.append("Test 4: Failed to detect security vulnerability")
    print()
    
    # Test 5: Recursive validation capability
    total_tests += 1
    print("Test 5: Validator Statistics")
    print(f"Validator 1 stats: {validator1.get_call_stats()}")
    print(f"Validator 3 had {len(result3.suggestions)} suggestions")
    
    if validator1.get_call_stats()['total_calls'] != 1:
        all_failures.append("Test 5: Expected exactly 1 LLM call")
    
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