#!/usr/bin/env bash
set -euo pipefail

# Installer for MCP server (run inside the target Ubuntu 24.04 LXC as root)

MCP_USER=${MCP_USER:-mcpbot}
MCP_BASE=/opt/mcp
VENV_DIR="$MCP_BASE/venv"
SERVER_DIR="$MCP_BASE/server"

echo "Creating user $MCP_USER and directories..."
if ! id -u "$MCP_USER" >/dev/null 2>&1; then
	useradd --system --create-home --home-dir /home/$MCP_USER --shell /usr/sbin/nologin $MCP_USER
fi
mkdir -p "$SERVER_DIR"
mkdir -p "$MCP_BASE"
chown -R $MCP_USER:$MCP_USER "$MCP_BASE" || true

echo "Installing packages..."
apt update && apt -y upgrade
apt install -y python3 python3-venv python3-pip git curl ca-certificates jq unzip build-essential || true

echo "Creating venv and installing Python deps..."
if [ ! -d "$VENV_DIR" ]; then
	python3 -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install fastapi uvicorn requests || true

echo "Copying server files..."
if [ -d ./server ]; then
	cp -a ./server "$MCP_BASE/" || true
	chown -R $MCP_USER:$MCP_USER "$MCP_BASE"
fi

echo "Installing systemd unit..."
install -d /etc/systemd/system
if [ -f ./systemd/mcp-http.service ]; then
	cp -a ./systemd/mcp-http.service /etc/systemd/system/mcp-http.service
	systemctl daemon-reload
	systemctl enable --now mcp-http.service || true
fi

echo "Setup complete. Service status:"
systemctl status mcp-http.service --no-pager || true

echo "Remember to edit $SERVER_DIR/allowed_cmds.txt and restart the service when ready."
