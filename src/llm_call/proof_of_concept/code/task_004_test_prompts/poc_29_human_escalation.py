#!/usr/bin/env python3
"""
POC 29: Human Escalation Flow
Task: Implement human-in-the-loop escalation for validation failures
Expected Output: Clear escalation to human review with context preservation
Links:
- https://docs.anthropic.com/claude/docs/human-in-the-loop
- https://arxiv.org/abs/2303.08774 (Constitutional AI)
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


class HumanDecision(Enum):
    """Possible human decisions"""
    APPROVE = "approve"
    REJECT = "reject"
    RETRY_WITH_MODIFICATION = "retry_with_modification"
    ESCALATE_FURTHER = "escalate_further"
    ABORT = "abort"


@dataclass
class HumanReviewContext:
    """Context provided to human reviewer"""
    request_id: str
    original_prompt: str
    llm_response: str
    validation_failures: List[Dict[str, Any]]
    retry_history: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class HumanReviewResult:
    """Result from human review"""
    decision: HumanDecision
    feedback: Optional[str] = None
    modified_prompt: Optional[str] = None
    additional_instructions: Optional[str] = None
    reviewer_id: Optional[str] = None
    review_time_seconds: float = 0.0


class HumanEscalationManager:
    """Manages human-in-the-loop escalation"""
    
    def __init__(self, 
                 notification_handler: Optional[Callable] = None,
                 review_interface: Optional[Callable] = None):
        self.notification_handler = notification_handler or self._default_notification
        self.review_interface = review_interface or self._default_review_interface
        self.pending_reviews: Dict[str, HumanReviewContext] = {}
        self.completed_reviews: List[Tuple[HumanReviewContext, HumanReviewResult]] = []
    
    async def escalate_to_human(self, context: HumanReviewContext) -> HumanReviewResult:
        """Escalate issue to human reviewer"""
        # Store context
        self.pending_reviews[context.request_id] = context
        
        # Notify human
        await self.notification_handler(context)
        
        # Get human decision
        start_time = datetime.now()
        result = await self.review_interface(context)
        result.review_time_seconds = (datetime.now() - start_time).total_seconds()
        
        # Record completion
        self.completed_reviews.append((context, result))
        del self.pending_reviews[context.request_id]
        
        # Log decision
        logger.info(f"🧑 Human decision for {context.request_id}: {result.decision.value}")
        if result.feedback:
            logger.info(f"   Feedback: {result.feedback}")
        
        return result
    
    async def _default_notification(self, context: HumanReviewContext):
        """Default notification handler - just logs"""
        logger.warning("=" * 60)
        logger.warning("🚨 HUMAN REVIEW REQUIRED")
        logger.warning("=" * 60)
        logger.warning(f"Request ID: {context.request_id}")
        logger.warning(f"Original Prompt: {context.original_prompt[:100]}...")
        logger.warning(f"Validation Failures: {len(context.validation_failures)}")
        logger.warning(f"Retry Attempts: {len(context.retry_history)}")
        logger.warning("=" * 60)
    
    async def _default_review_interface(self, context: HumanReviewContext) -> HumanReviewResult:
        """Default review interface - simulated for POC"""
        # In production, this would be a web UI, Slack bot, etc.
        logger.info("\n📋 Review Context:")
        logger.info(f"Original Prompt: {context.original_prompt}")
        logger.info(f"LLM Response: {context.llm_response[:200]}...")
        logger.info(f"Failures: {json.dumps(context.validation_failures, indent=2)}")
        
        # Simulate human review based on context
        if len(context.retry_history) >= 3:
            # Too many retries - abort
            return HumanReviewResult(
                decision=HumanDecision.ABORT,
                feedback="Too many retry attempts without success",
                reviewer_id="poc_simulator"
            )
        elif "syntax" in str(context.validation_failures).lower():
            # Syntax error - provide fix
            return HumanReviewResult(
                decision=HumanDecision.RETRY_WITH_MODIFICATION,
                feedback="Syntax error detected, providing corrected prompt",
                modified_prompt=context.original_prompt + "\n\nIMPORTANT: Ensure proper Python syntax with correct indentation.",
                reviewer_id="poc_simulator"
            )
        else:
            # General approval with guidance
            return HumanReviewResult(
                decision=HumanDecision.APPROVE,
                feedback="Approved with minor issues noted",
                additional_instructions="Focus on clarity and completeness",
                reviewer_id="poc_simulator"
            )
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get statistics about human reviews"""
        if not self.completed_reviews:
            return {"total_reviews": 0}
        
        decisions = [r.decision.value for _, r in self.completed_reviews]
        avg_time = sum(r.review_time_seconds for _, r in self.completed_reviews) / len(self.completed_reviews)
        
        return {
            "total_reviews": len(self.completed_reviews),
            "pending_reviews": len(self.pending_reviews),
            "decision_breakdown": {
                decision: decisions.count(decision) 
                for decision in set(decisions)
            },
            "average_review_time": f"{avg_time:.1f}s",
            "reviewers": list(set(r.reviewer_id for _, r in self.completed_reviews if r.reviewer_id))
        }


