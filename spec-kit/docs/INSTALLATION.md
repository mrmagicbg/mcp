# Spec-Kit MCP Installation Guide

Complete step-by-step guide for installing and configuring Spec-Kit MCP integration.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Install](#quick-install)
3. [Detailed Installation](#detailed-installation)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### Server Requirements
- Ubuntu 20.04 or later
- Python 3.11 or later
- 100MB free disk space
- Network access to target port (5000 for web, 22 for SSH)

### Software Requirements
- uv package manager (for installing spec-kit)
- git (for cloning repo)
- sudo access (for systemd service installation)

### Network Requirements
- Port 5000 available (configurable)
- Port 22 for SSH management
- Internet access for initial uv/pip installation

## Quick Install

### 1. Clone the Repository

```bash
cd /home/mrmagic/Code/GitHub/mrmagicbg/
git clone https://github.com/mrmagicbg/mcp
cd mcp/spec-kit
```

### 2. Run Installation Script

```bash
# Copy to target server if not already there
scp -r . user@10.10.10.24:/opt/mcp/spec-kit/

# On the target server
ssh user@10.10.10.24
cd /opt/mcp/spec-kit

# Make scripts executable
chmod +x install.sh

# Run installer
sudo bash install.sh
```

### 3. Verify Installation

```bash
# Check services are running
sudo systemctl status spec-kit-web.service spec-kit-mcp.service

# Test web UI
curl http://localhost:5000/api/commands

# Test spec-kit
source ~/.local/bin/env
specify version
```

## Detailed Installation

### Step 1: Prepare System

```bash
# Update package lists
sudo apt-get update

# Install system dependencies
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl

# Optional: Install uv if not present
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.local/bin/env
fi

# Verify Python version
python3 --version  # Should be 3.11+
```

### Step 2: Install Spec-Kit

```bash
# If uv is not in PATH
export PATH="$HOME/.local/bin:$PATH"

# Install spec-kit via uv
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Verify installation
source ~/.local/bin/env
specify --version
```

### Step 3: Install Flask

```bash
# Option A: System package (recommended for system service)
sudo apt-get install -y python3-flask

# Option B: via pip
sudo pip3 install flask

# Verify
python3 -c "import flask; print(flask.__version__)"
```

### Step 4: Copy MCP Spec-Kit Files

```bash
# Create directory structure
sudo mkdir -p /opt/mcp/spec-kit/{server,web,systemd}

# Copy files
sudo cp server/server.py /opt/mcp/spec-kit/server/
sudo cp web/app.py /opt/mcp/spec-kit/web/
sudo cp -r web/templates /opt/mcp/spec-kit/web/
sudo cp systemd/*.service /etc/systemd/system/

# Set permissions
sudo chown -R mrmagic:mrmagic /opt/mcp/spec-kit
chmod +x /opt/mcp/spec-kit/server/server.py
chmod +x /opt/mcp/spec-kit/web/app.py
```

### Step 5: Update Service Files

Edit `/etc/systemd/system/spec-kit-web.service`:

```bash
sudo nano /etc/systemd/system/spec-kit-web.service
```

Ensure paths are correct:
```ini
[Service]
User=mrmagic
WorkingDirectory=/opt/mcp/spec-kit/web
ExecStart=/usr/bin/python3 /opt/mcp/spec-kit/web/app.py
Environment="PATH=/home/mrmagic/.local/bin:/usr/local/bin:/usr/bin:/bin"
```

Do the same for `/etc/systemd/system/spec-kit-mcp.service`:

```ini
[Service]
User=mrmagic
WorkingDirectory=/opt/mcp/spec-kit/server
ExecStart=/usr/bin/python3 /opt/mcp/spec-kit/server/server.py
Environment="PATH=/home/mrmagic/.local/bin:/usr/local/bin:/usr/bin:/bin"
```

### Step 6: Enable and Start Services

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable services to auto-start
sudo systemctl enable spec-kit-web.service
sudo systemctl enable spec-kit-mcp.service

# Start services
sudo systemctl start spec-kit-web.service
sudo systemctl start spec-kit-mcp.service

# Verify they're running
sudo systemctl status spec-kit-web.service spec-kit-mcp.service
```

### Step 7: Configure Firewall (If Enabled)

```bash
# Allow port 5000 from trusted networks
sudo ufw allow from 10.10.10.0/24 to any port 5000

# Allow SSH if needed
sudo ufw allow from 10.10.10.0/24 to any port 22

# Verify rules
sudo ufw status
```

### Step 8: Test Installation

```bash
# Test web API
curl http://localhost:5000/api/commands | python3 -m json.tool

# Test version command
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"command": "version", "args": []}'

# Test MCP server (manually with input)
echo '{"type": "initialize"}' | python3 /opt/mcp/spec-kit/server/server.py
```

## Verification

### Service Status Check

```bash
# Check both services
sudo systemctl status spec-kit-web.service spec-kit-mcp.service

# Expected output should show "active (running)"
```

### Port Verification

```bash
# Check web UI port
sudo ss -tlnp | grep 5000

# Expected: LISTEN 0.0.0.0:5000

# Check SSH port
sudo ss -tlnp | grep 22

# Expected: LISTEN 0.0.0.0:22
```

### Web UI Accessibility

```bash
# From the server
curl -I http://localhost:5000/

# Expected: HTTP/1.1 200 OK

# From another machine (if accessible)
curl -I http://10.10.10.24:5000/

# Expected: HTTP/1.1 200 OK
```

### Spec-Kit Functionality

```bash
# Test version command
source ~/.local/bin/env
specify version

# Expected: Shows CLI version, template version, Python version, etc.

# Test check command
specify check

# Expected: Shows status of required tools

# Test init command
specify init /tmp/test-project

# Expected: Creates new project directory with Specify template
```

### API Endpoints

```bash
# Get available commands
curl http://localhost:5000/api/commands | python3 -m json.tool

# Run a command
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"command": "check", "args": []}'

