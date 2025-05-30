# Terminal Commands

Quick reference for common terminal commands used with the LLM Call project.

## Project Navigation

/cd-project
Description: Navigate to project root
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
```

/cd-src
Description: Navigate to source code
```bash
cd /home/graham/workspace/experiments/claude_max_proxy/src/llm_call
```

/cd-tests
Description: Navigate to tests
```bash
cd /home/graham/workspace/experiments/claude_max_proxy/tests
```

/cd-poc
Description: Navigate to proof of concept
```bash
cd /home/graham/workspace/experiments/claude_max_proxy/src/llm_call/proof_of_concept
```

## Environment Management

/env-activate
Description: Activate virtual environment
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
source .venv/bin/activate
```

/env-check
Description: Check Python environment
```bash
which python
python --version
pip list | grep -E "(litellm|fastapi|typer|fastmcp)"
```

/env-vars
Description: Show relevant environment variables
```bash
env | grep -E "(OPENAI|ANTHROPIC|CLAUDE|LLM|LITELLM|GROQ|VERTEX)" | sort
```

/env-set-pythonpath
Description: Set PYTHONPATH for imports
```bash
export PYTHONPATH=/home/graham/workspace/experiments/claude_max_proxy:$PYTHONPATH
echo "PYTHONPATH set to: $PYTHONPATH"
```

## Git Operations

/git-status
Description: Check git status
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
git status
```

/git-diff
Description: Show uncommitted changes
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
git diff
```

/git-log
Description: Show recent commits
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
git log --oneline -10
```

/git-branch
Description: Show current branch
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
git branch --show-current
```

## Process Management

/ps-llm
Description: Show LLM-related processes
```bash
ps aux | grep -E "(claude|llm|uvicorn|fastapi)" | grep -v grep
```

/kill-claude-proxy
Description: Kill Claude proxy process
```bash
pkill -f "poc_claude_proxy" || echo "No Claude proxy process found"
```

/kill-api-server
Description: Kill API server process
```bash
pkill -f "uvicorn.*llm_call" || echo "No API server process found"
```

/port-check
Description: Check which ports are in use
```bash
netstat -tlnp 2>/dev/null | grep -E "(3010|8000|5000|6379)" || \
  lsof -iTCP -sTCP:LISTEN | grep -E "(3010|8000|5000|6379)"
```

## Log Management

/logs-claude
Description: View Claude proxy logs
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
tail -f claude_proxy_polling.log
```

/logs-api
Description: View API server logs
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
tail -f api_server.log
```

/logs-clean
Description: Clean up log files
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
rm -f *.log
echo "Log files cleaned"
```

/logs-sqlite
Description: Check SQLite polling database
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
sqlite3 logs/llm_polling_tasks.db "SELECT task_id, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 10;"
```

## File Operations

/find-py
Description: Find Python files
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
find . -name "*.py" -type f | grep -v __pycache__ | sort
```

/grep-todo
Description: Find TODO comments
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
grep -r "TODO" --include="*.py" src/
```

/tree-src
Description: Show source tree structure
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
tree src/ -I "__pycache__"
```

/size-check
Description: Check project size
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
du -sh .
du -sh src/ tests/ docs/
```

## Quick Commands

/clear
Description: Clear terminal
```bash
clear
```

/reload
Description: Reload shell configuration
```bash
source ~/.bashrc
```

/watch-health
Description: Monitor service health
```bash
watch -n 2 'curl -s http://127.0.0.1:3010/health | jq .'
```

/http-test-claude
Description: Test Claude proxy endpoint
```bash
curl -X POST http://127.0.0.1:3010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "max/claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "Say hello"}],
    "max_tokens": 50
  }' | jq .
```

## Docker Commands

/docker-ps
Description: Show running containers
```bash
docker ps
```

/docker-logs [container]
Description: Show container logs
Arguments:
  - container: Container name or ID
```bash
docker logs -f [container]
```

/docker-clean
Description: Clean up Docker resources
```bash
docker system prune -f
```

## Python Utilities

/py-version
Description: Show Python version
```bash
python --version
```

/py-packages
Description: List installed packages
```bash
pip list | sort
```

/py-install
Description: Install project dependencies
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
uv pip install -e .
```

/py-shell
Description: Start Python REPL with project imports
```bash
cd /home/graham/workspace/experiments/claude_max_proxy
python -c "
import sys
sys.path.insert(0, '.')
from llm_call.core.caller import call_llm
from llm_call.core.router import LLMRouter
from llm_call.core.strategies import VALIDATION_STRATEGIES
print('Imports loaded. Available:')
print('  - call_llm')
print('  - LLMRouter')
print('  - VALIDATION_STRATEGIES')
" -i
```

## Common Workflows

### 1. Start Development
```bash
# Navigate to project
/cd-project

# Activate environment
/env-activate

# Set PYTHONPATH
/env-set-pythonpath

# Check environment
/env-check
```

### 2. Monitor Services
```bash
# Check what's running
/ps-llm

# Check ports
/port-check

# Watch health
/watch-health
```

### 3. Debug Issues
```bash
# Check logs
/logs-claude

# Check processes
/ps-llm

# Test endpoint
/http-test-claude
```