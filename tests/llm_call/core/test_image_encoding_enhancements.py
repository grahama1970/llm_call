#!/usr/bin/env python3
"""
Test multimodal utilities image encoding enhancements.
Verifies POC 11 patterns are integrated correctly.
"""

import sys
import time
from pathlib import Path
from PIL import Image
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from llm_call.core.utils.image_processing_utils import (
    detect_image_format,
    format_image_for_api,
    encode_image_with_metadata,
    process_image_input,
    SUPPORTED_FORMATS
)


def test_format_detection():
    """Test enhanced format detection."""
    print("\n🔍 Testing format detection...")
    
    # Create test images
    test_cases = []
    
    # PNG test
    png_path = Path("test_format.png")
    img = Image.new('RGB', (100, 100), color='red')
    img.save(png_path)
    test_cases.append((png_path, "png"))
    
    # JPEG test
    jpg_path = Path("test_format.jpg")
    img.save(jpg_path, format='JPEG')
    test_cases.append((jpg_path, "jpg"))
    
    # WebP test
    webp_path = Path("test_format.webp")
    img.save(webp_path, format='WEBP')
    test_cases.append((webp_path, "webp"))
    
    results = []
    try:
        for path, expected in test_cases:
            detected = detect_image_format(path)
            if detected == expected or (expected == "jpg" and detected == "jpeg"):
                print(f"✅ Correctly detected {path.name} as {detected}")
                results.append(True)
            else:
                print(f"❌ Wrong format for {path.name}: expected {expected}, got {detected}")
                results.append(False)
    finally:
        # Cleanup
        for path, _ in test_cases:
            path.unlink(missing_ok=True)
    
    return all(results)


def test_api_formatting():
    """Test API-specific formatting."""
    print("\n🔧 Testing API formatting...")
    
    # Create test image data
    test_data = {
        "type": "image_url",
        "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        }
    }
    
    results = []
    
    # Test OpenAI format (should be unchanged)
    openai_result = format_image_for_api(test_data.copy(), "openai")
    if openai_result == test_data:
        print("✅ OpenAI format correct (unchanged)")
        results.append(True)
    else:
        print("❌ OpenAI format incorrect")
        results.append(False)
    
    # Test Anthropic format
    anthropic_result = format_image_for_api(test_data.copy(), "anthropic")
    if (anthropic_result.get("type") == "image" and 
        "source" in anthropic_result and
        anthropic_result["source"]["type"] == "base64"):
        print("✅ Anthropic format correct")
        results.append(True)
    else:
        print("❌ Anthropic format incorrect")
        results.append(False)
    
    # Test LiteLLM format
    litellm_result = format_image_for_api(test_data.copy(), "litellm")
    if "format" in litellm_result["image_url"]:
        print("✅ LiteLLM format correct (added format)")
        results.append(True)
    else:
        print("❌ LiteLLM format incorrect")
        results.append(False)
    
    return all(results)


def test_metadata_encoding():
    """Test image encoding with metadata."""
    print("\n📊 Testing metadata encoding...")
    
    # Create test image
    img_path = Path("test_metadata.png")
    img = Image.new('RGB', (200, 150), color='blue')
    img.save(img_path)
    
    try:
        # Test base64 encoding with metadata
        start = time.time()
        result = encode_image_with_metadata(img_path, "base64")
        elapsed = (time.time() - start) * 1000
        
        # Check all required fields
        required_fields = ["format", "mime_type", "size_bytes", "dimensions", "encoded", "encoding", "encoding_time_ms"]
        missing = [f for f in required_fields if f not in result]
        
        if not missing:
            print(f"✅ All metadata fields present")
            print(f"   Format: {result['format']}")
            print(f"   Size: {result['size_bytes']} bytes")
            print(f"   Dimensions: {result['dimensions']}")
            print(f"   Encoding time: {result['encoding_time_ms']:.2f}ms")
            
            # Verify performance
            if result['encoding_time_ms'] < 100:
                print(f"✅ Performance good: {result['encoding_time_ms']:.2f}ms < 100ms")
                return True
            else:
                print(f"❌ Performance slow: {result['encoding_time_ms']:.2f}ms >= 100ms")
                return False
        else:
            print(f"❌ Missing metadata fields: {missing}")
            return False
            
    finally:
        img_path.unlink(missing_ok=True)


def test_integration():
    """Test integration with existing process_image_input."""
    print("\n🔗 Testing integration with process_image_input...")
    
    # Create test image
    img_path = Path("test_integration.jpg")
    img = Image.new('RGB', (300, 200), color='green')
    img.save(img_path, format='JPEG')
    
    # Create temp directory for processing
    temp_dir = Path("temp_images")
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Process the image
        result = process_image_input(str(img_path), str(temp_dir), max_size_kb=500)
        
        if result and "image_url" in result and "url" in result["image_url"]:
            url = result["image_url"]["url"]
            if url.startswith("data:image/jpeg;base64,"):
                print("✅ Integration successful - image processed and encoded")
                
                # Test API formatting on the result
                anthropic_formatted = format_image_for_api(result, "anthropic")
                if anthropic_formatted.get("type") == "image":
                    print("✅ Can format processed image for different APIs")
                    return True
                else:
                    print("❌ API formatting failed on processed image")
                    return False
            else:
                print("❌ Unexpected URL format")
                return False
        else:
            print("❌ Processing failed")
            return False
            
    finally:
        img_path.unlink(missing_ok=True)
        # Clean up temp directory
        for f in temp_dir.glob("*"):
            f.unlink()
        temp_dir.rmdir()


if __name__ == "__main__":
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Format detection
    total_tests += 1
    try:
        if test_format_detection():
            logger.success("✅ Format detection test passed")
        else:
            all_validation_failures.append("Format detection test failed")
    except Exception as e:
        all_validation_failures.append(f"Format detection exception: {str(e)}")
        logger.error(f"Exception in format detection: {e}")
    
    # Test 2: API formatting
    total_tests += 1
    try:
        if test_api_formatting():
            logger.success("✅ API formatting test passed")
        else:
            all_validation_failures.append("API formatting test failed")
    except Exception as e:
        all_validation_failures.append(f"API formatting exception: {str(e)}")
        logger.error(f"Exception in API formatting: {e}")
    
    # Test 3: Metadata encoding
    total_tests += 1
    try:
        if test_metadata_encoding():
            logger.success("✅ Metadata encoding test passed")
        else:
            all_validation_failures.append("Metadata encoding test failed")
    except Exception as e:
        all_validation_failures.append(f"Metadata encoding exception: {str(e)}")
        logger.error(f"Exception in metadata encoding: {e}")
    
    # Test 4: Integration
    total_tests += 1
    try:
        if test_integration():
            logger.success("✅ Integration test passed")
        else:
            all_validation_failures.append("Integration test failed")
    except Exception as e:
        all_validation_failures.append(f"Integration exception: {str(e)}")
        logger.error(f"Exception in integration: {e}")
    
    # Final result
    if all_validation_failures:
        logger.error(f"\n❌ VALIDATION FAILED - {len(all_validation_failures)} of {total_tests} tests failed:")
        for failure in all_validation_failures:
            logger.error(f"  - {failure}")
        sys.exit(1)
    else:
        logger.success(f"\n✅ VALIDATION PASSED - All {total_tests} tests produced expected results")
        logger.info("Multimodal utilities enhanced with POC 11 patterns")
        sys.exit(0)