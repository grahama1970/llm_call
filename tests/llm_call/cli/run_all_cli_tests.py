#!/usr/bin/env python3
"""
Comprehensive CLI Test Runner

This script runs all CLI tests and verifies that:
1. All CLI commands work correctly
2. MCP features are functional
3. CLI commands align with README documentation
4. All features mentioned in documentation are tested
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple
import re
import tempfile


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_cli_help() -> bool:
    """Check that CLI help works and extract commands."""
    print("\n📋 Checking CLI help...")
    
    code, stdout, stderr = run_command([sys.executable, "-m", "llm_call.cli.main", "--help"])
    
    if code != 0:
        print(f"❌ CLI help failed: {stderr}")
        return False
        
    print("✅ CLI help works")
    
    # Extract commands from help
    commands = re.findall(r'^\s+(\w+(?:-\w+)*)\s+', stdout, re.MULTILINE)
    print(f"📊 Found {len(commands)} CLI commands: {', '.join(sorted(commands))}")
    
    return True


def verify_readme_alignment() -> bool:
    """Verify that CLI aligns with README documentation."""
    print("\n📖 Verifying README alignment...")
    
    readme_path = Path("README.md")
    if not readme_path.exists():
        readme_path = Path(__file__).parent.parent.parent.parent / "README.md"
        
    if not readme_path.exists():
        print("❌ README.md not found")
        return False
        
    readme_content = readme_path.read_text()
    
    # Extract CLI examples from README
    cli_examples = []
    
    # Find code blocks with CLI commands
    code_blocks = re.findall(r'```(?:bash|python)?\n(.*?)\n```', readme_content, re.DOTALL)
    
    for block in code_blocks:
        # Look for llm-cli or main.py commands
        commands = re.findall(r'(?:llm-cli|python -m llm_call\.cli\.main)\s+(\w+(?:-\w+)*)', block)
        cli_examples.extend(commands)
        
    # Also check inline code
    inline_commands = re.findall(r'`(?:llm-cli\s+)?(\w+(?:-\w+)*)`', readme_content)
    cli_examples.extend(inline_commands)
    
    # Unique commands mentioned
    unique_commands = set(cli_examples)
    print(f"📚 Commands mentioned in README: {', '.join(sorted(unique_commands))}")
    
    # Verify each command exists
    all_exist = True
    for cmd in unique_commands:
        code, _, _ = run_command([sys.executable, "-m", "llm_call.cli.main", cmd, "--help"])
        if code != 0:
            print(f"❌ Command '{cmd}' mentioned in README but doesn't exist")
            all_exist = False
        else:
            print(f"✅ Command '{cmd}' exists")
            
    return all_exist


def test_basic_commands() -> bool:
    """Test basic CLI commands work."""
    print("\n🧪 Testing basic commands...")
    
    tests_passed = True
    
    # Test models command
    print("\n  Testing 'models' command...")
    code, stdout, _ = run_command([sys.executable, "-m", "llm_call.cli.main", "models", "--all"])
    if code == 0 and "Available Models" in stdout:
        print("  ✅ models command works")
    else:
        print("  ❌ models command failed")
        tests_passed = False
        
    # Test validators command
    print("\n  Testing 'validators' command...")
    code, stdout, _ = run_command([sys.executable, "-m", "llm_call.cli.main", "validators"])
    if code == 0 and "Validation Strategies" in stdout:
        print("  ✅ validators command works")
    else:
        print("  ❌ validators command failed")
        tests_passed = False
        
    # Test config-example command
    print("\n  Testing 'config-example' command...")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        code, _, _ = run_command([
            sys.executable, "-m", "llm_call.cli.main", 
            "config-example", "--output", tmp.name
        ])
        
        if code == 0 and Path(tmp.name).exists():
            # Verify it's valid JSON
            try:
                config = json.loads(Path(tmp.name).read_text())
                if "model" in config and "messages" in config:
                    print("  ✅ config-example command works")
                else:
                    print("  ❌ config-example generated invalid config")
                    tests_passed = False
            except:
                print("  ❌ config-example generated invalid JSON")
                tests_passed = False
        else:
            print("  ❌ config-example command failed")
            tests_passed = False
            
        Path(tmp.name).unlink(missing_ok=True)
        
    return tests_passed


def test_mcp_features() -> bool:
    """Test MCP-related features."""
    print("\n🔌 Testing MCP features...")
    
    tests_passed = True
    
    # Test generate-mcp-config
    print("\n  Testing 'generate-mcp-config' command...")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        code, _, _ = run_command([
            sys.executable, "-m", "llm_call.cli.main",
            "generate-mcp-config", "--output", tmp.name
        ])
        
        if code == 0 and Path(tmp.name).exists():
            try:
                config = json.loads(Path(tmp.name).read_text())
                if "tools" in config and "server" in config:
                    tool_count = len(config["tools"])
                    print(f"  ✅ generate-mcp-config works ({tool_count} tools)")
                else:
                    print("  ❌ generate-mcp-config generated invalid config")
                    tests_passed = False
            except:
                print("  ❌ generate-mcp-config generated invalid JSON")
                tests_passed = False
        else:
            print("  ❌ generate-mcp-config command failed")
            tests_passed = False
            
        Path(tmp.name).unlink(missing_ok=True)
        
    # Test generate-claude
    print("\n  Testing 'generate-claude' command...")
    with tempfile.TemporaryDirectory() as tmpdir:
        code, stdout, _ = run_command([
            sys.executable, "-m", "llm_call.cli.main",
            "generate-claude", "--output", tmpdir
        ])
        
        if code == 0:
            json_files = list(Path(tmpdir).glob("*.json"))
            if json_files:
                print(f"  ✅ generate-claude works ({len(json_files)} commands)")
            else:
                print("  ❌ generate-claude created no files")
                tests_passed = False
        else:
            print("  ❌ generate-claude command failed")
            tests_passed = False
            
    return tests_passed


def run_pytest_suites() -> bool:
    """Run pytest test suites."""
    print("\n🧪 Running pytest suites...")
    
    test_dir = Path(__file__).parent
    all_passed = True
    
    # Run comprehensive tests
    print("\n  Running comprehensive CLI tests...")
    code, stdout, stderr = run_command([
        sys.executable, "-m", "pytest",
        str(test_dir / "test_cli_comprehensive.py"),
        "-v", "--tb=short", "-q"
    ])
    
    if code == 0:
        print("  ✅ Comprehensive tests passed")
    else:
        print("  ❌ Comprehensive tests failed")
        print(stdout)
        if stderr:
            print(stderr)
        all_passed = False
        
    # Run MCP tests
    print("\n  Running MCP feature tests...")
    code, stdout, stderr = run_command([
        sys.executable, "-m", "pytest",
        str(test_dir / "test_mcp_features.py"),
        "-v", "--tb=short", "-q"
    ])
    
    if code == 0:
        print("  ✅ MCP tests passed")
    else:
        print("  ❌ MCP tests failed")
        print(stdout)
        if stderr:
            print(stderr)
        all_passed = False
        
    return all_passed


def check_feature_coverage() -> bool:
    """Check that all major features are covered by tests."""
    print("\n📊 Checking feature coverage...")
    
    features = {
        "Basic LLM calls": ["ask", "chat", "call"],
        "Configuration": ["config-example", "validators", "models"],
        "Claude integration": ["generate-claude"],
        "MCP integration": ["generate-mcp-config", "serve-mcp"],
        "Testing": ["test", "test-poc"]
    }
    
    all_covered = True
    
    for feature, commands in features.items():
        print(f"\n  {feature}:")
        for cmd in commands:
            # Check if command exists
            code, _, _ = run_command([
                sys.executable, "-m", "llm_call.cli.main", 
                cmd, "--help"
            ])
            
            if code == 0:
                print(f"    ✅ {cmd}")
            else:
                print(f"    ❌ {cmd} - not implemented")
                all_covered = False
                
    return all_covered


def main():
    """Run all CLI tests and validations."""
    print("🚀 Comprehensive CLI Test Runner")
    print("=" * 60)
    
    all_passed = True
    
    # Check CLI help
    if not check_cli_help():
        all_passed = False
        
    # Verify README alignment
    if not verify_readme_alignment():
        all_passed = False
        
    # Test basic commands
    if not test_basic_commands():
        all_passed = False
        
    # Test MCP features
    if not test_mcp_features():
        all_passed = False
        
    # Run pytest suites
    if not run_pytest_suites():
        all_passed = False
        
    # Check feature coverage
    if not check_feature_coverage():
        all_passed = False
        
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("✅ All CLI tests passed!")
        print("\n🎉 The CLI is fully functional and aligned with documentation!")
        return 0
    else:
        print("❌ Some tests failed!")
        print("\n⚠️  Please fix the failing tests before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())