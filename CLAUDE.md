# LLM CALL CONTEXT — CLAUDE.md

> **Inherits standards from global and workspace CLAUDE.md files with overrides below.**

## Project Context
**Purpose:** Universal LLM interface with validation and routing  
**Type:** Processing Spoke  
**Status:** Active  
**Pipeline Position:** Provides LLM access for all projects

## Project-Specific Overrides

### Special Dependencies
```toml
# LLM Call requires multiple LLM provider libraries
anthropic = "^0.25.0"
openai = "^1.3.0"
google-generativeai = "^0.3.0"
fastapi = "^0.104.0"
redis = "^5.0.0"
```

### Environment Variables
```bash
# .env additions for LLM Call
PROXY_PORT=8001
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
REDIS_URL=redis://localhost:6379
ENABLE_RL_ROUTING=true
DEFAULT_PROVIDER=claude
```

### Special Considerations
- **Multi-Provider Support:** Claude, GPT, Gemini routing
- **Response Validation:** 16 built-in validators for quality assurance
- **RL Optimization:** Provider selection based on performance metrics
- **Conversation Persistence:** Maintains context across provider switches

---

## License

MIT License — see [LICENSE](LICENSE) for details.