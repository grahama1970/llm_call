# Ask Perplexity Command

Research this topic using Perplexity and return real-time information with sources: $ARGUMENTS

## Expected Output:
- Provide current, factual information with citations
- Include sources like [1], [2] for each claim
- If information is unavailable or uncertain, state clearly
- Focus on accuracy over completeness

## Code Example:
```python
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
from litellm import completion

model = os.getenv('SLASHCMD_ASK_PERPLEXITY_MODEL') # Gets configured Perplexity model
response = completion(
  model=model,
  messages=[{"role": "user", "content": "YOUR_RESEARCH_QUERY"}]
  # NOTE: No max_tokens - let Perplexity provide complete research results
  # Research queries need full context and citations
)
print(response.choices[0].message.content)
```

## Error Recovery Instructions:
**IMPORTANT**: If you encounter errors when implementing this template:

1. **ALWAYS DEBUG THE ACTUAL OUTPUT**: When Perplexity returns None or unexpected results:
  - Print the FULL response: `print("Full response:", response)`
  - Check content: `print("Content:", response.choices[0].message.content)`
  - Perplexity responses often include citations - ensure you handle them properly

2. **API Key issues**:
  - Verify key is set: `print(os.getenv('PERPLEXITY_API_KEY'))`
  - Check model name: `print(f"Model: {model}")`
  - Ensure key has proper permissions for the selected model

3. **Response formatting**:
  - Perplexity includes citations like [1], [2] in responses
  - May include source URLs at the end
  - Handle special formatting in the response

4. **MANDATORY: Update this template when you encounter issues**:
  - **API errors?** → Add the exact error and solution
  - **Citation parsing issues?** → Document how to handle them
  - **Model not available?** → List working model names
  - **Response format changes?** → Update examples with new format
  - Don't just work around problems - FIX THE TEMPLATE
  - Future versions will be git-tracked for rollback if needed

Example with full error handling:
```python
try:
  response = completion(
    model=model,
    messages=[{"role": "user", "content": query}]
    # No max_tokens - research needs complete results
  )
   
  if hasattr(response, 'choices') and len(response.choices) > 0:
    result = response.choices[0].message.content
    if result is None:
      print("ERROR: Perplexity returned None content")
      print(f"Full response: {response}")
    else:
      # Perplexity includes citations and sources
      print(result)
  else:
    print("ERROR: Invalid response structure from Perplexity")
     
except Exception as e:
  print(f"Error calling Perplexity: {type(e).__name__}: {str(e)}")
  if "API key" in str(e):
    print("Check PERPLEXITY_API_KEY environment variable")
  import traceback
  traceback.print_exc()
```

## Model Selection:
- **sonar-reasoning-pro**: For complex analytical research requiring deep thinking
- **sonar-pro**: For general-purpose research queries  
- **sonar-deep-research**: For comprehensive research requiring multiple sources
- **sonar**: For simple, quick lookups

## Parameters:
- `reasoning_effort="high"`: Use for complex analysis (requires LiteLLM v1.72.6+)
- Always include proper error handling
- Return actual results with sources, not hallucinated content

## Helpful Documentation:
*Read these if you get stuck or confused:*
- **Perplexity Setup**: https://docs.litellm.ai/docs/providers/perplexity
- **LiteLLM Completion**: https://docs.litellm.ai/docs/completion/quick_start
- **Reasoning Parameters**: https://docs.litellm.ai/docs/providers/perplexity#reasoning-effort

Usage: `/user:ask-perplexity today's weather forecast with analysis`