"""
AI Server Package

OpenAI-compatible adapter for multiple AI providers (Mistral, OpenAI, Ollama)
with Swift array formatting capabilities.
"""

__version__ = "0.6.0"
__author__ = "AI Server Contributors"

from .config import Config
from .models import Message, ChatCompletionRequest, SwiftArrayCommand
from .ai_client import AIClient
from .response_builder import ResponseBuilder
from .swift_formatter import SwiftArrayFormatter, LocalFallbackFormatter

__all__ = [
    "Config",
    "Message",
    "ChatCompletionRequest",
    "SwiftArrayCommand",
    "AIClient",
    "ResponseBuilder",
    "SwiftArrayFormatter",
    "LocalFallbackFormatter",
]

