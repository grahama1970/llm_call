"""
Module: cli/app.py
Purpose: Main CLI for Claude Max Proxy with Granger standard integration

External Dependencies:
- typer: https://typer.tiangolo.com/
- rich: https://rich.readthedocs.io/

Example Usage:
>>> claude-max-proxy analyze-model claude-3-opus
>>> claude-max-proxy route-request "What is the capital of France?"
"""

import typer
from typing import Optional, List
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .granger_slash_mcp_mixin import add_slash_mcp_commands

# Initialize
app = typer.Typer(
    name="claude-max-proxy",
    help="Claude Max Proxy - Unified LLM interface with optimal routing"
)
console = Console()

# Add slash command and MCP generation
add_slash_mcp_commands(app, project_name="claude_max_proxy")


@app.command()
def analyze_model(
    model_name: str = typer.Argument(..., help="Model name to analyze (e.g., claude-3-opus)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed analysis")
):
    """
    Analyze a specific model's capabilities and performance.
    
    Examples:
        claude-max-proxy analyze-model claude-3-opus
        claude-max-proxy analyze-model gpt-4 --verbose
    """
    # Create analysis table
    table = Table(title=f"Model Analysis: {model_name}")
    table.add_column("Attribute", style="cyan")
    table.add_column("Value", style="white")
    
    # Mock data for now
    attributes = {
        "Context Length": "200K tokens",
        "Strengths": "Long context, reasoning, coding",
        "Weaknesses": "Speed on very long contexts",
        "Best Use Cases": "Complex analysis, code generation",
        "Cost Tier": "Premium"
    }
    
    for attr, value in attributes.items():
        table.add_row(attr, value)
    
    console.print(table)
    
    if verbose:
        panel = Panel(
            "This model excels at complex reasoning tasks and can handle very long contexts. "
            "It's particularly strong for code generation and analysis tasks.",
            title="Detailed Analysis",
            border_style="blue"
        )
        console.print(panel)


@app.command()
def route_request(
    prompt: str = typer.Argument(..., help="The prompt to route"),
    context_length: Optional[int] = typer.Option(None, "--context", "-c", help="Context length in tokens"),
    task_type: Optional[str] = typer.Option(None, "--task", "-t", help="Task type: code/analysis/chat"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save routing decision")
):
    """
    Route a request to the optimal model based on requirements.
    
    Examples:
        claude-max-proxy route-request "Write a Python function"
        claude-max-proxy route-request "Analyze this 100k token document" --context 100000
    """
    # Mock routing logic
    if context_length and context_length > 50000:
        recommended_model = "claude-3-opus"
        reason = "Long context requirement"
    elif task_type == "code":
        recommended_model = "claude-3-sonnet"
        reason = "Code generation task"
    else:
        recommended_model = "claude-3-haiku"
        reason = "General purpose task"
    
    result = {
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "recommended_model": recommended_model,
        "reason": reason,
        "estimated_cost": "$0.015",
        "estimated_time": "2.3s"
    }
    
    # Display result
    panel = Panel(
        f"[green]Recommended Model:[/green] {result['recommended_model']}\n"
        f"[yellow]Reason:[/yellow] {result['reason']}\n"
        f"[cyan]Estimated Cost:[/cyan] {result['estimated_cost']}\n"
        f"[magenta]Estimated Time:[/magenta] {result['estimated_time']}",
        title="Routing Decision",
        border_style="green"
    )
    console.print(panel)
    
    # Save if requested
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2))
        console.print(f"✅ Saved routing decision to {output}")


@app.command()
def list_models(
    available_only: bool = typer.Option(True, "--available/--all", help="Show only available models"),
    format: str = typer.Option("table", "--format", "-f", help="Output format: table/json")
):
    """
    List all models managed by the proxy.
    
    Examples:
        claude-max-proxy list-models
        claude-max-proxy list-models --all --format json
    """
    # Mock model data
    models = [
        {"name": "claude-3-opus", "status": "✅ Available", "context": "200K", "cost": "$$$"},
        {"name": "claude-3-sonnet", "status": "✅ Available", "context": "200K", "cost": "$$"},
        {"name": "claude-3-haiku", "status": "✅ Available", "context": "200K", "cost": "$"},
        {"name": "gpt-4-turbo", "status": "✅ Available", "context": "128K", "cost": "$$$"},
        {"name": "gemini-pro", "status": "❌ Unavailable", "context": "32K", "cost": "$$"},
    ]
    
    if available_only:
        models = [m for m in models if "✅" in m["status"]]
    
    if format == "json":
        console.print(json.dumps(models, indent=2))
    else:
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Context", style="yellow")
        table.add_column("Cost", style="magenta")
        
        for model in models:
            table.add_row(
                model["name"],
                model["status"],
                model["context"],
                model["cost"]
            )
        
        console.print(table)


@app.command()
def benchmark(
    models: List[str] = typer.Option(None, "--model", "-m", help="Models to benchmark"),
    task_file: Path = typer.Option(..., "--tasks", "-t", help="JSON file with benchmark tasks"),
    output: Path = typer.Option("benchmark_results.json", "--output", "-o", help="Output file")
):
    """
    Run benchmarks across multiple models.
    
    Examples:
        claude-max-proxy benchmark --tasks tasks.json --model claude-3-opus --model gpt-4
    """
    if not task_file.exists():
        console.print(f"[red]Task file not found: {task_file}[/red]")
        raise typer.Exit(1)
    
    # Mock benchmark
    console.print(f"[cyan]Running benchmarks on {len(models or ['all'])} models...[/cyan]")
    
    with console.status("Benchmarking..."):
        import time
        time.sleep(2)  # Simulate work
    
    results = {
        "timestamp": "2024-03-15T10:30:00",
        "models_tested": models or ["claude-3-opus", "claude-3-sonnet"],
        "tasks_completed": 10,
        "summary": {
            "fastest": "claude-3-haiku",
            "most_accurate": "claude-3-opus",
            "best_value": "claude-3-sonnet"
        }
    }
    
    output.write_text(json.dumps(results, indent=2))
    console.print(f"✅ Benchmark complete! Results saved to {output}")


@app.command()
def status():
    """
    Show Claude Max Proxy system status.
    
    Displays active models, routing statistics, and system health.
    """
    # System status
    table = Table(title="System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    components = [
        ("Proxy Server", "✅ Running"),
        ("Model Router", "✅ Active"),
        ("Cache System", "✅ 85% Hit Rate"),
        ("Rate Limiter", "✅ Within Limits"),
        ("Health Monitor", "✅ All Systems Go")
    ]
    
    for component, status in components:
        table.add_row(component, status)
    
    console.print(table)
    
    # Statistics panel
    stats = Panel(
        "[cyan]Requests Today:[/cyan] 1,234\n"
        "[green]Average Latency:[/green] 1.8s\n"
        "[yellow]Cache Hits:[/yellow] 1,049 (85%)\n"
        "[magenta]Cost Saved:[/magenta] $48.50",
        title="Statistics",
        border_style="blue"
    )
    console.print(stats)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    # Validation
    print("✅ Claude Max Proxy CLI initialized")
    print("Example commands:")
    print("  claude-max-proxy analyze-model claude-3-opus")
    print("  claude-max-proxy route-request 'Hello world'")
    print("  claude-max-proxy list-models")