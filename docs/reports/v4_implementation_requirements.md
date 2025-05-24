# V4 Implementation Requirements for test_prompts.json

## Understanding the Test Requirements

The test_prompts.json file contains 30+ test cases that validate the COMPLETE v4 implementation with:

1. **Real Claude CLI execution** - Not mocked
2. **Real MCP tool usage** - Claude actually spawns and uses tools
3. **Real API calls** - To Perplexity, OpenAI, Vertex AI, etc.
4. **Real validation logic** - Claude agents make decisions based on actual tool results

## Critical Components That Must Work

### 1. Claude CLI with MCP Support
- Must be installed at the path specified in CLAUDE_CLI_PATH
- Must support automatic .mcp.json loading from working directory
- Must be able to spawn MCP server processes via npx

### 2. MCP Tool Execution
When Claude is instructed to "use your perplexity-ask tool":
- CLI spawns: `npx -y server-perplexity-ask`
- Establishes JSON-RPC 2.0 communication
- Passes search queries via JSON-RPC
- Receives real search results back

### 3. Proxy Server (poc_claude_proxy_server.py)
- Writes .mcp.json to Claude's working directory per request
- Executes Claude CLI with proper working directory
- Parses streaming JSON output
- Returns OpenAI-compatible responses

### 4. Validation Flow
For agent_task validators:
- Primary LLM call generates content
- PoCAgentTaskValidator makes recursive call to Claude agent
- Claude agent uses MCP tools as instructed
- Agent returns JSON validation result
- Validator parses and returns pass/fail

### 5. Environment Requirements

**Required**:
- `PERPLEXITY_API_KEY` - For perplexity-ask tool
- `ANTHROPIC_API_KEY` - If using direct Claude API
- Node.js/npm - For npx commands
- Network access - For API calls

**Optional but tested**:
- `OPENAI_API_KEY` - For GPT model tests
- `VERTEX_AI_PROJECT` - For Gemini tests
- `GITHUB_TOKEN` - For GitHub MCP tool
- `BRAVE_API_KEY` - For Brave search tool

## Test Case Example Flow

Taking `agent_validation_001_contradiction_check_flat_earth`:

1. **Primary call**: Sends flat earth text to validation
2. **Validation triggers**: PoCAgentTaskValidator activates
3. **MCP config written**: perplexity-ask tool configured
4. **Claude agent called**: "max/contradiction_expert_claude"
5. **Claude reads prompt**: "You MUST use your 'perplexity-ask' tool..."
6. **Claude uses tool**: Searches "Flat Earth theory common arguments"
7. **Real results**: Perplexity returns actual search results
8. **Claude analyzes**: Compares text against research
9. **JSON response**: `{"validation_passed": false, "reasoning": "...", ...}`
10. **Validation result**: Test passes because contradictions found

## What "Passing All Tests" Means

- Every test case in test_prompts.json executes successfully
- Real tools are used (not mocked)
- Real API responses (not hallucinated)
- Correct validation decisions based on actual data
- No crashes or timeouts
- Proper error handling for expected failures

## Verification Checklist

Before claiming tests pass:

- [ ] Claude CLI is installed and supports MCP
- [ ] All required environment variables are set
- [ ] Proxy server starts without errors
- [ ] Basic Claude call returns real response
- [ ] Claude can list available MCP tools
- [ ] Tool execution works (e.g., perplexity-ask returns results)
- [ ] Validation flow completes end-to-end
- [ ] All 30+ test cases run without intervention
- [ ] Results are reproducible

## Not Acceptable

- Mocking Claude responses
- Hardcoding test results
- Skipping tool execution
- Claiming success without real execution
- Partial implementation that "should work"

The v4 implementation is only complete when ALL test cases pass with REAL execution.