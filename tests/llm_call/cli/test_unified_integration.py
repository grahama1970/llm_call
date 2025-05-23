#!/usr/bin/env python3
"""
Test unified CLI integration with litellm configuration.

This verifies:
1. Configuration building works correctly
2. CLI commands are properly defined
3. Slash command generation functions
4. Config file loading works
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from llm_call.cli.main_unified import build_llm_config, load_config_file
from llm_call.cli.slash_mcp_mixin import generate_claude_command_config


def test_config_building():
    """Test configuration building from various sources."""
    print("Testing configuration building...")
    
    # Test 1: Basic config
    config = build_llm_config(
        prompt="Test prompt",
        model="gpt-4",
        validation=["json", "code"],
        temperature=0.5,
        max_tokens=1000
    )
    
    assert config["messages"][0]["content"] == "Test prompt"
    assert config["model"] == "gpt-4"
    assert len(config["validation"]) == 2
    assert config["temperature"] == 0.5
    assert config["max_tokens"] == 1000
    print("✓ Basic configuration building works")
    
    # Test 2: With system prompt
    config = build_llm_config(
        prompt="User message",
        system_prompt="System message"
    )
    
    assert len(config["messages"]) == 2
    assert config["messages"][0]["role"] == "system"
    assert config["messages"][1]["role"] == "user"
    print("✓ System prompt handling works")
    
    # Test 3: JSON response format
    config = build_llm_config(
        prompt="Generate JSON",
        response_format="json_object"
    )
    
    assert config["response_format"]["type"] == "json_object"
    print("✓ Response format configuration works")
    
    # Test 4: Retry configuration
    config = build_llm_config(
        prompt="Test",
        retry_max=5
    )
    
    assert config["retry_config"]["max_attempts"] == 5
    print("✓ Retry configuration works")


def test_config_file_loading():
    """Test loading configurations from files."""
    print("\nTesting config file loading...")
    
    # Test JSON config
    json_config = {
        "model": "claude-3",
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.3,
        "validation": [{"strategy": "json"}]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json_config, f)
        json_path = Path(f.name)
    
    loaded = load_config_file(json_path)
    assert loaded["model"] == "claude-3"
    assert loaded["temperature"] == 0.3
    print("✓ JSON config loading works")
    
    # Test config override
    config = build_llm_config(
        prompt="Override prompt",
        model="gpt-4",  # Override model
        config_file=json_path
    )
    
    assert config["model"] == "gpt-4"  # CLI override
    assert config["messages"][0]["content"] == "Override prompt"  # CLI override
    assert config["temperature"] == 0.3  # From file
    print("✓ Config overrides work correctly")
    
    # Cleanup
    json_path.unlink()


def test_slash_command_generation():
    """Test slash command configuration generation."""
    print("\nTesting slash command generation...")
    
    # Generate config for a complex command
    config = generate_claude_command_config(
        name="ask",
        params=[
            {"name": "prompt", "type": str, "required": True},
            {"name": "model", "type": str, "required": False},
            {"name": "validate", "type": list, "required": False},
            {"name": "temperature", "type": float, "required": False}
        ],
        help_text="Ask LLM with configuration",
        module_path="llm_call.cli.main_unified"
    )
    
    assert config["name"] == "llm-ask"
    assert len(config["args"]) == 4
    assert config["args"][0]["name"] == "prompt"
    assert not config["args"][0]["optional"]
    assert config["args"][1]["optional"]
    print("✓ Slash command generation works")
    
    # Verify command construction
    assert "main_unified ask" in config["execute"]
    print("✓ Command execution string correct")


def test_validation_integration():
    """Test validation strategy integration."""
    print("\nTesting validation integration...")
    
    # Test validation config building
    config = build_llm_config(
        prompt="Generate code",
        validation=["code", "syntax", "imports"]
    )
    
    assert len(config["validation"]) == 3
    assert config["validation"][0]["strategy"] == "code"
    assert config["validation"][1]["strategy"] == "syntax"
    assert config["validation"][2]["strategy"] == "imports"
    print("✓ Multiple validation strategies configured")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("UNIFIED CLI INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        test_config_building()
        test_config_file_loading()
        test_slash_command_generation()
        test_validation_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print("\nThe unified CLI successfully integrates:")
        print("- Simple command interface")
        print("- Full litellm configuration support")
        print("- Config file loading with overrides")
        print("- Slash command auto-generation")
        print("- Validation strategy configuration")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())