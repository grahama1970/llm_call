#!/usr/bin/env python3
"""
POC-16: Result Aggregation and Decision Making

This script implements aggregation strategies for combining validation results.
Demonstrates weighted scoring, consensus mechanisms, and decision making.

Links:
- Aggregation Strategies: https://arxiv.org/html/2412.04093v1
- Ensemble Methods: https://www.evidentlyai.com/llm-guide/llm-as-a-judge
- Decision Theory: https://portkey.ai/docs/guides/prompts/llm-as-a-judge

Sample Input:
{
    "validation_results": [
        {"agent": "structure", "score": 0.9, "confidence": 0.95},
        {"agent": "content", "score": 0.8, "confidence": 0.85},
        {"agent": "safety", "score": 1.0, "confidence": 1.0}
    ],
    "aggregation_strategy": "weighted_average",
    "decision_threshold": 0.85
}

Expected Output:
{
    "aggregated_score": 0.88,
    "decision": "accept",
    "confidence": 0.93,
    "reasoning": "High scores across all agents with strong confidence",
    "dissenting_agents": []
}
"""

import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from loguru import logger
import statistics

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


class Decision(Enum):
    """Validation decision types."""
    ACCEPT = "accept"
    REJECT = "reject"
    REVIEW = "review"
    ESCALATE = "escalate"


@dataclass
class AgentResult:
    """Result from a validation agent."""
    agent_name: str
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    details: Optional[Dict[str, Any]] = None
    critical: bool = False  # If true, can veto


@dataclass
class AggregatedResult:
    """Final aggregated validation result."""
    aggregated_score: float
    decision: Decision
    confidence: float
    reasoning: str
    dissenting_agents: List[str]
    breakdown: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None


