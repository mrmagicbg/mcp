import os
import subprocess
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

SERVER_NAME = "linuxOps"
SAFE_BASE = Path("/opt/mcp/safefs").resolve()
ALLOWLIST_FILE = Path("/opt/mcp/server/allowed_cmds.txt").resolve()
SAFE_BASE.mkdir(parents=True, exist_ok=True)

app = FastAPI()

def read_allowlist():
    if not ALLOWLIST_FILE.exists():
        return []
    return [line.strip() for line in ALLOWLIST_FILE.read_text().splitlines() if line.strip() and not line.strip().startswith('#')]

@app.get("/health")
def health():
    return {"status": "ok", "server": SERVER_NAME}

@app.post("/exec")
def exec_allowlisted(payload: dict):
    cmd = payload.get("cmd", "")
    if not cmd:
        return JSONResponse({"error": "no cmd provided"}, status_code=400)
    if cmd not in read_allowlist():
        return JSONResponse({"error": f"DENIED: {cmd} not in allowlist"}, status_code=403)
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
        return {"stdout": res.stdout, "stderr": res.stderr, "returncode": res.returncode}
    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "command timeout"}, status_code=504)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("MCP_PORT", 3030)))
