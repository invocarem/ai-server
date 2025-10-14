# Code Migration to src/ Package Structure

## Summary

The AI Server codebase has been reorganized into a **proper Python package structure** following modern Python best practices (PEP 420 and src layout).

## What Changed?

### File Locations

| Old Location               | New Location                        | Notes                      |
| -------------------------- | ----------------------------------- | -------------------------- |
| `ai-server.py` (464 lines) | `src/ai_server/server.py`           | Main application           |
| `ai-server.py` (root)      | `ai-server.py` (launcher)           | Now just imports and runs  |
| `config.py`                | `src/ai_server/config.py`           | ✓                          |
| `models.py`                | `src/ai_server/models.py`           | ✓                          |
| `ai_client.py`             | `src/ai_server/ai_client.py`        | ✓                          |
| `response_builder.py`      | `src/ai_server/response_builder.py` | ✓                          |
| `swift_formatter.py`       | `src/ai_server/swift_formatter.py`  | ✓                          |
| `ollama_client.py`         | `src/ai_server/ollama_client.py`    | ✓ (legacy)                 |
| -                          | `src/ai_server/__init__.py`         | **New** - Package init     |
| -                          | `run.py`                            | **New** - Main entry point |

### Import Changes

All imports within the package now use **relative imports**:

**Before:**

```python
from config import Config
from models import Message
```

**After:**

```python
from .config import Config
from .models import Message
```

## How to Run (No Changes Needed!)

### Old way (still works):

```bash
python3 ai-server.py
```

### New recommended way:

```bash
python3 run.py
```

### Professional way:

```bash
python3 -m uvicorn src.ai_server.server:app --host 0.0.0.0 --port 5000
```

## Benefits

### 1. **Follows Python Standards**

- ✅ PEP 420 namespace packages
- ✅ src/ layout (prevents import errors)
- ✅ Proper package structure

### 2. **Better Organization**

- ✅ Clear separation between source and config
- ✅ Easier to navigate
- ✅ Professional project layout

### 3. **Installable Package**

Can now be installed and imported:

```python
from src.ai_server import Config, AIClient, SwiftArrayFormatter
```

### 4. **Testable**

Easy to add `tests/` directory:

```python
from src.ai_server.server import app
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get("/health")
```

### 5. **Backward Compatible**

- ✅ Old `ai-server.py` entry point still works
- ✅ Same API endpoints
- ✅ Same configuration
- ✅ No breaking changes

## Project Structure

```
ai-server/                          Root directory
├── src/                            Source code
│   └── ai_server/                  Main package
│       ├── __init__.py             Package exports
│       ├── server.py               FastAPI app (main routes)
│       ├── config.py               Configuration
│       ├── models.py               Data models
│       ├── ai_client.py            AI provider client
│       ├── response_builder.py     Response formatting
│       ├── swift_formatter.py      Swift formatting
│       └── ollama_client.py        Legacy Ollama client
│
├── run.py                          Main entry point ⭐
├── ai-server.py                    Legacy entry (still works)
├── requirements.txt                Dependencies
├── .env                            Configuration (create this)
│
├── README.md                       Main documentation
├── PROJECT_STRUCTURE.md            Detailed structure info
├── MIGRATION.md                    This file
├── QUICK_START.md                  Quick start guide
├── MISTRAL_SETUP.md                Mistral configuration
├── SUMMARY.md                      Config summary
│
└── env.mistral.example             Example configuration
```

## For Developers

### Running the Server

```bash
# Activate venv if you're using one
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the server
python3 run.py

# Or with auto-reload for development
python3 -m uvicorn src.ai_server.server:app --reload
```

### Importing in Code

```python
# Import the package
from src.ai_server import (
    Config,
    AIClient,
    SwiftArrayFormatter,
    Message,
    ChatCompletionRequest
)

# Use the components
config = Config()
print(f"Provider: {config.AI_PROVIDER}")

client = AIClient()
if client.is_available():
    print("AI client is configured!")
```

### Testing Imports

```bash
# Test package can be imported
python3 -c "from src.ai_server import Config; print('✓ Imports work')"

# Check package contents
python3 -c "from src import ai_server; print(dir(ai_server))"

# Verify version
python3 -c "from src.ai_server import __version__; print(__version__)"
```

## Common Patterns

### Pattern 1: Entry Point Pattern

```python
# run.py or any script
if __name__ == "__main__":
    from src.ai_server.server import main
    main()
```

### Pattern 2: Import and Use

```python
# your_script.py
from src.ai_server import AIClient, Config

client = AIClient()
response = client.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model=Config.DEFAULT_MODEL
)
```

### Pattern 3: Testing Pattern

```python
# tests/test_server.py
from src.ai_server.server import app
from fastapi.testclient import TestClient

def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

## Is This Standard?

**Yes!** This is the recommended structure for Python projects:

- ✅ Used by: Flask, Django, FastAPI projects
- ✅ Recommended by: Python Packaging Authority (PyPA)
- ✅ Required for: Publishing to PyPI
- ✅ Best practice: Testing, CI/CD, deployment

### Popular Projects Using src/ Layout

- **attrs** - Python package
- **black** - Python formatter
- **pytest** - Testing framework
- **requests** - HTTP library
- Many FastAPI projects

## Migration Checklist

- [x] Move Python modules to `src/ai_server/`
- [x] Create `__init__.py` with exports
- [x] Update imports to use relative imports (`.module`)
- [x] Create `run.py` entry point
- [x] Keep `ai-server.py` for backward compatibility
- [x] Update documentation
- [x] Test all imports work
- [x] Verify server starts correctly
- [x] Ensure backward compatibility

## Troubleshooting

### Issue: ModuleNotFoundError

```python
ModuleNotFoundError: No module named 'ai_server'
```

**Solution:** Use `src.ai_server` instead:

```python
from src.ai_server import Config  # ✓ Correct
# not: from ai_server import Config  # ✗ Wrong
```

### Issue: Imports Not Working

**Solution:** Make sure you're running from project root:

```bash
cd /path/to/ai-server  # Go to project root
python3 run.py         # Run from here
```

### Issue: Old ai-server.py Not Working

**Solution:** The file has been updated to a launcher. If you modified it, restore with:

```bash
git checkout ai-server.py  # If using git
# or copy from backup
```

## Next Steps

Potential future improvements:

1. **Add Tests**: Create `tests/` directory
2. **Add setup.py**: Make it pip-installable
3. **Add pyproject.toml**: Modern Python packaging
4. **Add CI/CD**: GitHub Actions, pytest
5. **Add Documentation**: Sphinx docs
6. **Add Type Checking**: mypy configuration
7. **Add Linting**: ruff or pylint config

## Conclusion

The code is now organized following **Python best practices** with a clean package structure. Everything still works as before, but the codebase is now more:

- ✅ **Professional**
- ✅ **Maintainable**
- ✅ **Testable**
- ✅ **Scalable**
- ✅ **Standard**

The old entry point (`ai-server.py`) still works for backward compatibility, but `run.py` is the recommended way going forward.
