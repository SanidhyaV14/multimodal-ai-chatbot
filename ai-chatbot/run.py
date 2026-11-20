"""
Aura Dual Runner: Launches both FastAPI backend and Streamlit frontend simultaneously.
Usage:
    python run.py
"""
import sys
import time
import signal
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

# Automatically use the active Python interpreter or virtualenv
PYTHON_EXE = sys.executable

def start_services():
    print("=" * 65)
    print("✦ Launching Aura Emotional Companion Services...")
    print("=" * 65)

    # 1. Start FastAPI Backend
    print("🚀 Starting FastAPI Backend on http://localhost:8000...")
    backend_cmd = [
        PYTHON_EXE, "-m", "uvicorn", "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(ROOT_DIR)
    )

    # Give backend a moment to bind to port 8000
    time.sleep(2)

    # 2. Start Streamlit Frontend
    print("🌿 Starting Streamlit Frontend on http://localhost:8501...")
    frontend_cmd = [
        PYTHON_EXE, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port", "8501",
        "--server.headless", "false"
    ]
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=str(ROOT_DIR)
    )

    print("\n" + "=" * 65)
    print("✦ Both services are running:")
    print("  • Frontend UI:    http://localhost:8501")
    print("  • Backend API:    http://localhost:8000")
    print("  • API Swagger:    http://localhost:8000/docs")
    print("=" * 65)
    print("Press Ctrl+C at any time to gracefully terminate both services.\n")

    def shutdown(sig, frame):
        print("\n✦ Shutting down Aura services gracefully...")
        try:
            frontend_proc.terminate()
            backend_proc.terminate()
            frontend_proc.wait(timeout=3)
            backend_proc.wait(timeout=3)
        except Exception:
            frontend_proc.kill()
            backend_proc.kill()
        print("✦ All services stopped. Goodbye!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep orchestrator alive and monitor subprocesses
    try:
        while True:
            # If any process unexpectedly exits, trigger shutdown
            if backend_proc.poll() is not None:
                print("⚠️ FastAPI backend exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("⚠️ Streamlit frontend exited.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown(None, None)

if __name__ == "__main__":
    start_services()
