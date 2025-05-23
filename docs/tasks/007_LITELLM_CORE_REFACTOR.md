# Task 1: Refactor PoC into Core and Integrate Advanced Retry/Validation ⏳ Not Started

**Objective**: To transition the validated Proof of Concept (PoC) functionalities (Claude CLI proxying, standard LiteLLM calls, multimodal message preparation, JSON mode prompting) into the `src/llm_call/core/` directory, establishing a robust and extensible architecture. Subsequently, integrate the advanced retry and validation mechanisms from `core/retry.py` and `core/validation/` to enhance the reliability and correctness of LLM calls.

**Requirements**:
1.  All PoC functionalities (Claude proxy, direct LiteLLM for Vertex/OpenAI, multimodal preprocessing, JSON mode prompting) must be successfully migrated to the `core` structure.
2.  The `core/caller.py::make_llm_request` function will be the central entry point for all LLM calls.
3.  A provider pattern will be used within `core/caller.py` to delegate calls to specific implementations (Claude Proxy Provider, LiteLLM Provider).
4.  The `core/api/main.py` (FastAPI app) will serve as the production Claude CLI proxy, incorporating logic from `poc_claude_proxy_server.py`.
5.  The `core/retry_manager.py::retry_with_validation` function will be used to wrap actual LLM/proxy execution calls made by the providers or `core/caller.py`.
6.  At least two basic validation strategies (e.g., `ResponseNotEmptyValidator`, `JsonStringValidator`) will be implemented and used.
7.  All calls, whether to the Claude proxy or direct LiteLLM, must go through the `retry_with_validation` loop.
8.  The system must gracefully handle the `skip_claude_multimodal` route identified in the PoC.
9.  Logging will be standardized using `core/utils/logging_setup.py` (Loguru).
10. Configuration will be managed via `core/config/loader.py` and `settings.py`.

## Overview

This task is critical for moving beyond the PoC stage to a more production-ready LLM interaction library. It involves restructuring existing `core` files and integrating the PoC's working code into this new structure. The primary outcome will be a unified `make_llm_request` function in `core/caller.py` that handles different LLM providers and incorporates sophisticated retry and response validation logic. This will significantly improve the reliability and maintainability of the `llm_call` package.

**IMPORTANT**:
1.  Each sub-task MUST include the creation of a conceptual verification report outline in `/docs/reports/` (since I cannot generate actual files/outputs). This outline should detail what would be tested and what kind of outputs would be expected.
2.  Task 6 (Final Verification) enforces MANDATORY iteration on ALL incomplete tasks. The agent MUST continue working until 100% completion of conceptual design and code structure is achieved - no partial completion is acceptable.

## Research Summary

Previous interactions have established working PoC client and server scripts demonstrating:
* HTTP client calls to a FastAPI server.
* FastAPI server using `subprocess.Popen` to execute the Claude CLI and stream/capture its JSON output.
* Conditional routing logic in a Python script to choose between calling the local FastAPI proxy (for `max/` models) or making standard LiteLLM calls (for `vertex_ai/`, `openai/` models).
* Preprocessing of messages for JSON mode and multimodal inputs (image path to Base64 conversion for LiteLLM-compatible models, and skipping multimodal for Claude CLI).
* Basic retry mechanisms using `tenacity`.
* A structured `core` directory with components for advanced retry/validation, providers, and utilities.
* The Claude CLI uses its default model and does not accept a model selection flag per call.
* Loguru colorization in Uvicorn requires careful sink configuration.

## MANDATORY Research Process

**CRITICAL REQUIREMENT**: For EACH implementation sub-task below that involves creating or significantly modifying Python code, the agent (myself) MUST conceptually perform the following (as I cannot execute tools):

