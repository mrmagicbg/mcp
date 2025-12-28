# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] - 2025-12-29

### MAJOR: Complete Integration & Restructuring

#### Changed
- **BREAKING: Spec-Kit Integration Restructured**
  - Moved from separate `/spec-kit/` subdirectory to root-level integrated structure
  - Unified `setup.sh` now installs both FastAPI MCP server AND Spec-Kit together
  - Unified `deploy.sh` handles deployment of both components in single pass
  - Single `systemd/` directory contains all service files (mcp-http, spec-kit-web, spec-kit-mcp)
  - Documentation moved from `/spec-kit/docs/` to `/docs/`

- **Installation Process** - Now Unified
  - `setup.sh` is comprehensive unified installer:
    - Creates user and directories
    - Installs system packages (python3, venv, pip, git, curl, build-essential)
    - Creates Python virtual environment
    - Installs FastAPI + Uvicorn + Flask dependencies
    - Installs uv package manager
    - Installs GitHub Spec-Kit via uv
    - Copies both server implementations
    - Copies Flask web UI with templates
    - Installs ALL systemd services
    - Enables and starts both services
    - Provides comprehensive verification summary

- **Deployment Process** - Now Unified
  - `deploy.sh` unified deployer supporting both local and remote:
    - Connects to target system via SSH
    - Clones latest repository code
    - Syncs both FastAPI and Flask components
    - Updates all systemd service files
    - Restarts all services in proper order
    - Health checks both endpoints (3030 and 5000)
    - Provides unified verification output

- **Directory Structure** (Consolidated from `/spec-kit/` subdirectory)
  - `/server/` - Contains both server.py and web/ subdirectory
    - `server.py` - FastAPI MCP implementation
    - `web/app.py` - Flask web UI backend
    - `allowed_cmds.txt` - Command allowlist
  - `/templates/` - Web UI assets at root level
    - `index.html` - Rich web interface
  - `/docs/` - Consolidated documentation
    - `INSTALLATION.md` - Setup guide
    - `DEPLOYMENT.md` - Deployment procedures
    - `SPEC_KIT.md` - Spec-Kit feature overview
  - `/systemd/` - All service files in one location
    - `mcp-http.service` - FastAPI server
    - `spec-kit-web.service` - Flask web UI
    - `spec-kit-mcp.service` - MCP protocol interface

#### Added
- **Improved MCP Server for Agent Compatibility**
  - Enhanced FastAPI endpoints for agent discovery
  - `/mcp/tools` endpoint for tool definitions
  - `/mcp/describe` endpoint for tool descriptions
  - Improved JSON response format for agent parsing
  - Better HTTP status codes and error messages

- **Unified Documentation** 
  - Updated README.md showing integrated architecture
  - Clear architecture diagram with both components
  - Single installation/deployment workflow described
  - Port configuration documented (3030, 5000, stdio)
  - Use cases for agent-based operations

- **Setup & Deploy Enhancements**
  - Progress indicators (▶ symbols) for better visibility
  - Improved error handling and failure recovery
  - Automatic service verification after deployment
  - SSH-based remote deployment capability
  - Local deployment support for same-system installs
  - Proper cleanup of temporary files

#### Fixed
- Path handling in systemd services for integrated directory structure
- Service startup order and dependency management
- Port binding configuration for coexisting services (3030 FastAPI + 5000 Flask)
- Documentation file paths and cross-references
- Environment variable sourcing in service files

#### Notes
- **Major architectural change**: Spec-kit no longer separate subdir, fully merged
- `setup.sh` and `deploy.sh` are now atomic - install/update both components
- Services properly ordered: mcp-http.service starts first, then spec-kit services
- Production deployment to 10.10.10.24 tested and verified
- Backward compatible deployment approach (no breaking client API changes)

---

## [2.0.0] - 2025-12-28

### Added
- **Spec-Kit MCP Integration** - Complete integration with GitHub Spec-Kit for spec-driven development
  - MCP server component exposing spec-kit as Model Context Protocol tools
  - Web UI for browser-based spec-kit command execution
  - HTTP API endpoints for command execution and history
  - Rich HTML/CSS/JavaScript user interface
  - Command execution, output display, history tracking, copy/paste support
  
- **Web Interface** (port 5000)
  - Flask-based web application
  - Dashboard with available commands
  - Command execution form with argument input
  - Real-time output display with syntax highlighting
  - Command history with last 20 commands tracked
  - Copy output to clipboard functionality
  - Status indicators for service health

- **MCP Server Component** (stdio transport)
  - Model Context Protocol compliant server
  - Exposes 4 tools: specify_init, specify_check, specify_version, specify_run_command
  - JSON-RPC request/response handling
  - Safe subprocess execution with timeout protection
  - Integration with GitHub Spec-Kit CLI

- **Systemd Services**
  - spec-kit-web.service for web UI (auto-start enabled)
  - spec-kit-mcp.service for MCP server (auto-start enabled)
  - Proper user permissions and environment variable handling
  - Automatic restart on failure with 10-second delay

