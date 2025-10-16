"""Configuration module for AI Server."""
import os
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

# Provider type
ProviderType = Literal["mistral", "openai", "ollama"]


class Config:
    """Application configuration."""
    
    # Server
    APP_TITLE = "AI Server"
    APP_VERSION = "0.6"
    HOST = "0.0.0.0"
    PORT = 5000
    
    # AI Provider Configuration
    # Options: "openai" (for OpenAI, Mistral, etc.), "ollama" (for local Ollama)
    AI_PROVIDER = os.environ.get("AI_PROVIDER", "openai").lower()
    
    # API Configuration
    API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.mistral.ai/v1")  # Default to Mistral
    API_KEY = os.environ.get("API_KEY")  # Your API key
    
    # Legacy Ollama support (for backward compatibility)
    OLLAMA_URL = os.environ.get("OLLAMA_URL")
    OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")
    
    # Defaults
    DEFAULT_MODEL = "mixtral:8x7b"
    DEFAULT_MAX_TOKENS = 256
    DEFAULT_TEMPERATURE = 0.0
    DEFAULT_SWIFT_MODEL = "mistral-small-latest"
    DEFAULT_SWIFT_MAX_TOKENS = 512
    
    # Timeouts
    REQUEST_TIMEOUT = 180
    
    # Provider-specific default endpoints
    PROVIDER_ENDPOINTS = {
        "openai": "https://api.openai.com/v1/chat/completions",
        "mistral": "https://api.mistral.ai/v1/chat/completions",
        "ollama": "/v1/chat/completions",  # OpenAI-compatible endpoint (Ollama v0.1.17+)
    }

    @classmethod
    def get_api_endpoint(cls) -> str:
        """Get the API endpoint based on provider configuration."""
        provider = cls.AI_PROVIDER
        
        # Handle Ollama provider
        if provider == "ollama":
            base_url = cls.OLLAMA_URL or cls.API_BASE_URL or "http://localhost:11434"
            return base_url.rstrip("/") + cls.PROVIDER_ENDPOINTS["ollama"]
        
        # For OpenAI-compatible cloud APIs (OpenAI, Mistral, etc.)
        if cls.API_BASE_URL:
            # If full endpoint is provided, use it
            if "/chat/completions" in cls.API_BASE_URL:
                return cls.API_BASE_URL
            # If base URL doesn't have the endpoint, add it
            return cls.API_BASE_URL.rstrip("/") + "/chat/completions"
        
        # Use default provider endpoints
        return cls.PROVIDER_ENDPOINTS.get(provider, cls.PROVIDER_ENDPOINTS["openai"])
    
    @classmethod
    def get_api_key(cls) -> str:
        """Get the API key from environment."""
        # Prefer new unified API_KEY
        if cls.API_KEY:
            return cls.API_KEY
        # Fall back to legacy OLLAMA_API_KEY
        if cls.OLLAMA_API_KEY:
            return cls.OLLAMA_API_KEY
        return None
    
    @classmethod
    def is_openai_compatible(cls) -> bool:
        """Check if the provider uses OpenAI-compatible API."""
        # All providers use OpenAI-compatible format (Ollama v0.1.17+ supports it)
        return True
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if AI provider is configured."""
        # Ollama doesn't require an API key (local server)
        if cls.AI_PROVIDER == "ollama":
            # Check if OLLAMA_URL or API_BASE_URL is set
            return bool(cls.OLLAMA_URL or cls.API_BASE_URL)
        # OpenAI-compatible cloud providers need an API key
        if cls.get_api_key():
            return True
        return False
    
    @classmethod
    def log_config(cls):
        """Log configuration for debugging."""
        print(f"[DEBUG] AI_PROVIDER: {cls.AI_PROVIDER}")
        print(f"[DEBUG] API_ENDPOINT: {cls.get_api_endpoint()}")
        api_key = cls.get_api_key()
        print(f"[DEBUG] API_KEY: {'*' * min(8, len(api_key)) if api_key else 'Not set'}")
        print(f"[DEBUG] DEFAULT_MODEL: {cls.DEFAULT_MODEL}")
        print(f"[DEBUG] OpenAI-compatible: {cls.is_openai_compatible()}")


# Log configuration on module import
Config.log_config()

