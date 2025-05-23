# LLM Call - Proof of Concept (PoC)

This directory contains the Proof of Concept (PoC) scripts for the `llm_call` project. The primary goal of this PoC is to establish and test a flexible system for making calls to various Large Language Models (LLMs), including a locally proxied Claude instance (via its CLI) and other models supported by LiteLLM (like OpenAI and Google Vertex AI). A key feature being prototyped is dynamic, AI-assisted validation of LLM responses with configurable retry mechanisms.

## Core Components of the PoC

1.  **PoC Claude Proxy Server (`poc_claude_proxy_server.py`):**
    * A standalone FastAPI application that acts as an HTTP proxy to a locally installed Claude Command Line Interface (CLI) tool.
    * **Functionality:**
        * Listens for OpenAI-compatible chat completion requests on an HTTP endpoint (e.g., `http://127.0.0.1:8001/v1/chat/completions`).
        * Receives the prompt and system message from the client.
        * **Dynamically Configures Claude CLI Tools:** It can accept an `mcp_config` (Multi-Claude Protocol configuration) in the request payload.
            * If `mcp_config` is provided, it writes a `.mcp.json` file to the Claude CLI's working directory, enabling specific tools for that particular CLI invocation.
            * If no `mcp_config` is provided by the client, it defaults to writing a `.mcp.json` file that enables a predefined set of "all available" tools (like `perplexity-ask`, `desktop-commander`, etc.).
        * Executes the Claude CLI tool as a subprocess (`subprocess.Popen`), passing the prompt, system prompt, and ensuring the CLI uses the (dynamically) created `.mcp.json` from its current working directory.
        * Captures the `stdout` from the Claude CLI (which is expected to be `stream-json` containing the LLM's response).
        * Parses the final result from the Claude CLI's output.
        * Cleans up the dynamically created `.mcp.json` file after the CLI call.
        * Returns an OpenAI-compatible JSON response to the calling client, echoing the model name requested by the client in its response.
    * **Purpose:** To allow other services or scripts to interact with the Claude CLI via a standard HTTP API, and to test dynamic tool/MCP configuration for the Claude agent.

2.  **PoC LLM Client (`litellm_client_poc.py`):**
    * This script serves as the primary testbed for the LLM calling logic.
    * **Key Functions:**
        * `determine_llm_route_and_params(llm_config)`:
            * Inspects the `model` field in the input `llm_config`.
            * If the model name starts with `max/` (e.g., `max/my-claude-agent`), it routes the call to the local PoC Claude Proxy Server.
            * For other model names (e.g., `vertex_ai/gemini-...`, `openai/gpt-4o-mini`), it routes the call to be handled by standard LiteLLM.
            * Performs message preprocessing:
                * Injects system prompts to request JSON output if `llm_config` specifies `response_format={"type": "json_object"}`.
                * Handles multimodal messages by calling `is_multimodal` and `format_multimodal_messages` (from `core/utils/multimodal_utils.py`) to process local image paths into Base64 data URIs for LiteLLM-compatible models.
                * Recognizes that the `max/` (Claude CLI) route does not support image inputs and flags it for skipping.
            * Prepares the necessary parameters (`llm_call_kwargs`) for the respective execution path (proxy or LiteLLM). This includes passing through `mcp_config` if present in the original `llm_config` for proxy calls.
        * `_execute_proxy_call_for_retry_loop(messages, response_format, **kwargs)`:
            * Makes an asynchronous HTTP POST request to the `poc_claude_proxy_server.py` using `httpx`.
            * The payload includes messages and any other relevant parameters (like `model`, `temperature`, `mcp_config`).
        * `_execute_litellm_call_for_retry_loop(messages, response_format, **kwargs)`:
            * Makes an asynchronous call to `litellm.acompletion` with the prepared parameters.
            * Handles provider-specific configurations (like Vertex AI project/location from environment variables if not in `llm_config`).
        * `llm_call(llm_config)`:
            * The main orchestrating function.
            * Uses `determine_llm_route_and_params` to get the route and processed parameters.
            * **Dynamically Loads Validation Strategies:** Reads a `validation` list from the input `llm_config`. Each item in the list specifies a `type` (name of a validator) and `params` for that validator.
            * Instantiates the required `AsyncValidationStrategy` classes (defined in `poc_validation_strategies.py`).
            * Injects itself (`llm_call`) into any AI-assisted validators so they can make recursive/delegated LLM calls.
            * Uses the `retry_with_validation` function (imported from `llm_call.core.retry`) to execute the chosen call (`_execute_proxy_call_for_retry_loop` or `_execute_litellm_call_for_retry_loop`).
            * `retry_with_validation` handles the retry loop (e.g., up to `N` retries), calls the validation strategies after each attempt, and if validation fails, it appends the error/suggestions to the message history to instruct the LLM to "fix it" on the next attempt.
        * `main_client_runner()`: Contains example test cases demonstrating:
            * Text-based calls to the Claude proxy.
            * Text-based calls to Vertex AI Gemini via LiteLLM.
            * Multimodal calls to OpenAI GPT-4o-mini via LiteLLM (with local image processing).
            * Attempted multimodal calls to the Claude proxy (which are correctly skipped).
            * AI-assisted validation using the `PoCAIContradictionValidator`, where the validator itself calls the Claude proxy (with a dynamic MCP config for the "perplexity-ask" tool) to analyze text (e.g., a Wikipedia article).

3.  **PoC Validation Strategies (`poc_validation_strategies.py`):**
    * This new file houses `AsyncValidationStrategy` implementations for the PoC.
    * **Python-based validators:**
        * `PoCResponseNotEmptyValidator`: Checks if the LLM response content is not empty.
        * `PoCJsonStringValidator`: Checks if the LLM response content is a valid JSON string.
        * `PoCFieldPresentValidator`: Checks if a specified field is present in a JSON response.
    * **AI-assisted validators:**
        * `PoCAgentTaskValidator`: A generic validator that takes a `task_prompt_to_claude` and an optional `mcp_config`. It calls the Claude proxy, instructing the Claude agent to perform the specified task (potentially using tools defined in the `mcp_config`) and report back in a structured JSON format indicating success/failure and details.
        * `PoCAIContradictionValidator`: A specialized AI validator that instructs the Claude agent to use its "perplexity-ask" MCP tool to find contradictions in a given text (e.g., a Wikipedia article on "Flat Earth" or "Cold Fusion").
    * `poc_strategy_registry`: A simple dictionary mapping string names to these validator classes, used by `llm_call` to instantiate them dynamically based on the user's `llm_config`.

## How to Run the PoC

1.  **Prerequisites:**
    * Ensure Python 3.10+ is installed.
    * Install dependencies from `pyproject.toml` using `uv pip install -e .[dev]`. This includes `fastapi`, `uvicorn`, `httpx`, `litellm`, `loguru`, `python-dotenv`, `wikipedia`, `Pillow`.
    * Ensure the Claude CLI is installed and the `CLAUDE_CLI_PATH` in `poc_claude_proxy_server.py` (or the corresponding environment variable) is correct.
    * Set up a `.env` file in the project root (`claude_max_proxy/.env`) with necessary API keys and configurations:
        * `GOOGLE_APPLICATION_CREDENTIALS=path/to/your/vertex_service_account.json`
        * `LITELLM_VERTEX_PROJECT=your-gcp-project-id`
        * `LITELLM_VERTEX_LOCATION=your-gcp-region`
        * `OPENAI_API_KEY=sk-...`
        * `PERPLEXITY_API_KEY_FOR_MCP=pplx-...` (if the perplexity tool in `DEFAULT_ALL_TOOLS_MCP_CONFIG` uses this)
        * Any other environment variables needed by your MCP tools.

2.  **Start the PoC Claude Proxy Server:**
    Open a terminal, navigate to the project root (`claude_max_proxy/`), and run:
    ```bash
    uv run python src/llm_call/proof_of_concept/poc_claude_proxy_server.py
    ```
    This will start the FastAPI server, typically on `http://127.0.0.1:8001`.

3.  **Run the PoC Client Script:**
    Open another terminal, navigate to the project root, and run:
    ```bash
    uv run python src/llm_call/proof_of_concept/litellm_client_poc.py
    ```

## Expected Behavior

* The **server terminal** will show Uvicorn startup logs and then logs for each incoming request from the client, including details of the Claude CLI execution and any MCP files written/removed.
* The **client terminal** will show logs for each test case:
    * The configuration being used.
    * Which route is taken (Proxy or LiteLLM).
    * Details of any validation steps being performed (if `debug_mode` is enabled in `RetryConfig` or if validators log verbosely).
    * The final response from the LLM or the proxy.
    * For the "skip\_claude\_multimodal" case, it will show the informative error message.
    * For the AI-assisted validation (e.g., contradiction check), it will show the logs from the validator making its call to the Claude agent, and then the validation outcome.

This PoC aims to validate the end-to-end architecture, including dynamic routing, message preprocessing, dynamic tool configuration for the Claude agent, and the integration of a sophisticated retry/validation loop.