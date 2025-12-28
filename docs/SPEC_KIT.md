# Spec-Kit MCP Integration

GitHub Spec-Kit (spec-driven development toolkit) integrated with Model Context Protocol for easy access via two interfaces: Web UI and MCP tools.

## Overview

This module provides:

1. **MCP Server** - Exposes spec-kit commands as Model Context Protocol tools (stdio transport)
2. **Web UI** - Browser-based interface for command execution and output viewing
3. **systemd Services** - Auto-start services for production deployment

### Components

```
server/
├── spec_kit_server.py        # stdio-based MCP protocol handler
├── web/                      # Flask web application
│   └── app.py                # Flask application and API endpoints
templates/
└── index.html                # Rich web UI (HTML/CSS/JS)
systemd/
├── spec-kit-mcp.service      # MCP server service (placeholder)
└── spec-kit-web.service      # Web UI service
```

## Quick Start

### Prerequisites

- Python 3.11+
- uv package manager
- GitHub Spec-Kit installed

### Installation

#### Automated (Recommended)

```bash
./setup.sh  # Unified installer (run on target as root)
```

#### Manual

1. **Copy files:**
   ```bash
  sudo cp server/spec_kit_server.py /opt/mcp/server/
  sudo cp server/web/app.py /opt/mcp/server/web/
  sudo cp -r templates /opt/mcp/
  sudo cp systemd/*.service /etc/systemd/system/
   ```

2. **Install dependencies:**
   ```bash
   # System packages
   sudo apt-get update
   sudo apt-get install -y python3-flask

   # Or use uv if available
   uv pip install flask
   ```

3. **Enable services:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable spec-kit-mcp.service spec-kit-web.service
   sudo systemctl start spec-kit-mcp.service spec-kit-web.service
   ```

## Usage

### Web UI

**Access:** `http://your-server:5000`

Features:
- Command selection dropdown
- Optional argument input
- Real-time output display
- Copy to clipboard
- Command history (last 20)
- Status indicators

Available commands:
- `check` - Verify required tools are installed
- `version` - Display Spec-Kit version and system info
- `init` - Initialize new Specify project (with optional path)

### MCP Server

**Path:** `/opt/mcp/server/spec_kit_server.py`

Exposed Tools:

#### `specify_init`
Initialize a new Specify project from template.

**Input Schema:**
```json
{
  "path": "string (optional)"
}
```

**Example Request:**
```json
{
  "type": "tools/call",
  "name": "specify_init",
  "arguments": { "path": "/tmp/my-project" }
}
```

#### `specify_check`
Check that all required tools are installed.

**Input Schema:**
```json
{}
```

#### `specify_version`
Display version and system information.

**Input Schema:**
```json
{}
```

#### `specify_run_command`
Run a raw specify command with custom arguments.

**Input Schema:**
```json
{
  "command": "string (required)",
  "args": ["string"]
}
```

**Example Request:**
```json
{
  "type": "tools/call",
  "name": "specify_run_command",
  "arguments": {
    "command": "version",
    "args": []
  }
}
```

### Direct SSH

```bash
# Connect
ssh user@your-server

# Source uv environment
source ~/.local/bin/env

# Run commands
specify version
specify check
specify init /path/to/project
```

## Services

### spec-kit-mcp.service

- **Type:** Simple (stdio transport)
- **User:** mrmagic
- **Working Dir:** `/opt/mcp`
- **Command:** `/opt/mcp/venv/bin/python /opt/mcp/server/spec_kit_server.py`
- **Auto-restart:** On failure with 10s delay
- **Auto-start:** Yes (enabled)

### spec-kit-web.service

- **Type:** Simple (HTTP server)
- **User:** mrmagic
- **Working Dir:** `/opt/mcp`
- **Port:** 5000
- **Command:** `/opt/mcp/venv/bin/python /opt/mcp/server/web/app.py`
- **Auto-restart:** On failure with 10s delay
- **Auto-start:** Yes (enabled)

## Management

### Status

```bash
# Check both services
sudo systemctl status spec-kit-mcp.service spec-kit-web.service

# Check specific service
sudo systemctl status spec-kit-web.service
```

### View Logs

```bash
# Web UI logs
sudo journalctl -u spec-kit-web.service -f

# MCP server logs
sudo journalctl -u spec-kit-mcp.service -f

# Combined logs
sudo journalctl -u spec-kit-web.service -u spec-kit-mcp.service -f
```

### Restart Services

```bash
# Restart web UI only
sudo systemctl restart spec-kit-web.service

# Restart MCP server only
sudo systemctl restart spec-kit-mcp.service

# Restart both
sudo systemctl restart spec-kit-web.service spec-kit-mcp.service
```

