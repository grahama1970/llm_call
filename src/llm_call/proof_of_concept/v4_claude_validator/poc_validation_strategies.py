import json
from typing import Any, Dict, List, Optional, Callable # Added Callable
from loguru import logger

# Assuming these core base classes are importable after 'uv pip install -e .'
from llm_call.core.base import ValidationResult, AsyncValidationStrategy
from llm_call.core.utils.json_utils import clean_json_string

# Import for PoCAgentTaskValidator to specify MCP tools for Claude
# This is a PoC-specific import pattern; in core, config would be handled differently.
from llm_call.proof_of_concept.poc_claude_proxy_server import DEFAULT_ALL_TOOLS_MCP_CONFIG


class PoCResponseNotEmptyValidator(AsyncValidationStrategy):
    @property
    def name(self) -> str: return "response_not_empty"

    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        logger.debug(f"[{self.name}] Validating response...")
        content_str = None
        is_error_response = False
        error_message = ""

        if isinstance(response, dict): # Proxy response or error structure
            if "error" in response and not response.get("choices"): # Direct error dict
                is_error_response = True
                error_message = str(response["error"])
            elif response.get("choices"):
                choices = response.get("choices", [])
                if choices and isinstance(choices, list) and len(choices) > 0:
                    content_str = choices[0].get("message", {}).get("content", "")
                else: # Valid structure but no choices or empty choices
                    error_message = "Response from proxy is missing 'choices' or 'choices' is empty."
                    is_error_response = True # Treat as an error for not_empty validation
            else: # Dict but not a recognized success or error structure
                error_message = f"Unrecognized dict response structure: {str(response)[:200]}"
                is_error_response = True
        elif hasattr(response, "choices") and isinstance(response.choices, list) and response.choices: # LiteLLM ModelResponse
            content_str = response.choices[0].message.content
        elif hasattr(response, "error"): # Generic error attribute if some custom error object
             is_error_response = True
             error_message = str(response.error)
        else: # Truly unknown or None
            return ValidationResult(valid=False, error=f"Unknown or None response type: {type(response).__name__}")

        if is_error_response:
            return ValidationResult(valid=False, error=f"LLM call resulted in error or problematic response: {error_message}")

        if content_str is None or not str(content_str).strip():
            return ValidationResult(valid=False, error="Response content is empty or not a string.",
                                    suggestions=["Try rephrasing prompt.", "Check model for empty response issue."])
        return ValidationResult(valid=True, debug_info={"content_preview": str(content_str)[:50]})

class PoCJsonStringValidator(AsyncValidationStrategy):
    @property
    def name(self) -> str: return "json_string"

    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        logger.debug(f"[{self.name}] Validating if response content is valid JSON string...")
        content_str = None
        if isinstance(response, dict) and response.get("choices"):
            content_str = response["choices"][0].get("message", {}).get("content")
        elif hasattr(response, "choices") and response.choices:
            content_str = response.choices[0].message.content
        
        if not isinstance(content_str, str) or not content_str.strip():
            return ValidationResult(valid=False, error="Content for JSON validation is empty or not a string.")
        
        # Use clean_json_string for flexible JSON extraction
        try:
            parsed_data = clean_json_string(content_str, return_dict=True)
            if parsed_data is None:
                # clean_json_string returns None if no JSON found
                return ValidationResult(valid=False, error="No valid JSON found in content",
                                        suggestions=["Ensure LLM is instructed for JSON output.", "Try using `response_format={'type': 'json_object'}`."])
            return ValidationResult(valid=True, debug_info={"parsed_json_type": type(parsed_data).__name__})
        except Exception as e:
            return ValidationResult(valid=False, error=f"Error extracting JSON: {e}",
                                    suggestions=["Ensure LLM is instructed for JSON output.", "Try using `response_format={'type': 'json_object'}`."])

