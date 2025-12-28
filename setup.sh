#!/usr/bin/env bash
set -euo pipefail

# Unified Installer for MCP Server + Spec-Kit Integration
# Installs both FastAPI command server and Spec-Kit web UI + MCP tools
# Run inside the target Ubuntu 24.04 LXC as root

MCP_USER=${MCP_USER:-mrmagic}
MCP_BASE=${MCP_BASE:-/opt/mcp}
VENV_DIR="$MCP_BASE/venv"
SERVER_DIR="$MCP_BASE/server"
WEB_DIR="$MCP_BASE/web"

echo "=========================================="
echo "MCP Server + Spec-Kit Unified Installer"
echo "=========================================="
echo ""

# Create user if needed
echo "▶ Creating user and directories..."
if ! id -u "$MCP_USER" >/dev/null 2>&1; then
	useradd --system --create-home --home-dir /home/$MCP_USER --shell /usr/sbin/nologin $MCP_USER || \
	useradd -m -s /bin/bash $MCP_USER || true
fi
mkdir -p "$SERVER_DIR" "$WEB_DIR"
chown -R $MCP_USER:$MCP_USER "$MCP_BASE" || true

# System dependencies
echo "▶ Installing system packages..."
apt-get update && apt-get upgrade -y
apt-get install -y \
	python3 python3-venv python3-pip python3-flask \
	git curl ca-certificates jq unzip build-essential \
	sqlite3 net-tools htop || true

# Python virtual environment
echo "▶ Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
	python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install fastapi uvicorn requests flask || true

# Install uv for spec-kit
echo "▶ Installing uv package manager..."
if ! command -v uv &> /dev/null; then
	curl -LsSf https://astral.sh/uv/install.sh | sh || true
	export PATH="$HOME/.local/bin:$PATH"
fi

# Install spec-kit
echo "▶ Installing GitHub Spec-Kit..."
export PATH="$HOME/.local/bin:$PATH"
if command -v uv &> /dev/null; then
	~/.local/bin/uv tool install specify-cli --from git+https://github.com/github/spec-kit.git || true
else
	echo "⚠ uv not available, spec-kit may need manual installation"
fi

# Copy server files
echo "▶ Installing MCP FastAPI server..."
if [ -d ./server ]; then
	cp -a ./server/* "$SERVER_DIR/" || true
	chown -R $MCP_USER:$MCP_USER "$SERVER_DIR"
fi

# Copy Spec-Kit web UI files
echo "▶ Installing Spec-Kit web UI..."
if [ -f ./server/web/app.py ]; then
	cp ./server/web/app.py "$WEB_DIR/app.py"
	chown $MCP_USER:$MCP_USER "$WEB_DIR/app.py"
fi
if [ -d ./templates ]; then
	cp -r ./templates "$MCP_BASE/"
	chown -R $MCP_USER:$MCP_USER "$MCP_BASE/templates"
fi

# Install systemd services
echo "▶ Installing systemd services..."
install -d /etc/systemd/system
if [ -f ./systemd/mcp-http.service ]; then
	cp ./systemd/mcp-http.service /etc/systemd/system/
fi
if [ -f ./systemd/spec-kit-web.service ]; then
	cp ./systemd/spec-kit-web.service /etc/systemd/system/
fi
if [ -f ./systemd/spec-kit-mcp.service ]; then
	cp ./systemd/spec-kit-mcp.service /etc/systemd/system/
fi

# Fix service paths for actual deployment
sed -i "s|/home/mrmagic/mcp-server-spec-kit|$MCP_BASE|g" /etc/systemd/system/spec-kit-*.service

# Enable services
echo "▶ Enabling systemd services..."
systemctl daemon-reload
systemctl enable mcp-http.service || true
systemctl enable spec-kit-web.service || true
systemctl enable spec-kit-mcp.service || true

# Start services
echo "▶ Starting services..."
systemctl start mcp-http.service || true
systemctl start spec-kit-web.service || true
systemctl start spec-kit-mcp.service || true

# Verify installation
echo ""
echo "=========================================="
echo "Installation Summary"
echo "=========================================="
systemctl status mcp-http.service --no-pager | grep -E "Loaded|Active" || true
systemctl status spec-kit-web.service --no-pager | grep -E "Loaded|Active" || true
echo ""
echo "Services:"
echo "  • MCP HTTP Server: http://localhost:3030/health"
echo "  • Spec-Kit Web UI: http://localhost:5000"
echo ""
echo "Next steps:"
echo "  1. Edit $SERVER_DIR/allowed_cmds.txt to customize allowed commands"
echo "  2. systemctl restart mcp-http.service spec-kit-web.service"
echo "  3. Test: curl http://localhost:3030/health"
echo "  4. Test: curl http://localhost:5000/"
echo ""
echo "✅ Setup complete!"
