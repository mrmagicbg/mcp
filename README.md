# MCP Server: Remote Command Execution + Spec-Kit Integration

## Overview

The **MCP (Model Context Protocol) Server** is a unified platform combining safe remote command execution with GitHub Spec-Kit integration. It provides multiple interfaces for AI agents, CI/CD systems, and development tools to interact with system operations and development workflows.

**Integrated Architecture:**
- **FastAPI Command Server** (port 3030) - MCP-compatible REST API for remote operations
- **Spec-Kit MCP Server** (stdio) - Model Context Protocol interface to GitHub Spec-Kit
- **Spec-Kit Web UI** (port 5000) - Browser-based interface for documentation/spec processing
- **Unified Deployment** - Single setup.sh and deploy.sh for both components
- **systemd Integration** - Production-ready service management
 - **Health Endpoints** - MCP: `/health`, Web UI: `/health`

**Core Features:**
- ✅ Command allowlisting (4 security tiers)
- ✅ 60-second execution timeout with error handling
- ✅ FastAPI REST endpoints with JSON responses
- ✅ MCP protocol compatibility for AI agents
- ✅ Spec-Kit integration for spec-driven development
- ✅ Web UI for interactive prompt processing
- ✅ Comprehensive test suite
- ✅ CLI helper tools

**Use Cases:**
- Remote system monitoring and administration via API
- Safe CI/CD operations and deployments
- Development workflow automation
- AI agent operations and tool discovery
- Spec-driven development workflows
- Network diagnostics and maintenance

## Architecture

```
MCP Server (Unified Installation)
├── FastAPI HTTP Server (port 3030)
│   ├── /health - Health check
│   ├── /api/health - Health alias
│   ├── /commands - List allowlisted commands
│   ├── /exec - Execute allowlisted commands
│   ├── /mcp/tools - Tool definitions for agents
│   └── /mcp/describe - Tool descriptions
├── Spec-Kit Web UI (port 5000)
│   ├── /health - Health check
│   ├── /api/health - Health alias
│   ├── /api/commands - REST API
│   ├── /api/process - Spec processing
│   └── /api/history - Execution history
└── Spec-Kit MCP Server (stdio)
    ├── MCP protocol endpoints
    └── Spec-Kit tool execution
```

## Installation & Setup

### Prerequisites
- Ubuntu 24.04 LXC container on Proxmox (or any Ubuntu 24.04 system)
- Root access for initial setup
- Git and curl installed

### Automated Installation (Recommended)

Run the unified installer on the target system:

```bash
# On target system (as root)
cd /opt/mcp
git clone https://github.com/mrmagicbg/mcp.git .
sudo bash setup.sh

# See admin operations guide
# docs/ADMIN.md
```

The installer will:
✅ Create `mrmagic` user with proper permissions
✅ Set up Python 3.12 virtual environment
✅ Install FastAPI, Uvicorn, Flask, and dependencies
✅ Install uv package manager
✅ Install GitHub Spec-Kit via uv
✅ Copy server files to `/opt/mcp/server/` and `/opt/mcp/web/`
✅ Copy templates to `/opt/mcp/templates/`
✅ Configure both systemd services (mcp-http, spec-kit-web)
✅ Start both services and verify
✅ Expose health endpoints for monitoring

### Manual Installation
If you prefer manual setup:

```bash
# Create user and directories
sudo useradd --system --create-home --home-dir /home/mcpbot --shell /usr/sbin/nologin mcpbot
sudo mkdir -p /opt/mcp/server
sudo chown -R mcpbot:mcpbot /opt/mcp

# Install dependencies
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
python3 -m venv /opt/mcp/venv
/opt/mcp/venv/bin/pip install fastapi uvicorn

# Copy files and start service
sudo cp -r server/* /opt/mcp/server/
sudo cp systemd/mcp-http.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mcp-http.service
```

### Verification
```bash
sudo systemctl status mcp-http.service
curl http://localhost:3030/health
```

## Configuration

### Allowlist Management
Commands are restricted to those in `server/allowed_cmds.txt`. The file is organized in 4 tiers:

**Tier 1: Safe Monitoring & Info**
- `uptime`, `df -h`, `df -i`, `free -m`, `free -h`, `who`, `uname -a`, `cat /etc/os-release`
- `lscpu`, `lsb_release -a`, `date`, `ps aux`, `du -h`, `du -sh`

