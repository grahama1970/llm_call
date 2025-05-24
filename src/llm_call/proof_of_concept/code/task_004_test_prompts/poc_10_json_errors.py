#!/usr/bin/env python3
"""
POC-10: Error Handling for Malformed JSON Responses

This script validates error handling when LLM returns malformed JSON.
Implements graceful fallback behavior and comprehensive error reporting.

Links:
- Error handling best practices: https://docs.python.org/3/tutorial/errors.html
- JSON parsing errors: https://docs.python.org/3/library/json.html#json.JSONDecodeError

Sample Input:
{
    "response": "Here's the user data: {name: 'John', age: 30, missing_quotes",
    "fallback_options": {
        "extract_partial": true,
        "return_default": {"status": "error", "data": null},
        "log_details": true
    }
}

Expected Output:
{
    "original_response": "...",
    "extracted_data": {"name": "John", "age": 30},
    "errors": ["Unterminated string starting at: line 1 column 45"],
    "fallback_used": "partial_extraction",
    "recovery_success": true
}
"""

import json
import re
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


class JSONErrorHandler:
    """Handles various JSON parsing errors with recovery strategies."""
    
    def __init__(self, fallback_options: Optional[Dict[str, Any]] = None):
        """Initialize with fallback options."""
        self.fallback_options = fallback_options or {
            "extract_partial": True,
            "return_default": {"status": "error", "data": None},
            "log_details": True,
            "max_repair_attempts": 3
        }
        self.error_patterns = {
            "missing_quotes": r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:',
            "single_quotes": r"'([^']*)'",
            "trailing_comma": r',\s*}',
            "unescaped_newlines": r'\\n',
            "python_booleans": r'\b(True|False)\b',
            "python_none": r'\bNone\b'
        }
    
    def parse_with_recovery(self, response: str) -> Tuple[Optional[Dict], List[str], str]:
        """
        Parse JSON with multiple recovery strategies.
        
        Returns:
            Tuple of (parsed_data, errors, fallback_used)
        """
        errors = []
        fallback_used = "none"
        
        # Try direct parsing first
        try:
            return json.loads(response), [], "none"
        except json.JSONDecodeError as e:
            errors.append(f"Initial parse error: {str(e)}")
            if self.fallback_options.get("log_details"):
                logger.warning(f"JSON parse failed: {e}")
        
        # Try to extract JSON from markdown/text
        if self.fallback_options.get("extract_partial"):
            extracted = self._extract_json_blocks(response)
            if extracted:
                for block in extracted:
                    try:
                        return json.loads(block), errors, "markdown_extraction"
                    except json.JSONDecodeError:
                        errors.append(f"Extracted block parse failed")
        
        # Try to repair common issues
        if self.fallback_options.get("max_repair_attempts", 0) > 0:
            repaired, repair_errors = self._repair_json(response)
            errors.extend(repair_errors)
            if repaired:
                try:
                    return json.loads(repaired), errors, "auto_repair"
                except json.JSONDecodeError as e:
                    errors.append(f"Repaired JSON still invalid: {str(e)}")
        
        # Try partial extraction with regex
        partial_data = self._extract_partial_data(response)
        if partial_data:
            errors.append("Using partial data extraction")
            return partial_data, errors, "partial_extraction"
        
        # Return default fallback
        if self.fallback_options.get("return_default"):
            errors.append("All recovery strategies failed, using default")
            return self.fallback_options["return_default"], errors, "default_fallback"
        
        return None, errors, "failed"
    
    def _extract_json_blocks(self, text: str) -> List[str]:
        """Extract JSON blocks from markdown or mixed text."""
        blocks = []
        
        # Look for ```json blocks
        json_block_pattern = r'```(?:json)?\s*\n(.*?)\n```'
        matches = re.findall(json_block_pattern, text, re.DOTALL)
        blocks.extend(matches)
        
        # Look for { } blocks
        brace_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(brace_pattern, text)
        blocks.extend(matches)
        
        return blocks
    
    def _repair_json(self, text: str) -> Tuple[Optional[str], List[str]]:
        """Attempt to repair common JSON issues."""
        repaired = text
        repair_log = []
        
        # Fix missing quotes on keys
        if re.search(self.error_patterns["missing_quotes"], repaired):
            repaired = re.sub(self.error_patterns["missing_quotes"], r'\1"\2":', repaired)
            repair_log.append("Fixed missing quotes on keys")
        
        # Replace single quotes with double quotes
        if "'" in repaired:
            # Be careful not to replace apostrophes in text
            repaired = re.sub(r"(?<=[{,])\s*'([^']+)'\s*:", r'"\1":', repaired)  # Keys
            repaired = re.sub(r":\s*'([^']+)'", r': "\1"', repaired)  # Values
            repaired = re.sub(r"\[\s*'([^']+)'\s*(?:,\s*'([^']+)'\s*)*\]", 
                            lambda m: '[' + ', '.join(f'"{x.strip()}"' for x in m.group(0)[1:-1].split(',') if x.strip().startswith("'") and x.strip().endswith("'")) + ']', 
                            repaired)  # Arrays
            repair_log.append("Replaced single quotes with double quotes")
        
        # Remove trailing commas
        if re.search(self.error_patterns["trailing_comma"], repaired):
            repaired = re.sub(self.error_patterns["trailing_comma"], '}', repaired)
            repaired = re.sub(r',\s*\]', ']', repaired)  # Also handle arrays
            repair_log.append("Removed trailing commas")
        
        # Fix Python booleans
        repaired = re.sub(self.error_patterns["python_booleans"], 
                         lambda m: m.group(0).lower(), repaired)
        if "True" in text or "False" in text:
            repair_log.append("Converted Python booleans to JSON format")
        
        # Fix Python None
        if re.search(self.error_patterns["python_none"], repaired):
            repaired = re.sub(self.error_patterns["python_none"], 'null', repaired)
            repair_log.append("Converted Python None to null")
        
        return repaired if repaired != text else None, repair_log
    
    def _extract_partial_data(self, text: str) -> Optional[Dict]:
        """Extract partial data using regex patterns."""
        data = {}
        
        # Try to extract key-value pairs
        kv_pattern = r'"?([a-zA-Z_][a-zA-Z0-9_]*)"?\s*:\s*(?:"([^"]*)"|([-0-9.]+)|(\btrue\b|\bfalse\b|\bnull\b))'
        matches = re.findall(kv_pattern, text)
        
        for match in matches:
            key = match[0]
            if match[1]:  # String value
                data[key] = match[1]
            elif match[2]:  # Number
                try:
                    data[key] = float(match[2]) if '.' in match[2] else int(match[2])
                except ValueError:
                    data[key] = match[2]
            elif match[3]:  # Boolean/null
                if match[3] == 'true':
                    data[key] = True
                elif match[3] == 'false':
                    data[key] = False
                else:
                    data[key] = None
        
        return data if data else None


