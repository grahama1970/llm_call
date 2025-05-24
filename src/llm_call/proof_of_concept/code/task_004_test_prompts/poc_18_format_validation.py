#!/usr/bin/env python3
"""
POC 18: Format Validation and Transformation
Task: Implement format validation with normalization and transformation
Expected Output: Validated and normalized data with transformation results
Links:
- https://pypi.org/project/phonenumbers/
- https://github.com/un33k/python-slugify
- https://pypi.org/project/python-dateutil/
"""

import re
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
import unicodedata
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


@dataclass
class FormatValidationResult:
    """Result of format validation and transformation"""
    original: str
    normalized: Optional[str]
    transformed: Optional[Any]
    is_valid: bool
    format_type: str
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class FormatValidator:
    """Validates and transforms string formats"""
    
    def __init__(self):
        self.formatters: Dict[str, Callable] = {
            "phone": self._format_phone,
            "email": self._format_email,
            "url": self._format_url,
            "slug": self._format_slug,
            "credit_card": self._format_credit_card,
            "postal_code": self._format_postal_code,
            "currency": self._format_currency,
            "percentage": self._format_percentage,
        }
    
    def _format_phone(self, value: str) -> FormatValidationResult:
        """Format and validate phone numbers"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', value)
        
        # Check for valid patterns
        patterns = [
            (r'^\+?1?(\d{10})$', 'US'),  # US number
            (r'^\+44(\d{10})$', 'UK'),   # UK number
            (r'^\+?(\d{10,15})$', 'International'),  # General international
        ]
        
        for pattern, region in patterns:
            match = re.match(pattern, cleaned)
            if match:
                digits = match.group(1) if match.lastindex else cleaned.lstrip('+')
                
                # Format based on region
                if region == 'US' and len(digits) == 10:
                    formatted = f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
                elif region == 'UK':
                    formatted = f"+44 {digits[:4]} {digits[4:7]} {digits[7:]}"
                else:
                    # Generic international format
                    formatted = f"+{cleaned.lstrip('+')}"
                
                return FormatValidationResult(
                    original=value,
                    normalized=cleaned,
                    transformed=formatted,
                    is_valid=True,
                    format_type="phone",
                    metadata={"region": region, "digits": len(digits)}
                )
        
        return FormatValidationResult(
            original=value,
            normalized=cleaned,
            transformed=None,
            is_valid=False,
            format_type="phone",
            errors=["Invalid phone number format"]
        )
    
    def _format_email(self, value: str) -> FormatValidationResult:
        """Format and validate email addresses"""
        # Normalize to lowercase and strip whitespace
        normalized = value.strip().lower()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, normalized):
            # Extract parts
            local, domain = normalized.split('@', 1)
            
            # Handle common transformations
            if domain in ['gmail.com', 'googlemail.com']:
                # Gmail ignores dots in local part
                canonical_local = local.replace('.', '')
                # Remove everything after + for Gmail
                if '+' in canonical_local:
                    canonical_local = canonical_local.split('+')[0]
                canonical = f"{canonical_local}@gmail.com"
            else:
                canonical = normalized
            
            return FormatValidationResult(
                original=value,
                normalized=normalized,
                transformed=canonical,
                is_valid=True,
                format_type="email",
                metadata={
                    "local": local,
                    "domain": domain,
                    "is_gmail": domain in ['gmail.com', 'googlemail.com']
                }
            )
        
        return FormatValidationResult(
            original=value,
            normalized=normalized,
            transformed=None,
            is_valid=False,
            format_type="email",
            errors=["Invalid email format"]
        )
    
    def _format_url(self, value: str) -> FormatValidationResult:
        """Format and validate URLs"""
        # Add protocol if missing
        url = value.strip()
        if not url.startswith(('http://', 'https://', '//')):
            url = 'https://' + url
        
        # Basic URL validation
        url_pattern = r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)$'
        
        if re.match(url_pattern, url):
            # Normalize URL
            normalized = url.lower()
            
            # Remove trailing slash
            if normalized.endswith('/') and normalized.count('/') > 2:
                normalized = normalized[:-1]
            
            # Remove www if present
            canonical = re.sub(r'://www\.', '://', normalized)
            
            return FormatValidationResult(
                original=value,
                normalized=normalized,
                transformed=canonical,
                is_valid=True,
                format_type="url",
                metadata={
                    "protocol": url.split('://')[0],
                    "has_www": 'www.' in url
                }
            )
        
        return FormatValidationResult(
            original=value,
            normalized=url,
            transformed=None,
            is_valid=False,
            format_type="url",
            errors=["Invalid URL format"]
        )
    
    def _format_slug(self, value: str) -> FormatValidationResult:
        """Convert text to URL-safe slug"""
        # Normalize unicode
        normalized = unicodedata.normalize('NFKD', value)
        # Remove non-ASCII
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        # Convert to lowercase and replace spaces/special chars
        slug = re.sub(r'[^\w\s-]', '', ascii_text).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        
        return FormatValidationResult(
            original=value,
            normalized=ascii_text,
            transformed=slug,
            is_valid=bool(slug),
            format_type="slug",
            metadata={
                "length": len(slug),
                "word_count": len(slug.split('-'))
            }
        )
    
    def _format_credit_card(self, value: str) -> FormatValidationResult:
        """Format and validate credit card numbers"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', value)
        
        # Check length
        if len(digits) < 13 or len(digits) > 19:
            return FormatValidationResult(
                original=value,
                normalized=digits,
                transformed=None,
                is_valid=False,
                format_type="credit_card",
                errors=["Invalid credit card length"]
            )
        
        # Luhn algorithm validation
        def luhn_check(card_number: str) -> bool:
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits_list = digits_of(card_number)
            odd_digits = digits_list[-1::-2]
            even_digits = digits_list[-2::-2]
            
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            
            return checksum % 10 == 0
        
        is_valid = luhn_check(digits)
        
        # Format with spaces
        if len(digits) == 16:
            formatted = f"{digits[:4]} {digits[4:8]} {digits[8:12]} {digits[12:]}"
        else:
            # Generic formatting for other lengths
            formatted = ' '.join(digits[i:i+4] for i in range(0, len(digits), 4))
        
        # Detect card type
        card_type = "Unknown"
        if digits.startswith('4'):
            card_type = "Visa"
        elif digits.startswith(('51', '52', '53', '54', '55')):
            card_type = "Mastercard"
        elif digits.startswith(('34', '37')):
            card_type = "American Express"
        
        return FormatValidationResult(
            original=value,
            normalized=digits,
            transformed=formatted if is_valid else None,
            is_valid=is_valid,
            format_type="credit_card",
            metadata={
                "card_type": card_type,
                "last_four": digits[-4:] if len(digits) >= 4 else "",
                "masked": f"{'*' * (len(digits) - 4)}{digits[-4:]}" if len(digits) >= 4 else ""
            },
            errors=[] if is_valid else ["Failed Luhn check"]
        )
    
    def _format_postal_code(self, value: str, country: str = "US") -> FormatValidationResult:
        """Format postal codes by country"""
        value = value.strip().upper()
        
        patterns = {
            "US": (r'^(\d{5})(-\d{4})?$', lambda m: m.group(0)),
            "UK": (r'^([A-Z]{1,2}\d{1,2}[A-Z]?)\s?(\d[A-Z]{2})$', lambda m: f"{m.group(1)} {m.group(2)}"),
            "CA": (r'^([A-Z]\d[A-Z])\s?(\d[A-Z]\d)$', lambda m: f"{m.group(1)} {m.group(2)}"),
        }
        
        if country in patterns:
            pattern, formatter = patterns[country]
            match = re.match(pattern, value.replace(' ', ''))
            
            if match:
                formatted = formatter(match)
                return FormatValidationResult(
                    original=value,
                    normalized=value.replace(' ', ''),
                    transformed=formatted,
                    is_valid=True,
                    format_type="postal_code",
                    metadata={"country": country}
                )
        
        return FormatValidationResult(
            original=value,
            normalized=value,
            transformed=None,
            is_valid=False,
            format_type="postal_code",
            errors=[f"Invalid {country} postal code format"]
        )
    
    def _format_currency(self, value: str) -> FormatValidationResult:
        """Format currency values"""
        # Remove currency symbols and whitespace
        cleaned = re.sub(r'[^\d\.\,\-]', '', value)
        # Handle different decimal separators
        cleaned = cleaned.replace(',', '')
        
        try:
            amount = float(cleaned)
            formatted = f"${amount:,.2f}"
            
            return FormatValidationResult(
                original=value,
                normalized=str(amount),
                transformed=formatted,
                is_valid=True,
                format_type="currency",
                metadata={
                    "amount": amount,
                    "cents": int(amount * 100)
                }
            )
        except ValueError:
            return FormatValidationResult(
                original=value,
                normalized=cleaned,
                transformed=None,
                is_valid=False,
                format_type="currency",
                errors=["Invalid currency format"]
            )
    
    def _format_percentage(self, value: str) -> FormatValidationResult:
        """Format percentage values"""
        # Remove % symbol and whitespace
        cleaned = value.strip().rstrip('%').strip()
        
        try:
            num = float(cleaned)
            # Determine if it's already in decimal form
            if 0 <= num <= 1 and '.' in cleaned:
                decimal = num
                percent = num * 100
            else:
                percent = num
                decimal = num / 100
            
            return FormatValidationResult(
                original=value,
                normalized=str(percent),
                transformed=f"{percent:.1f}%",
                is_valid=True,
                format_type="percentage",
                metadata={
                    "decimal": decimal,
                    "percent": percent
                }
            )
        except ValueError:
            return FormatValidationResult(
                original=value,
                normalized=cleaned,
                transformed=None,
                is_valid=False,
                format_type="percentage",
                errors=["Invalid percentage format"]
            )
    
    def validate_and_format(self, value: str, format_type: str, **kwargs) -> FormatValidationResult:
        """Validate and format a value"""
        if format_type not in self.formatters:
            return FormatValidationResult(
                original=value,
                normalized=value,
                transformed=None,
                is_valid=False,
                format_type=format_type,
                errors=[f"Unknown format type: {format_type}"]
            )
        
        formatter = self.formatters[format_type]
        # Pass kwargs for formatters that need them (like postal_code)
        if format_type == "postal_code" and "country" in kwargs:
            return formatter(value, kwargs["country"])
        
        return formatter(value)


