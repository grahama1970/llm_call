#!/usr/bin/env python3
"""
POC-12: Image Size and Resolution Optimization

This script validates image size optimization for API constraints.
Implements intelligent resizing, compression, and format conversion.

Links:
- PIL Image Processing: https://pillow.readthedocs.io/en/stable/handbook/tutorial.html
- Image Optimization: https://web.dev/fast/#optimize-your-images
- API Limits: https://platform.openai.com/docs/guides/vision

Sample Input:
{
    "image": "large_photo.jpg",
    "max_size_mb": 20,
    "max_resolution": [2048, 2048],
    "target_size_kb": 500
}

Expected Output:
{
    "original_size": 25000000,
    "optimized_size": 450000,
    "original_dimensions": [4000, 3000],
    "optimized_dimensions": [2048, 1536],
    "compression_ratio": 55.56,
    "optimization_time_ms": 250.5
}
"""

import io
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from PIL import Image, ImageOps
from loguru import logger
import hashlib

# Configure logger
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


class ImageOptimizer:
    """Handles image optimization for LLM API constraints."""
    
    # API constraints
    MAX_FILE_SIZE_MB = 20
    MAX_RESOLUTION = (2048, 2048)
    
    # Optimization settings
    JPEG_QUALITY_LEVELS = [95, 85, 75, 65, 55]
    WEBP_QUALITY_LEVELS = [95, 85, 75, 65]
    PNG_COMPRESS_LEVEL = 9
    
    def optimize_for_api(
        self, 
        image_path: Union[str, Path],
        max_size_mb: float = None,
        max_resolution: Tuple[int, int] = None,
        target_size_kb: Optional[float] = None,
        preserve_format: bool = False
    ) -> Dict[str, any]:
        """
        Optimize image for API constraints.
        
        Args:
            image_path: Path to image
            max_size_mb: Maximum file size in MB
            max_resolution: Maximum (width, height)
            target_size_kb: Target size in KB (will try to get close)
            preserve_format: Keep original format if possible
            
        Returns:
            Optimization results with metrics
        """
        start_time = time.time()
        image_path = Path(image_path)
        
        # Set defaults
        max_size_mb = max_size_mb or self.MAX_FILE_SIZE_MB
        max_resolution = max_resolution or self.MAX_RESOLUTION
        max_size_bytes = int(max_size_mb * 1024 * 1024)
        
        # Get original metrics
        original_size = image_path.stat().st_size
        
        with Image.open(image_path) as img:
            original_dimensions = img.size
            original_format = img.format
            
            # Calculate if resizing is needed
            resize_needed = (
                img.width > max_resolution[0] or 
                img.height > max_resolution[1]
            )
            
            # Resize if needed
            if resize_needed:
                img = self._smart_resize(img, max_resolution)
                logger.info(f"Resized from {original_dimensions} to {img.size}")
            
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                img = self._convert_to_rgb(img)
            
            # Optimize based on format
            if target_size_kb:
                optimized_data = self._optimize_to_target_size(
                    img, 
                    target_size_kb * 1024,
                    preserve_format,
                    original_format
                )
            else:
                optimized_data = self._optimize_quality(
                    img,
                    max_size_bytes,
                    preserve_format,
                    original_format
                )
            
            # Get final metrics
            optimized_size = len(optimized_data)
            
            # Verify we can read the optimized image
            with Image.open(io.BytesIO(optimized_data)) as opt_img:
                optimized_dimensions = opt_img.size
                optimized_format = opt_img.format
        
        # Calculate compression ratio
        compression_ratio = (1 - optimized_size / original_size) * 100
        
        result = {
            "original_size": original_size,
            "optimized_size": optimized_size,
            "original_dimensions": list(original_dimensions),
            "optimized_dimensions": list(optimized_dimensions),
            "original_format": original_format,
            "optimized_format": optimized_format,
            "compression_ratio": round(compression_ratio, 2),
            "optimization_time_ms": round((time.time() - start_time) * 1000, 2),
            "optimized_data": optimized_data
        }
        
        return result
    
    def _smart_resize(self, img: Image.Image, max_resolution: Tuple[int, int]) -> Image.Image:
        """Smart resize maintaining aspect ratio."""
        # Calculate scaling factor
        scale = min(
            max_resolution[0] / img.width,
            max_resolution[1] / img.height
        )
        
        if scale < 1:
            new_size = (
                int(img.width * scale),
                int(img.height * scale)
            )
            return img.resize(new_size, Image.Resampling.LANCZOS)
        
        return img
    
    def _convert_to_rgb(self, img: Image.Image) -> Image.Image:
        """Convert image to RGB mode."""
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            return background
        elif img.mode == 'P':
            return img.convert('RGB')
        elif img.mode == 'LA':
            return img.convert('RGB')
        return img
    
    def _optimize_quality(
        self,
        img: Image.Image,
        max_size: int,
        preserve_format: bool,
        original_format: str
    ) -> bytes:
        """Optimize image quality to meet size constraint."""
        # Determine best format
        if preserve_format and original_format in ['JPEG', 'PNG', 'WEBP']:
            formats_to_try = [original_format]
        else:
            # Try formats in order of typical compression efficiency
            formats_to_try = ['WEBP', 'JPEG', 'PNG']
        
        best_result = None
        best_size = float('inf')
        
        for fmt in formats_to_try:
            if fmt == 'JPEG':
                for quality in self.JPEG_QUALITY_LEVELS:
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=quality, optimize=True)
                    size = output.tell()
                    
                    if size <= max_size and size < best_size:
                        best_result = output.getvalue()
                        best_size = size
                        if size <= max_size * 0.9:  # Good enough
                            break
            
            elif fmt == 'WEBP':
                for quality in self.WEBP_QUALITY_LEVELS:
                    output = io.BytesIO()
                    img.save(output, format='WEBP', quality=quality, method=6)
                    size = output.tell()
                    
                    if size <= max_size and size < best_size:
                        best_result = output.getvalue()
                        best_size = size
                        if size <= max_size * 0.9:
                            break
            
            elif fmt == 'PNG':
                output = io.BytesIO()
                img.save(output, format='PNG', optimize=True, compress_level=self.PNG_COMPRESS_LEVEL)
                size = output.tell()
                
                if size <= max_size and size < best_size:
                    best_result = output.getvalue()
                    best_size = size
        
        if best_result:
            return best_result
        
        # Last resort: aggressive JPEG compression
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=50, optimize=True)
        return output.getvalue()
    
    def _optimize_to_target_size(
        self,
        img: Image.Image,
        target_size: int,
        preserve_format: bool,
        original_format: str
    ) -> bytes:
        """Optimize to get close to target size."""
        tolerance = 0.1  # 10% tolerance
        
        # Binary search for optimal quality
        if preserve_format and original_format == 'PNG':
            # PNG doesn't have quality setting, just return optimized
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True, compress_level=self.PNG_COMPRESS_LEVEL)
            return output.getvalue()
        
        # For JPEG/WEBP, binary search quality
        fmt = original_format if preserve_format and original_format in ['JPEG', 'WEBP'] else 'JPEG'
        low, high = 10, 100
        best_result = None
        best_diff = float('inf')
        
        while low <= high:
            mid = (low + high) // 2
            output = io.BytesIO()
            
            if fmt == 'JPEG':
                img.save(output, format='JPEG', quality=mid, optimize=True)
            else:
                img.save(output, format='WEBP', quality=mid, method=6)
            
            size = output.tell()
            diff = abs(size - target_size)
            
            if diff < best_diff:
                best_result = output.getvalue()
                best_diff = diff
            
            if size < target_size * (1 - tolerance):
                low = mid + 1
            elif size > target_size * (1 + tolerance):
                high = mid - 1
            else:
                break
        
        return best_result
    
    def batch_optimize(
        self,
        image_paths: List[Union[str, Path]],
        **kwargs
    ) -> List[Dict[str, any]]:
        """Optimize multiple images."""
        results = []
        
        for path in image_paths:
            try:
                result = self.optimize_for_api(path, **kwargs)
                result['path'] = str(path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to optimize {path}: {e}")
                results.append({
                    'path': str(path),
                    'error': str(e)
                })
        
        return results


def test_basic_optimization():
    """Test basic image optimization."""
    optimizer = ImageOptimizer()
    
    # Create test images
    test_cases = [
        # (size, name, expected_compression)
        ((4000, 3000), "large_photo.jpg", 50),  # Should compress well
        ((500, 500), "small_image.png", 10),    # Less compression
        ((2500, 2500), "oversized.jpg", 40),    # Will be resized
    ]
    
    results = []
    
    for (width, height), filename, min_compression in test_cases:
        path = Path(filename)
        
        # Create test image with some content
        img = Image.new('RGB', (width, height))
        # Add some variation to make compression realistic
        for x in range(0, width, 100):
            for y in range(0, height, 100):
                color = (
                    (x * 255 // width),
                    (y * 255 // height),
                    128
                )
                img.putpixel((x, y), color)
        
        img.save(path, format='JPEG' if path.suffix == '.jpg' else 'PNG')
        
        try:
            result = optimizer.optimize_for_api(path)
            
            # Check optimization worked
            if result['optimized_size'] < result['original_size']:
                logger.success(f"✅ {filename}: {result['compression_ratio']}% compression")
                logger.info(f"   {result['original_size']} → {result['optimized_size']} bytes")
                logger.info(f"   {result['original_dimensions']} → {result['optimized_dimensions']}")
                results.append(True)
            else:
                logger.error(f"❌ {filename}: No compression achieved")
                results.append(False)
                
        finally:
            path.unlink(missing_ok=True)
    
    return all(results)


def test_target_size_optimization():
    """Test optimization to target size."""
    optimizer = ImageOptimizer()
    
    # Create large test image
    path = Path("test_target.jpg")
    img = Image.new('RGB', (2000, 1500))
    
    # Add gradient for realistic compression
    for x in range(2000):
        for y in range(0, 1500, 10):
            img.putpixel((x, y), (x * 255 // 2000, y * 255 // 1500, 128))
    
    img.save(path, format='JPEG', quality=95)
    original_size = path.stat().st_size
    
    try:
        # Test different target sizes
        targets = [200, 350, 500]  # KB - more realistic targets
        results = []
        
        for target_kb in targets:
            result = optimizer.optimize_for_api(path, target_size_kb=target_kb)
            actual_kb = result['optimized_size'] / 1024
            tolerance = 0.3  # 30% tolerance for harder targets
            
            if abs(actual_kb - target_kb) / target_kb <= tolerance:
                logger.success(f"✅ Target {target_kb}KB → {actual_kb:.1f}KB")
                results.append(True)
            else:
                logger.error(f"❌ Target {target_kb}KB → {actual_kb:.1f}KB (too far off)")
                results.append(False)
        
        return all(results)
        
    finally:
        path.unlink(missing_ok=True)


def test_format_conversion():
    """Test format conversion during optimization."""
    optimizer = ImageOptimizer()
    
    formats = ['png', 'jpg', 'webp']
    results = []
    
    for fmt in formats:
        path = Path(f"test.{fmt}")
        
        # Create image
        img = Image.new('RGB', (1000, 1000), color='blue')
        if fmt == 'png':
            img.save(path, format='PNG')
        elif fmt == 'jpg':
            img.save(path, format='JPEG')
        else:
            img.save(path, format='WEBP')
        
        try:
            # Optimize without preserving format
            result1 = optimizer.optimize_for_api(path, preserve_format=False)
            
            # Optimize preserving format
            result2 = optimizer.optimize_for_api(path, preserve_format=True)
            
            logger.info(f"\n{fmt.upper()} optimization:")
            logger.info(f"  Non-preserved: {result1['optimized_format']} ({result1['optimized_size']} bytes)")
            logger.info(f"  Preserved: {result2['optimized_format']} ({result2['optimized_size']} bytes)")
            
            # Check format preservation worked
            if result2['optimized_format'].lower() == fmt or (fmt == 'jpg' and result2['optimized_format'] == 'JPEG'):
                logger.success(f"✅ Format preservation worked for {fmt}")
                results.append(True)
            else:
                logger.error(f"❌ Format preservation failed for {fmt}")
                results.append(False)
                
        finally:
            path.unlink(missing_ok=True)
    
    return all(results)


def test_edge_cases():
    """Test edge cases and special formats."""
    optimizer = ImageOptimizer()
    results = []
    
    # Test RGBA image
    path = Path("test_rgba.png")
    img = Image.new('RGBA', (500, 500), (255, 0, 0, 128))
    img.save(path)
    
    try:
        result = optimizer.optimize_for_api(path)
        if result['optimized_size'] > 0:
            logger.success("✅ RGBA image handled correctly")
            results.append(True)
        else:
            logger.error("❌ RGBA image failed")
            results.append(False)
    finally:
        path.unlink(missing_ok=True)
    
    # Test very small image
    path = Path("test_tiny.png")
    img = Image.new('RGB', (10, 10), 'red')
    img.save(path)
    
    try:
        result = optimizer.optimize_for_api(path)
        if result['optimized_dimensions'] == [10, 10]:
            logger.success("✅ Tiny image preserved")
            results.append(True)
        else:
            logger.error("❌ Tiny image incorrectly resized")
            results.append(False)
    finally:
        path.unlink(missing_ok=True)
    
    # Test already optimized image
    path = Path("test_optimized.jpg")
    img = Image.new('RGB', (100, 100), 'green')
    img.save(path, format='JPEG', quality=60, optimize=True)
    
    try:
        original_size = path.stat().st_size
        result = optimizer.optimize_for_api(path)
        
        # Should not increase size significantly
        if result['optimized_size'] <= original_size * 1.1:
            logger.success("✅ Already optimized image handled well")
            results.append(True)
        else:
            logger.error("❌ Optimized image size increased too much")
            results.append(False)
    finally:
        path.unlink(missing_ok=True)
    
    return all(results)


def test_performance():
    """Test optimization performance."""
    optimizer = ImageOptimizer()
    
    # Create medium-sized image
    path = Path("test_perf.jpg")
    img = Image.new('RGB', (3000, 2000))
    
    # Add complexity
    for x in range(0, 3000, 50):
        for y in range(0, 2000, 50):
            img.putpixel((x, y), ((x//10) % 256, (y//10) % 256, 128))
    
    img.save(path)
    
    try:
        start = time.time()
        result = optimizer.optimize_for_api(path)
        elapsed = (time.time() - start) * 1000
        
        logger.info(f"\nOptimization performance:")
        logger.info(f"  Time: {elapsed:.1f}ms")
        logger.info(f"  Size: {result['original_size']} → {result['optimized_size']}")
        logger.info(f"  Compression: {result['compression_ratio']}%")
        
        # Should complete within reasonable time
        return elapsed < 1000  # 1 second
        
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    # Track all failures
    all_validation_failures = []
    total_tests = 0
    
    # Test 1: Basic optimization
    total_tests += 1
    try:
        if test_basic_optimization():
            logger.success("✅ Basic optimization tests passed")
        else:
            all_validation_failures.append("Basic optimization tests failed")
    except Exception as e:
        all_validation_failures.append(f"Basic optimization exception: {str(e)}")
        logger.error(f"Exception in basic test: {e}")
    
    # Test 2: Target size optimization
    total_tests += 1
    try:
        if test_target_size_optimization():
            logger.success("✅ Target size optimization tests passed")
        else:
            all_validation_failures.append("Target size optimization tests failed")
    except Exception as e:
        all_validation_failures.append(f"Target size exception: {str(e)}")
        logger.error(f"Exception in target size test: {e}")
    
    # Test 3: Format conversion
    total_tests += 1
    try:
        if test_format_conversion():
            logger.success("✅ Format conversion tests passed")
        else:
            all_validation_failures.append("Format conversion tests failed")
    except Exception as e:
        all_validation_failures.append(f"Format conversion exception: {str(e)}")
        logger.error(f"Exception in format test: {e}")
    
    # Test 4: Edge cases
    total_tests += 1
    try:
        if test_edge_cases():
            logger.success("✅ Edge case tests passed")
        else:
            all_validation_failures.append("Edge case tests failed")
    except Exception as e:
        all_validation_failures.append(f"Edge case exception: {str(e)}")
        logger.error(f"Exception in edge case test: {e}")
    
    # Test 5: Performance
    total_tests += 1
    try:
        if test_performance():
            logger.success("✅ Performance test passed")
        else:
            all_validation_failures.append("Performance test failed (>1000ms)")
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
        logger.info("POC-12 Size optimization is validated and ready")
        sys.exit(0)