# Integration with retry system
class HumanEscalationError(Exception):
    """Raised when human escalation is needed"""
    def __init__(self, context: HumanReviewContext):
        self.context = context
        super().__init__(f"Human escalation required for request {context.request_id}")


async def retry_with_human_escalation(
    func: Callable,
    validation_func: Callable,
    max_retries: int = 3,
    escalation_manager: Optional[HumanEscalationManager] = None
) -> Any:
    """Retry with human escalation on repeated failures"""
    
    if not escalation_manager:
        escalation_manager = HumanEscalationManager()
    
    request_id = f"REQ-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    retry_history = []
    original_args = None
    
    for attempt in range(max_retries + 1):
        try:
            # Execute function
            result = await func(*original_args) if original_args else await func()
            
            # Validate result
            validation_result = await validation_func(result)
            
            if validation_result.get("valid", False):
                logger.success(f"✅ Validation passed on attempt {attempt + 1}")
                return result
            else:
                # Validation failed
                failure = {
                    "attempt": attempt + 1,
                    "result": result,
                    "validation_errors": validation_result.get("errors", [])
                }
                retry_history.append(failure)
                
                if attempt < max_retries:
                    logger.warning(f"⚠️  Validation failed on attempt {attempt + 1}, retrying...")
                    await asyncio.sleep(1)  # Basic delay
                else:
                    # Max retries reached - escalate to human
                    logger.error(f"❌ Max retries reached, escalating to human")
                    
                    context = HumanReviewContext(
                        request_id=request_id,
                        original_prompt=str(original_args) if original_args else "No args",
                        llm_response=str(result),
                        validation_failures=[f["validation_errors"] for f in retry_history],
                        retry_history=retry_history,
                        metadata={"function": func.__name__}
                    )
                    
                    # Get human decision
                    human_result = await escalation_manager.escalate_to_human(context)
                    
                    # Handle decision
                    if human_result.decision == HumanDecision.APPROVE:
                        logger.info("🧑 Human approved despite validation failures")
                        return result
                    elif human_result.decision == HumanDecision.RETRY_WITH_MODIFICATION:
                        logger.info("🧑 Human provided modification, retrying...")
                        # Modify args based on human input
                        if human_result.modified_prompt:
                            # In real implementation, modify function args
                            pass
                        continue
                    elif human_result.decision == HumanDecision.ABORT:
                        raise HumanEscalationError(context)
                    else:
                        raise ValueError(f"Unhandled human decision: {human_result.decision}")
                        
        except Exception as e:
            if isinstance(e, HumanEscalationError):
                raise
            logger.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt >= max_retries:
                raise