### Stop/Start

```bash
# Stop
sudo systemctl stop spec-kit-web.service spec-kit-mcp.service

# Start
sudo systemctl start spec-kit-web.service spec-kit-mcp.service
```

## Configuration

### Web UI Port

Edit `/opt/mcp/spec-kit/web/app.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Change port here
```

Then restart:
```bash
sudo systemctl restart spec-kit-web.service
```

### Command Timeout

Edit `/opt/mcp/spec-kit/server/server.py` or `/opt/mcp/spec-kit/web/app.py`:

```python
# Find: timeout=60
# Change to desired seconds
result = subprocess.run(
    cmd,
    shell=True,
    executable="/bin/bash",
    capture_output=True,
    text=True,
    timeout=60  # Change this
)
```

### Add Custom Commands

In the server or web app, add to the tools dictionary:

```python
self.tools["my_command"] = {
    "description": "Description of my command",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        }
    }
}
```

## Troubleshooting

### Web UI Not Responding

```bash
# Check service
sudo systemctl status spec-kit-web.service

# View recent logs
sudo journalctl -u spec-kit-web.service -n 20

# Check port is listening
sudo ss -tlnp | grep 5000

# Restart
sudo systemctl restart spec-kit-web.service
```

### Commands Not Executing

```bash
# Verify spec-kit is installed
which specify

# Check Python environment
python3 --version

# Test command directly
source ~/.local/bin/env && specify version

# View web service error logs
sudo journalctl -u spec-kit-web.service -p err
```

### Port Already in Use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process if needed
sudo kill -9 <PID>

# Or change the port in app.py
```

## Security

### Development Setup (Current)
- Web UI accessible from all interfaces
- No authentication required
- Commands run with user privileges
- HTTP only (no encryption)

### Production Hardening

1. **Firewall:**
   ```bash
   sudo ufw allow from 10.10.10.0/24 to any port 5000
   sudo ufw allow from 10.10.10.0/24 to any port 22
   ```

2. **Authentication:**
   - Add Flask BasicAuth or OAuth
   - Require API tokens for MCP calls

3. **HTTPS:**
   - Use Gunicorn with SSL certificates
   - Reverse proxy with nginx/apache

4. **Permissions:**
   - Run services with restricted user
   - Use sudo for elevated operations only

5. **Audit:**
   - Log all command executions
   - Implement rate limiting
   - Add alerting for failed attempts

## API Reference

### Web UI Endpoints

#### GET `/`
Serve main web interface.

**Response:** HTML (200 OK)

#### GET `/api/commands`
List available spec-kit commands.

**Response:**
```json
{
  "commands": [
    {
      "name": "check",
      "description": "Check that all required tools are installed",
      "args": []
    }
  ]
}
```

#### POST `/api/process`
Execute a spec-kit command.

**Request Body:**
```json
{
  "command": "version",
  "args": []
}
```

**Response:**
```json
{
  "success": true,
  "stdout": "...output...",
  "stderr": "",
  "returncode": 0
}
```

#### GET `/api/history`
Get recent command history (last 20).

**Response:**
```json
{
  "history": [
    {
      "timestamp": "2025-12-28T19:08:57",
      "command": "version",
      "args": [],
      "result": { ... }
    }
  ]
}
```

#### GET `/api/history/<index>`
Get specific history item by index.

#### POST `/api/clear-history`
Clear all command history.

**Response:**
```json
{
  "success": true,
  "message": "History cleared"
}
```

## Performance

- Web UI response time: 100-500ms per command
- Command execution timeout: 60 seconds (configurable)
- Memory per service: ~25MB
- CPU usage idle: < 1%
- CPU usage executing: ~2-5%

## Files

| File | Purpose |
|------|---------|
| `server/server.py` | MCP protocol implementation |
| `web/app.py` | Flask web server |
| `web/templates/index.html` | Web UI (HTML/CSS/JS) |
| `systemd/spec-kit-mcp.service` | MCP systemd service |
| `systemd/spec-kit-web.service` | Web systemd service |
| `docs/INSTALLATION.md` | Detailed installation |
| `docs/DEPLOYMENT.md` | Deployment guide |
| `README.md` | This file |

## Related Documentation

- [Spec-Kit GitHub](https://github.com/github/spec-kit)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [systemd Documentation](https://systemd.io/)

## License

Same as parent MCP repo.

## Support

For issues or questions:
1. Check logs: `sudo journalctl -u spec-kit-*`
2. Test commands directly: `specify --help`
3. Review configuration files
4. Check network connectivity
