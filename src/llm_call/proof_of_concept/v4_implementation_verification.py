#!/usr/bin/env python3
"""
Verification script to check what's actually implemented vs claimed.

This script audits the v4 implementation to identify:
1. What's actually implemented
2. What's just scaffolding
3. What hasn't been tested
4. What assumptions were made
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def check_file_exists(filepath: str) -> Tuple[bool, str]:
    """Check if a file exists and return status."""
    path = Path(filepath)
    if path.exists():
        return True, f"{GREEN}✓ EXISTS{RESET}"
    return False, f"{RED}✗ MISSING{RESET}"

def check_function_implemented(filepath: str, function_name: str) -> Tuple[bool, str]:
    """Check if a function is actually implemented (not just pass or ...)."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if function_name in content:
                # Check if it's just a stub
                func_start = content.find(f"def {function_name}")
                if func_start == -1:
                    func_start = content.find(f"async def {function_name}")
                
                if func_start != -1:
                    func_section = content[func_start:func_start + 500]
                    if "pass" in func_section[:100] or "..." in func_section[:100]:
                        return False, f"{YELLOW}⚠ STUB ONLY{RESET}"
                    elif "TODO" in func_section or "FIXME" in func_section:
                        return False, f"{YELLOW}⚠ TODO FOUND{RESET}"
                    else:
                        return True, f"{GREEN}✓ IMPLEMENTED{RESET}"
            return False, f"{RED}✗ NOT FOUND{RESET}"
    except Exception as e:
        return False, f"{RED}✗ ERROR: {e}{RESET}"

def verify_mcp_implementation():
    """Verify MCP implementation status."""
    print(f"\n{BLUE}=== MCP Implementation Verification ==={RESET}")
    
    checks = [
        ("MCP Proxy Server", check_file_exists("/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_claude_proxy_server.py")),
        ("MCP Config Writer", check_function_implemented("/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_claude_proxy_server.py", "write_dynamic_mcp_json")),
        ("MCP Config Cleanup", check_function_implemented("/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_claude_proxy_server.py", "remove_dynamic_mcp_json")),
        ("--mcp-config Flag", check_function_implemented("/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_claude_proxy_server.py", "--mcp-config")),
    ]
    
    for name, (status, msg) in checks:
        print(f"  {name}: {msg}")
    
    # Special check for --mcp-config flag
    print(f"\n  {YELLOW}⚠ ISSUE FOUND:{RESET} Claude CLI requires --mcp-config flag, not automatic .mcp.json loading")
    print(f"  {YELLOW}  Status:{RESET} Fixed in latest edit")

def verify_validation_strategies():
    """Verify validation strategy implementations."""
    print(f"\n{BLUE}=== Validation Strategies Verification ==={RESET}")
    
    validators = [
        "PoCResponseNotEmptyValidator",
        "PoCJsonStringValidator", 
        "PoCFieldPresentValidator",
        "PoCAgentTaskValidator"
    ]
    
    enhanced_file = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_validation_strategies_enhanced.py"
    original_file = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_validation_strategies.py"
    
    print(f"  Enhanced validators file: {check_file_exists(enhanced_file)[1]}")
    print(f"  Original validators file: {check_file_exists(original_file)[1]}")
    
    if Path(enhanced_file).exists():
        for validator in validators:
            _, msg = check_function_implemented(enhanced_file, validator)
            print(f"  {validator}: {msg}")

def verify_retry_manager():
    """Verify retry manager features."""
    print(f"\n{BLUE}=== Retry Manager Verification ==={RESET}")
    
    filepath = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/poc_retry_manager.py"
    
    features = [
        ("retry_with_validation_poc", "Main retry function"),
        ("max_attempts_before_tool_use", "Tool escalation threshold"),
        ("max_attempts_before_human", "Human escalation threshold"),
        ("debug_tool_mcp_config", "MCP config injection"),
        ("PoCHumanReviewNeededError", "Human review exception")
    ]
    
    for feature, desc in features:
        if Path(filepath).exists():
            with open(filepath, 'r') as f:
                content = f.read()
                if feature in content:
                    print(f"  {desc}: {GREEN}✓ FOUND{RESET}")
                else:
                    print(f"  {desc}: {RED}✗ NOT FOUND{RESET}")

