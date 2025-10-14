# Quick Start Guide - Using Mistral AI

## 🚀 Get Started in 3 Steps

### Step 1: Set Your API Key

Create a `.env` file in the project root:

```bash
# Create .env file with Mistral configuration
cat > .env << 'EOF'
AI_PROVIDER=openai
API_BASE_URL=https://api.mistral.ai/v1
API_KEY=your_mistral_api_key_here
EOF
```

**Note:** Mistral uses OpenAI-compatible API format, so set `AI_PROVIDER=openai` and point to Mistral's endpoint.

**Where to get your API key:**

1. Go to https://console.mistral.ai/
2. Sign up or log in
3. Navigate to "API Keys"
4. Copy your API key

### Step 2: Start the Server

```bash
python3 ai-server.py
```

You should see:

```
[DEBUG] AI_PROVIDER: mistral
[DEBUG] API_ENDPOINT: https://api.mistral.ai/v1/chat/completions
[DEBUG] API_KEY: ********
[DEBUG] DEFAULT_MODEL: mistral-small-latest
[DEBUG] OpenAI-compatible: True
INFO:     Uvicorn running on http://0.0.0.0:5000
```

### Step 3: Test It!

```bash
# Check health
curl http://localhost:5000/health

# Expected response:
# {
#   "ok": true,
#   "provider": "mistral",
#   "configured": true,
#   "model": "mistral-small-latest"
# }
```

## 💬 Using Chat Completions

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral-small-latest",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "max_tokens": 100
  }'
```

## 🔧 Configuration Details

Your `.env` file should contain:

```env
# Required
AI_PROVIDER=openai                              # Mistral uses OpenAI-compatible format
API_BASE_URL=https://api.mistral.ai/v1          # Mistral's endpoint (this is the default)
API_KEY=your_actual_mistral_api_key             # Your Mistral API key

# Or simplified (uses Mistral by default):
# AI_PROVIDER=openai
# API_KEY=your_actual_mistral_api_key
```

### Available Models

- `mistral-small-latest` (default) - Fast and cost-effective
- `mistral-medium-latest` - Balanced performance
- `mistral-large-latest` - Most capable

Change the model in requests or update `DEFAULT_MODEL` in `config.py`.

## 📝 Environment Variables Reference

| Variable       | Required | Default                     | Description                     |
| -------------- | -------- | --------------------------- | ------------------------------- |
| `AI_PROVIDER`  | No       | `openai`                    | Use `openai` for Mistral/OpenAI |
| `API_KEY`      | **Yes**  | None                        | Your Mistral API key            |
| `API_BASE_URL` | No       | `https://api.mistral.ai/v1` | Mistral endpoint (default)      |

## 🔍 Verification

After starting the server, you'll see these debug logs:

✅ **Correct Configuration:**

```
[DEBUG] AI_PROVIDER: openai
[DEBUG] API_ENDPOINT: https://api.mistral.ai/v1/chat/completions
[DEBUG] API_KEY: ********
[DEBUG] DEFAULT_MODEL: mistral-small-latest
[DEBUG] OpenAI-compatible: True
```

❌ **Missing API Key:**

```
[DEBUG] API_KEY: Not set
```

→ Check your `.env` file exists and contains `API_KEY=...`

## 🎯 Using with VS Code Continue

In your `.continue/config.json`:

```json
{
  "models": [
    {
      "title": "Mistral (via ai-server)",
      "provider": "openai",
      "model": "mistral-small-latest",
      "apiBase": "http://localhost:5000/v1",
      "apiKey": "not-needed"
    }
  ]
}
```

## 🆘 Troubleshooting

### Issue: "API_KEY: Not set"

**Solution:** Create/check your `.env` file:

```bash
echo "AI_PROVIDER=openai" > .env
echo "API_BASE_URL=https://api.mistral.ai/v1" >> .env
echo "API_KEY=your_key_here" >> .env
```

### Issue: 401 Unauthorized

**Solution:** Your API key is invalid. Get a new one from https://console.mistral.ai/

### Issue: Server not connecting to Mistral

**Solution:** Check:

1. Internet connection
2. API key is correct
3. Mistral service is not down (check status.mistral.ai)

## 📚 More Information

- **Full Setup Guide:** See `MISTRAL_SETUP.md`
- **API Documentation:** See `README.md`
- **Mistral Docs:** https://docs.mistral.ai/

## 💡 Tips

1. **OpenAI-Compatible:** Mistral uses OpenAI format, so set `AI_PROVIDER=openai`
2. **Cost Optimization:** Use `mistral-small-latest` for most tasks
3. **Rate Limits:** Free tier has lower limits; upgrade if needed
4. **Local Fallback:** Server works offline for basic Swift formatting
5. **Easy Switching:** Change `API_BASE_URL` to switch between Mistral/OpenAI/other providers

---

**Ready to use Mistral AI with your AI Server! 🎉**
