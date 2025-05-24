#!/usr/bin/env python3
"""
POC-14: Agent Delegation for Validation

This script implements an agent-based validation system with delegation.
Each agent specializes in specific validation tasks.

Links:
- Agent Patterns: https://lilianweng.github.io/posts/2023-06-23-agent/
- Multi-Agent Systems: https://github.com/langroid/langroid
- Delegation Best Practices: https://docs.uipath.com/agents/automation-cloud/latest/user-guide/best-practices

Sample Input:
{
    "response": {"name": "John", "age": 30, "email": "john@example.com"},
    "expected_type": "user_registration",
    "validation_level": "comprehensive"
}

Expected Output:
{
    "validation_results": {
        "structure_agent": {"valid": true, "score": 1.0},
        "content_agent": {"valid": true, "score": 0.95},
        "business_rules_agent": {"valid": true, "score": 0.9}
    },
    "overall_valid": true,
    "overall_score": 0.95,
    "delegation_path": ["orchestrator", "structure_agent", "content_agent", "business_rules_agent"]
}
"""

import asyncio
import json
import re
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


@dataclass
class ValidationResult:
    """Result from a validation agent."""
    agent_name: str
    valid: bool
    score: float
    details: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None
    processing_time_ms: Optional[float] = None


class ValidationAgent(ABC):
    """Base class for validation agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Perform validation on the data."""
        pass
    
    def can_handle(self, validation_type: str) -> bool:
        """Check if this agent can handle the validation type."""
        return True  # Override in subclasses for specific handling


class StructureValidationAgent(ValidationAgent):
    """Agent that validates data structure and schema."""
    
    def __init__(self):
        super().__init__(
            "structure_agent",
            "Validates data structure, types, and required fields"
        )
        
        # Define expected structures
        self.schemas = {
            "user_registration": {
                "required": ["name", "email"],
                "optional": ["age", "phone"],
                "types": {
                    "name": str,
                    "email": str,
                    "age": int,
                    "phone": str
                }
            },
            "api_request": {
                "required": ["method", "endpoint"],
                "optional": ["body", "headers"],
                "types": {
                    "method": str,
                    "endpoint": str,
                    "body": dict,
                    "headers": dict
                }
            },
            "product_data": {
                "required": ["id", "name", "price"],
                "optional": ["description", "category"],
                "types": {
                    "id": (int, str),
                    "name": str,
                    "price": (int, float),
                    "description": str,
                    "category": str
                }
            }
        }
    
    async def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate data structure."""
        start_time = time.time()
        errors = []
        
        expected_type = context.get("expected_type", "unknown")
        
        if not isinstance(data, dict):
            return ValidationResult(
                agent_name=self.name,
                valid=False,
                score=0.0,
                errors=["Data is not a dictionary"],
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        schema = self.schemas.get(expected_type)
        if not schema:
            # Generic validation
            return ValidationResult(
                agent_name=self.name,
                valid=True,
                score=0.5,
                details={"warning": f"No schema defined for {expected_type}"},
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Check required fields
        for field in schema["required"]:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check types
        for field, value in data.items():
            if field in schema["types"]:
                expected = schema["types"][field]
                if not isinstance(value, expected):
                    errors.append(f"Field {field} has wrong type: expected {expected}, got {type(value)}")
        
        # Calculate score
        total_fields = len(schema["required"]) + len(schema.get("optional", []))
        present_fields = len([f for f in data if f in schema["required"] or f in schema.get("optional", [])])
        score = present_fields / total_fields if total_fields > 0 else 1.0
        
        # Adjust score for errors
        if errors:
            score *= (1 - len(errors) * 0.2)
            score = max(0, score)
        
        return ValidationResult(
            agent_name=self.name,
            valid=len(errors) == 0,
            score=score,
            errors=errors if errors else None,
            processing_time_ms=(time.time() - start_time) * 1000
        )


class ContentValidationAgent(ValidationAgent):
    """Agent that validates content quality and patterns."""
    
    def __init__(self):
        super().__init__(
            "content_agent",
            "Validates content quality, formats, and patterns"
        )
        
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.phone_pattern = re.compile(r'^\+?1?\d{9,15}$')
        self.url_pattern = re.compile(r'^https?://[^\s]+$')
    
    async def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate content quality."""
        start_time = time.time()
        errors = []
        score = 1.0
        
        if not isinstance(data, dict):
            return ValidationResult(
                agent_name=self.name,
                valid=True,
                score=1.0,
                details={"skipped": "Not a dictionary"},
                processing_time_ms=(time.time() - start_time) * 1000
            )
        
        # Email validation
        if "email" in data:
            if not self.email_pattern.match(str(data["email"])):
                errors.append(f"Invalid email format: {data['email']}")
                score -= 0.3
        
        # Phone validation
        if "phone" in data:
            if not self.phone_pattern.match(str(data["phone"])):
                errors.append(f"Invalid phone format: {data['phone']}")
                score -= 0.2
        
        # URL validation (but not for API endpoints which start with /)
        for key in ["url", "website"]:
            if key in data:
                if not self.url_pattern.match(str(data[key])):
                    errors.append(f"Invalid URL format in {key}: {data[key]}")
                    score -= 0.2
        
        # String length validation
        if "name" in data:
            name = str(data["name"])
            if len(name) < 2:
                errors.append("Name too short")
                score -= 0.1
            elif len(name) > 100:
                errors.append("Name too long")
                score -= 0.1
        
        # Numeric range validation
        if "age" in data and isinstance(data["age"], (int, float)):
            if data["age"] < 0 or data["age"] > 150:
                errors.append(f"Age out of valid range: {data['age']}")
                score -= 0.2
        
        if "price" in data and isinstance(data["price"], (int, float)):
            if data["price"] < 0:
                errors.append("Price cannot be negative")
                score -= 0.3
        
        score = max(0, score)
        
        return ValidationResult(
            agent_name=self.name,
            valid=len(errors) == 0,
            score=score,
            errors=errors if errors else None,
            processing_time_ms=(time.time() - start_time) * 1000
        )


