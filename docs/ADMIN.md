# Admin Guide

This guide covers day-to-day operations for the unified MCP + Spec-Kit deployment.

## Overview

- MCP API (FastAPI): http://<server>:3030
- Spec-Kit Web UI (Flask): http://<server>:5000
- Base directory: /opt/mcp
- Services: `mcp-http.service`, `spec-kit-web.service`, `spec-kit-mcp.service`

## Quick Commands

### Check Status
```bash
sudo systemctl status mcp-http.service spec-kit-web.service
curl -s http://localhost:3030/health | jq .
curl -s http://localhost:5000/health | jq .
```

### Restart Services
```bash
sudo systemctl restart mcp-http.service
sudo systemctl restart spec-kit-web.service
```

### Logs
```bash
sudo journalctl -u mcp-http.service -f
sudo journalctl -u spec-kit-web.service -f
```

### Firewall
```bash
sudo ufw allow 3030/tcp
sudo ufw allow 5000/tcp
sudo ufw status
```

### Deployment
```bash
# From local repo
./deploy.sh
# Prompts: SSH user (default mrmagic), IP (default 10.10.10.24)
```

### Configuration
- Command allowlist: `/opt/mcp/server/allowed_cmds.txt`
- Templates folder: `/opt/mcp/templates` (used by web UI)

## Backups
```bash
sudo tar -czf /opt/mcp-backup-$(date +%F).tar.gz \
  /opt/mcp/server /opt/mcp/templates /etc/systemd/system/mcp-http.service \
  /etc/systemd/system/spec-kit-web.service /etc/systemd/system/spec-kit-mcp.service
```

## Troubleshooting
- Web UI 500 error on `/`: ensure `/opt/mcp/templates/index.html` exists.
- Port conflict on 5000: kill any stray Python process listening.
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
```
- MCP API `DENIED`: add the command string (or prefix) to `allowed_cmds.txt`.

## Health Endpoints
- MCP API: `GET /health` → `{"status":"ok","server":"linuxOps"}`
- Web UI: `GET /health` → `{"status":"ok","service":"spec-kit-web"}`

## Security Notes
- Restrict UFW to LAN if desired: `sudo ufw allow from 10.10.10.0/24 to any port 5000`
- Consider reverse proxy + TLS for internet exposure.

