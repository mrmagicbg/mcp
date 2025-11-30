#!/usr/bin/env bash
set -euo pipefail

# Installer for MCP server (run inside the target Ubuntu 24.04 LXC as root)

MCP_USER=${MCP_USER:-mcpbot}
MCP_BASE=/opt/mcp
VENV_DIR="$MCP_BASE/venv"
SERVER_DIR="$MCP_BASE/server"

echo "Creating user $MCP_USER and directories..."
id -u "$MCP_USER" >/dev/null 2>&1 || useradd --system --create-home --home-dir /home/$MCP_USER --shell /usr/sbin/nologin $MCP_USER
mkdir -p "$SERVER_DIR"
chown -R $MCP_USER:$MCP_USER "$MCP_BASE"

echo "Installing packages..."
apt update && apt -y full-upgrade
apt install -y python3 python3-venv python3-pip git curl ca-certificates jq unzip build-essential

echo "Creating venv and installing Python deps..."
python3 -m venv "$VENV_DIR"
 "$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install fastapi uvicorn

echo "Copying server files..."
cp -a ./server "$MCP_BASE/" || true
chown -R $MCP_USER:$MCP_USER "$MCP_BASE"

echo "Installing systemd unit..."
install -d /etc/systemd/system
cp -a ./systemd/mcp-http.service /etc/systemd/system/mcp-http.service
systemctl daemon-reload
systemctl enable --now mcp-http.service

echo "Setup complete. Service status:"
systemctl status mcp-http.service --no-pager || true

echo "Remember to edit $SERVER_DIR/allowed_cmds.txt and restart the service when ready."
