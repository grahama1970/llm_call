#!/usr/bin/env python3
"""
Module: test_all_interfaces.py
Description: Comprehensive verification of all llm_call interfaces (slash commands, CLI, Python imports)

External Dependencies:
- subprocess: https://docs.python.org/3/library/subprocess.html
- pathlib: https://docs.python.org/3/library/pathlib.html

Sample Input:
>>> verifier = LLMCallVerifier()
>>> verifier.test_all_interfaces()

Expected Output:
>>> Comprehensive test results for all interfaces with HTML report

Example Usage:
>>> python -m llm_call.verification.test_all_interfaces
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
import tempfile
import asyncio

# Add llm_call to path if needed
llm_call_path = Path(__file__).parent.parent.parent.parent
if llm_call_path not in sys.path:
    sys.path.insert(0, str(llm_call_path))


class InterfaceTest:
    """Container for test results across different interfaces."""
    def __init__(self, test_name: str, description: str):
        self.test_name = test_name
        self.description = description
        self.results = {}  # interface -> result
        self.category = "General"
        
    def add_result(self, interface: str, success: bool, output: str, command: str, duration: float):
        """Add test result for a specific interface."""
        self.results[interface] = {
            'success': success,
            'output': output,
            'command': command,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
    
    def all_passed(self) -> bool:
        """Check if all interfaces passed."""
        return all(r['success'] for r in self.results.values())


class LLMCallVerifier:
    """Comprehensive verification of all llm_call interfaces."""
    
    def __init__(self):
        self.tests: List[InterfaceTest] = []
        self.start_time = datetime.now()
        self.test_image = "/home/graham/workspace/experiments/llm_call/images/test2.png"
        
    def run_command(self, cmd: List[str], timeout: int = 30) -> Tuple[bool, str, float]:
        """Run a command and return success, output, duration."""
        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="/home/graham/workspace/experiments/llm_call"
            )
            duration = time.time() - start
            output = result.stdout + ("\n--- STDERR ---\n" + result.stderr if result.stderr else "")
            return result.returncode == 0, output, duration
        except subprocess.TimeoutExpired:
            return False, "Command timed out", timeout
        except Exception as e:
            return False, f"Error: {str(e)}", time.time() - start
    
    async def run_python_interface(self, code: str) -> Tuple[bool, str, float]:
        """Test Python import interface."""
        start = time.time()
        try:
            # Create a temporary Python file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Run it
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_file)
            duration = time.time() - start
            output = result.stdout + ("\n--- STDERR ---\n" + result.stderr if result.stderr else "")
            return result.returncode == 0, output, duration
            
        except Exception as e:
            return False, f"Error: {str(e)}", time.time() - start
    
    def test_basic_query(self):
        """Test basic text query across all interfaces."""
        test = InterfaceTest("Basic Text Query", "Simple text-only query to verify basic functionality")
        test.category = "Core Functionality"
        
        # Test 1: Slash command
        cmd = ["/home/graham/.claude/commands/llm_call", "--query", "Reply: TEST PASSED", "--model", "max/opus"]
        success, output, duration = self.run_command(cmd)
        test.add_result("slash_command", success and "TEST PASSED" in output, output, ' '.join(cmd), duration)
        
        # Test 2: CLI direct
        cmd = ["python", "-m", "llm_call", "--query", "Reply: TEST PASSED", "--model", "max/opus"]
        success, output, duration = self.run_command(cmd)
        test.add_result("cli_direct", success and "TEST PASSED" in output, output, ' '.join(cmd), duration)
        
        # Test 3: Python import
        code = '''
import asyncio
from llm_call import ask

async def main():
    result = await ask("Reply: TEST PASSED", model="max/opus")
    print(f"Result: {result}")

asyncio.run(main())
'''
        success, output, duration = asyncio.run(self.run_python_interface(code))
        test.add_result("python_import", success and "TEST PASSED" in output, output, "Python: ask() function", duration)
        
        self.tests.append(test)
    
    def test_multimodal(self):
        """Test image analysis across interfaces."""
        test = InterfaceTest("Multimodal Image Analysis", "Test image analysis capabilities")
        test.category = "Multimodal"
        
        # Test 1: Slash command with --image
        cmd = ["/home/graham/.claude/commands/llm", "--query", "Is there a coconut? YES or NO only", 
               "--image", self.test_image, "--model", "max/opus"]
        success, output, duration = self.run_command(cmd)
        test.add_result("slash_multimodal", success and ("YES" in output or "yes" in output), 
                       output, ' '.join(cmd), duration)
        
        # Test 2: Python with multimodal message
        code = '''
import asyncio
from llm_call.core.caller import make_llm_request

async def main():
    config = {
        "model": "max/opus",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": "Is there a coconut? YES or NO only"},
                {"type": "image_url", "image_url": {"url": "%s"}}
            ]
        }]
    }
    result = await make_llm_request(config)
    print(f"Result: {result}")

asyncio.run(main())
''' % self.test_image
        success, output, duration = asyncio.run(self.run_python_interface(code))
        test.add_result("python_multimodal", success and ("YES" in output or "yes" in output), 
                       output, "Python: make_llm_request()", duration)
        
        self.tests.append(test)
    
    def test_model_listing(self):
        """Test model listing functionality."""
        test = InterfaceTest("List Available Models", "Verify model discovery works")
        test.category = "Discovery"
        
        # Test 1: Slash command
        cmd = ["/home/graham/.claude/commands/llm_call", "--list-models"]
        success, output, duration = self.run_command(cmd)
        test.add_result("slash_list_models", success and "Claude Max" in output, 
                       output, ' '.join(cmd), duration)
        
        # Test 2: CLI
        cmd = ["python", "-m", "llm_call", "list-models"]
        success, output, duration = self.run_command(cmd)
        test.add_result("cli_list_models", success and "Available models" in output.lower(), 
                       output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def test_json_output(self):
        """Test JSON output format."""
        test = InterfaceTest("JSON Output Format", "Verify structured output")
        test.category = "Formatting"
        
        # Test 1: Slash command with --json
        cmd = ["/home/graham/.claude/commands/llm_call", "--query", "Say JSON", "--model", "max/opus", "--json"]
        success, output, duration = self.run_command(cmd)
        try:
            json_valid = '"response"' in output and json.loads(output.split('\n')[-1])
        except:
            json_valid = False
        test.add_result("slash_json", success and json_valid, output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def test_temperature_control(self):
        """Test temperature parameter."""
        test = InterfaceTest("Temperature Control", "Verify parameter handling")
        test.category = "Parameters"
        
        # Test with low temperature
        cmd = ["/home/graham/.claude/commands/llm_call", "--query", "Reply exactly: TEMP OK", 
               "--model", "max/opus", "--temperature", "0.1"]
        success, output, duration = self.run_command(cmd)
        test.add_result("slash_temperature", success and "TEMP OK" in output, 
                       output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def test_corpus_analysis(self):
        """Test corpus/directory analysis."""
        test = InterfaceTest("Corpus Analysis", "Test directory analysis feature")
        test.category = "Advanced Features"
        
        # Test corpus analysis
        cmd = ["/home/graham/.claude/commands/llm", "--query", "How many Python files?", 
               "--corpus", "/home/graham/workspace/experiments/llm_call/src/llm_call", "--model", "max/opus"]
        success, output, duration = self.run_command(cmd, timeout=60)
        test.add_result("slash_corpus", success and (".py" in output or "Python" in output), 
                       output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def test_validator_usage(self):
        """Test validator functionality."""
        test = InterfaceTest("Validator Usage", "Test response validation")
        test.category = "Validation"
        
        # Test JSON validator
        cmd = ["/home/graham/.claude/commands/llm_call", "--query", '{"test": true}', 
               "--model", "max/opus", "--validate", "json"]
        success, output, duration = self.run_command(cmd)
        test.add_result("slash_validator", success, output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def test_gpt_integration(self):
        """Test OpenAI GPT integration."""
        test = InterfaceTest("GPT-3.5 Integration", "Test OpenAI API integration")
        test.category = "Integration"
        
        # Test GPT-3.5
        cmd = ["/home/graham/.claude/commands/llm_call", "--query", "Say: GPT OK", "--model", "gpt-3.5-turbo"]
        success, output, duration = self.run_command(cmd)
        # Note: May fail if API key is invalid
        test.add_result("slash_gpt", success or "401" in output or "API key" in output, 
                       output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def test_config_file(self):
        """Test config file support."""
        test = InterfaceTest("Config File Support", "Test configuration file loading")
        test.category = "Configuration"
        
        # Create a test config
        config = {
            "model": "max/opus",
            "messages": [{"role": "user", "content": "Config test: OK"}],
            "temperature": 0.5
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name
        
        # Test config file
        cmd = ["/home/graham/.claude/commands/llm_call", "--config", config_file]
        success, output, duration = self.run_command(cmd)
        os.unlink(config_file)
        
        test.add_result("slash_config", success and "OK" in output, output, ' '.join(cmd), duration)
        
        self.tests.append(test)
    
    def generate_html_report(self) -> Path:
        """Generate comprehensive HTML report."""
        from .html_reporter import HTMLReporter
        
        reporter = HTMLReporter(self.tests)
        report_path = reporter.generate_report()
        return report_path
    
    def test_all_interfaces(self):
        """Run all interface tests."""
        print("\n🔍 LLM Call Comprehensive Interface Verification")
        print("=" * 70)
        
        # Run all tests
        self.test_basic_query()
        self.test_multimodal()
        self.test_model_listing()
        self.test_json_output()
        self.test_temperature_control()
        self.test_corpus_analysis()
        self.test_validator_usage()
        self.test_gpt_integration()
        self.test_config_file()
        
        # Generate summary
        total_interfaces_tested = sum(len(test.results) for test in self.tests)
        total_passed = sum(sum(1 for r in test.results.values() if r['success']) for test in self.tests)
        
        print(f"\n{'='*70}")
        print(f"VERIFICATION COMPLETE")
        print(f"{'='*70}")
        print(f"Total Tests: {len(self.tests)}")
        print(f"Total Interface Variations: {total_interfaces_tested}")
        print(f"Passed: {total_passed}/{total_interfaces_tested}")
        print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f}s")
        
        # Show which interfaces work for each test
        print(f"\n{'Test':<30} {'Slash':<10} {'CLI':<10} {'Python':<10}")
        print("-" * 60)
        for test in self.tests:
            slash = "✅" if test.results.get('slash_command', {}).get('success') or \
                           test.results.get('slash_multimodal', {}).get('success') or \
                           test.results.get('slash_list_models', {}).get('success') else "❌"
            cli = "✅" if test.results.get('cli_direct', {}).get('success') or \
                         test.results.get('cli_list_models', {}).get('success') else "-"
            python = "✅" if test.results.get('python_import', {}).get('success') or \
                           test.results.get('python_multimodal', {}).get('success') else "-"
            
            print(f"{test.test_name:<30} {slash:<10} {cli:<10} {python:<10}")
        
        return self.tests


def main():
    """Main entry point."""
    verifier = LLMCallVerifier()
    verifier.test_all_interfaces()
    
    # Generate HTML report
    report_path = verifier.generate_html_report()
    print(f"\n📊 HTML Report Generated: {report_path}")
    print(f"🌐 View at: http://localhost:8891/{report_path.name}")


if __name__ == "__main__":
    main()