"""RL-based provider selection using graham_rl_commons"""
Module: provider_selector.py

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import time
import logging
from collections import defaultdict

# Import from rl_commons
try:
    from rl_commons import ContextualBandit, RLState, RLAction, RLReward, RLTracker
except ImportError:
    raise ImportError(
        "rl_commons not found. Install with: "
        "uv add git+file:///home/graham/workspace/experiments/rl_commons"
    )

logger = logging.getLogger(__name__)


@dataclass
class ProviderMetrics:
    """Track provider performance metrics"""
    provider_name: str
    total_requests: int = 0
    successful_requests: int = 0
    total_latency: float = 0.0
    total_cost: float = 0.0
    error_count: int = 0
    quality_scores: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        return self.successful_requests / max(1, self.total_requests)
    
    @property
    def avg_latency(self) -> float:
        return self.total_latency / max(1, self.successful_requests)
    
    @property
    def avg_quality(self) -> float:
        return np.mean(self.quality_scores) if self.quality_scores else 0.5
    
    @property
    def avg_cost_per_request(self) -> float:
        return self.total_cost / max(1, self.successful_requests)


class RLProviderSelector:
    """
    RL-based provider selection for LLM calls
    Uses contextual bandits to optimize provider selection
    """
    
    def __init__(self, 
                 providers: List[str],
                 feature_extractor: Optional[callable] = None,
                 exploration_rate: float = 0.1,
                 model_path: Optional[Path] = None):
        """
        Initialize RL provider selector
        
        Args:
            providers: List of provider names
            feature_extractor: Custom feature extraction function
            exploration_rate: Initial exploration rate (alpha for UCB)
            model_path: Path to load existing model
        """
        self.providers = providers
        self.n_providers = len(providers)
        self.feature_extractor = feature_extractor or self._default_feature_extractor
        
        # Determine feature dimension
        dummy_request = {"prompt": "test", "max_tokens": 100}
        dummy_features = self.feature_extractor(dummy_request)
        self.n_features = len(dummy_features)
        
        # Initialize contextual bandit
        self.bandit = ContextualBandit(
            name="provider_selector",
            n_arms=self.n_providers,
            n_features=self.n_features,
            alpha=exploration_rate
        )
        
        # Initialize tracking
        self.tracker = RLTracker("llm_call_rl")
        self.provider_metrics = {p: ProviderMetrics(p) for p in providers}
        
        # Load existing model if provided
        if model_path and model_path.exists():
            self.load_model(model_path)
            logger.info(f"Loaded RL model from {model_path}")
    
    def _default_feature_extractor(self, request: Dict[str, Any]) -> np.ndarray:
        """Default feature extraction from request"""
        features = []
        
        # 1. Prompt length (normalized)
        prompt_length = len(request.get("prompt", ""))
        features.append(np.log1p(prompt_length) / 10)
        
        # 2. Time of day features (cyclic encoding)
        hour = time.localtime().tm_hour
        features.append(np.sin(2 * np.pi * hour / 24))
        features.append(np.cos(2 * np.pi * hour / 24))
        
        # 3. Request complexity estimate
        prompt_lower = request.get("prompt", "").lower()
        complexity_keywords = ["analyze", "explain", "summarize", "code", "math", "write"]
        complexity = sum(1 for kw in complexity_keywords if kw in prompt_lower)
        features.append(complexity / len(complexity_keywords))
        
        # 4. Expected response length
        max_tokens = request.get("max_tokens", 1000)
        features.append(np.log1p(max_tokens) / 10)
        
        # 5. Request type indicators
        is_code = float("code" in prompt_lower or "function" in prompt_lower)
        features.append(is_code)
        
        is_creative = float(any(kw in prompt_lower for kw in ["story", "poem", "creative"]))
        features.append(is_creative)
        
        is_analytical = float(any(kw in prompt_lower for kw in ["analyze", "compare", "evaluate"]))
        features.append(is_analytical)
        
        return np.array(features)
    
    def select_provider(self, request: Dict[str, Any], explore: bool = True) -> Tuple[str, Dict[str, Any]]:
        """
        Select optimal provider for request
        
        Args:
            request: LLM request dictionary
            explore: Whether to explore vs pure exploitation
            
        Returns:
            Tuple of (provider_name, selection_metadata)
        """
        # Extract features
        features = self.feature_extractor(request)
        state = RLState(features=features, context={"request": request})
        
        # Get RL decision
        action = self.bandit.select_action(state, explore=explore)
        selected_provider = self.providers[action.action_id]
        
        # Track the decision
        self.tracker.log_step(0, {"provider_selected": action.action_id})
        
        # Prepare metadata
        metadata = {
            "provider": selected_provider,
            "provider_index": action.action_id,
            "features": features.tolist(),
            "exploration": action.parameters.get("exploration", False),
            "selection_scores": action.parameters.get("ucb_values", []),
            "timestamp": time.time()
        }
        
        logger.debug(f"Selected provider: {selected_provider} (scores: {action.parameters.get('ucb_values', [])})")
        
        return selected_provider, metadata
    
    def update_from_result(self, 
                          request: Dict[str, Any],
                          provider: str,
                          result: Dict[str, Any],
                          latency: float,
                          cost: float,
                          quality_score: Optional[float] = None) -> Dict[str, float]:
        """
        Update RL model based on observed results
        
        Args:
            request: Original request
            provider: Provider that was used
            result: Response from provider
            latency: Request latency in seconds
            cost: Request cost in dollars
            quality_score: Optional quality score (0-1)
            
        Returns:
            Metrics from the update
        """
        # Get provider index
        provider_idx = self.providers.index(provider)
        
        # Extract features
        features = self.feature_extractor(request)
        state = RLState(features=features)
        
        # Update provider metrics
        metrics = self.provider_metrics[provider]
        metrics.total_requests += 1
        
        success = result.get("success", True) and not result.get("error")
        
        if success:
            metrics.successful_requests += 1
            metrics.total_latency += latency
            metrics.total_cost += cost
            
            # Estimate quality if not provided
            if quality_score is None:
                # Simple heuristic based on response length and structure
                response_text = result.get("response", "")
                expected_length = request.get("max_tokens", 1000)
                length_ratio = min(1.0, len(response_text) / max(100, expected_length))
                quality_score = 0.5 + 0.5 * length_ratio  # Basic estimate
            
            metrics.quality_scores.append(quality_score)
            
            # Calculate composite reward
            # Normalize components to [0, 1]
            normalized_latency = min(1.0, latency / 10.0)  # 10s = worst case
            normalized_cost = min(1.0, cost / 0.10)  # $0.10 = expensive
            
            # Multi-objective reward
            reward_value = (
                0.5 * quality_score +           # 50% weight on quality
                0.3 * (1 - normalized_latency) + # 30% weight on speed
                0.2 * (1 - normalized_cost)      # 20% weight on cost
            )
        else:
            metrics.error_count += 1
            reward_value = -0.5  # Penalty for errors
            quality_score = 0.0
        
        # Create RL action and reward
        action = RLAction(action_type="select_provider", action_id=provider_idx)
        reward = RLReward(
            value=reward_value,
            components={
                "quality": quality_score,
                "speed": 1 - min(1.0, latency / 10.0),
                "cost_efficiency": 1 - min(1.0, cost / 0.10),
                "success": float(success)
            }
        )
        
        # Update bandit
        update_metrics = self.bandit.update(state, action, reward, state)
        
        # Track metrics
        self.tracker.log_training_metrics(update_metrics)
        self.tracker.log_step(reward_value, {
            "provider": provider_idx,
            "latency": latency,
            "cost": cost,
            "quality": quality_score
        })
        
        return update_metrics
    
    def get_provider_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all providers"""
        stats = {}
        
        for provider, metrics in self.provider_metrics.items():
            stats[provider] = {
                "total_requests": metrics.total_requests,
                "success_rate": round(metrics.success_rate, 3),
                "avg_latency": round(metrics.avg_latency, 3) if metrics.successful_requests > 0 else None,
                "avg_quality": round(metrics.avg_quality, 3) if metrics.quality_scores else None,
                "avg_cost": round(metrics.avg_cost_per_request, 4) if metrics.successful_requests > 0 else None,
                "error_count": metrics.error_count
            }
        
        # Add bandit arm selection stats
        bandit_metrics = self.bandit.get_metrics()
        for i, provider in enumerate(self.providers):
            if f"arm_{i}_percentage" in bandit_metrics:
                stats[provider]["selection_percentage"] = round(bandit_metrics[f"arm_{i}_percentage"], 3)
        
        return stats
    
    def save_model(self, path: Path) -> None:
        """Save the RL model"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.bandit.save(path)
        
        # Also save provider metrics
        metrics_path = path.parent / f"{path.stem}_metrics.json"
        import json
        metrics_data = {
            provider: {
                "total_requests": m.total_requests,
                "successful_requests": m.successful_requests,
                "total_latency": m.total_latency,
                "total_cost": m.total_cost,
                "error_count": m.error_count,
                "quality_scores": m.quality_scores
            }
            for provider, m in self.provider_metrics.items()
        }
        metrics_path.write_text(json.dumps(metrics_data, indent=2))
    
    def load_model(self, path: Path) -> None:
        """Load the RL model"""
        self.bandit.load(path)
        
        # Try to load provider metrics
        metrics_path = path.parent / f"{path.stem}_metrics.json"
        if metrics_path.exists():
            import json
            metrics_data = json.loads(metrics_path.read_text())
            
            for provider, data in metrics_data.items():
                if provider in self.provider_metrics:
                    m = self.provider_metrics[provider]
                    m.total_requests = data["total_requests"]
                    m.successful_requests = data["successful_requests"]
                    m.total_latency = data["total_latency"]
                    m.total_cost = data["total_cost"]
                    m.error_count = data["error_count"]
                    m.quality_scores = data["quality_scores"]
    
    def get_recommendation_report(self) -> str:
        """Generate a recommendation report"""
        stats = self.get_provider_stats()
        bandit_metrics = self.bandit.get_metrics()
        
        report = ["=== RL Provider Selection Report ===\n"]
        
        report.append(f"Total Requests: {bandit_metrics['training_steps']}")
        report.append(f"Average Reward: {bandit_metrics['avg_reward']:.3f}")
        report.append(f"Exploration Rate (alpha): {bandit_metrics['alpha']}\n")
        
        report.append("Provider Performance:")
        for provider, data in stats.items():
            report.append(f"\n{provider}:")
            report.append(f"  Selection Rate: {data.get('selection_percentage', 0)*100:.1f}%")
            report.append(f"  Success Rate: {data['success_rate']*100:.1f}%")
            
            if data['avg_latency'] is not None:
                report.append(f"  Avg Latency: {data['avg_latency']:.2f}s")
            
            if data['avg_quality'] is not None:
                report.append(f"  Avg Quality: {data['avg_quality']:.2f}")
            
            if data['avg_cost'] is not None:
                report.append(f"  Avg Cost: ${data['avg_cost']:.4f}")
        
        # Recommendations
        report.append("\n=== Recommendations ===")
        
        # Find best provider by selection percentage
        if bandit_metrics['training_steps'] > 50:
            most_selected = bandit_metrics.get('most_selected_arm', 0)
            best_provider = self.providers[most_selected]
            report.append(f"Primary Provider: {best_provider} (selected {stats[best_provider].get('selection_percentage', 0)*100:.1f}% of the time)")
        
        return "\n".join(report)