def verify_llm_call_tool():
    """Verify recursive LLM call tool."""
    print(f"\n{BLUE}=== LLM Call Tool Verification ==={RESET}")
    
    tool_script = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/tools/llm_call_delegator.py"
    tool_json = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/tools/llm_call_tool.json"
    
    print(f"  Delegator script: {check_file_exists(tool_script)[1]}")
    print(f"  MCP tool definition: {check_file_exists(tool_json)[1]}")
    
    if Path(tool_script).exists():
        _, msg = check_function_implemented(tool_script, "delegate_llm_call")
        print(f"  delegate_llm_call function: {msg}")
        
        # Check for recursion protection
        with open(tool_script, 'r') as f:
            content = f.read()
            if "max_recursion_depth" in content:
                print(f"  Recursion protection: {GREEN}✓ IMPLEMENTED{RESET}")
            else:
                print(f"  Recursion protection: {RED}✗ MISSING{RESET}")

def verify_test_implementation():
    """Verify test implementation."""
    print(f"\n{BLUE}=== Test Implementation Verification ==={RESET}")
    
    test_file = "/home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept/test_v4_implementation.py"
    
    print(f"  Test file: {check_file_exists(test_file)[1]}")
    
    if Path(test_file).exists():
        with open(test_file, 'r') as f:
            content = f.read()
            
        # Check imports
        print(f"\n  {YELLOW}Import Issues:{RESET}")
        if "from litellm_client_poc import llm_call" in content:
            print(f"    - Imports from litellm_client_poc (wrong location)")
        if "from poc_claude_proxy_server import" in content:
            print(f"    - Imports from poc_claude_proxy_server (wrong location)")
            
        # Check for actual test execution
        if "asyncio.run(" in content:
            print(f"  Test runner: {GREEN}✓ PRESENT{RESET}")
        else:
            print(f"  Test runner: {RED}✗ MISSING{RESET}")

def check_untested_assumptions():
    """List assumptions made without testing."""
    print(f"\n{BLUE}=== Untested Assumptions ==={RESET}")
    
    assumptions = [
        "Claude CLI reads .mcp.json from working directory (WRONG - needs --mcp-config flag)",
        "MCP tool format matches the actual spec (UNVERIFIED)",
        "Claude will return JSON in expected format from agent validators (UNTESTED)",
        "Port 3010 is available and not in use (UNCHECKED)",
        "llm_call_tool parameters are passed correctly (UNTESTED)",
        "MCP tools handle errors gracefully (UNKNOWN)",
        "Multiple .mcp.json files won't conflict (UNVERIFIED)",
        "Recursive llm_call from validator will work (UNTESTED)",
        "Enhanced validators are actually imported and used (NOT INTEGRATED)"
    ]
    
    for i, assumption in enumerate(assumptions, 1):
        print(f"  {i}. {RED}⚠{RESET} {assumption}")

def main():
    """Run all verification checks."""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}V4 Implementation Verification Report{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    verify_mcp_implementation()
    verify_validation_strategies()
    verify_retry_manager()
    verify_llm_call_tool()
    verify_test_implementation()
    check_untested_assumptions()
    
    print(f"\n{BLUE}=== Summary ==={RESET}")
    print(f"{YELLOW}⚠ CRITICAL ISSUES:{RESET}")
    print("1. MCP implementation assumes automatic .mcp.json loading (WRONG)")
    print("2. Test imports are from wrong locations")
    print("3. No actual integration with existing codebase")
    print("4. No real testing with Claude CLI")
    print("5. Many untested assumptions about MCP behavior")
    
    print(f"\n{RED}CONCLUSION:{RESET} Implementation is mostly scaffolding with critical flaws.")
    print("Needs significant fixes and actual testing before claiming completion.")

if __name__ == "__main__":
    main()