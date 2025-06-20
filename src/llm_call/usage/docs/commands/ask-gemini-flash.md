# Ask Gemini Flash Command

Ask Gemini Flash this question and get a quick, balanced response: $ARGUMENTS

## Expected Output:
- Provide clear, concise answers (limit ~500 tokens per answer/critque)
- Use creative but accurate tone
- For complex code tasks, suggest using ask-gemini-pro instead
- If unable to answer, explain why clearly

## Code Example:
```python
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
from litellm import completion

model = os.getenv('SLASHCMD_ASK_GEMINI_FLASH_MODEL')  # Gets configured Gemini Flash model
response = completion(
    model=model,
    messages=[{"role": "user", "content": "YOUR_QUERY"}],
    temperature=0.7  # Balanced creativity
    # NOTE: No max_tokens parameter - let Gemini decide response length
    # Especially important for critiques and detailed analysis
)
print(response.choices[0].message.content)
```

## Error Recovery Instructions:
**IMPORTANT**: If you encounter errors when implementing this template:

1. **ALWAYS DEBUG THE ACTUAL OUTPUT**: When Gemini returns None or unexpected results:
   - Print the FULL response object: `print("Full response:", response)`
   - Check finish_reason: `print("Finish reason:", response.choices[0].finish_reason)`
   - If finish_reason='length', you hit token limit - REMOVE max_tokens parameter
   - Check the actual content: `print("Content:", response.choices[0].message.content)`
   - Look at token usage: `print("Tokens used:", response.usage)`

2. **Check for None responses**: If `response.choices[0].message.content` returns None:
   - This often means token limit was hit (finish_reason='length')
   - For critiques/validation: NEVER use max_tokens - let Gemini decide response length
   - Simple debug: `result = response.choices[0].message.content or f"ERROR: None (finish_reason={response.choices[0].finish_reason})"`

2. **API errors**: If you get authentication or API errors:
   - Verify environment variables are loaded: `print(f"Model: {model}")`
   - Check credentials: `print(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))`
   - Add try-except block with detailed error logging

3. **MANDATORY: Update this template when you encounter issues**:
   - **When you hit an error/ambiguity**: IMMEDIATELY edit this file after fixing it
   - **Document the fix**: Add comments like `# Fixed: max_tokens caused None responses`
   - **Add your working solution**: Replace broken examples with what actually worked
   - **Common fixes to add**:
     - Ambiguous instructions → Clarify with specific steps
     - Missing error handling → Add the handling that worked
     - Wrong assumptions → Correct them with facts
   - **Example**: Today I learned max_tokens=500 causes finish_reason='length' and None responses
   - Future versions will be git-tracked for rollback if needed

4. **Never simulate API calls**: 
   - This template is for REAL API calls to Gemini
   - If you see simulation code, that's an error - update the template
   - The purpose is actual external validation, not pretending

Example with full error handling:
```python
try:
    response = completion(
        model=model,
        messages=[{"role": "user", "content": query}],
        temperature=0.7,
        # NOTE: No max_tokens parameter - let Gemini decide response length
        # Especially important for critiques and detailed analysis
    )
    
    if hasattr(response, 'choices') and len(response.choices) > 0:
        result = response.choices[0].message.content
        if result is None:
            print("ERROR: Gemini returned None content")
            # Update this template if this happens frequently
        else:
            print(result)
    else:
        print("ERROR: Invalid response structure")
        
except Exception as e:
    print(f"Error calling Gemini: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
```

## Model Information:
- **Configured Model**: The environment variable `SLASHCMD_ASK_GEMINI_FLASH_MODEL` determines the actual model
- **Common Models**: 
  - `vertex_ai/gemini-2.5-flash`: Stable version of Gemini Flash
  - `vertex_ai/gemini-2.5-flash-preview-05-20`: Preview version with enhanced capabilities
- **Good for**: Code generation, analysis, general questions, quick responses, detailed critiques
- **Features**: Multi-modal support, function calling, safety settings, extended context windows

## Environment Requirements:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON file
- `VERTEX_PROJECT`: Google Cloud project ID (optional, can be in credentials)
- `VERTEX_LOCATION`: Region like 'us-central1' (optional)

## Helpful Documentation:
- **Vertex AI Setup**: https://docs.litellm.ai/docs/providers/vertex
- **Gemini Models**: https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini
- **Authentication**: https://cloud.google.com/docs/authentication/getting-started

## Usage Examples:
- `/user:ask-gemini-flash Write a Python function to calculate fibonacci`
- `/user:ask-gemini-flash Explain quantum computing in simple terms`
- `/user:ask-gemini-flash Debug this code: [paste code]`

## Notes:
- Ensure Google Cloud credentials are properly configured
- Flash model is optimized for speed and cost-efficiency
- For complex reasoning tasks, consider using gemini-2.5-pro instead