**Tier 2: Developer Operations**
- `git clone`, `git pull`, `git status`, `git commit -m`, `git push`
- `git log --oneline -10`, `git diff --stat`, `git branch -a`
- `pip install`, `pip list`, `python3`, `python3 -c`, `python3 -m pip`, `python3 -m venv`
- `python3 -m pytest`, `python3 -m unittest discover`
- `ls -l`, `ls -la`, `cat`, `echo`, `find`, `grep`, `head`, `tail`, `wc -l`
- `make`, `sqlite3`, `tar -tzf`, `tar -xzf`, `gzip -l`

**Tier 3: Administrative Operations**
- `sudo apt update`, `sudo apt upgrade -y`, `sudo apt install -y ...`
- `sudo apt list --installed`, `sudo apt search`
- `sudo systemctl status`, `sudo systemctl restart`, `sudo systemctl stop`, `sudo systemctl start`
- `sudo systemctl enable`, `sudo systemctl disable`, `sudo journalctl -u`
- `id`, `whoami`

**Install and Package Management (prefixes allowed)**
- `sudo apt install -y`, `apt install -y`, `sudo apt-get install -y`, `apt-get install -y`
- `sudo apt remove -y`, `sudo apt purge -y`
- `pip install`, `pip3 install`, `python3 -m pip install`, `sudo python3 -m pip install`
- `dpkg -i`, `snap install`, `snap remove`

**Tier 4: Network Operations** (Added for network discovery)
- `ping -c 1`, `ping -c 3`, `arp -a`, `ip neigh`, `ip route`, `ip addr`, `hostname -I`
- `nslookup`, `dig`, `traceroute`, `netstat -tlnp`, `ss -tlnp`

**To modify the allowlist:**
1. Edit `server/allowed_cmds.txt`
2. Restart the service: `sudo systemctl restart mcp-http.service`

### Server Configuration
- **Port**: 3030 (configurable via `MCP_PORT` environment variable)
- **Host**: 0.0.0.0 (binds to all interfaces)
- **User**: mcpbot (restricted permissions)
- **Timeout**: 60 seconds per command
- **Working Directory**: `/opt/mcp/server`

## API Reference

### Base URL
```
http://<server-ip>:3030
```

### Endpoints

#### GET /health
Returns server status and name.

**Response:**
```json
{
  "status": "ok",
  "server": "linuxOps"
}
```

#### POST /exec
Executes an allowlisted command.

**Request Body:**
```json
{
  "cmd": "uptime"
}
```

**Success Response:**
```json
{
  "stdout": " 14:23:01 up 2 days,  1 user,  load average: 0.15, 0.10, 0.05\n",
  "stderr": "",
  "returncode": 0
}
```

**Error Response:**
```json
{
  "error": "DENIED: nmap not in allowlist"
}
```

**Error Codes:**
- `400`: No command provided
- `403`: Command not in allowlist
- `504`: Command timeout (60s)

## Usage Examples

### Command Line
```bash
# Health check
curl http://10.10.10.24:3030/health

# Execute command
curl -X POST -H "Content-Type: application/json" \
  -d '{"cmd":"uptime"}' \
  http://10.10.10.24:3030/exec

# Network discovery
curl -X POST -H "Content-Type: application/json" \
  -d '{"cmd":"ping -c 1 10.10.10.1"}' \
  http://10.10.10.24:3030/exec

# Using the helper script
python3 mcp_cmd.py "df -h"
python3 mcp_cmd.py "ping -c 3 8.8.8.8"
python3 mcp_cmd.py "arp -a"
```

### Python Integration
```python
import requests

class MCPClient:
    def __init__(self, url="http://10.10.10.24:3030"):
        self.url = url

    def health_check(self):
        return requests.get(f"{self.url}/health").json()

    def execute(self, cmd):
        response = requests.post(f"{self.url}/exec", json={"cmd": cmd})
        return response.json()

    def ping_host(self, ip):
        return self.execute(f"ping -c 1 {ip}")

# Usage
client = MCPClient()
print("Server health:", client.health_check())

# Network discovery
result = client.ping_host("10.10.10.1")
if "error" in result:
    print(f"Ping failed: {result['error']}")
else:
    print("Ping result:", result["stdout"])
```

### VS Code Integration

#### Tasks Configuration
The `.vscode/tasks.json` provides:
- **Test MCP Server**: Run automated endpoint tests
- **Health Check**: Quick server status
- **Run Remote Command**: Interactive command execution with input prompt

#### MCP Configuration
`.vscode/mcp.json` contains server connection details for extensions.

#### Workflow Example
1. Open MCP project in VS Code
2. Run "Test MCP Server" task to verify connection
3. Use "Run Remote Command" to execute allowlisted operations
4. Integrate with custom extensions using the API

## Testing

### Automated Testing
```bash
python3 test_server.py
```

