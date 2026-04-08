"""Start both FastAPI and Streamlit for development."""
import subprocess
import sys
import os
import signal

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)

processes = []

def cleanup(sig=None, frame=None):
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == "__main__":
    # Initialize and seed DB
    subprocess.run([sys.executable, "scripts/init_db.py"])
    subprocess.run([sys.executable, "scripts/seed_db.py"])

    # Start FastAPI
    api = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api.app:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ])
    processes.append(api)
    print("FastAPI started at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")

    # Start Streamlit
    st = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501", "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false"
    ])
    processes.append(st)
    print("Streamlit started at http://localhost:8501")

    try:
        api.wait()
    except KeyboardInterrupt:
        cleanup()
