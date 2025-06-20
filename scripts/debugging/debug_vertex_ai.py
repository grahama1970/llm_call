#!/usr/bin/env python3
"""
Module: debug_vertex_ai.py
Description: Debug why Vertex AI is returning empty content

External Dependencies:
- litellm: https://docs.litellm.ai/
- loguru: https://loguru.readthedocs.io/

Sample Input:
>>> # No input required

Expected Output:
>>> # Detailed debug information about Vertex AI responses

Example Usage:
>>> python scripts/debug_vertex_ai.py
"""

import asyncio
import os
import litellm
from loguru import logger
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_call.core.caller import make_llm_request

# Enable debug logging
litellm.set_verbose = True


async def test_vertex_directly():
    """Test Vertex AI directly with LiteLLM."""
    logger.info("Testing Vertex AI directly with LiteLLM...")
    
    try:
        # Direct LiteLLM call
        response = await litellm.acompletion(
            model="vertex_ai/gemini-2.5-flash-preview-05-20",
            messages=[{"role": "user", "content": "Say exactly: HELLO WORLD"}],
            temperature=0.1,
            max_tokens=20
        )
        
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response dict: {response.dict() if hasattr(response, 'dict') else response}")
        
        # Try different ways to get content
        if hasattr(response, 'choices'):
            logger.info(f"Has choices attribute")
            if response.choices:
                choice = response.choices[0]
                logger.info(f"Choice type: {type(choice)}")
                logger.info(f"Choice dict: {choice if isinstance(choice, dict) else vars(choice)}")
                
                # Get message
                message = choice.get('message') if isinstance(choice, dict) else choice.message
                logger.info(f"Message type: {type(message)}")
                logger.info(f"Message content: {message}")
                
                # Get content
                if isinstance(message, dict):
                    content = message.get('content', '')
                else:
                    content = getattr(message, 'content', '')
                
                logger.info(f"Final content: '{content}'")
                logger.info(f"Content length: {len(content) if content else 0}")
        
        return response
        
    except Exception as e:
        logger.error(f"Direct LiteLLM call failed: {e}")
        logger.exception(e)
        return None


async def test_through_llm_call():
    """Test through our llm_call wrapper."""
    logger.info("\nTesting through llm_call wrapper...")
    
    try:
        result = await make_llm_request({
            "model": "vertex_ai/gemini-2.5-flash-preview-05-20",
            "messages": [{"role": "user", "content": "Say exactly: HELLO WORLD"}],
            "temperature": 0.1,
            "max_tokens": 20
        })
        
        logger.info(f"Result type: {type(result)}")
        logger.info(f"Result: {result}")
        
        if result:
            # Extract content
            if hasattr(result, 'choices'):
                content = result.choices[0]['message']['content']
            else:
                content = result['choices'][0]['message']['content']
            
            logger.info(f"Extracted content: '{content}'")
            logger.info(f"Content length: {len(content) if content else 0}")
        
        return result
        
    except Exception as e:
        logger.error(f"llm_call wrapper failed: {e}")
        logger.exception(e)
        return None


async def test_different_models():
    """Test different Vertex AI models."""
    models = [
        "vertex_ai/gemini-2.5-flash-preview-05-20",
        "vertex_ai/gemini-1.5-flash",
        "vertex_ai/gemini-pro"
    ]
    
    for model in models:
        logger.info(f"\nTesting model: {model}")
        try:
            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": "Count to 3"}],
                temperature=0.1,
                max_tokens=50
            )
            
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                logger.success(f"✅ {model}: Got content: {content[:50]}...")
            else:
                logger.error(f"❌ {model}: No content in response")
                
        except Exception as e:
            logger.error(f"❌ {model}: Failed - {e}")


async def main():
    """Main debug function."""
    logger.info("=== VERTEX AI DEBUG SESSION ===")
    
    # Check environment
    logger.info("\n1. Checking environment variables...")
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    logger.info(f"GOOGLE_APPLICATION_CREDENTIALS: {creds}")
    
    if creds and os.path.exists(creds):
        logger.success("✅ Credentials file exists")
    else:
        logger.error("❌ Credentials file missing!")
    
    project = os.getenv("LITELLM_VERTEX_PROJECT")
    location = os.getenv("LITELLM_VERTEX_LOCATION")
    logger.info(f"LITELLM_VERTEX_PROJECT: {project}")
    logger.info(f"LITELLM_VERTEX_LOCATION: {location}")
    
    # Test direct LiteLLM
    logger.info("\n2. Testing direct LiteLLM call...")
    await test_vertex_directly()
    
    # Test through wrapper
    logger.info("\n3. Testing through llm_call wrapper...")
    await test_through_llm_call()
    
    # Test different models
    logger.info("\n4. Testing different Vertex AI models...")
    await test_different_models()


if __name__ == "__main__":
    # Set up detailed logging
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
    
    # Run debug session
    asyncio.run(main())