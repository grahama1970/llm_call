"""
Final test to verify Claude proxy with async SQLite polling is working.
This is a simplified test that focuses on the core functionality.
"""

import asyncio
import httpx
import json
import time
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), level="INFO")

# Test configuration
PROXY_URL = "http://127.0.0.1:3010"
POLLING_DB_PATH = Path(__file__).parent.parent.parent.parent / "logs" / "llm_polling_tasks.db"

async def test_polling_functionality():
    """Test the complete polling functionality with Claude proxy."""
    logger.info("\n🚀 Testing Claude Proxy with Async SQLite Polling\n")
    
    async with httpx.AsyncClient() as client:
        # 1. Test polling mode - returns task_id immediately
        logger.info("1️⃣ Test: Submit task in polling mode")
        
        response = await client.post(
            f"{PROXY_URL}/v1/chat/completions",
            json={
                "model": "max/text-general",
                "messages": [{"role": "user", "content": "What is 2+2? Reply with just the number."}],
                "polling_mode": True,
                "max_tokens": 10
            },
            timeout=10.0
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["status"] == "pending"
        
        task_id = data["task_id"]
        logger.info(f"✅ Got task_id: {task_id}")
        
        # 2. Check status updates via polling
        logger.info("\n2️⃣ Test: Check task status via polling")
        
        statuses = []
        for i in range(10):  # Check for up to 20 seconds
            status_response = await client.get(
                f"{PROXY_URL}/v1/polling/status/{task_id}"
            )
            
            assert status_response.status_code == 200
            status_data = status_response.json()
            
            status = status_data["status"]
            statuses.append(status)
            logger.info(f"   Status check {i+1}: {status}")
            
            if status == "completed":
                assert "result" in status_data
                result = status_data["result"]
                content = result["choices"][0]["message"]["content"]
                logger.info(f"✅ Task completed! Response: {content}")
                assert "4" in content
                break
                
            await asyncio.sleep(2)
        
        # Should have transitioned through statuses
        assert "completed" in statuses
        
        # 3. Test sync mode - waits for completion
        logger.info("\n3️⃣ Test: Submit task in sync mode (waits for completion)")
        
        start_time = time.time()
        response = await client.post(
            f"{PROXY_URL}/v1/chat/completions",
            json={
                "model": "max/text-general",
                "messages": [{"role": "user", "content": "Say 'Hello async world' exactly"}],
                "polling_mode": False,  # Sync mode
                "max_tokens": 50
            },
            timeout=70.0
        )
        
        elapsed = time.time() - start_time
        assert response.status_code == 200
        data = response.json()
        
        # Should get the result directly, not a task_id
        assert "choices" in data
        content = data["choices"][0]["message"]["content"]
        logger.info(f"✅ Got direct response in {elapsed:.1f}s: {content}")
        assert "Hello async world" in content
        
        # 4. Test active tasks endpoint
        logger.info("\n4️⃣ Test: Check active tasks")
        
        active_response = await client.get(f"{PROXY_URL}/v1/polling/active")
        assert active_response.status_code == 200
        active_data = active_response.json()
        
        logger.info(f"✅ Active tasks: {active_data['count']}")
        
        # 5. Verify SQLite persistence
        logger.info("\n5️⃣ Test: Verify SQLite persistence")
        
        import sqlite3
        conn = sqlite3.connect(str(POLLING_DB_PATH))
        cursor = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE task_id = ?",
            (task_id,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
        logger.info(f"✅ Task persisted in SQLite database")
        
        logger.info("\n🎉 All tests passed! Claude proxy with async SQLite polling is working correctly.")
        logger.info("\nKey features verified:")
        logger.info("  ✅ Polling mode returns task_id immediately")
        logger.info("  ✅ Status can be checked via /v1/polling/status/{task_id}")
        logger.info("  ✅ Tasks complete and results are retrievable")
        logger.info("  ✅ Sync mode waits for completion")
        logger.info("  ✅ Tasks are persisted in SQLite database")
        logger.info("  ✅ Active tasks can be monitored")

if __name__ == "__main__":
    # Check if proxy is running
    async def check_and_run():
        try:
            async with httpx.AsyncClient() as client:
                health = await client.get(f"{PROXY_URL}/health", timeout=2.0)
                assert health.status_code == 200
                logger.info("✅ Claude proxy server is running")
        except:
            logger.error("❌ Claude proxy server is not running!")
            logger.error("   Please ensure the server is running:")
            logger.error("   python src/llm_call/proof_of_concept/poc_claude_proxy_with_polling.py")
            return
        
        # Run the test
        await test_polling_functionality()
    
    asyncio.run(check_and_run())