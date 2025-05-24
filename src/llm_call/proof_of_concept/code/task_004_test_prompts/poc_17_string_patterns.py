#!/usr/bin/env python3
"""
POC 17: String Pattern Validation
Task: Implement regex patterns for common string validations
Expected Output: Validation results for email, URL, phone, and custom patterns
Links:
- https://docs.python.org/3/library/re.html
- https://emailregex.com/
- https://regexr.com/
"""

import re
from typing import Dict, List, Optional, Pattern, Tuple
from dataclasses import dataclass
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class ValidationResult:
    """Result of a pattern validation"""
    is_valid: bool
    pattern_name: str
    value: str
    error_message: Optional[str] = None
    matches: Optional[Dict[str, str]] = None


class StringPatternValidator:
    """Validates strings against common and custom patterns"""
    
    def __init__(self):
        # Compile patterns for better performance
        self.patterns: Dict[str, Pattern] = {
            # Email pattern - RFC 5322 simplified
            "email": re.compile(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            ),
            
            # URL pattern - HTTP/HTTPS with optional www
            "url": re.compile(
                r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
            ),
            
            # Phone pattern - E.164 format
            "phone": re.compile(
                r'^\+?[1-9]\d{1,14}$'
            ),
            
            # UUID pattern
            "uuid": re.compile(
                r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
            ),
            
            # ISO date pattern (YYYY-MM-DD)
            "iso_date": re.compile(
                r'^(?P<year>\d{4})-(?P<month>0[1-9]|1[0-2])-(?P<day>0[1-9]|[12]\d|3[01])$'
            ),
            
            # Credit card pattern (simplified - just format)
            "credit_card": re.compile(
                r'^[0-9]{13,19}$'
            ),
            
            # IPv4 pattern
            "ipv4": re.compile(
                r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            ),
            
            # Semantic version pattern
            "semver": re.compile(
                r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
            )
        }
    
    def validate(self, value: str, pattern_name: str) -> ValidationResult:
        """Validate a string against a named pattern"""
        if pattern_name not in self.patterns:
            return ValidationResult(
                is_valid=False,
                pattern_name=pattern_name,
                value=value,
                error_message=f"Unknown pattern: {pattern_name}"
            )
        
        pattern = self.patterns[pattern_name]
        match = pattern.fullmatch(value)
        
        if match:
            # Extract named groups if any
            matches = match.groupdict() if match.groupdict() else None
            return ValidationResult(
                is_valid=True,
                pattern_name=pattern_name,
                value=value,
                matches=matches
            )
        else:
            return ValidationResult(
                is_valid=False,
                pattern_name=pattern_name,
                value=value,
                error_message=f"Value does not match {pattern_name} pattern"
            )
    
    def add_custom_pattern(self, name: str, pattern: str) -> None:
        """Add a custom pattern for validation"""
        try:
            compiled = re.compile(pattern)
            self.patterns[name] = compiled
            logger.info(f"Added custom pattern: {name}")
        except re.error as e:
            logger.error(f"Invalid regex pattern for {name}: {e}")
            raise
    
    def validate_batch(self, values: List[Tuple[str, str]]) -> List[ValidationResult]:
        """Validate multiple values against their patterns"""
        results = []
        for value, pattern_name in values:
            result = self.validate(value, pattern_name)
            results.append(result)
            
            if result.is_valid:
                logger.success(f"✅ {pattern_name}: '{value}' is valid")
                if result.matches:
                    logger.info(f"   Captured groups: {result.matches}")
            else:
                logger.error(f"❌ {pattern_name}: '{value}' - {result.error_message}")
        
        return results


