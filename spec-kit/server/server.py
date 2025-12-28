#!/usr/bin/env python3
"""
MCP Server for GitHub Spec-Kit
Exposes spec-kit commands as Model Context Protocol tools via stdio
"""

import json
import subprocess
import sys
import os
from typing import Any

# MCP Protocol implementation
class MCPServer:
    def __init__(self):
        self.tools = {
            "specify_init": {
                "description": "Initialize a new Specify project from the latest template",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path for new Specify project (defaults to current directory)"
                        }
                    }
                }
            },
            "specify_check": {
                "description": "Check that all required tools are installed for Specify",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "specify_version": {
                "description": "Display version and system information for Specify",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "specify_run_command": {
                "description": "Run a raw specify command with custom arguments",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The specify subcommand to run (e.g., 'init', 'check', 'version')"
                        },
                        "args": {
                            "type": "array",
                            "description": "Additional arguments to pass to the command",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["command"]
                }
            }
        }

    def run_specify_command(self, command: str, args: list = None) -> dict:
        """Execute a specify CLI command"""
        if args is None:
            args = []
        
        try:
            # Validate command is whitelisted
            valid_commands = {'init', 'check', 'version', 'help'}
            if command not in valid_commands:
                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Unknown command: {command}. Valid commands: {valid_commands}",
                    "returncode": 1
                }
            
            # Validate args - check for shell injection attempts
            for arg in args:
                if not isinstance(arg, str):
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": "All arguments must be strings",
                        "returncode": 1
                    }
                # Block dangerous shell metacharacters
                if any(c in arg for c in ['|', '&', ';', '$', '`', '\n', '\r']):
                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": f"Invalid characters in argument: {arg}",
                        "returncode": 1
                    }
            
            # Build command - ensure uv environment is sourced
            cmd = f"source ~/.local/bin/env && specify {command}"
            if args:
                # Use shlex.quote for safe argument quoting (if needed in future)
                cmd += " " + " ".join(args)
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after 30 seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    def handle_call_tool(self, tool_name: str, tool_input: dict) -> str:
        """Handle tool execution"""
        if tool_name == "specify_init":
            path = tool_input.get("path", ".")
            result = self.run_specify_command("init", [path] if path != "." else [])
            return json.dumps(result)
        
        elif tool_name == "specify_check":
            result = self.run_specify_command("check")
            return json.dumps(result)
        
        elif tool_name == "specify_version":
            result = self.run_specify_command("version")
            return json.dumps(result)
        
        elif tool_name == "specify_run_command":
            command = tool_input.get("command", "")
            args = tool_input.get("args", [])
            if not command:
                return json.dumps({
                    "success": False,
                    "stderr": "command parameter is required"
                })
            result = self.run_specify_command(command, args)
            return json.dumps(result)
        
        else:
            return json.dumps({
                "success": False,
                "stderr": f"Unknown tool: {tool_name}"
            })

    def process_request(self, request: dict) -> dict:
        """Process MCP protocol request"""
        request_type = request.get("type")
        
        if request_type == "initialize":
            return {
                "type": "initialize",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "serverInfo": {
                    "name": "spec-kit-mcp-server",
                    "version": "1.0.0"
                }
            }
        
        elif request_type == "tools/list":
            return {
                "type": "tools/list",
                "tools": [
                    {
                        "name": name,
                        "description": tool["description"],
                        "inputSchema": tool["inputSchema"]
                    }
                    for name, tool in self.tools.items()
                ]
            }
        
        elif request_type == "tools/call":
            tool_name = request.get("name")
            tool_input = request.get("arguments", {})
            result = self.handle_call_tool(tool_name, tool_input)
            
            return {
                "type": "tools/call",
                "name": tool_name,
                "result": result
            }
        
        else:
            return {
                "type": "error",
                "message": f"Unknown request type: {request_type}"
            }

def main():
    """Main entry point - read JSON-RPC messages from stdin"""
    server = MCPServer()
    
    # Log that server started
    sys.stderr.write("Spec-Kit MCP Server started\n")
    sys.stderr.flush()
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = server.process_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError as e:
                print(json.dumps({
                    "type": "error",
                    "message": f"Invalid JSON: {e}"
                }), flush=True)
            except Exception as e:
                print(json.dumps({
                    "type": "error",
                    "message": str(e)
                }), flush=True)
    
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        # stdin closed, exit gracefully
        sys.stderr.write("Spec-Kit MCP Server stopped\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
