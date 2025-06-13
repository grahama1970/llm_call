"""
MCP Tool definitions for conversational multi-model collaboration.
Module: mcp_conversational_tools.py
Description: Functions for mcp conversational tools operations

These tools enable Claude Desktop/Code to maintain conversation state
while delegating between different models.
"""

from typing import Dict, Any, List, Optional
import json
from pathlib import Path

# MCP Tool specifications for Claude Desktop integration
CONVERSATIONAL_TOOLS = [
    {
        "name": "start_collaboration",
        "description": "Start a new multi-model collaboration conversation",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name/description of the collaboration"
                },
                "initial_prompt": {
                    "type": "string",
                    "description": "Initial task or question"
                },
                "models": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of models that may participate (e.g., ['max/opus', 'vertex_ai/gemini-1.5-pro'])"
                }
            },
            "required": ["name", "initial_prompt"]
        }
    },
    {
        "name": "delegate_to_model",
        "description": "Delegate current task to another model with conversation context",
        "input_schema": {
            "type": "object", 
            "properties": {
                "conversation_id": {
                    "type": "string",
                    "description": "Existing conversation ID"
                },
                "model": {
                    "type": "string",
                    "description": "Target model (e.g., 'vertex_ai/gemini-1.5-pro' for 1M context)"
                },
                "prompt": {
                    "type": "string",
                    "description": "Delegation prompt/instructions for the target model"
                },
                "reason": {
                    "type": "string",
                    "description": "Why delegating (e.g., 'Document exceeds my 200k context limit')"
                }
            },
            "required": ["model", "prompt"]
        }
    },
    {
        "name": "continue_conversation",
        "description": "Continue an existing multi-model conversation",
        "input_schema": {
            "type": "object",
            "properties": {
                "conversation_id": {
                    "type": "string",
                    "description": "Conversation ID to continue"
                },
                "model": {
                    "type": "string",
                    "description": "Model to use for this response"
                },
                "prompt": {
                    "type": "string", 
                    "description": "Next message in the conversation"
                }
            },
            "required": ["conversation_id", "prompt"]
        }
    },
    {
        "name": "get_conversation_summary",
        "description": "Get a summary of the current conversation state",
        "input_schema": {
            "type": "object",
            "properties": {
                "conversation_id": {
                    "type": "string",
                    "description": "Conversation ID"
                },
                "include_full_history": {
                    "type": "boolean",
                    "description": "Include full message history (default: false)"
                }
            },
            "required": ["conversation_id"]
        }
    },
    {
        "name": "analyze_with_context",
        "description": "Analyze content with specific model while maintaining conversation context",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content to analyze (can be very large)"
                },
                "model": {
                    "type": "string",
                    "description": "Model to use (e.g., 'vertex_ai/gemini-1.5-pro' for large docs)"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["summary", "key_points", "sentiment", "technical", "custom"],
                    "description": "Type of analysis needed"
                },
                "custom_instructions": {
                    "type": "string",
                    "description": "Custom analysis instructions if analysis_type is 'custom'"
                },
                "conversation_id": {
                    "type": "string",
                    "description": "Optional: Link to existing conversation"
                }
            },
            "required": ["content", "model", "analysis_type"]
        }
    }
]

def get_mcp_config_for_conversational_tools() -> Dict[str, Any]:
    """
    Generate MCP configuration for Claude Desktop with conversational tools.
    
    Returns:
        MCP configuration dict
    """
    return {
        "mcpServers": {
            "llm-collaboration": {
                "command": "python",
                "args": [
                    "-m",
                    "llm_call.tools.conversational_delegator"
                ],
                "env": {}
            }
        },
        "tools": CONVERSATIONAL_TOOLS
    }

