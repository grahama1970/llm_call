# src/llm_call/proof_of_concept/litellm_client_poc.py

import asyncio
import httpx
import litellm
import json
import os
import copy # For deepcopy
from typing import Dict, Any, Union, Optional, List
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path

# --- CORE IMPORTS ---
from llm_call.core.base import ValidationResult, AsyncValidationStrategy
# Import from the PoC retry manager - use absolute imports
from llm_call.proof_of_concept.poc_retry_manager import retry_with_validation_poc as retry_with_validation, PoCRetryConfig as RetryConfig, PoCHumanReviewNeededError
from tenacity import RetryError # For catching if retry_with_validation re-raises it (should ideally be PoCHumanReviewNeededError)


# --- PoC VALIDATOR IMPORTS ---
# Using absolute imports as per CLAUDE.md standards
from llm_call.proof_of_concept.poc_validation_strategies import (
    PoCResponseNotEmptyValidator,
    PoCJsonStringValidator,
    PoCFieldPresentValidator,
    PoCAgentTaskValidator,
    PoCAIContradictionValidator,
    poc_strategy_registry # The dict mapping names to classes
)

# --- UTILITY IMPORTS ---
from llm_call.core.utils.multimodal_utils import format_multimodal_messages, is_multimodal
from llm_call.core.utils.initialize_litellm_cache import initialize_litellm_cache

# --- Client Configuration ---
FASTAPI_PROXY_URL = "http://127.0.0.1:3010/v1/chat/completions" # For 'max/' models
# DEFAULT_PROXY_MODEL_REQUEST_LABEL = "max/poc-claude-default" # This is defined in prepare_payload_for_proxy

