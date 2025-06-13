#!/usr/bin/env python3
"""
Module: test_openai_simple.py
Description: Integration test for OpenAI API using real LLM calls

External Dependencies:
- litellm: https://docs.litellm.ai/
- pytest-asyncio: https://pytest-asyncio.readthedocs.io/

Sample Input:
>>> response = await litellm.acompletion(model="gpt-3.5-turbo", messages=[...])

Expected Output:
>>> response.choices[0].message.content == "Hello World!"

Example Usage:
>>> pytest tests/integration/test_openai_simple.py -v
"""

import os
import time
import pytest
import litellm
from loguru import logger

class TestOpenAIIntegration:
    """Test OpenAI integration with real API calls."""
    
    @pytest.mark.asyncio
    async def test_openai_hello_world(self):
        """Test OpenAI API with a simple hello world request."""
        start_time = time.time()
        
        # Load API key from environment
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set in environment")
        
        logger.info(f"Testing OpenAI with API key ending in: ***{api_key[-8:]}")
        
        try:
            response = await litellm.acompletion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say exactly: Hello World!"}],
                temperature=0.1,
                max_tokens=100
            )
            
            duration = time.time() - start_time
            content = response.choices[0].message.content
            
            # Verify response
            assert response is not None, "No response from OpenAI"
            assert hasattr(response, 'choices'), "Response missing choices"
            assert len(response.choices) > 0, "No choices in response"
            assert content is not None, "No content in response"
            
            # Verify timing - real API calls should take >50ms
            assert duration > 0.05, f"API call too fast ({duration:.3f}s) - might be mocked"
            
            logger.success(f"OpenAI test passed: '{content}' in {duration:.3f}s")
            
            # Content verification (may vary slightly)
            assert "hello" in content.lower() or "world" in content.lower(), \
                f"Unexpected response: {content}"
                
        except Exception as e:
            logger.error(f"OpenAI test failed: {e}")
            # Re-raise to fail the test properly
            raise
    
    @pytest.mark.asyncio
    async def test_openai_error_handling(self):
        """Test OpenAI error handling with invalid request."""
        start_time = time.time()
        
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            pytest.skip("OPENAI_API_KEY not set in environment")
        
        with pytest.raises(Exception):  # Expecting an error
            # Invalid model name should cause error
            await litellm.acompletion(
                model="gpt-99-invalid",
                messages=[{"role": "user", "content": "Test"}],
                timeout=10
            )
        
        duration = time.time() - start_time
        # Error should still take some time due to network
        assert duration > 0.01, f"Error returned too quickly ({duration:.3f}s)"

if __name__ == "__main__":
    # When run directly, use pytest
    pytest.main([__file__, "-v"])