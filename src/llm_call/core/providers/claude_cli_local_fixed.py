"""
Claude CLI local provider implementation with multimodal support.
Module: claude_cli_local_fixed.py

This provider executes Claude CLI directly without a proxy server.
Now supports multimodal messages by extracting image paths.

Links:
- subprocess documentation: https://docs.python.org/3/library/subprocess.html

Sample usage:
    provider = ClaudeCLILocalProvider()
    response = await provider.complete(messages=[...])

Expected output:
    Dict with OpenAI-compatible response format
"""

import os
import uuid
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger

from llm_call.core.providers.base_provider import BaseLLMProvider
from llm_call.core.config.loader import load_configuration
from llm_call.core.api.claude_cli_executor import execute_claude_cli

# Load config at module level
config = load_configuration()


class ClaudeCLILocalProvider(BaseLLMProvider):
    """Provider that executes Claude CLI directly locally."""
    
    def __init__(self, cli_path: Optional[str] = None, workspace_dir: Optional[str] = None):
        """
        Initialize the Claude CLI local provider.
        
        Args:
            cli_path: Path to Claude CLI executable
            workspace_dir: Working directory for Claude CLI
        """
        # Use local_cli_path from config if available, otherwise fall back to cli_path
        default_path = config.claude_proxy.local_cli_path or config.claude_proxy.cli_path
        self.cli_path = Path(cli_path or os.environ.get('CLAUDE_CLI_PATH', default_path))
        self.workspace_dir = Path(workspace_dir or os.environ.get('CLAUDE_PROXY_WORKSPACE_DIR', config.claude_proxy.workspace_dir))
        
        # Ensure ANTHROPIC_API_KEY is not set
        if 'ANTHROPIC_API_KEY' in os.environ:
            logger.warning("ANTHROPIC_API_KEY is set - unsetting to use Claude Max OAuth")
            os.environ.pop('ANTHROPIC_API_KEY')
        
        logger.info(f"Initialized ClaudeCLILocalProvider with CLI: {self.cli_path}")
    
    def _extract_content_from_message(self, msg: Dict[str, Any]) -> str:
        """
        Extract content from a message, handling both string and multimodal formats.
        
        Args:
            msg: Message dictionary
            
        Returns:
            String content suitable for Claude CLI
        """
        content = msg.get("content", "")
        
        # Handle string content (simple case)
        if isinstance(content, str):
            return content
        
        # Handle multimodal content (list format)
        if isinstance(content, list):
            parts = []
            
            for item in content:
                if not isinstance(item, dict):
                    continue
                    
                item_type = item.get("type")
                
                if item_type == "text":
                    text = item.get("text", "")
                    if text:
                        parts.append(text)
                        
                elif item_type == "image_url":
                    # Extract image URL/path
                    image_url = item.get("image_url", {}).get("url", "")
                    
                    if image_url:
                        # Check if it's a local file path
                        if image_url.startswith("/") or image_url.startswith("./"):
                            # It's a local path - Claude CLI can handle this
                            parts.append(image_url)
                        elif image_url.startswith("data:"):
                            # It's a base64 data URI - we'd need to save it to a file
                            logger.warning("Base64 image data not yet supported for Claude CLI")
                            parts.append("[Image data provided but not supported via CLI]")
                        elif image_url.startswith("http"):
                            # It's a URL - Claude CLI might handle this
                            parts.append(image_url)
                        else:
                            # Unknown format
                            parts.append(f"[Image: {image_url}]")
            
            # Join all parts with spaces
            return " ".join(parts)
        
        # Fallback for unexpected formats
        logger.warning(f"Unexpected content format: {type(content)}")
        return str(content)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        response_format: Any = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete a chat conversation via local Claude CLI.
        
        Args:
            messages: List of message dictionaries
            response_format: Optional response format (not used for Claude CLI)
            **kwargs: Additional parameters like model, temperature, max_tokens
            
        Returns:
            OpenAI-compatible response dictionary
        """
        # Extract the last user message as the prompt
        prompt = ""
        system_prompt = "You are a helpful assistant."
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = self._extract_content_from_message(msg)
            elif msg["role"] == "user":
                prompt = self._extract_content_from_message(msg)
        
        if not prompt:
            raise ValueError("No user message found in messages")
        
        # Get model name
        model_name = kwargs.get("model", "max/opus")
        
        logger.debug(f"[ClaudeCLILocal] Executing Claude CLI locally")
        logger.debug(f"[ClaudeCLILocal] Model: {model_name}")
        logger.debug(f"[ClaudeCLILocal] Prompt: {prompt[:100]}...")
        
        # Execute Claude CLI
        start_time = time.time()
        
        result = execute_claude_cli(
            prompt=prompt,
            system_prompt_content=system_prompt,
            target_dir=self.workspace_dir,
            claude_exe_path=self.cli_path,
            timeout=kwargs.get("timeout", 120),
            model_name=model_name
        )
        
        duration = time.time() - start_time
        
        # Format response in OpenAI-compatible format
        if result and not result.startswith("Error"):
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model_name,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(result.split()),
                    "total_tokens": len(prompt.split()) + len(result.split())
                }
            }
            
            logger.success(f"[ClaudeCLILocal] Got response in {duration:.2f}s")
            return response
        else:
            # Handle error case
            logger.error(f"[ClaudeCLILocal] Claude CLI error: {result}")
            raise Exception(f"Claude CLI execution failed: {result}")


# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_multimodal():
        logger.info("Testing Claude CLI local provider with multimodal support...")
        
        provider = ClaudeCLILocalProvider()
        
        # Test 1: Text only
        messages = [
            {"role": "user", "content": "What is 2+2?"}
        ]
        
        try:
            response = await provider.complete(messages=messages, model="max/opus")
            logger.success(f"✅ Text test passed: {response['choices'][0]['message']['content']}")
        except Exception as e:
            logger.error(f"❌ Text test failed: {e}")
        
        # Test 2: Multimodal with image path
        messages = [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Please describe this image:"},
                    {"type": "image_url", "image_url": {"url": "/home/graham/workspace/experiments/llm_call/images/test.png"}}
                ]
            }
        ]
        
        try:
            response = await provider.complete(messages=messages, model="max/opus")
            logger.success(f"✅ Multimodal test passed: {response['choices'][0]['message']['content'][:100]}...")
        except Exception as e:
            logger.error(f"❌ Multimodal test failed: {e}")
    
    # Run test
    asyncio.run(test_multimodal())