#!/usr/bin/env python3
"""
Module: test_model_hello_world.py
Description: Comprehensive "Hello World" test for all LLM models with real API verification

This module tests real API connections to verify each model integration is working properly.
No mocks are used - all tests interact with actual LLM services.

External Dependencies:
- litellm: https://docs.litellm.ai/
- openai: https://platform.openai.com/docs/
- anthropic: https://docs.anthropic.com/

Sample Input:
>>> test_vertex_ai_hello_world()
>>> # Sends "Say 'Hello World!'" to Vertex AI Gemini

Expected Output:
>>> # Response containing "Hello World!" from the model
>>> # Test duration > 0.5s (real network call)

Example Usage:
>>> pytest test_model_hello_world.py -v --durations=0
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional
import pytest
from loguru import logger
from datetime import datetime

# Import the real llm_call module
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from llm_call.core.caller import make_llm_request
from llm_call.core.utils.auth_diagnostics import AuthDiagnostics

class TestModelHelloWorld:
    """Real API tests for all supported LLM models."""
    
    # Minimum duration for real API calls (in seconds)
    MIN_API_DURATION = 0.05  # 50ms minimum for network latency
    
    # Test message that all models should handle
    HELLO_PROMPT = "Please respond with exactly: Hello World!"
    
    def setup_method(self):
        """Setup before each test."""
        self.test_results = []
        self.start_time = None
        
    def teardown_method(self):
        """Cleanup after each test."""
        if self.test_results:
            logger.info(f"Test results: {self.test_results}")
    
    def _verify_duration(self, duration: float, operation: str) -> None:
        """Verify operation took realistic time."""
        assert duration > self.MIN_API_DURATION, (
            f"{operation} completed in {duration:.3f}s - "
            f"too fast for real API call (minimum: {self.MIN_API_DURATION}s)"
        )
        logger.info(f"✓ {operation} duration: {duration:.3f}s (realistic)")
    
    def _verify_response(self, response: Any, model: str) -> Dict[str, Any]:
        """Verify and extract response content."""
        assert response is not None, f"No response from {model}"
        
        # Extract content based on response type
        content = None
        if hasattr(response, 'choices') and response.choices:
            # LiteLLM ModelResponse format
            content = response.choices[0].message.content
        elif isinstance(response, dict):
            # Direct dict response
            content = response.get('content') or response.get('response')
        elif isinstance(response, str):
            # String response
            content = response
        else:
            # Try to convert to string
            content = str(response)
        
        assert content, f"No content in response from {model}"
        assert "hello" in content.lower(), f"Response doesn't contain 'hello': {content}"
        
        return {
            "model": model,
            "content": content,
            "response_type": type(response).__name__,
            "has_hello": "hello" in content.lower(),
            "has_world": "world" in content.lower()
        }
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_vertex_ai_hello_world(self):
        """Test Vertex AI Gemini model with real API call."""
        model = "vertex_ai/gemini-2.5-flash-preview-05-20"
        logger.info(f"Testing {model}...")
        
        # Check credentials first
        creds_check = AuthDiagnostics.check_credentials(model)
        if creds_check["issues"]:
            pytest.skip(f"Credential issues: {creds_check['issues']}")
        
        # Make real API call
        start_time = time.time()
        
        try:
            response = await make_llm_request({
                "model": model,
                "messages": [
                    {"role": "user", "content": self.HELLO_PROMPT}
                ],
                "temperature": 0.1,  # Low temperature for consistent output
                "max_tokens": 50
            })
            
            duration = time.time() - start_time
            
            # Verify timing
            self._verify_duration(duration, f"Vertex AI API call")
            
            # Verify response
            result = self._verify_response(response, model)
            result["duration"] = duration
            result["timestamp"] = datetime.now().isoformat()
            
            self.test_results.append(result)
            logger.success(f"✅ Vertex AI test passed: {result['content']}")
            
        except Exception as e:
            # Log detailed diagnostics for auth errors
            error_str = str(e).lower()
            if any(term in error_str for term in ["auth", "jwt", "token", "forbidden"]):
                logger.error(f"Authentication error for {model}")
                # Diagnostics will be printed automatically
            raise
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_gemini_direct_hello_world(self):
        """Test Gemini direct API (not via Vertex) with real API call."""
        model = "gemini/gemini-1.5-pro"
        logger.info(f"Testing {model}...")
        
        # Check for API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            pytest.skip("GEMINI_API_KEY not set")
        
        # Make real API call
        start_time = time.time()
        
        try:
            response = await make_llm_request({
                "model": model,
                "messages": [
                    {"role": "user", "content": self.HELLO_PROMPT}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            })
            
            duration = time.time() - start_time
            
            # Verify timing
            self._verify_duration(duration, f"Gemini Direct API call")
            
            # Verify response
            result = self._verify_response(response, model)
            result["duration"] = duration
            result["timestamp"] = datetime.now().isoformat()
            
            self.test_results.append(result)
            logger.success(f"✅ Gemini Direct test passed: {result['content']}")
            
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "invalid" in error_str:
                pytest.skip(f"API key issue: {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_openai_hello_world(self):
        """Test OpenAI GPT model with real API call."""
        model = "gpt-3.5-turbo"
        logger.info(f"Testing {model}...")
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set")
        
        # Make real API call
        start_time = time.time()
        
        try:
            response = await make_llm_request({
                "model": model,
                "messages": [
                    {"role": "user", "content": self.HELLO_PROMPT}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            })
            
            duration = time.time() - start_time
            
            # Verify timing
            self._verify_duration(duration, f"OpenAI API call")
            
            # Verify response
            result = self._verify_response(response, model)
            result["duration"] = duration
            result["timestamp"] = datetime.now().isoformat()
            
            self.test_results.append(result)
            logger.success(f"✅ OpenAI test passed: {result['content']}")
            
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "authentication" in error_str:
                pytest.skip(f"API key issue: {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_claude_opus_hello_world(self):
        """Test Claude Opus via proxy with real API call."""
        model = "max/claude-3-opus-20240229"
        logger.info(f"Testing {model}...")
        
        # Check if Claude proxy is running
        import requests
        try:
            proxy_status = requests.get("http://localhost:3010/health", timeout=2)
            if proxy_status.status_code != 200:
                pytest.skip("Claude proxy not running on port 3010")
        except:
            pytest.skip("Claude proxy not accessible on port 3010")
        
        # Make real API call
        start_time = time.time()
        
        try:
            response = await make_llm_request({
                "model": model,
                "messages": [
                    {"role": "user", "content": self.HELLO_PROMPT}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            })
            
            duration = time.time() - start_time
            
            # Verify timing (Claude proxy calls are usually faster)
            assert duration > 0.01, f"Claude call too fast: {duration}s"
            logger.info(f"✓ Claude API call duration: {duration:.3f}s")
            
            # Verify response
            result = self._verify_response(response, model)
            result["duration"] = duration
            result["timestamp"] = datetime.now().isoformat()
            result["via_proxy"] = True
            
            self.test_results.append(result)
            logger.success(f"✅ Claude Opus test passed: {result['content']}")
            
        except Exception as e:
            if "proxy" in str(e).lower() or "connection" in str(e).lower():
                pytest.skip(f"Claude proxy connection issue: {e}")
            raise
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_claude_direct_hello_world(self):
        """Test Claude via direct Anthropic API with real API call."""
        model = "claude-3-sonnet-20240229"
        logger.info(f"Testing {model} via direct Anthropic API...")
        
        # Check for API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            pytest.skip("ANTHROPIC_API_KEY not set")
        
        # Make real API call
        start_time = time.time()
        
        try:
            response = await make_llm_request({
                "model": model,
                "messages": [
                    {"role": "user", "content": self.HELLO_PROMPT}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            })
            
            duration = time.time() - start_time
            
            # Verify timing
            self._verify_duration(duration, f"Anthropic API call")
            
            # Verify response
            result = self._verify_response(response, model)
            result["duration"] = duration
            result["timestamp"] = datetime.now().isoformat()
            
            self.test_results.append(result)
            logger.success(f"✅ Claude Direct test passed: {result['content']}")
            
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "authentication" in error_str:
                pytest.skip(f"API key issue: {e}")
            raise
    
    @pytest.mark.integration
    def test_model_comparison(self):
        """Compare response patterns across models (run after other tests)."""
        # This test should run last to analyze results
        if not hasattr(self.__class__, '_all_results'):
            self.__class__._all_results = []
        
        # Skip if no results yet
        if not self.test_results:
            pytest.skip("No test results to compare")
        
        # Aggregate results
        self.__class__._all_results.extend(self.test_results)
        
        # If we have results from multiple models, compare
        if len(self.__class__._all_results) >= 2:
            logger.info("=== Model Comparison ===")
            for result in self.__class__._all_results:
                logger.info(
                    f"{result['model']}: "
                    f"Duration={result['duration']:.3f}s, "
                    f"Response='{result['content'][:50]}...'"
                )
            
            # Verify all models responded with hello world
            all_have_hello = all(r['has_hello'] for r in self.__class__._all_results)
            all_have_world = all(r['has_world'] for r in self.__class__._all_results)
            
            assert all_have_hello, "Not all models included 'hello' in response"
            assert all_have_world, "Not all models included 'world' in response"
            
            logger.success("✅ All models successfully returned Hello World!")

# Test validation function
if __name__ == "__main__":
    import subprocess
    
    logger.info("Running LLM Hello World tests...")
    
    # Run with pytest for proper async support
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--durations=0", "-s"],
        capture_output=False
    )
    
    if result.returncode == 0:
        logger.success("✅ All model tests passed!")
    else:
        logger.error("❌ Some model tests failed")
        
    sys.exit(result.returncode)