class PoCFieldPresentValidator(AsyncValidationStrategy):
    def __init__(self, field_name: str, expected_value: Optional[Any] = None, present: bool = True):
        self._field_name = field_name
        self._expected_value = expected_value
        self._present = present # True to check for presence, False to check for absence
        super().__init__()

    @property
    def name(self) -> str:
        presence_str = "present" if self._present else "absent"
        return f"field_{presence_str}_check_for_{self._field_name}"

    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        # ... (logic as before, but refined for clarity) ...
        logger.debug(f"[{self.name}] Validating field '{self._field_name}'. Expected presence: {self._present}")
        content_str = None; data_to_check = None
        if isinstance(response, dict) and response.get("choices"): 
            content_str = response["choices"][0].get("message", {}).get("content")
        elif hasattr(response, "choices") and response.choices: 
            content_str = response.choices[0].message.content
        
        if not isinstance(content_str, str) or not content_str.strip(): 
            return ValidationResult(valid=False, error="Content is empty/not string for field check.")
        # Use clean_json_string for flexible JSON extraction
        try: 
            data_to_check = clean_json_string(content_str, return_dict=True)
            if data_to_check is None:
                return ValidationResult(valid=False, error=f"No valid JSON found, cannot check field '{self._field_name}'.")
        except Exception: 
            return ValidationResult(valid=False, error=f"Error extracting JSON, cannot check field '{self._field_name}'.")
        if not isinstance(data_to_check, dict): 
            return ValidationResult(valid=False, error=f"JSON content not dict, cannot check field '{self._field_name}'.")

        field_is_present = self._field_name in data_to_check
        
        if self._present: # Check for presence
            if field_is_present:
                if self._expected_value is not None:
                    actual_value = data_to_check[self._field_name]
                    if actual_value == self._expected_value:
                        return ValidationResult(valid=True, debug_info={self._field_name: actual_value})
                    else:
                        return ValidationResult(valid=False, error=f"Field '{self._field_name}' present but value '{actual_value}' != expected '{self._expected_value}'.")
                return ValidationResult(valid=True, debug_info={self._field_name: data_to_check.get(self._field_name)})
            else:
                return ValidationResult(valid=False, error=f"Required field '{self._field_name}' is missing.", suggestions=[f"Ensure LLM includes '{self._field_name}'."])
        else: # Check for absence
            if not field_is_present:
                return ValidationResult(valid=True, debug_info={self._field_name: "correctly_absent"})
            else:
                return ValidationResult(valid=False, error=f"Field '{self._field_name}' is present but should be absent.", suggestions=[f"Ensure LLM excludes '{self._field_name}'."])


