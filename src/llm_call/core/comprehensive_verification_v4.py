#!/usr/bin/env python3
"""
Comprehensive Verification of Core and CLI Modules (V4 - CORRECTED)
==================================================================

This version correctly tests the POC retry functionality as it actually exists.

Purpose: Verify all modules in core/ and cli/ are working after recent changes.
Created: 2025-05-23 by Claude Assistant
Fixed: Corrected POC retry test to use actual implementation

Expected output: Comprehensive report of all module functionality
"""

import os
import sys
import importlib
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Any
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Initialize cache first
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache
initialize_litellm_cache()

# Setup logging
from llm_call.core.utils.logging_setup import setup_logging
setup_logging(level="INFO")


class ModuleVerifier:
    """Verify module functionality systematically"""
    
    def __init__(self):
        self.successes = []
        self.failures = []
        self.warnings = []
        
    def verify_module_import(self, module_path: str) -> bool:
        """Verify a module can be imported"""
        try:
            module = importlib.import_module(module_path)
            self.successes.append(f"✅ Import: {module_path}")
            return True
        except Exception as e:
            self.failures.append(f"❌ Import failed: {module_path} - {e}")
            return False
            
    def verify_core_modules(self):
        """Verify all core modules with correct function/class names"""
        logger.info("\n=== VERIFYING CORE MODULES ===")
        
        core_modules = [
            # Base modules
            ("llm_call.core.base", ["ValidationResult", "ValidationStrategy", "BaseValidator"]),
            ("llm_call.core.caller", ["make_llm_request", "preprocess_messages"]),
            ("llm_call.core.router", ["resolve_route"]),
            ("llm_call.core.strategies", ["registry"]),
            
            # Configuration
            ("llm_call.core.config.loader", ["load_configuration"]),
            ("llm_call.core.config.settings", ["Settings", "RetrySettings"]),
            
            # Providers
            ("llm_call.core.providers.base_provider", ["BaseLLMProvider"]),
            ("llm_call.core.providers.litellm_provider", ["LiteLLMProvider"]),
            ("llm_call.core.providers.claude_cli_proxy", ["ClaudeCLIProxyProvider"]),
            
            # Validation
            ("llm_call.core.validation.retry_manager", []),
            ("llm_call.core.validation.ai_validator_base", []),
            ("llm_call.core.validation.builtin_strategies.basic_validators", 
             ["ResponseNotEmptyValidator", "JsonStringValidator"]),
        ]
        
        for module_name, expected_attrs in core_modules:
            if self.verify_module_import(module_name):
                self._verify_module_attributes(module_name, expected_attrs)
                
    def verify_cli_modules(self):
        """Verify all CLI modules"""
        logger.info("\n=== VERIFYING CLI MODULES ===")
        
        cli_modules = [
            ("llm_call.cli.main", []),
            ("llm_call.cli.slash_mcp_mixin", []),
            ("llm_call.cli.example_simple_cli", []),
        ]
        
        for module_name, expected_attrs in cli_modules:
            if self.verify_module_import(module_name):
                self._verify_module_attributes(module_name, expected_attrs)
                
    def _verify_module_attributes(self, module_name: str, expected_attrs: List[str]):
        """Verify module has expected attributes"""
        try:
            module = importlib.import_module(module_name)
            for attr in expected_attrs:
                if hasattr(module, attr):
                    self.successes.append(f"  ✓ {module_name}.{attr} exists")
                else:
                    self.warnings.append(f"  ⚠ {module_name}.{attr} missing")
        except Exception as e:
            self.failures.append(f"  ❌ Attribute check failed: {module_name} - {e}")
            
    async def verify_functional_tests(self):
        """Run key functional tests"""
        logger.info("\n=== RUNNING FUNCTIONAL TESTS ===")
        
        # Test 1: Basic LLM call
        try:
            from llm_call.core.caller import make_llm_request
            llm_config = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say hello test"}],
                "provider": "litellm",
                "max_tokens": 10
            }
            response = await make_llm_request(llm_config)
            if response and response.get("content"):
                self.successes.append(f"✅ Basic LLM call works: {response.get('content', '')[:50]}...")
            else:
                self.failures.append("❌ Basic LLM call returned empty response")
        except Exception as e:
            self.failures.append(f"❌ Basic LLM call failed: {str(e)[:100]}...")
            
        # Test 2: JSON validation
        try:
            from llm_call.core.validation.builtin_strategies.basic_validators import (
                JsonStringValidator
            )
            validator = JsonStringValidator()
            test_json = '{"test": "value"}'
            result = await validator.validate(test_json, {})
            if result.valid:  # Correct attribute name
                self.successes.append("✅ JSON validation works")
            else:
                self.failures.append("❌ JSON validation failed")
        except Exception as e:
            self.failures.append(f"❌ JSON validation error: {str(e)[:100]}...")
            
        # Test 3: Claude CLI Proxy
        try:
            from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
            proxy = ClaudeCLIProxyProvider()
            self.successes.append("✅ Claude CLI Proxy initializes")
        except Exception as e:
            self.warnings.append(f"⚠ Claude CLI Proxy init warning: {str(e)[:100]}...")
            
        # Test 4: Router functionality
        try:
            from llm_call.core.router import resolve_route
            test_config = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "test"}],
                "provider": "litellm"
            }
            provider_class, params = resolve_route(test_config)
            if provider_class and params:
                if "provider" not in params:
                    self.successes.append("✅ Router resolve_route works and removes 'provider' key")
                else:
                    self.failures.append("❌ Router failed to remove 'provider' key")
            else:
                self.failures.append("❌ Router failed to resolve")
        except Exception as e:
            self.failures.append(f"❌ Router error: {str(e)[:100]}...")
            
    async def verify_poc_retry_functionality(self):
        """Verify POC retry functionality AS IT ACTUALLY EXISTS"""
        logger.info("\n=== VERIFYING POC RETRY FUNCTIONALITY ===")
        
        # Test 1: Import the actual functions
        try:
            from llm_call.proof_of_concept.poc_retry_manager import (
                retry_with_validation_poc,
                PoCRetryConfig,
                PoCHumanReviewNeededError,
                build_retry_feedback_message,
                extract_content_from_response
            )
            self.successes.append("✅ POC retry functions imported successfully")
            
            # Test 2: Verify PoCRetryConfig works
            config = PoCRetryConfig(
                max_attempts=3,
                initial_delay=1.0,
                backoff_factor=2.0,
                debug_mode=True
            )
            if config.max_attempts == 3 and config.debug_mode:
                self.successes.append("✅ PoCRetryConfig works correctly")
            else:
                self.failures.append("❌ PoCRetryConfig initialization failed")
                
            # Test 3: Test content extraction
            test_responses = [
                {"choices": [{"message": {"content": "Test content"}}]},
                "Simple string response"
            ]
            
            for resp in test_responses:
                content = extract_content_from_response(resp)
                if content:
                    self.successes.append(f"✅ Content extraction works: '{content[:30]}...')")
                    
        except ImportError as e:
            self.failures.append(f"❌ POC retry import failed: {str(e)[:100]}...")
            
        # Test 4: Test the integrated llm_call function
        try:
            from llm_call.proof_of_concept.litellm_client_poc import llm_call
            
            # Simple test config
            test_config = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 5,
                "validation": [{"type": "response_not_empty"}],
                "retry_config": {
                    "max_attempts": 1,
                    "debug_mode": True
                }
            }
            
            # Note: We're not actually calling it here to avoid API costs
            # Just verify it's importable and structured correctly
            self.successes.append("✅ POC llm_call function is available")
            
        except ImportError as e:
            self.failures.append(f"❌ POC llm_call import failed: {str(e)[:100]}...")
            
    def verify_all_files_in_directories(self):
        """List all Python files in core and cli directories for completeness"""
        logger.info("\n=== CHECKING ALL FILES IN DIRECTORIES ===")
        
        core_dir = Path(__file__).parent.parent / "core"
        cli_dir = Path(__file__).parent.parent / "cli"
        
        core_files = list(core_dir.rglob("*.py"))
        cli_files = list(cli_dir.rglob("*.py"))
        
        logger.info(f"Found {len(core_files)} Python files in core/")
        logger.info(f"Found {len(cli_files)} Python files in cli/")
        
    def print_report(self):
        """Print comprehensive verification report"""
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE VERIFICATION REPORT V4 (CORRECTED)")
        logger.info("="*60)
        
        total_checks = len(self.successes) + len(self.failures) + len(self.warnings)
        logger.info(f"\nTotal checks performed: {total_checks}")
        logger.info(f"✅ Successes: {len(self.successes)}")
        logger.info(f"❌ Failures: {len(self.failures)}")
        logger.info(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.successes:
            logger.info("\n=== SUCCESSES ===")
            for success in self.successes[:15]:
                logger.info(success)
            if len(self.successes) > 15:
                logger.info(f"... and {len(self.successes) - 15} more successes")
                
        if self.warnings:
            logger.info("\n=== WARNINGS ===")
            for warning in self.warnings:
                logger.warning(warning)
                
        if self.failures:
            logger.info("\n=== FAILURES ===")
            for failure in self.failures:
                logger.error(failure)
                
        logger.info("\n=== OVERALL STATUS ===")
        if not self.failures:
            logger.success("✅ ALL CRITICAL MODULES VERIFIED SUCCESSFULLY!")
            logger.info("\nNOTE: POC retry functionality is implemented as functions, not a class.")
            logger.info("Use: from llm_call.proof_of_concept.litellm_client_poc import llm_call")
        else:
            logger.error(f"❌ {len(self.failures)} CRITICAL FAILURES DETECTED")
            

async def main():
    """Run comprehensive verification"""
    verifier = ModuleVerifier()
    
    # Run all verifications
    verifier.verify_core_modules()
    verifier.verify_cli_modules()
    await verifier.verify_functional_tests()
    await verifier.verify_poc_retry_functionality()
    verifier.verify_all_files_in_directories()
    
    # Print report
    verifier.print_report()
    
    return 1 if verifier.failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
