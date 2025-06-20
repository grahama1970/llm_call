#!/bin/bash
# Script to run F1.4 test with proper environment settings

echo "Running F1.4 - max/opus haiku test"
echo "=================================="
echo ""
echo "Setting up environment for Claude CLI local execution..."

# Ensure ANTHROPIC_API_KEY is not set (required for Max plan)
unset ANTHROPIC_API_KEY

# Set execution mode to local
export CLAUDE_PROXY_EXECUTION_MODE=local

# Find and set Claude CLI path
CLAUDE_PATH=$(which claude)
if [ -z "$CLAUDE_PATH" ]; then
    echo "ERROR: Claude CLI not found in PATH"
    echo "Please install Claude CLI first"
    exit 1
fi

export CLAUDE_CLI_PATH=$CLAUDE_PATH
echo "Found Claude CLI at: $CLAUDE_CLI_PATH"
echo ""

# Run the test
python usage_F1_4_max_opus_haiku.py