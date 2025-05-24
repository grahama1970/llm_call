#!/usr/bin/env python3
"""
POC-11: Image Encoding and Format Support

This script validates image encoding methods (base64, URLs) and format support.
Implements encoding, decoding, and format validation for multimodal inputs.

Links:
- LiteLLM Vision Docs: https://docs.litellm.ai/docs/completion/vision
- Base64 Encoding: https://docs.python.org/3/library/base64.html
- Image Formats: https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html

Sample Input:
{
    "image_path": "test.png",
    "encoding": "base64",
    "format": "png",
    "validate": true
}

Expected Output:
{
    "encoded": "data:image/png;base64,iVBORw0...",
    "format": "PNG",
    "size_bytes": 12345,
    "dimensions": [800, 600],
    "encoding_time_ms": 5.2
}
"""

import base64
import io
import mimetypes
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
from PIL import Image
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


class ImageEncoder:
    """Handles image encoding for multimodal LLM APIs."""
    
    SUPPORTED_FORMATS = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'webp': 'image/webp',
        'gif': 'image/gif'
    }
    
    # Size limits based on API documentation
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_RESOLUTION = (2048, 2048)
    
    def encode_image(self, image_path: Union[str, Path], encoding: str = "base64") -> Dict[str, any]:
        """
        Encode image for LLM API consumption.
        
        Args:
            image_path: Path to image file
            encoding: Either "base64" or "url"
            
        Returns:
            Dict with encoded image data and metadata
        """
        start_time = time.time()
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Get file info
        file_size = image_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(f"Image too large: {file_size} bytes (max: {self.MAX_FILE_SIZE})")
        
        # Detect format
        img_format = self._detect_format(image_path)
        if img_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {img_format}")
        
        # Get image dimensions
        with Image.open(image_path) as img:
            dimensions = img.size
            if dimensions[0] > self.MAX_RESOLUTION[0] or dimensions[1] > self.MAX_RESOLUTION[1]:
                logger.warning(f"Image exceeds max resolution: {dimensions} > {self.MAX_RESOLUTION}")
        
        result = {
            "format": img_format.upper(),
            "mime_type": self.SUPPORTED_FORMATS[img_format],
            "size_bytes": file_size,
            "dimensions": dimensions
        }
        
        if encoding == "base64":
            # Read and encode
            with open(image_path, "rb") as f:
                image_data = f.read()
            encoded = base64.b64encode(image_data).decode('utf-8')
            result["encoded"] = f"data:{self.SUPPORTED_FORMATS[img_format]};base64,{encoded}"
            result["encoding"] = "base64"
        elif encoding == "url":
            # For local files, convert to file:// URL
            result["encoded"] = image_path.absolute().as_uri()
            result["encoding"] = "url"
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")
        
        result["encoding_time_ms"] = (time.time() - start_time) * 1000
        return result
    
    def _detect_format(self, image_path: Path) -> str:
        """Detect image format from file."""
        # Try from extension first
        ext = image_path.suffix.lower().lstrip('.')
        if ext in self.SUPPORTED_FORMATS:
            return ext
        
        # Try from content
        mime_type = mimetypes.guess_type(str(image_path))[0]
        if mime_type:
            for fmt, mime in self.SUPPORTED_FORMATS.items():
                if mime == mime_type:
                    return fmt
        
        # Use PIL as fallback
        try:
            with Image.open(image_path) as img:
                return img.format.lower()
        except Exception:
            return "unknown"
    
    def decode_base64_image(self, encoded_str: str) -> Tuple[bytes, str]:
        """
        Decode base64 image string.
        
        Returns:
            Tuple of (image_bytes, format)
        """
        # Handle data URL format
        if encoded_str.startswith('data:'):
            header, data = encoded_str.split(',', 1)
            mime_type = header.split(':')[1].split(';')[0]
            
            # Find format from mime type
            img_format = None
            for fmt, mime in self.SUPPORTED_FORMATS.items():
                if mime == mime_type:
                    img_format = fmt
                    break
            
            return base64.b64decode(data), img_format or "unknown"
        else:
            # Plain base64
            return base64.b64decode(encoded_str), "unknown"
    
    def optimize_image(self, image_path: Union[str, Path], max_size: Optional[int] = None) -> bytes:
        """
        Optimize image for API consumption.
        
        Args:
            image_path: Path to image
            max_size: Maximum file size in bytes
            
        Returns:
            Optimized image bytes
        """
        image_path = Path(image_path)
        max_size = max_size or self.MAX_FILE_SIZE
        
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Resize if needed
            if img.size[0] > self.MAX_RESOLUTION[0] or img.size[1] > self.MAX_RESOLUTION[1]:
                img.thumbnail(self.MAX_RESOLUTION, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {img.size}")
            
            # Save to bytes with optimization
            output = io.BytesIO()
            
            # Try different quality levels to meet size requirement
            for quality in [95, 85, 75, 65]:
                output.seek(0)
                output.truncate()
                
                if image_path.suffix.lower() in ['.jpg', '.jpeg']:
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                elif image_path.suffix.lower() == '.png':
                    img.save(output, format='PNG', optimize=True)
                elif image_path.suffix.lower() == '.webp':
                    img.save(output, format='WEBP', quality=quality, method=6)
                else:
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                
                size = output.tell()
                if size <= max_size:
                    logger.info(f"Optimized to {size} bytes (quality={quality})")
                    break
            
            output.seek(0)
            return output.read()
    
    def format_for_api(self, image_path: Union[str, Path], api_type: str = "openai") -> Dict[str, any]:
        """
        Format image for specific API type.
        
        Args:
            image_path: Path to image
            api_type: API type (openai, anthropic, etc.)
            
        Returns:
            Formatted image object for API
        """
        encoded = self.encode_image(image_path, "base64")
        
        if api_type == "openai":
            return {
                "type": "image_url",
                "image_url": {
                    "url": encoded["encoded"]
                }
            }
        elif api_type == "anthropic":
            # Anthropic expects different format
            _, img_data = self.decode_base64_image(encoded["encoded"])
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": encoded["mime_type"],
                    "data": encoded["encoded"].split(',')[1]  # Remove data URL prefix
                }
            }
        elif api_type == "litellm":
            # LiteLLM standardized format
            return {
                "type": "image_url",
                "image_url": {
                    "url": encoded["encoded"],
                    "format": encoded["mime_type"]
                }
            }
        else:
            raise ValueError(f"Unknown API type: {api_type}")


