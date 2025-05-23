import json
from typing import Any, Dict, List, Optional
from loguru import logger

from llm_call.core.base import ValidationResult, AsyncValidationStrategy
# from llm_call.proof_of_concept.litellm_client_poc import llm_call as poc_llm_caller # Injected

class PoCResponseNotEmptyValidator(AsyncValidationStrategy):
    @property
    def name(self) -> str: return "response_not_empty"
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        # ... (implementation) ...
        content_str = None; is_error_response = False; error_message = ""
        if isinstance(response, dict):
            if "error" in response: is_error_response = True; error_message = str(response["error"])
            else:
                choices = response.get("choices", []);
                if choices and isinstance(choices, list) and len(choices) > 0: content_str = choices[0].get("message", {}).get("content", "")
                else: error_message = "Response from proxy is missing 'choices' or 'choices' is empty."
        elif hasattr(response, "choices") and response.choices: content_str = response.choices[0].message.content
        elif hasattr(response, "error"): is_error_response = True; error_message = str(response.get("error", "Unknown error structure"))
        else: return ValidationResult(valid=False, error=f"Unknown response type: {type(response).__name__}")
        if is_error_response: return ValidationResult(valid=False, error=f"LLM call resulted in error: {error_message}")
        if content_str is None or not str(content_str).strip(): return ValidationResult(valid=False, error="Response content is empty.", suggestions=["Try rephrasing prompt."])
        return ValidationResult(valid=True, debug_info={"content_preview": str(content_str)[:50]})


class PoCJsonStringValidator(AsyncValidationStrategy):
    # ... (implementation) ...
    @property
    def name(self) -> str: return "json_string"
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        # ... (implementation)
        content_str = None
        if isinstance(response, dict) and response.get("choices"): content_str = response["choices"][0].get("message", {}).get("content")
        elif hasattr(response, "choices") and response.choices: content_str = response.choices[0].message.content
        if not isinstance(content_str, str) or not content_str.strip(): return ValidationResult(valid=False, error="Content for JSON validation is empty or not a string.")
        try: json.loads(content_str); return ValidationResult(valid=True)
        except json.JSONDecodeError as e: return ValidationResult(valid=False, error=f"Content is not valid JSON: {e}", suggestions=["Instruct LLM for JSON."])

class PoCFieldPresentValidator(AsyncValidationStrategy):
    # ... (implementation) ...
    def __init__(self, field_name: str): self._field_name = field_name; super().__init__()
    @property
    def name(self) -> str: return f"field_present_check_for_{self._field_name}"
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        # ... (implementation)
        content_str = None; data_to_check = None
        if isinstance(response, dict) and response.get("choices"): content_str = response["choices"][0].get("message", {}).get("content")
        elif hasattr(response, "choices") and response.choices: content_str = response.choices[0].message.content
        if not isinstance(content_str, str) or not content_str.strip(): return ValidationResult(valid=False, error="Content is empty/not string.")
        try: data_to_check = json.loads(content_str)
        except json.JSONDecodeError: return ValidationResult(valid=False, error=f"Content not JSON, cannot check field '{self._field_name}'.")
        if not isinstance(data_to_check, dict): return ValidationResult(valid=False, error=f"JSON content not dict, cannot check field '{self._field_name}'.")
        if self._field_name in data_to_check and data_to_check[self._field_name] is not None: return ValidationResult(valid=True)
        return ValidationResult(valid=False, error=f"Field '{self._field_name}' missing/null.", suggestions=[f"Ensure LLM includes '{self._field_name}'."])


