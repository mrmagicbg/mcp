#!/usr/bin/env bash
set -euo pipefail

# Unified Deployer for MCP + Spec-Kit
# Syncs latest code and restarts both services
# Usage: ./deploy.sh [target_ip] or run on target as root

TARGET="${1:-10.10.10.24}"
REPO_URL="https://github.com/mrmagicbg/mcp.git"
REPO_DIR="/tmp/mcp-deploy-$$"
MCP_BASE="/opt/mcp"

echo "=========================================="
echo "MCP + Spec-Kit Unified Deployment"
echo "=========================================="
echo "Target: $TARGET"
echo ""

# Cleanup function
cleanup() {
	rm -rf "$REPO_DIR" 2>/dev/null || true
}
trap cleanup EXIT

# SSH helper
ssh_cmd() {
	ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "root@$TARGET" "$@" 2>/dev/null || return 1
}

# Deploy via SSH to remote target
deploy_remote() {
	echo "▶ Connecting to $TARGET..."
	
	if ! ssh_cmd "echo OK" >/dev/null 2>&1; then
		echo "❌ Cannot reach $TARGET via SSH"
		return 1
	fi
	
	echo "▶ Cloning repository on target..."
	ssh_cmd "rm -rf $REPO_DIR && mkdir -p $REPO_DIR && cd $REPO_DIR && git clone $REPO_URL ."
	
	echo "▶ Creating MCP directories..."
	ssh_cmd "mkdir -p $MCP_BASE/server $MCP_BASE/web $MCP_BASE/templates"
	
	echo "▶ Syncing code files..."
	ssh_cmd "cd $REPO_DIR && cp -a server/*.py $MCP_BASE/server/ 2>/dev/null || true"
	ssh_cmd "cd $REPO_DIR && cp -a server/web/* $MCP_BASE/server/web/ 2>/dev/null || true"
	ssh_cmd "cd $REPO_DIR && cp -a templates/* $MCP_BASE/templates/ 2>/dev/null || true"
	
	echo "▶ Installing Python dependencies..."
	if [ -f requirements.txt ]; then
		ssh_cmd "cd $REPO_DIR && [ -d $MCP_BASE/venv ] && $MCP_BASE/venv/bin/pip install -r requirements.txt || true"
	fi
	
	echo "▶ Updating systemd services..."
	ssh_cmd "cd $REPO_DIR && cp -a systemd/*.service /etc/systemd/system/ 2>/dev/null || true"
	
	echo "▶ Fixing service paths..."
	ssh_cmd "sed -i 's|/home/mrmagic|$MCP_BASE|g' /etc/systemd/system/spec-kit-*.service 2>/dev/null || true"
	
	echo "▶ Reloading systemd and restarting services..."
	ssh_cmd "systemctl daemon-reload"
	ssh_cmd "systemctl restart mcp-http.service" || echo "⚠ mcp-http.service had issues"
	ssh_cmd "systemctl restart spec-kit-web.service" || echo "⚠ spec-kit-web.service had issues"
	ssh_cmd "systemctl restart spec-kit-mcp.service" || echo "⚠ spec-kit-mcp.service had issues"
	
	echo "▶ Cleaning up remote temp files..."
	ssh_cmd "rm -rf $REPO_DIR" || true
}

# Deploy locally on this system
deploy_local() {
	echo "▶ Deploying on local system..."
	
	echo "▶ Cloning repository..."
	mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	git clone "$REPO_URL" . 2>&1 | grep -v "^Cloning\|^Receiving\|^Unpacking" || true
	
	echo "▶ Creating directories..."
	mkdir -p "$MCP_BASE/server" "$MCP_BASE/web" "$MCP_BASE/templates"
	
	echo "▶ Copying files..."
	cp -a server/*.py "$MCP_BASE/server/" 2>/dev/null || true
	cp -a server/web/* "$MCP_BASE/server/web/" 2>/dev/null || true
	cp -a templates/* "$MCP_BASE/templates/" 2>/dev/null || true
	
	echo "▶ Installing Python dependencies..."
	if [ -f requirements.txt ] && [ -d "$MCP_BASE/venv" ]; then
		"$MCP_BASE/venv/bin/pip" install -r requirements.txt -q || true
	fi
	
	echo "▶ Updating systemd services..."
	cp -a systemd/*.service /etc/systemd/system/ 2>/dev/null || true
	
	echo "▶ Reloading systemd and restarting services..."
	systemctl daemon-reload
	systemctl restart mcp-http.service || echo "⚠ mcp-http.service had issues"
	systemctl restart spec-kit-web.service || echo "⚠ spec-kit-web.service had issues"
	systemctl restart spec-kit-mcp.service || echo "⚠ spec-kit-mcp.service had issues"
}

# Determine deployment mode
if [ "$TARGET" = "localhost" ] || [ "$TARGET" = "127.0.0.1" ] || [ "$(hostname -I | awk '{print $1}')" = "$TARGET" ]; then
	deploy_local
else
	deploy_remote || exit 1
fi

# Wait for services
sleep 2

echo ""
echo "=========================================="
echo "Deployment Verification"
echo "=========================================="
echo ""

# Status check
if [ "$TARGET" = "localhost" ] || [ "$TARGET" = "127.0.0.1" ]; then
	echo "Service Status (local):"
	systemctl status mcp-http.service --no-pager 2>&1 | grep -E "Loaded|Active" || true
	systemctl status spec-kit-web.service --no-pager 2>&1 | grep -E "Loaded|Active" || true
	echo ""
	echo "Testing endpoints (local)..."
	timeout 3 curl -s "http://localhost:3030/health" | jq . 2>/dev/null || echo "⚠ MCP HTTP not responding"
	timeout 3 curl -s "http://localhost:5000/" | head -5 2>/dev/null || echo "⚠ Spec-Kit web not responding"
else
	echo "Service Status ($TARGET):"
	ssh_cmd "systemctl status mcp-http.service --no-pager 2>&1 | grep -E 'Loaded|Active'" || echo "⚠ Status check failed"
	echo ""
	echo "Testing endpoints ($TARGET)..."
	timeout 5 curl -s "http://$TARGET:3030/health" | jq . 2>/dev/null || echo "⚠ MCP HTTP not responding"
	timeout 5 curl -s -I "http://$TARGET:5000/" 2>/dev/null | head -1 || echo "⚠ Spec-Kit web not responding"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Access points:"
if [ "$TARGET" != "localhost" ] && [ "$TARGET" != "127.0.0.1" ]; then
	echo "  • MCP API: http://$TARGET:3030"
	echo "  • Spec-Kit Web: http://$TARGET:5000"
else
	echo "  • MCP API: http://localhost:3030"
	echo "  • Spec-Kit Web: http://localhost:5000"
fi