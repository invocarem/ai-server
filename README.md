# AI Server

OpenAI-compatible adapter for Ollama or local Swift array formatting.

## Overview

This server provides OpenAI-compatible API endpoints for:

- Chat completions with multiple AI providers (Mistral, OpenAI, Ollama)
- Swift array verse numbering and cleaning
- Local fallback formatting when no AI provider is configured

### Supported Providers

All OpenAI-compatible APIs are supported, including:

- **Mistral AI** - Fast and affordable (default endpoint)
- **OpenAI** - GPT models
- **Ollama** - Local AI models
- **Any OpenAI-compatible API** - Just set the `API_BASE_URL`

## Architecture

The codebase follows **Python best practices** with a proper package structure:

```
ai-server/
├── src/ai_server/              # Main Python package
│   ├── server.py               # FastAPI application and routes
│   ├── config.py               # Configuration management
│   ├── models.py               # Pydantic data models
│   ├── ai_client.py            # AI client (Mistral, OpenAI, Ollama)
│   ├── response_builder.py     # Response formatting
│   └── swift_formatter.py      # Swift code formatting
├── run.py                      # Main entry point (recommended)
├── requirements.txt            # Python dependencies
└── .env                        # Your configuration
```

**See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed information.**

### Modules

- **server.py**: FastAPI application with all API routes
- **config.py**: Centralized configuration with environment variables
- **models.py**: Pydantic models for type-safe request/response handling
- **ai_client.py**: Unified client for all AI providers (Mistral, OpenAI, Ollama)
- **swift_formatter.py**: Swift array formatting with both AI and local methods
- **response_builder.py**: Builds OpenAI-compatible response structures

## Setup

### 1. Install Dependencies

Using virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Or with user installation:

```bash
pip3 install --user -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root with your AI provider configuration.

#### For Mistral AI (Default):

```env
AI_PROVIDER=openai
API_BASE_URL=https://api.mistral.ai/v1
API_KEY=your_mistral_api_key_here
```

Get your Mistral API key from: https://console.mistral.ai/

**Note:** Mistral uses OpenAI-compatible API, so set `AI_PROVIDER=openai`. The default `API_BASE_URL` is already set to Mistral, so you can omit it:

```env
AI_PROVIDER=openai
API_KEY=your_mistral_api_key_here
```

#### For OpenAI:

```env
AI_PROVIDER=openai
API_BASE_URL=https://api.openai.com/v1
API_KEY=your_openai_api_key_here
```

#### For Ollama (Local):

```env
AI_PROVIDER=ollama
API_BASE_URL=http://localhost:11434
```

**Note:** Ollama v0.1.17+ supports OpenAI-compatible endpoints. This server now uses `/v1/chat/completions` endpoint for Ollama.

If your Ollama is running on a different host/port:

```env
AI_PROVIDER=ollama
API_BASE_URL=http://your-ollama-host:11434
```

#### Configuration Options:

- `AI_PROVIDER` - Which provider to use: `openai` (for Mistral, OpenAI, etc.) or `ollama` for local Ollama (default: `openai`)
- `API_KEY` - Your API key for Mistral or OpenAI (not needed for Ollama)
- `API_BASE_URL` - API endpoint (default: `https://api.mistral.ai/v1` for OpenAI provider, `http://localhost:11434` for Ollama)

**Legacy Ollama variables** (still supported):

- `OLLAMA_URL` - URL of your Ollama instance (use `API_BASE_URL` instead)

If no provider is configured, the server falls back to local formatting.

### 3. Run the Server

```bash
# Recommended way
python3 run.py

# Or using the legacy entry point
python3 ai-server.py

# Or with uvicorn directly
python3 -m uvicorn src.ai_server.server:app --host 0.0.0.0 --port 5000
```

The server will start on `http://0.0.0.0:5000`

## API Endpoints

### Chat Completions

**POST** `/v1/chat/completions`

````bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'


### Renumber Verses

**POST** `/renumber-verses-stream`

Adds sequential numbering to Swift array elements.

```json
{
  "code": "private let verses = [\n  \"First verse\",\n  \"Second verse\"\n]",
  "model": "mistral:latest",
  "max_tokens": 512,
  "temperature": 0.0
}
````

**POST** `/renumber-verses`

Same as above but returns simplified response:

````json
{
  "formatted_code": "```swift\n...\n```"
}
````

```bash
$ curl -X POST http://localhost:5000/renumber-verses   -H "Content-Type: application/json"   -d @input.json -o output.json
```

### Clean Verses

**POST** `/clean-verses`

Removes all `/* number */` comments from Swift array.

```json
{
  "code": "private let verses = [\n  /* 1 */ \"First verse\",\n  /* 2 */ \"Second verse\"\n]",
  "model": "mistral:latest"
}
```

**POST** `/clean-verses`

Same as above but returns simplified response:

````json
{
  "cleaned_code": "```swift\n...\n```"
}
````

### Health Check

**GET** `/health`

Returns server health status:

```json
{
  "ok": true,
  "ollama": true
}
```

### List Models

**GET** `/v1/models`

Lists available models:

```json
{
  "data": [
    { "id": "mistral:latest", "object": "model" },
    { "id": "deepseek-coder:6.7b", "object": "model" }
  ]
}
```

## Features

### Refactored Architecture

The codebase has been refactored for better:

- **Modularity**: Separated concerns into focused modules
- **Maintainability**: Clear separation between API, business logic, and utilities
- **Testability**: Each module can be tested independently
- **Readability**: Cleaner code with better organization
- **Type Safety**: Comprehensive type hints and Pydantic models

### Dual Mode Operation

- **Ollama Mode**: Forward requests to Ollama for AI-powered processing
- **Local Mode**: Use deterministic local algorithms as fallback

### Swift Array Formatting

- Automatic sequential numbering of array elements
- Comment cleaning while preserving structure
- Markdown code block extraction
- Preservation of original formatting and indentation

## Development

### Testing

Basic import and functionality test:

```bash
python3 test_imports.py
```

### Code Structure

The refactored architecture follows these principles:

- Single Responsibility: Each module has one clear purpose
- Dependency Injection: OllamaClient and formatters are instantiated once
- Configuration Management: All settings in one place
- Error Handling: Consistent error handling across modules

## Version

Current version: **0.5** (Refactored)

## License

See project license file.
