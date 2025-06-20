"""
Module: conversation.py
Description: Extended conversation management for llm_call

External Dependencies:
- asyncio: https://docs.python.org/3/library/asyncio.html
- uuid: https://docs.python.org/3/library/uuid.html
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from collections import defaultdict


class ConversationManager:
    """Manage multiple conversation sessions"""
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.metadata: Dict[str, Dict[str, Any]] = {}
    
    def create_conversation(self, user_id: str, **metadata) -> str:
        """Create a new conversation and return its ID"""
        conv_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        self.metadata[conv_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            **metadata
        }
        return conv_id
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to a conversation"""
        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a conversation"""
        return self.conversations.get(conversation_id, [])
    
    def list_conversations(self, user_id: Optional[str] = None) -> List[str]:
        """List all conversations, optionally filtered by user"""
        if user_id:
            return [
                conv_id 
                for conv_id, meta in self.metadata.items() 
                if meta.get("user_id") == user_id
            ]
        return list(self.metadata.keys())
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            del self.metadata[conversation_id]
            return True
        return False


class ConversationManagerSync:
    """Synchronous version of ConversationManager"""
    
    def __init__(self):
        self.manager = ConversationManager()
    
    def create_conversation(self, user_id: str, **metadata) -> str:
        """Create a new conversation and return its ID"""
        return self.manager.create_conversation(user_id, **metadata)
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to a conversation"""
        return self.manager.add_message(conversation_id, role, content)
    
    def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages in a conversation"""
        return self.manager.get_messages(conversation_id)
    
    def list_conversations(self, user_id: Optional[str] = None) -> List[str]:
        """List all conversations, optionally filtered by user"""
        return self.manager.list_conversations(user_id)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        return self.manager.delete_conversation(conversation_id)