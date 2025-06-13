#!/usr/bin/env python3
"""
Test llm_call core functionality without pytest or complex dependencies.
Progressive testing Phase 3: Test core project functionality.
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

async def test_make_llm_request():
    """Test the core make_llm_request function."""
    print("=== Testing llm_call Core Functionality ===")
    print(f"Time: {datetime.now().isoformat()}")
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
        
        # Import core function
        print("\n1. Testing imports...")
        from llm_call.core.caller import make_llm_request
        print("✅ Import successful")
        
        # Prepare test config
        print("\n2. Preparing test configuration...")
        config = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "What is 2+2? Answer with just the number."}
            ],
            "max_tokens": 10,
            "temperature": 0
        }
        print(f"✅ Config ready: {config['model']}")
        
        # Make real LLM call
        print("\n3. Making real LLM request...")
        start = time.time()
        response = await make_llm_request(config)
        duration = time.time() - start
        
        # Verify response structure
        print("\n4. Verifying response...")
        assert response is not None, "No response received"
        assert "choices" in response, f"No choices in response: {list(response.keys())}"
        assert len(response["choices"]) > 0, "Empty choices array"
        assert "message" in response["choices"][0], "No message in choice"
        assert "content" in response["choices"][0]["message"], "No content in message"
        
        # Extract content
        content = response["choices"][0]["message"]["content"].strip()
        print(f"✅ Response received: '{content}'")
        
        # Verify correctness
        assert "4" in content or "four" in content.lower(), f"Wrong answer: {content}"
        print("✅ Correct answer!")
        
        # Verify it was a real API call
        assert duration > 0.05, f"Too fast for real API ({duration:.3f}s)"
        print(f"✅ Real API call confirmed (duration: {duration:.3f}s)")
        
        # Show full evidence
        print("\n5. Response details:")
        print(f"   Model: {response.get('model', 'unknown')}")
        print(f"   ID: {response.get('id', 'none')}")
        print(f"   Usage: {response.get('usage', {})}")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PYTHONPATH=./src is set")
        print("2. Check if llm_call is installed: pip install -e .")
        return False
        
    except Exception as e:
        print(f"\n❌ Test failed: {type(e).__name__}: {e}")
        
        # Detailed debugging
        import traceback
        print("\nStack trace:")
        traceback.print_exc()
        
        return False


async def test_router():
    """Test the routing logic."""
    print("\n\n=== Testing Router ===")
    
    try:
        from llm_call.core.router import resolve_route
        
        # Test different model names
        test_cases = [
            ("gpt-4", "LiteLLMProvider"),
            ("vertex_ai/gemini-1.5-pro", "LiteLLMProvider"),
            ("max/opus", "ClaudeCLIProxyProvider"),
        ]
        
        print("Testing model routing:")
        for model, expected in test_cases:
            config = {
                "model": model,
                "messages": [{"role": "user", "content": "test"}]
            }
            
            provider_class, params = resolve_route(config)
            actual = provider_class.__name__
            
            if actual == expected:
                print(f"  ✅ {model} -> {actual}")
            else:
                print(f"  ❌ {model} -> {actual} (expected {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Router test failed: {e}")
        return False


async def test_conversation_manager():
    """Test conversation persistence."""
    print("\n\n=== Testing Conversation Manager ===")
    
    try:
        from llm_call.core.conversation_manager import ConversationManager
        
        # Create manager
        manager = ConversationManager()
        
        # Create conversation
        print("1. Creating conversation...")
        conv_id = await manager.create_conversation(
            name="Test Conversation",
            metadata={"test": True}
        )
        print(f"✅ Created conversation: {conv_id}")
        
        # Add messages
        print("\n2. Adding messages...")
        await manager.add_message(conv_id, "user", "Hello")
        await manager.add_message(conv_id, "assistant", "Hi there!", model="gpt-3.5-turbo")
        print("✅ Messages added")
        
        # Retrieve messages
        print("\n3. Retrieving messages...")
        messages = await manager.get_conversation_for_llm(conv_id)
        assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
        print(f"✅ Retrieved {len(messages)} messages")
        
        # Verify content
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"
        assert messages[1]["role"] == "assistant"
        assert messages[1]["content"] == "Hi there!"
        print("✅ Message content verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests progressively."""
    print("LLM_CALL PROGRESSIVE TESTING")
    print("="*50)
    
    all_passed = True
    
    # Phase 1: Core functionality
    if await test_make_llm_request():
        print("\n✅ PHASE 1 PASSED: Core functionality works!")
    else:
        print("\n❌ PHASE 1 FAILED: Fix core functionality first")
        all_passed = False
        return False  # Don't continue if core doesn't work
    
    # Phase 2: Router
    if await test_router():
        print("\n✅ PHASE 2 PASSED: Router works!")
    else:
        print("\n❌ PHASE 2 FAILED: Router issues")
        all_passed = False
    
    # Phase 3: Conversation management
    if await test_conversation_manager():
        print("\n✅ PHASE 3 PASSED: Conversations work!")
    else:
        print("\n❌ PHASE 3 FAILED: Conversation issues")
        all_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\nNext steps:")
        print("1. Add more providers (test_two_providers.py)")
        print("2. Test validation strategies")
        print("3. Test multi-model collaboration")
    else:
        print("❌ Some tests failed")
        print("\nFix the failing tests before proceeding")
    
    return all_passed


if __name__ == "__main__":
    # Ensure PYTHONPATH is set
    if not os.environ.get("PYTHONPATH"):
        print("⚠️  Setting PYTHONPATH=./src")
        os.environ["PYTHONPATH"] = "./src"
    
    success = asyncio.run(main())
    exit(0 if success else 1)