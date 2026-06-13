from __future__ import annotations

import os
import argparse
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
HEALTH_URL = "http://127.0.0.1:8000/health"
FRONTEND_URL = "http://127.0.0.1:5173"


def wait_for_backend(timeout_seconds: int = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f"Backend did not become healthy at {HEALTH_URL}. Last error: {last_error}")


def wait_for_url(url: str, timeout_seconds: int = 60) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error = ""
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f"URL did not become reachable at {url}. Last error: {last_error}")


def vite_command() -> list[str]:
    if os.name == "nt":
        vite = FRONTEND / "node_modules" / ".bin" / "vite.cmd"
    else:
        vite = FRONTEND / "node_modules" / ".bin" / "vite"
    return [str(vite), "--host", "127.0.0.1", "--port", "5173"]


def stop_process(proc: subprocess.Popen[bytes] | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        else:
            proc.terminate()
        proc.wait(timeout=8)
    except Exception:
        proc.kill()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run FailureLens IQ backend and frontend together.")
    parser.add_argument("--smoke-test", action="store_true", help="Start both servers, verify health, then stop them.")
    args = parser.parse_args()

    env = os.environ.copy()
    env.setdefault("HOST", "127.0.0.1")
    env.setdefault("PORT", "8000")
    env.setdefault("BACKEND_PORT", "8000")

    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.api.main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]

    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    backend = frontend = None
    try:
        print("[dev] starting FastAPI backend on http://127.0.0.1:8000")
        backend = subprocess.Popen(backend_cmd, cwd=ROOT, env=env, creationflags=creationflags)
        wait_for_backend()
        print("[dev] backend healthy")
        print("[dev] starting Vite frontend on http://127.0.0.1:5173")
        frontend = subprocess.Popen(vite_command(), cwd=FRONTEND, env=env, creationflags=creationflags)
        if args.smoke_test:
            wait_for_url(FRONTEND_URL)
            print("[dev] frontend reachable")
            print("[dev] smoke test passed")
            return 0
        while True:
            backend_code = backend.poll()
            frontend_code = frontend.poll()
            if backend_code is not None:
                print(f"[dev] backend exited with code {backend_code}")
                return backend_code
            if frontend_code is not None:
                print(f"[dev] frontend exited with code {frontend_code}")
                return frontend_code
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[dev] stopping full-stack dev servers")
        return 0
    finally:
        stop_process(frontend)
        stop_process(backend)


if __name__ == "__main__":
    raise SystemExit(main())
