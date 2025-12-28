# Security Considerations

## Overview

This document outlines security measures, best practices, and considerations for the MCP Server and Spec-Kit integration.

## Current Security Model

### Command Allowlisting

**Remote Command Server (FastAPI):**
- All commands are restricted to those listed in `server/allowed_cmds.txt`
- Organized in 4 security tiers
- Prefix matching for commands with arguments
- No shell metacharacters allowed in inputs

**Spec-Kit MCP & Web UI:**
- Commands restricted to: `init`, `check`, `version`, `help`
- Arguments validated to prevent shell injection
- Command validation on both server and client side
- Timeout protection (60 seconds for web, 30 seconds for MCP)

### Input Validation

**Web UI:**
- JSON schema validation for all requests
- Command whitelisting
- Argument list validation (must be array of strings)
- Shell metacharacter filtering: `|`, `&`, `;`, `$`, `` ` ``, newlines, etc.
- HTTP-level request validation

**MCP Server:**
- Command whitelisting
- Argument type checking
- Shell metacharacter filtering
- JSON-RPC protocol validation

### Subprocess Execution

**Safety Measures:**
- No shell=True when using argument lists (arguments are properly escaped)
- Timeout protection prevents hung processes
- stdout/stderr captured to prevent output injection
- Process runs as unprivileged user (mrmagic)
- Environment variables are sanitized

## Development vs. Production

### Development Setup (Current)

**Characteristics:**
- HTTP only (no encryption)
- Web UI accessible from 0.0.0.0 (all interfaces)
- No authentication required
- In-memory command history (not persistent)
- Debug mode disabled
- Basic logging only

**Suitable for:**
- Local network testing
- Development and debugging
- Internal team testing
- Proof of concept

**Not suitable for:**
- Public internet exposure
- Sensitive data handling
- Multi-tenant environments
- Production SLAs

### Production Hardening Checklist

#### 1. Network Security

```bash
# Firewall restrictions
sudo ufw allow from 10.10.10.0/24 to any port 5000
sudo ufw allow from 10.10.10.0/24 to any port 22
sudo ufw enable

# Rate limiting (with nginx reverse proxy)
limit_req_zone $binary_remote_addr zone=spec-kit:10m rate=10r/s;
limit_req zone=spec-kit burst=20;

# IP allowlisting
allow 10.10.10.0/24;
deny all;
```

#### 2. Encryption

```bash
# Use HTTPS with valid certificate
# Option 1: Self-signed (for internal use)
sudo openssl req -x509 -newkey rsa:4096 -nodes \
  -out /etc/ssl/certs/spec-kit.crt \
  -keyout /etc/ssl/private/spec-kit.key -days 365

# Option 2: Let's Encrypt (for public URLs)
sudo certbot certonly --standalone -d spec-kit.example.com

# Configure nginx reverse proxy with SSL
# See deployment guide for full configuration
```

#### 3. Authentication

```python
# Option 1: HTTP Basic Auth
from functools import wraps
from flask import auth

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not check_auth(auth_header):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/protected')
@require_auth
def protected():
    return "OK"

# Option 2: API Token
VALID_TOKENS = ['your-secret-token-here']

@app.before_request
def check_token():
    token = request.headers.get('X-API-Token')
    if not token or token not in VALID_TOKENS:
        return jsonify({"error": "Invalid token"}), 401

# Option 3: OAuth/JWT
# Implement proper OAuth provider integration
```

#### 4. Database Security

If implementing persistent history:

```python
# Use parameterized queries
cursor.execute("SELECT * FROM history WHERE user_id = ?", (user_id,))

# Hash sensitive data
import hashlib
hashed = hashlib.sha256(command.encode()).hexdigest()

# Encrypt at rest if using database with sensitive data
from cryptography.fernet import Fernet
cipher = Fernet(key)
encrypted = cipher.encrypt(command.encode())
```

#### 5. Audit Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Set up audit log
audit_logger = logging.getLogger('audit')
handler = RotatingFileHandler(
    '/var/log/spec-kit/audit.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10
)
audit_logger.addHandler(handler)

# Log important events
@app.after_request
def log_audit(response):
    audit_logger.info(
        f"User: {get_user()} | Command: {request.json.get('command')} | "
        f"Status: {response.status_code} | IP: {request.remote_addr}"
    )
    return response
```

#### 6. CORS and Headers

```python
from flask_cors import CORS
from flask_talisman import Talisman

# Restrict CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://trusted-domain.com"],
        "methods": ["POST", "GET"],
        "max_age": 3600
    }
})

# Security headers
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self'",
        'style-src': "'self'"
    }
)
```

