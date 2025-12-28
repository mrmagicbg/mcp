# Spec-Kit MCP Deployment Guide

Guide for deploying Spec-Kit MCP to production on Proxmox LXC containers.

## Overview

This guide covers:
- Initial deployment from GitHub
- Service configuration and startup
- Health checks and verification
- Monitoring and maintenance
- Upgrades and rollback procedures

## Pre-Deployment Checklist

- [ ] Target server has Ubuntu 20.04+ installed
- [ ] Python 3.11+ available
- [ ] SSH key-based access configured
- [ ] Firewall rules planned
- [ ] Backup strategy in place
- [ ] Monitoring tools ready
- [ ] Documentation reviewed

## Deployment Steps

### Phase 1: Preparation

#### 1.1 Verify SSH Access

```bash
# From local machine
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 "whoami && uname -a"

# Expected output: mrmagic and Linux version
```

#### 1.2 Check System Requirements

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
echo "=== System Check ==="
echo "Python: $(python3 --version)"
echo "Disk: $(df -h / | tail -1)"
echo "Memory: $(free -h | grep Mem)"
echo "Uptime: $(uptime -p)"
EOF
```

#### 1.3 Create Deployment Directory

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
sudo mkdir -p /opt/mcp/spec-kit/{server,web,systemd}
sudo chown -R mrmagic:mrmagic /opt/mcp
ls -la /opt/mcp/
EOF
```

### Phase 2: Clone and Deploy Repository

#### 2.1 Clone MCP Repository

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
cd /opt/mcp
git clone https://github.com/mrmagicbg/mcp .
git log --oneline -5
EOF
```

#### 2.2 Verify Repository Contents

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
ls -la /opt/mcp/spec-kit/
ls -la /opt/mcp/spec-kit/{server,web,systemd}/
EOF
```

#### 2.3 Install Spec-Kit

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
# Install uv if needed
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Install spec-kit
~/.local/bin/uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Verify
source ~/.local/bin/env
specify --version
EOF
```

#### 2.4 Install System Dependencies

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
sudo apt-get update
sudo apt-get install -y python3-flask
python3 -c "import flask; print('Flask installed')"
EOF
```

### Phase 3: Install Services

#### 3.1 Copy Service Files

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
sudo cp /opt/mcp/spec-kit/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
ls -la /etc/systemd/system/spec-kit-*.service
EOF
```

#### 3.2 Make Scripts Executable

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
chmod +x /opt/mcp/spec-kit/server/server.py
chmod +x /opt/mcp/spec-kit/web/app.py
ls -la /opt/mcp/spec-kit/{server,web}/{server.py,app.py}
EOF
```

#### 3.3 Enable and Start Services

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
# Enable services to auto-start
sudo systemctl enable spec-kit-web.service
sudo systemctl enable spec-kit-mcp.service

# Start services
sudo systemctl start spec-kit-web.service
sudo systemctl start spec-kit-mcp.service

# Check status
sudo systemctl status spec-kit-web.service spec-kit-mcp.service --no-pager
EOF
```

### Phase 4: Verification

#### 4.1 Service Health Check

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
echo "=== Service Status ==="
sudo systemctl is-active spec-kit-web.service
sudo systemctl is-active spec-kit-mcp.service

echo "=== Port Check ==="
sudo ss -tlnp | grep -E '5000|22'

echo "=== Process Check ==="
ps aux | grep -E 'app.py|server.py' | grep -v grep
EOF
```

#### 4.2 API Functionality Test

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
echo "=== API Commands Test ==="
curl -s http://localhost:5000/api/commands | python3 -m json.tool | head -20

echo "=== API Version Test ==="
curl -s -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"command": "version", "args": []}' | python3 -m json.tool | head -10
EOF
```

#### 4.3 Direct Spec-Kit Test

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
source ~/.local/bin/env
echo "=== Spec-Kit Version ==="
specify version 2>&1 | grep -E "CLI Version|Python"

echo "=== Spec-Kit Check ==="
specify check 2>&1 | head -5
EOF
```

## Post-Deployment Configuration

### Firewall Rules (UFW)

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
# Allow web UI from trusted network
sudo ufw allow from 10.10.10.0/24 to any port 5000

# Allow SSH from trusted network
sudo ufw allow from 10.10.10.0/24 to any port 22

# Verify rules
sudo ufw status

# Enable firewall if not already
sudo ufw enable
EOF
```

### Logging Configuration

```bash
ssh -i _.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
# View real-time logs
sudo journalctl -u spec-kit-web.service -u spec-kit-mcp.service -f