- **Documentation**
  - spec-kit/README.md - Feature overview and API reference
  - spec-kit/docs/INSTALLATION.md - Detailed step-by-step installation guide
  - spec-kit/docs/DEPLOYMENT.md - Production deployment procedures
  - API documentation with request/response examples
  - Troubleshooting guide with common issues and solutions

- **Configuration Files**
  - Server configuration for stdio transport MCP implementation
  - Web application configuration with Flask settings
  - Service file templates for easy deployment
  - Environment variable handling for spec-kit integration

### Dependencies Added
- Flask (3.0.2+) - Web framework for UI and API
- Python 3.11+ - Runtime environment
- uv package manager - For installing spec-kit
- GitHub Spec-Kit (v0.0.22+) - Spec-driven development toolkit

### Improvements
- Enhanced main README.md with spec-kit section
- Added architecture diagram showing component relationships
- Integrated spec-kit documentation into main repo structure
- Organized spec-kit files into logical subdirectories (server, web, systemd, docs)

### Configuration
- Web UI accessible on port 5000 (configurable)
- Command execution timeout set to 60 seconds (configurable)
- Service startup delay of 10 seconds on failure
- Stdout/stderr capture for all command execution
- Environment sourcing for uv/spec-kit PATH

### Files Changed/Added
- Added: spec-kit/server/server.py - MCP protocol implementation
- Added: spec-kit/web/app.py - Flask web server and API
- Added: spec-kit/web/templates/index.html - Web UI
- Added: spec-kit/systemd/spec-kit-mcp.service - MCP service file
- Added: spec-kit/systemd/spec-kit-web.service - Web service file
- Added: spec-kit/README.md - Main spec-kit documentation
- Added: spec-kit/docs/INSTALLATION.md - Installation guide
- Added: spec-kit/docs/DEPLOYMENT.md - Deployment guide
- Modified: README.md - Added spec-kit section and overview

### Testing
- Web UI verified functional and accessible at http://10.10.10.24:5000
- API endpoints tested: /api/commands, /api/process, /api/history
- Spec-kit version command execution verified working
- systemd services verified active and running
- All documentation reviewed and verified complete

## [1.0.0] - 2025-12-15

### Initial Release
- FastAPI-based REST API for remote command execution
- Command allowlisting system with 4 security tiers
- Systemd service integration
- VS Code task automation support
- CLI helper tool (mcp_cmd.py)
- Test server implementation
- Basic documentation and setup scripts

---

## Version Details

### 2.0.0 - Spec-Kit Integration Release
- **Date:** 2025-12-28
- **Status:** Stable
- **Major Features:** Complete spec-kit MCP integration with dual interfaces
- **Breaking Changes:** None (backward compatible with v1.0.0)
- **Upgrade Path:** Safe to upgrade from v1.0.0

### 1.0.0 - Initial Release
- **Date:** 2025-12-15
- **Status:** Stable
- **Major Features:** Remote command execution with allowlisting

---

## Upgrade Guide

### From 1.0.0 to 2.0.0

1. **Backup existing installation:**
   ```bash
   tar -czf mcp-backup-1.0.0.tar.gz /opt/mcp
   ```

2. **Pull latest code:**
   ```bash
   cd /opt/mcp
   git fetch origin
   git pull origin main
   ```

3. **Install new dependencies:**
   ```bash
   sudo apt-get install -y python3-flask
   ```

4. **Install spec-kit:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.local/bin/env
   ~/.local/bin/uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
   ```

5. **Deploy new services:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable spec-kit-web.service spec-kit-mcp.service
   sudo systemctl start spec-kit-web.service spec-kit-mcp.service
   ```

6. **Verify installation:**
   ```bash
   sudo systemctl status spec-kit-web.service spec-kit-mcp.service
   curl http://localhost:5000/api/commands
   ```

---

## Known Issues

### v2.0.0
- None currently identified

### v1.0.0
- FastAPI timeout handling may need adjustment for long-running commands

---

## Future Roadmap

### v2.1.0 (Planned)
- [ ] Database-backed command history persistence
- [ ] User authentication for web UI
- [ ] HTTPS/TLS support with reverse proxy
- [ ] Advanced command scheduling
- [ ] Webhook integration for event-driven commands
- [ ] Real-time command progress streaming

### v3.0.0 (Planned)
- [ ] Multi-user support with role-based access control
- [ ] Command templating and variables
- [ ] Audit logging and compliance reporting
- [ ] Integration with popular CI/CD platforms
- [ ] Mobile app for command execution
- [ ] Advanced analytics and monitoring

---

## Maintenance

### Supported Versions
- **v2.0.0** (Current) - Full support
- **v1.0.0** - Security fixes only
- **Earlier versions** - Unsupported

### End of Life
- v1.0.0: 2025-12-28 (replaced by v2.0.0)

### Deprecation Notices
- None at this time

---

## Contributors

- mrmagicbg - Initial development and spec-kit integration

---

## Contact & Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/mrmagicbg/mcp/issues
- Documentation: See spec-kit/docs/ for detailed guides
- Service Logs: `sudo journalctl -u spec-kit-* -f`
