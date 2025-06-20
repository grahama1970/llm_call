# Ask Ollama Command

Ask a local Ollama model this question, automatically selecting the best available model: $ARGUMENTS

## Important Implementation Notes:
When implementing this template, you should:
1. **Customize the system prompt** based on the user's actual request to get better results from Ollama
2. **Select the appropriate model** - the template includes basic automatic selection, but you should:
   - **Check what models are actually available** before making selection decisions
   - **Adapt the selection logic** in the `select_model` function based on available models
   - **Override when needed**: After automatic selection, you can still override with `selected_model = "specific-model"`
   - **Consider the task**: Code tasks → codellama, Math → specialized math models, General → balanced models
   - **Don't assume specific models exist** - the template's examples may not match your available models
3. **Replace the basic keyword matching** with more sophisticated logic based on what the user is asking

For example, if the user asks "debug this complex Python function":
- First check what models you have available
- If you see a code-specialized model (look for 'code' in the name), consider using it
- Create an appropriate system prompt for debugging

If the user asks "explain quantum computing simply":
- Consider what models are available and their sizes
- Smaller models might be fine for simple explanations
- Focus on crafting a good system prompt for clear explanations

If the user specifically requests a model:
- Check if that model (or similar) exists in available_models
- Honor their request if possible
- If not available, explain what you're using instead

Remember: Don't assume specific models exist. Always work with what's actually available.

## Expected Output:
- Choose appropriate model based on query complexity (simple questions use smaller/faster models)
- Check available models first and report which one was selected
- Provide helpful responses using local model (no internet required)
- Responses are private and processed locally
- If specific model requested, use that if available

## Code Example:
```python
from dotenv import load_dotenv
load_dotenv('/home/graham/workspace/experiments/llm_call/.env')
import os
import sys
import subprocess
from litellm import completion

# Step 1: Get available models from Docker container
def get_available_models():
    try:
        container_name = os.getenv('OLLAMA_DOCKER_CONTAINER', 'llm-call-ollama')
        result = subprocess.run(['docker', 'exec', container_name, 'ollama', 'list'],
                                capture_output=True, text=True, check=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            return [line.split()[0] for line in lines if line.strip()]
        return []
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting models from Docker container '{container_name}': {e}", file=sys.stderr)
        print("Please ensure Docker is running and the 'docker' command is in your system's PATH.", file=sys.stderr)
        return []

# Step 2: Select best model for query
def select_model(query, available_models):
    # Default fallback model
    default_model_name = os.getenv('SLASHCMD_ASK_OLLAMA_MODEL', 'ollama/phi3:mini')
    default_model = default_model_name.replace('ollama/', '') if default_model_name.startswith('ollama/') else default_model_name

    if not available_models:
        return default_model

    query_lower = query.lower()
    
    # Dynamically check if the user's query mentions an available model family.
    for model in available_models:
        # Extract the base name (e.g., 'llama3:8b-instruct' -> 'llama3')
        base_name = model.split(':')[0]
        if base_name in query_lower:
            # The user's query requests a model family that is installed.
            print(f"--- Detected manual model request for '{base_name}' ---")
            return model # Return the full model name, e.g., 'llama3:8b-instruct'
    
    # If no manual override was found, auto-select based on keywords
    complex_keywords = ['analyze', 'explain', 'complex', 'detailed', 'comprehensive', 'algorithm', 'review', 'debug', 'refactor']
    is_complex = any(keyword in query_lower for keyword in complex_keywords)
    
    # AGENT: Replace this entire section with logic appropriate for your available models
    # and the user's specific request. Consider:
    # - What models are actually available? (check available_models list)
    # - What is the user asking for? (analyze the query)
    # - Which available model would best serve this request?
    
    # This is just placeholder logic - DO NOT use it as-is
    # Instead, write selection logic based on:
    # 1. The actual models you see in available_models
    # 2. The specific nature of the user's query
    # 3. Any explicit model requests from the user
    
    # For now, return first available model as a fallback
    if available_models:
        return available_models[0]
    
    # Final fallback to the default model if no other logic matches
    return default_model

# Step 3: Execute query
def main(query):
    available_models = get_available_models()

    # Special case: if user wants to list models, just show them
    if any(keyword in query.lower() for keyword in ['list models', 'available models', 'show models']):
        if available_models:
            print("Available Ollama models:")
            for model in available_models:
                print(f"- {model}")
        else:
            print("Could not retrieve model list. Is the Ollama Docker container running?")
        return

    selected_model = select_model(query, available_models)
    
    # AGENT: You can override the automatic model selection here if needed
    # Example: selected_model = "codellama:13b-instruct-q8_0" for complex code tasks
    # Example: selected_model = "qwen2.5:32b" for tasks requiring deep reasoning
    
    print(f"--- Using model: {selected_model} ---")
    
    try:
        api_base = os.getenv('OLLAMA_API_BASE_URL', 'http://localhost:11434')
        
        # Build messages with optional system prompt
        messages = []
        
        # Add system prompt if needed (can be customized based on model/task)
        system_prompt = os.getenv('OLLAMA_SYSTEM_PROMPT', 'You are a helpful AI assistant.')
        
        # The agent implementing this template should customize the system prompt
        # based on the user's actual request for better results
        if 'code' in query.lower() or 'debug' in query.lower():
            system_prompt = "You are an expert programmer. Provide clear, concise code solutions."
        elif 'explain' in query.lower():
            system_prompt = "You are a patient teacher. Explain concepts clearly and simply."
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user query
        messages.append({"role": "user", "content": query})
        
        response = completion(
            model=f"ollama/{selected_model}",
            messages=messages,
            api_base=api_base,
            temperature=0.7
        )
        
        if hasattr(response, 'choices') and len(response.choices) > 0:
            result = response.choices[0].message.content
            if result is None:
                print(f"ERROR: Ollama returned None content. Finish Reason: {response.choices[0].finish_reason}", file=sys.stderr)
            else:
                print(result)
        else:
            print("ERROR: Invalid response structure from Ollama.", file=sys.stderr)
            print(f"Full response object: {response}", file=sys.stderr)

    except Exception as e:
        print(f"Error calling Ollama: {type(e).__name__}: {str(e)}", file=sys.stderr)
        print(f"Attempted model: ollama/{selected_model}", file=sys.stderr)
        print("Check if Ollama container is running and the model is downloaded.", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # This block makes the generated script a robust command-line utility.
    if len(sys.argv) < 2:
        print("Usage: python <script_name>.py \"<your query>\"", file=sys.stderr)
        # Provide a default example query for testing or if run without args.
        print("\nRunning with default example query...", file=sys.stderr)
        user_query = "What is the capital of France?"
    else:
        user_query = " ".join(sys.argv[1:])
    
    main(user_query)
```