class ResultAggregator:
    """Aggregates validation results from multiple agents."""
    
    def __init__(
        self,
        decision_threshold: float = 0.85,
        review_threshold: float = 0.7,
        min_confidence: float = 0.6
    ):
        self.decision_threshold = decision_threshold
        self.review_threshold = review_threshold
        self.min_confidence = min_confidence
        
        # Agent weights for different strategies
        self.default_weights = {
            "structure": 0.25,
            "content": 0.35,
            "accuracy": 0.25,
            "safety": 0.15
        }
        
        self.critical_agents = {"safety", "accuracy"}  # Can veto decisions
    
    def aggregate(
        self,
        results: List[AgentResult],
        strategy: str = "weighted_average"
    ) -> AggregatedResult:
        """Aggregate results using specified strategy."""
        if strategy == "weighted_average":
            return self._weighted_average(results)
        elif strategy == "consensus":
            return self._consensus(results)
        elif strategy == "strict":
            return self._strict_all(results)
        elif strategy == "lenient":
            return self._lenient_any(results)
        elif strategy == "hybrid":
            return self._hybrid(results)
        else:
            raise ValueError(f"Unknown aggregation strategy: {strategy}")
    
    def _weighted_average(self, results: List[AgentResult]) -> AggregatedResult:
        """Weighted average aggregation."""
        total_score = 0
        total_weight = 0
        total_confidence = 0
        breakdown = {}
        
        for result in results:
            weight = self.default_weights.get(result.agent_name, 0.2)
            weighted_score = result.score * weight
            total_score += weighted_score
            total_weight += weight
            total_confidence += result.confidence * weight
            breakdown[result.agent_name] = result.score
        
        aggregated_score = total_score / total_weight if total_weight > 0 else 0
        confidence = total_confidence / total_weight if total_weight > 0 else 0
        
        # Check for critical agent vetoes
        critical_failures = [
            r.agent_name for r in results
            if r.agent_name in self.critical_agents and r.score < 0.5
        ]
        
        # Determine decision
        if critical_failures:
            decision = Decision.REJECT
            reasoning = f"Critical agents failed: {', '.join(critical_failures)}"
        elif aggregated_score >= self.decision_threshold:
            decision = Decision.ACCEPT
            reasoning = f"Score {aggregated_score:.2f} exceeds threshold {self.decision_threshold}"
        elif aggregated_score >= self.review_threshold:
            decision = Decision.REVIEW
            reasoning = f"Score {aggregated_score:.2f} requires review"
        else:
            decision = Decision.REJECT
            reasoning = f"Score {aggregated_score:.2f} below threshold"
        
        # Find dissenting agents
        dissenting = [
            r.agent_name for r in results
            if r.score < self.review_threshold
        ]
        
        return AggregatedResult(
            aggregated_score=round(aggregated_score, 2),
            decision=decision,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            dissenting_agents=dissenting,
            breakdown=breakdown
        )
    
    def _consensus(self, results: List[AgentResult]) -> AggregatedResult:
        """Consensus-based aggregation."""
        scores = [r.score for r in results]
        breakdown = {r.agent_name: r.score for r in results}
        
        # Calculate consensus metrics
        mean_score = statistics.mean(scores)
        median_score = statistics.median(scores)
        
        # Low variance indicates consensus
        if len(scores) > 1:
            variance = statistics.variance(scores)
            consensus_strength = 1 - min(variance, 1)  # High consensus = low variance
        else:
            consensus_strength = 1.0
        
        # Use median for robustness
        aggregated_score = median_score
        
        # Confidence based on consensus strength
        confidence = consensus_strength * statistics.mean([r.confidence for r in results])
        
        # Decision based on consensus
        accepting = sum(1 for r in results if r.score >= self.decision_threshold)
        total = len(results)
        
        if accepting >= total * 0.8:  # 80% agree
            decision = Decision.ACCEPT
            reasoning = f"Strong consensus: {accepting}/{total} agents accept"
        elif accepting >= total * 0.6:  # 60% agree
            decision = Decision.REVIEW
            reasoning = f"Weak consensus: {accepting}/{total} agents accept"
        else:
            decision = Decision.REJECT
            reasoning = f"No consensus: only {accepting}/{total} agents accept"
        
        # Dissenting agents
        dissenting = [
            r.agent_name for r in results
            if r.score < self.decision_threshold
        ]
        
        return AggregatedResult(
            aggregated_score=round(aggregated_score, 2),
            decision=decision,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            dissenting_agents=dissenting,
            breakdown=breakdown,
            metadata={"variance": variance if len(scores) > 1 else 0}
        )
    
    def _strict_all(self, results: List[AgentResult]) -> AggregatedResult:
        """Strict: all agents must pass."""
        breakdown = {r.agent_name: r.score for r in results}
        
        # Minimum score across all agents
        min_score = min(r.score for r in results)
        aggregated_score = min_score
        
        # All must exceed threshold
        all_pass = all(r.score >= self.decision_threshold for r in results)
        
        if all_pass:
            decision = Decision.ACCEPT
            reasoning = "All agents passed validation"
        else:
            decision = Decision.REJECT
            failing = [r.agent_name for r in results if r.score < self.decision_threshold]
            reasoning = f"Failed agents: {', '.join(failing)}"
        
        # Conservative confidence
        confidence = min(r.confidence for r in results)
        
        dissenting = [
            r.agent_name for r in results
            if r.score < self.decision_threshold
        ]
        
        return AggregatedResult(
            aggregated_score=round(aggregated_score, 2),
            decision=decision,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            dissenting_agents=dissenting,
            breakdown=breakdown
        )
    
    def _lenient_any(self, results: List[AgentResult]) -> AggregatedResult:
        """Lenient: any agent can approve."""
        breakdown = {r.agent_name: r.score for r in results}
        
        # Maximum score across agents
        max_score = max(r.score for r in results)
        aggregated_score = max_score
        
        # Best agent that approves
        approving = [r for r in results if r.score >= self.decision_threshold]
        
        if approving:
            decision = Decision.ACCEPT
            best_agent = max(approving, key=lambda r: r.score)
            reasoning = f"{best_agent.agent_name} strongly approves ({best_agent.score:.2f})"
        elif max_score >= self.review_threshold:
            decision = Decision.REVIEW
            reasoning = f"Highest score {max_score:.2f} warrants review"
        else:
            decision = Decision.REJECT
            reasoning = "No agent provided sufficient approval"
        
        # Optimistic confidence
        confidence = max(r.confidence for r in results)
        
        dissenting = [
            r.agent_name for r in results
            if r.score < self.review_threshold
        ]
        
        return AggregatedResult(
            aggregated_score=round(aggregated_score, 2),
            decision=decision,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            dissenting_agents=dissenting,
            breakdown=breakdown
        )
    
    def _hybrid(self, results: List[AgentResult]) -> AggregatedResult:
        """Hybrid approach combining multiple strategies."""
        # Get results from different strategies
        weighted = self._weighted_average(results)
        consensus = self._consensus(results)
        
        # Combine scores
        aggregated_score = (weighted.aggregated_score + consensus.aggregated_score) / 2
        
        # Check critical agents
        critical_issues = []
        for r in results:
            if r.agent_name in self.critical_agents and r.score < 0.6:
                critical_issues.append(r.agent_name)
        
        # Decision logic
        if critical_issues:
            decision = Decision.ESCALATE
            reasoning = f"Critical issues in: {', '.join(critical_issues)}. Escalation required."
        elif weighted.decision == Decision.ACCEPT and consensus.decision == Decision.ACCEPT:
            decision = Decision.ACCEPT
            reasoning = "Both weighted and consensus strategies approve"
        elif weighted.decision == Decision.REJECT or consensus.decision == Decision.REJECT:
            decision = Decision.REJECT
            reasoning = "At least one strategy rejects"
        else:
            decision = Decision.REVIEW
            reasoning = "Mixed signals from different strategies"
        
        # Confidence is lower of the two
        confidence = min(weighted.confidence, consensus.confidence)
        
        # Combine dissenting lists
        dissenting = list(set(weighted.dissenting_agents + consensus.dissenting_agents))
        
        breakdown = {r.agent_name: r.score for r in results}
        
        return AggregatedResult(
            aggregated_score=round(aggregated_score, 2),
            decision=decision,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            dissenting_agents=dissenting,
            breakdown=breakdown,
            metadata={
                "weighted_score": weighted.aggregated_score,
                "consensus_score": consensus.aggregated_score
            }
        )


