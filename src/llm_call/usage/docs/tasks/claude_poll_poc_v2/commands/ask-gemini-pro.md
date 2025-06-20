# Ask Gemini Pro Command

Ask Gemini Pro to analyze, review, or generate complex code.

## Parameters:
- `query`: (string) The full text of the complex question/analysis request for Gemini Pro
- `output_path`: (string) The file path where the Gemini Pro response should be saved

## Expected Output:
- Provide detailed, thorough code analysis or generation
- Include best practices, error handling, and optimization suggestions
- Use lower temperature for precise, consistent code
- For simple tasks, suggest using ask-gemini-flash instead

## Code Example:
```python
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
from litellm import completion

model = os.getenv('SLASHCMD_ASK_GEMINI_PRO_MODEL') # Gets configured Gemini Pro model
response = completion(
  model=model,
  messages=[{"role": "user", "content": """{{ params.query }}"""}],
  temperature=0.3 # Lower temperature for more precise code
  # NOTE: No max_tokens parameter - let Gemini Pro decide response length
  # Gemini Pro is designed for detailed analysis and should not be limited
)
print(response.choices[0].message.content)
```

## Error Recovery Instructions:
**IMPORTANT**: If you encounter errors when implementing this template:

1. **ALWAYS DEBUG THE ACTUAL OUTPUT**: When Gemini Pro returns None or unexpected results:
  - Print the FULL response object: `print("Full response:", response)`
  - Check finish_reason: `print("Finish reason:", response.choices[0].finish_reason)`
  - If finish_reason='length', you hit token limit - REMOVE max_tokens parameter
  - Check the actual content: `print("Content:", response.choices[0].message.content)`
  - Look at token usage: `print("Tokens used:", response.usage)`

2. **Check for None responses**: If `response.choices[0].message.content` returns None:
  - This often means token limit was hit (finish_reason='length')
  - For code reviews and analysis: NEVER use max_tokens - let Gemini Pro provide complete analysis
  - Debug with: `result = response.choices[0].message.content or f"ERROR: None (finish_reason={response.choices[0].finish_reason})"`

3. **MANDATORY: Update this template when you encounter issues**:
  - **When you hit an error/ambiguity**: IMMEDIATELY edit this file after fixing it
  - **Document the fix**: Add comments like `# Fixed: max_tokens limited detailed analysis`
  - **Add your working solution**: Replace broken examples with what actually worked
  - **Track your learnings**: Each fix makes the template better for next time
  - Future versions will be git-tracked for rollback if needed

Example with full error handling:
```python
try:
  response = completion(
    model=model,
    messages=[{"role": "user", "content": query}],
    temperature=0.3
    # NO max_tokens - let Gemini Pro provide complete analysis
  )
   
  if hasattr(response, 'choices') and len(response.choices) > 0:
    result = response.choices[0].message.content
    if result is None:
      print(f"ERROR: Gemini Pro returned None (finish_reason={response.choices[0].finish_reason})")
      print(f"Full response: {response}")
    else:
      print(result)
  else:
    print("ERROR: Invalid response structure")
     
except Exception as e:
  print(f"Error calling Gemini Pro: {type(e).__name__}: {str(e)}")
  import traceback
  traceback.print_exc()
```

## Model Information:
- **Configured Model**: The environment variable `SLASHCMD_ASK_GEMINI_PRO_MODEL` determines the actual model
- **Common Models**:
 - `vertex_ai/gemini-2.5-pro`: Stable version
 - `vertex_ai/gemini-2.5-pro-preview-06-05`: Advanced version with enhanced capabilities
- **Best for**: Complex code generation, code reviews, debugging, architecture analysis, detailed critiques
- **Features**: Advanced reasoning, multi-modal support, function calling, detailed code analysis

## Environment Requirements:
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account JSON file
- `VERTEX_PROJECT`: Google Cloud project ID (optional, can be in credentials)
- `VERTEX_LOCATION`: Region like 'us-central1' (optional)

## Helpful Documentation:
*Read these if you get stuck or confused:*
- **Vertex AI Setup**: https://docs.litellm.ai/docs/providers/vertex
- **Gemini Models**: https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/gemini
- **Authentication**: https://cloud.google.com/docs/authentication/getting-started

## Usage Examples:
- `/user:ask-gemini-pro Review this Python class for best practices`
- `/user:ask-gemini-pro Debug this function that's causing memory leaks`
- `/user:ask-gemini-pro Refactor this code to be more efficient`
- `/user:ask-gemini-pro Write unit tests for this API endpoint`

## Notes:
- Pro model is more powerful but slower than Flash
- Optimized for complex reasoning and detailed code analysis
- Use for code reviews, debugging, and architectural decisions
- For simple code generation, consider ask-gemini-flash instead