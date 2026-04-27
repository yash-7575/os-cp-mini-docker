#!/usr/bin/env python3
"""
web/server.py — Mini Docker Web Interface Backend
==================================================
FastAPI + WebSockets: executes compiled C binaries and streams
their stdout/stderr to the browser in real-time.

START:
  cd /path/to/mini-docker
  pip install fastapi uvicorn
  uvicorn web.server:app --host 0.0.0.0 --port 8080

Open browser: http://localhost:8080
From Windows (same WiFi): http://<ubuntu-ip>:8080
"""

import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent          # repo root
WEB  = Path(__file__).parent                 # web/ dir

# ── Binary map ───────────────────────────────────────────────────────────────
BINARIES: dict[str, Path] = {
    "1": ROOT / "bin" / "role1_demo",
    "2": ROOT / "bin" / "role2_demo",
    "3": ROOT / "bin" / "role3_demo",
    "4": ROOT / "bin" / "role4_demo",
    "5": ROOT / "bin" / "role5_demo",
}

# Role 4 is pure userspace (Banker's algo + POSIX sem) — no sudo needed
NEEDS_SUDO: set[str] = {"1", "2", "3", "5"}

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="Mini Docker Web UI", version="1.0.0")


@app.get("/")
async def root() -> HTMLResponse:
    """Serve the single-page frontend."""
    html = (WEB / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/api/status")
async def status() -> JSONResponse:
    """Return which binaries are compiled and ready."""
    result = {}
    for role_id, path in BINARIES.items():
        result[role_id] = {
            "exists": path.exists(),
            "path": str(path),
            "needs_sudo": role_id in NEEDS_SUDO,
        }
    return JSONResponse(result)


@app.websocket("/ws/run/{role}")
async def run_role(websocket: WebSocket, role: str) -> None:
    """
    WebSocket endpoint.
    Accepts a connection, runs the role binary, streams output line-by-line,
    then sends the sentinel '__DONE__' when the process exits.
    """
    await websocket.accept()

    binary = BINARIES.get(role)

    # ── Guards ────────────────────────────────────────────────────────────
    if binary is None:
        await websocket.send_text(f"ERROR: Unknown role '{role}'. Valid: 1-5\n")
        await websocket.close()
        return

    if not binary.exists():
        compile_cmd = f"sudo make role{role}" if role in NEEDS_SUDO else f"make role{role}"
        await websocket.send_text(
            f"ERROR: Binary not found: {binary}\n"
            f"  → Compile it first with:  {compile_cmd}\n"
        )
        await websocket.close()
        return

    # ── Build command ─────────────────────────────────────────────────────
    cmd = ["sudo", str(binary)] if role in NEEDS_SUDO else [str(binary)]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(ROOT),
        )

        # Stream stdout/stderr line-by-line to the WebSocket
        async for raw in proc.stdout:                          # type: ignore[union-attr]
            line = raw.decode("utf-8", errors="replace")
            try:
                await websocket.send_text(line)
            except WebSocketDisconnect:
                proc.kill()
                return

        await proc.wait()
        await websocket.send_text("\n__DONE__\n")

    except FileNotFoundError:
        await websocket.send_text(
            "ERROR: Could not execute binary.\n"
            "  → Make sure you're on Ubuntu/Linux with gcc and make installed.\n"
        )
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        try:
            await websocket.send_text(f"ERROR: {exc}\n")
        except Exception:
            pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
