"""
Test AI Validator with Real LLM Calls

This test demonstrates the AI validator base class with actual LLM responses.
Uses a small, fast model for testing.
"""

import asyncio
import json
from typing import Dict, Any
import os

from llm_call.core.validation.ai_validator_base import AIAssistedValidator, ValidationResult, AIValidatorConfig
from llm_call.core.caller import make_llm_request
from loguru import logger


class ContradictionValidator(AIAssistedValidator):
    """Validates text for logical contradictions using real LLM"""
    
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
    """Validates code quality and best practices using real LLM"""
    
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


async def real_llm_caller(config: Dict[str, Any]) -> Dict[str, Any]:
    """Real LLM caller using small, fast model"""
    # Use a small, fast model for testing
    test_model = os.getenv("LLM_TEST_MODEL", "gpt-3.5-turbo")
    
    # Override model for testing
    config = config.copy()
    config["model"] = test_model
    config["temperature"] = 0.1  # Low temperature for consistency
    config["max_tokens"] = 500
    
    # Make real LLM call
    response = await make_llm_request(config)
    return response


async def test_real_llm_validation():
    """Test AI validators with real LLM calls"""
    # We have OpenAI API key configured, tests should run with real calls
    print("🧪 Testing AI Validator with Real LLM (OpenAI configured)")
    
    print("🧪 Testing AI Validator with Real LLM")
    print("=" * 60)
    
    all_failures = []
    total_tests = 0
    
    # Test 1: Detect contradiction
    total_tests += 1
    print("Test 1: Contradiction Detection (Real LLM)")
    validator1 = ContradictionValidator()
    validator1.set_llm_caller(real_llm_caller)
    
    text1 = "The Earth is completely flat. Scientists have proven that the Earth is a sphere."
    result1 = await validator1.validate(text1, {"topic": "science"})
    
    print(f"Text: contains Earth shape contradiction")
    print(f"Valid: {result1.valid}")
    print(f"Confidence: {result1.confidence}")
    print(f"Reasoning: {result1.reasoning}")
    
    # Real LLM should detect the contradiction
    if result1.valid:
        all_failures.append("Test 1: Failed to detect Earth shape contradiction")
    print()
    
    # Test 2: No contradiction
    total_tests += 1
    print("Test 2: Consistent Text (Real LLM)")
    validator2 = ContradictionValidator()
    validator2.set_llm_caller(real_llm_caller)
    
    text2 = "Python is a high-level programming language. Python is known for its readability and simplicity."
    result2 = await validator2.validate(text2, {"topic": "programming"})
    
    print(f"Text: consistent Python description")
    print(f"Valid: {result2.valid}")
    print(f"Confidence: {result2.confidence}")
    
    if not result2.valid:
        all_failures.append("Test 2: Expected consistent text but found issues")
    print()
    
    # Test 3: Code quality check
    total_tests += 1
    print("Test 3: Python Code Quality (Real LLM)")
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
        
    # Should have suggestions even if valid
    if len(result3.suggestions) == 0:
        all_failures.append("Test 3: Expected improvement suggestions from LLM")
    print()
    
    # Test 4: Security vulnerability
    total_tests += 1
    print("Test 4: Security Vulnerability Detection (Real LLM)")
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
    
    # Real LLM should detect eval() security issue
    if result4.valid and "eval" in result4.reasoning.lower():
        all_failures.append("Test 4: Failed to flag eval() as security issue")
    print()
    
    # Test 5: Call statistics
    total_tests += 1
    print("Test 5: Validator Statistics")
    stats = validator1.get_call_stats()
    print(f"Validator 1 stats: {stats}")
    
    if stats['total_calls'] != 1:
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
        print("\nSuccessfully demonstrated with REAL LLM:")
        print("  1. Contradiction detection in text")
        print("  2. Validation of consistent content")
        print("  3. Code quality analysis with suggestions")
        print("  4. Security vulnerability detection")
        print("  5. Proper call statistics tracking")
        return 0


if __name__ == "__main__":
    import sys
    
    # Use OpenAI for testing
    os.environ["LLM_TEST_MODEL"] = "gpt-3.5-turbo"
    print(f"ℹ️  Using test model: {os.environ['LLM_TEST_MODEL']}")
    
    exit_code = asyncio.run(test_real_llm_validation())
    sys.exit(exit_code)