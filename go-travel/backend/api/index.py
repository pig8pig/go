"""
Vercel Serverless Function Entry Point
=======================================
Exports the FastAPI app for Vercel's Python runtime.
Vercel auto-detects the `app` variable as an ASGI application.
"""
import sys
import os

# Ensure the parent directory (backend root) is in the Python path
# so that imports like `from agents import ...` work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