1.  **Conceptually use `perplexity_ask`** to research (based on my existing knowledge and simulated search):
    * Current best practices (2025-current) for the specific Python patterns being implemented (e.g., robust subprocess management, FastAPI error handling, provider pattern, retry logic).
    * Production implementation patterns for similar functionalities (e.g., LLM gateways, API call wrappers).
    * Common pitfalls and solutions related to `asyncio`, `httpx`, `litellm`, `FastAPI`, `subprocess`.
    * Performance optimization techniques for I/O-bound operations.

2.  **Conceptually use `WebSearch`** to find (based on my existing knowledge and simulated search):
    * GitHub repositories with working code for similar patterns (e.g., Python projects using LiteLLM with extensive provider configurations, FastAPI applications managing external processes).
    * Real production examples of LLM interaction layers.
    * Popular library implementations for retry mechanisms or validation.

3.  **Document all conceptual findings** in task report outlines:
    * Simulated links to source repositories or design patterns.
    * Code snippets illustrating best practices or solutions to potential issues.
    * Conceptual performance characteristics or integration patterns.

4.  **DO NOT proceed with code generation without this conceptual research**:
    * No purely theoretical implementations where established patterns exist.
    * Prioritize patterns that enhance robustness, testability, and maintainability.

Example Conceptual Research Queries (What I would do if I had the tools):
perplexity_ask: "python robust subprocess management asyncio best practices 2025"
perplexity_ask: "fastapi dependency injection for provider pattern python"
perplexity_ask: "litellm advanced routing and configuration patterns production"
WebSearch: "site:github.com python llm gateway example"
WebSearch: "site:github.com fastapi litellm provider pattern"


## Implementation Tasks (Ordered by Priority/Complexity)

### Task 1: Setup Core Utilities and Configuration ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Objective**: Establish foundational utilities for logging and configuration that will be used throughout the `core` module and the application.

**Research Requirements**:
- [ ] `perplexity_ask`: Best practices for Loguru setup in a library/application context.
- [ ] `perplexity_ask`: Pydantic settings management best practices.
- [ ] `WebSearch`: Examples of `pyproject.toml` driven configuration loading with Pydantic.
- [ ] `WebSearch`: GitHub examples of Loguru configuration for FastAPI/Uvicorn applications.

**Implementation Steps**:
- [ ] 1.1 Create `core/utils/logging_setup.py`:
    - Define a function `setup_logging()` that configures Loguru (e.g., console sink with `sys.stderr` and `colorize=True`, optional file sink).
    - Allow customization of log levels via parameters or environment variables.
    - Ensure it can be called once at application startup.
- [ ] 1.2 Create `core/config/settings.py`:
    - Define Pydantic models for various configurations (e.g., `LLMSettings`, `RetrySettings`, `ClaudeProxySettings`, `VertexAISettings`, `OpenAISettings`, `APISettings`).
    - Include fields for API keys (to be loaded from env), model names, proxy URLs, CLI paths, workspace directories.
    - Use `BaseSettings` for environment variable loading if appropriate.
- [ ] 1.3 Create `core/config/loader.py`:
    - Define a function `load_configuration()` that:
        - Loads `.env` file using `python-dotenv`.
        - Loads a primary YAML/JSON configuration file (e.g., `config.yml` in project root or `src/llm_call/config/`).
        - Populates and validates the Pydantic settings models.
        - Returns a global configuration object or settings instances.
- [ ] 1.4 Update `core/__init__.py`:
    - Call `setup_logging()` to initialize logging when `core` is imported.
    - Potentially instantiate and expose a global config object loaded by `core/config/loader.py`.
- [ ] 1.5 Create verification report outline for Task 1.
    - Sections for: Log output examples, Pydantic model definitions, config loading example, environment variable interaction.

**Technical Specifications**:
- Loguru configured as the sole logger for `llm_call`.
- Pydantic models for type-safe configuration.
- Configuration loadable from `.env` and a primary config file.

**Verification Method (Conceptual)**:
- Show example Loguru output with correct formatting.
- Display Pydantic model definitions.
- Describe how `load_configuration()` would merge env vars and file settings.

