#!/usr/bin/env python3
"""
Example: Using LLM Call's synchronous API.

This demonstrates how to use the synchronous wrappers for simple,
non-async Python code.
"""

from llm_call import ask_sync, chat_sync, call_sync


def main():
    """Demonstrate synchronous API usage."""
    print("LLM Call Synchronous API Examples")
    print("=" * 50)
    
    # Example 1: Simple question with ask_sync
    print("\n1. Using ask_sync for a simple question:")
    response = ask_sync(
        "What are the benefits of Python programming?",
        model="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=150
    )
    print(f"Response: {response}")
    
    # Example 2: Code generation with validation
    print("\n2. Using ask_sync with validation:")
    code = ask_sync(
        "Write a Python function to calculate factorial",
        model="gpt-3.5-turbo",
        validate=["code", "python"],
        temperature=0
    )
    print(f"Generated code:\n{code}")
    
    # Example 3: Interactive chat session
    print("\n3. Using chat_sync for conversation:")
    session = chat_sync(
        model="gpt-3.5-turbo",
        system="You are a helpful programming tutor. Keep explanations concise.",
        temperature=0.5
    )
    
    # First question
    response1 = session.send("What is a Python decorator?")
    print(f"Q: What is a Python decorator?")
    print(f"A: {response1}")
    
    # Follow-up question
    response2 = session.send("Can you show me a simple example?")
    print(f"\nQ: Can you show me a simple example?")
    print(f"A: {response2}")
    
    # Check conversation history
    history = session.get_history()
    print(f"\nConversation has {len(history)} messages")
    
    # Example 4: Using call_sync with configuration
    print("\n4. Using call_sync with config dict:")
    config = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a JSON API that returns structured data."},
            {"role": "user", "content": "List 3 Python web frameworks with their key features"}
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"}
    }
    
    result = call_sync(config)
    print(f"Structured response: {result}")
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")


if __name__ == "__main__":
    main()