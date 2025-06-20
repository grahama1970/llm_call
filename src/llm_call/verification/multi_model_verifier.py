#!/usr/bin/env python3
"""
Multi-Model Verification System for Usage Functions

This system uses multiple LLMs to verify outputs since Claude Code cannot be trusted
to accurately report success.
"""

import json
import subprocess
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm_call.api import ask_sync


class MultiModelVerifier:
    """Verify usage function outputs using multiple models"""
    
    def __init__(self):
        self.verifiers = {
            "ollama_qwen": self._verify_with_ollama,
            "gemini": self._verify_with_gemini,
            "claude_opus": self._verify_with_opus,
            "perplexity": self._verify_with_perplexity
        }
        
    def _verify_with_ollama(self, prompt: str) -> Dict[str, Any]:
        """Quick local verification with Ollama Qwen 30B"""
        try:
            # Use docker exec to call ollama
            cmd = [
                "docker", "exec", "llm-call-ollama",
                "ollama", "run", "hf.co/Qwen/Qwen3-30B-A3B-GGUF:Q8_0",
                prompt
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            
            response = result.stdout.strip()
            
            return {
                "model": "ollama/qwen3-30b",
                "response": response,
                "error": result.stderr if result.returncode != 0 else None,
                "latency_ms": None  # Could add timing
            }
        except Exception as e:
            return {
                "model": "ollama/qwen3-30b",
                "response": None,
                "error": str(e),
                "latency_ms": None
            }
    
    def _verify_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Verify with Google Gemini"""
        try:
            import time
            start = time.time()
            
            response = ask_sync(
                prompt=prompt,
                model="vertex_ai/gemini-2.5-flash-preview-05-20",
                temperature=0.1
            )
            
            latency = (time.time() - start) * 1000
            
            return {
                "model": "gemini-2.5-flash",
                "response": response,
                "error": None,
                "latency_ms": latency
            }
        except Exception as e:
            return {
                "model": "gemini-2.5-flash",
                "response": None,
                "error": str(e),
                "latency_ms": None
            }
    
    def _verify_with_opus(self, prompt: str) -> Dict[str, Any]:
        """Verify with Claude Opus"""
        try:
            import time
            start = time.time()
            
            response = ask_sync(
                prompt=prompt,
                model="claude-3-opus-20240229",
                temperature=0.1
            )
            
            latency = (time.time() - start) * 1000
            
            return {
                "model": "claude-3-opus",
                "response": response,
                "error": None,
                "latency_ms": latency
            }
        except Exception as e:
            return {
                "model": "claude-3-opus",
                "response": None,
                "error": str(e),
                "latency_ms": None
            }
    
    def _verify_with_perplexity(self, prompt: str) -> Dict[str, Any]:
        """Verify with Perplexity"""
        try:
            import time
            start = time.time()
            
            # Using llm_call to route through perplexity
            response = ask_sync(
                prompt=prompt,
                model="perplexity/sonar-small-online",  # Fast model
                temperature=0.1
            )
            
            latency = (time.time() - start) * 1000
            
            return {
                "model": "perplexity-sonar",
                "response": response,
                "error": None,
                "latency_ms": latency
            }
        except Exception as e:
            return {
                "model": "perplexity-sonar",
                "response": None,
                "error": str(e),
                "latency_ms": None
            }
    
    def verify_single_result(
        self, 
        operation_name: str,
        input_prompt: str,
        output: str,
        expected_behavior: str,
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Verify a single operation result with specified models"""
        
        if models is None:
            models = ["ollama_qwen"]  # Default to fast local verification
        
        verification_prompt = f"""Verify this operation result:
Operation: {operation_name}
Input: {input_prompt}
Output: {output}
Expected: {expected_behavior}

Reply with only: PASS or FAIL"""
        
        results = {
            "operation": operation_name,
            "input": input_prompt,
            "output": output,
            "expected": expected_behavior,
            "verifications": {}
        }
        
        for model in models:
            if model in self.verifiers:
                results["verifications"][model] = self.verifiers[model](verification_prompt)
        
        return results
    
    def verify_all_results(
        self,
        results_file: str,
        test_definitions: Dict[str, Dict[str, str]],
        models: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Verify all results from a usage function output file"""
        
        if models is None:
            models = ["ollama_qwen", "gemini"]  # Default verification pipeline
        
        with open(results_file) as f:
            results = json.load(f)
        
        verifications = {
            "timestamp": datetime.now().isoformat(),
            "results_file": results_file,
            "models_used": models,
            "operations": []
        }
        
        for result in results:
            op_name = result["operation"]
            if op_name in test_definitions:
                verification = self.verify_single_result(
                    operation_name=op_name,
                    input_prompt=result["input"],
                    output=result["output"] if result["error"] is None else f"ERROR: {result['error']}",
                    expected_behavior=test_definitions[op_name]["expected"],
                    models=models
                )
                verifications["operations"].append(verification)
        
        return verifications
    
    def generate_verification_report(
        self, 
        verifications: Dict[str, Any],
        output_format: str = "markdown"
    ) -> str:
        """Generate a readable verification report"""
        
        if output_format == "markdown":
            return self._generate_markdown_report(verifications)
        elif output_format == "json":
            return json.dumps(verifications, indent=2)
        else:
            raise ValueError(f"Unknown format: {output_format}")
    
    def _generate_markdown_report(self, verifications: Dict[str, Any]) -> str:
        """Generate markdown report with comparison table"""
        
        report = f"""# Multi-Model Verification Report

Generated: {verifications['timestamp']}
Results File: {verifications['results_file']}
Models Used: {', '.join(verifications['models_used'])}

## Summary Table

| Operation | Input | Output | """
        
        # Add model columns
        for model in verifications['models_used']:
            report += f"{model} | "
        
        report += "Consensus |\n|"
        report += "---|" * (3 + len(verifications['models_used']) + 1) + "\n"
        
        # Add rows for each operation
        for op in verifications['operations']:
            # Truncate long strings for table
            input_short = op['input'][:30] + "..." if len(op['input']) > 30 else op['input']
            output_short = op['output'][:30] + "..." if len(op['output']) > 30 else op['output']
            
            report += f"| {op['operation']} | {input_short} | {output_short} | "
            
            # Add each model's verdict
            passes = 0
            total = 0
            for model in verifications['models_used']:
                if model in op['verifications']:
                    verdict = op['verifications'][model]
                    if verdict['error']:
                        report += "ERROR | "
                    else:
                        response = verdict['response']
                        if response and 'PASS' in response.upper():
                            report += "✅ PASS | "
                            passes += 1
                        else:
                            report += "❌ FAIL | "
                        total += 1
                else:
                    report += "N/A | "
            
            # Consensus
            if total == 0:
                consensus = "No data"
            elif passes == total:
                consensus = "✅ PASS"
            elif passes == 0:
                consensus = "❌ FAIL"
            else:
                consensus = f"🟡 Mixed ({passes}/{total})"
            
            report += f"{consensus} |\n"
        
        # Add detailed results
        report += "\n## Detailed Results\n\n"
        
        for op in verifications['operations']:
            report += f"### {op['operation']}\n\n"
            report += f"**Input:** `{op['input']}`\n\n"
            report += f"**Output:** `{op['output']}`\n\n"
            report += f"**Expected:** {op['expected']}\n\n"
            
            for model, verdict in op['verifications'].items():
                report += f"**{model}:**\n"
                if verdict['error']:
                    report += f"- Error: {verdict['error']}\n"
                else:
                    report += f"- Response: {verdict['response']}\n"
                    if verdict['latency_ms']:
                        report += f"- Latency: {verdict['latency_ms']:.0f}ms\n"
                report += "\n"
            
            report += "---\n\n"
        
        return report


if __name__ == "__main__":
    # Test the verifier
    verifier = MultiModelVerifier()
    
    # Define what we expect from each operation
    test_definitions = {
        "basic_math_gpt35": {"expected": "Should return 4"},
        "haiku_gpt4": {"expected": "Should be a haiku with 5-7-5 syllables"},
        "json_response_gemini": {"expected": "Should return valid JSON with name and age keys"},
        "completion_routed": {"expected": "Should complete with 'jumps over the lazy dog'"}
    }
    
    # Run verification
    results = verifier.verify_all_results(
        results_file="basic_operations_results.json",
        test_definitions=test_definitions,
        models=["ollama_qwen", "gemini"]  # Start with these two
    )
    
    # Generate report
    report = verifier.generate_verification_report(results, "markdown")
    print(report)
    
    # Save report
    with open("multi_model_verification_report.md", "w") as f:
        f.write(report)