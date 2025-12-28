#!/usr/bin/env python3
"""
Web UI for GitHub Spec-Kit
Provides a browser interface for prompt processing with spec-kit
"""

import subprocess
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Session storage for prompts (in-memory, could be extended to use database)
prompts_history = []

def run_specify_command(command: str, args: list = None) -> dict:
    """Execute a specify CLI command"""
    if args is None:
        args = []
    
    try:
        # Build command - ensure uv environment is sourced
        cmd = f"source ~/.local/bin/env && specify {command}"
        if args:
            cmd += " " + " ".join(args)
        
        result = subprocess.run(
            cmd,
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True,
            timeout=60
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
            "stderr": "Command timed out after 60 seconds",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """Get available spec-kit commands"""
    return jsonify({
        "commands": [
            {
                "name": "init",
                "description": "Initialize a new Specify project from the latest template",
                "args": ["path (optional)"]
            },
            {
                "name": "check",
                "description": "Check that all required tools are installed",
                "args": []
            },
            {
                "name": "version",
                "description": "Display version and system information",
                "args": []
            }
        ]
    })

@app.route('/api/process', methods=['POST'])
def process_prompt():
    """Process a spec-kit command"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        command = data.get('command', '').strip()
        args = data.get('args', [])
        
        if not command:
            return jsonify({"error": "Command is required"}), 400
        
        # Validate command is a known spec-kit command
        valid_commands = ['check', 'version', 'init', 'help']
        if command not in valid_commands and command != 'help':
            return jsonify({"error": f"Unknown command: {command}. Valid: {valid_commands}"}), 400
        
        # Validate args is a list
        if not isinstance(args, list):
            return jsonify({"error": "args must be an array"}), 400
        
        # Validate each arg is a string and doesn't contain shell metacharacters
        for arg in args:
            if not isinstance(arg, str):
                return jsonify({"error": "Each arg must be a string"}), 400
            # Basic check for dangerous shell characters
            if any(c in arg for c in ['|', '&', ';', '$', '`', '\n']):
                return jsonify({"error": f"Invalid characters in argument: {arg}"}), 400
        
        # Run the command
        result = run_specify_command(command, args)
        
        # Store in history
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args,
            "result": result
        }
        prompts_history.append(history_entry)
        
        return jsonify({
            "success": result["success"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "returncode": result["returncode"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get command history"""
    return jsonify({
        "history": prompts_history[-20:]  # Last 20 commands
    })

@app.route('/api/history/<int:index>', methods=['GET'])
def get_history_item(index):
    """Get specific history item"""
    if 0 <= index < len(prompts_history):
        return jsonify(prompts_history[index])
    return jsonify({"error": "Not found"}), 404

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear command history"""
    global prompts_history
    prompts_history = []
    return jsonify({"success": True, "message": "History cleared"})

if __name__ == '__main__':
    # Create templates directory if needed
    Path('templates').mkdir(exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