This runs tests for:
- Health endpoint
- Multiple allowlisted commands across all tiers
- Error handling for denied commands

### Manual Testing
```bash
# Test various commands
python3 mcp_cmd.py uptime
python3 mcp_cmd.py "ls -l /opt/mcp"
python3 mcp_cmd.py "ping -c 1 127.0.0.1"
python3 mcp_cmd.py "ip route"
```

### Network Discovery Testing
```bash
# Ping gateway
python3 mcp_cmd.py "ping -c 1 10.10.10.1"

# Check ARP table
python3 mcp_cmd.py "arp -a"

# Show network interfaces
python3 mcp_cmd.py "ip addr"
```

## Security Considerations

### Command Restrictions
- Only explicitly allowlisted commands execute
- Arguments are validated as part of command string
- No shell injection possible (uses `subprocess.run` with restricted commands)

### User Isolation
- Commands run as `mcpbot` user with limited privileges
- No access to sensitive files or operations
- Network access restricted by container configuration

### Network Security
- Bind to specific IP ranges if needed
- Use HTTPS in production (add reverse proxy like nginx)
- Implement API key authentication for production use
- Rate limiting recommended for production deployments

### Monitoring
- Check systemd logs: `sudo journalctl -u mcp-http.service`
- Monitor command execution in application logs
- Implement audit logging for security

## Troubleshooting

### Service Issues
```bash
# Check service status
sudo systemctl status mcp-http.service

# View logs
sudo journalctl -u mcp-http.service -f

# Restart service
sudo systemctl restart mcp-http.service
```

### Connection Problems
- Verify port 3030 is open: `sudo ufw status` or `sudo iptables -L`
- Check container networking in Proxmox
- Test local connectivity: `curl http://localhost:3030/health`

### Command Failures
- Verify command is in allowlist: `cat /opt/mcp/server/allowed_cmds.txt`
- Check command syntax and permissions
- Review stderr in API response

### Common Issues
- **Permission denied**: Command requires sudo but not allowlisted with sudo
- **Command not found**: Package not installed on container
- **Timeout**: Long-running commands exceed 60s limit
- **Network unreachable**: Container network configuration issues

## Files

- `server/server.py` - FastAPI application with /health and /exec endpoints
- `server/allowed_cmds.txt` - Command allowlist organized in tiers
- `setup.sh` - Automated installation script
- `deploy.sh` - Automated deployment/update script
- `systemd/mcp-http.service` - Systemd service configuration
- `test_server.py` - Comprehensive test suite
- `mcp_cmd.py` - CLI helper for remote command execution
- `.vscode/tasks.json` - VS Code tasks for testing and interaction
- `.vscode/mcp.json` - VS Code integration configuration

## Extending the Server

### Adding Commands
1. Edit `server/allowed_cmds.txt`
2. Test the command manually as `mcpbot` user
3. Restart the service
4. Update documentation

### Custom Endpoints
Modify `server/server.py` to add new endpoints:
```python
@app.get("/custom")
def custom_endpoint():
    # Your custom logic
    return {"result": "custom data"}
```

### Authentication
Add API key validation:
```python
API_KEY = os.environ.get("MCP_API_KEY")

@app.post("/exec")
def exec_allowlisted(payload: dict, api_key: str = Header(None)):
    if api_key != API_KEY:
        return JSONResponse({"error": "Invalid API key"}, status_code=401)
    # ... rest of function
```

## Deployment

### Automated Deployment

The MCP server can update itself using the deployment script. SSH to the MCP server and run:

```bash
# SSH to MCP server
ssh user@10.10.10.24

# Run deployment script
sudo bash /path/to/deploy.sh
```

Or download and run directly:

```bash
# Download and run deployment script
curl -s https://raw.githubusercontent.com/mrmagicbg/mcp/main/deploy.sh | sudo bash
```

The deployment script will:
- Clone/update the repository
- Install any missing dependencies
- Update server files
- Restart the MCP service
- Test the deployment
- Clean up temporary files

### Manual Deployment

If you prefer manual deployment:

```bash
# On the MCP server
cd /tmp
git clone https://github.com/mrmagicbg/mcp.git
cd mcp

# Update server files
sudo cp -r server/* /opt/mcp/server/
sudo chown -R mcpbot:mcpbot /opt/mcp/server

# Restart service
sudo systemctl restart mcp-http.service

# Test
curl http://localhost:3030/health

# Cleanup
cd /
rm -rf /tmp/mcp
```

### Deployment Commands

#### Quick Deployment (On the MCP Server)
```bash
# On the MCP server (10.10.10.24), run:
cd ~ && git clone https://github.com/mrmagicbg/mcp.git && cd mcp && sudo bash deploy.sh
```

