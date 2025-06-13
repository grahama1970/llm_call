
  1. Claude Proxy Server Location & Integration

  - Should poc_claude_proxy_server.py be a standalone
  FastAPI server, or integrate with the existing API in
   src/llm_call/core/api/?
   > shouldn't be a standalong runing file as would be normal with FastAPI servers, remeber this will eventuall be running a fast api server in one terminal and the python cli commands in another terminal. And,eventually, this will happen in a docker container so claude is in an isolated safe environnment
  - What port should it run on? (The docs mention
  localhost:3010 for LLM Call proxy)
  3010 is fin
  - Should the "max/" prefix routing be handled in the
  proxy server or in the router?
  look at the fastapi server in the proof of concept directory 

  2. MCP File Management

  - Where should .mcp.json files be written?
    - Claude CLI's working directory (where is this?)
    > yes, here. otherwise claude can't load the tools
    - A temp directory we control?
    - Project-specific directory?
  - Should we clean up .mcp.json files after each
  validation call
  > yes. Because each prompt might require different tools 
  - How do we handle concurrent calls that might
  overwrite each other's MCP configs?
  > For now we should use only one claude code instance/directory. In the next version, we'll create claudes in tmux sessions that we can have listen to a task queue as we discussed

  3. Tool Definitions & Paths

  - For llm_call_delegator.py - where should this live?
    - The docs mention /app/tools/ - is this a Docker
  container path?
  > its up to you. Look at the current directory. And ask-perplexity if you don't know
    - Should it be in src/llm_call/tools/?
  - For tools like perplexity-ask - are these npm
  packages we need to install?
  - What about python_executor and python_linter_tool -
   are these placeholder names or real tools?
   > I don;t think these are real tools yet

  4. Integration with Existing Code

  - Should I modify the existing poc_retry_manager.py
  or create a new version?
  - The existing poc_validation_strategies.py already
  has some validators - should I merge the v4 ones or
  replace?
  > merge them so we have a variety of validation strategies some clause, some pyton code heuristics
  - How should DEFAULT_ALL_TOOLS_MCP_CONFIG be defined?
   I see it's imported but not defined in the v4 files.
> Gemini answer the question here
  5. Testing Infrastructure

  - Do we have a real Claude CLI endpoint to test
  against?
  - Should I create mock implementations for testing?
  - Are the test images (six_animals.png,
  dummy_image.png) already in the project?

  6. Recursive LLM Call Implementation

  - When Claude uses llm_call_tool, should it import
  from litellm_client_poc.py or core/caller.py?
  - How do we prevent infinite recursion (Claude
  calling Claude calling Claude)?
  - Should there be a max recursion depth?

  7. Error Handling & Fallbacks

  - If MCP config write fails, should we:
    - Fail the validation?
    - Proceed without tools?
    - Use default tools?
  - If Claude proxy is unavailable, should we fall back
   to direct LiteLLM calls?

  These answers will help me implement correctly
  without making assumptions that might conflict with
  your architecture vision.