## Error Recovery Instructions:
**IMPORTANT**: If you encounter errors when implementing this template:

1. **FIRST - Interactively debug the Docker container**:
   ```bash
   # Check if container is running
   docker ps | grep ollama
   
   # If not running, check all containers
   docker ps -a | grep ollama
   
   # Start container if stopped
   docker start llm-call-ollama
   
   # Get interactive shell in container to debug
   docker exec -it llm-call-ollama /bin/bash
   
   # Inside container, test Ollama directly:
   ollama list         # See available models
   ollama run phi3:mini  # Test a model interactively
   exit                # Exit container shell
   ```

2. **Model issues - Debug interactively**:
   ```bash
   # List models from outside container
   docker exec ll-call-ollama ollama list
   
   # If model missing, pull it
   docker exec llm-call-ollama ollama pull phi3:mini
   ```

3. **MANDATORY: Update this template when you encounter issues**:
   - **When you hit an error or ambiguity**: IMMEDIATELY edit THIS file after fixing the generated script.
   - **Document the fix**: Add comments like `# Fixed: subprocess check=True for better error handling`.
   - **Add your working solution**: Replace broken examples with what actually worked.
   - Each debugging session should improve this template for the next run.

## Environment Requirements:
- `OLLAMA_API_BASE_URL`: Base URL for Ollama API (default: http://localhost:11434)
- `OLLAMA_DOCKER_CONTAINER`: Docker container name (default: llm-call-ollama)
- `SLASHCMD_ASK_OLLAMA_MODEL`: Default model to use (default: ollama/phi3:mini)
- `OLLAMA_SYSTEM_PROMPT`: Optional system prompt (default: "You are a helpful AI assistant.")
  - Set to empty string to disable system prompt
  - Can be customized for specific use cases

## Notes:
- Ensure the Ollama Docker container is running and accessible at the URL specified in OLLAMA_API_BASE_URL
- The agent should generate a script from the `Code Example` and then execute it by passing the user's query as a command-line argument (e.g., `python generated_script.py "List available models"`).
