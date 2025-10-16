"""
AI Server: OpenAI-compatible adapter for multiple AI providers (Mistral, OpenAI, Ollama)

Refactored version with modular architecture supporting multiple AI providers.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import json
import time
import uuid

from .config import Config
from .models import ChatCompletionRequest, SwiftArrayCommand, Message
from .ai_client import AIClient
from .swift_formatter import SwiftArrayFormatter, LocalFallbackFormatter
from .response_builder import ResponseBuilder


# Initialize FastAPI app
app = FastAPI(title=Config.APP_TITLE, version=Config.APP_VERSION)

# Initialize AI client
ai_client = AIClient()


# -------------------- Streaming Helpers --------------------

def create_streaming_response(content: str, model: str):
    """
    Create an OpenAI-compatible streaming response generator.
    
    Args:
        content: The content to stream
        model: Model name
        
    Yields:
        Server-Sent Events formatted strings
    """
    chunk_id = f"chatcmpl-{uuid.uuid4().hex}"
    created_ts = int(time.time())
    
    # First chunk with role
    first_chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": created_ts,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {"role": "assistant", "content": ""},
            "finish_reason": None
        }]
    }
    yield f"data: {json.dumps(first_chunk)}\n\n"
    
    # Content chunk
    content_chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": created_ts,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {"content": content},
            "finish_reason": None
        }]
    }
    yield f"data: {json.dumps(content_chunk)}\n\n"
    
    # Final chunk with finish_reason
    final_chunk = {
        "id": chunk_id,
        "object": "chat.completion.chunk",
        "created": created_ts,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"


# -------------------- Routes --------------------

@app.post("/v1/chat/completions")
async def chat_completions(body: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    
    Forwards requests to configured AI provider (Mistral, OpenAI, Ollama),
    otherwise uses local fallback. Supports streaming responses.
    """
    model = body.model or Config.DEFAULT_MODEL
    messages = body.messages
    max_tokens = body.max_tokens or Config.DEFAULT_MAX_TOKENS
    temperature = body.temperature or Config.DEFAULT_TEMPERATURE
    stream = body.stream or False

    # Detect VS Code Continue commands embedded in the user's last message
    # If found, route to the specialized Swift array handlers so Continue can
    # use the /v1/chat/completions endpoint for these commands.
    last_user = None
    for m in reversed(messages):
        if m.role == "user":
            last_user = m.content
            break

    if last_user:
        lower = last_user.lower()
        # Recognize both the @command and plain command tokens
        if "@renumber-verses" in lower or "renumber-verses" in lower:
            # Try to extract Swift code from the user's message; if not found,
            # try concatenating all user messages. If still not found, fall
            # back to normal AI processing.
            code = SwiftArrayFormatter.extract_swift_code(last_user)
            if not code:
                # concatenate all user messages as a last resort
                all_user = "\n".join([m.content for m in messages if m.role == "user"])
                code = SwiftArrayFormatter.extract_swift_code(all_user)

            if code:
                cmd = SwiftArrayCommand(code=code, model=model, max_tokens=max_tokens, temperature=temperature)
                resp = await renumber_verses_stream(cmd)
                # Extract and wrap the code in markdown for VS Code Continue chat
                try:
                    content = resp["choices"][0]["message"]["content"]
                    # Extract the inner Swift code (no fenced block)
                    inner = SwiftArrayFormatter.extract_swift_code(content) or SwiftArrayFormatter.extract_code_from_response(content) or content
                    # Wrap in markdown code block for VS Code Continue
                    formatted_response = f"```swift\n{inner}\n```"
                    
                    # Return streaming or regular response based on request
                    if stream:
                        return StreamingResponse(
                            create_streaming_response(formatted_response, model),
                            media_type="text/event-stream"
                        )
                    else:
                        return ResponseBuilder.build_chat_completion(formatted_response, model)
                except Exception:
                    if stream:
                        content = resp["choices"][0]["message"]["content"]
                        return StreamingResponse(
                            create_streaming_response(content, model),
                            media_type="text/event-stream"
                        )
                    return resp

        if "@clean-verses" in lower or "clean-verses" in lower:
            code = SwiftArrayFormatter.extract_swift_code(last_user)
            if not code:
                all_user = "\n".join([m.content for m in messages if m.role == "user"])
                code = SwiftArrayFormatter.extract_swift_code(all_user)

            if code:
                cmd = SwiftArrayCommand(code=code, model=model, max_tokens=max_tokens, temperature=temperature)
                resp = await clean_verses_stream(cmd)
                try:
                    content = resp["choices"][0]["message"]["content"]
                    inner = SwiftArrayFormatter.extract_swift_code(content) or SwiftArrayFormatter.extract_code_from_response(content) or content
                    # Wrap in markdown code block for VS Code Continue
                    formatted_response = f"```swift\n{inner}\n```"
                    
                    # Return streaming or regular response based on request
                    if stream:
                        return StreamingResponse(
                            create_streaming_response(formatted_response, model),
                            media_type="text/event-stream"
                        )
                    else:
                        return ResponseBuilder.build_chat_completion(formatted_response, model)
                except Exception:
                    if stream:
                        content = resp["choices"][0]["message"]["content"]
                        return StreamingResponse(
                            create_streaming_response(content, model),
                            media_type="text/event-stream"
                        )
                    return resp

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

    # Return streaming or regular response
    if stream:
        return StreamingResponse(
            create_streaming_response(reply_text, model),
            media_type="text/event-stream"
        )
    else:
        return ResponseBuilder.build_chat_completion(reply_text, model)

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

    reply_text = None
    
    if ai_client.is_available():
        # Try AI-based formatting first
        print(f"[DEBUG] Sending to {Config.AI_PROVIDER} with model: {model}")
        
        try:
            ai_reply = ai_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature
            )
            print(f"[DEBUG] Raw AI reply (first 500 chars): {ai_reply[:500]}")
            print(f"[DEBUG] Raw AI reply (last 500 chars): {ai_reply[-500:]}")
            
            reply_text = SwiftArrayFormatter.extract_code_from_response(ai_reply)
            print(f"[DEBUG] Cleaned response (first 500 chars): {reply_text[:500]}")
            
        except Exception as e:
            print(f"[DEBUG] Error calling AI provider: {e}")
            print(f"[DEBUG] Falling back to local deterministic formatter")
            # Don't raise - fall through to local formatter below
    
    # Use local deterministic formatter if AI not available or failed
    if reply_text is None:
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