# Get history
curl http://localhost:5000/api/history | python3 -m json.tool
```

## Troubleshooting

### Service Won't Start

**Check service status:**
```bash
sudo systemctl status spec-kit-web.service
```

**View detailed logs:**
```bash
sudo journalctl -u spec-kit-web.service -n 50
```

**Common causes:**
- Port already in use: `sudo lsof -i :5000`
- Python not found: Verify `python3 --version`
- Flask not installed: `python3 -c "import flask"`
- Working directory missing: `ls -la /opt/mcp/spec-kit/`

### Web UI Not Responding

```bash
# Check if service is running
sudo systemctl is-active spec-kit-web.service

# Check port is listening
sudo ss -tlnp | grep 5000

# Test with localhost
curl http://127.0.0.1:5000/

# If still failing, restart
sudo systemctl restart spec-kit-web.service
```

### Commands Not Executing

```bash
# Verify spec-kit installed
which specify

# Check uv environment
source ~/.local/bin/env
specify --version

# Test command directly
specify version

# Check web service logs for errors
sudo journalctl -u spec-kit-web.service -p err -f
```

### Permission Denied

```bash
# Check file ownership
ls -la /opt/mcp/spec-kit/

# Should be owned by mrmagic:mrmagic

# Fix permissions if needed
sudo chown -R mrmagic:mrmagic /opt/mcp/spec-kit
chmod +x /opt/mcp/spec-kit/server/server.py
chmod +x /opt/mcp/spec-kit/web/app.py
```

### Port Already in Use

```bash
# Find what's using port 5000
sudo lsof -i :5000

# Option 1: Kill the process
sudo kill -9 <PID>

# Option 2: Change the port in app.py
# Edit: app.run(host='0.0.0.0', port=5000)
# Change to: app.run(host='0.0.0.0', port=5001)
# Then restart: sudo systemctl restart spec-kit-web.service
```

### Python Module Not Found

```bash
# Install Flask if missing
sudo apt-get install -y python3-flask

# Or via pip
sudo pip3 install flask

# Verify installation
python3 -c "import flask; print(flask.__version__)"

# Restart services
sudo systemctl restart spec-kit-web.service spec-kit-mcp.service
```

### uv Not Found

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Make permanent (add to ~/.bashrc)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Install spec-kit
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

## Post-Installation

### Configuration Options

**Change web UI port:**
- Edit: `/opt/mcp/spec-kit/web/app.py`
- Line: `app.run(host='0.0.0.0', port=5000)`
- Restart: `sudo systemctl restart spec-kit-web.service`

**Change command timeout:**
- Edit: `/opt/mcp/spec-kit/web/app.py` or `/opt/mcp/spec-kit/server/server.py`
- Find: `timeout=60`
- Change to desired seconds
- Restart services

**Add firewall rules:**
```bash
sudo ufw allow from 10.10.10.0/24 to any port 5000
sudo ufw allow from 10.10.10.0/24 to any port 22
```

### Backup Configuration

```bash
# Backup service files
sudo cp /etc/systemd/system/spec-kit-*.service /opt/mcp/spec-kit/systemd/

# Backup application files
sudo tar -czf /opt/mcp/spec-kit-backup-$(date +%Y%m%d).tar.gz \
  /opt/mcp/spec-kit \
  /etc/systemd/system/spec-kit-*.service
```

### Monitoring

```bash
# Real-time service logs
sudo journalctl -u spec-kit-web.service -u spec-kit-mcp.service -f

# Check service health
sudo systemctl status spec-kit-web.service spec-kit-mcp.service

# Monitor disk usage
df -h /opt/mcp/

# Monitor memory
free -h

# Monitor processes
ps aux | grep specify
ps aux | grep python3
```

## Next Steps

1. Access web UI: http://10.10.10.24:5000
2. Try running commands in the browser
3. Test MCP server integration with your tools
4. Configure firewall rules for production
5. Add authentication for security
6. Set up monitoring and alerts
7. Create deployment scripts for future updates

## Support

For additional help:
1. Check `/opt/mcp/spec-kit/README.md`
2. Review service logs: `sudo journalctl -u spec-kit-*`
3. Test spec-kit directly: `specify --help`
4. Check GitHub issues: https://github.com/github/spec-kit/issues