class PoCAgentTaskValidator(AsyncValidationStrategy):
    def __init__(self,
                 task_prompt_to_claude: str,
                 validation_model_alias: str = "max/generic_agent_validator",
                 mcp_config: Optional[Dict] = None,
                 success_criteria: Optional[Dict] = None):
        self._task_prompt_to_claude = task_prompt_to_claude
        self._validation_model_alias = validation_model_alias
        self._mcp_config = mcp_config
        self._success_criteria = success_criteria if success_criteria else {}
        self._llm_caller: Optional[callable] = None

    def set_llm_caller(self, caller_func: callable):
        self._llm_caller = caller_func

    @property
    def name(self) -> str:
        # Generate a more dynamic name if possible, or keep it simple
        prompt_summary = self._task_prompt_to_claude[:30].replace("\n", " ").strip()
        return f"agent_task_{prompt_summary}..."

    async def validate(self, response_to_validate: Any, context: Dict[str, Any]) -> ValidationResult:
        if not self._llm_caller:
            return ValidationResult(valid=False, error=f"[{self.name}] LLM caller not set.")

        content_to_pass_to_agent = ""
        if isinstance(response_to_validate, dict) and response_to_validate.get("choices"):
            content_to_pass_to_agent = response_to_validate["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response_to_validate, "choices") and response_to_validate.choices:
            content_to_pass_to_agent = response_to_validate.choices[0].message.content or ""
        elif isinstance(response_to_validate, str):
            content_to_pass_to_agent = response_to_validate
        else: # If response_to_validate is None or unhandled type, and task needs it
            if "{CODE_TO_VALIDATE}" in self._task_prompt_to_claude or "{TEXT_TO_VALIDATE}" in self._task_prompt_to_claude: # crude check
                 logger.warning(f"[{self.name}] Task prompt expects content to validate, but previous response was None or unhandled type.")
                 # Depending on the task, this might be an immediate validation failure or the agent might handle it.
                 # For code validation, it's a failure.

        # Substitute placeholders in the task prompt
        final_task_prompt = self._task_prompt_to_claude.replace("{CODE_TO_VALIDATE}", content_to_pass_to_agent)
        final_task_prompt = final_task_prompt.replace("{TEXT_TO_VALIDATE}", content_to_pass_to_agent)
        final_task_prompt = final_task_prompt.replace("{ORIGINAL_USER_PROMPT}", context.get("original_user_prompt", "N/A"))


        agent_task_messages = [
            {"role": "system", "content": "You are a task execution and validation agent. Follow instructions precisely. Use available tools if needed. Respond ONLY with JSON: {\"validation_passed\": boolean, \"reasoning\": \"string\", \"details\": \"(string or dict of tool outputs/test results)\"}."},
            {"role": "user", "content": final_task_prompt}
        ]
        
        agent_llm_config = {
            "model": self._validation_model_alias, "messages": agent_task_messages,
            "response_format": {"type": "json_object"}, "temperature": 0.0, "max_tokens": 1500,
        }
        if self._mcp_config:
            agent_llm_config["mcp_config"] = self._mcp_config

        logger.info(f"[{self.name}] Sending task to agent '{self._validation_model_alias}'.")
        logger.debug(f"[{self.name}] Agent task prompt (first 200 chars): {final_task_prompt[:200]}...")
        agent_response_dict = await self._llm_caller(agent_llm_config)

        if not agent_response_dict:
            return ValidationResult(valid=False, error=f"[{self.name}] No response from validation agent.")
        
        try:
            agent_report_str = ""
            if isinstance(agent_response_dict, dict) and agent_response_dict.get("choices"):
                agent_report_str = agent_response_dict["choices"][0].get("message", {}).get("content","")
            # No elif for LiteLLM ModelResponse here, as agent_response_dict should be from proxy.
            
            if not agent_report_str:
                 return ValidationResult(valid=False, error=f"[{self.name}] Validation agent returned empty content.")
            
            agent_report = json.loads(agent_report_str)
            
            validation_passed_by_agent = agent_report.get("validation_passed", False)
            reasoning = agent_report.get("reasoning", "No reasoning provided by agent.")
            details_from_agent = agent_report.get("details", {}) # Expect details to be a dict for "all_true_in_details_keys"

            final_validation_passed = validation_passed_by_agent # Start with agent's decision
            
            # Apply success_criteria
            if "must_contain_in_details" in self._success_criteria and isinstance(details_from_agent, str):
                if self._success_criteria["must_contain_in_details"].lower() not in details_from_agent.lower():
                    final_validation_passed = False
                    reasoning += f" [Criteria Fail: details did not contain '{self._success_criteria['must_contain_in_details']}']"
            elif "all_true_in_details_keys" in self._success_criteria and isinstance(details_from_agent, dict):
                required_keys = self._success_criteria["all_true_in_details_keys"]
                if not isinstance(required_keys, list): required_keys = [required_keys]
                for key_to_check in required_keys:
                    if not details_from_agent.get(key_to_check, False) == True: # Must be explicitly True
                        final_validation_passed = False
                        reasoning += f" [Criteria Fail: details key '{key_to_check}' not true or missing.]"
                        break 
            
            if final_validation_passed:
                return ValidationResult(valid=True, debug_info={"agent_report": agent_report})
            else:
                return ValidationResult(valid=False, error=f"Agent task validation failed: {reasoning}", 
                                        suggestions=[f"Agent details: {str(details_from_agent)[:200]}..."],
                                        debug_info={"agent_report": agent_report})
        except json.JSONDecodeError as e:
            return ValidationResult(valid=False, error=f"[{self.name}] Could not parse JSON from agent: {e}. Raw: {agent_report_str[:300]}", debug_info={"raw_agent_response": agent_report_str})
        except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response.")
            return ValidationResult(valid=False, error=f"[{self.name}] Error processing agent response: {e}", debug_info={"raw_agent_response": str(agent_response_dict)})

# PoCAIContradictionValidator (can be a specialized use of PoCAgentTaskValidator or separate)
class PoCAIContradictionValidator(AsyncValidationStrategy):
    # ... (implementation as before, uses PoCAgentTaskValidator concepts) ...
    def __init__(self, text_to_check: str, topic_context: str, 
                 validation_model_alias: str = "max/contradiction_expert_agent",
                 required_mcp_tools: Optional[List[str]] = ["perplexity-ask"]):
        self._text_to_check = text_to_check
        self._topic_context = topic_context
        self._validation_model_alias = validation_model_alias
        self._required_mcp_tools = required_mcp_tools
        self._llm_caller: Optional[callable] = None

    def set_llm_caller(self, caller_func: callable): self._llm_caller = caller_func
    @property
    def name(self) -> str: return f"ai_contradiction_check_on_{self._topic_context[:20].replace(' ','_')}"

    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        if not self._llm_caller: return ValidationResult(valid=False, error="AIContradictionValidator: LLM caller not set.")
        if not self._text_to_check or not self._text_to_check.strip():
            return ValidationResult(valid=True, debug_info={"reason": "No text for contradiction check."})

        logger.info(f"[{self.name}] Requesting AI-assisted contradiction check for topic: '{self._topic_context}'.")
        claude_task_prompt = (
            f"Analyze text on '{self._topic_context}' for contradictions or conflicts with scientific consensus. "
            f"MUST use 'perplexity-ask' tool to research '{self._topic_context}'. "
            f"Text:\n```text\n{self._text_to_check[:150000]}\n```\n"
            f"Respond ONLY JSON: {{\"contradictions_found\": <bool>, \"certainty_of_findings\": <float>, \"summary_of_findings\": \"<str>\", \"perplexity_ask_queries_used\": [\"<str>\"], \"perplexity_ask_key_insights\": \"<str>\"}}"
        )
        from llm_call.proof_of_concept.poc_claude_proxy_server import DEFAULT_ALL_TOOLS_MCP_CONFIG # For PoC
        mcp_config_for_call = {"mcpServers": {}}
        if self._required_mcp_tools:
            for tool_name in self._required_mcp_tools:
                if tool_name in DEFAULT_ALL_TOOLS_MCP_CONFIG["mcpServers"]:
                    mcp_config_for_call["mcpServers"][tool_name] = DEFAULT_ALL_TOOLS_MCP_CONFIG["mcpServers"][tool_name]
        
        agent_llm_config = {
            "model": self._validation_model_alias,
            "messages": [{"role": "system", "content": "You are an AI contradiction analyst."}, {"role": "user", "content": claude_task_prompt}],
            "response_format": {"type": "json_object"}, "temperature": 0.0, "max_tokens": 1000,
            "mcp_config": mcp_config_for_call if mcp_config_for_call["mcpServers"] else None
        }
        agent_response_dict = await self._llm_caller(agent_llm_config)
        # ... (parsing and ValidationResult logic as in PoCAgentTaskValidator, checking "contradictions_found") ...
        if not agent_response_dict: return ValidationResult(valid=False, error="AIContradictionValidator: No response from agent.")
        try:
            agent_report_str = agent_response_dict.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not agent_report_str: return ValidationResult(valid=False, error="AIContradictionValidator: Agent returned empty content.")
            agent_report = json.loads(agent_report_str)
            if agent_report.get("contradictions_found") == True:
                return ValidationResult(valid=False, error=f"AI found contradictions: {agent_report.get('summary_of_findings', 'N/A')}", debug_info={"agent_report": agent_report})
            return ValidationResult(valid=True, debug_info={"agent_report": agent_report})
        except Exception as e: return ValidationResult(valid=False, error=f"AIContradictionValidator: Error processing agent response: {e}", debug_info={"raw_response": str(agent_response_dict)})


poc_strategy_registry = {
    "response_not_empty": PoCResponseNotEmptyValidator,
    "json_string": PoCJsonStringValidator,
    "field_present": PoCFieldPresentValidator,
    "agent_task": PoCAgentTaskValidator,
    "ai_contradiction_check": PoCAIContradictionValidator,
}