# Configure logger
logger.remove()
logger.add(lambda msg: print(msg, end=""), colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>", level="INFO")

# Global reference for recursive calls by AI validators (PoC hack)
_recursive_llm_caller: Optional[callable] = None

# --- 1. Routing and Parameter Preparation ---
def determine_llm_route_and_params(llm_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Determines the route, prepares messages (JSON instruction, multimodal), and parameters.
    Returns a dictionary structured for the main llm_call function.
    """
    model_name_original = llm_config.get("model", "")
    model_name_lower = model_name_original.lower()

    if not model_name_original:
        raise ValueError("❌ 'model' field is required in llm_config.")

    original_messages = llm_config.get("messages", [])
    if not original_messages:
        raise ValueError("❌ 'messages' field is required in llm_config.")

    processed_messages = copy.deepcopy(original_messages)
    response_format_config = llm_config.get("response_format")
    requires_json = isinstance(response_format_config, dict) and response_format_config.get("type") == "json_object"

    if requires_json:
        logger.info("📝 JSON response format requested. Modifying system prompt if necessary.")
        system_messages = [msg for msg in processed_messages if msg.get("role") == "system"]
        json_instruction = "You MUST respond with a valid JSON object. Do not include any text outside of the JSON structure."
        if not system_messages:
            processed_messages.insert(0, {"role": "system", "content": json_instruction})
        else:
            system_content = system_messages[0].get("content", "")
            if "json object" not in system_content.lower() and "valid json" not in system_content.lower():
                system_messages[0]["content"] = f"{json_instruction} {system_content}".strip()

    is_multimodal_request = is_multimodal(processed_messages)

    # Base parameters for the execution function. These will form the **kwargs for the llm_call_func
    # passed to retry_with_validation.
    execution_kwargs = llm_config.copy() # Start with all original config items
    # Remove keys that are for llm_call orchestration, not the actual API call
    execution_kwargs.pop("validation", None)
    execution_kwargs.pop("retry_config", None)
    execution_kwargs.pop("default_validate", None)
    execution_kwargs.pop("max_attempts_before_tool_use", None)
    execution_kwargs.pop("max_attempts_before_human", None)
    execution_kwargs.pop("debug_tool_name", None)
    execution_kwargs.pop("debug_tool_mcp_config", None)
    execution_kwargs.pop("original_user_prompt", None) # If it was added for validators

    # Messages will be handled by format_multimodal_messages if needed, then passed directly
    # to retry_with_validation, which passes it to the execution_kwargs.
    # So, ensure 'messages' in execution_kwargs is the final processed_messages.

    if model_name_lower.startswith("max/"):
        if is_multimodal_request:
            logger.warning(f"🖼️ Multimodal request for '{model_name_original}'. Claude CLI (via proxy) does not support image inputs. Skipping call.")
            return {"route_type": "skip_claude_multimodal", "processed_messages": processed_messages, "llm_call_kwargs": {}, "model_name_original": model_name_original}
        
        # Specific defaults for proxy if not overridden by user in llm_config
        execution_kwargs["temperature"] = llm_config.get("temperature", 0.1)
        execution_kwargs["max_tokens"] = llm_config.get("max_tokens", 250)
        execution_kwargs["messages"] = processed_messages # Ensure proxy gets correctly pre-processed messages

        # image_directory and max_image_size_kb are not for the proxy payload
        execution_kwargs.pop("image_directory", None)
        execution_kwargs.pop("max_image_size_kb", None)
        
        logger.info(f"➡️ Determined route: PROXY for model '{model_name_original}'")
        return {"route_type": "proxy", 
                "processed_messages": processed_messages, 
                "llm_call_kwargs": execution_kwargs, 
                "proxy_url": FASTAPI_PROXY_URL, 
                "model_name_original": model_name_original}
    else: # Standard LiteLLM calls
        if is_multimodal_request:
            logger.info(f"🖼️ Multimodal content detected for LiteLLM call '{model_name_original}'. Formatting messages...")
            image_directory = llm_config.get("image_directory", "") 
            max_size_kb = llm_config.get("max_image_size_kb", 500)
            
            needs_image_dir = any(
                isinstance(item, dict) and item.get("type") == "image_url" and 
                not (item.get("image_url", {}).get("url", "").startswith(("data:", "http:", "https:")) or 
                     Path(item.get("image_url", {}).get("url", "")).is_absolute())
                for msg_content_list in (m.get("content") for m in processed_messages) if isinstance(msg_content_list, list)
                for item in msg_content_list
            )
            if needs_image_dir and not image_directory:
                 logger.warning("📸 Multimodal content with relative image paths detected, but 'image_directory' not specified in llm_config.")
            
            processed_messages = format_multimodal_messages(processed_messages, image_directory, max_size_kb)
        
        execution_kwargs["messages"] = processed_messages

        execution_kwargs.pop("image_directory", None)
        execution_kwargs.pop("max_image_size_kb", None)
        execution_kwargs.pop("mcp_config", None) 
        
        logger.info(f"➡️ Determined route: LITELLM for model '{model_name_original}'")
        if model_name_lower.startswith("vertex_ai/"):
            if "vertex_project" not in execution_kwargs:
                project = os.getenv("LITELLM_VERTEX_PROJECT", os.getenv("GOOGLE_CLOUD_PROJECT"))
                if project: execution_kwargs["vertex_project"] = project
            if "vertex_location" not in execution_kwargs:
                location = os.getenv("LITELLM_VERTEX_LOCATION", os.getenv("GOOGLE_CLOUD_REGION"))
                if location: execution_kwargs["vertex_location"] = location
        
        return {"route_type": "litellm", 
                "processed_messages": processed_messages, 
                "llm_call_kwargs": execution_kwargs, 
                "model_name_original": model_name_original}

# --- 2. Actual API Call Execution Functions (NO Tenacity Decorator here) ---
async def _execute_proxy_call_for_retry_loop(messages: List[Dict[str, str]], response_format: Optional[Any] = None, **kwargs) -> Dict[str, Any]:
    """Makes the HTTPX call to the proxy. Signature matches retry_with_validation's llm_call_func."""
    proxy_url = kwargs.pop("proxy_url_actual", FASTAPI_PROXY_URL)
    # Construct payload: model, temp, max_tokens, mcp_config etc. are already in kwargs
    payload = {"messages": messages, **kwargs} 
    if response_format: 
        payload["response_format"] = response_format

    logger.debug(f"📞 Attempting PROXY call to {proxy_url}. Payload: {json.dumps(payload, indent=2, default=str)}")
    async with httpx.AsyncClient() as client:
        response = await client.post(proxy_url, json=payload, timeout=120.0)
    response.raise_for_status() 
    logger.debug(f"✅ PROXY call attempt successful (status: {response.status_code})")
    return response.json()

async def _execute_litellm_call_for_retry_loop(messages: List[Dict[str, str]], response_format: Optional[Any] = None, **kwargs) -> litellm.ModelResponse:
    """Makes the LiteLLM call. Signature matches retry_with_validation's llm_call_func."""
    api_params = {"messages": messages, **kwargs} # kwargs already contains model, temp, etc.
    if response_format:
        api_params["response_format"] = response_format
    
    model_being_called = api_params.get("model", "unknown_model")
    logger.debug(f"📞 Attempting LITELLM call to '{model_being_called}'. Params (excluding messages): "
                 f"{json.dumps({k: v for k, v in api_params.items() if k != 'messages'}, indent=2, default=str)}")
    logger.trace(f"Messages for '{model_being_called}': {json.dumps(api_params['messages'], indent=2, default=str)}")

    response = await litellm.acompletion(**api_params) # Use acompletion
    logger.debug(f"✅ LITELLM call attempt successful for '{model_being_called}'.")
    return response

# --- 3. Main Orchestrating Function (llm_call) using PoC Retry Manager ---
async def llm_call(llm_config_input: Dict[str, Any]) -> Union[Dict[str, Any], litellm.ModelResponse, None]:
    global _recursive_llm_caller
    if _recursive_llm_caller is None:
        _recursive_llm_caller = llm_call 
        
    model_name_for_logging = llm_config_input.get('model', 'N/A')
    try:
        if not llm_config_input:
            logger.error("❌ 'llm_config_input' (user input) cannot be empty.")
            return None
        
        # Handle "question" format (convert to messages)
        if "question" in llm_config_input and "messages" not in llm_config_input:
            question = llm_config_input.pop("question")
            llm_config_input["messages"] = [
                {"role": "user", "content": question}
            ]
            logger.debug(f"Converted 'question' to 'messages' format")
            
        route_info = determine_llm_route_and_params(llm_config_input)
        
        if route_info["route_type"] == "skip_claude_multimodal":
            return {"error": f"Claude CLI (via proxy for model '{route_info['model_name_original']}') does not support multimodal image inputs.", 
                    "model": route_info['model_name_original']}

        actual_llm_call_func: Optional[callable] = None
        # kwargs_for_retry_loop are the specific parameters for the execution function
        kwargs_for_retry_loop = route_info["llm_call_kwargs"].copy() 
        kwargs_for_retry_loop.pop("messages", None)  # Remove messages since we pass it explicitly

        if route_info["route_type"] == "proxy":
            actual_llm_call_func = _execute_proxy_call_for_retry_loop
            # Add proxy_url_actual for the _execute_proxy_call_for_retry_loop to use,
            # it's not a direct LLM param so it was popped from execution_kwargs if it was there.
            # It's passed in route_info now.
            kwargs_for_retry_loop["proxy_url_actual"] = route_info["proxy_url"]
        elif route_info["route_type"] == "litellm":
            actual_llm_call_func = _execute_litellm_call_for_retry_loop
        else:
            logger.error(f"🚨 Unknown route type: {route_info.get('route_type')} for model '{model_name_for_logging}'")
            return None

        validation_config_list = llm_config_input.get("validation", [])
        if not isinstance(validation_config_list, list):
            validation_config_list = [validation_config_list] if validation_config_list else []
            
        active_validation_strategies: List[AsyncValidationStrategy] = []
        if validation_config_list:
            logger.info(f"Found {len(validation_config_list)} validation configs for '{model_name_for_logging}'.")
        for val_conf in validation_config_list:
            if not isinstance(val_conf, dict): 
                logger.warning(f"Skipping invalid validation config item (not a dict): {val_conf}")
                continue
            strategy_type_name = val_conf.get("type")
            strategy_params = val_conf.get("params", {})
            
            ValidatorClass = poc_strategy_registry.get(strategy_type_name)
            if ValidatorClass:
                try:
                    validator_instance = ValidatorClass(**strategy_params)
                    if hasattr(validator_instance, "set_llm_caller") and _recursive_llm_caller:
                         validator_instance.set_llm_caller(_recursive_llm_caller) 
                    active_validation_strategies.append(validator_instance)
                    logger.info(f"Loaded validator for '{model_name_for_logging}': {strategy_type_name} with params: {strategy_params}")
                except Exception as e_val_init:
                    logger.error(f"Failed to instantiate validator '{strategy_type_name}' with params {strategy_params} for '{model_name_for_logging}': {e_val_init}")
            else:
                logger.warning(f"Unknown validation strategy type: '{strategy_type_name}' for model '{model_name_for_logging}'")
        
        if not active_validation_strategies and llm_config_input.get("default_validate", True):
             logger.info(f"No specific validators for '{model_name_for_logging}', adding default PoCResponseNotEmptyValidator.")
             active_validation_strategies.append(PoCResponseNotEmptyValidator())

        # Retry Configuration using PoCRetryConfig
        retry_settings_from_config = llm_config_input.get("retry_config", {})
        # Propagate debug_mode from main llm_config if not in retry_config sub-dict
        if "debug_mode" not in retry_settings_from_config and "debug_mode" in llm_config_input:
            retry_settings_from_config["debug_mode"] = llm_config_input["debug_mode"]
        
        current_poc_retry_config = RetryConfig(**retry_settings_from_config)

        # Pass original_llm_config and other specific kwargs needed by retry_with_validation_poc
        # This is for the staged retry logic (tool use, human escalation).
        # kwargs_for_retry_loop already contains model, temp, max_tokens, mcp_config (for proxy).
        # We add specific thresholds for the retry stages here.
        retry_control_params = {
            "max_attempts_before_tool_use": llm_config_input.get("max_attempts_before_tool_use"),
            "max_attempts_before_human": llm_config_input.get("max_attempts_before_human"),
            "debug_tool_name": llm_config_input.get("debug_tool_name"),
            "debug_tool_mcp_config": llm_config_input.get("debug_tool_mcp_config")
        }
        # Filter out None values from retry_control_params before merging
        # Note: retry_control_params are passed via original_llm_config, not as LLM API params
        # Extract response_format to pass it explicitly (avoiding duplicate keyword argument)
        response_format_value = kwargs_for_retry_loop.pop("response_format", None)

        final_response = await retry_with_validation(
            llm_call_func=actual_llm_call_func,
            messages=route_info["processed_messages"],
            response_format=response_format_value,
            validation_strategies=active_validation_strategies,
            config=current_poc_retry_config,
            original_llm_config=llm_config_input,
            **kwargs_for_retry_loop
        )
        return final_response
            
    except ValueError as ve: 
        logger.error(f"Configuration error for model '{model_name_for_logging}': {ve}")
    except PoCHumanReviewNeededError as hrne: 
        logger.error(f"🚫 HUMAN REVIEW NEEDED for model '{model_name_for_logging}': {hrne.args[0]}") # hrne.args[0] is the message
        # Log more details if needed, hrne.last_response and hrne.validation_errors are available
        return {"error": "Human review needed", "details": str(hrne.args[0]), 
                "last_response": hrne.last_response, 
                "validation_errors": [ve.error for ve in hrne.validation_errors if hasattr(ve, 'error')]}
    except RetryError as re_outer: # Fallback if tenacity retries (within _execute_... if any) are re-raised
        final_exception = re_outer.last_attempt.exception()
        logger.error(f"❌ Call for model '{model_name_for_logging}' FAILED AFTER MAX RETRIES (Tenacity outer loop).")
        logger.error(f"   Last exception type: {type(final_exception).__name__}")
        logger.error(f"   Last exception details: {final_exception}")
    except Exception as e:
        logger.error(f"💥 Unexpected error in llm_call orchestrator for model '{model_name_for_logging}': {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
    return None

# --- Main Execution Block for Client ---
async def main_client_runner():
    load_dotenv() 
    try:
        initialize_litellm_cache()
    except Exception as e: # Catch any exception from cache init
        logger.warning(f"LiteLLM cache initialization failed or was skipped: {e}")
    
    litellm.set_verbose = False 

    # --- Test Case 1: Claude Max Proxy Call (Text) with Basic Validation ---
    logger.info("\n--- Test Case 1: Claude Max Proxy Call with Validation ---")
    claude_text_config = {
        "model": "max/text-generation", 
        "messages": [
            {"role": "system", "content": "You are Claude. Be brief and answer the question."},
            {"role": "user", "content": "What is your name?"}
        ], 
        "temperature": 0.1, "max_tokens": 100,
        "validation": [{"type": "response_not_empty"}]
    }
    claude_response = await llm_call(claude_text_config)
    if claude_response and isinstance(claude_response, dict):
        if "error" in claude_response: 
            logger.warning(f"Claude proxy call info: {claude_response['error']} for model {claude_response.get('model')}")
        elif claude_response.get("choices"):
            content = claude_response["choices"][0].get("message", {}).get("content", "N/A")
            print(f"💬 Claude (via proxy) says: '{content}'")
        else: print(f"Raw/Unexpected response from proxy: {json.dumps(claude_response, indent=2)}")
    else: logger.info(f"No valid response or error from Claude proxy call (Test Case 1). Final: {claude_response}")

    logger.info("-" * 70)

    # --- Test Case 2: Vertex AI Gemini Call for JSON with Multiple Validations ---
    logger.info("\n--- Test Case 2: Vertex AI Gemini Call for JSON with Validation ---")
    gemini_json_config = {
        "model": "vertex_ai/gemini-1.5-flash-001", 
        "messages": [{"role": "user", "content": "Provide user details for Jane Doe, age 28, favorite color green, as a JSON object."}],
        "temperature": 0.1, "max_tokens": 250,
        "response_format": {"type": "json_object"}, 
        "validation": [
            {"type": "response_not_empty"}, {"type": "json_string"},
            {"type": "field_present", "params": {"field_name": "name"}},
            {"type": "field_present", "params": {"field_name": "age"}}
        ]
    }
    gemini_response_obj = await llm_call(gemini_json_config) 
    if gemini_response_obj and isinstance(gemini_response_obj, litellm.ModelResponse):
        try:
            content_str = gemini_response_obj.choices[0].message.content
            print(f"💬 Gemini (JSON) says:\n{json.dumps(json.loads(content_str), indent=2)}")
        except Exception as e: logger.error(f"Could not parse/print Gemini JSON response: {e}")
    else: logger.info(f"No valid response or error from Gemini call (Test Case 2). Final: {gemini_response_obj}")

    logger.info("-" * 70)
    
    # --- Test Case 3: Multimodal LiteLLM Call (openai/gpt-4o-mini) ---
    # (Assuming dummy image setup as before)
    logger.info("\n--- Test Case 3: Multimodal LiteLLM Call (openai/gpt-4o-mini) ---")
    current_script_dir = Path(__file__).parent.resolve() 
    image_dir_for_poc = current_script_dir / "test_images_poc"
    image_dir_for_poc.mkdir(exist_ok=True)
    dummy_image_path = image_dir_for_poc / "dummy_image.png" 
    if not dummy_image_path.exists():
        try: from PIL import Image; Image.new('RGB', (60,30), color='deepskyblue').save(dummy_image_path); logger.info(f"Created {dummy_image_path}")
        except: logger.warning("Pillow not installed or failed to create dummy image for Test Case 3.")

    if os.getenv("OPENAI_API_KEY") and dummy_image_path.exists():
        multimodal_config_openai = {
            "model": "openai/gpt-4o-mini", 
            "messages": [{"role": "user", "content": [{"type": "text", "text": "Describe this image briefly."}, {"type": "image_url", "image_url": {"url": str(dummy_image_path.resolve())}}]}],
            "max_tokens": 100, 
            "image_directory": str(image_dir_for_poc.resolve()),
            "validation": [{"type": "response_not_empty"}]
        }
        multimodal_response = await llm_call(multimodal_config_openai)
        if multimodal_response and isinstance(multimodal_response, litellm.ModelResponse):
            try:
                content = multimodal_response.choices[0].message.content
                print(f"💬 GPT-4o-mini (multimodal) says: '{content}'")
            except Exception as e: logger.error(f"Could not parse multimodal LiteLLM response: {e}")
        elif multimodal_response and "error" in multimodal_response:
             logger.warning(f"Multimodal call info: {multimodal_response['error']}")
        else: logger.info(f"No valid response or error from multimodal call (Test Case 3). Final: {multimodal_response}")
    else: logger.warning("Skipping Multimodal OpenAI test (Test Case 3): OPENAI_API_KEY not set or dummy image not found.")

    logger.info("-" * 70)

    # --- Test Case 6: Iterative Code Gen (from previous example) ---
    logger.info("\n--- Test Case 6: Iterative Code Gen with Tool-Assisted Debug & Human Escalation ---")
    # ... (Test Case 6 definition as in previous message, ensuring "max_attempts_before_tool_use",
    #      "max_attempts_before_human", "debug_tool_name", "debug_tool_mcp_config", and
    #      "original_user_prompt" are correctly included in code_generation_llm_config) ...
    # ... (and handle its response appropriately, checking for PoCHumanReviewNeededError effects) ...
    coding_task_user_prompt = (
        "You are an expert Python developer. Write a Python function named `calculate_average` "
        "that takes a list of numbers and returns their average. "
        "It MUST handle an empty list by returning 0.0 (float). "
        "It MUST include a comprehensive docstring. "
        "For the first attempt, deliberately include a syntax error (e.g., use 'deff' instead of 'def'). "
        "Respond ONLY with the Python code block for the function, no other text."
    )
    perplexity_tool_mcp_config = {"mcpServers": {"perplexity-ask": {"command": "node", "args": ["path/to/your/perplexity-tool.js"], "env": {"PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY_FOR_MCP")}}}}
    code_tester_mcp_config = {"mcpServers": {"python_executor": {"command": "python_tool_placeholder"}}}

    code_generation_llm_config = {
        "model": "max/code_generator_agent_iterative", 
        "messages": [
            {"role": "system", "content": "You are a Python code generation assistant. Output only raw Python code. If given feedback about errors, try your best to fix them precisely."},
            {"role": "user", "content": coding_task_user_prompt}
        ],
        "temperature": 0.2, "max_tokens": 700,
        "retry_config": { "max_attempts": 5, "debug_mode": True },
        "max_attempts_before_tool_use": 2, 
        "max_attempts_before_human": 4,    
        "debug_tool_name": "perplexity-ask", 
        "debug_tool_mcp_config": perplexity_tool_mcp_config, 
        "validation": [
            {"type": "response_not_empty"},
            {
                "type": "agent_task", 
                "params": {
                    "validation_model_alias": "max/code_tester_agent", 
                    "task_prompt_to_claude": (
                        "The Python code provided by the previous step is an attempt to solve: '{ORIGINAL_USER_PROMPT}'.\n"
                        "Code to validate:\n```python\n{CODE_TO_VALIDATE}\n```\n"
                        "Validate it meticulously:\n1. Syntax ok?\n2. Name `calculate_average`?\n3. `calculate_average([])` returns `0.0`?\n4. `calculate_average([1,2,3,6])` returns `3.0`?\n5. Docstring present?\n"
                        "Use 'python_executor' tool for tests 3 & 4. Respond ONLY JSON: {\"validation_passed\": <bool>, \"reasoning\": \"<str>\", \"details\": {\"syntax_ok\": <bool>, \"name_ok\":<bool>, \"empty_list_test_pass\": <bool>, \"non_empty_test_pass\": <bool>, \"docstring_present\": <bool>}}"
                    ),
                    "mcp_config": code_tester_mcp_config,
                    "success_criteria": {"all_true_in_details_keys": ["syntax_ok", "name_ok", "empty_list_test_pass", "non_empty_test_pass", "docstring_present"]}
                }
            }
        ],
        "original_user_prompt": coding_task_user_prompt 
    }
    final_code_response = await llm_call(code_generation_llm_config)
    if final_code_response:
        if isinstance(final_code_response, dict) and "error" in final_code_response:
            if final_code_response["error"] == "Human review needed": logger.error(f"🚩 CODING TASK REQUIRES HUMAN REVIEW. Details: {final_code_response.get('details')}")
            else: logger.warning(f"Coding task info: {final_code_response['error']}")
        elif hasattr(final_code_response, "choices"): 
            generated_code = final_code_response.choices[0].message.content
            logger.success("✅ Coding task successful!")
            print("\n>>> Final Generated Code:\n", generated_code, "\n<<< End of Code")
        elif isinstance(final_code_response, dict) and final_code_response.get("choices"):
            generated_code = final_code_response["choices"][0].get("message", {}).get("content")
            logger.success("✅ Coding task successful!")
            print("\n>>> Final Generated Code:\n", generated_code, "\n<<< End of Code")
        else: logger.warning(f"Unexpected response from coding task: {json.dumps(final_code_response, indent=2, default=str)}")
    else: logger.error("Coding task failed, no specific error message returned.")


if __name__ == "__main__":
    asyncio.run(main_client_runner())