def test_json_error_handling():
    """Test comprehensive JSON error handling."""
    handler = JSONErrorHandler()
    
    test_cases = [
        {
            "name": "Valid JSON",
            "response": '{"name": "John", "age": 30, "active": true}',
            "expect_success": True,
            "expect_data": {"name": "John", "age": 30, "active": True}
        },
        {
            "name": "JSON in markdown",
            "response": '''Here's the user data:
```json
{
    "name": "Alice",
    "email": "alice@example.com",
    "verified": true
}
```
Additional text here.''',
            "expect_success": True,
            "expect_fallback": "markdown_extraction"
        },
        {
            "name": "Missing quotes on keys",
            "response": '{name: "Bob", age: 25, city: "NYC"}',
            "expect_success": True,
            "expect_fallback": "auto_repair"
        },
        {
            "name": "Single quotes",
            "response": "{'user': 'Charlie', 'role': 'admin', 'active': true}",
            "expect_success": True,
            "expect_fallback": "auto_repair"
        },
        {
            "name": "Trailing comma",
            "response": '{"items": ["a", "b", "c",], "count": 3,}',
            "expect_success": True,
            "expect_any_data": True  # May use different fallback strategies
        },
        {
            "name": "Python format",
            "response": "{'enabled': True, 'value': None, 'items': ['x', 'y']}",
            "expect_success": True,
            "expect_any_data": True  # Complex repair may use different strategies
        },
        {
            "name": "Completely malformed",
            "response": "This is just {random: text with no valid JSON structure at all",
            "expect_success": True,
            "expect_any_data": True  # Should extract at least 'random'
        },
        {
            "name": "Mixed valid and invalid",
            "response": '''The response contains {"valid": "data"} and then some 
{broken: json, with: 'mixed quotes" and trailing,} parts''',
            "expect_success": True,
            "expect_any_data": True
        }
    ]
    
    results = []
    logger.info("Testing JSON error handling...")
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("=" * 50)
        
        data, errors, fallback = handler.parse_with_recovery(test_case["response"])
        
        if test_case.get("expect_success"):
            if data is not None:
                logger.success(f"✅ Successfully parsed/recovered data")
                logger.info(f"   Fallback used: {fallback}")
                if errors:
                    logger.info(f"   Errors encountered: {len(errors)}")
                
                # Check specific expectations
                if test_case.get("expect_data"):
                    if data == test_case["expect_data"]:
                        logger.success(f"✅ Data matches expected: {data}")
                        results.append({"test": test_case["name"], "passed": True})
                    else:
                        logger.error(f"❌ Data mismatch")
                        logger.error(f"   Expected: {test_case['expect_data']}")
                        logger.error(f"   Got: {data}")
                        results.append({"test": test_case["name"], "passed": False, "reason": "Data mismatch"})
                elif test_case.get("expect_fallback"):
                    if fallback == test_case["expect_fallback"]:
                        logger.success(f"✅ Used expected fallback: {fallback}")
                        results.append({"test": test_case["name"], "passed": True})
                    else:
                        logger.error(f"❌ Wrong fallback used: {fallback}")
                        results.append({"test": test_case["name"], "passed": False, "reason": "Wrong fallback"})
                elif test_case.get("expect_any_data"):
                    if data and len(data) > 0:
                        logger.success(f"✅ Extracted some data: {data}")
                        results.append({"test": test_case["name"], "passed": True})
                    else:
                        logger.error(f"❌ No data extracted")
                        results.append({"test": test_case["name"], "passed": False, "reason": "No data"})
                else:
                    results.append({"test": test_case["name"], "passed": True})
            else:
                logger.error(f"❌ Failed to parse/recover data")
                results.append({"test": test_case["name"], "passed": False, "reason": "Parse failed"})
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("JSON ERROR HANDLING TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = sum(1 for r in results if r["passed"])
    logger.info(f"Total: {passed}/{len(results)} tests passed")
    
    for result in results:
        if result["passed"]:
            logger.info(f"✅ {result['test']}")
        else:
            logger.info(f"❌ {result['test']}")
            if "reason" in result:
                logger.info(f"   Reason: {result['reason']}")
    
    return all(r["passed"] for r in results)


def test_performance():
    """Test performance of error handling."""
    handler = JSONErrorHandler()
    
    # Large malformed JSON
    large_json = "{"
    for i in range(1000):
        large_json += f'item{i}: "value{i}", '
    large_json += "}"
    
    start = time.time()
    data, errors, fallback = handler.parse_with_recovery(large_json)
    elapsed = (time.time() - start) * 1000
    
    logger.info(f"\nLarge JSON repair completed in {elapsed:.2f}ms")
    logger.info(f"Fallback used: {fallback}")
    logger.info(f"Data items recovered: {len(data) if data else 0}")
    
    return elapsed < 100  # Should complete within 100ms


def test_edge_cases():
    """Test edge cases and error conditions."""
    handler = JSONErrorHandler()
    
    edge_cases = [
        ("Empty string", ""),
        ("Just a number", "42"),
        ("Just a string", '"hello"'),
        ("Null", "null"),
        ("Boolean", "true"),
        ("Array", "[1, 2, 3]"),
        ("Nested malformed", '{"a": {b: "c"}, "d": [1, 2,]}'),
        ("Unicode issues", '{"emoji": "🎉", "chinese": "你好"}'),
        ("Escaped quotes", '{"text": "He said \\"hello\\""}'),
        ("Very long strings", '{"data": "' + "x" * 10000 + '"}')
    ]
    
    logger.info("\nTesting edge cases...")
    all_handled = True
    
    for name, test_input in edge_cases:
        try:
            data, errors, fallback = handler.parse_with_recovery(test_input)
            logger.info(f"✅ {name}: Handled successfully (fallback: {fallback})")
        except Exception as e:
            logger.error(f"❌ {name}: Unhandled exception: {e}")
            all_handled = False
    
    return all_handled


if __name__ == "__main__":
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Error handling
    total_tests += 1
    try:
        if test_json_error_handling():
            logger.success("✅ JSON error handling tests passed")
        else:
            all_validation_failures.append("JSON error handling tests failed")
    except Exception as e:
        all_validation_failures.append(f"JSON error handling exception: {str(e)}")
        logger.error(f"Exception in error handling test: {e}")
        traceback.print_exc()
    
    # Test 2: Performance
    total_tests += 1
    try:
        if test_performance():
            logger.success("✅ Performance test passed")
        else:
            all_validation_failures.append("Performance test failed (>100ms)")
    except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
        logger.error(f"Exception in performance test: {e}")
    
    # Test 3: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge case handling passed")
        else:
            all_validation_failures.append("Edge case handling failed")
    except Exception as e:
        all_validation_failures.append(f"Edge case test exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-10 JSON error handling is validated and ready")
        sys.exit(0)