### Task 2: Implement Core API Server (Claude Proxy) ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Objective**: Refactor `poc_claude_proxy_server.py` into `core/api/main.py` and `core/api/handlers.py` to create a robust, configurable Claude CLI proxy service.

**Research Requirements**:
- [ ] `perplexity_ask`: FastAPI best practices for structuring larger applications (routers, dependencies).
- [ ] `perplexity_ask`: Secure and efficient subprocess management in an async FastAPI application.
- [ ] `WebSearch`: GitHub examples of FastAPI acting as a proxy to CLI tools.

**Implementation Steps**:
- [ ] 2.1 Create `core/api/main.py`:
    - Define the FastAPI `app` instance.
    - Include routers for endpoints (e.g., `/v1/chat/completions`).
    - Handle application startup/shutdown events if needed (e.g., for initializing resources).
    - Use the global logger and configuration established in Task 1.
- [ ] 2.2 Create `core/api/handlers.py`:
    - Move the logic from `poc_claude_proxy_server.py :: poc_chat_completions_endpoint` here.
    - Move `execute_claude_cli_for_poc` (or a refined version) here, or call it if it's moved to a Claude-specific utility within `core`.
    - The handler should take `Request` object, extract messages and model info.
    - It should use configured `CLAUDE_CLI_PATH` and workspace directory from global config.
    - It should dynamically use the `model` field from the client's request in the response it sends back (as implemented in PoC).
- [ ] 2.3 Configuration Integration:
    - Ensure `CLAUDE_CLI_PATH` and workspace path are read from the global configuration (Task 1).
- [ ] 2.4 Error Handling:
    - Implement robust error handling for CLI execution failures, timeouts, etc., returning appropriate HTTP status codes and error messages.
- [ ] 2.5 Create verification report outline for Task 2.
    - Sections for: FastAPI route definition, handler logic for Claude CLI call, example `curl` request and expected successful/error JSON responses, sample server logs showing a request being processed.

**Technical Specifications**:
- FastAPI app runnable with Uvicorn.
- `/v1/chat/completions` endpoint compatible with OpenAI spec for basic chat.
- Uses configured Claude CLI path.

**Verification Method (Conceptual)**:
- Show `curl` command to test the endpoint.
- Display example successful JSON response.
- Display example error JSON response.
- Show server logs for a request.

### Task 3: Implement Core Caller and Providers ⏳ Not Started

**Priority**: HIGH | **Complexity**: HIGH | **Impact**: HIGH

**Objective**: Create `core/caller.py` with `make_llm_request` and implement the provider pattern for routing to the Claude Proxy and standard LiteLLM.

**Research Requirements**:
- [ ] `perplexity_ask`: Python provider/strategy design pattern examples.
- [ ] `perplexity_ask`: Best practices for abstracting external API calls.
- [ ] `WebSearch`: LiteLLM examples for various providers (Vertex, OpenAI, Anthropic direct).
- [ ] `WebSearch`: `httpx` usage patterns for robust async client calls.

**Implementation Steps**:
- [ ] 3.1 Define `core/providers/base.py`:
    - Create an abstract `BaseLLMProvider` class with an `async def complete(self, params: Dict[str, Any]) -> Any;` method.
- [ ] 3.2 Implement `core/providers/claude_cli_proxy.py`:
    - Create `ClaudeCLIProxyProvider(BaseLLMProvider)`.
    - Its `complete` method will use `httpx.AsyncClient` to call the `core/api/main.py` service (using configured URL).
    - It will take prepared parameters (payload) for the proxy.
- [ ] 3.3 Implement `core/providers/litellm_provider.py`:
    - Create `LiteLLMProvider(BaseLLMProvider)`.
    * Its `complete` method will call `await litellm.acompletion(**params)`.
    * It will handle general LiteLLM parameters.
