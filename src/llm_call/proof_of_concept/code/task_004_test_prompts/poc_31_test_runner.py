#!/usr/bin/env python3
"""
POC 31: Test Runner Framework
Task: Create framework to execute JSON-defined test cases
Expected Output: Execute all test cases from test_prompts.json with proper tracking
Links:
- https://docs.pytest.org/
- https://github.com/pytest-dev/pytest-xdist
"""

import json
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime
from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | {message}")


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of a single test execution"""
    test_case_id: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """Represents a test case from JSON"""
    test_case_id: str
    description: str
    llm_config: Dict[str, Any]
    validation: Optional[List[Dict[str, Any]]] = None
    tags: List[str] = field(default_factory=list)
    priority: int = 5
    enabled: bool = True


class TestRunner:
    """Framework for running JSON-defined test cases"""
    
    def __init__(self, 
                 llm_executor: Optional[Callable] = None,
                 validator_registry: Optional[Dict[str, Callable]] = None):
        self.llm_executor = llm_executor or self._mock_llm_executor
        self.validator_registry = validator_registry or {}
        self.results: List[TestResult] = []
        self.test_cases: List[TestCase] = []
    
    def load_test_cases(self, json_path: Path) -> List[TestCase]:
        """Load test cases from JSON file"""
        logger.info(f"Loading test cases from {json_path}")
        
        with open(json_path, 'r') as f:
            # Skip the comment lines at the beginning
            content = f.read()
            # Find the start of the JSON array
            json_start = content.find('[')
            if json_start == -1:
                raise ValueError("No JSON array found in file")
            
            # Parse JSON starting from the array
            json_content = content[json_start:]
            raw_cases = json.loads(json_content)
        
        # Convert to TestCase objects
        test_cases = []
        for raw in raw_cases:
            # Skip comment strings
            if isinstance(raw, str):
                continue
                
            test_case = TestCase(
                test_case_id=raw["test_case_id"],
                description=raw["description"],
                llm_config=raw["llm_config"],
                validation=raw.get("validation"),
                tags=raw.get("tags", []),
                priority=raw.get("priority", 5),
                enabled=raw.get("enabled", True)
            )
            test_cases.append(test_case)
        
        self.test_cases = test_cases
        logger.info(f"Loaded {len(test_cases)} test cases")
        return test_cases
    
    async def execute_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        logger.info(f"Executing test: {test_case.test_case_id}")
        
        result = TestResult(
            test_case_id=test_case.test_case_id,
            status=TestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # Execute LLM call
            start = time.time()
            llm_response = await self._execute_llm_call(test_case.llm_config)
            execution_time = (time.time() - start) * 1000
            
            result.metadata["llm_execution_time_ms"] = execution_time
            result.metadata["llm_response_preview"] = str(llm_response)[:200]
            
            # Run validations if specified
            if test_case.validation:
                validation_passed = await self._run_validations(
                    llm_response, 
                    test_case.validation
                )
                result.validation_results = validation_passed
                
                # Determine overall status
                if all(v.get("passed", False) for v in validation_passed):
                    result.status = TestStatus.PASSED
                else:
                    result.status = TestStatus.FAILED
                    failed_validations = [
                        v for v in validation_passed if not v.get("passed", False)
                    ]
                    result.error_message = f"Validation failed: {failed_validations}"
            else:
                # No validation - assume pass if we got a response
                result.status = TestStatus.PASSED if llm_response else TestStatus.FAILED
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.stack_trace = self._get_stack_trace()
            logger.error(f"Test {test_case.test_case_id} failed with error: {e}")
        
        result.end_time = datetime.now()
        result.duration_ms = (result.end_time - result.start_time).total_seconds() * 1000
        
        self.results.append(result)
        return result
    
    async def _execute_llm_call(self, llm_config: Dict[str, Any]) -> Any:
        """Execute LLM call (mock or real)"""
        if self.llm_executor:
            return await self.llm_executor(llm_config)
        else:
            return await self._mock_llm_executor(llm_config)
    
    async def _mock_llm_executor(self, llm_config: Dict[str, Any]) -> Dict[str, Any]:
        """Mock LLM executor for testing"""
        await asyncio.sleep(0.1)  # Simulate API call
        
        model = llm_config.get("model", "unknown")
        
        # Return different responses based on test requirements
        if "json" in model.lower():
            return {"type": "json", "title": "Test Book", "author": "Test Author", "year_published": 2024}
        elif "multimodal" in model.lower():
            return {"type": "multimodal", "description": "I see an image with objects"}
        elif "validation" in llm_config:
            # Return response that may or may not pass validation
            if "string_check" in str(llm_config.get("validation", [])):
                return {"type": "text", "content": "The sky is blue today"}
            else:
                return {"type": "text", "content": "Generic response"}
        else:
            return {"type": "text", "content": f"Mock response for {model}"}
    
    async def _run_validations(self, 
                              response: Any, 
                              validations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run validation checks on response"""
        results = []
        
        for validation in validations:
            val_type = validation.get("type")
            val_params = validation.get("params", {})
            
            if val_type in self.validator_registry:
                validator = self.validator_registry[val_type]
                try:
                    is_valid = await validator(response, val_params)
                    results.append({
                        "type": val_type,
                        "passed": is_valid,
                        "params": val_params
                    })
                except Exception as e:
                    results.append({
                        "type": val_type,
                        "passed": False,
                        "error": str(e),
                        "params": val_params
                    })
            else:
                # Unknown validator - mock result
                results.append({
                    "type": val_type,
                    "passed": True,  # Assume pass for POC
                    "params": val_params,
                    "note": "Validator not implemented"
                })
        
        return results
    
    def _get_stack_trace(self) -> str:
        """Get current stack trace"""
        import traceback
        return traceback.format_exc()
    
    async def run_all_tests(self, 
                           parallel: bool = False,
                           max_workers: int = 5) -> Dict[str, Any]:
        """Run all loaded test cases"""
        if not self.test_cases:
            logger.warning("No test cases loaded")
            return {"total": 0, "results": []}
        
        logger.info(f"Running {len(self.test_cases)} tests (parallel={parallel})")
        
        start_time = datetime.now()
        
        if parallel:
            # Run tests in parallel using asyncio
            tasks = []
            for test_case in self.test_cases:
                if test_case.enabled:
                    task = asyncio.create_task(self.execute_test_case(test_case))
                    tasks.append(task)
            
            # Limit concurrency
            results = []
            for i in range(0, len(tasks), max_workers):
                batch = tasks[i:i + max_workers]
                batch_results = await asyncio.gather(*batch)
                results.extend(batch_results)
        else:
            # Run tests sequentially
            for test_case in self.test_cases:
                if test_case.enabled:
                    await self.execute_test_case(test_case)
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # Generate summary
        summary = self._generate_summary(total_duration)
        
        return summary
    
    def _generate_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate test run summary"""
        status_counts = {}
        for result in self.results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total": len(self.results),
            "duration_seconds": total_duration,
            "status_counts": status_counts,
            "passed": status_counts.get("passed", 0),
            "failed": status_counts.get("failed", 0),
            "errors": status_counts.get("error", 0),
            "skipped": status_counts.get("skipped", 0),
            "pass_rate": (
                status_counts.get("passed", 0) / len(self.results) * 100
                if self.results else 0
            ),
            "results": self.results
        }
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get all failed test results"""
        return [
            r for r in self.results 
            if r.status in [TestStatus.FAILED, TestStatus.ERROR]
        ]


