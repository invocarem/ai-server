# Setting Up Mistral AI with AI-Server

This guide will help you configure the AI server to use Mistral AI.

## Step 1: Get Your Mistral API Key

1. Visit [Mistral AI Console](https://console.mistral.ai/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key or copy your existing one

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your Mistral configuration:

```env
# Set provider to Mistral
AI_PROVIDER=mistral

# Add your Mistral API key
API_KEY=your_actual_mistral_api_key_here
```

That's it! The server will automatically use Mistral's API endpoint (`https://api.mistral.ai/v1/chat/completions`).

## Step 3: Verify Configuration

Start the server:

```bash
python3 ai-server.py
```

You should see output like:

```
[DEBUG] AI_PROVIDER: mistral
[DEBUG] API_ENDPOINT: https://api.mistral.ai/v1/chat/completions
[DEBUG] API_KEY: ********
[DEBUG] DEFAULT_MODEL: mistral-small-latest
[DEBUG] OpenAI-compatible: True
```

## Step 4: Test the Server

### Test with health endpoint:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{
  "ok": true,
  "provider": "mistral",
  "configured": true,
  "model": "mistral-small-latest"
}
```

### Test with chat completions:

```bash
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
```

## Available Mistral Models

The server supports these Mistral models:

- `mistral-small-latest` - Fast and cost-effective (default)
- `mistral-medium-latest` - Balanced performance
- `mistral-large-latest` - Most capable model

You can specify the model in your requests or change the default in `config.py`.

## Advanced Configuration

### Custom API Base URL

If you're using a proxy or custom endpoint:

```env
AI_PROVIDER=mistral
API_BASE_URL=https://your-custom-endpoint.com/v1/chat/completions
API_KEY=your_api_key
```

### Multiple Providers

You can easily switch between providers by changing the `AI_PROVIDER` variable:

```env
# For Mistral
AI_PROVIDER=mistral
API_KEY=your_mistral_key

# For OpenAI
# AI_PROVIDER=openai
# API_KEY=your_openai_key

# For Ollama (local)
# AI_PROVIDER=ollama
# API_BASE_URL=http://localhost:11434
```

## Using with VS Code Continue

In your Continue configuration (`.continue/config.json`), use:

```json
{
  "models": [
    {
      "title": "Mistral via Local Server",
      "provider": "openai",
      "model": "mistral-small-latest",
      "apiBase": "http://localhost:5000/v1",
      "apiKey": "not-needed"
    }
  ]
}
```

## Troubleshooting

### "API_KEY: Not set" in debug logs

Make sure your `.env` file is in the correct location and contains:

```env
API_KEY=your_actual_key_here
```

### "AI provider 'mistral' is not properly configured"

Check that:

1. Your `.env` file exists and is loaded
2. `API_KEY` is set in the `.env` file
3. The API key is valid

### 401 Unauthorized error

Your API key is invalid or expired. Get a new one from [Mistral Console](https://console.mistral.ai/).

### Rate limiting errors

Mistral has rate limits based on your subscription tier. Consider:

- Reducing request frequency
- Upgrading your Mistral plan
- Using `mistral-small-latest` which has higher rate limits

## Cost Optimization

To minimize costs with Mistral:

1. Use `mistral-small-latest` for most tasks (default)
2. Set appropriate `max_tokens` limits
3. Use `temperature: 0.0` for deterministic outputs
4. Enable local fallback for simple formatting tasks

The server automatically falls back to local formatting if the AI provider is not configured, so you can work offline for basic tasks.

## Example: Swift Array Formatting with Mistral

```bash
curl -X POST http://localhost:5000/renumber-verses-stream \
  -H "Content-Type: application/json" \
  -d '{
    "code": "private let verses = [\n  \"First verse\",\n  \"Second verse\"\n]",
    "model": "mistral-small-latest"
  }'
```

Mistral will intelligently format your Swift arrays with sequential numbering!
