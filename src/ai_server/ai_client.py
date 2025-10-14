"""AI client for making API calls to various providers."""
import json
import re
from typing import List
import requests

from .config import Config
from .models import Message


class AIClient:
    """Unified client for interacting with various AI APIs (Mistral, OpenAI, Ollama)."""
    
    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.endpoint = Config.get_api_endpoint()
        self.api_key = Config.get_api_key()
        self.timeout = Config.REQUEST_TIMEOUT
        self.is_openai_compatible = Config.is_openai_compatible()
    
    def is_available(self) -> bool:
        """Check if AI provider is configured and available."""
        return Config.is_configured()
    
    def chat_completion(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int = 256,
        temperature: float = 0.0
    ) -> str:
        """
        Generate a chat completion using the configured AI provider.
        
        Args:
            messages: List of chat messages
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If provider is not configured or request fails
        """
        if not self.is_available():
            raise RuntimeError(f"AI provider '{self.provider}' is not properly configured")
        
        if self.is_openai_compatible:
            return self._call_openai_compatible(messages, model, max_tokens, temperature)
        else:
            # Ollama uses a different format
            return self._call_ollama(messages, model, max_tokens, temperature)
    
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 256,
        temperature: float = 0.0
    ) -> str:
        """
        Generate a completion using a simple prompt (for backward compatibility).
        
        Args:
            prompt: The input prompt
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        # Convert prompt to messages format
        messages = [Message(role="user", content=prompt)]
        return self.chat_completion(messages, model, max_tokens, temperature)
    
    def _call_openai_compatible(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call OpenAI-compatible API (Mistral, OpenAI, etc.)."""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        print(f"[DEBUG] Calling {self.provider} with model: {model}")
        print(f"[DEBUG] Endpoint: {self.endpoint}")
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = error_json["error"].get("message", error_detail)
                except:
                    pass
                raise RuntimeError(
                    f"{self.provider} returned {response.status_code}: {error_detail}"
                )
            
            data = response.json()
            print(f"[DEBUG] Response keys: {list(data.keys())}")
            
            # Extract content from OpenAI-compatible response
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
                elif "text" in choice:
                    return choice["text"]
            
            raise RuntimeError(f"Unexpected response format from {self.provider}")
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to call {self.provider}: {str(e)}")
    
    def _call_ollama(
        self,
        messages: List[Message],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call Ollama API with its specific format."""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Convert messages to Ollama prompt format
        prompt = self.messages_to_prompt(messages)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        print(f"[DEBUG] Calling Ollama with model: {model}")
        
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise RuntimeError(
                    f"Ollama returned {response.status_code}: {response.text}"
                )
            
            return self._parse_ollama_response(response)
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to call Ollama: {str(e)}")
    
    def _parse_ollama_response(self, response: requests.Response) -> str:
        """Parse Ollama response, handling various response formats."""
        try:
            data = response.json()
            print(f"[DEBUG] Ollama response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
            if isinstance(data, dict):
                # Try different response field names
                for key in ["response", "text", "result"]:
                    if key in data:
                        return data[key]
                
                # Handle choices format (if Ollama returns OpenAI-compatible response)
                if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                    choice = data["choices"][0]
                    if isinstance(choice, dict):
                        if "message" in choice and "content" in choice["message"]:
                            return choice["message"]["content"]
                        for key in ["content", "text"]:
                            if key in choice:
                                return choice[key]
            
            # Handle streaming data concatenated
            if isinstance(data, str) and "response" in data:
                return self._parse_streaming_response(data)
            
            # Last resort: return string representation
            return str(data)
            
        except (ValueError, json.JSONDecodeError) as e:
            print(f"[DEBUG] JSON parse error: {e}")
            return self._extract_response_from_text(response.text)
    
    def _parse_streaming_response(self, data: str) -> str:
        """Parse concatenated streaming response data."""
        lines = data.strip().split('\n')
        responses = []
        
        for line in lines:
            if line.strip():
                try:
                    chunk = json.loads(line)
                    if "response" in chunk:
                        responses.append(chunk["response"])
                except json.JSONDecodeError:
                    continue
        
        if responses:
            return ''.join(responses)
        return data
    
    def _extract_response_from_text(self, text: str) -> str:
        """Extract response from raw text using regex."""
        if '"response":' in text:
            match = re.search(r'"response":\s*"([^"]*)"', text)
            if match:
                return match.group(1)
        return text
    
    @staticmethod
    def messages_to_prompt(messages: List[Message]) -> str:
        """
        Convert list of messages to a formatted prompt (for non-OpenAI APIs).
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted prompt string
        """
        lines = []
        for message in messages:
            lines.append(f"[{message.role.upper()}] {message.content}")
        return "\n\n".join(lines)

