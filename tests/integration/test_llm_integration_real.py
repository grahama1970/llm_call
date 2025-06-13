#!/usr/bin/env python3
"""
Module: test_llm_integration_real.py
Description: Real integration tests for LLM Call module following GRANGER standards

This module provides comprehensive integration testing for the llm_call module,
ensuring it works correctly with all supported LLM providers and integrates
properly with the GRANGER ecosystem.

External Dependencies:
- litellm: https://docs.litellm.ai/
- pytest: https://docs.pytest.org/
- loguru: https://github.com/Delgan/loguru

Sample Input:
>>> config = {
...     "model": "vertex_ai/gemini-2.5-flash-preview-05-20", 
...     "messages": [{"role": "user", "content": "Hello"}]
... }
>>> response = await make_llm_request(config)

Expected Output:
>>> response.choices[0].message.content
'Hello! How can I help you today?'

Example Usage:
>>> pytest test_llm_integration_real.py -v --durations=0
>>> # Run specific test
>>> pytest test_llm_integration_real.py::TestLLMIntegration::test_granger_hub_compatibility -v
"""

import asyncio
import os
import sys
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

import pytest
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_call.core.caller import make_llm_request
from llm_call.core.utils.auth_diagnostics import AuthDiagnostics, diagnose_auth_error
from llm_call.core.config.loader import load_configuration

