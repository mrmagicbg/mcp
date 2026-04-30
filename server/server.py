import os
import shlex
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

SERVER_NAME = "linuxOps"
SAFE_BASE = Path("/opt/mcp/safefs").resolve()
ALLOWLIST_FILE = Path("/opt/mcp/server/allowed_cmds.txt").resolve()
SAFE_BASE.mkdir(parents=True, exist_ok=True)

# API key authentication (optional — set MCP_API_KEY env var to enable)
API_KEY = os.environ.get("MCP_API_KEY", "")

# Request logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/opt/mcp/server/audit.log", mode="a"),
    ]
)
logger = logging.getLogger("mcp-http")

app = FastAPI()


@app.middleware("http")
async def auth_and_logging_middleware(request: Request, call_next):
    """Validate API key (if configured) and log all requests."""
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path

    # Enforce API key if MCP_API_KEY is set
    if API_KEY:
        provided_key = request.headers.get("X-API-Key", "")
        if provided_key != API_KEY:
            logger.warning(f"AUTH_DENIED ip={client_ip} method={method} path={path}")
            return JSONResponse({"error": "unauthorized"}, status_code=401)

    response = await call_next(request)
    logger.info(f"ip={client_ip} method={method} path={path} status={response.status_code}")
    return response

def read_allowlist():
    if not ALLOWLIST_FILE.exists():
        return []
    return [line.strip() for line in ALLOWLIST_FILE.read_text().splitlines() if line.strip() and not line.strip().startswith('#')]

@app.get("/health")
def health():
    return {"status": "ok", "server": SERVER_NAME}

@app.get("/api/health")
def api_health():
    # Alias for monitoring tools that expect /api/health
    return {"status": "ok", "server": SERVER_NAME}

@app.get("/commands")
def list_commands():
    """Return the configured allowlisted commands."""
    cmds = read_allowlist()
    return {"commands": cmds, "count": len(cmds)}

@app.post("/exec")
def exec_allowlisted(payload: dict):
    cmd = payload.get("cmd", "")
    if not cmd:
        return JSONResponse({"error": "no cmd provided"}, status_code=400)
    allowlist = read_allowlist()
    # Allow exact matches or commands that start with an allowlist entry plus a space
    def is_allowed(requested: str):
        for a in allowlist:
            if requested == a:
                return True
            # prefix match: allow 'ping -c' to match 'ping -c 1 10.10.10.1'
            if requested.startswith(a + " "):
                return True
        return False

    if not is_allowed(cmd):
        return JSONResponse({"error": f"DENIED: {cmd} not in allowlist"}, status_code=403)
    try:
        # Use shell=False with shlex to prevent shell injection
        args = shlex.split(cmd)
        logger.info(f"EXEC cmd={cmd}")
        res = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=60)
        return {"stdout": res.stdout, "stderr": res.stderr, "returncode": res.returncode}
    except subprocess.TimeoutExpired:
        logger.warning(f"TIMEOUT cmd={cmd}")
        return JSONResponse({"error": "command timeout"}, status_code=504)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("MCP_PORT", 3030)))