- [ ] 3.4 Implement `core/router.py` (refine existing):
    * Function `resolve_route(llm_config: Dict[str, Any]) -> Tuple[Type[BaseLLMProvider], Dict[str, Any]]`.
    * Takes `llm_config`.
    * Returns the appropriate provider class (e.g., `ClaudeCLIProxyProvider`, `LiteLLMProvider`) and the prepared `api_params` for that provider.
    * It will use `model_name.startswith("max/")` for Claude proxy routing.
    * It will prepare `api_params` for LiteLLM, ensuring correct model strings and provider-specific keys like `vertex_project`, `vertex_location` (pulled from config/env if not in `llm_config`).
- [ ] 3.5 Implement `core/caller.py :: make_llm_request(llm_config: Dict[str, Any])`:
    * This function will be the main entry point.
    * **Step 1: Pre-processing (JSON instructions, Multimodal formatting):**
        * Create a helper function (e.g., `_prepare_messages_and_params`) that takes `llm_config`, performs a deepcopy of messages, injects JSON instructions if `response_format={"type": "json_object"}` is present, and calls `format_multimodal_messages` (from `core/utils/multimodal_utils.py`) if `is_multimodal` is true.
        * This helper should also handle the "skip\_claude\_multimodal" case early if the model is `max/` and multimodal.
    * **Step 2: Routing:**
        * Call `router.resolve_route()` with the (potentially modified by pre-processing) `llm_config` to get the provider instance and final `api_params`.
    * **Step 3: Execution (placeholder before retry/validation integration):**
        * Call `provider_instance.complete(api_params=final_api_params)`.
        * For now, this raw call is fine. Retry/validation will wrap this later.
- [ ] 3.6 Create verification report outline for Task 3.
    - Sections for: Provider class definitions, `router.resolve_route` logic, `caller.make_llm_request` structure, example calls to `make_llm_request` for "max/" and "vertex_ai/" models, and the conceptual parameters passed to the respective providers.

**Technical Specifications**:
- `make_llm_request` successfully routes to Claude proxy provider or LiteLLM provider.
- Message preprocessing (JSON, multimodal) is applied before routing.
- Parameters are correctly formatted for each provider.

**Verification Method (Conceptual)**:
- Show example `llm_config` inputs.
- Trace how `make_llm_request` and `router.resolve_route` process these.
- Show the conceptual parameters that would be passed to `ClaudeCLIProxyProvider.complete` and `LiteLLMProvider.complete`.

### Task 4: Integrate Retry and Basic Validation into Core Caller ⏳ Not Started

**Priority**: HIGH | **Complexity**: MEDIUM | **Impact**: HIGH

**Objective**: Wrap the provider calls within `core/caller.py::make_llm_request` with the `core/retry_manager.py::retry_with_validation` mechanism, using basic validation strategies.

**Research Requirements**:
- [ ] `perplexity_ask`: Best practices for integrating retry loops with pluggable validation.
- [ ] `WebSearch`: Examples of Pydantic for defining `response_format` in LiteLLM and validating against it.

**Implementation Steps**:
- [ ] 4.1 Define Basic Validators:
    - In `core/validation/builtin_strategies/basic_validators.py`, implement:
        - `ResponseNotEmptyValidator(AsyncValidationStrategy)`
        - `JsonStringValidator(AsyncValidationStrategy)` (checks if content is valid JSON string)
- [ ] 4.2 Register Validators:
    - Ensure these validators are registered with the `StrategyRegistry` in `core/validation/strategies.py` (e.g., using the `@validator` decorator).
- [ ] 4.3 Modify `core/providers/` methods' signatures:
    - The `complete` method in `ClaudeCLIProxyProvider` and `LiteLLMProvider` should be adjusted to accept `messages: List[Dict[str, str]], response_format: Optional[Any] = None, **kwargs` to match the signature expected by the `llm_call_func` argument of `retry_with_validation`. Inside `complete`, these will be assembled into the provider-specific payload/params.
