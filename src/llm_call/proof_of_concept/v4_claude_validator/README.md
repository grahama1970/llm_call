# LLM Call PoC: AI-Assisted Validation & Iterative Task Execution Framework

This document details an advanced layer of the `llm_call` Proof of Concept (PoC), focusing on how LLM responses can be validated using AI-driven strategies, including leveraging a "Claude Code agent" (referred to as the "agent" or "validator agent" below) to perform complex checks and tasks, potentially using its own suite of dynamically configured tools (MCPs). This framework also supports multi-stage retry logic for iterative refinement of LLM outputs.

## Core Concepts

1.  **Main LLM Call (`llm_call` function):**
    * The primary entry point for any LLM interaction, orchestrated by `litellm_client_poc.py`.
    * Accepts an `llm_config` dictionary detailing the model, messages, generation parameters, and specific validation requirements.

2.  **Dynamic Validation Strategies:**
    * The `llm_config` can include a `validation` key, which is a list of validation tasks to be performed on the response from the primary LLM call.
    * Each validation task is defined by a `type` (mapping to a registered `AsyncValidationStrategy` class) and `params` specific to that validator.
    * Example:
        ```json
        "validation": [
            {"type": "response_not_empty"},
            {"type": "json_string"},
            {"type": "agent_task", "params": {/* ... agent task specific params ... */}}
        ]
        ```

3.  **AI-Assisted Validation via "Agent Tasks":**
    * A key validation type is `"agent_task"`, implemented by `PoCAgentTaskValidator`.
    * This strategy allows delegating complex validation logic to a Claude Code agent instance (accessed via the `max/` proxy route, e.g., `max/validator_agent`).
    * **How it works:**
        1.  The Python `PoCAgentTaskValidator` receives the primary LLM's response.
        2.  It constructs a detailed **natural language prompt** for the Claude Code agent. This prompt includes:
            * The primary LLM's response (or relevant parts of it) as `{TEXT_TO_VALIDATE}` or `{CODE_TO_VALIDATE}`.
            * The original user prompt or task description (as `{ORIGINAL_USER_PROMPT}`) for context.
            * Specific instructions on *what to validate* and *what criteria to use*.
            * Crucially, instructions on **which of its available tools the Claude agent MUST or SHOULD use** to perform the validation (e.g., "You MUST use your 'perplexity-ask' tool to research X...").
            * A requirement for the Claude agent to respond ONLY in a specific structured JSON format detailing the validation outcome (e.g., `{"validation_passed": boolean, "reasoning": "...", "details": {...}}`).
        3.  The `PoCAgentTaskValidator` can also specify an `mcp_config` in its `params`. This `mcp_config` is sent to the `poc_claude_proxy_server.py`.
        4.  The proxy server writes this `mcp_config` to a `.mcp.json` file in the Claude CLI's working directory for *that specific validation call*. This dynamically enables and configures the tools the Claude agent needs for the validation task. If no `mcp_config` is sent by the validator, the proxy server defaults to enabling all its pre-defined tools for the Claude agent.
        5.  The `PoCAgentTaskValidator` then makes a recursive `llm_call` to the specified Claude agent (e.g., `max/validator_agent`).
        6.  The Claude agent executes the task, uses its (dynamically configured) tools as instructed in the prompt, and returns its findings in the requested JSON format.
        7.  The Python `PoCAgentTaskValidator` parses this JSON and determines the `ValidationResult` (pass/fail, error messages, suggestions).

4.  **Multi-Stage Retry Loop (`retry_with_validation_poc`):**
    * All primary LLM calls made via `llm_call` are wrapped in the `retry_with_validation_poc` loop (from `poc_retry_manager.py`).
    * This loop handles:
        * **Initial Attempts & Self-Correction:** If validation fails, the error messages and suggestions from the `ValidationResult` are appended to the conversation history, and the primary LLM is asked to try again, incorporating the feedback.
        * **Tool-Assisted Retry Stage:** The `llm_config` can specify `max_attempts_before_tool_use` and a `debug_tool_name` (e.g., "perplexity-ask") along with a `debug_tool_mcp_config`.
            * If validation continues to fail and this attempt threshold is reached, `retry_with_validation_poc` modifies the feedback prompt to the *primary LLM agent* (e.g., `max/code_generator_agent`), explicitly instructing it to use the `debug_tool_name` to research the errors before its next attempt.
            * For this tool-assisted retry, `retry_with_validation_poc` ensures that the `debug_tool_mcp_config` is passed to the Claude proxy, so the primary LLM agent has the specified debug tool (e.g., "perplexity-ask") enabled for that attempt.
        * **Human Escalation Stage:** The `llm_config` can specify `max_attempts_before_human`. If all retries (including tool-assisted ones) fail up to this limit, `retry_with_validation_poc` raises a `PoCHumanReviewNeededError`, signaling that the task could not be completed automatically.

