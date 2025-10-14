"""Response builder for OpenAI-compatible responses."""
import time
import uuid
from typing import Dict, Any


class ResponseBuilder:
    """Builder for OpenAI-compatible chat completion responses."""
    
    @staticmethod
    def build_chat_completion(
        content: str,
        model: str
    ) -> Dict[str, Any]:
        """
        Build an OpenAI-compatible chat completion response.
        
        Args:
            content: Response content text
            model: Model name used
            
        Returns:
            OpenAI-compatible response dictionary
        """
        now_ts = int(time.time())
        token_count = len(content.split())
        
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex}",
            "object": "chat.completion",
            "created": now_ts,
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": token_count,
                "total_tokens": token_count
            }
        }