#### Alternative: Download and Execute
```bash
# On the MCP server, download and run directly:
cd ~ && wget https://github.com/mrmagicbg/mcp/archive/main.zip && unzip main.zip && cd mcp-main && sudo bash deploy.sh
```

#### Manual Deployment Steps (On the MCP Server)
```bash
# 1. Clone repository
cd ~
git clone https://github.com/mrmagicbg/mcp.git
cd mcp

# 2. Run deployment
sudo bash deploy.sh

# 3. Verify deployment
curl http://localhost:3030/health
curl -X POST -H "Content-Type: application/json" \
  -d '{"cmd":"python3 --version"}' \
  http://localhost:3030/exec

# 4. Cleanup (optional)
cd ~ && rm -rf ~/mcp
```

#### Post-Deployment Testing
```bash
# From your local machine, test the deployed server
python3 mcp_cmd.py "uptime"
python3 mcp_cmd.py "python3 --version"
python3 mcp_cmd.py "git status"
```

## Spec-Kit MCP Integration

### Overview

This repository includes a complete integration with **GitHub Spec-Kit**, a spec-driven development toolkit. Two interfaces are provided:

1. **Web UI** (http://your-server:5000) - Browser-based interface for command execution
2. **MCP Server** (stdio-based) - Model Context Protocol interface for AI agents and tools

### Quick Start

#### Installation
```bash
# Clone and deploy spec-kit
cd /opt/mcp/spec-kit
sudo bash install.sh

# Verify
sudo systemctl status spec-kit-web.service spec-kit-mcp.service
curl http://localhost:5000/api/commands
```

#### Web UI Access
```
http://10.10.10.24:5000
```

Features:
- Command execution (check, version, init)
- Real-time output display
- Copy/paste support
- Command history tracking

#### MCP Server Usage
```bash
# Run MCP server
python3 /opt/mcp/spec-kit/server/server.py

# Or use as systemd service
sudo systemctl status spec-kit-mcp.service
```

Available tools:
- `specify_init` - Create new Specify project
- `specify_check` - Check tool dependencies
- `specify_version` - Display version info
- `specify_run_command` - Execute custom commands

### Architecture

```
mcp/
├── server/              # FastAPI command execution server
├── systemd/             # systemd service files
├── spec-kit/            # Spec-Kit integration
│   ├── server/          # MCP protocol implementation (stdio)
│   ├── web/             # Flask web application
│   │   ├── app.py       # Web server and API
│   │   └── templates/   # HTML/CSS/JS UI
│   ├── systemd/         # Service configurations
│   └── docs/            # Installation and deployment guides
└── README.md            # This file
```

### Documentation

- **[spec-kit/README.md](spec-kit/README.md)** - Feature overview and API reference
- **[spec-kit/docs/INSTALLATION.md](spec-kit/docs/INSTALLATION.md)** - Detailed installation guide
- **[spec-kit/docs/DEPLOYMENT.md](spec-kit/docs/DEPLOYMENT.md)** - Production deployment guide

### Services

#### spec-kit-web.service
- Flask HTTP server on port 5000
- Web UI and REST API
- Auto-start and auto-restart on failure

#### spec-kit-mcp.service
- stdio-based MCP protocol server
- Exposes spec-kit as Model Context Protocol tools
- Ready for AI agent integration

### Performance

- Web UI response: 100-500ms per command
- Command timeout: 60 seconds (configurable)
- Memory per service: ~25MB
- CPU idle: < 1%
- CPU executing: 2-5%

### Configuration

**Change web port (spec-kit/web/app.py):**
```python
app.run(host='0.0.0.0', port=5000)  # Change port number
```

**Change command timeout:**
```python
timeout=60  # Increase for longer operations
```

### Management

```bash
# Check status
sudo systemctl status spec-kit-web.service spec-kit-mcp.service

# View logs
sudo journalctl -u spec-kit-web.service -f
sudo journalctl -u spec-kit-mcp.service -f

# Restart
sudo systemctl restart spec-kit-web.service spec-kit-mcp.service
```

### Security Considerations

**Current (Development):**
- Web UI accessible from all interfaces
- No authentication required
- HTTP only

**Production (Recommended):**
- Restrict firewall to trusted IPs
- Add BasicAuth or OAuth
- Use HTTPS with reverse proxy
- Run with limited permissions
- Implement rate limiting
- Add audit logging

## License

MIT License

---

**Server Location**: Currently deployed at `10.10.10.24:3030`
**Last Updated**: November 30, 2025
