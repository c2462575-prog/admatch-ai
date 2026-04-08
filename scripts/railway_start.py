"""Railway deployment: start API + Streamlit in single service.

Railway exposes one PORT. We run:
- FastAPI on internal port 8000
- Streamlit on $PORT (Railway-exposed)
- Streamlit calls API via localhost:8000
"""
import subprocess
import sys
import os
import signal
import time

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)

# Ensure API_BASE_URL points to internal API
os.environ["API_BASE_URL"] = "http://localhost:8000/api"

PORT = os.environ.get("PORT", "8501")
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
    # Init DB
    subprocess.run([sys.executable, "scripts/init_db.py"], check=True)

    # Seed if empty
    subprocess.run([sys.executable, "scripts/seed_db.py"])

    # Start FastAPI (internal, port 8000)
    api = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api.app:app",
        "--host", "0.0.0.0", "--port", "8000",
    ])
    processes.append(api)
    print(f"[Railway] FastAPI started on internal port 8000")

    time.sleep(2)  # Wait for API to boot

    # Start Streamlit on Railway's PORT
    st_proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", PORT,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
    ])
    processes.append(st_proc)
    print(f"[Railway] Streamlit started on port {PORT}")

    try:
        # Wait for either process to exit
        while True:
            for p in processes:
                ret = p.poll()
                if ret is not None:
                    print(f"[Railway] Process exited with code {ret}")
                    cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
