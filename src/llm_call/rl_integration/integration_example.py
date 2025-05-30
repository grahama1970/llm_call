"""Example of integrating RL provider selection into existing LLMClient"""

from typing import Dict, Any, Optional
from pathlib import Path
import random
import logging

from .provider_selector import RLProviderSelector

logger = logging.getLogger(__name__)


class RLEnhancedLLMClient:
    """
    Example LLM Client with RL-based provider selection
    This shows how to integrate RL into the existing claude_max_proxy
    """
    
    def __init__(self, 
                 providers_config: Dict[str, Dict[str, Any]],
                 use_rl: bool = True,
                 rl_exploration_rate: float = 0.1,
                 fallback_provider: Optional[str] = None):
        """
        Initialize LLM client with RL provider selection
        
        Args:
            providers_config: Dict mapping provider names to their configs
            use_rl: Whether to use RL for provider selection
            rl_exploration_rate: How much to explore vs exploit (0-1)
            fallback_provider: Provider to use if RL fails
        """
        self.providers_config = providers_config
        self.use_rl = use_rl
        self.fallback_provider = fallback_provider or list(providers_config.keys())[0]
        
        if self.use_rl:
            # Initialize RL selector
            self.rl_selector = RLProviderSelector(
                providers=list(providers_config.keys()),
                exploration_rate=rl_exploration_rate
            )
            
            # Try to load existing model
            model_path = Path.home() / ".llm_call" / "rl_model.json"
            if model_path.exists():
                try:
                    self.rl_selector.load_model(model_path)
                    logger.info("Loaded existing RL model")
                except Exception as e:
                    logger.warning(f"Failed to load RL model: {e}")
        else:
            self.rl_selector = None
    
    async def call_llm(self, 
                       prompt: str, 
                       max_tokens: int = 1000,
                       temperature: float = 0.7,
                       **kwargs) -> Dict[str, Any]:
        """
        Call LLM with RL-optimized provider selection
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with provider info
        """
        request = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        # Select provider
        if self.use_rl and self.rl_selector:
            try:
                provider, selection_metadata = self.rl_selector.select_provider(request)
                logger.info(f"RL selected provider: {provider}")
            except Exception as e:
                logger.error(f"RL selection failed: {e}, using fallback")
                provider = self.fallback_provider
                selection_metadata = {"fallback": True}
        else:
            # Random selection without RL
            provider = random.choice(list(self.providers_config.keys()))
            selection_metadata = {"method": "random"}
        
        # Make the actual API call
        import time
        start_time = time.time()
        
        try:
            # This is where you would integrate with actual provider APIs
            # For now, we simulate a response
            response = await self._call_provider(provider, request)
            
            latency = time.time() - start_time
            success = True
            
            # Estimate cost (would be calculated from actual API response)
            cost = self._estimate_cost(provider, request, response)
            
        except Exception as e:
            logger.error(f"Provider {provider} failed: {e}")
            response = {"error": str(e)}
            latency = time.time() - start_time
            success = False
            cost = 0.0
        
        # Update RL model if enabled
        if self.use_rl and self.rl_selector and "fallback" not in selection_metadata:
            try:
                # In production, quality_score would be calculated from actual response
                quality_score = self._estimate_quality(response) if success else 0.0
                
                update_metrics = self.rl_selector.update_from_result(
                    request=request,
                    provider=provider,
                    result={"success": success, "response": response.get("text", "")},
                    latency=latency,
                    cost=cost,
                    quality_score=quality_score
                )
                
                logger.debug(f"RL update metrics: {update_metrics}")
                
                # Periodically save model
                if self.rl_selector.bandit.training_steps % 100 == 0:
                    self._save_rl_model()
                    
            except Exception as e:
                logger.error(f"Failed to update RL model: {e}")
        
        # Return response with metadata
        return {
            "response": response,
            "provider": provider,
            "latency": latency,
            "cost": cost,
            "selection_metadata": selection_metadata
        }
    
    async def _call_provider(self, provider: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actually call the provider API
        In production, this would use the real provider APIs
        """
        # Simulate different provider behaviors
        import asyncio
        
        if provider == "gpt-4":
            await asyncio.sleep(0.5)  # Simulate latency
            return {
                "text": f"GPT-4 response to: {request['prompt']}",
                "model": "gpt-4",
                "usage": {"total_tokens": 150}
            }
        elif provider == "claude-3":
            await asyncio.sleep(0.3)
            return {
                "text": f"Claude-3 response to: {request['prompt']}",
                "model": "claude-3-opus",
                "usage": {"total_tokens": 140}
            }
        else:  # llama-local
            await asyncio.sleep(0.1)
            return {
                "text": f"Llama response to: {request['prompt']}",
                "model": "llama-2-70b",
                "usage": {"total_tokens": 160}
            }
    
    def _estimate_cost(self, provider: str, request: Dict[str, Any], response: Dict[str, Any]) -> float:
        """Estimate cost based on provider and usage"""
        # Simple cost model (in production, use actual pricing)
        costs_per_1k_tokens = {
            "gpt-4": 0.03,
            "claude-3": 0.02,
            "llama-local": 0.0
        }
        
        tokens = response.get("usage", {}).get("total_tokens", 100)
        cost_per_token = costs_per_1k_tokens.get(provider, 0.01) / 1000
        
        return tokens * cost_per_token
    
    def _estimate_quality(self, response: Dict[str, Any]) -> float:
        """Estimate response quality (0-1)"""
        # In production, this could use:
        # - Response length vs expected
        # - Coherence scoring
        # - Task-specific validation
        # - User feedback
        
        text = response.get("text", "")
        if not text:
            return 0.0
        
        # Simple heuristic
        length_score = min(1.0, len(text) / 500)  # Expect ~500 chars
        
        # Check for common quality indicators
        quality_indicators = ["therefore", "because", "however", "specifically"]
        indicator_score = sum(1 for ind in quality_indicators if ind in text.lower()) / len(quality_indicators)
        
        return 0.7 * length_score + 0.3 * indicator_score
    
    def _save_rl_model(self):
        """Save the RL model to disk"""
        if self.rl_selector:
            model_path = Path.home() / ".llm_call" / "rl_model.json"
            model_path.parent.mkdir(exist_ok=True)
            
            try:
                self.rl_selector.save_model(model_path)
                logger.info("Saved RL model")
            except Exception as e:
                logger.error(f"Failed to save RL model: {e}")
    
    def get_rl_report(self) -> Optional[str]:
        """Get RL optimization report"""
        if self.rl_selector:
            return self.rl_selector.get_recommendation_report()
        return None


class SafeRLDeployment:
    """
    Wrapper for safe gradual rollout of RL
    Allows A/B testing between RL and baseline
    """
    
    def __init__(self,
                 rl_client: RLEnhancedLLMClient,
                 baseline_client: Any,
                 initial_rl_percentage: float = 0.1):
        """
        Initialize safe deployment wrapper
        
        Args:
            rl_client: RL-enhanced client
            baseline_client: Existing baseline client
            initial_rl_percentage: Percentage of traffic to send to RL (0-1)
        """
        self.rl_client = rl_client
        self.baseline_client = baseline_client
        self.rl_percentage = initial_rl_percentage
        
        # Track comparative metrics
        self.rl_metrics = {"requests": 0, "total_cost": 0.0, "total_latency": 0.0}
        self.baseline_metrics = {"requests": 0, "total_cost": 0.0, "total_latency": 0.0}
    
    async def call_llm(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Route request to RL or baseline based on percentage"""
        use_rl = random.random() < self.rl_percentage
        
        if use_rl:
            result = await self.rl_client.call_llm(prompt, **kwargs)
            self.rl_metrics["requests"] += 1
            self.rl_metrics["total_cost"] += result.get("cost", 0)
            self.rl_metrics["total_latency"] += result.get("latency", 0)
            result["ab_test_group"] = "rl"
        else:
            # Baseline doesn't have our metadata, so we wrap it
            import time
            start = time.time()
            
            result = await self.baseline_client.call_llm(prompt, **kwargs)
            
            latency = time.time() - start
            # Estimate cost for baseline (would need actual implementation)
            cost = 0.03  # Assume baseline always uses expensive provider
            
            self.baseline_metrics["requests"] += 1
            self.baseline_metrics["total_cost"] += cost
            self.baseline_metrics["total_latency"] += latency
            
            result["ab_test_group"] = "baseline"
            result["latency"] = latency
            result["cost"] = cost
        
        return result
    
    def increase_rl_traffic(self, new_percentage: float):
        """Gradually increase RL traffic"""
        self.rl_percentage = min(1.0, new_percentage)
        logger.info(f"RL traffic percentage set to: {self.rl_percentage*100:.1f}%")
    
    def get_ab_test_results(self) -> Dict[str, Any]:
        """Get A/B test comparison"""
        results = {
            "rl_percentage": self.rl_percentage,
            "rl": {
                "requests": self.rl_metrics["requests"],
                "avg_cost": self.rl_metrics["total_cost"] / max(1, self.rl_metrics["requests"]),
                "avg_latency": self.rl_metrics["total_latency"] / max(1, self.rl_metrics["requests"])
            },
            "baseline": {
                "requests": self.baseline_metrics["requests"],
                "avg_cost": self.baseline_metrics["total_cost"] / max(1, self.baseline_metrics["requests"]),
                "avg_latency": self.baseline_metrics["total_latency"] / max(1, self.baseline_metrics["requests"])
            }
        }
        
        # Calculate improvements
        if results["baseline"]["avg_cost"] > 0:
            results["cost_reduction"] = (
                (results["baseline"]["avg_cost"] - results["rl"]["avg_cost"]) / 
                results["baseline"]["avg_cost"] * 100
            )
        
        if results["baseline"]["avg_latency"] > 0:
            results["latency_reduction"] = (
                (results["baseline"]["avg_latency"] - results["rl"]["avg_latency"]) / 
                results["baseline"]["avg_latency"] * 100
            )
        
        return results


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example provider configuration
        providers_config = {
            "gpt-4": {"api_key": "sk-...", "cost_per_1k": 0.03},
            "claude-3": {"api_key": "sk-...", "cost_per_1k": 0.02},
            "llama-local": {"endpoint": "http://localhost:8080", "cost_per_1k": 0.0}
        }
        
        # Create RL-enhanced client
        rl_client = RLEnhancedLLMClient(
            providers_config=providers_config,
            use_rl=True,
            rl_exploration_rate=0.1
        )
        
        # Test a few requests
        for i in range(5):
            response = await rl_client.call_llm(
                prompt=f"Test request {i}: Explain quantum computing briefly",
                max_tokens=200
            )
            print(f"Request {i}: Provider={response['provider']}, Cost=${response['cost']:.4f}")
        
        # Show RL report
        print("\n" + rl_client.get_rl_report())
    
    asyncio.run(main())
