#!/usr/bin/env python3
"""
Module: verify_tests.py
Description: Simple CLI tool for verifying test outputs from Claude Code

External Dependencies:
- typer: https://typer.tiangolo.com/

Sample Input:
>>> # From command line:
>>> python verify_tests.py "pytest tests/"

Expected Output:
>>> TEST VERIFICATION SUMMARY
>>> ========================
>>> Total: 10 tests
>>> Passed: 7
>>> Failed: 3
>>> Success Rate: 70.0%

Example Usage:
>>> # Verify pytest output
>>> python verify_tests.py "pytest tests/" --method gemini
>>> 
>>> # Verify raw output file
>>> python verify_tests.py --file test_output.txt
>>> 
>>> # Quick pattern matching only
>>> python verify_tests.py "pytest" --quick
"""

import typer
from pathlib import Path
from typing import Optional
import json
import sys

from verification_workflow import run_and_verify, verify_claude_output
from simple_verifier import verify_simple, verify_with_gemini

app = typer.Typer()


@app.command()
def verify(
    command: Optional[str] = typer.Argument(None, help="Test command to run"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Verify output from file"),
    method: str = typer.Option("auto", "--method", "-m", help="Verification method: auto, gemini, simple"),
    quick: bool = typer.Option(False, "--quick", "-q", help="Quick verification (pattern matching only)"),
    claude: bool = typer.Option(False, "--claude", "-c", help="Verify Claude Code output specifically")
):
    """Verify test outputs with external validation"""
    
    if file:
        # Read output from file
        if not file.exists():
            typer.echo(f"Error: File {file} not found", err=True)
            raise typer.Exit(1)
        
        output = file.read_text()
        
        if claude:
            # Special handling for Claude output
            results = verify_claude_output(output)
            
            typer.echo("\n" + "="*60)
            typer.echo("CLAUDE OUTPUT VERIFICATION")
            typer.echo("="*60)
            
            if results['claude_claims']:
                typer.echo("⚠️  Claude claims detected:")
                for claim in results['claude_claims']:
                    typer.echo(f"  - {claim}")
            
            if 'error' not in results['actual_results']:
                typer.echo(f"\nActual results found:")
                typer.echo(f"  - Passed: {results['actual_results']['passed']}")
                typer.echo(f"  - Failed: {results['actual_results']['failed']}")
                typer.echo(f"  - Total: {results['actual_results']['total']}")
            else:
                typer.echo(f"\n❌ {results['actual_results']['error']}")
            
            if results['likely_hallucination']:
                typer.echo("\n🚨 LIKELY HALLUCINATION DETECTED!")
                typer.echo("Claude claims success but tests are failing.")
            
            typer.echo("="*60 + "\n")
            
        else:
            # Regular output verification
            if quick or method == "simple":
                results = verify_simple(output)
            elif method == "gemini":
                results = verify_with_gemini(output)
            else:
                # Auto mode - try Gemini first, fall back to simple
                try:
                    results = verify_with_gemini(output)
                except:
                    results = verify_simple(output)
            
            display_results(results)
    
    elif command:
        # Run command and verify
        use_gemini = method != "simple" and not quick
        results = run_and_verify(command, use_gemini=use_gemini)
        
        # Exit with appropriate code
        if results['results']['failed'] > 0:
            raise typer.Exit(1)
    
    else:
        typer.echo("Error: Provide either a command to run or a file to verify", err=True)
        raise typer.Exit(1)


def display_results(results: dict):
    """Display verification results in a clear format"""
    typer.echo("\n" + "="*40)
    typer.echo("VERIFICATION RESULTS")
    typer.echo("="*40)
    
    total = results.get('total', 0)
    passed = results.get('passed', 0)
    failed = results.get('failed', 0)
    accuracy = results.get('accuracy', 0)
    
    typer.echo(f"Total Tests: {total}")
    typer.echo(f"Passed: {passed} ✅")
    typer.echo(f"Failed: {failed} ❌")
    typer.echo(f"Success Rate: {accuracy:.1f}%")
    
    if results.get('suspicious'):
        typer.echo(f"\n⚠️  WARNING: {results.get('warning')}")
    
    typer.echo("="*40 + "\n")
    
    # Return appropriate exit code
    if failed > 0:
        sys.exit(1)


@app.command()
def compare(
    file1: Path = typer.Argument(..., help="First output file"),
    file2: Path = typer.Argument(..., help="Second output file")
):
    """Compare two test output files"""
    
    if not file1.exists() or not file2.exists():
        typer.echo("Error: Both files must exist", err=True)
        raise typer.Exit(1)
    
    output1 = file1.read_text()
    output2 = file2.read_text()
    
    results1 = verify_simple(output1)
    results2 = verify_simple(output2)
    
    typer.echo("\n" + "="*60)
    typer.echo("TEST OUTPUT COMPARISON")
    typer.echo("="*60)
    typer.echo(f"\nFile 1: {file1.name}")
    typer.echo(f"  Passed: {results1['passed']}, Failed: {results1['failed']}, Total: {results1['total']}")
    
    typer.echo(f"\nFile 2: {file2.name}")
    typer.echo(f"  Passed: {results2['passed']}, Failed: {results2['failed']}, Total: {results2['total']}")
    
    if results1 == results2:
        typer.echo("\n✅ Results match!")
    else:
        typer.echo("\n❌ Results differ!")
        
    typer.echo("="*60 + "\n")


if __name__ == "__main__":
    app()