#!/usr/bin/env python3
"""
VS Code integration script for MCP server
Run allowlisted commands remotely via the MCP API
"""

import requests
import json
import os
import sys

MCP_URL = os.environ.get("MCP_URL", "http://10.10.10.24:3030")

def run_remote_cmd(cmd):
    """Execute a command on the remote MCP server"""
    try:
        response = requests.post(f"{MCP_URL}/exec", json={"cmd": cmd}, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False

        if result.get("stdout"):
            print(result["stdout"].rstrip())
        if result.get("stderr"):
            print(result["stderr"].rstrip(), file=sys.stderr)

        return result.get("returncode", 0) == 0

    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False

def print_commands():
    """Fetch and print allowlisted commands from the remote MCP server"""
    try:
        response = requests.get(f"{MCP_URL}/commands", timeout=15)
        response.raise_for_status()
        data = response.json()
        cmds = data.get("commands", [])
        print(f"✅ {len(cmds)} allowlisted commands:")
        for c in cmds:
            print(f" - {c}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch commands: {e}")
        return False

def check_health():
    """Check remote MCP health via /api/health"""
    try:
        response = requests.get(f"{MCP_URL}/api/health", timeout=10)
        response.raise_for_status()
        print(json.dumps(response.json(), indent=2))
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    # Optional: allow URL override via --url
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 mcp_cmd.py [--url http://host:3030] [--list|--health] <allowlisted_command>")
        print("Examples:")
        print("  python3 mcp_cmd.py --url http://10.10.10.24:3030 'uptime'")
        print("  python3 mcp_cmd.py --list")
        print("  python3 mcp_cmd.py --health")
        sys.exit(1)

    if args[0] == "--url" and len(args) >= 3:
        MCP_URL = args[1]
        args = args[2:]

    if args and args[0] == "--list":
        success = print_commands()
    elif args and args[0] == "--health":
        success = check_health()
    else:
        cmd = " ".join(args)
        success = run_remote_cmd(cmd)
    sys.exit(0 if success else 1)