- [ ] 4.4 Update `core/caller.py::make_llm_request`:
    * After `router.resolve_route()` gives you the `provider_instance` and the initial `prepared_params` (which includes model string, temperature, etc., but *not yet* the messages or response_format that `retry_with_validation` expects as direct arguments for its `llm_call_func`):
        * Extract `processed_messages` and `response_format_for_provider` from the output of your pre-processing step (Task 3.5, Step 1).
        * Instantiate `RetryConfig` (from `core/retry_manager.py`).
        * Determine `validation_strategies` to use (from `llm_config` or defaults like `[ResponseNotEmptyValidator()]`). If `response_format_for_provider` indicates JSON, add `JsonStringValidator()`.
        * The `llm_call_func` for `retry_with_validation` will be `provider_instance.complete`.
        * Call `retry_with_validation` like so:
            ```python
            # Inside make_llm_request, after getting provider, processed_messages, 
            # response_format_for_provider, and other_llm_params
            retry_config_instance = RetryConfig(**llm_config.get("retry_config", {}))
            # ... determine strategies_to_use ...

            final_response = await retry_with_validation(
                llm_call_func=provider_instance.complete,
                messages=processed_messages,
                response_format=response_format_for_provider,
                validation_strategies=strategies_to_use,
                config=retry_config_instance,
                **other_llm_params # (e.g., model, temperature, max_tokens specific to the provider)
            )
            return final_response
            ```
- [ ] 4.5 Create verification report outline for Task 4.
    - Sections for: Definitions of PoC validators, how `retry_with_validation` is called in `caller.py`, example logs showing retry attempts and validation success/failure for both Claude proxy and LiteLLM routes.

**Technical Specifications**:
- LLM calls are wrapped in `retry_with_validation`.
- Basic validation for empty response and JSON format (if requested) is applied.
- Retries occur upon validation failure or specified exceptions.

**Verification Method (Conceptual)**:
- Show `llm_config` that triggers JSON validation.
- Simulate an LLM response that fails validation (e.g., empty or non-JSON).
- Show conceptual logs of `retry_with_validation` attempting retries and validation steps.

### Task 5: Testing and Minor Utilities Integration ⏳ Not Started

**Priority**: MEDIUM | **Complexity**: MEDIUM | **Impact**: MEDIUM

**Objective**: Ensure the new core components are testable and integrate remaining small utilities from PoC or `core/utils`.

**Implementation Steps**:
- [ ] 5.1 Review `core/utils/` for remaining PoC utilities:
    - `initialize_litellm_cache.py`: Integrate its call into `core/__init__.py` or `core/config/loader.py` (called once, using settings from `core/config/settings.py`).
    - `file_utils.py`: `get_project_root` might be used by `core/config/loader.py`. `load_text_file` is a general util, can stay in `core/utils/common_utils.py` or a refined `file_utils.py`.
    - `json_utils.py`: Already a core util. Ensure `clean_json_string` is used by `retry_with_validation` if a "repair JSON" step is added to the validation feedback loop, or if a validator uses it.
- [ ] 5.2 Create Test Stubs/Scripts:
    - Write a simple test script in `tests/` (e.g., `tests/test_core_caller.py`) that calls `core/caller.py::make_llm_request` with configurations for:
        - Claude proxy (text).
        - Claude proxy (multimodal, expecting skip/error).
        - LiteLLM Vertex AI (text).
        - LiteLLM OpenAI (multimodal).
        - LiteLLM OpenAI (JSON response requested).
    - These tests will initially rely on environment variables for API keys and the running `core/api/main.py` for the Claude proxy part. Mocking can be introduced later.
- [ ] 5.3 Create verification report outline for Task 5.
    - Sections for: Test script structure, example configurations used for testing each path, expected (conceptual) outputs or logs from these test calls.

**Technical Specifications**:
- Basic test calls for all major paths in `core/caller.py`.
- Key utilities from PoC are integrated or have a clear home.

**Verification Method (Conceptual)**:
- Show example test script.
- Describe expected behavior for each test case.

### Task 6: Completion Verification and Iteration ⏳ Not Started

