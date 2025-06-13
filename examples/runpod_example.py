"""
Module: runpod_example.py
Description: Example of using Runpod inference with llm_call

This example demonstrates how to use Runpod endpoints for LLM inference
through the llm_call package. Runpod allows you to deploy and inference
30-70B models with OpenAI-compatible endpoints.

External Dependencies:
- llm_call: Main package for LLM routing
- asyncio: For async operations

Sample Input:
>>> # Using pod ID in model name
>>> config = {
...     "model": "runpod/abc123xyz/llama-3-70b",
...     "messages": [{"role": "user", "content": "Explain quantum computing"}]
... }

Expected Output:
>>> # Response from Llama 3 70B model running on Runpod
>>> "Quantum computing is a revolutionary approach to computation..."

Example Usage:
>>> python examples/runpod_example.py
"""

import asyncio
from llm_call import make_llm_request
from loguru import logger


async def runpod_with_pod_id():
    """Example using pod ID in the model name."""
    logger.info("=== Runpod Example with Pod ID ===")
    
    # Replace 'abc123xyz' with your actual Runpod pod ID
    config = {
        "model": "runpod/abc123xyz/llama-3-70b",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            },
            {
                "role": "user",
                "content": "What are the key differences between classical and quantum computing? Be concise."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = await make_llm_request(**config)
        logger.success(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")


async def runpod_with_api_base():
    """Example using explicit api_base parameter."""
    logger.info("\n=== Runpod Example with API Base ===")
    
    # Use this approach when you want to specify the endpoint directly
    config = {
        "model": "runpod/llama-3-70b",  # No pod ID in model name
        "api_base": "https://your-pod-id-8000.proxy.runpod.net/v1",  # Replace with your endpoint
        "messages": [
            {
                "role": "user",
                "content": "Write a haiku about artificial intelligence."
            }
        ],
        "temperature": 0.9,
        "max_tokens": 50
    }
    
    try:
        response = await make_llm_request(**config)
        logger.success(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")


async def runpod_with_custom_model():
    """Example using a custom fine-tuned model on Runpod."""
    logger.info("\n=== Runpod Example with Custom Model ===")
    
    # Example with a custom fine-tuned model
    config = {
        "model": "runpod/your-pod-id/your-custom-model",
        "messages": [
            {
                "role": "user",
                "content": "Generate a Python function to calculate fibonacci numbers."
            }
        ],
        "temperature": 0.2,  # Lower temperature for code generation
        "max_tokens": 300
    }
    
    try:
        response = await make_llm_request(**config)
        logger.success(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")


async def runpod_streaming_example():
    """Example with streaming responses from Runpod."""
    logger.info("\n=== Runpod Streaming Example ===")
    
    config = {
        "model": "runpod/your-pod-id/llama-3-70b",
        "messages": [
            {
                "role": "user",
                "content": "Tell me a short story about a robot learning to paint."
            }
        ],
        "temperature": 0.8,
        "max_tokens": 500,
        "stream": True  # Enable streaming
    }
    
    try:
        # Note: Streaming support depends on your llm_call configuration
        response = await make_llm_request(**config)
        
        if hasattr(response, '__aiter__'):  # Check if response is async iterable
            logger.info("Streaming response:")
            async for chunk in response:
                print(chunk, end='', flush=True)
            print()  # New line after streaming
        else:
            logger.success(f"Response: {response}")
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """Run all examples."""
    logger.info("""
    Runpod Integration Examples
    ==========================
    
    Before running these examples, you need:
    1. A Runpod account with deployed models
    2. Your pod ID from the Runpod dashboard
    3. The model should be running (check pod status)
    
    Model name formats:
    - runpod/{pod_id}/{model_name} - Uses pod ID to construct endpoint
    - runpod/{model_name} - Requires api_base parameter
    
    Note: Replace 'abc123xyz' and 'your-pod-id' with actual pod IDs
    """)
    
    # Run examples (comment out the ones you don't need)
    asyncio.run(runpod_with_pod_id())
    # asyncio.run(runpod_with_api_base())
    # asyncio.run(runpod_with_custom_model())
    # asyncio.run(runpod_streaming_example())


if __name__ == "__main__":
    main()