#### 7. Process Isolation

```bash
# Run services with minimal permissions
# In systemd service file:
[Service]
User=spec-kit-user
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/mcp/spec-kit
```

#### 8. Dependency Management

```bash
# Regular security updates
sudo apt-get update && sudo apt-get upgrade -y

# Pin dependencies to specific versions
# In requirements.txt
Flask==3.0.2
Werkzeug==3.0.1

# Regular vulnerability scanning
pip-audit
pip install --upgrade pip-audit
pip-audit
```

## Threat Model

### Potential Threats

| Threat | Risk | Mitigation |
|--------|------|-----------|
| Shell Injection | High | Command/argument validation, whitelist, no shell metacharacters |
| DDoS Attacks | High | Rate limiting, firewall rules, authentication |
| Unauthorized Access | High | Authentication, firewall, HTTPS |
| Data Exposure | Medium | Encryption, audit logging, access control |
| Privilege Escalation | Low | Run as unprivileged user, no sudo in commands |
| Resource Exhaustion | Medium | Timeout protection, resource limits |
| Man-in-the-Middle | High | HTTPS/TLS encryption, certificate validation |

### Threat Mitigation Strategy

1. **Before Deployment:**
   - Code review for security issues
   - Dependency vulnerability scanning
   - Input validation testing
   - Penetration testing (in test environment)

2. **During Operation:**
   - Monitor logs for suspicious activity
   - Implement rate limiting
   - Regular security updates
   - Audit logging of all operations
   - Intrusion detection

3. **After Incident:**
   - Incident response plan
   - Log analysis and retention
   - Automated alerting
   - Regular security audits

## Security Best Practices

### For Administrators

1. **Keep systems updated:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Monitor logs regularly:**
   ```bash
   sudo journalctl -u spec-kit-web.service -u spec-kit-mcp.service -f
   ```

3. **Restrict access:**
   ```bash
   sudo ufw default deny incoming
   sudo ufw allow from 10.10.10.0/24 to any port 5000
   ```

4. **Use strong credentials:**
   - Generate long, random API tokens
   - Use SSH keys, not passwords
   - Rotate credentials regularly

5. **Backup configuration:**
   ```bash
   sudo tar -czf /opt/backup/spec-kit-config.tar.gz \
     /etc/systemd/system/spec-kit-* \
     /opt/mcp/spec-kit
   ```

### For Developers

1. **Never hardcode secrets:**
   ```python
   # Bad
   API_KEY = "secret-key-12345"
   
   # Good
   import os
   API_KEY = os.getenv('API_KEY')
   ```

2. **Validate all inputs:**
   ```python
   # Validate type, length, format
   if not isinstance(command, str) or len(command) > 100:
       return error()
   ```

3. **Use security headers:**
   ```python
   @app.after_request
   def set_security_headers(response):
       response.headers['X-Content-Type-Options'] = 'nosniff'
       response.headers['X-Frame-Options'] = 'DENY'
       response.headers['X-XSS-Protection'] = '1; mode=block'
       return response
   ```

4. **Log security events:**
   ```python
   audit_log.warning(f"Failed auth attempt from {ip_address}")
   ```

## Compliance

### Standards

- **CWE:** Common Weakness Enumeration
  - CWE-78: OS Command Injection
  - CWE-79: Cross-site Scripting (XSS)
  - CWE-200: Exposure of Sensitive Information
  
- **OWASP Top 10:**
  - A1: Broken Access Control
  - A2: Cryptographic Failures
  - A3: Injection
  - A4: Insecure Design
  - A5: Security Misconfiguration

### Audit Checklist

- [ ] All inputs validated and sanitized
- [ ] Authentication implemented and tested
- [ ] HTTPS/TLS enabled in production
- [ ] Firewall rules configured correctly
- [ ] Audit logging enabled and monitored
- [ ] Dependencies scanned for vulnerabilities
- [ ] Error handling doesn't leak sensitive info
- [ ] Secrets not hardcoded or in version control
- [ ] Access control tested and verified
- [ ] Backup and recovery procedures tested

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do not** post it publicly
2. Email security details to: [security contact]
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
4. Allow time for patch before disclosure

## References

- [OWASP Security Guidelines](https://owasp.org/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Flask Security Documentation](https://flask.palletsprojects.com/security/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## License

This security documentation is part of the MCP Server project and subject to the same license.
