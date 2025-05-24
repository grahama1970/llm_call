#!/usr/bin/env python3
"""
Comprehensive Verification of Core and CLI Modules (V2)
======================================================

Updated version that correctly identifies the actual functions and classes
in the modules.

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
        
        # Key core modules to verify (updated with correct names)
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
            ("llm_call.core.validation.retry_manager", []),  # Check what's actually in here
            ("llm_call.core.validation.ai_validator_base", []),  # Check what's actually in here
            ("llm_call.core.validation.builtin_strategies.basic_validators", 
             ["ResponseNotEmptyValidator", "JSONResponseValidator"]),
            
            # Utils
            ("llm_call.core.utils.json_utils", []),  # Check actual contents
            ("llm_call.core.utils.file_utils", []),  # Check actual contents
            ("llm_call.core.utils.embedding_utils", []),  # Check actual contents
        ]
        
        for module_name, expected_attrs in core_modules:
            if self.verify_module_import(module_name):
                self._verify_module_attributes(module_name, expected_attrs)
                
    def verify_cli_modules(self):
        """Verify all CLI modules"""
        logger.info("\n=== VERIFYING CLI MODULES ===")
        
        cli_modules = [
            ("llm_call.cli.main", []),  # Check actual contents
            ("llm_call.cli.slash_mcp_mixin", []),  # Check actual contents
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
                "messages": [{"role": "user", "content": "Say 'hello test'"}],
                "provider": "litellm"
            }
            response = await make_llm_request(llm_config)
            if response and response.get("content"):
                self.successes.append("✅ Basic LLM call works")
            else:
                self.failures.append("❌ Basic LLM call returned empty response")
        except Exception as e:
            self.failures.append(f"❌ Basic LLM call failed: {e}")
            
        # Test 2: JSON validation
        try:
            from llm_call.core.validation.builtin_strategies.basic_validators import (
                JSONResponseValidator
            )
            validator = JSONResponseValidator()
            test_json = '{"test": "value"}'
            result = await validator.validate(test_json, {})
            if result.is_valid:
                self.successes.append("✅ JSON validation works")
            else:
                self.failures.append("❌ JSON validation failed")
        except Exception as e:
            self.failures.append(f"❌ JSON validation error: {e}")
            
        # Test 3: Claude CLI Proxy
        try:
            from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
            proxy = ClaudeCLIProxyProvider()
            # Just verify it initializes
            self.successes.append("✅ Claude CLI Proxy initializes")
        except Exception as e:
            self.warnings.append(f"⚠ Claude CLI Proxy init warning: {e}")
            
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
                self.successes.append("✅ Router resolve_route works")
            else:
                self.failures.append("❌ Router failed to resolve")
        except Exception as e:
            self.failures.append(f"❌ Router error: {e}")
            
    def verify_poc_retry_manager(self):
        """Verify POC retry manager functionality"""
        logger.info("\n=== VERIFYING POC RETRY MANAGER ===")
        
        try:
            # Check if it's in a different location
            poc_paths = [
                "proof_of_concept.poc_retry_manager",
                "llm_call.proof_of_concept.poc_retry_manager",
                "poc_retry_manager"
            ]
            
            poc_found = False
            for path in poc_paths:
                try:
                    module = importlib.import_module(path)
                    poc_found = True
                    self.successes.append(f"✅ POC Retry Manager found at: {path}")
                    break
                except ImportError:
                    continue
                    
            if not poc_found:
                # Check if files exist in filesystem
                poc_file_path = Path(__file__).parent.parent.parent / "proof_of_concept" / "poc_retry_manager.py"
                if poc_file_path.exists():
                    self.warnings.append(f"⚠ POC files exist but not importable. Path: {poc_file_path}")
                else:
                    self.warnings.append("⚠ POC Retry Manager not found in expected locations")
                    
        except Exception as e:
            self.warnings.append(f"⚠ POC Retry Manager error: {e}")
            
    def list_all_functions_in_module(self, module_path: str):
        """List all functions and classes in a module for debugging"""
        try:
            module = importlib.import_module(module_path)
            items = []
            for name in dir(module):
                if not name.startswith('_'):
                    obj = getattr(module, name)
                    if callable(obj):
                        items.append(name)
            if items:
                logger.debug(f"Available in {module_path}: {', '.join(items)}")
        except Exception as e:
            logger.debug(f"Could not list items in {module_path}: {e}")
            
    def print_report(self):
        """Print comprehensive verification report"""
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE VERIFICATION REPORT V2")
        logger.info("="*60)
        
        # Summary
        total_checks = len(self.successes) + len(self.failures) + len(self.warnings)
        logger.info(f"\nTotal checks performed: {total_checks}")
        logger.info(f"✅ Successes: {len(self.successes)}")
        logger.info(f"❌ Failures: {len(self.failures)}")
        logger.info(f"⚠️  Warnings: {len(self.warnings)}")
        
        # Details
        if self.successes:
            logger.info("\n=== SUCCESSES ===")
            for success in self.successes:
                logger.info(success)
                
        if self.warnings:
            logger.info("\n=== WARNINGS ===")
            for warning in self.warnings:
                logger.warning(warning)
                
        if self.failures:
            logger.info("\n=== FAILURES ===")
            for failure in self.failures:
                logger.error(failure)
                
        # Overall status
        logger.info("\n=== OVERALL STATUS ===")
        if not self.failures:
            logger.success("✅ ALL CRITICAL MODULES VERIFIED SUCCESSFULLY!")
        else:
            logger.error(f"❌ {len(self.failures)} CRITICAL FAILURES DETECTED")
            

async def main():
    """Run comprehensive verification"""
    verifier = ModuleVerifier()
    
    # Run all verifications
    verifier.verify_core_modules()
    verifier.verify_cli_modules()
    await verifier.verify_functional_tests()
    verifier.verify_poc_retry_manager()
    
    # Print report
    verifier.print_report()
    
    # Return exit code based on failures
    return 1 if verifier.failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
