#!/usr/bin/env python3
"""
Client example for polling server.

Demonstrates how to use the polling API for long-running LLM calls.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any, Optional

from loguru import logger

logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, 
          format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")


class PollingClient:
    """Client for LLM polling server."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def submit_task(
        self,
        llm_config: Dict[str, Any],
        polling_mode: bool = True,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """Submit a new LLM task."""
        response = await self.client.post(
            f"{self.base_url}/v1/tasks/submit",
            json={
                "llm_config": llm_config,
                "polling_mode": polling_mode,
                "timeout": timeout
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def get_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        response = await self.client.get(
            f"{self.base_url}/v1/tasks/{task_id}/status"
        )
        response.raise_for_status()
        return response.json()
    
    async def wait_for_task(
        self,
        task_id: str,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """Wait for task completion."""
        response = await self.client.get(
            f"{self.base_url}/v1/tasks/{task_id}/wait",
            params={"timeout": timeout}
        )
        response.raise_for_status()
        return response.json()
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task."""
        response = await self.client.post(
            f"{self.base_url}/v1/tasks/{task_id}/cancel"
        )
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close client connection."""
        await self.client.aclose()


async def demo_simple_task(client: PollingClient):
    """Demo: Simple task with polling."""
    logger.info("\n=== Demo 1: Simple Task with Polling ===")
    
    # Submit task
    config = {
        "model": "max/text-general",
        "messages": [
            {"role": "user", "content": "Write a haiku about programming"}
        ]
    }
    
    result = await client.submit_task(config)
    task_id = result["task_id"]
    logger.info(f"✅ Task submitted: {task_id}")
    
    # Poll for status
    while True:
        await asyncio.sleep(2)
        status = await client.get_status(task_id)
        logger.info(f"   Status: {status['status']}, Progress: {status['progress']}%")
        
        if status['status'] in ['completed', 'failed', 'timeout']:
            if status['status'] == 'completed':
                content = status['result']['choices'][0]['message']['content']
                logger.success(f"✅ Result:\n{content}")
            else:
                logger.error(f"❌ Task failed: {status.get('error', 'Unknown error')}")
            break


async def demo_complex_validation(client: PollingClient):
    """Demo: Complex task with validation."""
    logger.info("\n=== Demo 2: Code Generation with Validation ===")
    
    config = {
        "model": "max/code-expert",
        "messages": [
            {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
        ],
        "validation": [
            {
                "type": "agent_task",
                "params": {
                    "task_prompt_to_claude": "Analyze this code:\n\n{CODE_TO_VALIDATE}\n\n1. Is it valid Python?\n2. Does it calculate Fibonacci numbers?\n3. Is it efficient?\n\nRespond with JSON: {\"validation_passed\": true/false, \"reasoning\": \"explanation\", \"details\": \"VALID\" or \"INVALID\"}",
                    "validation_model_alias": "max/text-general",
                    "success_criteria": {"must_contain_in_details": "VALID"}
                }
            }
        ],
        "retry_config": {
            "max_attempts": 3,
            "debug_mode": True
        }
    }
    
    result = await client.submit_task(config)
    task_id = result["task_id"]
    logger.info(f"✅ Task submitted: {task_id}")
    
    # Wait for completion
    logger.info("⏳ Waiting for validation to complete...")
    final_result = await client.wait_for_task(task_id, timeout=120)
    
    if final_result['status'] == 'completed':
        content = final_result['result']['choices'][0]['message']['content']
        logger.success("✅ Generated and validated code:")
        print("\n" + "="*60)
        print(content)
        print("="*60 + "\n")
    else:
        logger.error(f"❌ Task failed: {final_result.get('error', 'Unknown error')}")


async def demo_parallel_tasks(client: PollingClient):
    """Demo: Multiple parallel tasks."""
    logger.info("\n=== Demo 3: Parallel Tasks ===")
    
    # Submit multiple tasks
    tasks = [
        {
            "model": "max/text-general",
            "messages": [{"role": "user", "content": f"Tell me fact #{i+1} about Python"}]
        }
        for i in range(3)
    ]
    
    task_ids = []
    for i, config in enumerate(tasks):
        result = await client.submit_task(config)
        task_ids.append(result["task_id"])
        logger.info(f"✅ Submitted task {i+1}: {result['task_id']}")
    
    # Wait for all to complete
    logger.info("\n⏳ Waiting for all tasks to complete...")
    
    results = await asyncio.gather(*[
        client.wait_for_task(task_id, timeout=60)
        for task_id in task_ids
    ])
    
    # Display results
    for i, result in enumerate(results):
        if result['status'] == 'completed':
            content = result['result']['choices'][0]['message']['content']
            logger.success(f"\n✅ Task {i+1} result:\n{content}")
        else:
            logger.error(f"\n❌ Task {i+1} failed: {result.get('error', 'Unknown error')}")


async def demo_task_cancellation(client: PollingClient):
    """Demo: Task cancellation."""
    logger.info("\n=== Demo 4: Task Cancellation ===")
    
    # Submit a long-running task
    config = {
        "model": "max/text-general",
        "messages": [
            {"role": "user", "content": "Write a very detailed 1000-word essay about artificial intelligence"}
        ]
    }
    
    result = await client.submit_task(config)
    task_id = result["task_id"]
    logger.info(f"✅ Task submitted: {task_id}")
    
    # Wait a bit then cancel
    await asyncio.sleep(3)
    logger.info("🛑 Cancelling task...")
    
    cancel_result = await client.cancel_task(task_id)
    logger.info(f"   Result: {cancel_result['message']}")
    
    # Check final status
    status = await client.get_status(task_id)
    logger.info(f"   Final status: {status['status']}")


async def main():
    """Run all demos."""
    client = PollingClient()
    
    try:
        # Check health
        health = await client.health_check()
        logger.info(f"Server health: {health['status']}")
        
        if health['proxy'] != 'ok':
            logger.warning("⚠️  Claude proxy not running - some tests may fail")
        
        # Run demos
        await demo_simple_task(client)
        await asyncio.sleep(2)
        
        await demo_complex_validation(client)
        await asyncio.sleep(2)
        
        await demo_parallel_tasks(client)
        await asyncio.sleep(2)
        
        await demo_task_cancellation(client)
        
        logger.success("\n✅ All demos completed!")
        
    except httpx.ConnectError:
        logger.error("❌ Cannot connect to polling server!")
        logger.info("Start it with: python src/llm_call/proof_of_concept/polling_server.py")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
    finally:
        await client.close()


if __name__ == "__main__":
    logger.info("LLM Polling Client Demo")
    logger.info("=" * 60)
    asyncio.run(main())