class PoCAgentTaskValidator(AsyncValidationStrategy): # This is our primary AI-assisted validator
    def __init__(self,
                 task_prompt_to_claude: str, # The full prompt telling the agent what to do
                 validation_model_alias: str = "max/default_validator_agent", # The Claude agent to call
                 mcp_config: Optional[Dict] = None, # Specific MCP tools for this validation task
                 # How to interpret the agent's JSON response for pass/fail:
                 success_criteria: Optional[Dict] = {"agent_must_report_true": "validation_passed"} 
                ):
        self._task_prompt_to_claude = task_prompt_to_claude
        self._validation_model_alias = validation_model_alias
        self._mcp_config = mcp_config
        self._success_criteria = success_criteria if success_criteria else {}
        self._llm_caller: Optional[Callable] = None

    def set_llm_caller(self, caller_func: Callable):
        self._llm_caller = caller_func

    @property
    def name(self) -> str:
        # Generate a name, e.g., from the first few words of the task prompt
        prompt_summary = "_".join(self._task_prompt_to_claude.split()[:3]).lower()
        safe_summary = "".join(c if c.isalnum() else "_" for c in prompt_summary)
        return f"agent_task_{safe_summary}"

    async def validate(self, response_to_validate: Any, context: Dict[str, Any]) -> ValidationResult:
        if not self._llm_caller:
            return ValidationResult(valid=False, error=f"[{self.name}] LLM caller not set for AI-assisted validation.")

        # Extract the content from the primary LLM's response that needs validation
        content_from_primary_llm = ""
        if isinstance(response_to_validate, dict) and response_to_validate.get("choices"):
            content_from_primary_llm = response_to_validate["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response_to_validate, "choices") and response_to_validate.choices:
            content_from_primary_llm = response_to_validate.choices[0].message.content or ""
        elif isinstance(response_to_validate, str):
            content_from_primary_llm = response_to_validate
        
        # The task_prompt_to_claude should include placeholders for the content to validate
        # and original user prompt from the context.
        final_agent_prompt = self._task_prompt_to_claude.format(
            TEXT_TO_VALIDATE=content_from_primary_llm,
            CODE_TO_VALIDATE=content_from_primary_llm, # Alias for convenience
            ORIGINAL_USER_PROMPT=context.get("original_llm_config", {}).get("messages", [{}])[-1].get("content", "N/A") # Last user message
        )

        agent_task_messages = [
            {"role": "system", "content": "You are a diligent validation agent. Execute the user's validation task precisely using any specified tools. Respond ONLY with a structured JSON object detailing your findings as per the user's requested JSON schema."},
            {"role": "user", "content": final_agent_prompt}
        ]
        
        agent_llm_config = {
            "model": self._validation_model_alias,
            "messages": agent_task_messages,
            "response_format": {"type": "json_object"}, # Agent must return JSON
            "temperature": 0.0, # For deterministic validation
            "max_tokens": 1500, # Allow for detailed JSON reports from agent
        }
        if self._mcp_config: # Pass specific MCP config for this validation call
            agent_llm_config["mcp_config"] = self._mcp_config

        logger.info(f"[{self.name}] Sending validation task to agent: '{self._validation_model_alias}'.")
        logger.debug(f"[{self.name}] Agent task prompt (first 300 chars): {final_agent_prompt[:300]}...")
        if self._mcp_config:
            logger.debug(f"[{self.name}] MCP Config for agent: {json.dumps(self._mcp_config, indent=2)}")

        agent_response_dict = await self._llm_caller(agent_llm_config)

        if not agent_response_dict:
            return ValidationResult(valid=False, error=f"[{self.name}] No response received from validation agent.")
        
        try:
            agent_report_str = agent_response_dict.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not agent_report_str:
                 return ValidationResult(valid=False, error=f"[{self.name}] Validation agent returned empty content.")
            
            logger.debug(f"[{self.name}] Validation agent raw report string: {agent_report_str}")
            # Use clean_json_string for flexible extraction from agent responses
            agent_report = clean_json_string(agent_report_str, return_dict=True)
            if agent_report is None or not isinstance(agent_report, dict):
                # If we got a string or other non-dict, it's not a valid agent response
                error_msg = f"[{self.name}] Agent response is not a valid JSON object."
                if agent_report is not None:
                    error_msg += f" Got {type(agent_report).__name__}: {repr(agent_report)[:100]}"
                error_msg += f" Raw response: {agent_report_str[:300]}..."
                return ValidationResult(valid=False, error=error_msg)
            
            # Apply success_criteria to interpret agent_report
            is_valid = True # Assume valid unless criteria say otherwise
            reasoning = agent_report.get("reasoning", "Agent provided no explicit reasoning.") # Default reasoning

            if self._success_criteria.get("agent_must_report_true"):
                key = self._success_criteria["agent_must_report_true"]
                if not agent_report.get(key, False) == True: # Must be explicitly True
                    is_valid = False
                    reasoning = f"Agent report key '{key}' was not true. Agent reasoning: {reasoning}"
            elif self._success_criteria.get("must_not_contain_string_in_reasoning") and isinstance(reasoning, str):
                substring = self._success_criteria["must_not_contain_string_in_reasoning"]
                if substring.lower() in reasoning.lower():
                    is_valid = False
                    reasoning = f"Agent reasoning contained forbidden string '{substring}'. Full reasoning: {reasoning}"
            elif self._success_criteria.get("all_true_in_details_keys"):
                # Check if all specified keys in details are True
                required_keys = self._success_criteria["all_true_in_details_keys"]
                details = agent_report.get("details", {})
                failed_keys = []
                for key in required_keys:
                    if not details.get(key, False) == True:
                        failed_keys.append(key)
                if failed_keys:
                    is_valid = False
                    reasoning = f"Agent validation failed: {len(failed_keys)} of {len(required_keys)} checks failed. Failed: {failed_keys}. Agent reasoning: {reasoning}"
            # Add more sophisticated success criteria checks here as needed

            if is_valid:
                logger.success(f"[{self.name}] Agent task validation PASSED. Agent reasoning: {reasoning}")
                return ValidationResult(valid=True, debug_info={"agent_report": agent_report})
            else:
                logger.warning(f"[{self.name}] Agent task validation FAILED. Final Reasoning: {reasoning}")
                return ValidationResult(valid=False, error=f"Agent validation failed: {reasoning}", 
                                        suggestions=[f"Review agent report. Agent reasoning: {agent_report.get('reasoning', 'N/A')[:200]}..."],
                                        debug_info={"agent_report": agent_report})
        except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response.")
            return ValidationResult(valid=False, error=f"[{self.name}] Critical error processing agent response: {e}", debug_info={"raw_agent_response": str(agent_response_dict)})


# PoC strategy registry (maps type string from llm_config to validator class)
poc_strategy_registry = {
    "response_not_empty": PoCResponseNotEmptyValidator,
    "json_string": PoCJsonStringValidator,
    "field_present": PoCFieldPresentValidator,
    "agent_task": PoCAgentTaskValidator, # Generic AI agent task validator
    # "ai_contradiction_check": PoCAIContradictionValidator, # Can be implemented using agent_task
}