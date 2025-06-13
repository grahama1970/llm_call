"""
Base provider interface for LLM providers.
Module: base_provider.py

This module defines the abstract base class that all LLM providers must implement.

Links:
- ABC documentation: https://docs.python.org/3/library/abc.html

Sample usage:
    class MyProvider(BaseLLMProvider):
        async def complete(self, messages, **kwargs):
            # Implementation

Expected output:
    Provider-specific response
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def complete(
        self, 
        messages: List[Dict[str, str]], 
        response_format: Any = None,
        **kwargs
    ) -> Any:
        """
        Complete a chat conversation.
        
        This method signature matches what retry_with_validation expects
        for its llm_call_func parameter.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            response_format: Optional response format specification
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Provider-specific response object
        """
        pass
    
    def validate_response(self, response: Any) -> bool:
        """
        Validate the response from the provider.
        
        Base implementation always returns True. Override in subclasses
        for provider-specific validation.
        
        Args:
            response: The response from the provider
            
        Returns:
            bool: True if response is valid, False otherwise
        """
        return True


# Test function
if __name__ == "__main__":
    import sys
    from loguru import logger
    
    logger.info("Testing base provider...")
    
    # Test that we can't instantiate the abstract class
    try:
        provider = BaseLLMProvider()
        logger.error("L Should not be able to instantiate abstract class")
        sys.exit(1)
    except TypeError as e:
        logger.success(" Cannot instantiate abstract class (as expected)")
    
    # Test that we can create a concrete implementation
    class TestProvider(BaseLLMProvider):
        async def complete(self, messages, response_format=None, **kwargs):
            return {"test": "response"}
    
    try:
        provider = TestProvider()
        logger.success(" Can create concrete implementation")
        sys.exit(0)
    except Exception as e:
        logger.error(f"L Failed to create concrete implementation: {e}")
        sys.exit(1)