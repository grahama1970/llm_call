#!/usr/bin/env python3
"""
POC-13: Multimodal Message Formatting

This script validates formatting of messages containing both text and images.
Implements proper message structure for various LLM providers.

Links:
- OpenAI Vision Format: https://platform.openai.com/docs/guides/vision
- Anthropic Messages: https://docs.anthropic.com/claude/reference/messages
- LiteLLM Vision: https://docs.litellm.ai/docs/completion/vision

Sample Input:
{
    "text": "What's in this image?",
    "images": ["path/to/image1.jpg", "data:image/png;base64,..."],
    "provider": "openai"
}

Expected Output:
{
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "..."}}
        ]
    }],
    "formatted_for": "openai",
    "content_count": 2
}
"""

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from PIL import Image
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


class MultimodalMessageFormatter:
    """Formats multimodal messages for different LLM providers."""
    
    def format_message(
        self,
        text: Optional[str] = None,
        images: Optional[List[Union[str, Path]]] = None,
        provider: str = "openai",
        role: str = "user",
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Format a multimodal message for the specified provider.
        
        Args:
            text: Text content
            images: List of image paths or base64 strings
            provider: Target provider (openai, anthropic, litellm)
            role: Message role (user, assistant, system)
            system_prompt: Optional system message
            
        Returns:
            Formatted message structure
        """
        if provider == "openai":
            return self._format_openai(text, images, role, system_prompt)
        elif provider == "anthropic":
            return self._format_anthropic(text, images, role, system_prompt)
        elif provider == "litellm":
            return self._format_litellm(text, images, role, system_prompt)
        elif provider == "gemini":
            return self._format_gemini(text, images, role, system_prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _format_openai(
        self,
        text: Optional[str],
        images: Optional[List[Union[str, Path]]],
        role: str,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Format for OpenAI API."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt and role == "user":
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Build content array
        content = []
        
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        
        if images:
            for img in images:
                img_data = self._process_image(img)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": img_data["url"],
                        "detail": "auto"  # Can be "low", "high", or "auto"
                    }
                })
        
        # Add main message
        if content:
            messages.append({
                "role": role,
                "content": content if len(content) > 1 or images else content[0]["text"]
            })
        
        return {
            "messages": messages,
            "formatted_for": "openai",
            "content_count": len(content)
        }
    
    def _format_anthropic(
        self,
        text: Optional[str],
        images: Optional[List[Union[str, Path]]],
        role: str,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Format for Anthropic API."""
        messages = []
        
        # Build content array
        content = []
        
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        
        if images:
            for img in images:
                img_data = self._process_image(img)
                
                # Anthropic expects different format
                if img_data["url"].startswith("data:"):
                    # Extract base64 data
                    header, data = img_data["url"].split(",", 1)
                    media_type = header.split(":")[1].split(";")[0]
                    
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": data
                        }
                    })
                else:
                    # For URLs, we need to download and convert
                    raise NotImplementedError("URL images need to be converted to base64 for Anthropic")
        
        # Add message
        if content:
            messages.append({
                "role": role,
                "content": content
            })
        
        result = {
            "messages": messages,
            "formatted_for": "anthropic",
            "content_count": len(content)
        }
        
        # Anthropic uses separate system parameter
        if system_prompt:
            result["system"] = system_prompt
        
        return result
    
    def _format_litellm(
        self,
        text: Optional[str],
        images: Optional[List[Union[str, Path]]],
        role: str,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Format for LiteLLM standardized format."""
        messages = []
        
        # Add system prompt if provided
        if system_prompt and role == "user":
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Build content array
        content = []
        
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        
        if images:
            for img in images:
                img_data = self._process_image(img)
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": img_data["url"],
                        "format": img_data.get("mime_type", "image/jpeg")
                    }
                })
        
        # Add main message
        if content:
            messages.append({
                "role": role,
                "content": content
            })
        
        return {
            "messages": messages,
            "formatted_for": "litellm",
            "content_count": len(content)
        }
    
    def _format_gemini(
        self,
        text: Optional[str],
        images: Optional[List[Union[str, Path]]],
        role: str,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Format for Google Gemini."""
        messages = []
        
        # Gemini uses "parts" instead of "content"
        parts = []
        
        if text:
            parts.append({"text": text})
        
        if images:
            for img in images:
                img_data = self._process_image(img)
                
                if img_data["url"].startswith("data:"):
                    # Extract base64 and mime type
                    header, data = img_data["url"].split(",", 1)
                    mime_type = header.split(":")[1].split(";")[0]
                    
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": data
                        }
                    })
                else:
                    parts.append({"image_url": img_data["url"]})
        
        # Add message
        if parts:
            messages.append({
                "role": "user" if role == "user" else "model",
                "parts": parts
            })
        
        result = {
            "messages": messages,
            "formatted_for": "gemini",
            "content_count": len(parts)
        }
        
        # Add system instruction if provided
        if system_prompt:
            result["system_instruction"] = {"parts": [{"text": system_prompt}]}
        
        return result
    
    def _process_image(self, image: Union[str, Path]) -> Dict[str, str]:
        """Process image input to standard format."""
        # If already a data URL or http URL
        if isinstance(image, str) and (image.startswith("data:") or image.startswith("http")):
            return {"url": image}
        
        # Convert path to base64
        image_path = Path(image)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Read and encode
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Detect MIME type
        mime_type = self._get_mime_type(image_path)
        
        # Create data URL
        encoded = base64.b64encode(image_data).decode('utf-8')
        url = f"data:{mime_type};base64,{encoded}"
        
        return {"url": url, "mime_type": mime_type}
    
    def _get_mime_type(self, path: Path) -> str:
        """Get MIME type from file extension."""
        ext = path.suffix.lower()
        mime_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        return mime_map.get(ext, 'image/jpeg')
    
    def convert_between_formats(
        self,
        message: Dict[str, Any],
        from_provider: str,
        to_provider: str
    ) -> Dict[str, Any]:
        """Convert message format between providers."""
        # Extract components from source format
        text = None
        images = []
        role = "user"
        system_prompt = None
        
        if from_provider == "openai":
            for msg in message.get("messages", []):
                if msg["role"] == "system":
                    system_prompt = msg["content"]
                else:
                    role = msg["role"]
                    content = msg.get("content", [])
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        for item in content:
                            if item["type"] == "text":
                                text = item["text"]
                            elif item["type"] == "image_url":
                                images.append(item["image_url"]["url"])
        
        # Re-format for target
        return self.format_message(text, images, to_provider, role, system_prompt)