async def main():
    """Test human escalation scenarios"""
    
    # Test scenarios
    scenarios = [
        {
            "name": "Repeated Validation Failures",
            "func": lambda: {"code": "def foo()\n  return 42"},  # Syntax error
            "validator": lambda r: {"valid": False, "errors": ["Syntax error: missing colon"]},
            "max_retries": 1,  # Results in 2 attempts total, under 3 threshold
            "expected_decision": HumanDecision.RETRY_WITH_MODIFICATION
        },
        {
            "name": "Too Many Retries",
            "func": lambda: {"result": "Always fails"},
            "validator": lambda r: {"valid": False, "errors": ["Generic failure"]},
            "max_retries": 3,  # Results in 4 attempts, triggers abort at 3+
            "expected_decision": HumanDecision.ABORT
        },
        {
            "name": "Human Override Approval",
            "func": lambda: {"result": "Close enough"},
            "validator": lambda r: {"valid": False, "errors": ["Minor issues"]},
            "max_retries": 0,  # Only 1 attempt, definitely under threshold
            "expected_decision": HumanDecision.APPROVE
        }
    ]
    
    logger.info("=" * 60)
    logger.info("HUMAN ESCALATION TESTING")
    logger.info("=" * 60)
    
    escalation_manager = HumanEscalationManager()
    passed = 0
    failed = 0
    
    for scenario in scenarios:
        logger.info(f"\n🧪 Testing: {scenario['name']}")
        logger.info("-" * 40)
        
        try:
            # Create async wrapper for lambda
            async def async_func():
                return scenario["func"]()
            
            async def async_validator(result):
                return scenario["validator"](result)
            
            result = await retry_with_human_escalation(
                async_func,
                async_validator,
                max_retries=scenario.get("max_retries", 2),
                escalation_manager=escalation_manager
            )
            
            # Check if we got expected outcome
            stats = escalation_manager.get_review_stats()
            last_decision = None
            if escalation_manager.completed_reviews:
                _, last_review = escalation_manager.completed_reviews[-1]
                last_decision = last_review.decision
            
            if last_decision == scenario["expected_decision"]:
                passed += 1
                logger.success(f"✅ Got expected decision: {last_decision.value}")
            else:
                failed += 1
                logger.error(f"❌ Expected {scenario['expected_decision'].value}, got {last_decision}")
                
        except HumanEscalationError as e:
            if scenario["expected_decision"] == HumanDecision.ABORT:
                passed += 1
                logger.success("✅ Correctly aborted after human review")
            else:
                failed += 1
                logger.error(f"❌ Unexpected abort: {e}")
        except Exception as e:
            failed += 1
            logger.error(f"❌ Unexpected error: {e}")
    
    # Display statistics
    logger.info("\n" + "=" * 60)
    logger.info("HUMAN REVIEW STATISTICS")
    logger.info("=" * 60)
    
    stats = escalation_manager.get_review_stats()
    logger.info(f"Total Reviews: {stats.get('total_reviews', 0)}")
    logger.info(f"Decision Breakdown: {json.dumps(stats.get('decision_breakdown', {}), indent=2)}")
    logger.info(f"Average Review Time: {stats.get('average_review_time', 'N/A')}")
    
    # Test notification formats
    logger.info("\n" + "=" * 60)
    logger.info("NOTIFICATION FORMAT EXAMPLES")
    logger.info("=" * 60)
    
    # Example Slack notification
    slack_format = """
🚨 *Human Review Required*
*Request ID:* REQ-20240315-143022
*Original Task:* Generate Python function for data validation
*Failures:* 3 validation errors after 4 retry attempts
*Priority:* High
*Review Link:* https://review.example.com/REQ-20240315-143022
"""
    logger.info("Slack Notification Example:")
    logger.info(slack_format)
    
    # Example Email notification
    email_format = """
Subject: [ACTION REQUIRED] LLM Validation Review - REQ-20240315-143022

Dear Reviewer,

An LLM response requires human review due to repeated validation failures.

Details:
- Request ID: REQ-20240315-143022
- Task: Generate Python function for data validation
- Attempts: 4
- Latest Error: Syntax error in generated code

Please review at: https://review.example.com/REQ-20240315-143022

Best regards,
LLM Validation System
"""
    logger.info("\nEmail Notification Example:")
    logger.info(email_format)
    
    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    total_tests = passed + failed
    if failed == 0:
        logger.success(f"✅ ALL TESTS PASSED: {passed}/{total_tests}")
        return 0
    else:
        logger.error(f"❌ TESTS FAILED: {failed}/{total_tests} failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))