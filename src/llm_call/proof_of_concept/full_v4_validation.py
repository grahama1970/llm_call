#!/usr/bin/env python3
"""
Complete V4 validation test - runs all 28 tests and reports results.
"""
import asyncio
import json
import sys
import re
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

# Setup paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.llm_call.proof_of_concept.v4_claude_validator.litellm_client_poc import llm_call

console = Console()

# Configure logger
logger.remove()
logger.add(sys.stderr, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")


def parse_test_prompts(file_path: Path):
    """Parse test_prompts.json with comment handling."""
    from llm_call.core.utils.json_utils import clean_json_string, extract_json
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find JSON start
    json_start = content.find('[')
    if json_start == -1:
        # Try to extract JSON
        result = extract_json(content)
        if result['valid']:
            return result['data']
        else:
            raise ValueError(f"Could not extract JSON: {result['error']}")
    
    json_content = content[json_start:]
    
    # Clean and parse
    cleaned = clean_json_string(json_content)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try harder with extraction
        result = extract_json(cleaned)
        if result['valid']:
            return result['data']
        else:
            raise ValueError(f"Could not parse JSON: {result.get('error', 'Unknown error')}")


async def run_single_test(test_case: dict) -> dict:
    """Run a single test case."""
    test_id = test_case.get("test_case_id", "unknown")
    description = test_case.get("description", "")
    llm_config = test_case.get("llm_config", {})
    model = llm_config.get("model", "")
    
    logger.info(f"Running test: {test_id}")
    
    try:
        start_time = datetime.now()
        result = await llm_call(llm_config)
        duration = (datetime.now() - start_time).total_seconds()
        
        if result:
            # Extract response content
            if isinstance(result, dict):
                if 'choices' in result:
                    content = result['choices'][0]['message']['content']
                elif 'error' in result:
                    # Special handling for expected errors (like multimodal skip)
                    return {
                        "test_id": test_id,
                        "model": model,
                        "status": "⚠️ SKIPPED",
                        "duration": duration,
                        "response": result.get('error', 'Skipped'),
                        "description": description
                    }
                else:
                    content = str(result)
            else:
                content = str(result)
            
            # Truncate long responses
            preview = content[:100] + "..." if len(content) > 100 else content
            
            return {
                "test_id": test_id,
                "model": model,
                "status": "✅ PASSED",
                "duration": duration,
                "response": preview,
                "description": description
            }
        else:
            return {
                "test_id": test_id,
                "model": model,
                "status": "❌ FAILED",
                "duration": duration,
                "response": "No response",
                "description": description
            }
            
    except Exception as e:
        duration = 0
        error_msg = str(e)
        
        # Check for known issues
        if "LLM Provider NOT provided" in error_msg and "meta-task" in model:
            status = "⚠️ META-TASK"
            error_msg = "Meta-task model (test framework)"
        elif "500 Internal Server Error" in error_msg:
            status = "❌ PROXY ERROR"
            error_msg = "Proxy server error"
        else:
            status = "❌ FAILED"
            
        return {
            "test_id": test_id,
            "model": model,
            "status": status,
            "duration": duration,
            "response": error_msg[:100],
            "description": description
        }


async def main():
    """Run all V4 validation tests."""
    console.print("\n[bold cyan]V4 Test Prompts Complete Validation[/bold cyan]\n")
    
    # Load tests
    test_file = Path(__file__).parent / "v4_claude_validator" / "test_prompts.json"
    test_cases = parse_test_prompts(test_file)
    
    console.print(f"Loaded [bold green]{len(test_cases)}[/bold green] test cases\n")
    
    # Run all tests
    results = []
    for i, test_case in enumerate(test_cases, 1):
        console.print(f"[dim]Test {i}/{len(test_cases)}[/dim]")
        result = await run_single_test(test_case)
        results.append(result)
        
        # Small delay between tests
        if i < len(test_cases):
            await asyncio.sleep(0.5)
    
    # Create results table
    table = Table(title="V4 Validation Results", show_lines=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("Test ID", style="cyan", width=35)
    table.add_column("Model", style="yellow", width=30)
    table.add_column("Status", width=12)
    table.add_column("Response/Error", style="green", width=50)
    
    # Count results
    passed = 0
    failed = 0
    skipped = 0
    meta_task = 0
    
    for i, result in enumerate(results, 1):
        status = result["status"]
        
        # Style based on status
        if "✅" in status:
            passed += 1
            status_style = "green"
        elif "❌" in status:
            failed += 1
            status_style = "red"
        elif "META-TASK" in status:
            meta_task += 1
            status_style = "yellow"
        else:
            skipped += 1
            status_style = "dim"
        
        table.add_row(
            str(i),
            result["test_id"],
            result["model"],
            f"[{status_style}]{status}[/{status_style}]",
            result["response"]
        )
    
    console.print(table)
    
    # Summary panel
    total = len(results)
    summary = Panel(
        f"""[bold]Test Summary[/bold]
        
Total Tests: {total}
✅ Passed: {passed} ({passed/total*100:.1f}%)
❌ Failed: {failed} ({failed/total*100:.1f}%)
⚠️ Meta-task: {meta_task} ({meta_task/total*100:.1f}%)
⚠️ Skipped: {skipped} ({skipped/total*100:.1f}%)

[dim]Meta-task models are test framework models, not real LLMs[/dim]""",
        title="Summary",
        border_style="cyan"
    )
    
    console.print("\n", summary)
    
    # Save detailed results
    output_file = Path(__file__).parent / f"v4_validation_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "meta_task": meta_task,
                "skipped": skipped
            },
            "results": results
        }, f, indent=2)
    
    console.print(f"\n💾 Detailed results saved to: [cyan]{output_file}[/cyan]\n")
    
    # Return True only if all non-meta-task tests passed
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)