def test_basic_formatting():
    """Test basic message formatting for each provider."""
    formatter = MultimodalMessageFormatter()
    
    # Create test image
    test_img = Path("test_format.png")
    img = Image.new('RGB', (100, 100), color='red')
    img.save(test_img)
    
    results = []
    
    try:
        # Test each provider
        providers = ["openai", "anthropic", "litellm", "gemini"]
        
        for provider in providers:
            try:
                result = formatter.format_message(
                    text="What's in this image?",
                    images=[test_img],
                    provider=provider
                )
                
                # Verify structure
                if "messages" in result and result["content_count"] == 2:
                    logger.success(f"✅ {provider}: Formatted correctly with {result['content_count']} content items")
                    results.append(True)
                else:
                    logger.error(f"❌ {provider}: Invalid format")
                    results.append(False)
                    
            except Exception as e:
                logger.error(f"❌ {provider}: {e}")
                results.append(False)
    
    finally:
        test_img.unlink(missing_ok=True)
    
    return all(results)


def test_multiple_images():
    """Test formatting with multiple images."""
    formatter = MultimodalMessageFormatter()
    
    # Create test images
    images = []
    for i in range(3):
        path = Path(f"test_multi_{i}.jpg")
        img = Image.new('RGB', (50, 50), color=['red', 'green', 'blue'][i])
        img.save(path)
        images.append(path)
    
    results = []
    
    try:
        result = formatter.format_message(
            text="Describe these images",
            images=images,
            provider="openai"
        )
        
        # Should have 1 text + 3 images = 4 content items
        if result["content_count"] == 4:
            logger.success(f"✅ Multiple images: {result['content_count']} content items")
            
            # Check message structure
            msg = result["messages"][0]
            if len(msg["content"]) == 4:
                logger.success("✅ Content array has correct length")
                results.append(True)
            else:
                logger.error("❌ Content array wrong length")
                results.append(False)
        else:
            logger.error(f"❌ Wrong content count: {result['content_count']}")
            results.append(False)
            
    finally:
        for path in images:
            path.unlink(missing_ok=True)
    
    return all(results)


def test_system_prompts():
    """Test system prompt handling."""
    formatter = MultimodalMessageFormatter()
    
    test_cases = [
        ("openai", True),    # Separate system message
        ("anthropic", True), # Separate system parameter
        ("litellm", True),   # Separate system message
        ("gemini", True)     # system_instruction parameter
    ]
    
    results = []
    
    for provider, has_system in test_cases:
        result = formatter.format_message(
            text="Hello",
            provider=provider,
            system_prompt="You are a helpful assistant"
        )
        
        if provider == "openai" or provider == "litellm":
            # Should have system message
            if len(result["messages"]) >= 2 and result["messages"][0]["role"] == "system":
                logger.success(f"✅ {provider}: System message handled correctly")
                results.append(True)
            else:
                logger.error(f"❌ {provider}: System message missing")
                results.append(False)
                
        elif provider == "anthropic":
            # Should have system parameter
            if "system" in result:
                logger.success(f"✅ {provider}: System parameter present")
                results.append(True)
            else:
                logger.error(f"❌ {provider}: System parameter missing")
                results.append(False)
                
        elif provider == "gemini":
            # Should have system_instruction
            if "system_instruction" in result:
                logger.success(f"✅ {provider}: System instruction present")
                results.append(True)
            else:
                logger.error(f"❌ {provider}: System instruction missing")
                results.append(False)
    
    return all(results)


