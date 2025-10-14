"""Pydantic models for API requests and responses."""
from pydantic import BaseModel
from typing import List, Optional, Literal


class Message(BaseModel):
    """Chat message model."""
    role: Literal["system", "user", "assistant"]
    content: str


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request."""
    model: Optional[str] = None
    messages: List[Message]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = False


class SwiftArrayCommand(BaseModel):
    """Convenience endpoint payload for Swift array operations."""
    code: str
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

