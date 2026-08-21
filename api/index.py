import os
import sys

# Ensure repository root is on sys.path for serverless execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Exported ASGI app for Vercel serverless execution
__all__ = ["app"]