5.  **Claude Agent's `llm_call_tool` (Recursive Capability):**
    * A core concept is that the Claude Code agent itself can be equipped with an MCP tool that allows *it* to make new LLM calls (using the same `llm_call` framework).
    * **Use Case Example:** If an `agent_task` validator asks Claude to find contradictions in a very large document (>200K tokens, exceeding its direct context window), the prompt to Claude would instruct it: "This document is very long. Use your 'llm_call_tool' to ask 'vertex_ai/gemini-1.5-pro-latest' (which has a 1M context window) to find contradictions in the full text and report its findings to you. Then, summarize those findings in your validation report."
    * **Mechanism:**
        1.  The `PoCAgentTaskValidator`'s `params` for the `agent_task` would include an `mcp_config` that defines the `llm_call_tool`. This tool's command would point to a Python script (e.g., `/app/tools/llm_call_delegator.py`) inside the Claude agent's Docker container.
        2.  The Claude agent, when processing the prompt, would decide to use this `llm_call_tool`.
        3.  The Claude CLI executes `/app/tools/llm_call_delegator.py`, passing parameters like the target model (`vertex_ai/gemini-1.5-pro-latest`), the large text (or a path to it), and the specific sub-task prompt (e.g., "find contradictions in this text").
        4.  The `llm_call_delegator.py` script then imports and uses the *same* `llm_call` function (from `litellm_client_poc.py` or eventually `core/caller.py`, assuming the `llm_call` package is installed in Claude's container) to make the call to Gemini.
        5.  Gemini's response is returned to the `llm_call_delegator.py`, which prints it to `stdout`.
        6.  The Claude CLI captures this output and uses it to complete its original validation task.

## How Users Specify Complex Validations

The user configures these advanced validations easily within their `llm_config`:

```python
# Example llm_config for an iterative coding task
coding_task_llm_config = {
    "model": "max/code_generator_agent", # Primary agent to generate code
    "messages": [
        {"role": "system", "content": "Generate Python code. Fix errors based on feedback."},
        {"role": "user", "content": "Write a function to calculate Fibonacci numbers. Make a syntax error on first try."}
    ],
    "retry_config": {"max_attempts": 5, "debug_mode": True},
    "max_attempts_before_tool_use": 2,
    "max_attempts_before_human": 4,
    "debug_tool_name": "perplexity-ask",
    "debug_tool_mcp_config": { "mcpServers": { "perplexity-ask": { /* perplexity tool definition */ }}},
    "validation": [
        {
            "type": "agent_task",
            "params": {
                "validation_model_alias": "max/code_tester_agent", # Claude agent for testing code
                "task_prompt_to_claude": "Code: '{CODE_TO_VALIDATE}'. Task: '{ORIGINAL_USER_PROMPT}'. Validate syntax and run test: fib(5) should be 5. Respond JSON: {\"validation_passed\": bool, \"reasoning\": str, \"details\": {\"syntax_ok\": bool, \"test_fib_5_pass\": bool}}",
                "mcp_config": { "mcpServers": { "python_executor": { /* tool def for running python */ }}},
                "success_criteria": {"all_true_in_details_keys": ["syntax_ok", "test_fib_5_pass"]}
            }
        }
    ],
    "original_user_prompt": "Write a function to calculate Fibonacci numbers." 
}

Okay, here is a README.md in raw Markdown, specifically tailored to explain the AI-assisted validation and iterative task execution features we've added to the Proof of Concept. This should help another AI (like your "Claude Code, the Code Executor") understand the mechanics.

You can save this as src/llm_call/proof_of_concept/README_AI_VALIDATION_PoC.md or similar.

Markdown

# LLM Call PoC: AI-Assisted Validation & Iterative Task Execution Framework

This document details an advanced layer of the `llm_call` Proof of Concept (PoC), focusing on how LLM responses can be validated using AI-driven strategies, including leveraging a "Claude Code agent" (referred to as the "agent" or "validator agent" below) to perform complex checks and tasks, potentially using its own suite of dynamically configured tools (MCPs). This framework also supports multi-stage retry logic for iterative refinement of LLM outputs.

## Core Concepts

1.  **Main LLM Call (`llm_call` function):**
    * The primary entry point for any LLM interaction, orchestrated by `litellm_client_poc.py`.
    * Accepts an `llm_config` dictionary detailing the model, messages, generation parameters, and specific validation requirements.

2.  **Dynamic Validation Strategies:**
    * The `llm_config` can include a `validation` key, which is a list of validation tasks to be performed on the response from the primary LLM call.
    * Each validation task is defined by a `type` (mapping to a registered `AsyncValidationStrategy` class) and `params` specific to that validator.
    * Example:
        ```json
        "validation": [
            {"type": "response_not_empty"},
            {"type": "json_string"},
            {"type": "agent_task", "params": {/* ... agent task specific params ... */}}
        ]
        ```

3.  **AI-Assisted Validation via "Agent Tasks":**
    * A key validation type is `"agent_task"`, implemented by `PoCAgentTaskValidator`.
    * This strategy allows delegating complex validation logic to a Claude Code agent instance (accessed via the `max/` proxy route, e.g., `max/validator_agent`).
    * **How it works:**
        1.  The Python `PoCAgentTaskValidator` receives the primary LLM's response.
        2.  It constructs a detailed **natural language prompt** for the Claude Code agent. This prompt includes:
            * The primary LLM's response (or relevant parts of it) as `{TEXT_TO_VALIDATE}` or `{CODE_TO_VALIDATE}`.
            * The original user prompt or task description (as `{ORIGINAL_USER_PROMPT}`) for context.
            * Specific instructions on *what to validate* and *what criteria to use*.
            * Crucially, instructions on **which of its available tools the Claude agent MUST or SHOULD use** to perform the validation (e.g., "You MUST use your 'perplexity-ask' tool to research X...").
            * A requirement for the Claude agent to respond ONLY in a specific structured JSON format detailing the validation outcome (e.g., `{"validation_passed": boolean, "reasoning": "...", "details": {...}}`).
        3.  The `PoCAgentTaskValidator` can also specify an `mcp_config` in its `params`. This `mcp_config` is sent to the `poc_claude_proxy_server.py`.
        4.  The proxy server writes this `mcp_config` to a `.mcp.json` file in the Claude CLI's working directory for *that specific validation call*. This dynamically enables and configures the tools the Claude agent needs for the validation task. If no `mcp_config` is sent by the validator, the proxy server defaults to enabling all its pre-defined tools for the Claude agent.
        5.  The `PoCAgentTaskValidator` then makes a recursive `llm_call` to the specified Claude agent (e.g., `max/validator_agent`).
        6.  The Claude agent executes the task, uses its (dynamically configured) tools as instructed in the prompt, and returns its findings in the requested JSON format.
        7.  The Python `PoCAgentTaskValidator` parses this JSON and determines the `ValidationResult` (pass/fail, error messages, suggestions).

4.  **Multi-Stage Retry Loop (`retry_with_validation_poc`):**
    * All primary LLM calls made via `llm_call` are wrapped in the `retry_with_validation_poc` loop (from `poc_retry_manager.py`).
    * This loop handles:
        * **Initial Attempts & Self-Correction:** If validation fails, the error messages and suggestions from the `ValidationResult` are appended to the conversation history, and the primary LLM is asked to try again, incorporating the feedback.
        * **Tool-Assisted Retry Stage:** The `llm_config` can specify `max_attempts_before_tool_use` and a `debug_tool_name` (e.g., "perplexity-ask") along with a `debug_tool_mcp_config`.
            * If validation continues to fail and this attempt threshold is reached, `retry_with_validation_poc` modifies the feedback prompt to the *primary LLM agent* (e.g., `max/code_generator_agent`), explicitly instructing it to use the `debug_tool_name` to research the errors before its next attempt.
            * For this tool-assisted retry, `retry_with_validation_poc` ensures that the `debug_tool_mcp_config` is passed to the Claude proxy, so the primary LLM agent has the specified debug tool (e.g., "perplexity-ask") enabled for that attempt.
        * **Human Escalation Stage:** The `llm_config` can specify `max_attempts_before_human`. If all retries (including tool-assisted ones) fail up to this limit, `retry_with_validation_poc` raises a `PoCHumanReviewNeededError`, signaling that the task could not be completed automatically.

5.  **Claude Agent's `llm_call_tool` (Recursive Capability):**
    * A core concept is that the Claude Code agent itself can be equipped with an MCP tool that allows *it* to make new LLM calls (using the same `llm_call` framework).
    * **Use Case Example:** If an `agent_task` validator asks Claude to find contradictions in a very large document (>200K tokens, exceeding its direct context window), the prompt to Claude would instruct it: "This document is very long. Use your 'llm_call_tool' to ask 'vertex_ai/gemini-1.5-pro-latest' (which has a 1M context window) to find contradictions in the full text and report its findings to you. Then, summarize those findings in your validation report."
    * **Mechanism:**
        1.  The `PoCAgentTaskValidator`'s `params` for the `agent_task` would include an `mcp_config` that defines the `llm_call_tool`. This tool's command would point to a Python script (e.g., `/app/tools/llm_call_delegator.py`) inside the Claude agent's Docker container.
        2.  The Claude agent, when processing the prompt, would decide to use this `llm_call_tool`.
        3.  The Claude CLI executes `/app/tools/llm_call_delegator.py`, passing parameters like the target model (`vertex_ai/gemini-1.5-pro-latest`), the large text (or a path to it), and the specific sub-task prompt (e.g., "find contradictions in this text").
        4.  The `llm_call_delegator.py` script then imports and uses the *same* `llm_call` function (from `litellm_client_poc.py` or eventually `core/caller.py`, assuming the `llm_call` package is installed in Claude's container) to make the call to Gemini.
        5.  Gemini's response is returned to the `llm_call_delegator.py`, which prints it to `stdout`.
        6.  The Claude CLI captures this output and uses it to complete its original validation task.

## How Users Specify Complex Validations

The user configures these advanced validations easily within their `llm_config`:

```python
# Example llm_config for an iterative coding task
coding_task_llm_config = {
    "model": "max/code_generator_agent", # Primary agent to generate code
    "messages": [
        {"role": "system", "content": "Generate Python code. Fix errors based on feedback."},
        {"role": "user", "content": "Write a function to calculate Fibonacci numbers. Make a syntax error on first try."}
    ],
    "retry_config": {"max_attempts": 5, "debug_mode": True},
    "max_attempts_before_tool_use": 2,
    "max_attempts_before_human": 4,
    "debug_tool_name": "perplexity-ask",
    "debug_tool_mcp_config": { "mcpServers": { "perplexity-ask": { /* perplexity tool definition */ }}},
    "validation": [
        {
            "type": "agent_task",
            "params": {
                "validation_model_alias": "max/code_tester_agent", # Claude agent for testing code
                "task_prompt_to_claude": "Code: '{CODE_TO_VALIDATE}'. Task: '{ORIGINAL_USER_PROMPT}'. Validate syntax and run test: fib(5) should be 5. Respond JSON: {\"validation_passed\": bool, \"reasoning\": str, \"details\": {\"syntax_ok\": bool, \"test_fib_5_pass\": bool}}",
                "mcp_config": { "mcpServers": { "python_executor": { /* tool def for running python */ }}},
                "success_criteria": {"all_true_in_details_keys": ["syntax_ok", "test_fib_5_pass"]}
            }
        }
    ],
    "original_user_prompt": "Write a function to calculate Fibonacci numbers." 
}
Key elements for the Claude Code Executor to understand:

Prompts are King: The behavior of the Claude Code agent (both as a primary worker and as a validator) is heavily guided by the natural language prompts it receives. These prompts will instruct it on the task, the criteria, and which of its available tools to use.
.mcp.json is Dynamic: The poc_claude_proxy_server.py writes the .mcp.json file in the Claude CLI's working directory for each call based on the mcp_config in the request payload. This means the set of tools available to Claude can change with each invocation if the client desires. If no mcp_config is sent, a default enabling all known tools is used.
Tool Execution: When Claude is prompted to "use tool X," it will look for "X" in its loaded .mcp.json and execute the defined command and args, with the specified env variables set for that tool's subprocess.
Structured JSON Output for Validation: When Claude acts as a validator (e.g., when called by PoCAgentTaskValidator), it's instructed to return its findings in a specific JSON format so the Python validation strategy can parse it.
llm_call_tool enables delegation: The ability for Claude to use a tool that itself uses the llm_call framework allows it to delegate sub-tasks (like processing very large contexts) to other, more suitable LLMs.
This PoC framework is designed to be a powerful testbed for these advanced, iterative, and tool-driven AI agent interactions.