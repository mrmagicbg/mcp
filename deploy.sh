#!/bin/bash
# MCP Server Deployment Script
# Run this on the MCP server (10.10.10.24) to update the MCP server itself

set -euo pipefail

# Configuration
REPO_URL="https://github.com/mrmagicbg/mcp.git"
REPO_DIR="$HOME/mcp-deploy"
MCP_BASE="/opt/mcp"
SERVICE_NAME="mcp-http.service"

echo "🚀 Starting MCP Server deployment..."

# Ensure REPO_DIR exists
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

# Cleanup function
cleanup() {
    # Do not remove if REPO_DIR is under $HOME and developer may want it
    if [[ "$REPO_DIR" == "$HOME"* ]]; then
        echo "Leaving $REPO_DIR in place"
    else
        rm -rf "$REPO_DIR" || true
    fi
}
trap cleanup EXIT

echo "📥 Cloning/updating repository..."
if command -v git >/dev/null 2>&1; then
    if [ -d ".git" ]; then
        git fetch --all --prune
        git reset --hard origin/main
    else
        git clone "$REPO_URL" .
    fi
else
    echo "git not installed; attempting wget/unzip fallback"
    wget -q "$REPO_URL/archive/main.zip" -O main.zip
    unzip -q main.zip
    cd mcp-main || cd mcp-* || true
fi

echo "📋 Ensuring required packages are installed..."
apt update || true
apt install -y python3 python3-venv python3-pip git curl unzip || true

# Ensure MCP base exists
mkdir -p "$MCP_BASE"
chown -R $(whoami):$(whoami) "$MCP_BASE" || true

echo "🔧 Updating server files..."
# Backup current server files
if [ -d "$MCP_BASE/server" ]; then
    backup="$MCP_BASE/server.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backing up existing server to $backup"
    cp -a "$MCP_BASE/server" "$backup"
fi

# Copy new server files
if [ -d server ]; then
    rsync -a --delete server/ "$MCP_BASE/server/"
    chown -R mcpbot:mcpbot "$MCP_BASE/server" || true
else
    echo "Warning: server/ directory not found in repository"
fi

echo "🔄 Restarting MCP service..."
systemctl daemon-reload || true
systemctl restart "$SERVICE_NAME" || true

echo "⏳ Waiting for service to start..."
sleep 3

# Test the service
echo "🧪 Testing deployment..."
if curl -s http://localhost:3030/health | grep -q '"status": "ok"'; then
    echo "✅ Deployment successful!"
    echo "📊 Service status:"
    systemctl status "$SERVICE_NAME" --no-pager -l | head -10 || true
else
    echo "❌ Deployment failed - service not responding"
    echo "📋 Checking service logs:"
    journalctl -u "$SERVICE_NAME" -n 30 --no-pager || true
    exit 1
fi

echo "🎉 MCP Server deployment complete!"
echo "🌐 Server available at: http://10.10.10.24:3030"