def main():
    """Test format validation and transformation"""
    validator = FormatValidator()
    
    # Test cases
    test_cases = [
        # Phone numbers
        ("phone", "415-555-1234", True),
        ("phone", "(415) 555-1234", True),
        ("phone", "+1 415 555 1234", True),
        ("phone", "415.555.1234", True),
        ("phone", "invalid-phone", False),
        
        # Emails
        ("email", "user@example.com", True),
        ("email", "John.Doe+filter@gmail.com", True),
        ("email", "ADMIN@COMPANY.COM", True),
        ("email", "invalid.email", False),
        
        # URLs
        ("url", "example.com", True),
        ("url", "https://www.example.com/", True),
        ("url", "http://subdomain.example.com/path?query=1", True),
        ("url", "not a url", False),
        
        # Slugs
        ("slug", "Hello World!", True),
        ("slug", "This is a Test - 123", True),
        ("slug", "Café résumé", True),
        ("slug", "", False),
        
        # Credit cards
        ("credit_card", "4532015112830366", True),  # Valid Visa
        ("credit_card", "5425-2334-3010-9903", True),  # Valid Mastercard with dashes
        ("credit_card", "4532 0151 1283 0367", False),  # Invalid Luhn
        ("credit_card", "1234", False),  # Too short
        
        # Currency
        ("currency", "$1,234.56", True),
        ("currency", "1234.56", True),
        ("currency", "-$99.99", True),
        ("currency", "invalid", False),
        
        # Percentages
        ("percentage", "50%", True),
        ("percentage", "0.75", True),
        ("percentage", "100", True),
        ("percentage", "abc%", False),
    ]
    
    logger.info("=" * 50)
    logger.info("Testing format validation and transformation")
    logger.info("=" * 50)
    
    passed = 0
    failed = 0
    
    for format_type, value, expected_valid in test_cases:
        result = validator.validate_and_format(value, format_type)
        
        if result.is_valid == expected_valid:
            passed += 1
            logger.success(f"✅ {format_type}: '{value}'")
            if result.transformed:
                logger.info(f"   → Transformed: {result.transformed}")
            if result.metadata:
                logger.info(f"   → Metadata: {result.metadata}")
        else:
            failed += 1
            logger.error(f"❌ {format_type}: '{value}' - Expected valid={expected_valid}, got {result.is_valid}")
            if result.errors:
                logger.error(f"   → Errors: {result.errors}")
    
    # Test postal codes with country
    logger.info("\n" + "=" * 50)
    logger.info("Testing postal codes by country")
    logger.info("=" * 50)
    
    postal_tests = [
        ("12345", "US", True),
        ("12345-6789", "US", True),
        ("SW1A 1AA", "UK", True),
        ("sw1a1aa", "UK", True),
        ("K1A 0B1", "CA", True),
        ("K1A0B1", "CA", True),
        ("INVALID", "US", False),
    ]
    
    for value, country, expected in postal_tests:
        result = validator.validate_and_format(value, "postal_code", country=country)
        
        if result.is_valid == expected:
            passed += 1
            logger.success(f"✅ postal_code ({country}): '{value}'")
            if result.transformed:
                logger.info(f"   → Formatted: {result.transformed}")
        else:
            failed += 1
            logger.error(f"❌ postal_code ({country}): '{value}' - Expected {expected}")
    
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
        sys.exit(1)


if __name__ == "__main__":
    main()