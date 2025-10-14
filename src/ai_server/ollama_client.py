"""Ollama client for making API calls (legacy, use AIClient instead)."""
import json
import re
from typing import List
import requests

from .config import Config
from .models import Message


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self):
        self.base_url = Config.OLLAMA_URL
        self.api_key = Config.OLLAMA_API_KEY
        self.timeout = Config.OLLAMA_TIMEOUT
    
    def is_available(self) -> bool:
        """Check if Ollama is configured and available."""
        return bool(self.base_url)
    
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 256,
        temperature: float = 0.0
    ) -> str:
        """
        Generate a completion using Ollama.
        
        Args:
            prompt: The input prompt
            model: Model to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If Ollama is not configured or request fails
        """
        if not self.base_url:
            raise RuntimeError("OLLAMA_URL is not configured")
        
        url = self.base_url.rstrip("/") + "/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        print(f"[DEBUG] Calling Ollama with model: {model}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                raise RuntimeError(
                    f"Ollama returned {response.status_code}: {response.text}"
                )
            
            return self._parse_response(response)
            
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to call Ollama: {str(e)}")
    
    def _parse_response(self, response: requests.Response) -> str:
        """
        Parse Ollama response, handling various response formats.
        
        Args:
            response: HTTP response from Ollama
            
        Returns:
            Extracted text content
        """
        try:
            data = response.json()
            print(f"[DEBUG] Raw Ollama response keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
            
            if isinstance(data, dict):
                # Try different response field names
                for key in ["response", "text", "result"]:
                    if key in data:
                        return data[key]
                
                # Handle choices format
                if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                    choice = data["choices"][0]
                    if isinstance(choice, dict):
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
        Convert list of messages to a formatted prompt.
        
        Args:
            messages: List of chat messages
            
        Returns:
            Formatted prompt string
        """
        lines = []
        for message in messages:
            lines.append(f"[{message.role.upper()}] {message.content}")
        return "\n\n".join(lines)

