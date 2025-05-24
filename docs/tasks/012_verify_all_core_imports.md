# Task 012: Verify All Core Module Imports

## Objective
Systematically verify all core module imports using Claude Code CLI commands.

## Prerequisites
- SSH access with key: ~/.ssh/id_ed25519_wsl2
- Python virtual environment at .venv
- Redis running for cache initialization

## Commands to Execute

### 1. Initialize Environment
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "print(\"Environment ready\")"'"
```

### 2. Test Core Base Modules
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.base import ValidationResult, ValidationStrategy, BaseValidator; print(\"✅ base.py imports successful\")"'"

claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.caller import make_llm_request, preprocess_messages; print(\"✅ caller.py imports successful\")"'"

claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.router import resolve_route; print(\"✅ router.py imports successful\")"'"
```

### 3. Test Configuration Modules
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.config.loader import load_configuration; print(\"✅ config.loader imports successful\")"'"

claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.config.settings import Settings, RetrySettings; print(\"✅ config.settings imports successful\")"'"
```

### 4. Test Provider Modules
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.providers.base_provider import BaseLLMProvider; print(\"✅ base_provider imports successful\")"'"

claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.providers.litellm_provider import LiteLLMProvider; print(\"✅ litellm_provider imports successful\")"'"

claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.providers.claude_cli_proxy import ClaudeCLIProxyProvider; print(\"✅ claude_cli_proxy imports successful\")"'"
```

### 5. Test Validation Modules
```bash
claude code "ssh -i ~/.ssh/id_ed25519_wsl2 graham@192.168.86.49 'cd /home/graham/workspace/experiments/claude_max_proxy/ && source .venv/bin/activate && cd src && python -c "from llm_call.core.validation.builtin_strategies.basic_validators import ResponseNotEmptyValidator, JsonStringValidator; print(\"✅ validators import successful\")"'"
```

## Expected Results
All commands should output success messages without any ImportError exceptions.

## Success Criteria
- All 10+ import tests pass
- No ModuleNotFoundError or ImportError
- Each module prints its success message