class TestLLMIntegration:
    """Real integration tests for LLM Call module."""
    
    # Test configuration
    MIN_DURATION = 0.05  # 50ms minimum for real API calls
    TEST_MODELS = [
        "vertex_ai/gemini-2.5-flash-preview-05-20",  # Vertex AI
        "gemini/gemini-1.5-pro",  # Direct Gemini API
        "gpt-3.5-turbo",  # OpenAI
        "claude-3-sonnet-20240229",  # Anthropic
    ]
    
    @classmethod
    def setup_class(cls):
        """Setup test class - verify environment."""
        logger.info("Setting up LLM integration tests...")
        
        # Load configuration
        cls.config = load_configuration()
        
        # Track test results for reporting
        cls.test_results = {
            "start_time": datetime.now().isoformat(),
            "models_tested": [],
            "successful_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "durations": {}
        }
    
    @classmethod
    def teardown_class(cls):
        """Generate test report."""
        cls.test_results["end_time"] = datetime.now().isoformat()
        
        # Save test report
        report_path = Path(__file__).parent / "test_results" / f"llm_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(cls.test_results, f, indent=2)
        
        logger.info(f"Test report saved to: {report_path}")
        logger.info(f"Summary: {cls.test_results['successful_tests']} passed, "
                   f"{cls.test_results['failed_tests']} failed, "
                   f"{cls.test_results['skipped_tests']} skipped")
    
    def _verify_real_api_call(self, duration: float, model: str) -> None:
        """Verify the API call was real based on duration."""
        assert duration > self.MIN_DURATION, (
            f"{model} responded in {duration:.3f}s - "
            f"too fast for real API (minimum: {self.MIN_DURATION}s). "
            "Possible mock or cached response!"
        )
        logger.info(f"✓ {model} duration {duration:.3f}s is realistic")
    
    def _extract_content(self, response: Any) -> str:
        """Extract content from various response formats."""
        if hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content
        elif isinstance(response, dict):
            return response.get('content', response.get('response', ''))
        elif isinstance(response, str):
            return response
        return str(response)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_basic_hello_world_all_models(self):
        """Test basic Hello World across all configured models."""
        for model in self.TEST_MODELS:
            logger.info(f"\n=== Testing {model} ===")
            
            # Check if we should skip this model
            if model.startswith("vertex_ai/") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                logger.warning(f"Skipping {model} - no Vertex AI credentials")
                self.test_results["skipped_tests"] += 1
                continue
            elif model.startswith("gemini/") and not os.getenv("GEMINI_API_KEY"):
                logger.warning(f"Skipping {model} - no Gemini API key")
                self.test_results["skipped_tests"] += 1
                continue
            elif "gpt" in model and not os.getenv("OPENAI_API_KEY"):
                logger.warning(f"Skipping {model} - no OpenAI API key")
                self.test_results["skipped_tests"] += 1
                continue
            elif "claude" in model and not os.getenv("ANTHROPIC_API_KEY"):
                logger.warning(f"Skipping {model} - no Anthropic API key")
                self.test_results["skipped_tests"] += 1
                continue
            
            start_time = time.time()
            
            try:
                response = await make_llm_request({
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Say 'Hello GRANGER Ecosystem!' exactly"}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 50
                })
                
                duration = time.time() - start_time
                
                # Verify it was a real API call
                self._verify_real_api_call(duration, model)
                
                # Verify response
                content = self._extract_content(response)
                assert content, f"No content from {model}"
                assert "granger" in content.lower(), f"Response missing GRANGER: {content}"
                
                # Record success
                self.test_results["models_tested"].append(model)
                self.test_results["successful_tests"] += 1
                self.test_results["durations"][model] = duration
                
                logger.success(f"✅ {model} passed: {content[:50]}...")
                
            except Exception as e:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ {model} failed: {e}")
                
                # Provide diagnostics for auth errors
                if "auth" in str(e).lower() or "token" in str(e).lower():
                    diagnose_auth_error(e, model, verbose=True)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_granger_hub_compatibility(self):
        """Test compatibility with GRANGER Hub message format."""
        model = "vertex_ai/gemini-2.5-flash-preview-05-20"
        
        # GRANGER Hub standard message format
        hub_message = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are part of the GRANGER ecosystem. Respond in JSON."
                },
                {
                    "role": "user", 
                    "content": "What modules can you interact with?"
                }
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        start_time = time.time()
        
        try:
            response = await make_llm_request(hub_message)
            duration = time.time() - start_time
            
            # Verify real call
            self._verify_real_api_call(duration, model)
            
            # Extract and parse JSON response
            content = self._extract_content(response)
            assert content, "No response content"
            
            # Try to parse as JSON
            try:
                json_response = json.loads(content)
                assert isinstance(json_response, dict), "Response is not a JSON object"
                logger.success(f"✅ GRANGER Hub compatibility test passed")
                logger.info(f"Response: {json_response}")
            except json.JSONDecodeError:
                pytest.fail(f"Response is not valid JSON: {content}")
                
        except Exception as e:
            logger.error(f"GRANGER Hub compatibility test failed: {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.asyncio  
    async def test_multi_module_context(self):
        """Test LLM understanding of GRANGER module relationships."""
        model = self.config.llm.default_model
        
        # Test understanding of module relationships
        granger_context = """
        You are analyzing the GRANGER ecosystem. Based on these modules:
        - SPARTA: Downloads documents
        - Marker: Extracts content from documents  
        - ArangoDB: Stores extracted content
        - LLM Call: Provides AI capabilities
        
        Describe the data flow for processing a PDF document.
        """
        
        start_time = time.time()
        
        response = await make_llm_request({
            "model": model,
            "messages": [
                {"role": "user", "content": granger_context}
            ],
            "temperature": 0.5,
            "max_tokens": 300
        })
        
        duration = time.time() - start_time
        self._verify_real_api_call(duration, model)
        
        content = self._extract_content(response)
        
        # Verify understanding of module relationships
        required_modules = ["sparta", "marker", "arangodb", "llm"]
        for module in required_modules:
            assert module.lower() in content.lower(), f"Missing {module} in explanation"
        
        logger.success("✅ Multi-module context test passed")
        logger.info(f"Module flow explanation: {content[:200]}...")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_validation_strategies(self):
        """Test built-in validation strategies with real LLM."""
        model = self.config.llm.default_model
        
        # Test JSON validation
        json_request = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Respond only with valid JSON"},
                {"role": "user", "content": "List 3 GRANGER modules as JSON"}
            ],
            "response_format": {"type": "json_object"},
            "validation": [
                {"type": "json_string"},
                {"type": "field_present", "params": {"field": "modules"}}
            ],
            "temperature": 0.3
        }
        
        start_time = time.time()
        
        response = await make_llm_request(json_request)
        duration = time.time() - start_time
        
        self._verify_real_api_call(duration, model)
        
        content = self._extract_content(response)
        
        # Verify it's valid JSON with required field
        data = json.loads(content)
        assert "modules" in data, "JSON missing required 'modules' field"
        assert isinstance(data["modules"], (list, dict)), "modules field has wrong type"
        
        logger.success("✅ Validation strategies test passed")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_conversation_persistence(self):
        """Test conversation context persistence across calls."""
        model = self.config.llm.default_model
        
        # First message - establish context
        response1 = await make_llm_request({
            "model": model,
            "messages": [
                {"role": "user", "content": "My favorite GRANGER module is ArangoDB. Remember this."}
            ],
            "temperature": 0.3
        })
        
        content1 = self._extract_content(response1)
        assert "arangodb" in content1.lower(), "First response should acknowledge ArangoDB"
        
        # Second message - test context
        response2 = await make_llm_request({
            "model": model,
            "messages": [
                {"role": "user", "content": "My favorite GRANGER module is ArangoDB. Remember this."},
                {"role": "assistant", "content": content1},
                {"role": "user", "content": "What is my favorite GRANGER module?"}
            ],
            "temperature": 0.3
        })
        
        content2 = self._extract_content(response2)
        assert "arangodb" in content2.lower(), "Should remember ArangoDB from context"
        
        logger.success("✅ Conversation persistence test passed")
    
    @pytest.mark.integration 
    @pytest.mark.asyncio
    async def test_error_handling_and_diagnostics(self):
        """Test error handling with intentionally bad requests."""
        # Test with invalid model name
        with pytest.raises(Exception) as exc_info:
            await make_llm_request({
                "model": "invalid/model-that-does-not-exist",
                "messages": [{"role": "user", "content": "Test"}]
            })
        
        logger.info(f"Expected error for invalid model: {exc_info.value}")
        
        # Test with missing messages
        result = await make_llm_request({
            "model": "gpt-3.5-turbo"
            # Missing messages field
        })
        
        assert result is None, "Should return None for invalid config"
        logger.success("✅ Error handling test passed")
    
    @pytest.mark.integration
    def test_module_imports_and_structure(self):
        """Verify all required modules can be imported."""
        required_imports = [
            "llm_call.core.caller",
            "llm_call.core.router", 
            "llm_call.core.providers.litellm_provider",
            "llm_call.core.validation.retry_manager",
            "llm_call.core.utils.auth_diagnostics"
        ]
        
        for module_path in required_imports:
            try:
                module = __import__(module_path, fromlist=[''])
                assert module is not None
                logger.info(f"✓ Successfully imported {module_path}")
            except ImportError as e:
                pytest.fail(f"Failed to import {module_path}: {e}")
        
        logger.success("✅ All module imports successful")

# Validation runner
if __name__ == "__main__":
    import subprocess
    
    logger.info("Running LLM integration tests...")
    logger.info("This will make REAL API calls - ensure credentials are configured")
    
    # Check for required environment variables
    env_vars = {
        "GOOGLE_APPLICATION_CREDENTIALS": "Vertex AI",
        "GEMINI_API_KEY": "Gemini Direct", 
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic"
    }
    
    logger.info("\nEnvironment check:")
    for var, service in env_vars.items():
        if os.getenv(var):
            logger.info(f"✓ {service} configured ({var} set)")
        else:
            logger.warning(f"✗ {service} not configured ({var} not set)")
    
    # Run tests
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--durations=0", "-s"],
        capture_output=False
    )
    
    sys.exit(result.returncode)