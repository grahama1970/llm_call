#!/usr/bin/env python3
"""
Test working models to demonstrate V4 validation functionality.
"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
from rich.console import Console
from rich.table import Table

# Import v4 client
from llm_call.proof_of_concept.litellm_client_poc import llm_call

console = Console()

# Configure logger
logger.remove()
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")


async def test_openai_text():
    """Test OpenAI text generation."""
    logger.info("Testing OpenAI text generation...")
    result = await llm_call({
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "What is the capital of France? Answer in one word."}],
        "max_tokens": 10
    })
    return {
        "test": "OpenAI Text",
        "status": "✅ PASSED" if result else "❌ FAILED",
        "response": result['choices'][0]['message']['content'] if result else None
    }


async def test_openai_json():
    """Test OpenAI JSON generation with validation."""
    logger.info("Testing OpenAI JSON generation with validation...")
    result = await llm_call({
        "model": "openai/gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": "Generate a JSON object for a book with title, author, and year_published fields. Use 'The Great Gatsby' as an example."
        }],
        "response_format": {"type": "json_object"},
        "validation": [
            {"type": "response_not_empty"},
            {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "title"}},
            {"type": "field_present", "params": {"field_name": "author"}},
            {"type": "field_present", "params": {"field_name": "year_published"}}
        ]
    })
    
    if result:
        try:
            parsed = json.loads(result['choices'][0]['message']['content'])
            return {
                "test": "OpenAI JSON Validation",
                "status": "✅ PASSED",
                "response": parsed
            }
        except:
            return {
                "test": "OpenAI JSON Validation",
                "status": "❌ FAILED",
                "response": "Invalid JSON"
            }
    else:
        return {
            "test": "OpenAI JSON Validation",
            "status": "❌ FAILED",
            "response": None
        }


async def test_max_proxy():
    """Test max/* model through proxy."""
    logger.info("Testing max/* model through proxy...")
    result = await llm_call({
        "model": "max/text-general",
        "messages": [{"role": "user", "content": "Count from 1 to 5"}],
        "max_tokens": 50
    })
    return {
        "test": "Max Proxy Model",
        "status": "✅ PASSED" if result else "❌ FAILED",
        "response": result['choices'][0]['message']['content'] if result else None
    }


async def test_multimodal():
    """Test multimodal with local image."""
    logger.info("Testing multimodal image processing...")
    
    # Check if test image exists
    image_path = Path(__file__).parent / "test_images_poc" / "six_animals.png"
    if not image_path.exists():
        return {
            "test": "Multimodal Image",
            "status": "⏭️ SKIPPED",
            "response": "Test image not found"
        }
    
    result = await llm_call({
        "model": "openai/gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "How many animals are in this image?"},
                {"type": "image_url", "image_url": {"url": str(image_path)}}
            ]
        }],
        "max_tokens": 50,
        "image_directory": str(image_path.parent)
    })
    
    return {
        "test": "Multimodal Image",
        "status": "✅ PASSED" if result else "❌ FAILED",
        "response": result['choices'][0]['message']['content'] if result else None
    }


async def main():
    """Run all tests."""
    console.print("\n[bold cyan]V4 Validation Test Suite[/bold cyan]")
    console.print("Testing working models to demonstrate functionality\n")
    
    # Run tests
    tests = [
        test_openai_text(),
        test_openai_json(),
        test_max_proxy(),
        test_multimodal()
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Create results table
    table = Table(title="Test Results", show_lines=True)
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Response", style="green", max_width=60)
    
    passed = 0
    failed = 0
    
    for result in results:
        if isinstance(result, Exception):
            table.add_row(
                "Error",
                "❌ FAILED",
                str(result)[:60]
            )
            failed += 1
        else:
            table.add_row(
                result["test"],
                result["status"],
                str(result["response"])[:60] + "..." if len(str(result["response"])) > 60 else str(result["response"])
            )
            if "✅" in result["status"]:
                passed += 1
            elif "❌" in result["status"]:
                failed += 1
    
    console.print(table)
    
    # Summary
    total = passed + failed
    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"✅ Passed: {passed}/{total}")
    console.print(f"❌ Failed: {failed}/{total}")
    console.print(f"Success Rate: {passed/total*100:.1f}%" if total > 0 else "N/A")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path(__file__).parent / f"working_models_test_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": passed,
                "failed": failed,
                "total": total
            },
            "results": [r if not isinstance(r, Exception) else {"error": str(r)} for r in results]
        }, f, indent=2)
    
    console.print(f"\nDetailed results saved to: {output_file}")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)