@app.post("/renumber-verses")
async def renumber_verses(cmd: SwiftArrayCommand):
    """
    Alternative endpoint that returns just the formatted code without OpenAI wrapper.
    """
    try:
        response = await renumber_verses_stream(cmd)
        return {"formatted_code": response["choices"][0]["message"]["content"]}
    except Exception as e:
        # Fall back to local implementation if AI fails
        code_snippet = SwiftArrayFormatter.extract_swift_code(cmd.code)
        if not code_snippet:
            raise HTTPException(
                status_code=400,
                detail="Could not extract Swift code from input"
            )
        formatted = SwiftArrayFormatter.format_local(code_snippet)
        if not formatted:
            raise HTTPException(status_code=500, detail="Formatting failed")
        return {"formatted_code": formatted}


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


# Update the clean_verses function to call the stream function directly
@app.post("/clean-verses")
async def clean_verses(cmd: SwiftArrayCommand):
    """
    Alternative endpoint that returns just the cleaned code without OpenAI wrapper.
    """
    try:
        response = await clean_verses_stream(cmd)
        return {"cleaned_code": response["choices"][0]["message"]["content"]}
    except Exception as e:
        # Fall back to local implementation if AI fails
        cleaned = SwiftArrayFormatter.clean_comments_local(cmd.code)
        if not cleaned:
            raise HTTPException(status_code=500, detail="Comment cleaning failed")
        return {"cleaned_code": cleaned}

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

