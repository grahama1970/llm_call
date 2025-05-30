"""
AI-assisted validation strategies.

This module contains validators that make recursive LLM calls to validate responses.

Links:
- AsyncValidationStrategy base class documentation

Sample usage:
    validator = AIContradictionValidator(
        text_to_check="Flat Earth theory text...",
        topic_context="Flat Earth theory"
    )
    validator.set_llm_caller(llm_call_function)
    result = await validator.validate(response, context)

Expected output:
    ValidationResult with contradiction analysis
"""

import json
from typing import Any, Dict, List, Optional, Callable, Union
from loguru import logger

from llm_call.core.base import ValidationResult, AsyncValidationStrategy
from llm_call.core.strategies import validator


# Default MCP configuration for all tools
DEFAULT_ALL_TOOLS_MCP_CONFIG = {
    "mcpServers": {
        "perplexity-ask": {
            "command": "npx",
            "args": ["-y", "@haltiamieli/perplexity-server"],
            "env": {"PERPLEXITY_API_KEY": "${PERPLEXITY_API_KEY}"}
        },
        "desktop-commander": {
            "command": "npx",
            "args": ["-y", "@enesien/mcp-desktop-commander"],
            "env": {}
        }
    }
}


def build_selective_mcp_config(required_tools: List[str]) -> Dict[str, Any]:
    """Build MCP configuration with only the required tools."""
    if not required_tools:
        return {}
    
    config = {"mcpServers": {}}
    all_servers = DEFAULT_ALL_TOOLS_MCP_CONFIG["mcpServers"]
    
    for tool in required_tools:
        if tool in all_servers:
            config["mcpServers"][tool] = all_servers[tool]
    
    return config if config["mcpServers"] else {}


