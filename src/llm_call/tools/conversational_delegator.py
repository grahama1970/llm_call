#!/usr/bin/env python3
"""
Conversational LLM Delegator for fluid multi-model collaboration.

This enhanced delegator maintains conversation state across model calls,
enabling true collaborative conversations between Claude, Gemini, GPT, etc.

Usage:
    # Start a new conversation
    python conversational_delegator.py --model "vertex_ai/gemini-1.5-pro" \
        --prompt "Analyze this document" --conversation-name "doc-analysis"
    
    # Continue existing conversation
    python conversational_delegator.py --model "gpt-4" \
        --prompt "What patterns did you find?" --conversation-id "uuid-here"
"""

import asyncio
import json
import sys
import argparse
from typing import Dict, Any, Optional, List
from pathlib import Path
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import conversation manager and LLM caller
from src.llm_call.core.conversation_manager import ConversationManager
from src.llm_call.core.caller import make_llm_request
from src.llm_call.core.router import resolve_route

# Configure logging for interactive use
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")


async def conversational_delegate(
    model: str,
    prompt: str,
    conversation_id: Optional[str] = None,
    conversation_name: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    json_mode: bool = False,
    use_arango: bool = False,
    include_context_summary: bool = True
) -> Dict[str, Any]:
    """
    Make a conversational LLM call with persistent state.
    
    Args:
        model: Target model
        prompt: User prompt
        conversation_id: Existing conversation to continue
        conversation_name: Name for new conversation
        system_prompt: System prompt (used for new conversations)
        temperature: Generation temperature
        max_tokens: Max tokens to generate
        json_mode: Request JSON output
        use_arango: Use ArangoDB instead of SQLite
        include_context_summary: Include conversation summary for context
        
    Returns:
        Response with conversation details
    """
    # Initialize conversation manager
    manager = ConversationManager(
        storage_backend="arango" if use_arango and os.path.exists("/home/graham/workspace/experiments/arangodb") else "sqlite"
    )
    
    # Get or create conversation
    if conversation_id:
        logger.info(f"Continuing conversation: {conversation_id}")
    else:
        conversation_id = await manager.create_conversation(
            name=conversation_name or f"Delegation to {model}",
            metadata={
                "initial_model": model,
                "system_prompt": system_prompt
            }
        )
        logger.info(f"Created new conversation: {conversation_id}")
        
        # Add system prompt if provided and new conversation
        if system_prompt:
            await manager.add_message(
                conversation_id,
                role="system",
                content=system_prompt,
                model="system"
            )
    
    # Add user message
    await manager.add_message(
        conversation_id,
        role="user",
        content=prompt,
        model="user"
    )
    
    # Get conversation history for context
    messages = await manager.get_conversation_for_llm(conversation_id)
    
    # Optionally add context summary for long conversations
    if include_context_summary and len(messages) > 10:
        # Get recent messages
        recent_messages = messages[-8:]  # Keep last 8 messages
        
        # Add summary message
        summary_msg = {
            "role": "system",
            "content": f"[Conversation has {len(messages)} total messages. Showing recent context.]"
        }
        messages = [messages[0]] + [summary_msg] + recent_messages  # Keep original system prompt
    
    # Log the model routing
    logger.info(f"Routing to model: {model}")
    
    # Build LLM config
    llm_config = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "default_validate": False
    }
    
    if json_mode:
        llm_config["response_format"] = {"type": "json_object"}
    
    try:
        # Make the LLM call
        response = await make_llm_request(llm_config)
        
        # Extract content
        content = None
        if isinstance(response, dict):
            if "error" in response:
                content = f"Error: {response['error']}"
            elif response.get("choices"):
                content = response["choices"][0].get("message", {}).get("content", "")
        elif hasattr(response, "choices") and response.choices:
            content = response.choices[0].message.content
        else:
            content = str(response)
        
        # Add assistant response to conversation
        await manager.add_message(
            conversation_id,
            role="assistant",
            content=content,
            model=model,
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        
        logger.success(f"Response received from {model}")
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "model": model,
            "content": content,
            "message_count": len(messages) + 1
        }
        
    except Exception as e:
        logger.error(f"Error calling {model}: {e}")
        
        # Save error to conversation
        await manager.add_message(
            conversation_id,
            role="system",
            content=f"Error calling {model}: {str(e)}",
            model="system"
        )
        
        return {
            "success": False,
            "conversation_id": conversation_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "model": model
        }


async def show_conversation_history(conversation_id: str, use_arango: bool = False):
    """Display conversation history."""
    manager = ConversationManager(
        storage_backend="arango" if use_arango else "sqlite"
    )
    
    messages = await manager.get_conversation(conversation_id)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Conversation: {conversation_id}")
    logger.info(f"{'='*80}")
    
    for msg in messages:
        role = msg["role"].upper()
        model = msg.get("model", "unknown")
        content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
        
        logger.info(f"\n[{role}] ({model}):")
        logger.info(content)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Total messages: {len(messages)}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Conversational LLM Delegator with state persistence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start new conversation with Claude analyzing a document
  python conversational_delegator.py --model "max/opus" \\
    --prompt "This 500k document needs analysis" \\
    --conversation-name "large-doc-analysis"
  
  # Claude delegates to Gemini (using returned conversation ID)
  python conversational_delegator.py --model "vertex_ai/gemini-1.5-pro" \\
    --prompt "I'll analyze this large document for you" \\
    --conversation-id "uuid-from-previous"
  
  # Gemini responds, then Claude summarizes
  python conversational_delegator.py --model "max/opus" \\
    --prompt "Based on your analysis, here are the key points..." \\
    --conversation-id "uuid-from-previous"
  
  # View conversation history
  python conversational_delegator.py --show-history --conversation-id "uuid"
"""
    )
    
    parser.add_argument("--model", "-m", help="Target model")
    parser.add_argument("--prompt", "-p", help="User prompt")
    parser.add_argument("--conversation-id", "-c", help="Continue existing conversation")
    parser.add_argument("--conversation-name", "-n", help="Name for new conversation")
    parser.add_argument("--system", "-s", help="System prompt for new conversation")
    parser.add_argument("--temperature", "-t", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--json", "-j", action="store_true", help="Request JSON output")
    parser.add_argument("--use-arango", action="store_true", help="Use ArangoDB for storage")
    parser.add_argument("--show-history", action="store_true", help="Show conversation history")
    
    args = parser.parse_args()
    
    if args.show_history:
        if not args.conversation_id:
            parser.error("--conversation-id required for --show-history")
        asyncio.run(show_conversation_history(args.conversation_id, args.use_arango))
        return
    
    if not args.model or not args.prompt:
        parser.error("--model and --prompt are required")
    
    # Run the conversational delegation
    result = asyncio.run(conversational_delegate(
        model=args.model,
        prompt=args.prompt,
        conversation_id=args.conversation_id,
        conversation_name=args.conversation_name,
        system_prompt=args.system,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        json_mode=args.json,
        use_arango=args.use_arango
    ))
    
    # Output result
    print(json.dumps(result, indent=2))
    
    if result.get("success"):
        logger.info(f"\nConversation ID: {result['conversation_id']}")
        logger.info("Use this ID to continue the conversation")


if __name__ == "__main__":
    main()