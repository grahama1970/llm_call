#!/usr/bin/env python3
"""Test the RL integration for claude_max_proxy"""

import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.llm_call.rl_integration.integration_example import RLEnhancedLLMClient, SafeRLDeployment


async def test_rl_provider_selection():
    """Test that RL provider selection works"""
    print("=== Testing RL Provider Selection ===\n")
    
    # Provider configuration
    providers_config = {
        "gpt-4": {"api_key": "test-key-1", "cost_per_1k": 0.03},
        "claude-3": {"api_key": "test-key-2", "cost_per_1k": 0.02},
        "llama-local": {"endpoint": "http://localhost:8080", "cost_per_1k": 0.0}
    }
    
    # Create RL client
    client = RLEnhancedLLMClient(
        providers_config=providers_config,
        use_rl=True,
        rl_exploration_rate=0.2  # Higher exploration for testing
    )
    
    # Test various request types
    test_requests = [
        ("Write a short poem", "creative", 200),
        ("Explain quantum computing", "analytical", 500),
        ("Write a Python function to sort a list", "code", 300),
        ("Hello, how are you?", "simple", 50),
        ("Analyze the pros and cons of renewable energy", "analytical", 1000),
    ]
    
    print("Running test requests...\n")
    
    for prompt, request_type, max_tokens in test_requests:
        response = await client.call_llm(
            prompt=prompt,
            max_tokens=max_tokens
        )
        
        print(f"Request Type: {request_type}")
        print(f"  Prompt: {prompt[:50]}...")
        print(f"  Selected Provider: {response['provider']}")
        print(f"  Latency: {response['latency']:.3f}s")
        print(f"  Cost: ${response['cost']:.4f}")
        print(f"  Selection Scores: {response['selection_metadata'].get('selection_scores', [])}")
        print()
    
    # Show RL report
    print("\n" + "="*50)
    print(client.get_rl_report())
    
    return client


async def test_ab_deployment():
    """Test A/B testing deployment"""
    print("\n\n=== Testing A/B Deployment ===\n")
    
    # Create baseline client (mock)
    class BaselineClient:
        async def call_llm(self, prompt, **kwargs):
            # Always uses expensive provider
            await asyncio.sleep(0.5)
            return {"response": f"Baseline response to: {prompt}", "provider": "gpt-4"}
    
    # Create RL client
    providers_config = {
        "gpt-4": {"cost": 0.03},
        "claude-3": {"cost": 0.02},
        "llama-local": {"cost": 0.0}
    }
    
    rl_client = RLEnhancedLLMClient(providers_config=providers_config)
    baseline_client = BaselineClient()
    
    # Create safe deployment wrapper
    safe_deployment = SafeRLDeployment(
        rl_client=rl_client,
        baseline_client=baseline_client,
        initial_rl_percentage=0.3  # 30% to RL
    )
    
    # Run some requests
    print("Running A/B test with 30% RL traffic...\n")
    
    for i in range(10):
        response = await safe_deployment.call_llm(
            prompt=f"Test request {i}",
            max_tokens=100
        )
        print(f"Request {i}: Group={response['ab_test_group']}, "
              f"Cost=${response.get('cost', 0.03):.4f}")
    
    # Show A/B test results
    results = safe_deployment.get_ab_test_results()
    
    print("\n=== A/B Test Results ===")
    print(f"RL Traffic: {results['rl_percentage']*100:.0f}%")
    print(f"\nRL Group:")
    print(f"  Requests: {results['rl']['requests']}")
    print(f"  Avg Cost: ${results['rl']['avg_cost']:.4f}")
    print(f"  Avg Latency: {results['rl']['avg_latency']:.3f}s")
    print(f"\nBaseline Group:")
    print(f"  Requests: {results['baseline']['requests']}")
    print(f"  Avg Cost: ${results['baseline']['avg_cost']:.4f}")
    print(f"  Avg Latency: {results['baseline']['avg_latency']:.3f}s")
    
    if 'cost_reduction' in results:
        print(f"\nCost Reduction: {results['cost_reduction']:.1f}%")
    if 'latency_reduction' in results:
        print(f"Latency Reduction: {results['latency_reduction']:.1f}%")


async def main():
    """Run all tests"""
    print("🚀 Testing RL Integration for claude_max_proxy\n")
    
    # Test basic RL provider selection
    client = await test_rl_provider_selection()
    
    # Test A/B deployment
    await test_ab_deployment()
    
    print("\n✅ All tests completed!")
    print("\nTo integrate into production:")
    print("1. Install rl_commons: pip install -e /home/graham/workspace/experiments/rl_commons")
    print("2. Import RLProviderSelector in your existing LLMClient")
    print("3. Start with 10% traffic using SafeRLDeployment")
    print("4. Monitor performance and gradually increase traffic")


if __name__ == "__main__":
    asyncio.run(main())