**Priority**: CRITICAL | **Complexity**: LOW | **Impact**: CRITICAL

**Implementation Steps**:
- [ ] 6.1 Review all conceptual task report outlines from Tasks 1-5.
    - Create checklist of all implemented code structures and functionalities.
    - Identify any conceptual gaps or inconsistencies in the proposed code designs.
- [ ] 6.2 Create task completion matrix (conceptual for now).
    - Build comprehensive status table.
    - Mark each sub-task's design as COMPLETE/INCOMPLETE.
    - List specific design questions or areas needing more detail.
- [ ] 6.3 Iterate on incomplete conceptual tasks.
    - Revisit previous task designs if issues are found.
    - Refine code structures and function signatures.
- [ ] 6.4 Final comprehensive validation of the design.
    - Mentally walk through the data flow for all test cases.
    - Ensure all requirements from the main task objective are addressed in the design.
- [ ] 6.5 Create final summary report outline.
    - Include the conceptual completion matrix.
    - Document the proposed final structure of `core`.
    - List any remaining design decisions or future considerations.
- [ ] 6.6 Mark task complete only if ALL sub-task designs are conceptually sound and complete.

**Technical Specifications**:
- Conceptual design for all core components is complete and coherent.
- All PoC learnings are addressed.

**Verification Method (Conceptual)**:
- Completion matrix showing 100% conceptual design completion.
- Final proposed file structure and key function signatures.

---
## Usage Table (Conceptual for the Core Library)

| Function / Component         | Description                                                                    | Example Usage (Conceptual)                                                                 | Expected Output Type (Conceptual)     |
|------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|---------------------------------------|
| `setup_logging()`            | Initializes Loguru                                                             | `from llm_call.core.utils.logging_setup import setup_logging; setup_logging()`             | Logger configured                     |
| `load_configuration()`       | Loads and merges .env, YAML/JSON config into Pydantic models                   | `from llm_call.core.config import loader; config = loader.load_configuration()`            | Pydantic Settings Object              |
| `core/api/main.py` (run)     | Starts the Claude CLI Proxy FastAPI server                                     | `uvicorn llm_call.core.api.main:app --port 3010`                                           | FastAPI server running                |
| `make_llm_request(config)`   | Central function to make any LLM call (proxy or direct) with retry/validation  | `from llm_call.core.caller import make_llm_request; response = await make_llm_request(llm_cfg)` | `ModelResponse` or `dict` or `None` |
| `BaseLLMProvider.complete()` | Abstract method for provider execution                                         | `await provider.complete(messages=msgs, model="x", ...)`                                   | Provider-specific response            |
| `retry_with_validation()`    | Core retry/validation loop                                                     | Used internally by `make_llm_request`                                                      | Validated response or exception       |

## Version Control Plan (Conceptual)

- **Initial Commit for Refactor**: Create task-1-core-refactor-start tag before beginning Task 1.
- **Feature Commits**: After each major sub-task (e.g., `core-logging-config-done`, `core-api-server-implemented`, `core-caller-with-providers-done`, `core-retry-validation-integrated`).
- **Final Tag**: Create `task-1-core-refactor-complete` after all sub-tasks of Task 1 (this main task) pass conceptual verification and the design is stable.

## Resources

**Python Packages (Core to this refactor)**:
- `fastapi`
- `uvicorn`
- `httpx`
- `litellm`
- `loguru`
- `pydantic`
- `python-dotenv`
- (Your existing `image_processing_utils`, `multimodal_utils`, etc.)

**Documentation**:
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Loguru Documentation](https://loguru.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [HTTPX Documentation](https://www.python-httpx.org/)

## Progress Tracking

- Start date: TBD
- Current phase: Planning this refactor
- Expected completion: TBD
- Completion criteria: `core/caller.py::make_llm_request` successfully orchestrates calls with retry and validation for both Claude proxy and direct LiteLLM routes, using the new core structure.

---
This task list should now be easily copyable into a Markdown file for your records and use.