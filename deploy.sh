#!/bin/bash
# MCP Server Deployment Script
# Run this on the MCP server (10.10.10.24) to update the MCP server itself

set -euo pipefail

# Configuration
REPO_URL="https://github.com/mrmagicbg/mcp.git"
REPO_DIR="/tmp/mcp-deploy"
MCP_BASE="/opt/mcp"
SERVICE_NAME="mcp-http.service"

echo "🚀 Starting MCP Server deployment..."

# Create temp directory
rm -rf "$REPO_DIR"
mkdir -p "$REPO_DIR"
cd "$REPO_DIR"

echo "📥 Cloning/updating repository..."
if [ -d ".git" ]; then
    git pull origin main
else
    git clone "$REPO_URL" .
fi

echo "📋 Checking for required packages..."
# Install any missing dependencies
apt update
apt install -y python3 python3-venv python3-pip git curl || true

echo "🔧 Updating server files..."
# Backup current server files
if [ -d "$MCP_BASE/server" ]; then
    cp -r "$MCP_BASE/server" "$MCP_BASE/server.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy new server files
cp -r server/* "$MCP_BASE/server/"
chown -R mcpbot:mcpbot "$MCP_BASE/server"

echo "🔄 Restarting MCP service..."
systemctl daemon-reload
systemctl restart "$SERVICE_NAME"

echo "⏳ Waiting for service to start..."
sleep 3

# Test the service
echo "🧪 Testing deployment..."
if curl -s http://localhost:3030/health | grep -q '"status": "ok"'; then
    echo "✅ Deployment successful!"
    echo "📊 Service status:"
    systemctl status "$SERVICE_NAME" --no-pager -l | head -10
else
    echo "❌ Deployment failed - service not responding"
    echo "📋 Checking service logs:"
    journalctl -u "$SERVICE_NAME" -n 20 --no-pager
    exit 1
fi

echo "🧹 Cleaning up..."
cd /
rm -rf "$REPO_DIR"

echo "🎉 MCP Server deployment complete!"
echo "🌐 Server available at: http://10.10.10.24:3030"