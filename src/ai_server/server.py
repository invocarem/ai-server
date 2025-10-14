"""
AI Server: OpenAI-compatible adapter for multiple AI providers (Mistral, OpenAI, Ollama)

Refactored version with modular architecture supporting multiple AI providers.
"""
from fastapi import FastAPI, HTTPException

from .config import Config
from .models import ChatCompletionRequest, SwiftArrayCommand, Message
from .ai_client import AIClient
from .swift_formatter import SwiftArrayFormatter, LocalFallbackFormatter
from .response_builder import ResponseBuilder


# Initialize FastAPI app
app = FastAPI(title=Config.APP_TITLE, version=Config.APP_VERSION)

# Initialize AI client
ai_client = AIClient()


# -------------------- Routes --------------------

@app.post("/v1/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    
    Forwards requests to configured AI provider (Mistral, OpenAI, Ollama),
    otherwise uses local fallback.
    """
    model = body.model or Config.DEFAULT_MODEL
    messages = body.messages
    max_tokens = body.max_tokens or Config.DEFAULT_MAX_TOKENS
    temperature = body.temperature or Config.DEFAULT_TEMPERATURE

    # Try AI provider if available, otherwise use local fallback
    if ai_client.is_available():
        try:
            reply_text = ai_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        reply_text = LocalFallbackFormatter.simple_reply(messages)

    return ResponseBuilder.build_chat_completion(reply_text, model)


@app.post("/renumber-verses-stream")
async def renumber_verses_stream(cmd: SwiftArrayCommand):
    """
    Renumber Swift array verses sequentially.
    
    Convenience endpoint for VS Code Continue commands. Uses AI if available,
    otherwise falls back to local deterministic formatter.
    """
    user_code = cmd.code
    model = cmd.model or Config.DEFAULT_SWIFT_MODEL
    max_tokens = cmd.max_tokens or Config.DEFAULT_SWIFT_MAX_TOKENS
    temperature = cmd.temperature or Config.DEFAULT_TEMPERATURE

    # Construct messages for AI
    messages = [
        Message(role="system", content=SwiftArrayFormatter.RENUMBER_SYSTEM_PROMPT),
        Message(role="user", content=f"```swift\n{user_code}\n```"),
    ]

    if ai_client.is_available():
        # Use AI-based formatting
        print(f"[DEBUG] Sending to {Config.AI_PROVIDER} with model: {model}")

        try:
            ai_reply = ai_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            print(f"[DEBUG] Raw AI reply (first 500 chars): {ai_reply[:500]}")
            
            reply_text = SwiftArrayFormatter.extract_code_from_response(ai_reply)
            print(f"[DEBUG] Cleaned response (first 500 chars): {reply_text[:500]}")
            
        except Exception as e:
            print(f"[DEBUG] Error calling AI provider: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Use local deterministic formatter
        print("[DEBUG] Using local deterministic formatter")
        code_snippet = SwiftArrayFormatter.extract_swift_code(user_code)
        if not code_snippet:
            raise HTTPException(
                status_code=400,
                detail="Could not extract Swift code from input"
            )
        
        formatted = SwiftArrayFormatter.format_local(code_snippet)
        if not formatted:
            raise HTTPException(status_code=500, detail="Formatting failed")
        
        reply_text = formatted

    return ResponseBuilder.build_chat_completion(reply_text, model)


@app.post("/clean-verses-stream")
async def clean_verses_stream(cmd: SwiftArrayCommand):
    """
    Remove all /* number */ comments from Swift array.
    
    Preserves array structure and string content while removing numbering comments.
    """
    user_code = cmd.code
    model = cmd.model or Config.DEFAULT_SWIFT_MODEL
    max_tokens = cmd.max_tokens or Config.DEFAULT_SWIFT_MAX_TOKENS
    temperature = cmd.temperature or Config.DEFAULT_TEMPERATURE

    if ai_client.is_available():
        # Use AI-based cleaning
        messages = [
            Message(role="system", content=SwiftArrayFormatter.CLEAN_SYSTEM_PROMPT),
            Message(role="user", content=f"```swift\n{user_code}\n```"),
        ]

        print(f"[DEBUG] Cleaning verses with {Config.AI_PROVIDER} model: {model}")

        try:
            ai_reply = ai_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            print(f"[DEBUG] Raw AI reply for cleaning (first 500 chars): {ai_reply[:500]}")
            
            reply_text = SwiftArrayFormatter.extract_code_from_response(ai_reply)
            print(f"[DEBUG] Cleaned response (first 500 chars): {reply_text[:500]}")
            
        except Exception as e:
            print(f"[DEBUG] Error calling AI provider for cleaning: {e}")
            # Fall back to local implementation
            cleaned = SwiftArrayFormatter.clean_comments_local(user_code)
            if not cleaned:
                raise HTTPException(status_code=500, detail="Comment cleaning failed")
            reply_text = cleaned
    else:
        # Use local implementation
        print("[DEBUG] Using local comment cleaner")
        cleaned = SwiftArrayFormatter.clean_comments_local(user_code)
        if not cleaned:
            raise HTTPException(status_code=500, detail="Comment cleaning failed")
        reply_text = cleaned

    return ResponseBuilder.build_chat_completion(reply_text, model)


@app.post("/renumber-verses")
async def renumber_verses(cmd: SwiftArrayCommand):
    """
    Alternative endpoint that returns just the formatted code without OpenAI wrapper.
    """
    try:
        response = await renumber_verses_stream(cmd)
        return {"formatted_code": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/clean-verses")
async def clean_verses(cmd: SwiftArrayCommand):
    """
    Alternative endpoint that returns just the cleaned code without OpenAI wrapper.
    """
    try:
        response = await clean_verses_stream(cmd)
        return {"cleaned_code": response["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/models")
async def list_models():
    """List available models."""
    # Return default Mistral models (since it's the default endpoint)
    # Users can use any model supported by their API endpoint
    models = [
        {"id": "mistral-small-latest", "object": "model"},
        {"id": "mistral-medium-latest", "object": "model"},
        {"id": "mistral-large-latest", "object": "model"},
        {"id": "gpt-4o", "object": "model"},
        {"id": "gpt-4o-mini", "object": "model"},
    ]
    
    # Add Ollama models if using Ollama
    if Config.AI_PROVIDER == "ollama":
        models.extend([
            {"id": "mistral:latest", "object": "model"},
            {"id": "deepseek-coder:6.7b", "object": "model"},
        ])
    
    return {"data": models}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "ok": True,
        "provider": Config.AI_PROVIDER,
        "configured": ai_client.is_available(),
        "model": Config.DEFAULT_MODEL
    }


# -------------------- Main --------------------

def main():
    """Run the server."""
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)


if __name__ == "__main__":
    main()

