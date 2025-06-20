# Slash Command Setup Guide

This guide explains how to configure the llm_call slash commands and where to place configuration files.

## File Locations

The slash commands look for configuration files in the following order:

### 1. Environment File (.env)

The commands check these locations in order:
1. Path specified in `LLM_CALL_ENV_FILE` environment variable
2. `/home/graham/workspace/experiments/llm_call/.env` (default project location)
3. `~/.llm_call/.env` (user home directory)
4. `.env` in the same directory as the slash command

### 2. Service Account Files

Google Vertex AI service account credentials are referenced in the .env file:
```bash
GOOGLE_APPLICATION_CREDENTIALS=/path/to/vertex_ai_service_account.json
```

## Recommended Setup Options

### Option 1: Keep Files in Project Directory (Current Setup)
- **Pros**: All config in one place, easy to manage with the project
- **Cons**: Hardcoded paths, less portable

```bash
/home/graham/workspace/experiments/llm_call/
├── .env
└── vertex_ai_service_account.json
```

### Option 2: User Home Directory (Recommended for Personal Use)
- **Pros**: Portable, secure, works across projects
- **Cons**: Need to remember to update when switching projects

```bash
~/.llm_call/
├── .env
└── vertex_ai_service_account.json
```

Then update your .env:
```bash
GOOGLE_APPLICATION_CREDENTIALS=~/.llm_call/vertex_ai_service_account.json
```

### Option 3: Environment Variable Override (Most Flexible)
- **Pros**: Can switch configs easily, good for multiple projects
- **Cons**: Need to set environment variable

```bash
export LLM_CALL_ENV_FILE=/path/to/your/project/.env
```

### Option 4: Slash Command Directory (Portable)
- **Pros**: Config travels with commands, self-contained
- **Cons**: May expose secrets if commands directory is shared

```bash
~/.claude/commands/
├── llm_call
├── llm_call_multimodal
├── llm
├── .env
└── vertex_ai_service_account.json
```

## Security Best Practices

1. **Never commit** `.env` or service account files to git
2. **Set appropriate permissions**:
   ```bash
   chmod 600 ~/.llm_call/.env
   chmod 600 ~/.llm_call/vertex_ai_service_account.json
   ```
3. **Use different service accounts** for different projects/environments
4. **Rotate API keys** regularly

## Quick Setup

For most users, we recommend Option 2:

```bash
# Create config directory
mkdir -p ~/.llm_call

# Copy configuration files
cp /home/graham/workspace/experiments/llm_call/.env ~/.llm_call/
cp /home/graham/workspace/experiments/llm_call/vertex_ai_service_account.json ~/.llm_call/

# Update the service account path in .env
sed -i 's|/home/graham/workspace/experiments/llm_call/|~/.llm_call/|g' ~/.llm_call/.env

# Set permissions
chmod 600 ~/.llm_call/.env
chmod 600 ~/.llm_call/vertex_ai_service_account.json
```

## Debugging

Run slash commands with `--debug` to see which .env file is being loaded:

```bash
/llm_call --debug --query "test" --model max/opus
```

## Environment Variables Used

Key environment variables loaded from .env:
- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Anthropic API access (removed for Claude Max OAuth)
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Vertex AI service account
- `OLLAMA_API_BASE` - Ollama server URL
- `CLAUDE_PROXY_EXECUTION_MODE` - "local" or "proxy"
- `CLAUDE_PROXY_LOCAL_CLI_PATH` - Path to Claude CLI binary