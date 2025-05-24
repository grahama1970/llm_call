#!/usr/bin/env python3
"""
Comprehensive Verification of Core and CLI Modules
================================================

This script systematically verifies all modules in the core and cli directories
to ensure they are working as expected after recent changes.

Expected output: Comprehensive report of all module functionality
"""

import os
import sys
import importlib
import subprocess
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
setup_logging(level="DEBUG")


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
        """Verify all core modules"""
        logger.info("\n=== VERIFYING CORE MODULES ===")
        
        # Key core modules to verify
        core_modules = [
            # Base modules
            ("llm_call.core.base", ["get_provider", "LLMProvider"]),
            ("llm_call.core.caller", ["call_llm"]),
            ("llm_call.core.router", ["router"]),
            ("llm_call.core.strategies", ["BaseStrategy", "registry"]),
            
            # Configuration
            ("llm_call.core.config.loader", ["load_configuration"]),
            ("llm_call.core.config.settings", ["Settings", "RetrySettings"]),
            
            # Providers
            ("llm_call.core.providers.base_provider", ["BaseProvider"]),
            ("llm_call.core.providers.litellm_provider", ["LiteLLMProvider"]),
            ("llm_call.core.providers.claude_cli_proxy", ["ClaudeCLIProxy"]),
            
            # Validation
            ("llm_call.core.validation.retry_manager", ["RetryManager"]),
            ("llm_call.core.validation.ai_validator_base", ["AIValidator"]),
            
            # Utils
            ("llm_call.core.utils.json_utils", ["JsonUtils"]),
            ("llm_call.core.utils.file_utils", ["ensure_directory"]),
            ("llm_call.core.utils.embedding_utils", ["EmbeddingGenerator"]),
        ]
        
        for module_name, expected_attrs in core_modules:
            if self.verify_module_import(module_name):
                self._verify_module_attributes(module_name, expected_attrs)
                
    def verify_cli_modules(self):
        """Verify all CLI modules"""
        logger.info("\n=== VERIFYING CLI MODULES ===")
        
        cli_modules = [
            ("llm_call.cli.main", ["main"]),
            ("llm_call.cli.slash_mcp_mixin", ["SlashMCPMixin"]),
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
            
    def verify_functional_tests(self):
        """Run key functional tests"""
        logger.info("\n=== RUNNING FUNCTIONAL TESTS ===")
        
        # Test 1: Basic LLM call
        try:
            from llm_call.core.caller import call_llm
            response = call_llm("Test: say 'hello'", provider="litellm")
            if response and len(response) > 0:
                self.successes.append("✅ Basic LLM call works")
            else:
                self.failures.append("❌ Basic LLM call returned empty response")
        except Exception as e:
            self.failures.append(f"❌ Basic LLM call failed: {e}")
            
        # Test 2: JSON validation
        try:
            from llm_call.core.validation.builtin_strategies.basic_validators import (
                json_string
            )
            test_json = '{"test": "value"}'
            if json_string(test_json):
                self.successes.append("✅ JSON validation works")
            else:
                self.failures.append("❌ JSON validation failed")
        except Exception as e:
            self.failures.append(f"❌ JSON validation error: {e}")
            
        # Test 3: Claude CLI Proxy
        try:
            from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxy
            proxy = ClaudeCLIProxy()
            # Just verify it initializes
            self.successes.append("✅ Claude CLI Proxy initializes")
        except Exception as e:
            self.warnings.append(f"⚠ Claude CLI Proxy init warning: {e}")
            
    def verify_poc_retry_manager(self):
        """Verify POC retry manager functionality"""
        logger.info("\n=== VERIFYING POC RETRY MANAGER ===")
        
        try:
            from proof_of_concept.poc_retry_manager import POCRetryManager
            from proof_of_concept.litellm_client_poc import LiteLLMClientPOC
            
            # Test basic initialization
            client = LiteLLMClientPOC()
            manager = POCRetryManager(client)
            
            # Test simple call
            result = manager.call_with_retry(
                "Say 'test successful'",
                validation_strategy="response_not_empty"
            )
            
            if result.success and result.response:
                self.successes.append("✅ POC Retry Manager works")
            else:
                self.failures.append("❌ POC Retry Manager call failed")
                
        except Exception as e:
            self.warnings.append(f"⚠ POC Retry Manager not found/error: {e}")
            
    def print_report(self):
        """Print comprehensive verification report"""
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE VERIFICATION REPORT")
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
            

def main():
    """Run comprehensive verification"""
    verifier = ModuleVerifier()
    
    # Run all verifications
    verifier.verify_core_modules()
    verifier.verify_cli_modules()
    verifier.verify_functional_tests()
    verifier.verify_poc_retry_manager()
    
    # Print report
    verifier.print_report()
    
    # Return exit code based on failures
    return 1 if verifier.failures else 0


if __name__ == "__main__":
    sys.exit(main())
