"""
Conversation state persistence for fluid multi-model collaboration.
Module: conversation_manager.py
Description: Implementation of conversation manager functionality

This module manages conversation state to enable fluid, iterative conversations
between different LLM models (Claude, Gemini, GPT, etc.) using SQLite or ArangoDB.

Links:
- SQLite: https://docs.python.org/3/library/sqlite3.html
- ArangoDB: https://www.arangodb.com/docs/stable/

Sample usage:
    manager = ConversationManager()
    conv_id = await manager.create_conversation("claude-gemini-collab")
    await manager.add_message(conv_id, "user", "Analyze this 500k document...")
    await manager.add_message(conv_id, "claude", "I'll delegate to Gemini for large context")
    messages = await manager.get_conversation(conv_id)
"""

import sqlite3
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from loguru import logger
import asyncio
from contextlib import asynccontextmanager

# Try to import ArangoDB client
try:
    from arango import ArangoClient
    HAS_ARANGO = True
except ImportError:
    HAS_ARANGO = False
    logger.warning("ArangoDB client not installed. Using SQLite only.")

from llm_call.core.config.loader import load_configuration

# Load settings
settings = load_configuration()


class ConversationManager:
    """Manages conversation state for multi-model collaboration."""
    
    def __init__(
        self,
        storage_backend: str = "sqlite",
        db_path: Optional[Path] = None,
        arango_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize conversation manager.
        
        Args:
            storage_backend: "sqlite" or "arango"
            db_path: Path to SQLite database (default: logs/conversations.db)
            arango_config: ArangoDB connection config
        """
        self.storage_backend = storage_backend
        
        if storage_backend == "sqlite":
            self.db_path = db_path or Path("logs/conversations.db")
            self._init_sqlite()
        elif storage_backend == "arango" and HAS_ARANGO:
            self._init_arango(arango_config)
        else:
            raise ValueError(f"Unsupported storage backend: {storage_backend}")
    
    def _init_sqlite(self):
        """Initialize SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    created_at REAL,
                    updated_at REAL,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    role TEXT,
                    content TEXT,
                    model TEXT,
                    timestamp REAL,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
                )
            ''')
            
            # Index for faster conversation queries
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_messages_conversation 
                ON messages(conversation_id, timestamp)
            ''')
            
            conn.commit()
        
        logger.info(f"SQLite conversation database initialized at {self.db_path}")
    
    def _init_arango(self, config: Optional[Dict[str, Any]]):
        """Initialize ArangoDB connection."""
        if not config:
            # Use defaults from environment
            config = {
                "host": "localhost",
                "port": 8529,
                "username": "root",
                "password": "openSesame",
                "database": "llm_conversations"
            }
        
        self.arango_client = ArangoClient(hosts=f"http://{config['host']}:{config['port']}")
        self.arango_db = self.arango_client.db(
            config["database"],
            username=config["username"],
            password=config["password"]
        )
        
        # Create collections if they don't exist
        if not self.arango_db.has_collection("conversations"):
            self.arango_db.create_collection("conversations")
        if not self.arango_db.has_collection("messages"):
            self.arango_db.create_collection("messages")
        if not self.arango_db.has_graph("conversation_graph"):
            self.arango_db.create_graph(
                "conversation_graph",
                edge_definitions=[{
                    "edge_collection": "message_flow",
                    "from_vertex_collections": ["messages"],
                    "to_vertex_collections": ["messages"]
                }]
            )
        
        logger.info("ArangoDB conversation storage initialized")
    
    async def create_conversation(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new conversation.
        
        Args:
            name: Conversation name/description
            metadata: Optional metadata (e.g., initial models, purpose)
            
        Returns:
            Conversation ID
        """
        conv_id = str(uuid.uuid4())
        timestamp = time.time()
        
        if self.storage_backend == "sqlite":
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    '''INSERT INTO conversations (id, name, created_at, updated_at, metadata)
                       VALUES (?, ?, ?, ?, ?)''',
                    (conv_id, name, timestamp, timestamp, json.dumps(metadata or {}))
                )
                conn.commit()
        
        elif self.storage_backend == "arango":
            self.arango_db.collection("conversations").insert({
                "_key": conv_id,
                "name": name,
                "created_at": timestamp,
                "updated_at": timestamp,
                "metadata": metadata or {}
            })
        
        logger.info(f"Created conversation '{name}' with ID: {conv_id}")
        return conv_id
    
    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user, assistant, system, etc.)
            content: Message content
            model: Model that generated the message
            metadata: Optional metadata (e.g., tokens, latency)
            
        Returns:
            Message ID
        """
        msg_id = str(uuid.uuid4())
        timestamp = time.time()
        
        if self.storage_backend == "sqlite":
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.execute(
                    '''INSERT INTO messages 
                       (id, conversation_id, role, content, model, timestamp, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (msg_id, conversation_id, role, content, model, timestamp, 
                     json.dumps(metadata or {}))
                )
                
                # Update conversation timestamp
                conn.execute(
                    "UPDATE conversations SET updated_at = ? WHERE id = ?",
                    (timestamp, conversation_id)
                )
                conn.commit()
        
        elif self.storage_backend == "arango":
            self.arango_db.collection("messages").insert({
                "_key": msg_id,
                "conversation_id": conversation_id,
                "role": role,
                "content": content,
                "model": model,
                "timestamp": timestamp,
                "metadata": metadata or {}
            })
            
            # Update conversation
            self.arango_db.collection("conversations").update({
                "_key": conversation_id,
                "updated_at": timestamp
            })
        
        logger.debug(f"Added {role} message to conversation {conversation_id}")
        return msg_id
    
    async def get_conversation(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            limit: Optional limit on number of messages
            
        Returns:
            List of messages in chronological order
        """
        if self.storage_backend == "sqlite":
            with sqlite3.connect(str(self.db_path)) as conn:
                query = '''
                    SELECT role, content, model, timestamp, metadata
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp
                '''
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor = conn.execute(query, (conversation_id,))
                messages = []
                for row in cursor:
                    msg = {
                        "role": row[0],
                        "content": row[1],
                        "model": row[2],
                        "timestamp": row[3],
                        "metadata": json.loads(row[4])
                    }
                    messages.append(msg)
                
                return messages
        
        elif self.storage_backend == "arango":
            query = '''
                FOR msg IN messages
                FILTER msg.conversation_id == @conv_id
                SORT msg.timestamp
                RETURN msg
            '''
            if limit:
                query = query.replace("RETURN msg", f"LIMIT {limit} RETURN msg")
            
            cursor = self.arango_db.aql.execute(
                query,
                bind_vars={"conv_id": conversation_id}
            )
            return list(cursor)
    
    async def get_conversation_for_llm(
        self,
        conversation_id: str,
        format: str = "openai"
    ) -> List[Dict[str, str]]:
        """
        Get conversation formatted for LLM API calls.
        
        Args:
            conversation_id: Conversation ID
            format: Output format ("openai" style)
            
        Returns:
            List of message dicts with role/content
        """
        messages = await self.get_conversation(conversation_id)
        
        if format == "openai":
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
        else:
            return messages
    
    async def find_conversations(
        self,
        name_pattern: Optional[str] = None,
        model: Optional[str] = None,
        days_ago: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find conversations by criteria.
        
        Args:
            name_pattern: Name pattern to search
            model: Model involved in conversation
            days_ago: Conversations from last N days
            
        Returns:
            List of conversation summaries
        """
        if self.storage_backend == "sqlite":
            with sqlite3.connect(str(self.db_path)) as conn:
                query = "SELECT id, name, created_at, updated_at FROM conversations WHERE 1=1"
                params = []
                
                if name_pattern:
                    query += " AND name LIKE ?"
                    params.append(f"%{name_pattern}%")
                
                if days_ago:
                    cutoff = time.time() - (days_ago * 86400)
                    query += " AND created_at >= ?"
                    params.append(cutoff)
                
                if model:
                    # Need to join with messages
                    query = '''
                        SELECT DISTINCT c.id, c.name, c.created_at, c.updated_at
                        FROM conversations c
                        JOIN messages m ON c.id = m.conversation_id
                        WHERE m.model = ?
                    '''
                    params = [model]
                    
                    if name_pattern:
                        query += " AND c.name LIKE ?"
                        params.append(f"%{name_pattern}%")
                
                cursor = conn.execute(query, params)
                return [
                    {
                        "id": row[0],
                        "name": row[1],
                        "created_at": row[2],
                        "updated_at": row[3]
                    }
                    for row in cursor
                ]
        
        elif self.storage_backend == "arango":
            # ArangoDB AQL query
            filters = []
            bind_vars = {}
            
            if name_pattern:
                filters.append("REGEX_TEST(conv.name, @pattern, true)")
                bind_vars["pattern"] = name_pattern
            
            if days_ago:
                cutoff = time.time() - (days_ago * 86400)
                filters.append("conv.created_at >= @cutoff")
                bind_vars["cutoff"] = cutoff
            
            where_clause = " AND ".join(filters) if filters else "true"
            
            query = f'''
                FOR conv IN conversations
                FILTER {where_clause}
                RETURN conv
            '''
            
            cursor = self.arango_db.aql.execute(query, bind_vars=bind_vars)
            return list(cursor)
    
    @asynccontextmanager
    async def conversation_context(
        self,
        conversation_id: Optional[str] = None,
        name: Optional[str] = None
    ):
        """
        Context manager for handling conversations.
        
        Usage:
            async with manager.conversation_context() as conv:
                conv_id = conv["id"]
                # Use conv_id for operations
        """
        if not conversation_id:
            conversation_id = await self.create_conversation(
                name or f"auto-conversation-{datetime.now().isoformat()}"
            )
        
        try:
            yield {"id": conversation_id}
        finally:
            # Could add cleanup or summary generation here
            pass


# Helper function for integration with existing system
async def get_or_create_conversation_manager(
    use_arango: bool = False
) -> ConversationManager:
    """
    Get or create a conversation manager instance.
    
    Args:
        use_arango: Whether to use ArangoDB (if available)
        
    Returns:
        ConversationManager instance
    """
    if use_arango and HAS_ARANGO:
        # Check if ArangoDB is accessible
        try:
            return ConversationManager(
                storage_backend="arango",
                arango_config={
                    "host": "localhost",
                    "port": 8529,
                    "username": "root",
                    "password": "openSesame",
                    "database": "llm_conversations"
                }
            )
        except Exception as e:
            logger.warning(f"Failed to connect to ArangoDB: {e}. Falling back to SQLite.")
    
    # Default to SQLite
    return ConversationManager(storage_backend="sqlite")


# Test function
if __name__ == "__main__":
    import asyncio
    
    async def test_conversation_flow():
        """Test conversation management."""
        manager = await get_or_create_conversation_manager()
        
        # Create a conversation
        conv_id = await manager.create_conversation(
            "Claude-Gemini Large Doc Analysis",
            metadata={
                "purpose": "Analyze 500k character document",
                "models": ["claude-3-opus", "gemini-1.5-pro"]
            }
        )
        
        # Simulate conversation flow
        await manager.add_message(
            conv_id, "user", 
            "Please analyze this 500k character document about quantum computing...",
            model="user"
        )
        
        await manager.add_message(
            conv_id, "assistant",
            "I notice this document is quite large (500k characters). I'll delegate this to Gemini 1.5 Pro which has a 1M token context window.",
            model="claude-3-opus"
        )
        
        await manager.add_message(
            conv_id, "assistant",
            "Analysis complete. The document covers: 1) Quantum entanglement principles...",
            model="gemini-1.5-pro",
            metadata={"tokens_processed": 125000, "latency": 4.5}
        )
        
        await manager.add_message(
            conv_id, "assistant",
            "Based on Gemini's analysis, here are the key insights with practical applications...",
            model="claude-3-opus"
        )
        
        # Retrieve conversation
        messages = await manager.get_conversation_for_llm(conv_id)
        logger.info(f"Conversation has {len(messages)} messages")
        
        for msg in messages:
            logger.info(f"{msg['role']}: {msg['content'][:100]}...")
        
        logger.success("✅ Conversation management test passed")
    
    asyncio.run(test_conversation_flow())