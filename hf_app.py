"""Hugging Face Spaces entry point.
Runs FastAPI in a background thread + Streamlit-compatible setup.
"""
import os
import sys
import threading
import time
import uvicorn

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

# Initialize DB on startup
from core.database import init_db
init_db()

# Seed if empty
from core.database import get_db
with get_db() as conn:
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        from scripts.seed_db import seed
        seed()


def start_api():
    """Start FastAPI in background thread."""
    uvicorn.run("api.app:app", host="0.0.0.0", port=8000, log_level="warning")


# Start API server in background
api_thread = threading.Thread(target=start_api, daemon=True)
api_thread.start()
time.sleep(2)  # Wait for API to boot

# Set API base URL for Streamlit frontend
os.environ["API_BASE_URL"] = "http://localhost:8000/api"