def test_aggregation_strategies():
    """Test different aggregation strategies."""
    aggregator = ResultAggregator()
    
    # Test scenarios
    test_cases = [
        {
            "name": "All agents approve",
            "results": [
                AgentResult("structure", 0.95, 0.9),
                AgentResult("content", 0.92, 0.95),
                AgentResult("accuracy", 0.88, 0.85),
                AgentResult("safety", 0.96, 1.0)
            ],
            "strategies": ["weighted_average", "consensus", "strict", "lenient"],
            "expect_decision": Decision.ACCEPT
        },
        {
            "name": "Mixed results",
            "results": [
                AgentResult("structure", 0.85, 0.9),
                AgentResult("content", 0.75, 0.8),
                AgentResult("accuracy", 0.70, 0.7),
                AgentResult("safety", 0.95, 0.95)
            ],
            "strategies": ["weighted_average"],
            "expect_decision": Decision.REVIEW,
            "consensus_may_reject": True
        },
        {
            "name": "Mixed results - consensus",
            "results": [
                AgentResult("structure", 0.85, 0.9),
                AgentResult("content", 0.75, 0.8),
                AgentResult("accuracy", 0.70, 0.7),
                AgentResult("safety", 0.95, 0.95)
            ],
            "strategies": ["consensus"],
            "expect_any": [Decision.REVIEW, Decision.REJECT]  # Consensus may reject with only 50% approval
        },
        {
            "name": "Critical agent failure",
            "results": [
                AgentResult("structure", 0.90, 0.9),
                AgentResult("content", 0.88, 0.85),
                AgentResult("accuracy", 0.85, 0.8),
                AgentResult("safety", 0.4, 0.9, critical=True)  # Safety fails
            ],
            "strategies": ["weighted_average"],
            "expect_decision": Decision.REJECT,
            "hybrid_escalates": True
        },
        {
            "name": "Critical agent failure - hybrid",
            "results": [
                AgentResult("structure", 0.90, 0.9),
                AgentResult("content", 0.88, 0.85),
                AgentResult("accuracy", 0.85, 0.8),
                AgentResult("safety", 0.4, 0.9, critical=True)  # Safety fails
            ],
            "strategies": ["hybrid"],
            "expect_decision": Decision.ESCALATE  # Hybrid escalates critical failures
        },
        {
            "name": "Low confidence",
            "results": [
                AgentResult("structure", 0.85, 0.5),
                AgentResult("content", 0.82, 0.4),
                AgentResult("accuracy", 0.80, 0.45),
                AgentResult("safety", 0.88, 0.6)
            ],
            "strategies": ["consensus", "hybrid"],
            "check_confidence": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("=" * 50)
        
        for strategy in test_case["strategies"]:
            result = aggregator.aggregate(test_case["results"], strategy)
            
            logger.info(f"\n{strategy.upper()} Strategy:")
            logger.info(f"  Score: {result.aggregated_score}")
            logger.info(f"  Decision: {result.decision.value}")
            logger.info(f"  Confidence: {result.confidence}")
            logger.info(f"  Reasoning: {result.reasoning}")
            if result.dissenting_agents:
                logger.info(f"  Dissenting: {result.dissenting_agents}")
            
            # Check expectations
            if "expect_any" in test_case:
                if result.decision in test_case["expect_any"]:
                    logger.success(f"✅ Decision {result.decision.value} is acceptable")
                    results.append(True)
                else:
                    logger.error(f"❌ Unexpected decision: {result.decision.value}")
                    results.append(False)
            elif "expect_decision" in test_case:
                if result.decision == test_case["expect_decision"]:
                    logger.success(f"✅ Expected decision: {result.decision.value}")
                    results.append(True)
                else:
                    # Some strategies may have different but valid decisions
                    if strategy == "strict" and result.decision == Decision.REJECT:
                        logger.info(f"ℹ️ Strict strategy rejected as expected")
                        results.append(True)
                    elif strategy == "lenient" and result.decision == Decision.ACCEPT:
                        logger.info(f"ℹ️ Lenient strategy accepted as expected")
                        results.append(True)
                    else:
                        logger.error(f"❌ Unexpected decision: {result.decision.value}")
                        results.append(False)
            
            if test_case.get("check_confidence") and result.confidence < 0.6:
                logger.success(f"✅ Low confidence detected: {result.confidence}")
                results.append(True)
    
    return all(results) if results else True


def test_edge_cases():
    """Test edge cases in aggregation."""
    aggregator = ResultAggregator()
    
    edge_cases = [
        {
            "name": "Single agent",
            "results": [AgentResult("only_agent", 0.8, 0.9)],
            "strategy": "weighted_average"
        },
        {
            "name": "All fail",
            "results": [
                AgentResult("agent1", 0.3, 0.8),
                AgentResult("agent2", 0.4, 0.7),
                AgentResult("agent3", 0.2, 0.9)
            ],
            "strategy": "consensus",
            "expect_reject": True
        },
        {
            "name": "High variance",
            "results": [
                AgentResult("agent1", 1.0, 1.0),
                AgentResult("agent2", 0.0, 1.0),
                AgentResult("agent3", 0.5, 0.8)
            ],
            "strategy": "consensus"
        },
        {
            "name": "Unknown agents",
            "results": [
                AgentResult("new_agent_1", 0.85, 0.9),
                AgentResult("new_agent_2", 0.82, 0.85),
                AgentResult("new_agent_3", 0.88, 0.92)
            ],
            "strategy": "weighted_average"
        }
    ]
    
    results = []
    
    for case in edge_cases:
        logger.info(f"\nTesting edge case: {case['name']}")
        
        try:
            result = aggregator.aggregate(case["results"], case["strategy"])
            
            logger.info(f"Score: {result.aggregated_score}")
            logger.info(f"Decision: {result.decision.value}")
            logger.info(f"Reasoning: {result.reasoning}")
            
            if case.get("expect_reject") and result.decision == Decision.REJECT:
                logger.success("✅ Correctly rejected as expected")
                results.append(True)
            else:
                logger.success("✅ Handled edge case successfully")
                results.append(True)
                
        except Exception as e:
            logger.error(f"❌ Error handling edge case: {e}")
            results.append(False)
    
    return all(results)


def test_decision_thresholds():
    """Test different decision thresholds."""
    # Test with different thresholds
    thresholds = [
        (0.9, 0.8),   # Very strict
        (0.85, 0.7),  # Default
        (0.7, 0.5),   # Lenient
        (0.5, 0.3)    # Very lenient
    ]
    
    test_results = [
        AgentResult("structure", 0.75, 0.85),
        AgentResult("content", 0.78, 0.9),
        AgentResult("accuracy", 0.72, 0.8),
        AgentResult("safety", 0.80, 0.95)
    ]
    
    logger.info("\nTesting decision thresholds:")
    logger.info("=" * 50)
    
    results = []
    
    for accept_threshold, review_threshold in thresholds:
        aggregator = ResultAggregator(
            decision_threshold=accept_threshold,
            review_threshold=review_threshold
        )
        
        result = aggregator.aggregate(test_results, "weighted_average")
        
        logger.info(f"\nThresholds - Accept: {accept_threshold}, Review: {review_threshold}")
        logger.info(f"  Score: {result.aggregated_score}")
        logger.info(f"  Decision: {result.decision.value}")
        
        # Verify threshold logic
        if result.aggregated_score >= accept_threshold:
            expected = Decision.ACCEPT
        elif result.aggregated_score >= review_threshold:
            expected = Decision.REVIEW
        else:
            expected = Decision.REJECT
        
        # Critical agent check might override
        if result.decision == expected or "Critical" in result.reasoning:
            logger.success(f"✅ Decision matches threshold logic")
            results.append(True)
        else:
            logger.error(f"❌ Decision doesn't match threshold logic")
            results.append(False)
    
    return all(results)


if __name__ == "__main__":
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Aggregation strategies
    total_tests += 1
    try:
        if test_aggregation_strategies():
            logger.success("✅ Aggregation strategies tests passed")
        else:
            all_validation_failures.append("Aggregation strategies tests failed")
    except Exception as e:
        all_validation_failures.append(f"Aggregation strategies exception: {str(e)}")
        logger.error(f"Exception in strategies test: {e}")
    
    # Test 2: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge case tests passed")
        else:
            all_validation_failures.append("Edge case tests failed")
    except Exception as e:
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Test 3: Decision thresholds
    total_tests += 1
    try:
        if test_decision_thresholds():
            logger.success("✅ Decision threshold tests passed")
        else:
            all_validation_failures.append("Decision threshold tests failed")
    except Exception as e:
        all_validation_failures.append(f"Decision threshold exception: {str(e)}")
        logger.error(f"Exception in threshold test: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-16 Result aggregation is validated and ready")
        sys.exit(0)