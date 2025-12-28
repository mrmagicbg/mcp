#!/usr/bin/env python3
"""
Test script for MCP server at 10.10.10.24:3030
Tests /health and /exec endpoints with allowlisted commands.
"""

import requests
import json
import os
import sys

SERVER_URL = os.environ.get("SERVER_URL", "http://10.10.10.24:3030")

def test_health():
    try:
        response = requests.get(f"{SERVER_URL}/health")
        response.raise_for_status()
        data = response.json()
        print("✅ /health endpoint:")
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"❌ /health failed: {e}")
        return False

def test_api_health():
    try:
        response = requests.get(f"{SERVER_URL}/api/health")
        response.raise_for_status()
        data = response.json()
        print("✅ /api/health endpoint:")
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"❌ /api/health failed: {e}")
        return False

def test_exec(cmd):
    try:
        response = requests.post(f"{SERVER_URL}/exec", json={"cmd": cmd})
        response.raise_for_status()
        data = response.json()
        print(f"✅ /exec with '{cmd}':")
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"❌ /exec with '{cmd}' failed: {e}")
        return False

def test_commands():
    try:
        response = requests.get(f"{SERVER_URL}/commands")
        response.raise_for_status()
        data = response.json()
        print("✅ /commands endpoint:")
        print(json.dumps({"count": data.get("count"), "sample": (data.get("commands") or [])[:10]}, indent=2))
        return True
    except Exception as e:
        print(f"❌ /commands failed: {e}")
        return False

if __name__ == "__main__":
    # Optional URL override via first argument
    if len(sys.argv) >= 2 and sys.argv[1].startswith("http"):
        SERVER_URL = sys.argv[1]

    print("Testing MCP server at", SERVER_URL)
    print()

    success = True
    success &= test_health()
    success &= test_api_health()
    print()

    # Test some allowlisted commands from different tiers
    allowlisted_cmds = [
        "uptime",           # Tier 1
        "df -h",            # Tier 1
        "free -h",          # Tier 1
        "git status",       # Tier 2
        "python3 --version", # Tier 2
        "ls -l",            # Tier 2
        "id",               # Tier 3
        "ping -c 1 127.0.0.1", # Tier 4
        "ip route"          # Tier 4
    ]
    for cmd in allowlisted_cmds:
        success &= test_exec(cmd)
        print()

    success &= test_commands()

    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Some tests failed.")