# Set retention (e.g., 30 days)
sudo journalctl --vacuum-time=30d

# Check log size
sudo journalctl -b --disk-usage
EOF
```

### Performance Tuning

For production systems with high load:

**Increase command timeout (web/app.py):**
```python
timeout=120  # Increase from 60 seconds
```

**Run behind reverse proxy (nginx):**
```nginx
upstream spec-kit {
    server 127.0.0.1:5000;
}

server {
    listen 443 ssl http2;
    server_name spec-kit.example.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    location / {
        proxy_pass http://spec-kit;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Maintenance

### Daily Checks

```bash
# Script: /opt/mcp/check-health.sh
#!/bin/bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
echo "$(date): Health Check"

# Service status
sudo systemctl is-active spec-kit-web.service > /tmp/web.status
sudo systemctl is-active spec-kit-mcp.service > /tmp/mcp.status

# Web API test
curl -s -f http://localhost:5000/api/commands > /dev/null && echo "Web OK" || echo "Web FAIL"

# Command test
source ~/.local/bin/env
specify version > /dev/null 2>&1 && echo "Spec-Kit OK" || echo "Spec-Kit FAIL"

# Disk space
df -h / | awk '{print $5}' | grep -E '^[789]|^[0-9]{2,3}%' && echo "Disk WARNING" || echo "Disk OK"
EOF
```

### Weekly Tasks

1. Review logs for errors
   ```bash
   sudo journalctl -u spec-kit-web.service -u spec-kit-mcp.service --since "7 days ago" | grep -i error
   ```

2. Check disk usage
   ```bash
   du -sh /opt/mcp
   du -sh /home/mrmagic/.local
   ```

3. Verify backups
   ```bash
   ls -la /opt/backup/
   ```

4. Test recovery procedure
   ```bash
   # Practice restore from backup
   ```

### Monthly Tasks

1. Update system packages
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. Rotate logs
   ```bash
   sudo journalctl --vacuum-time=30d
   ```

3. Review and update documentation

4. Performance analysis and optimization

## Upgrading Spec-Kit

### Update Repository

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
cd /opt/mcp
git fetch origin
git log --oneline -5 origin/main
git pull origin main
EOF
```

### Update Spec-Kit CLI

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
export PATH="$HOME/.local/bin:$PATH"
~/.local/bin/uv tool upgrade specify-cli
source ~/.local/bin/env
specify version
EOF
```

### Reload Services

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
sudo systemctl daemon-reload
sudo systemctl restart spec-kit-web.service spec-kit-mcp.service
sudo systemctl status spec-kit-web.service spec-kit-mcp.service
EOF
```

## Rollback Procedure

### Backup Current Version

```bash
ssh -i ~/.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
sudo tar -czf /opt/backup/spec-kit-current-$(date +%Y%m%d-%H%M%S).tar.gz \
  /opt/mcp/spec-kit \
  /etc/systemd/system/spec-kit-*.service
EOF
```

### Revert to Previous Commit

```bash
ssh -i _.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
cd /opt/mcp
git log --oneline -10
git revert HEAD  # Or specific commit
git push origin main
git pull
EOF
```

### Restart Services

```bash
ssh -i _.ssh/id_ed25519_mrmagicbg mrmagic@10.10.10.24 << 'EOF'
sudo systemctl restart spec-kit-web.service spec-kit-mcp.service
sudo systemctl status spec-kit-web.service spec-kit-mcp.service
EOF
```

## Disaster Recovery

### Complete System Restore

```bash
# 1. Stop services
sudo systemctl stop spec-kit-web.service spec-kit-mcp.service

# 2. Restore from backup
sudo tar -xzf /opt/backup/spec-kit-backup-2025-12-28.tar.gz -C /

# 3. Reinstall dependencies if needed
sudo apt-get install -y python3-flask

# 4. Restart services
sudo systemctl daemon-reload
sudo systemctl start spec-kit-web.service spec-kit-mcp.service

# 5. Verify
sudo systemctl status spec-kit-web.service spec-kit-mcp.service
curl http://localhost:5000/api/commands
```

## Summary

Deployment checklist:
- [ ] SSH access verified
- [ ] System requirements met
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Services configured
- [ ] Services started
- [ ] Health checks passed
- [ ] Firewall configured
- [ ] Monitoring enabled
- [ ] Backups in place
- [ ] Documentation reviewed
- [ ] Team trained

## Support

For deployment issues:
1. Check service logs: `sudo journalctl -u spec-kit-*`
2. Verify network connectivity
3. Test API manually with curl
4. Review INSTALLATION.md for troubleshooting
5. Check GitHub for known issues