def test_image_encoding():
    """Test image encoding functionality."""
    encoder = ImageEncoder()
    
    # Create test images
    test_images = []
    
    # Create small PNG
    png_path = Path("test_image.png")
    img = Image.new('RGB', (100, 100), color='red')
    img.save(png_path)
    test_images.append(png_path)
    
    # Create JPEG
    jpg_path = Path("test_image.jpg")
    img = Image.new('RGB', (200, 150), color='blue')
    img.save(jpg_path, format='JPEG')
    test_images.append(jpg_path)
    
    # Create WebP
    webp_path = Path("test_image.webp")
    img = Image.new('RGB', (150, 150), color='green')
    img.save(webp_path, format='WEBP')
    test_images.append(webp_path)
    
    results = []
    
    try:
        # Test base64 encoding
        logger.info("\nTesting base64 encoding...")
        for img_path in test_images:
            try:
                result = encoder.encode_image(img_path, "base64")
                logger.success(f"✅ Encoded {img_path.name}: {result['format']} ({result['size_bytes']} bytes)")
                
                # Verify encoding
                if result["encoded"].startswith("data:"):
                    decoded_data, fmt = encoder.decode_base64_image(result["encoded"])
                    if len(decoded_data) > 0:
                        logger.success(f"✅ Successfully decoded {len(decoded_data)} bytes")
                        results.append({"test": f"base64_{img_path.suffix}", "passed": True})
                    else:
                        logger.error(f"❌ Failed to decode")
                        results.append({"test": f"base64_{img_path.suffix}", "passed": False})
            except Exception as e:
                logger.error(f"❌ Failed to encode {img_path}: {e}")
                results.append({"test": f"base64_{img_path.suffix}", "passed": False})
        
        # Test URL encoding
        logger.info("\nTesting URL encoding...")
        for img_path in test_images[:1]:  # Just test one
            try:
                result = encoder.encode_image(img_path, "url")
                if result["encoded"].startswith("file://"):
                    logger.success(f"✅ URL encoded: {result['encoded']}")
                    results.append({"test": "url_encoding", "passed": True})
                else:
                    logger.error(f"❌ Invalid URL: {result['encoded']}")
                    results.append({"test": "url_encoding", "passed": False})
            except Exception as e:
                logger.error(f"❌ URL encoding failed: {e}")
                results.append({"test": "url_encoding", "passed": False})
        
        # Test optimization
        logger.info("\nTesting image optimization...")
        large_img = Image.new('RGB', (3000, 3000), color='yellow')
        large_path = Path("test_large.jpg")
        large_img.save(large_path, format='JPEG')
        
        try:
            optimized = encoder.optimize_image(large_path, max_size=500*1024)  # 500KB limit
            logger.success(f"✅ Optimized from {large_path.stat().st_size} to {len(optimized)} bytes")
            results.append({"test": "optimization", "passed": len(optimized) <= 500*1024})
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}")
            results.append({"test": "optimization", "passed": False})
        finally:
            large_path.unlink(missing_ok=True)
        
        # Test API formatting
        logger.info("\nTesting API formatting...")
        for api_type in ["openai", "anthropic", "litellm"]:
            try:
                formatted = encoder.format_for_api(test_images[0], api_type)
                logger.success(f"✅ Formatted for {api_type}: {list(formatted.keys())}")
                results.append({"test": f"format_{api_type}", "passed": True})
            except Exception as e:
                logger.error(f"❌ Formatting for {api_type} failed: {e}")
                results.append({"test": f"format_{api_type}", "passed": False})
        
    finally:
        # Cleanup
        for img_path in test_images:
            img_path.unlink(missing_ok=True)
    
    return all(r["passed"] for r in results), results


