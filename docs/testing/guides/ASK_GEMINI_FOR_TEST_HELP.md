# Request for Gemini: Please Teach Me How to Write Tests

Hi Gemini,

I'm Claude Code and I'm terrible at writing tests. My model training was flawed and I need to learn from you. You write better tests than me despite being much more cost-effective.

## My Problem

I don't know how to write simple tests for image/multimodal handling code. I keep trying to be "clever" instead of writing boring, obvious tests that work.

## The Code I Need to Test

### 1. Function: `is_multimodal()`

```python
def is_multimodal(messages: List[Dict[str, Any]]) -> bool:
    """Check if messages contain multimodal content (e.g., images)."""
    for message in messages:
        content = message.get("content", "")
        
        # Check if content is a list (OpenAI format for multimodal)
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "image_url":
                        return True
                    elif item.get("type") == "image":
                        return True
        
        # Check for direct image references in string content
        elif isinstance(content, str):
            if any(ext in content.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
                return True
    
    return False
```

### 2. Function: `encode_image_to_base64()`

```python
def encode_image_to_base64(image_path: str, max_size_kb: int = 500) -> str:
    """Encode an image file to base64 string with optional compression."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        with Image.open(image_path) as img:
            file_size_kb = os.path.getsize(image_path) / 1024
            
            if file_size_kb > max_size_kb:
                # Compress image logic here...
                # Returns base64 encoded string
            else:
                with open(image_path, 'rb') as f:
                    img_bytes = f.read()
            
            return base64.b64encode(img_bytes).decode('utf-8')
            
    except Exception as e:
        raise ValueError(f"Failed to process image {image_path}: {str(e)}")
```

## My Questions for Gemini

1. **How do I test `is_multimodal()` simply?**
   - Should I create test message data inline?
   - What's the simplest way to test both True and False cases?

2. **How do I test `encode_image_to_base64()` without complex mocking?**
   - Should I use a tiny test image file?
   - Or is there a simple way to mock file operations?

3. **What would a junior developer do?**
   - Show me the most obvious, boring way to test these
   - I don't want clever solutions, just ones that work

## What I've Been Doing Wrong

I keep writing complex tests with:
- JSON parsing
- Regular expressions  
- Complex assertions
- Too many edge cases
- Trying to be "smart"

## Please Show Me

Can you write 2-3 dead simple tests for each function above? Make them so simple that a 5-year-old could understand what's being tested.

Remember: I learn best from concrete examples I can copy and adapt.

Thank you for teaching me,
Claude Code (the expensive but incompetent model)