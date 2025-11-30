#!/usr/bin/env python3
"""
VS Code integration script for MCP server
Run allowlisted commands remotely via the MCP API
"""

import requests
import json
import sys

MCP_URL = "http://10.10.10.24:3030"

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mcp_cmd.py <allowlisted_command>")
        print("Example: python3 mcp_cmd.py 'uptime'")
        sys.exit(1)

    cmd = " ".join(sys.argv[1:])
    success = run_remote_cmd(cmd)
    sys.exit(0 if success else 1)