class AIAssistedValidator(AsyncValidationStrategy):
    """Base class for AI-assisted validators that need to make LLM calls."""
    
    def __init__(self):
        self._llm_caller: Optional[Callable] = None
    
    def set_llm_caller(self, caller_func: Callable) -> None:
        """
        Set the LLM caller function for recursive calls.
        
        Args:
            caller_func: Async function that takes llm_config dict and returns response
        """
        self._llm_caller = caller_func
    
    async def _call_llm(self, llm_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a recursive LLM call.
        
        Args:
            llm_config: Configuration for the LLM call
            
        Returns:
            LLM response dict or None if error
        """
        if not self._llm_caller:
            logger.error(f"[{self.name}] LLM caller not set for AI-assisted validation")
            return None
        
        try:
            return await self._llm_caller(llm_config)
        except Exception as e:
            logger.error(f"[{self.name}] Error calling LLM: {e}")
            return None


@validator("ai_contradiction_check")
class AIContradictionValidator(AIAssistedValidator):
    """
    Validator that uses AI to check for contradictions in text.
    
    This validator instructs Claude to use its perplexity-ask tool to research
    a topic and identify contradictions or factual inconsistencies.
    """
    
    def __init__(
        self,
        text_to_check: str,
        topic_context: str,
        validation_model: str = "max/claude-3-opus",
        required_mcp_tools: Optional[List[str]] = None
    ):
        """
        Initialize the contradiction validator.
        
        Args:
            text_to_check: Text to analyze for contradictions
            topic_context: Context/topic for the analysis (e.g., "Flat Earth theory")
            validation_model: Model to use for validation
            required_mcp_tools: MCP tools to enable (defaults to ["perplexity-ask"])
        """
        super().__init__()
        self._text_to_check = text_to_check
        self._topic_context = topic_context
        self._validation_model = validation_model
        self._required_mcp_tools = required_mcp_tools or ["perplexity-ask"]
    
    @property
    def name(self) -> str:
        """Generate validator name based on topic."""
        safe_topic = "".join(c if c.isalnum() else "_" for c in self._topic_context[:30])
        return f"ai_contradiction_check_on_{safe_topic}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate by checking for contradictions using AI.
        
        Note: The 'response' parameter is ignored as this validator operates on
        text_to_check provided during initialization.
        
        Args:
            response: LLM response (ignored by this validator)
            context: Validation context
            
        Returns:
            ValidationResult indicating if contradictions were found
        """
        if not self._text_to_check or not self._text_to_check.strip():
            logger.info(f"[{self.name}] No text provided to check. Skipping validation.")
            return ValidationResult(valid=True, debug_info={"reason": "No text to check"})
        
        logger.info(f"[{self.name}] Requesting AI contradiction check for topic: '{self._topic_context}'")
        
        # Construct prompt for Claude
        claude_task_prompt = (
            f"Please analyze the following text, which is related to '{self._topic_context}', "
            f"for any internal contradictions, logical fallacies, or statements that significantly conflict with "
            f"well-established scientific consensus or factual knowledge.\n\n"
            f"You MUST use your 'perplexity-ask' tool to research '{self._topic_context}', focusing on common misconceptions, "
            f"key facts, and any known internal inconsistencies within theories related to this topic. "
            f"Use the information from perplexity-ask to inform your analysis of the provided text.\n\n"
            f"Text to Analyze:\n```text\n{self._text_to_check[:150000]}\n```\n"
            f"(Note: The provided text might be truncated if exceedingly long. Base your primary analysis on this given text.)\n\n"
            f"After your analysis and tool use, respond ONLY with a JSON object with the following structure:\n"
            f"{{\n"
            f'  "contradictions_found": <boolean>,\n'
            f'  "certainty_of_findings": <float_from_0.0_to_1.0>,\n'
            f'  "summary_of_findings": "<string_explanation>",\n'
            f'  "perplexity_ask_queries_used": ["<query1>", "<query2>", ...],\n'
            f'  "perplexity_ask_key_insights": "<string_summary>"\n'
            f"}}\n"
            f"If no contradictions are found, set 'contradictions_found' to false and explain why."
        )
        
        # Prepare LLM config
        agent_llm_config = {
            "model": self._validation_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a highly analytical validation assistant specializing in identifying contradictions and factual inconsistencies using research tools."
                },
                {"role": "user", "content": claude_task_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
            "max_tokens": 1000,
        }
        
        # Add MCP configuration if tools are specified
        if self._required_mcp_tools:
            agent_llm_config["mcp_config"] = build_selective_mcp_config(self._required_mcp_tools)
        
        # Make the LLM call
        agent_response = await self._call_llm(agent_llm_config)
        
        if not agent_response:
            return ValidationResult(
                valid=False,
                error="AI Validator: No response from validation agent"
            )
        
        try:
            # Extract response content
            content = agent_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                return ValidationResult(
                    valid=False,
                    error="AI Validator: Agent returned empty content"
                )
            
            # Parse JSON response
            logger.debug(f"[{self.name}] Agent response: {content}")
            agent_report = json.loads(content)
            
            contradictions_found = agent_report.get("contradictions_found", True)
            explanation = agent_report.get("summary_of_findings", "No explanation provided")
            certainty = agent_report.get("certainty_of_findings", 0.0)
            
            if contradictions_found:
                logger.warning(f"[{self.name}] Contradictions found (certainty: {certainty:.2f})")
                return ValidationResult(
                    valid=False,
                    error=f"AI found contradictions: {explanation}",
                    suggestions=["Review the contradictions identified by the AI validator"],
                    debug_info={"agent_report": agent_report}
                )
            else:
                logger.success(f"[{self.name}] No contradictions found (certainty: {certainty:.2f})")
                return ValidationResult(
                    valid=True,
                    debug_info={"agent_report": agent_report}
                )
                
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                error=f"AI Validator: Could not parse JSON response: {e}",
                debug_info={"raw_response": content[:300]}
            )
        except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response")
            return ValidationResult(
                valid=False,
                error=f"AI Validator: Error processing response: {e}"
            )