def main():
    """Test string pattern validation with various examples"""
    validator = StringPatternValidator()
    
    # Test cases
    test_cases = [
        # Email tests
        ("user@example.com", "email", True),
        ("john.doe+tag@company.co.uk", "email", True),
        ("invalid.email@", "email", False),
        ("@invalid.com", "email", False),
        ("user@.com", "email", False),
        
        # URL tests
        ("https://www.example.com", "url", True),
        ("http://subdomain.example.com/path?query=value", "url", True),
        ("https://example.com:8080/path", "url", True),
        ("ftp://example.com", "url", False),
        ("not-a-url", "url", False),
        
        # Phone tests
        ("+14155552671", "phone", True),
        ("14155552671", "phone", True),
        ("+1234567890123456", "phone", False),  # Too long
        ("0123456789", "phone", False),  # Starts with 0
        
        # UUID tests
        ("550e8400-e29b-41d4-a716-446655440000", "uuid", True),
        ("550e8400-e29b-11d4-a716-446655440000", "uuid", True),
        ("not-a-uuid", "uuid", False),
        
        # ISO date tests
        ("2024-03-15", "iso_date", True),
        ("2024-13-01", "iso_date", False),  # Invalid month
        ("2024-02-30", "iso_date", True),  # Note: Format is valid, actual date validation would need calendar logic
        
        # IPv4 tests
        ("192.168.1.1", "ipv4", True),
        ("255.255.255.255", "ipv4", True),
        ("256.1.1.1", "ipv4", False),  # Out of range
        ("192.168.1", "ipv4", False),  # Missing octet
        
        # Semantic version tests
        ("1.0.0", "semver", True),
        ("2.1.0-beta.1", "semver", True),
        ("3.0.0-rc.1+build.123", "semver", True),
        ("1.0", "semver", False),  # Missing patch
    ]
    
    logger.info("=" * 50)
    logger.info("Testing string pattern validation")
    logger.info("=" * 50)
    
    # Track results
    passed = 0
    failed = 0
    
    for value, pattern, expected in test_cases:
        result = validator.validate(value, pattern)
        
        if result.is_valid == expected:
            passed += 1
            logger.success(f"✅ {pattern}: '{value}' -> {result.is_valid} (expected)")
            if result.matches:
                logger.info(f"   Captured: {result.matches}")
        else:
            failed += 1
            logger.error(f"❌ {pattern}: '{value}' -> {result.is_valid} (expected {expected})")
            if result.error_message:
                logger.error(f"   Error: {result.error_message}")
    
    # Test custom patterns
    logger.info("\n" + "=" * 50)
    logger.info("Testing custom patterns")
    logger.info("=" * 50)
    
    # Add custom pattern for product SKU
    validator.add_custom_pattern(
        "product_sku",
        r'^(?P<category>[A-Z]{3})-(?P<id>\d{4})-(?P<variant>[A-Z]{2})$'
    )
    
    custom_tests = [
        ("ABC-1234-XL", "product_sku", True),
        ("DEF-5678-SM", "product_sku", True),
        ("abc-1234-xl", "product_sku", False),  # Lowercase
        ("AB-1234-XL", "product_sku", False),   # Wrong format
    ]
    
    for value, pattern, expected in custom_tests:
        result = validator.validate(value, pattern)
        
        if result.is_valid == expected:
            passed += 1
            logger.success(f"✅ {pattern}: '{value}' -> {result.is_valid} (expected)")
            if result.matches:
                logger.info(f"   Captured: {result.matches}")
        else:
            failed += 1
            logger.error(f"❌ {pattern}: '{value}' -> {result.is_valid} (expected {expected})")
    
    # Test batch validation
    logger.info("\n" + "=" * 50)
    logger.info("Testing batch validation")
    logger.info("=" * 50)
    
    batch_values = [
        ("contact@company.com", "email"),
        ("https://api.company.com/v1", "url"),
        ("+12025551234", "phone"),
        ("192.168.0.1", "ipv4"),
        ("4.2.0-alpha.1", "semver"),
    ]
    
    results = validator.validate_batch(batch_values)
    
    # All batch values should be valid
    batch_valid = all(r.is_valid for r in results)
    if batch_valid:
        passed += 1
        logger.success("✅ All batch validations passed")
    else:
        failed += 1
        logger.error("❌ Some batch validations failed")
    
    # Final summary
    logger.info("\n" + "=" * 50)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 50)
    
    total_tests = passed + failed
    if failed == 0:
        logger.success(f"✅ ALL TESTS PASSED: {passed}/{total_tests}")
        sys.exit(0)
    else:
        logger.error(f"❌ TESTS FAILED: {failed}/{total_tests} failed")
        logger.info(f"Passed: {passed}, Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()