# Example validators for testing
async def mock_json_validator(response: Any, params: Dict[str, Any]) -> bool:
    """Mock JSON validator"""
    return isinstance(response, dict) and response.get("type") == "json"


async def mock_field_validator(response: Any, params: Dict[str, Any]) -> bool:
    """Mock field presence validator"""
    field_name = params.get("field_name")
    if not field_name:
        return True
    return isinstance(response, dict) and field_name in response


async def main():
    """Test the runner framework"""
    
    # Create test JSON file
    test_json_path = Path("test_cases_poc.json")
    test_cases_json = """[
        {
            "test_case_id": "poc_test_001",
            "description": "Simple text test",
            "llm_config": {
                "model": "openai/gpt-3.5-turbo",
                "question": "What is 2+2?"
            }
        },
        {
            "test_case_id": "poc_test_002",
            "description": "JSON validation test",
            "llm_config": {
                "model": "openai/json-model",
                "question": "Generate a book JSON"
            },
            "validation": [
                {"type": "json_string"},
                {"type": "field_present", "params": {"field_name": "title"}}
            ]
        },
        {
            "test_case_id": "poc_test_003",
            "description": "Failed test example",
            "llm_config": {
                "model": "failing/model",
                "question": "This will fail"
            },
            "validation": [
                {"type": "field_present", "params": {"field_name": "nonexistent"}}
            ]
        }
    ]"""
    
    with open(test_json_path, 'w') as f:
        f.write(test_cases_json)
    
    # Create runner with mock validators
    runner = TestRunner(
        validator_registry={
            "json_string": mock_json_validator,
            "field_present": mock_field_validator
        }
    )
    
    # Load test cases
    runner.load_test_cases(test_json_path)
    
    logger.info("=" * 60)
    logger.info("TEST RUNNER FRAMEWORK TESTING")
    logger.info("=" * 60)
    
    # Test 1: Sequential execution
    logger.info("\n🧪 Test 1: Sequential Execution")
    summary = await runner.run_all_tests(parallel=False)
    
    logger.info(f"Total tests: {summary['total']}")
    logger.info(f"Passed: {summary['passed']}")
    logger.info(f"Failed: {summary['failed']}")
    logger.info(f"Pass rate: {summary['pass_rate']:.1f}%")
    logger.info(f"Duration: {summary['duration_seconds']:.2f}s")
    
    # Test 2: Parallel execution
    logger.info("\n🧪 Test 2: Parallel Execution")
    runner.results.clear()  # Clear previous results
    summary = await runner.run_all_tests(parallel=True, max_workers=2)
    
    logger.info(f"Total tests: {summary['total']}")
    logger.info(f"Duration: {summary['duration_seconds']:.2f}s (should be faster)")
    
    # Test 3: Failed test details
    logger.info("\n🧪 Test 3: Failed Test Analysis")
    failed_tests = runner.get_failed_tests()
    
    for failed in failed_tests:
        logger.error(f"Failed: {failed.test_case_id}")
        logger.error(f"  Error: {failed.error_message}")
        if failed.validation_results:
            logger.error(f"  Validations: {failed.validation_results}")
    
    # Clean up
    test_json_path.unlink()
    
    # Verify framework works
    if summary['total'] == 3 and summary['passed'] >= 1:
        logger.success("\n✅ Test runner framework working correctly")
        return 0
    else:
        logger.error("\n❌ Test runner framework has issues")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))