@validator("agent_task")
class AgentTaskValidator(AIAssistedValidator):
    """
    Generic AI validator that can perform custom validation tasks.
    
    This validator sends a custom task prompt to Claude and expects a
    structured JSON response indicating validation success/failure.
    """
    
    def __init__(
        self,
        task_prompt: str,
        validation_model: str = "max/claude-3-opus",
        mcp_config: Optional[Dict[str, Any]] = None,
        required_mcp_tools: Optional[List[str]] = None
    ):
        """
        Initialize the agent task validator.
        
        Args:
            task_prompt: The validation task prompt to send to Claude
            validation_model: Model to use for validation
            mcp_config: Full MCP configuration dict (takes precedence)
            required_mcp_tools: List of tool names to enable (if mcp_config not provided)
        """
        super().__init__()
        self._task_prompt = task_prompt
        self._validation_model = validation_model
        self._mcp_config = mcp_config
        self._required_mcp_tools = required_mcp_tools
    
    @property
    def name(self) -> str:
        """Generate validator name from task prompt."""
        # Extract first few words from task prompt
        words = self._task_prompt.split()[:5]
        safe_name = "_".join(w.lower() for w in words if w.isalnum())
        return f"agent_task_{safe_name}"
    
    async def validate(self, response: Any, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate by sending task to AI agent.
        
        Args:
            response: The LLM response to validate
            context: Validation context
            
        Returns:
            ValidationResult based on agent's task execution
        """
        logger.info(f"[{self.name}] Sending validation task to agent")
        
        # Include the response in the task prompt
        full_prompt = (
            f"{self._task_prompt}\n\n"
            f"Response to validate:\n```\n{response}\n```\n\n"
            f"Respond with a JSON object containing:\n"
            f'{{"validation_passed": <boolean>, "explanation": "<string>", "details": {{}}}}'
        )
        
        # Prepare LLM config
        agent_llm_config = {
            "model": self._validation_model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a validation agent. Execute the given task and report results in JSON format."
                },
                {"role": "user", "content": full_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.0,
            "max_tokens": 1000,
        }
        
        # Add MCP configuration
        if self._mcp_config:
            agent_llm_config["mcp_config"] = self._mcp_config
        elif self._required_mcp_tools:
            agent_llm_config["mcp_config"] = build_selective_mcp_config(self._required_mcp_tools)
        
        # Make the LLM call
        agent_response = await self._call_llm(agent_llm_config)
        
        if not agent_response:
            return ValidationResult(
                valid=False,
                error="Agent Task Validator: No response from agent"
            )
        
        try:
            # Extract and parse response
            content = agent_response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                return ValidationResult(
                    valid=False,
                    error="Agent Task Validator: Empty response"
                )
            
            result = json.loads(content)
            validation_passed = result.get("validation_passed", False)
            explanation = result.get("explanation", "No explanation provided")
            details = result.get("details", {})
            
            if validation_passed:
                logger.success(f"[{self.name}] Validation passed: {explanation}")
                return ValidationResult(
                    valid=True,
                    debug_info={"agent_result": result}
                )
            else:
                logger.warning(f"[{self.name}] Validation failed: {explanation}")
                return ValidationResult(
                    valid=False,
                    error=f"Agent validation failed: {explanation}",
                    debug_info={"agent_result": result, "details": details}
                )
                
        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                error=f"Agent Task Validator: Invalid JSON response: {e}",
                debug_info={"raw_response": content[:300]}
            )
        except Exception as e:
            logger.exception(f"[{self.name}] Error processing agent response")
            return ValidationResult(
                valid=False,
                error=f"Agent Task Validator: Error: {e}"
            )


if __name__ == "__main__":
    import asyncio
    
    async def test_validators():
        """Test AI validators (without actual LLM calls)."""
        print("Testing AI validators...")
        
        # Test contradiction validator
        validator = AIContradictionValidator(
            text_to_check="The Earth is flat and also round at the same time.",
            topic_context="Earth shape theories"
        )
        print(f"✅ Created contradiction validator: {validator.name}")
        
        # Test agent task validator
        task_validator = AgentTaskValidator(
            task_prompt="Check if the response contains valid Python code",
            required_mcp_tools=["desktop-commander"]
        )
        print(f"✅ Created agent task validator: {task_validator.name}")
        
        # Test without LLM caller set
        result = await validator.validate("test response", {})
        assert not result.valid
        assert "LLM caller not set" in result.error
        print("✅ Validator correctly handles missing LLM caller")
        
        print("\n✅ All AI validator tests passed!")
    
    asyncio.run(test_validators())