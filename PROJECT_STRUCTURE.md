# Project Structure

The AI Server code has been reorganized following Python best practices with a proper package structure.

## Directory Layout

```
ai-server/
├── src/                        # Source code (Python package)
│   └── ai_server/              # Main package
│       ├── __init__.py         # Package initialization
│       ├── server.py           # FastAPI application and routes
│       ├── config.py           # Configuration management
│       ├── models.py           # Pydantic data models
│       ├── ai_client.py        # AI client (Mistral, OpenAI, Ollama)
│       ├── response_builder.py # Response formatting
│       ├── swift_formatter.py  # Swift code formatting logic
│       └── ollama_client.py    # Legacy Ollama client
│
├── run.py                      # Main entry point (recommended)
├── ai-server.py                # Legacy entry point (backward compatible)
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration (create this)
│
├── README.md                   # Main documentation
├── QUICK_START.md              # Quick setup guide
├── MISTRAL_SETUP.md            # Mistral configuration guide
├── SUMMARY.md                  # Configuration summary
├── PROJECT_STRUCTURE.md        # This file
│
├── env.mistral.example         # Example Mistral configuration
└── venv/                       # Virtual environment (if created)
```

## Why This Structure?

This follows **Python packaging best practices**:

### 1. **src/ Layout** (PEP 420)

- ✅ Prevents accidental imports of development code
- ✅ Clear separation between source and other files
- ✅ Standard for modern Python projects
- ✅ Works seamlessly with setuptools, pip, and build tools

### 2. **Package Structure**

- ✅ Code is organized as a proper Python package (`ai_server`)
- ✅ Can be installed with `pip install -e .`
- ✅ Easy to import: `from ai_server import Config, AIClient`
- ✅ Better for testing and distribution

### 3. **Entry Points**

- **`run.py`** - Recommended modern entry point
- **`ai-server.py`** - Kept for backward compatibility

## Running the Server

### Option 1: Using run.py (Recommended)

```bash
python3 run.py
```

### Option 2: Using ai-server.py (Legacy, still works)

```bash
python3 ai-server.py
# or
./ai-server.py
```

### Option 3: As a Python module

```bash
python3 -m uvicorn src.ai_server.server:app --host 0.0.0.0 --port 5000
```

### Option 4: Direct import

```python
from src.ai_server.server import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=5000)
```

## Development Setup

### 1. Install Dependencies

```bash
# Using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Or install in user directory
pip3 install --user -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example configuration
cp env.mistral.example .env

# Edit .env and add your API key
nano .env  # or use your favorite editor
```

### 3. Run the Server

```bash
python3 run.py
```

## Importing the Package

You can import and use the package in your own Python code:

```python
# Import the entire package
from src import ai_server

# Import specific components
from src.ai_server import Config, AIClient, SwiftArrayFormatter

# Use the FastAPI app
from src.ai_server.server import app

# Initialize client
client = AIClient()
if client.is_available():
    response = client.chat_completion(
        messages=[{"role": "user", "content": "Hello!"}],
        model="mistral-small-latest"
    )
```

## Package Contents

### Core Modules

- **`server.py`** - FastAPI application with all API routes
- **`config.py`** - Configuration class with environment variables
- **`models.py`** - Pydantic models for request/response validation
- **`ai_client.py`** - Unified client for all AI providers

### Utilities

- **`response_builder.py`** - Builds OpenAI-compatible responses
- **`swift_formatter.py`** - Swift array formatting and manipulation
- **`ollama_client.py`** - Legacy Ollama-specific client (deprecated)

### Package Files

- **`__init__.py`** - Package initialization, exports main classes

## Testing Package Structure

```bash
# Verify imports work
python3 -c "from src.ai_server import Config, AIClient; print('✓ OK')"

# Check if all files compile
python3 -m py_compile src/ai_server/*.py

# List package contents
python3 -c "from src import ai_server; print(dir(ai_server))"
```

## Migration Notes

### Old Structure (Before)

```
ai-server/
├── ai-server.py
├── config.py
├── models.py
├── ai_client.py
├── response_builder.py
├── swift_formatter.py
└── ollama_client.py
```

### New Structure (After)

```
ai-server/
├── src/
│   └── ai_server/
│       ├── __init__.py
│       ├── server.py      (was ai-server.py)
│       ├── config.py
│       ├── models.py
│       ├── ai_client.py
│       ├── response_builder.py
│       ├── swift_formatter.py
│       └── ollama_client.py
├── run.py                  (new main entry point)
└── ai-server.py            (now just a launcher)
```

## Benefits of New Structure

1. **Professional** - Follows Python community standards
2. **Installable** - Can be installed as a package
3. **Testable** - Easier to write unit tests
4. **Importable** - Can import modules from other scripts
5. **Maintainable** - Clear separation of concerns
6. **Scalable** - Easy to add more modules
7. **Compatible** - Old entry point still works

## Future Enhancements

With this structure, we can easily add:

- `tests/` directory for unit tests
- `docs/` for Sphinx documentation
- `setup.py` or `pyproject.toml` for package distribution
- `scripts/` for utility scripts
- Multiple sub-packages if needed

## Common Commands

```bash
# Start server
python3 run.py

# Start with custom port
python3 -m uvicorn src.ai_server.server:app --port 8000

# Start with reload (development)
python3 -m uvicorn src.ai_server.server:app --reload

# Check health
curl http://localhost:5000/health

# Test imports
python3 -c "from src.ai_server import Config; print(Config.AI_PROVIDER)"
```

## Conclusion

This new structure makes the project more **professional, maintainable, and follows Python best practices**. The code is now properly packaged while maintaining full backward compatibility with the old entry point.