def create_tool_handler_script():
    """
    Create a script that handles MCP tool calls for conversational delegation.
    """
    script_content = '''#!/usr/bin/env python3
"""
MCP Tool handler for conversational multi-model collaboration.
This script is called by Claude Desktop when using collaboration tools.
"""

import sys
import json
import asyncio
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from llm_call.tools.conversational_delegator import conversational_delegate
from llm_call.core.conversation_manager import ConversationManager

async def handle_tool_call(tool_name: str, params: dict):
    """Handle MCP tool calls."""
    
    if tool_name == "start_collaboration":
        manager = ConversationManager()
        conv_id = await manager.create_conversation(
            name=params["name"],
            metadata={
                "models": params.get("models", []),
                "initial_prompt": params["initial_prompt"]
            }
        )
        
        # Add initial prompt
        await manager.add_message(
            conv_id,
            role="user",
            content=params["initial_prompt"],
            model="user"
        )
        
        return {
            "conversation_id": conv_id,
            "status": "Collaboration started",
            "name": params["name"]
        }
    
    elif tool_name == "delegate_to_model":
        result = await conversational_delegate(
            model=params["model"],
            prompt=params["prompt"],
            conversation_id=params.get("conversation_id"),
            include_context_summary=True
        )
        
        if params.get("reason"):
            # Log delegation reason
            manager = ConversationManager()
            await manager.add_message(
                result["conversation_id"],
                role="system",
                content=f"Delegation reason: {params['reason']}",
                model="system"
            )
        
        return result
    
    elif tool_name == "continue_conversation":
        result = await conversational_delegate(
            model=params.get("model", "max/opus"),
            prompt=params["prompt"],
            conversation_id=params["conversation_id"]
        )
        return result
    
    elif tool_name == "get_conversation_summary":
        manager = ConversationManager()
        messages = await manager.get_conversation(params["conversation_id"])
        
        summary = {
            "conversation_id": params["conversation_id"],
            "message_count": len(messages),
            "models_involved": list(set(m.get("model", "unknown") for m in messages)),
            "last_message": messages[-1] if messages else None
        }
        
        if params.get("include_full_history"):
            summary["messages"] = messages
        else:
            summary["recent_messages"] = messages[-5:]  # Last 5 messages
        
        return summary
    
    elif tool_name == "analyze_with_context":
        # Create or continue conversation
        conv_id = params.get("conversation_id")
        if not conv_id:
            manager = ConversationManager()
            conv_id = await manager.create_conversation(
                f"Analysis: {params['analysis_type']}",
                metadata={"analysis_type": params["analysis_type"]}
            )
        
        # Build analysis prompt
        analysis_prompts = {
            "summary": "Please provide a concise summary of the following content:",
            "key_points": "Extract and list the key points from the following content:",
            "sentiment": "Analyze the sentiment and tone of the following content:",
            "technical": "Provide a technical analysis of the following content:",
            "custom": params.get("custom_instructions", "Analyze the following content:")
        }
        
        full_prompt = f"{analysis_prompts[params['analysis_type']]}\\n\\n{params['content']}"
        
        result = await conversational_delegate(
            model=params["model"],
            prompt=full_prompt,
            conversation_id=conv_id
        )
        
        return result
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}

if __name__ == "__main__":
    # Read tool call from stdin (MCP protocol)
    tool_call = json.loads(sys.stdin.read())
    
    # Handle the tool call
    result = asyncio.run(handle_tool_call(
        tool_call["tool"],
        tool_call["parameters"]
    ))
    
    # Return result
    print(json.dumps(result))
'''
    
    return script_content


# Example usage for Claude Desktop
EXAMPLE_CLAUDE_CONFIG = """
# Add this to Claude Desktop's configuration to enable conversational tools:

{
  "mcpServers": {
    "llm-collaboration": {
      "command": "python",
      "args": [
        "/home/graham/workspace/experiments/llm_call/src/llm_call/tools/mcp_tool_handler.py"
      ]
    }
  }
}

# Then in Claude Desktop, you can use commands like:
# - "Start a collaboration to analyze this 500k character document"
# - "Delegate this to Gemini 1.5 Pro because it exceeds my context limit"
# - "Continue the conversation and summarize the findings"
"""