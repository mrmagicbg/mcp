# MCP Server Automated Install & Config (Ubuntu LXC on Proxmox)

## Overview
This repository provides scripts and documentation to automate the installation and configuration of an MCP server inside an Ubuntu 24.04 LXC container on Proxmox.

The MCP server exposes a small HTTP API that can run allowlisted commands. It's intended for delegated safe operations from tools like VS Code Copilot or CLI integrations.

## Quick Start
- Edit the IP/port in `.vscode/mcp.json` if needed.
- Review `server/allowed_cmds.txt` and adjust tiers before enabling the service.
- On the target container run `sudo bash setup.sh` to install and enable the service.

## Files
- `server/server.py` - FastAPI server implementation
- `server/allowed_cmds.txt` - Allowlisted commands (tiered)
- `setup.sh` - Installer script to configure user, venv, systemd and files
- `systemd/mcp-http.service` - Example systemd unit file
- `.vscode/mcp.json` - VS Code integration example

## License
MIT
