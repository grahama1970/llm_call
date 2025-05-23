"""
API models for Claude CLI proxy.

This module defines Pydantic models for the OpenAI-compatible API.

Links:
- OpenAI API Reference: https://platform.openai.com/docs/api-reference
- Pydantic documentation: https://docs.pydantic.dev/

Sample usage:
    request = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )

Expected output:
    Validated request/response models
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
import time


class Message(BaseModel):
    """Chat message model."""
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: str
    messages: List[Message]
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1)
    stream: Optional[bool] = Field(default=False)
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    # MCP configuration for Claude CLI proxy
    mcp_config: Optional[Dict[str, Any]] = Field(default=None, description="MCP tool configuration for Claude CLI")


class Usage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    """Response choice."""
    index: int
    message: Message
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response."""
    id: str = Field(default_factory=lambda: f"chatcmpl-{int(time.time())}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Choice]
    usage: Optional[Usage] = None
    system_fingerprint: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Streaming response chunk."""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict[str, Any]]


if __name__ == "__main__":
    # Validation testing
    print("Testing API models...")
    
    # Test message
    msg = Message(role="user", content="Hello, Claude!")
    print(f"✅ Message created: {msg}")
    
    # Test request
    request = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[msg]
    )
    print(f"✅ Request created with model: {request.model}")
    
    # Test response
    response = ChatCompletionResponse(
        model="gpt-3.5-turbo",
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content="Hello! How can I help you?"),
                finish_reason="stop"
            )
        ],
        usage=Usage(prompt_tokens=10, completion_tokens=8, total_tokens=18)
    )
    print(f"✅ Response created with {len(response.choices)} choices")
    
    print("\n✅ All API models validated successfully!")