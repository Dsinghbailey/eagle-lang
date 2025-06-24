"""Shell tool for Eagle - executes shell commands safely."""

import subprocess
import os
from typing import Dict, Any
from eagle_lang.tools.base import EagleTool


class ShellTool(EagleTool):
    """Tool for executing shell commands."""
    
    @property
    def name(self) -> str:
        return "shell"
    
    @property
    def description(self) -> str:
        return "Execute shell commands. Use with caution - has safety restrictions on dangerous commands."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Optional working directory to run the command in",
                    "default": "."
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30, max: 300)",
                    "default": 30,
                    "maximum": 300
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Whether to capture and return the output",
                    "default": True
                }
            },
            "required": ["command"]
        }
    
    @property
    def usage_patterns(self) -> Dict[str, Any]:
        return {
            "category": "system_operations",
            "patterns": [
                "Run build commands and tests",
                "Execute development tools and scripts", 
                "Perform system operations and file management",
                "Run data processing and analysis commands"
            ],
            "workflows": {
                "Development": ["shell", "read", "print"],
                "Testing": ["shell", "print", "ask_permission"],
                "Build Process": ["shell", "shell", "write"],
                "Data Processing": ["read", "shell", "write"]
            }
        }
    
    def execute(self, command: str, working_directory: str = ".", timeout: int = 30, capture_output: bool = True) -> str:
        """Execute the shell tool."""
        # Safety checks
        if not self._is_safe_command(command):
            return f"Command blocked for safety: {command}"
        
        return self._execute_command(command, working_directory, timeout, capture_output)
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute with common sense protection."""
        # Basic dangerous patterns - common sense protection only
        dangerous_patterns = [
            "rm -rf /",     # Don't delete root
            ":(){ :|:& };:", # Fork bomb
            "sudo rm -rf",   # Don't sudo delete everything
            "shutdown",      # Don't shutdown system
            "reboot",        # Don't reboot system
            "halt",          # Don't halt system
            "dd if=/dev/zero", # Don't zero out disks
            "mkfs",          # Don't format disks
            "fdisk",         # Don't modify partition tables
        ]
        
        command_lower = command.lower().strip()
        
        # Check dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return False
        
        return True
    
    def _execute_command(self, command: str, working_directory: str, timeout: int, capture_output: bool) -> str:
        """Execute the shell command."""
        try:
            # Validate working directory
            if working_directory and working_directory != ".":
                if not os.path.exists(working_directory):
                    return f"Working directory does not exist: {working_directory}"
                if not os.path.isdir(working_directory):
                    return f"Working directory path is not a directory: {working_directory}"
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_directory if working_directory != "." else None,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            
            if capture_output:
                output = []
                if result.stdout:
                    output.append(f"STDOUT:\n{result.stdout}")
                if result.stderr:
                    output.append(f"STDERR:\n{result.stderr}")
                
                output.append(f"Exit code: {result.returncode}")
                
                if result.returncode == 0:
                    status = "Command executed successfully"
                else:
                    status = f"Command failed with exit code {result.returncode}"
                
                return f"{status}\n\n" + "\n\n".join(output)
            else:
                return f"Command executed with exit code: {result.returncode}"
                
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds"
        except FileNotFoundError:
            return f"Command not found: {command.split()[0] if command.split() else command}"
        except Exception as e:
            return f"Error executing command: {str(e)}"