class BusinessRulesAgent(ValidationAgent):
    """Agent that validates business logic and rules."""
    
    def __init__(self):
        super().__init__(
            "business_rules_agent",
            "Validates business logic, constraints, and domain rules"
        )
    
    async def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
        """Validate business rules."""
        start_time = time.time()
        errors = []
        score = 1.0
        
        expected_type = context.get("expected_type", "unknown")
        
        if expected_type == "user_registration":
            # Check age restrictions
            if "age" in data and data["age"] < 18:
                errors.append("User must be 18 or older")
                score -= 0.5
            
            # Check email domain restrictions
            if "email" in data and data["email"].endswith("@test.com"):
                errors.append("Test email domains not allowed")
                score -= 0.3
        
        elif expected_type == "api_request":
            # Check method validity
            if "method" in data:
                valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
                if data["method"].upper() not in valid_methods:
                    errors.append(f"Invalid HTTP method: {data['method']}")
                    score -= 0.4
            
            # Check endpoint format
            if "endpoint" in data and not data["endpoint"].startswith("/"):
                errors.append("API endpoint must start with /")
                score -= 0.2
            
            # Check body requirements
            if "method" in data and data["method"].upper() == "GET" and "body" in data:
                errors.append("GET requests should not have a body")
                score -= 0.3
        
        elif expected_type == "product_data":
            # Check price constraints
            if "price" in data and data["price"] > 10000:
                errors.append("Price exceeds maximum allowed (10000)")
                score -= 0.3
            
            # Check category validity
            if "category" in data:
                valid_categories = ["electronics", "clothing", "food", "books", "other"]
                if data["category"].lower() not in valid_categories:
                    errors.append(f"Invalid category: {data['category']}")
                    score -= 0.2
        
        score = max(0, score)
        
        return ValidationResult(
            agent_name=self.name,
            valid=len(errors) == 0,
            score=score,
            errors=errors if errors else None,
            processing_time_ms=(time.time() - start_time) * 1000
        )