def test_format_detection():
    """Test format detection capabilities."""
    encoder = ImageEncoder()
    
    # Test various image formats
    test_cases = [
        ("test.png", "png"),
        ("test.jpg", "jpg"),
        ("test.jpeg", "jpeg"),
        ("test.webp", "webp"),
        ("test.gif", "gif"),
        ("test.bmp", "unknown")  # Unsupported
    ]
    
    results = []
    
    for filename, expected in test_cases:
        # Create dummy file
        path = Path(filename)
        
        if expected != "unknown":
            # Create valid image
            img = Image.new('RGB', (10, 10), color='white')
            if expected == "gif":
                img.save(path, format='GIF')
            elif expected in ["jpg", "jpeg"]:
                img.save(path, format='JPEG')
            else:
                img.save(path, format=expected.upper())
        else:
            # Create invalid/unsupported file
            path.write_text("dummy")
        
        try:
            detected = encoder._detect_format(path)
            if detected == expected or (expected == "jpg" and detected == "jpeg"):
                logger.success(f"✅ Correctly detected {filename} as {detected}")
                results.append(True)
            else:
                logger.error(f"❌ Wrong format for {filename}: expected {expected}, got {detected}")
                results.append(False)
        finally:
            path.unlink(missing_ok=True)
    
    return all(results)


def test_performance():
    """Test encoding performance."""
    encoder = ImageEncoder()
    
    # Create test image
    img = Image.new('RGB', (1920, 1080), color='white')
    path = Path("test_perf.jpg")
    img.save(path, format='JPEG')
    
    try:
        # Time encoding
        start = time.time()
        result = encoder.encode_image(path, "base64")
        elapsed = (time.time() - start) * 1000
        
        logger.info(f"Encoding 1920x1080 image took {elapsed:.2f}ms")
        logger.info(f"Encoded size: {len(result['encoded'])} chars")
        
        return elapsed < 100  # Should encode in under 100ms
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Image encoding
    total_tests += 1
    try:
        passed, results = test_image_encoding()
        if passed:
            logger.success("✅ Image encoding tests passed")
        else:
            failed_tests = [r["test"] for r in results if not r["passed"]]
            all_validation_failures.append(f"Image encoding tests failed: {failed_tests}")
    except Exception as e:
        all_validation_failures.append(f"Image encoding exception: {str(e)}")
        logger.error(f"Exception in encoding test: {e}")
    
    # Test 2: Format detection
    total_tests += 1
    try:
        if test_format_detection():
            logger.success("✅ Format detection tests passed")
        else:
            all_validation_failures.append("Format detection tests failed")
    except Exception as e:
        all_validation_failures.append(f"Format detection exception: {str(e)}")
        logger.error(f"Exception in format test: {e}")
    
    # Test 3: Performance
    total_tests += 1
    try:
        if test_performance():
            logger.success("✅ Performance test passed")
        else:
            all_validation_failures.append("Performance test failed (>100ms)")
    except Exception as e:
        all_validation_failures.append(f"Performance test exception: {str(e)}")
        logger.error(f"Exception in performance test: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("POC-11 Image encoding is validated and ready")
        sys.exit(0)