def test_format_conversion():
    """Test converting between provider formats."""
    formatter = MultimodalMessageFormatter()
    
    # Create test image
    test_img = Path("test_convert.png")
    img = Image.new('RGB', (50, 50), color='yellow')
    img.save(test_img)
    
    results = []
    
    try:
        # Create OpenAI format message
        openai_msg = formatter.format_message(
            text="Test message",
            images=[test_img],
            provider="openai",
            system_prompt="Test system"
        )
        
        # Convert to other formats
        conversions = [
            ("openai", "anthropic"),
            ("openai", "litellm"),
            ("openai", "gemini")
        ]
        
        for from_fmt, to_fmt in conversions:
            try:
                converted = formatter.convert_between_formats(
                    openai_msg,
                    from_fmt,
                    to_fmt
                )
                
                if converted["formatted_for"] == to_fmt:
                    logger.success(f"✅ Converted {from_fmt} → {to_fmt}")
                    results.append(True)
                else:
                    logger.error(f"❌ Conversion {from_fmt} → {to_fmt} failed")
                    results.append(False)
                    
            except Exception as e:
                logger.error(f"❌ Conversion error: {e}")
                results.append(False)
                
    finally:
        test_img.unlink(missing_ok=True)
    
    return all(results)


def test_edge_cases():
    """Test edge cases in message formatting."""
    formatter = MultimodalMessageFormatter()
    
    results = []
    
    # Test text-only message
    result = formatter.format_message(
        text="Just text",
        provider="openai"
    )
    
    # Should simplify to string content for OpenAI
    msg = result["messages"][0]
    if isinstance(msg["content"], str):
        logger.success("✅ Text-only message simplified correctly")
        results.append(True)
    else:
        logger.error("❌ Text-only message not simplified")
        results.append(False)
    
    # Test image-only message
    test_img = Path("test_edge.jpg")
    img = Image.new('RGB', (10, 10), color='black')
    img.save(test_img)
    
    try:
        result = formatter.format_message(
            images=[test_img],
            provider="openai"
        )
        
        if result["content_count"] == 1:
            logger.success("✅ Image-only message formatted correctly")
            results.append(True)
        else:
            logger.error("❌ Image-only message has wrong content count")
            results.append(False)
            
    finally:
        test_img.unlink(missing_ok=True)
    
    # Test empty message
    result = formatter.format_message(provider="openai")
    if len(result["messages"]) == 0:
        logger.success("✅ Empty message handled correctly")
        results.append(True)
    else:
        logger.error("❌ Empty message created unexpected content")
        results.append(False)
    
    # Test base64 string input
    base64_img = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    result = formatter.format_message(
        text="Base64 test",
        images=[base64_img],
        provider="openai"
    )
    
    if result["content_count"] == 2:
        logger.success("✅ Base64 image handled correctly")
        results.append(True)
    else:
        logger.error("❌ Base64 image not handled correctly")
        results.append(False)
    
    return all(results)


if __name__ == "__main__":
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic formatting
    total_tests += 1
    try:
        if test_basic_formatting():
            logger.success("✅ Basic formatting tests passed")
        else:
            all_validation_failures.append("Basic formatting tests failed")
    except Exception as e:
        all_validation_failures.append(f"Basic formatting exception: {str(e)}")
        logger.error(f"Exception in basic test: {e}")
    
    # Test 2: Multiple images
    total_tests += 1
    try:
        if test_multiple_images():
            logger.success("✅ Multiple images tests passed")
        else:
            all_validation_failures.append("Multiple images tests failed")
    except Exception as e:
        all_validation_failures.append(f"Multiple images exception: {str(e)}")
        logger.error(f"Exception in multiple images test: {e}")
    
    # Test 3: System prompts
    total_tests += 1
    try:
        if test_system_prompts():
            logger.success("✅ System prompts tests passed")
        else:
            all_validation_failures.append("System prompts tests failed")
    except Exception as e:
        all_validation_failures.append(f"System prompts exception: {str(e)}")
        logger.error(f"Exception in system prompts test: {e}")
    
    # Test 4: Format conversion
    total_tests += 1
    try:
        if test_format_conversion():
            logger.success("✅ Format conversion tests passed")
        else:
            all_validation_failures.append("Format conversion tests failed")
    except Exception as e:
        all_validation_failures.append(f"Format conversion exception: {str(e)}")
        logger.error(f"Exception in format conversion test: {e}")
    
    # Test 5: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge cases tests passed")
        else:
            all_validation_failures.append("Edge cases tests failed")
    except Exception as e:
        all_validation_failures.append(f"Edge cases exception: {str(e)}")
        logger.error(f"Exception in edge cases test: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-13 Multimodal message formatting is validated and ready")
        sys.exit(0)