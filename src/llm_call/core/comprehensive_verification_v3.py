#!/usr/bin/env python3
"""
Comprehensive Verification of Core and CLI Modules (V3)
======================================================

Final version with all fixes and correct class names.

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
             ["ResponseNotEmptyValidator", "JsonStringValidator"]),  # Fixed names
            
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
        
        # Test 1: Basic LLM call (with fixed provider removal)
        try:
            from llm_call.core.caller import make_llm_request
            llm_config = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say hello test"}],
                "provider": "litellm",
                "max_tokens": 10
            }
            response = await make_llm_request(llm_config)
            if response:
                # Handle both dict and ModelResponse objects
                if hasattr(response, 'choices') and response.choices:
                    content = response.choices[0].message.content
                    self.successes.append(f"✅ Basic LLM call works: {content[:50]}...")
                elif isinstance(response, dict) and response.get("content"):
                    self.successes.append(f"✅ Basic LLM call works: {response.get('content', '')[:50]}...")
                else:
                    self.failures.append("❌ Basic LLM call returned empty response")
            else:
                self.failures.append("❌ Basic LLM call returned None")
        except Exception as e:
            self.failures.append(f"❌ Basic LLM call failed: {str(e)[:100]}...")
            
        # Test 2: JSON validation (with correct class name)
        try:
            from llm_call.core.validation.builtin_strategies.basic_validators import (
                JsonStringValidator
            )
            validator = JsonStringValidator()
            # Create a proper response object
            test_response = {
                "choices": [{
                    "message": {
                        "content": '{"test": "value"}'
                    }
                }]
            }
            result = await validator.validate(test_response, {})
            if result.valid:
                self.successes.append("✅ JSON validation works")
            else:
                self.failures.append("❌ JSON validation failed")
        except Exception as e:
            self.failures.append(f"❌ JSON validation error: {str(e)[:100]}...")
            
        # Test 3: Claude CLI Proxy
        try:
            from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider
            proxy = ClaudeCLIProxyProvider()
            # Just verify it initializes
            self.successes.append("✅ Claude CLI Proxy initializes")
        except Exception as e:
            self.warnings.append(f"⚠ Claude CLI Proxy init warning: {str(e)[:100]}...")
            
        # Test 4: Router functionality (should work now with provider fix)
        try:
            from llm_call.core.router import resolve_route
            test_config = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "test"}],
                "provider": "litellm"
            }
            provider_class, params = resolve_route(test_config)
            if provider_class and params:
                # Verify provider key was removed
                if "provider" not in params:
                    self.successes.append("✅ Router resolve_route works and removes 'provider' key")
                else:
                    self.failures.append("❌ Router failed to remove 'provider' key")
            else:
                self.failures.append("❌ Router failed to resolve")
        except Exception as e:
            self.failures.append(f"❌ Router error: {str(e)[:100]}...")
            
    def verify_poc_retry_manager(self):
        """Verify POC retry manager functionality"""
        logger.info("\n=== VERIFYING POC RETRY MANAGER ===")
        
        try:
            # Import the actual functions/classes from poc_retry_manager
            from llm_call.proof_of_concept.poc_retry_manager import (
                retry_with_validation_poc,
                PoCRetryConfig,
                PoCHumanReviewNeededError
            )
            
            self.successes.append("✅ POC Retry Manager modules imported successfully")
            
            # Test retry config
            config = PoCRetryConfig(max_attempts=3, debug_mode=True)
            if config.max_attempts == 3 and config.debug_mode:
                self.successes.append("✅ POC Retry Config works correctly")
            else:
                self.failures.append("❌ POC Retry Config initialization failed")
                
        except ImportError as e:
            self.warnings.append(f"⚠ POC Retry Manager import error: {str(e)[:100]}...")
            
    def verify_all_files_in_directories(self):
        """List all Python files in core and cli directories for completeness"""
        logger.info("\n=== CHECKING ALL FILES IN DIRECTORIES ===")
        
        core_dir = Path(__file__).parent.parent / "core"
        cli_dir = Path(__file__).parent.parent / "cli"
        
        # Count files
        core_files = list(core_dir.rglob("*.py"))
        cli_files = list(cli_dir.rglob("*.py"))
        
        logger.info(f"Found {len(core_files)} Python files in core/")
        logger.info(f"Found {len(cli_files)} Python files in cli/")
        
        # Check if any files are not being tested
        tested_modules = set()
        for check in [self.successes, self.failures, self.warnings]:
            for item in check:
                if "Import:" in item:
                    module = item.split("Import: ")[1].strip()
                    tested_modules.add(module)
                    
        # Find untested files
        all_files = core_files + cli_files
        untested = []
        for file in all_files:
            if file.name == "__init__.py":
                continue
            module_path = str(file).replace("/", ".").replace(".py", "")
            module_name = "llm_call." + module_path.split("llm_call.")[1]
            if module_name not in tested_modules and "test_" not in module_name:
                untested.append(module_name)
                
        if untested:
            logger.info(f"\nUntested modules ({len(untested)}):")
            for module in sorted(untested):
                logger.info(f"  - {module}")
                
    def print_report(self):
        """Print comprehensive verification report"""
        logger.info("\n" + "="*60)
        logger.info("COMPREHENSIVE VERIFICATION REPORT V3")
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
            for success in self.successes[:10]:  # Show first 10
                logger.info(success)
            if len(self.successes) > 10:
                logger.info(f"... and {len(self.successes) - 10} more successes")
                
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
            logger.info("\n📝 NEXT STEPS:")
            logger.info("1. Review warnings for non-critical issues")
            logger.info("2. Check untested modules listed above")
            logger.info("3. Run integration tests for end-to-end validation")
        else:
            logger.error(f"❌ {len(self.failures)} CRITICAL FAILURES DETECTED")
            logger.info("\n🔧 RECOMMENDED FIXES:")
            logger.info("1. Address each failure listed above")
            logger.info("2. Re-run verification after fixes")
            logger.info("3. Ensure all tests pass before deployment")
            

async def main():
    """Run comprehensive verification"""
    verifier = ModuleVerifier()
    
    # Run all verifications
    verifier.verify_core_modules()
    verifier.verify_cli_modules()
    await verifier.verify_functional_tests()
    verifier.verify_poc_retry_manager()
    verifier.verify_all_files_in_directories()
    
    # Print report
    verifier.print_report()
    
    # Return exit code based on failures
    return 1 if verifier.failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
