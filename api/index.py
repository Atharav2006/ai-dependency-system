import sys
import os

# Add the backend directory to sys.path so 'app' can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app

# The FastAPI app is already imported from backend.app.main
# Vercel's Python runtime will look for the 'app' or 'handler' attribute
handler = app