class ValidationOrchestrator:
    """Orchestrates validation across multiple agents."""
    
    def __init__(self, agents: List[ValidationAgent]):
        self.agents = {agent.name: agent for agent in agents}
        self.delegation_path = []
    
    async def validate(
        self,
        data: Any,
        expected_type: str,
        validation_level: str = "basic"
    ) -> Dict[str, Any]:
        """Orchestrate validation across agents."""
        self.delegation_path = ["orchestrator"]
        context = {
            "expected_type": expected_type,
            "validation_level": validation_level
        }
        
        # Determine which agents to use based on validation level
        if validation_level == "basic":
            agent_names = ["structure_agent"]
        elif validation_level == "standard":
            agent_names = ["structure_agent", "content_agent"]
        else:  # comprehensive
            agent_names = ["structure_agent", "content_agent", "business_rules_agent"]
        
        # Run validations
        results = {}
        tasks = []
        
        for agent_name in agent_names:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                self.delegation_path.append(agent_name)
                tasks.append(self._run_agent_validation(agent, data, context))
        
        # Execute validations concurrently
        validation_results = await asyncio.gather(*tasks)
        
        # Process results
        for result in validation_results:
            results[result.agent_name] = {
                "valid": result.valid,
                "score": result.score,
                "errors": result.errors,
                "processing_time_ms": result.processing_time_ms
            }
        
        # Calculate overall results
        all_valid = all(r["valid"] for r in results.values())
        avg_score = sum(r["score"] for r in results.values()) / len(results) if results else 0
        
        return {
            "validation_results": results,
            "overall_valid": all_valid,
            "overall_score": round(avg_score, 2),
            "delegation_path": self.delegation_path,
            "total_agents_used": len(results)
        }
    
    async def _run_agent_validation(
        self,
        agent: ValidationAgent,
        data: Any,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Run validation for a single agent."""
        try:
            return await agent.validate(data, context)
        except Exception as e:
            logger.error(f"Agent {agent.name} failed: {e}")
            return ValidationResult(
                agent_name=agent.name,
                valid=False,
                score=0.0,
                errors=[f"Agent error: {str(e)}"]
            )


async def test_agent_delegation():
    """Test agent delegation system."""
    # Create agents
    structure_agent = StructureValidationAgent()
    content_agent = ContentValidationAgent()
    business_agent = BusinessRulesAgent()
    
    # Create orchestrator
    orchestrator = ValidationOrchestrator([
        structure_agent,
        content_agent,
        business_agent
    ])
    
    # Test cases
    test_cases = [
        {
            "name": "Valid user registration",
            "data": {
                "name": "John Doe",
                "age": 25,
                "email": "john@example.com",
                "phone": "+1234567890"
            },
            "expected_type": "user_registration",
            "validation_level": "comprehensive",
            "expect_valid": True
        },
        {
            "name": "Invalid user (underage)",
            "data": {
                "name": "Jane Smith",
                "age": 16,
                "email": "jane@example.com"
            },
            "expected_type": "user_registration",
            "validation_level": "comprehensive",
            "expect_valid": False
        },
        {
            "name": "Valid API request",
            "data": {
                "method": "POST",
                "endpoint": "/api/users",
                "body": {"name": "Alice"}
            },
            "expected_type": "api_request",
            "validation_level": "standard",
            "expect_valid": True
        },
        {
            "name": "Invalid API request (GET with body)",
            "data": {
                "method": "GET",
                "endpoint": "/api/users",
                "body": {"filter": "active"}
            },
            "expected_type": "api_request",
            "validation_level": "comprehensive",
            "expect_valid": False
        },
        {
            "name": "Basic validation only",
            "data": {
                "name": "Test User",
                "email": "invalid-email"  # Won't be checked in basic
            },
            "expected_type": "user_registration",
            "validation_level": "basic",
            "expect_valid": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        logger.info(f"\nTesting: {test_case['name']}")
        logger.info("=" * 50)
        
        result = await orchestrator.validate(
            test_case["data"],
            test_case["expected_type"],
            test_case["validation_level"]
        )
        
        # Log results
        logger.info(f"Overall valid: {result['overall_valid']}")
        logger.info(f"Overall score: {result['overall_score']}")
        logger.info(f"Delegation path: {' → '.join(result['delegation_path'])}")
        
        for agent_name, agent_result in result["validation_results"].items():
            logger.info(f"\n{agent_name}:")
            logger.info(f"  Valid: {agent_result['valid']}")
            logger.info(f"  Score: {agent_result['score']}")
            if agent_result.get("errors"):
                logger.info(f"  Errors: {agent_result['errors']}")
        
        # Check expectation
        if result["overall_valid"] == test_case["expect_valid"]:
            logger.success(f"✅ Test passed as expected")
            results.append(True)
        else:
            logger.error(f"❌ Test failed: expected {test_case['expect_valid']}, got {result['overall_valid']}")
            results.append(False)
    
    return all(results)


async def test_concurrent_validation():
    """Test concurrent agent execution."""
    orchestrator = ValidationOrchestrator([
        StructureValidationAgent(),
        ContentValidationAgent(),
        BusinessRulesAgent()
    ])
    
    # Create multiple validation requests
    requests = []
    for i in range(5):
        requests.append({
            "data": {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "age": 20 + i
            },
            "expected_type": "user_registration",
            "validation_level": "comprehensive"
        })
    
    # Run concurrently
    start_time = time.time()
    tasks = [
        orchestrator.validate(req["data"], req["expected_type"], req["validation_level"])
        for req in requests
    ]
    
    results = await asyncio.gather(*tasks)
    elapsed = (time.time() - start_time) * 1000
    
    logger.info(f"\nConcurrent validation of {len(requests)} requests completed in {elapsed:.1f}ms")
    logger.info(f"Average time per request: {elapsed/len(requests):.1f}ms")
    
    # All should be valid
    all_valid = all(r["overall_valid"] for r in results)
    return all_valid


async def test_error_handling():
    """Test error handling in agents."""
    
    class FaultyAgent(ValidationAgent):
        """Agent that throws errors."""
        
        def __init__(self):
            super().__init__("business_rules_agent", "Agent that fails")  # Masquerade as business rules agent
        
        async def validate(self, data: Any, context: Dict[str, Any]) -> ValidationResult:
            raise ValueError("Simulated agent failure")
    
    # Replace business rules agent with faulty one
    orchestrator = ValidationOrchestrator([
        StructureValidationAgent(),
        ContentValidationAgent(),
        FaultyAgent()  # This will be called for comprehensive validation
    ])
    
    result = await orchestrator.validate(
        {"name": "Test", "email": "test@example.com"},
        "user_registration",
        "comprehensive"  # This will use all three agents
    )
    
    # Should handle the error gracefully
    faulty_result = result["validation_results"].get("business_rules_agent")
    if faulty_result and faulty_result["valid"] == False and faulty_result["errors"]:
        error_msg = faulty_result["errors"][0]
        if "Agent error" in error_msg and "Simulated agent failure" in error_msg:
            logger.success("✅ Error handling worked correctly")
            logger.info(f"  Error captured: {error_msg}")
            return True
    
    logger.error("❌ Error handling failed")
    return False


async def main():
    """Run all tests."""
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Agent delegation
    total_tests += 1
    try:
        if await test_agent_delegation():
            logger.success("✅ Agent delegation tests passed")
        else:
            all_validation_failures.append("Agent delegation tests failed")
    except Exception as e:
        all_validation_failures.append(f"Agent delegation exception: {str(e)}")
        logger.error(f"Exception in delegation test: {e}")
    
    # Test 2: Concurrent validation
    total_tests += 1
    try:
        if await test_concurrent_validation():
            logger.success("✅ Concurrent validation tests passed")
        else:
            all_validation_failures.append("Concurrent validation tests failed")
    except Exception as e:
        all_validation_failures.append(f"Concurrent validation exception: {str(e)}")
        logger.error(f"Exception in concurrent test: {e}")
    
    # Test 3: Error handling
    total_tests += 1
    try:
        if await test_error_handling():
            logger.success("✅ Error handling tests passed")
        else:
            all_validation_failures.append("Error handling tests failed")
    except Exception as e:
        all_validation_failures.append(f"Error handling exception: {str(e)}")
        logger.error(f"Exception in error handling test: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-14 Agent delegation is validated and ready")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())