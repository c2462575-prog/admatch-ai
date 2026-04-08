"""Initialize the database with all tables."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.database import init_db

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
