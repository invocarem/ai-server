#!/usr/bin/env python3
"""
Main entry point for AI Server.

This script launches the FastAPI server with Uvicorn.
"""

if __name__ == "__main__":
    from src.ai_server.server import main
    main()

