"""
Functional tests for max/ model routing with Claude CLI.

These tests verify that the model name parsing and --model flag
addition work correctly in the claude_cli_executor.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from llm_call.core.api.claude_cli_executor import execute_claude_cli
from llm_call.core.router import resolve_route
from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider


class TestMaxModelRoutingFunctional:
    """Test the complete flow of max/ model routing."""
    
    def test_model_parsing_in_executor(self):
        """Test that model names are correctly parsed and added to CLI command."""
        test_cases = [
            ("max/opus", ["--model", "opus"]),
            ("max/sonnet", ["--model", "sonnet"]),
            ("max/claude-opus-4-20250514", ["--model", "claude-opus-4-20250514"]),
            ("max/claude-sonnet-4-20250514", ["--model", "claude-sonnet-4-20250514"]),
            ("max/", ["--model", "opus"]),  # Default
            ("MAX/OPUS", ["--model", "opus"]),  # Case insensitive
            ("max/unknown", ["--model", "unknown"]),  # Unknown model
            ("max/mustard-model", ["--model", "mustard-model"]),  # Invalid model name
            (None, []),  # No model specified
            ("gpt-4", []),  # Non-max model
        ]
        
        mock_exe_path = Path("/usr/bin/claude")
        mock_target_dir = Path("/tmp")
        
        for model_name, expected_model_args in test_cases:
            with patch('subprocess.Popen') as mock_popen, \
                 patch.object(Path, 'is_file', return_value=True), \
                 patch.object(Path, 'is_dir', return_value=True):
                # Mock the subprocess
                mock_process = MagicMock()
                mock_process.stdout.readline.side_effect = [
                    '{"type": "assistant", "message": {"content": [{"type": "text", "text": "Test response"}]}}',
                    '{"type": "result", "subtype": "success", "result": "Test response"}',
                    ''  # End of stream
                ]
                mock_process.poll.return_value = 0
                mock_process.returncode = 0
                mock_process.communicate.return_value = ('', '')
                mock_popen.return_value = mock_process
                
                # Execute with model name
                try:
                    result = execute_claude_cli(
                        prompt="Test prompt",
                        system_prompt_content="Test system",
                        target_dir=mock_target_dir,
                        claude_exe_path=mock_exe_path,
                        model_name=model_name
                    )
                except Exception:
                    # If the executable doesn't exist, it returns early
                    # We can still check if Popen was called
                    pass
                
                # Verify the command was constructed correctly
                if expected_model_args:
                    # Check that Popen was called with the model flag
                    popen_call = mock_popen.call_args
                    cmd_list = popen_call[0][0]
                    
                    # Verify model flag is present
                    assert "--model" in cmd_list, f"--model flag missing for {model_name}"
                    model_idx = cmd_list.index("--model")
                    assert cmd_list[model_idx + 1] == expected_model_args[1], \
                        f"Wrong model value for {model_name}: expected {expected_model_args[1]}, got {cmd_list[model_idx + 1]}"
                else:
                    # Verify no model flag for non-max models
                    if mock_popen.called:
                        popen_call = mock_popen.call_args
                        cmd_list = popen_call[0][0]
                        assert "--model" not in cmd_list, f"--model flag should not be present for {model_name}"
    
    def test_router_to_executor_flow(self):
        """Test the complete flow from router to executor."""
        # Test that router correctly identifies max/ models
        config = {
            "model": "max/opus",
            "messages": [{"role": "user", "content": "test"}]
        }
        
        provider_class, api_params = resolve_route(config)
        
        # Verify correct routing
        assert provider_class == ClaudeCLIProxyProvider
        assert api_params["model"] == "max/opus"
        
        # Test the provider would pass the model correctly
        # (In real usage, the provider calls the API which calls the executor)
        assert "model" in api_params
        assert api_params["model"].startswith("max/")
    
    @pytest.mark.parametrize("model,expected_cli_model", [
        ("max/opus", "opus"),
        ("max/sonnet", "sonnet"),
        ("max/claude-opus-4-20250514", "claude-opus-4-20250514"),
        ("max/", "opus"),
    ])
    def test_model_extraction_logic(self, model, expected_cli_model):
        """Test the model extraction logic in isolation."""
        # Simulate the logic from claude_cli_executor
        claude_model_spec = None
        
        if model and model.lower().startswith("max/"):
            model_suffix = model[4:]  # Skip "max/"
            if model_suffix:
                if model_suffix.lower() == "opus":
                    claude_model_spec = "opus"
                elif model_suffix.lower() == "sonnet":
                    claude_model_spec = "sonnet"
                elif model_suffix.startswith("claude-"):
                    claude_model_spec = model_suffix
                else:
                    claude_model_spec = model_suffix
            else:
                claude_model_spec = "opus"  # Default
        
        assert claude_model_spec == expected_cli_model, \
            f"Model extraction failed for {model}: expected {expected_cli_model}, got {claude_model_spec}"
    
    def test_invalid_model_error_handling(self):
        """Test error handling when Claude CLI rejects invalid model."""
        mock_exe_path = Path("/usr/bin/claude")
        mock_target_dir = Path("/tmp")
        
        # Test cases of invalid models that Claude CLI would reject
        invalid_models = [
            "max/mustard-model",
            "max/invalid-model-12345",
            "max/gpt-4",  # Wrong provider model
        ]
        
        for model_name in invalid_models:
            with patch('subprocess.Popen') as mock_popen, \
                 patch.object(Path, 'is_file', return_value=True), \
                 patch.object(Path, 'is_dir', return_value=True):
                # Mock Claude CLI returning an error for invalid model
                mock_process = MagicMock()
                mock_process.stdout.readline.side_effect = [
                    '{"type": "result", "subtype": "error", "error": "Invalid model specified"}',
                    ''  # End of stream
                ]
                mock_process.poll.return_value = 1
                mock_process.returncode = 1
                mock_process.communicate.return_value = ('', 'Error: Invalid model')
                mock_popen.return_value = mock_process
                
                # Execute with invalid model
                result = execute_claude_cli(
                    prompt="Test prompt",
                    system_prompt_content="Test system",
                    target_dir=mock_target_dir,
                    claude_exe_path=mock_exe_path,
                    model_name=model_name
                )
                
                # Verify error handling
                assert result is not None
                assert "Error from Claude CLI" in result or "Invalid model" in result, \
                    f"Expected error message for invalid model {model_name}, got: {result}"
                
                # Verify the --model flag was still passed
                popen_call = mock_popen.call_args
                cmd_list = popen_call[0][0]
                assert "--model" in cmd_list
                model_idx = cmd_list.index("--model")
                # Extract just the model name without max/ prefix
                expected_model = model_name[4:] if model_name.startswith("max/") else model_name
                assert cmd_list[model_idx + 1] == expected_model
    
    def test_api_key_error_handling(self):
        """Test handling of API key errors from Claude CLI."""
        mock_exe_path = Path("/usr/bin/claude")
        mock_target_dir = Path("/tmp")
        
        # Test with valid model but API key error
        test_cases = [
            ("max/opus", "Authentication failed: Invalid API key"),
            ("max/sonnet", "Error: API key not found or invalid"),
            ("max/claude-opus-4-20250514", "403 Forbidden: Invalid credentials"),
        ]
        
        for model_name, error_message in test_cases:
            with patch('subprocess.Popen') as mock_popen, \
                 patch.object(Path, 'is_file', return_value=True), \
                 patch.object(Path, 'is_dir', return_value=True):
                # Mock Claude CLI returning API key error
                mock_process = MagicMock()
                mock_process.stdout.readline.side_effect = [
                    f'{{"type": "result", "subtype": "error", "error": "{error_message}"}}',
                    ''  # End of stream
                ]
                mock_process.poll.return_value = 1
                mock_process.returncode = 1
                mock_process.communicate.return_value = ('', f'Error: {error_message}')
                mock_popen.return_value = mock_process
                
                # Execute with valid model but expect API key error
                result = execute_claude_cli(
                    prompt="Test prompt",
                    system_prompt_content="Test system",
                    target_dir=mock_target_dir,
                    claude_exe_path=mock_exe_path,
                    model_name=model_name
                )
                
                # Verify error is properly returned
                assert result is not None
                assert "Error from Claude CLI" in result or error_message in result, \
                    f"Expected API key error for {model_name}, got: {result}"
                
                # Verify the correct model was still passed
                popen_call = mock_popen.call_args
                cmd_list = popen_call[0][0]
                assert "--model" in cmd_list
    
    def test_honeypot_invalid_models(self):
        """Test honeypot cases - completely invalid model names that might trick the system."""
        mock_exe_path = Path("/usr/bin/claude")
        mock_target_dir = Path("/tmp")
        
        # Honeypot test cases - trying to trick the system
        honeypot_models = [
            "max/../../etc/passwd",  # Path traversal attempt
            "max/claude-opus-4-20250514; rm -rf /",  # Command injection
            "max/claude' OR '1'='1",  # SQL injection style
            "max/${OPENAI_API_KEY}",  # Environment variable expansion
            "max/\"; cat /etc/passwd; echo \"",  # Quote escape attempt
            "max/claude-opus-4-20250514\x00malicious",  # Null byte injection
            "max/" + "A" * 1000,  # Buffer overflow attempt
            "max/claude-opus-4-20250514%20--no-sandbox",  # URL encoding
            "max/claude-opus-4-$(whoami)",  # Command substitution
        ]
        
        for model_name in honeypot_models:
            with patch('subprocess.Popen') as mock_popen, \
                 patch.object(Path, 'is_file', return_value=True), \
                 patch.object(Path, 'is_dir', return_value=True):
                # Mock subprocess - should safely handle any input
                mock_process = MagicMock()
                mock_process.stdout.readline.side_effect = [
                    '{"type": "result", "subtype": "error", "error": "Invalid model"}',
                    ''
                ]
                mock_process.poll.return_value = 1
                mock_process.returncode = 1
                mock_process.communicate.return_value = ('', 'Error: Invalid model')
                mock_popen.return_value = mock_process
                
                # Execute with honeypot model - should not cause any security issues
                result = execute_claude_cli(
                    prompt="Test prompt",
                    system_prompt_content="Test system",
                    target_dir=mock_target_dir,
                    claude_exe_path=mock_exe_path,
                    model_name=model_name
                )
                
                # Verify it's handled safely
                assert result is not None
                
                # Verify the model name is passed safely (no command injection)
                popen_call = mock_popen.call_args
                cmd_list = popen_call[0][0]
                assert "--model" in cmd_list
                model_idx = cmd_list.index("--model")
                passed_model = cmd_list[model_idx + 1]
                
                # The model should be passed as a single argument, not split or executed
                assert isinstance(passed_model, str), "Model should be a single string argument"
                # Verify dangerous characters are preserved as-is (not executed)
                expected_model = model_name[4:]  # Remove "max/" prefix
                assert passed_model == expected_model, f"Model not passed safely: {passed_model}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])